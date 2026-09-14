#!/usr/bin/env python3
"""Does the Transformer actually need a heavy dataset? Measure it.

Trains XGBoost and the 2-layer Transformer encoder on 5, 10, 25, 50 and 100
percent of the same training split, and scores both on the same untouched
30,000-row test set. Also counts parameters, so "heavy model" is a number
rather than an adjective.
"""
import os, sys, json, time
import numpy as np
import torch, torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bench_torch import Windows, TransformerNet, LSTMNet, train, evaluate, LOOKBACK

torch.manual_seed(42); np.random.seed(42); torch.set_num_threads(4)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BM   = os.path.join(ROOT, "outputs", "benchmark")
from sklearn.metrics import accuracy_score
import xgboost as xgb

FRACTIONS = [0.05, 0.10, 0.25, 0.50, 1.00]


def subsample(X, y, frac, seed=42):
    """Contiguous per-class slices, so sequence windows stay intact."""
    if frac >= 1.0:
        return X, y
    keep = np.zeros(len(y), dtype=bool)
    bnd = np.flatnonzero(np.diff(y)) + 1
    starts = np.concatenate(([0], bnd)); ends = np.concatenate((bnd, [len(y)]))
    for s, e in zip(starts, ends):
        n = max(int((e - s) * frac), LOOKBACK + 1)
        keep[s:min(s + n, e)] = True
    return X[keep], y[keep]


def count_params(m):
    return sum(p.numel() for p in m.parameters())


def main():
    d = np.load(os.path.join(BM, "splits.npz"))
    Xtr, ytr, Xte, yte = d["X_train"], d["y_train"], d["X_test"], d["y_test"]
    nf = Xtr.shape[1]
    te_ds = Windows(Xte, yte, stride=1)

    # ---- parameter counts, for the "heavy model" claim -------------------
    tf = TransformerNet(nf); ls = LSTMNet(nf)
    pos = tf.pos.numel()
    params = {
        "Transformer_params": count_params(tf),
        "Transformer_positional_params": pos,
        "LSTM_params": count_params(ls),
    }
    print(f"Transformer: {params['Transformer_params']:,} parameters "
          f"({pos:,} of them positional encoding)")
    print(f"LSTM:        {params['LSTM_params']:,} parameters")

    curve = {"XGBoost": {}, "Transformer": {}}
    for frac in FRACTIONS:
        Xs, ys = subsample(Xtr, ytr, frac)
        print(f"\n=== {frac*100:.0f}% of train — {len(ys):,} rows ===", flush=True)

        m = xgb.XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.08,
                              subsample=0.85, colsample_bytree=0.85,
                              random_state=42, eval_metric="mlogloss", n_jobs=4)
        t0 = time.time(); m.fit(Xs, ys); xt = time.time() - t0
        xacc = accuracy_score(yte, m.predict(Xte))
        curve["XGBoost"][str(frac)] = {"rows": int(len(ys)), "accuracy": float(xacc),
                                       "train_s": xt}
        print(f"  XGBoost      {xacc*100:6.2f}%   ({xt:.0f}s)", flush=True)

        torch.manual_seed(42)
        net = TransformerNet(nf)
        tr_ds = Windows(Xs, ys, stride=3)
        dl = DataLoader(tr_ds, batch_size=256, shuffle=True, num_workers=2,
                        drop_last=True, persistent_workers=True)
        t0 = time.time(); train(net, dl, 6, f"TF@{int(frac*100)}%"); tt = time.time() - t0
        y, p = evaluate(net, te_ds)
        tacc = accuracy_score(y, p)
        curve["Transformer"][str(frac)] = {"rows": int(len(ys)), "accuracy": float(tacc),
                                           "train_s": tt}
        print(f"  Transformer  {tacc*100:6.2f}%   ({tt:.0f}s)", flush=True)

        json.dump({"curve": curve, "params": params},
                  open(os.path.join(BM, "data_efficiency.json"), "w"), indent=2)

    print("\nsaved", os.path.relpath(os.path.join(BM, "data_efficiency.json"), ROOT))


if __name__ == "__main__":
    main()
