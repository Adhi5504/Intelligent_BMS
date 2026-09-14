#!/usr/bin/env python3
"""The rule-based BMS baseline — what a conventional controller would do.

Thresholds are this project's own NMC limits, lifted verbatim from
backend/fault_risk_config.py, applied in severity order. There is
deliberately no Weak Cell rule: a threshold controller has no way to express
"this cell is degrading but still inside limits", which is the entire reason
the ML layer exists.
"""
import os, sys, json, time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BM   = os.path.join(ROOT, "outputs", "benchmark")
sys.path.insert(0, os.path.join(ROOT, "backend"))
from fault_risk_config import CHEMISTRY_CONFIGS
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

NMC = CHEMISTRY_CONFIGS["NMC"]
NORMAL, IMBAL, WEAK, OV, UV, OT = range(6)


def classify(cell_max, cell_min, delta_v, temp):
    """Vectorised threshold ladder, highest severity first."""
    out = np.full(len(temp), NORMAL, dtype=np.int64)
    out[delta_v   >  NMC["imbalance_critical_limit"]] = IMBAL     # 0.15 V
    out[cell_min  <  NMC["cell_min_voltage"]]         = UV        # 3.00 V
    out[cell_max  >  NMC["cell_max_voltage"]]         = OV        # 4.15 V
    out[temp      >  NMC["temp_critical_limit"]]      = OT        # 55 °C
    return out


def main():
    d = np.load(os.path.join(BM, "test_raw.npz"))
    X, y = d["X"], d["y"]
    feats = json.load(open(os.path.join(BM, "features.json")))
    col = {f: i for i, f in enumerate(feats)}
    cmax, cmin = X[:, col["cell_max"]], X[:, col["cell_min"]]
    dv, temp = X[:, col["delta_v"]], X[:, col["temperature"]]

    print("thresholds from backend/fault_risk_config.py['NMC']:")
    for k in ("imbalance_critical_limit", "cell_min_voltage",
              "cell_max_voltage", "temp_critical_limit"):
        print(f"   {k:26s} {NMC[k]}")

    yp = classify(cmax, cmin, dv, temp)

    # single-row latency, same protocol as the learned models
    rng = np.random.default_rng(0); idx = rng.choice(len(X), 200, replace=False)
    for i in idx[:20]:
        classify(cmax[i:i+1], cmin[i:i+1], dv[i:i+1], temp[i:i+1])
    t = []
    for i in idx:
        s = time.perf_counter()
        classify(cmax[i:i+1], cmin[i:i+1], dv[i:i+1], temp[i:i+1])
        t.append(time.perf_counter() - s)
    lat = float(np.median(t) * 1000)

    acc = accuracy_score(y, yp); f1 = f1_score(y, yp, average="macro")
    names = ["Normal", "Cell Imbalance", "Weak Cell",
             "Overvoltage", "Undervoltage", "Overtemperature"]
    cm = confusion_matrix(y, yp, labels=range(6))
    print(f"\n  Rule-based      acc={acc*100:6.2f}%  macroF1={f1:.4f}  "
          f"{lat:7.3f} ms  ~0 MB")
    print("\n  per-class recall:")
    for i, n in enumerate(names):
        r = cm[i, i] / cm[i].sum() if cm[i].sum() else 0
        print(f"    {n:18s} {r*100:6.2f}%")

    json.dump({"Rule-based BMS": {
        "accuracy": float(acc), "macro_f1": float(f1),
        "latency_ms": lat, "size_mb": 0.0,
        "note": "project's own NMC thresholds; no Weak Cell rule exists",
        "per_class_recall": {n: float(cm[i, i] / cm[i].sum()) for i, n in enumerate(names)},
    }}, open(os.path.join(BM, "rule_results.json"), "w"), indent=2)
    print("\nsaved", os.path.relpath(os.path.join(BM, "rule_results.json"), ROOT))


if __name__ == "__main__":
    main()
