#!/usr/bin/env python3
"""Benchmark the tree/kernel/rule baselines on the identical split.

Everything here is measured on this machine: accuracy on the same 30,000-row
held-out test set, median single-row inference latency, and on-disk size.
Latency is reported per row for a single sample, because that is what the
edge deployment actually does -- one window at a time, not a batch.
"""
import os, sys, json, time, tempfile
import numpy as np, joblib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BM   = os.path.join(ROOT, "outputs", "benchmark")
from sklearn.metrics import accuracy_score, f1_score

CLASSES = ["Normal", "Cell Imbalance", "Weak Cell",
           "Overvoltage", "Undervoltage", "Overtemperature"]


def latency_ms(predict_one, X, n=200, seed=0):
    """Median wall-clock for a single-sample prediction."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(X), n, replace=False)
    for i in idx[:20]:                       # warm up
        predict_one(X[i:i+1])
    t = []
    for i in idx:
        s = time.perf_counter(); predict_one(X[i:i+1]); t.append(time.perf_counter() - s)
    return float(np.median(t) * 1000)


def size_mb(model):
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=True) as f:
        joblib.dump(model, f.name, compress=0)
        return os.path.getsize(f.name) / 1e6


def record(results, name, y_true, y_pred, lat, size, note=""):
    acc = accuracy_score(y_true, y_pred)
    f1  = f1_score(y_true, y_pred, average="macro")
    results[name] = {"accuracy": float(acc), "macro_f1": float(f1),
                     "latency_ms": lat, "size_mb": size, "note": note}
    print(f"  {name:16s} acc={acc*100:6.2f}%  macroF1={f1:.4f}  "
          f"{lat:7.3f} ms  {size:6.2f} MB  {note}")
    return results


def main():
    d = np.load(os.path.join(BM, "splits.npz"))
    Xtr, ytr = d["X_train"], d["y_train"]
    Xte, yte = d["X_test"],  d["y_test"]
    print(f"train {Xtr.shape} · test {Xte.shape}")
    res = {}

    # ---------------------------------------------------------- XGBoost
    import xgboost as xgb
    m = xgb.XGBClassifier(); m.load_model(os.path.join(ROOT, "models", "bms_xgboost_model.json"))
    sz = os.path.getsize(os.path.join(ROOT, "models", "bms_xgboost_model.json")) / 1e6
    record(res, "XGBoost", yte, m.predict(Xte),
           latency_ms(lambda x: m.predict(x), Xte), sz, "shipped checkpoint")

    # ---------------------------------------------------- Random Forest
    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier(n_estimators=200, max_depth=None, n_jobs=-1,
                                random_state=42)
    t0 = time.time(); rf.fit(Xtr, ytr); tr = time.time() - t0
    record(res, "Random Forest", yte, rf.predict(Xte),
           latency_ms(lambda x: rf.predict(x), Xte), size_mb(rf),
           f"200 trees, trained in {tr:.0f}s")

    # -------------------------------------------------------------- SVM
    # RBF SVC is O(n^2) in the sample count; on 140k rows it does not finish in
    # any usable time, which is itself part of the verdict. Trained on a
    # stratified 20k subsample and evaluated on the full test set.
    from sklearn.svm import SVC
    from sklearn.model_selection import train_test_split
    Xs, _, ys, _ = train_test_split(Xtr, ytr, train_size=20000, stratify=ytr,
                                    random_state=42)
    sv = SVC(kernel="rbf", C=10.0, gamma="scale", cache_size=1000)
    t0 = time.time(); sv.fit(Xs, ys); tr = time.time() - t0
    record(res, "SVM (RBF)", yte, sv.predict(Xte),
           latency_ms(lambda x: sv.predict(x), Xte, n=60), size_mb(sv),
           f"20k subsample, trained in {tr:.0f}s")

    json.dump(res, open(os.path.join(BM, "sklearn_results.json"), "w"), indent=2)
    print("\nsaved", os.path.relpath(os.path.join(BM, "sklearn_results.json"), ROOT))


if __name__ == "__main__":
    main()
