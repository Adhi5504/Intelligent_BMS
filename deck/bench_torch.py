#!/usr/bin/env python3
"""Benchmark the two sequence models on the same split as everything else.

Both take a 60-row lookback window, matching the architecture described in
outputs/training_report.txt. Windows are built inside each (split, label)
group so none straddles a boundary, and the test set produces exactly one
window per test row -- so accuracy is over the identical 30,000 labels the
per-row models are scored on.

Note this gives the sequence models 60 rows of context the per-row models
never see. If anything that favours them.
"""
import os, sys, json, time, tempfile
import numpy as np
import torch, torch.nn as nn
from torch.utils.data import Dataset, DataLoader

torch.manual_seed(42); np.random.seed(42)
torch.set_num_threads(4)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BM   = os.path.join(ROOT, "outputs", "benchmark")
from sklearn.metrics import accuracy_score, f1_score

LOOKBACK, NCLS = 60, 6


class Windows(Dataset):
    """Lookback windows built by index — no dense copy of the whole tensor."""
    def __init__(self, X, y, stride=1):
        self.X = torch.from_numpy(X)
        self.y = torch.from_numpy(y)
        # group boundaries: label changes mark the start of a new segment
        bnd = np.flatnonzero(np.diff(y)) + 1
        starts = np.concatenate(([0], bnd))
        ends = np.concatenate((bnd, [len(y)]))
        idx = []
        for s, e in zip(starts, ends):
            idx.extend(range(s, e, stride))
        self.idx = np.asarray(idx, dtype=np.int64)
        self.seg_start = np.zeros(len(y), dtype=np.int64)
        for s, e in zip(starts, ends):
            self.seg_start[s:e] = s

    def __len__(self):
        return len(self.idx)

    def __getitem__(self, k):
        i = self.idx[k]
        lo = max(self.seg_start[i], i - LOOKBACK + 1)
        w = self.X[lo:i + 1]
        if len(w) < LOOKBACK:                       # left-pad short windows
            w = torch.cat([w[:1].repeat(LOOKBACK - len(w), 1), w], 0)
        return w, self.y[i]


class LSTMNet(nn.Module):
    def __init__(self, nf, hidden=64, layers=2):
        super().__init__()
        self.lstm = nn.LSTM(nf, hidden, layers, batch_first=True, dropout=0.1)
        self.head = nn.Sequential(nn.Linear(hidden, 64), nn.ReLU(), nn.Linear(64, NCLS))

    def forward(self, x):
        o, _ = self.lstm(x)
        return self.head(o[:, -1])


class TransformerNet(nn.Module):
    """d_model 64, 4 heads, 2 layers, ff 128 — the architecture in the report."""
    def __init__(self, nf, d=64, heads=4, layers=2, ff=128):
        super().__init__()
        self.proj = nn.Linear(nf, d)
        self.pos = nn.Parameter(torch.randn(1, LOOKBACK, d) * 0.02)
        enc = nn.TransformerEncoderLayer(d, heads, ff, dropout=0.1,
                                         batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(enc, layers)
        self.head = nn.Sequential(nn.LayerNorm(d), nn.Linear(d, NCLS))

    def forward(self, x):
        h = self.enc(self.proj(x) + self.pos)
        return self.head(h[:, -1])


def train(model, dl, epochs, tag):
    opt = torch.optim.AdamW(model.parameters(), lr=2e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, 2e-3, epochs * len(dl))
    lossf = nn.CrossEntropyLoss()
    t0 = time.time()
    for ep in range(epochs):
        model.train(); tot = n = 0
        for xb, yb in dl:
            opt.zero_grad()
            l = lossf(model(xb), yb)
            l.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step()
            tot += l.item() * len(yb); n += len(yb)
        print(f"    {tag} epoch {ep+1}/{epochs}  loss {tot/n:.4f}  "
              f"({time.time()-t0:.0f}s)", flush=True)
    return time.time() - t0


@torch.no_grad()
def evaluate(model, ds, bs=512):
    model.eval()
    dl = DataLoader(ds, batch_size=bs, shuffle=False, num_workers=0)
    P, Y = [], []
    for xb, yb in dl:
        P.append(model(xb).argmax(1).numpy()); Y.append(yb.numpy())
    return np.concatenate(Y), np.concatenate(P)


@torch.no_grad()
def latency_ms(model, ds, n=150):
    model.eval()
    rng = np.random.default_rng(0); idx = rng.choice(len(ds), n, replace=False)
    for k in idx[:20]:
        model(ds[k][0].unsqueeze(0))
    t = []
    for k in idx:
        x = ds[k][0].unsqueeze(0)
        s = time.perf_counter(); model(x); t.append(time.perf_counter() - s)
    return float(np.median(t) * 1000)


def size_mb(model):
    with tempfile.NamedTemporaryFile(suffix=".pth", delete=True) as f:
        torch.save(model.state_dict(), f.name)
        return os.path.getsize(f.name) / 1e6


def main():
    d = np.load(os.path.join(BM, "splits.npz"))
    Xtr, ytr, Xte, yte = d["X_train"], d["y_train"], d["X_test"], d["y_test"]
    nf = Xtr.shape[1]
    tr_ds = Windows(Xtr, ytr, stride=3)      # ~47k training windows
    te_ds = Windows(Xte, yte, stride=1)      # one window per test row
    print(f"train windows {len(tr_ds)} · test windows {len(te_ds)} · features {nf}")
    dl = DataLoader(tr_ds, batch_size=256, shuffle=True, num_workers=2,
                    drop_last=True, persistent_workers=True)

    res = {}
    for name, net, epochs in [("LSTM", LSTMNet(nf), 6),
                              ("Transformer", TransformerNet(nf), 6)]:
        print(f"\n  training {name} ...", flush=True)
        secs = train(net, dl, epochs, name)
        y, p = evaluate(net, te_ds)
        acc = accuracy_score(y, p); f1 = f1_score(y, p, average="macro")
        lat = latency_ms(net, te_ds); sz = size_mb(net)
        res[name] = {"accuracy": float(acc), "macro_f1": float(f1),
                     "latency_ms": lat, "size_mb": sz,
                     "note": f"60-row lookback, {epochs} epochs, trained in {secs:.0f}s"}
        print(f"  {name:16s} acc={acc*100:6.2f}%  macroF1={f1:.4f}  "
              f"{lat:7.3f} ms  {sz:6.2f} MB", flush=True)
        json.dump(res, open(os.path.join(BM, "torch_results.json"), "w"), indent=2)
    print("\nsaved", os.path.relpath(os.path.join(BM, "torch_results.json"), ROOT))


if __name__ == "__main__":
    main()
