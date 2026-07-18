import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
import joblib
import xgboost as xgb
import warnings
from datetime import datetime

def classify_confidence(score):
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0

    score = max(0.0, min(1.0, score))

    if score < 0.35:
        label = "Low Confidence"
    elif score < 0.85:
        label = "Moderate Confidence"
    else:
        label = "High Confidence"

    return {
        "score": round(score, 2),
        "label": label
    }

# 1. Model Caching logic for XGBoost (prevents repeated disk reads)
_cached_xgb_model = None
_cached_xgb_mtime = None

# Alarm Hysteresis Persistence globals
_last_processed_ts = None
_recent_predictions = []
_last_confirmed_fault = "Normal"
_last_raw_fault = "Normal"
_last_hysteresis_status = "Alert Verified"

_cached_scaler = None
_cached_feature_cols = None
_cached_label_map = None

_cached_ood_model = None
_cached_ood_config = None
_ood_recent_flags = []

_cached_limits = {
    "min_limit": 3.0,
    "max_limit": 4.15,
    "temp_limit": 45.0,
    "current_limit": 120.0
}

from pathlib import Path

def init_ml_model(model_dir):
    global _cached_xgb_model, _cached_xgb_mtime, _cached_scaler, _cached_feature_cols, _cached_label_map, _cached_limits
    global _cached_ood_model, _cached_ood_config
    
    print("Starting fault detection server")
    print("Loading ML model...")
    
    BASE_DIR = Path(__file__).resolve().parent
    model_dir_path = Path(model_dir) if Path(model_dir).is_absolute() else BASE_DIR / model_dir
    
    model_path = model_dir_path / "bms_xgboost_model.json"
    scaler_path = model_dir_path / "bms_scaler.joblib"
    feature_path = model_dir_path / "feature_columns.json"
    label_path = model_dir_path / "label_map.json"
    
    missing_files = []
    if not model_path.exists(): missing_files.append(str(model_path))
    if not scaler_path.exists(): missing_files.append(str(scaler_path))
    if not feature_path.exists(): missing_files.append(str(feature_path))
    if not label_path.exists(): missing_files.append(str(label_path))
    
    if missing_files:
        err_msg = f"Missing required ML files:\n" + "\n".join(missing_files)
        print(f"[ERROR] {err_msg}")
        import traceback
        traceback.print_stack()
        return {"status": "error", "error": err_msg, "model_loaded": False}
        
    try:
        mtime = os.path.getmtime(model_path)
        if _cached_xgb_model is None or _cached_xgb_mtime != mtime:
            model = xgb.XGBClassifier()
            model.load_model(model_path)
            _cached_xgb_model = model
            _cached_xgb_mtime = mtime
            
        if _cached_scaler is None:
            _cached_scaler = joblib.load(scaler_path)
        if _cached_feature_cols is None:
            with open(feature_path, 'r') as f:
                _cached_feature_cols = json.load(f)
        if _cached_label_map is None:
            with open(label_path, 'r') as f:
                lm = json.load(f)
                _cached_label_map = {int(k): v for k, v in lm.items()}
                
        ood_model_path = os.path.join(model_dir, "ood_detector.joblib")
        ood_config_path = os.path.join(model_dir, "ood_config.json")
        if os.path.exists(ood_model_path) and _cached_ood_model is None:
            _cached_ood_model = joblib.load(ood_model_path)
        if os.path.exists(ood_config_path) and _cached_ood_config is None:
            with open(ood_config_path, 'r') as f:
                _cached_ood_config = json.load(f)
                
        profile_path = os.path.join(model_dir, "active_profile.json")
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    profile = json.load(f)
                    cell_params = profile.get("cell_parameters", {})
                    if cell_params.get("minimum_voltage") is not None:
                        _cached_limits["min_limit"] = float(cell_params["minimum_voltage"])
                    if cell_params.get("maximum_voltage") is not None:
                        _cached_limits["max_limit"] = float(cell_params["maximum_voltage"])
                    if cell_params.get("discharge_temperature_max") is not None:
                        _cached_limits["temp_limit"] = float(cell_params["discharge_temperature_max"])
                    if cell_params.get("maximum_continuous_discharge_current") is not None:
                        _cached_limits["current_limit"] = float(cell_params["maximum_continuous_discharge_current"])
            except Exception as e:
                pass
                
        print("ML model loaded successfully")
        return {"status": "ok", "service": "fault-detection", "model_loaded": True}
    except Exception as e:
        err_msg = f"Failed to load ML model: {str(e)}"
        print(f"[ERROR] {err_msg}")
        return {"status": "error", "error": err_msg, "model_loaded": False}

def get_xgb_model(model_dir):
    global _cached_xgb_model, _cached_xgb_mtime
    model_path = os.path.join(model_dir, "bms_xgboost_model.json")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained XGBoost model weights not found at: {model_path}")
        
    mtime = os.path.getmtime(model_path)
    if _cached_xgb_model is None or _cached_xgb_mtime != mtime:
        model = xgb.XGBClassifier()
        model.load_model(model_path)
        _cached_xgb_model = model
        _cached_xgb_mtime = mtime
    return _cached_xgb_model

def run_inference(df_60, model_dir):
    """
    df_60: DataFrame containing exactly 60 rows of raw battery telemetry.
    model_dir: directory where models and scalers are saved.
    """
    if len(df_60) != 60:
        raise ValueError(f"Input must contain exactly 60 rows of telemetry, got {len(df_60)} rows.")
        
    # Standardize columns to lowercase
    df = df_60.copy()
    df.columns = [str(c).lower().strip() for c in df.columns]
    
    # Check base columns
    required = ['voltage', 'current', 'temperature', 'soc']
    cell_cols = [f'cell_v{i}' for i in range(1, 9)]
    
    for col in required + cell_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
            
    # Compute delta_v if missing
    if 'delta_v' not in df.columns:
        df['delta_v'] = df[cell_cols].max(axis=1) - df[cell_cols].min(axis=1)
        
    # Fill NTCs if missing
    for ntc in ['ntc1', 'ntc2', 'ntc3', 'ntc4']:
        if ntc not in df.columns:
            df[ntc] = df['temperature']
            
    # --- 1. Dynamic Mode Classification ---
    import sys
    if model_dir not in sys.path:
        sys.path.append(model_dir)
    try:
        from mode_classifier import classify_operating_modes
        threshold_path = os.path.join(model_dir, "mode_thresholds.json")
        df = classify_operating_modes(df, recompute_thresholds=False, threshold_path=threshold_path)
        mode_name = df['Operating_Mode'].iloc[-1]
        
        df['mode_IDLE'] = (df['Operating_Mode'] == 'IDLE').astype(float)
        df['mode_DECEL'] = (df['Operating_Mode'] == 'DECEL').astype(float)
        df['mode_ACCEL'] = (df['Operating_Mode'] == 'ACCEL').astype(float)
        df['mode_CRUISE'] = (df['Operating_Mode'] == 'CRUISE').astype(float)
    except Exception as e:
        print(f"Warning: Failed to use dynamic modes, falling back. {e}")
        mode_name = "CRUISE"
        for m in ['ACCEL', 'CRUISE', 'DECEL', 'IDLE']:
            df[f'mode_{m}'] = 0.0
        df['mode_CRUISE'] = 1.0
    
    # --- 2. Feature Engineering ---
    # No current inversion needed here since gateway telemetry is now in standard JBD convention
    df['cell_max'] = df[cell_cols].max(axis=1)
    df['cell_min'] = df[cell_cols].min(axis=1)
    df['cell_mean'] = df[cell_cols].mean(axis=1)
    df['cell_std'] = df[cell_cols].std(axis=1)
    df['cell_range'] = df['cell_max'] - df['cell_min']

    df['dv_dt'] = df['delta_v'].diff().fillna(0)
    df['dtemp_dt'] = df['temperature'].diff().fillna(0)
    df['dsoc_dt'] = df['soc'].diff().fillna(0)
    df['dvoltage_dt'] = df['voltage'].diff().fillna(0)

    df['rolling_mean_voltage'] = df['voltage'].rolling(window=10, min_periods=1).mean()
    df['rolling_std_voltage'] = df['voltage'].rolling(window=10, min_periods=1).std().fillna(0)
    df['rolling_mean_temperature'] = df['temperature'].rolling(window=10, min_periods=1).mean()
    df['rolling_std_temperature'] = df['temperature'].rolling(window=10, min_periods=1).std().fillna(0)

    # Spatial thermal spread calculation
    df['ntc_spread'] = df[['ntc1', 'ntc2', 'ntc3', 'ntc4']].max(axis=1) - df[['ntc1', 'ntc2', 'ntc3', 'ntc4']].min(axis=1)

    for i in range(1, 9):
        col = f'cell_v{i}'
        df[f'cell_drop_rate_{i}'] = df[col].diff().clip(upper=0).abs().fillna(0)
        df[f'cell_rise_rate_{i}'] = df[col].diff().clip(lower=0).fillna(0)
        
    # --- 3. Load Saved Scale and Columns config ---
    global _cached_scaler, _cached_feature_cols, _cached_label_map
    if _cached_scaler is None or _cached_feature_cols is None or _cached_label_map is None:
        res = init_ml_model(model_dir)
        if not res.get("model_loaded", False):
            raise RuntimeError(res.get("error", "Unknown error loading ML model"))
            
    scaler = _cached_scaler
    feature_cols = _cached_feature_cols
    label_map = _cached_label_map
        
    # Align features
    X_raw = df[feature_cols].values
    X_scaled = scaler.transform(X_raw) # shape [60, num_features]
    
    # --- 4. Model Inference ---
    model = get_xgb_model(model_dir)
    
    # Extract the very last row (the current time step) for prediction
    X_latest = X_scaled[-1].reshape(1, -1)
    
    # --- Hybrid OOD Detection (Stage 2) ---
    global _cached_ood_model, _cached_ood_config, _ood_recent_flags
    is_ood = False
    ood_score = 0.0
    crit_threshold = -0.6
    if _cached_ood_model is not None and _cached_ood_config is not None:
        score_array = _cached_ood_model.score_samples(X_latest)
        raw_score = float(score_array[0])
        ood_score = round(abs(raw_score), 4) # absolute magnitude for display
        crit_threshold = _cached_ood_config.get("critical_threshold_raw", -0.5)
        
        current_is_ood = bool(raw_score < crit_threshold)
        _ood_recent_flags.append(current_is_ood)
        if len(_ood_recent_flags) > 3:
            _ood_recent_flags.pop(0)
            
        # Hysteresis: requires 2 out of 3 consecutive frames to trigger to avoid false alarms
        if sum(_ood_recent_flags) >= 2:
            is_ood = True
            
    # Check for totally broken sensor data
    data_integrity_fault = bool(np.isnan(X_latest).any() or (X_latest == 0).all())
    
    ood_status = "OOD Anomaly Detected" if is_ood else "In-Distribution (Safe)"
    
    # Run prediction and output class probabilities
    probs = model.predict_proba(X_latest)[0]
    pred_idx = int(np.argmax(probs))
        
    pred_fault = label_map[pred_idx]
    confidence = float(probs[pred_idx])
    
    # Mapping probabilities to output dictionary
    all_probs_dict = {label_map[i]: float(probs[i]) for i in range(len(label_map))}
    
    # --- 4.5 Output ML Probabilities ---
    output = {
        "Operating Mode": mode_name,
        "Fault Prediction": pred_fault,
        "Raw Prediction": pred_fault,
        "is_ood": bool(is_ood),
        "ood_score": float(ood_score),
        "known_class_confidence": float(confidence),
        "All Class Probabilities": {k: float(v) for k, v in all_probs_dict.items()},
        "NTC Spread": f"{df['ntc_spread'].iloc[-1]:.2f} °C",
        "data_integrity_fault": bool(data_integrity_fault)
    }
    
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict battery faults and operating modes.")
    parser.add_argument("--file", type=str, help="Path to an Excel file with battery telemetry.")
    parser.add_argument("--sheet", type=str, default="Charging", help="Sheet name to read from.")
    parser.add_argument("--model_dir", type=str, default="../models", help="Directory containing model weights and scaler.")
    args = parser.parse_ok = parser.parse_args()
    
    filepath = args.file
    if not filepath:
        # Fallback to a file in output_dir
        directory = args.model_dir
        excel_files = [f for f in os.listdir(directory) if f.endswith('.xlsx')]
        if not excel_files:
            print(json.dumps({"error": "No Excel files found in model_dir. Please provide a file using --file."}))
            sys.exit(1)
        filepath = os.path.join(directory, excel_files[0])
        
    try:
        # Load data
        xls = pd.ExcelFile(filepath)
        sheet_name = args.sheet if args.sheet in xls.sheet_names else xls.sheet_names[0]
        df_full = pd.read_excel(filepath, sheet_name=sheet_name)
        
        # Take latest 60 rows
        if len(df_full) < 60:
            print(json.dumps({"error": f"File sheet {sheet_name} has only {len(df_full)} rows, need at least 60."}))
            sys.exit(1)
            
        df_60 = df_full.iloc[-60:].reset_index(drop=True)
        
        # Run inference
        result = run_inference(df_60, args.model_dir)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
