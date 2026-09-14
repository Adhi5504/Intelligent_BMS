#!/usr/bin/env python3
"""Materialise the exact train/val/test matrices every benchmarked model uses.

Identical feature engineering, identical split, identical scaler as
backend/train_xgboost.py -- so the comparison table is apples to apples.
"""
import os, sys, json
import numpy as np, pandas as pd, joblib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
from train_xgboost import engineer_features
from sklearn.preprocessing import MinMaxScaler

OUT = os.path.join(ROOT, "outputs", "benchmark")
os.makedirs(OUT, exist_ok=True)

def main():
    raw = pd.read_excel(os.path.join(ROOT, "data", "augmented_telemetry_dataset.xlsx"),
                        sheet_name=0)
    feats = json.load(open(os.path.join(ROOT, "models", "feature_columns.json")))
    parts = [engineer_features(g.reset_index(drop=True))
             for _, g in raw.groupby(["split", "fault_label"])]
    df = pd.concat(parts, ignore_index=True)

    out = {}
    for name in ("train", "val", "test"):
        m = df["split"] == name
        out[f"X_{name}"] = df[m][feats].values.astype(np.float32)
        out[f"y_{name}"] = df[m]["fault_label"].values.astype(np.int64)
        print(f"  {name}: {out[f'X_{name}'].shape}")

    # the shipped scaler was fitted on this same train split
    sc = joblib.load(os.path.join(ROOT, "models", "bms_scaler.joblib"))
    for name in ("train", "val", "test"):
        out[f"X_{name}"] = sc.transform(out[f"X_{name}"]).astype(np.float32)

    np.savez_compressed(os.path.join(OUT, "splits.npz"), **out)
    print("  saved", os.path.relpath(os.path.join(OUT, "splits.npz"), ROOT))

    # raw (unscaled) test matrix + column index, for the rule-based baseline
    m = df["split"] == "test"
    np.savez_compressed(os.path.join(OUT, "test_raw.npz"),
                        X=df[m][feats].values.astype(np.float32),
                        y=df[m]["fault_label"].values.astype(np.int64))
    json.dump(feats, open(os.path.join(OUT, "features.json"), "w"))
    print("  saved test_raw.npz + features.json")

if __name__ == "__main__":
    main()
