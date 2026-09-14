#!/usr/bin/env python3
"""Second batch of data-driven figures for the expanded AI-PBMS deck.

Same rule as make_charts.py: every value is measured from a file in this
repository or stated in the brief. Where a number does not exist, the figure
says so rather than filling the gap.
"""
import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme
from theme import (ACCENT, WARNING, CRITICAL, INK, MUTED, HAIRLINE, PANEL, BG,
                   ACCENT_TINT, WARNING_TINT, CRITICAL_TINT)
theme.apply()
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "assets", "generated")
DATA = os.path.join(ROOT, "data")
os.makedirs(OUT, exist_ok=True)

CELLS = [f"cell_v{i}" for i in range(1, 9)]


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor=theme.BG, transparent=False)
    plt.close(fig)
    print("  wrote", os.path.relpath(p, ROOT))


def _window(n=2400):
    """A clean, contiguous discharge window out of the 155k-row log."""
    d = pd.read_csv(os.path.join(DATA, "bms_data_corrected (3).csv"), low_memory=False)
    d = d[(d[CELLS] > 2.5).all(axis=1) & (d.temperature > 10) & (d.soc > 0)]
    best = None
    for st in range(0, len(d) - n, 600):
        w = d.iloc[st:st + n]
        if w.current.mean() < -5 and w.soc.iloc[0] - w.soc.iloc[-1] > 3 and w.ntc1.min() > 15:
            sc = (w.soc.iloc[0] - w.soc.iloc[-1]) + w.temperature.std()
            if best is None or sc > best[0]:
                best = (sc, st)
    return d.iloc[best[1]:best[1] + n].reset_index(drop=True)


# ------------------------------------------------- 1. the eight cell traces
def cell_traces(w):
    """Real per-cell voltages over a logged discharge. This is the evidence
    for the whole dataset story: cell 1 is visibly a different cell."""
    t = np.arange(len(w)) / 60.0                  # samples -> minutes (1 Hz log)
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    for c in CELLS[1:]:
        ax.plot(t, w[c], lw=1.0, color=HAIRLINE, zorder=2)
    ax.plot([], [], lw=1.6, color=HAIRLINE, label="cell_v2 … cell_v8")
    ax.plot(t, w["cell_v1"], lw=2.1, color=CRITICAL, zorder=4, label="cell_v1")

    gap = w[CELLS[1:]].mean().mean() - w["cell_v1"].mean()
    mid = len(w) // 2
    ax.annotate("", xy=(t[mid], w["cell_v1"].iloc[mid]),
                xytext=(t[mid], w[CELLS[1:]].iloc[mid].mean()),
                arrowprops=dict(arrowstyle="<->", color=CRITICAL, lw=1.6))
    ax.text(t[mid] + 0.9, (w["cell_v1"].iloc[mid] + w[CELLS[1:]].iloc[mid].mean()) / 2,
            f"{gap*1000:.0f} mV", fontsize=14, fontweight="bold", color=CRITICAL,
            va="center")
    ax.set_xlabel("Time into discharge (min)")
    ax.set_ylabel("Cell voltage (V)")
    ax.set_title("One cell is not like the others", pad=14)
    ax.legend(loc="upper right", fontsize=10, labelcolor=INK)
    theme.strip(ax)
    fig.text(0.5, -0.03, f"{len(w)} consecutive logged samples · "
             "data/bms_data_corrected (3).csv",
             ha="center", fontsize=8.5, color=MUTED, style="italic")
    save(fig, "fig_cell_traces.png")


# ------------------------------------------------------- 2. thermal zones
def thermal_zones(w):
    t = np.arange(len(w)) / 60.0
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(7.6, 5.4), sharex=True,
                                  gridspec_kw={"height_ratios": [2.6, 1]})
    cols = [("ntc1", ACCENT), ("ntc2", "#5B8DB8"), ("ntc3", WARNING), ("ntc4", CRITICAL)]
    for c, col in cols:
        ax.plot(t, w[c], lw=1.6, color=col, label=c.upper())
    ax.set_ylabel("Zone temperature (°C)")
    ax.set_title("Four thermal zones, one pack", pad=14)
    ax.legend(loc="center right", fontsize=9.5, labelcolor=INK, ncol=2)
    theme.strip(ax)

    spread = w[["ntc1", "ntc2", "ntc3", "ntc4"]].max(axis=1) - \
             w[["ntc1", "ntc2", "ntc3", "ntc4"]].min(axis=1)
    ax2.fill_between(t, 0, spread, color=WARNING, alpha=0.30, zorder=2)
    ax2.plot(t, spread, lw=1.4, color=WARNING, zorder=3)
    ax2.set_ylabel("ntc_spread\n(°C)", fontsize=9.5)
    ax2.set_xlabel("Time into discharge (min)")
    ax2.set_ylim(0, spread.max() * 1.25)
    theme.strip(ax2)
    ax2.text(0.015, 0.93, f"peak spread {spread.max():.1f} °C — an input feature, "
             "not just a readout", transform=ax2.transAxes,
             fontsize=9, color=INK, va="top",
             bbox=dict(boxstyle="round,pad=0.35", facecolor=BG,
                       edgecolor=HAIRLINE, linewidth=0.8))
    save(fig, "fig_thermal_zones.png")


# --------------------------------------------- 3. real feature importances
def feature_importance(top=12):
    import xgboost as xgb
    m = xgb.XGBClassifier(); m.load_model(os.path.join(ROOT, "models", "bms_xgboost_model.json"))
    feats = json.load(open(os.path.join(ROOT, "models", "feature_columns.json")))
    imp = m.feature_importances_
    idx = np.argsort(imp)[::-1][:top][::-1]
    names = [feats[i] for i in idx]
    vals  = imp[idx] * 100

    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    cols = [ACCENT if "mode_" not in n else WARNING for n in names]
    ax.barh(range(len(names)), vals, color=cols, height=0.68, zorder=3)
    for i, v in enumerate(vals):
        ax.text(v + 0.22, i, f"{v:.1f}", va="center", fontsize=9.5, color=MUTED)
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=10)
    ax.set_xlabel("Gain-based importance (% of total)")
    ax.set_title(f"What the model actually looks at — top {top} of {len(feats)}", pad=14)
    ax.set_xlim(0, vals.max() * 1.18)
    ax.grid(axis="y", visible=False)
    theme.strip(ax)
    ax.scatter([], [], marker="s", s=60, color=WARNING, label="driving-mode features")
    ax.scatter([], [], marker="s", s=60, color=ACCENT, label="sensor / derived features")
    ax.legend(loc="lower right", fontsize=9, labelcolor=INK)
    fig.text(0.5, -0.025, "Read from models/bms_xgboost_model.json",
             ha="center", fontsize=8.5, color=MUTED, style="italic")
    save(fig, "fig_feature_importance.png")


# ------------------------------------------------ 4. per-class P / R / F1
def per_class_metrics():
    cm = np.array(json.load(open(os.path.join(OUT, "confusion_matrix_source.json")))["matrix"])
    names = ["Normal", "Cell\nImbalance", "Weak\nCell", "Over-\nvoltage",
             "Under-\nvoltage", "Over-\ntemperature"]
    tp = np.diag(cm).astype(float)
    prec = tp / cm.sum(axis=0)
    rec  = tp / cm.sum(axis=1)
    f1   = 2 * prec * rec / (prec + rec)

    x = np.arange(len(names)); bw = 0.26
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.bar(x - bw, prec*100, bw, label="Precision", color=ACCENT, zorder=3)
    ax.bar(x,       rec*100, bw, label="Recall",    color="#7FC4CB", zorder=3)
    ax.bar(x + bw,  f1*100,  bw, label="F1",        color=INK, zorder=3)
    for xi, v in zip(x - bw, prec*100): ax.text(xi, v+1.2, f"{v:.0f}", ha="center", fontsize=8, color=MUTED)
    for xi, v in zip(x,      rec*100):  ax.text(xi, v+1.2, f"{v:.0f}", ha="center", fontsize=8, color=MUTED)
    for xi, v in zip(x + bw, f1*100):   ax.text(xi, v+1.2, f"{v:.0f}", ha="center", fontsize=8, color=MUTED)
    ax.axhline(75, color=CRITICAL, lw=1.1, ls=(0, (5, 4)), zorder=2)
    ax.text(5.60, 71.5, "below 75% — needs work", fontsize=9, color=CRITICAL,
            ha="right", va="top", style="italic")
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=9.5)
    ax.set_ylabel("Score (%)"); ax.set_ylim(0, 118)
    ax.set_title("Where the classifier is strong, and where it is not", pad=30)
    ax.legend(fontsize=9.5, labelcolor=INK, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, 1.11))
    ax.grid(axis="x", visible=False)
    theme.strip(ax)
    fig.text(0.5, -0.035, "Measured on the 30,000-row held-out test split using "
             "the shipped checkpoint.", ha="center", fontsize=8.5, color=MUTED,
             style="italic")
    save(fig, "fig_per_class_metrics.png")


# ------------------------------------------------------ 5. driving modes
def driving_modes():
    d = pd.read_csv(os.path.join(DATA, "bms_data_corrected (3).csv"),
                    usecols=["driving_mode"], low_memory=False)
    lab = {0: "IDLE", 1: "ACCEL", 2: "CRUISE", 3: "DECEL"}
    col = {0: MUTED, 1: CRITICAL, 2: ACCENT, 3: WARNING}
    vc = d["driving_mode"].value_counts().sort_index()
    tot = vc.sum()

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    left = 0.0
    for k, v in vc.items():
        pct = v / tot * 100
        ax.barh(0, pct, left=left, height=0.52, color=col[k],
                edgecolor=BG, linewidth=2.0, zorder=3)
        if pct > 7:
            ax.text(left + pct/2, 0, f"{lab[k]}\n{pct:.1f}%", ha="center", va="center",
                    fontsize=12, fontweight="bold", color=BG, zorder=4, linespacing=1.5)
        else:
            ax.text(left + pct/2, -0.45, f"{lab[k]}  {pct:.1f}%", ha="center", va="top",
                    fontsize=10, fontweight="bold", color=col[k])
        left += pct
    ax.set_xlim(0, 100); ax.set_ylim(-1.0, 0.75); ax.axis("off")
    ax.set_title("Operating-mode mix across the logged dataset", pad=16)
    fig.text(0.5, 0.06, f"{tot:,} classified rows · mode set from the change in "
             "current magnitude between consecutive samples",
             ha="center", fontsize=9, color=MUTED)
    save(fig, "fig_driving_modes.png")


# ------------------------------------------- 6. cycle history / prognosis
def cycle_history():
    d = pd.DataFrame(json.load(open(os.path.join(DATA, "cycle_history.json"))))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.4),
                                 gridspec_kw={"width_ratios": [1.15, 1]})

    dis = d[d.type == "Discharge"]; chg = d[d.type == "Charge"]
    a1.scatter(dis.avg_current.abs(), dis.temp_rise, s=58, color=CRITICAL,
               alpha=0.80, zorder=3, label=f"Discharge (n={len(dis)})",
               edgecolor=BG, linewidth=0.8)
    a1.scatter(chg.avg_current.abs(), chg.temp_rise, s=58, color=ACCENT,
               alpha=0.80, zorder=3, label=f"Charge (n={len(chg)})",
               edgecolor=BG, linewidth=0.8)
    a1.set_xlabel("Mean current magnitude (A)")
    a1.set_ylabel("Temperature rise over the cycle (°C)")
    a1.set_title("Thermal cost of current", fontsize=12.5, pad=10)
    a1.legend(fontsize=9, labelcolor=INK, loc="upper left")
    theme.strip(a1)

    ids = d.cycle_id.values
    a2.plot(ids, d.voltage_spread_start*1000, marker="o", ms=4, lw=1.5,
            color=WARNING, label="ΔV at cycle start", zorder=3)
    a2.plot(ids, d.voltage_spread_end*1000, marker="o", ms=4, lw=1.5,
            color=ACCENT, label="ΔV at cycle end", zorder=3)
    a2.set_xlabel("Cycle ID"); a2.set_ylabel("Cell voltage spread (mV)")
    a2.set_title("Imbalance across 39 logged cycles", fontsize=12.5, pad=10)
    a2.set_ylim(0, 520)
    peak = d.voltage_spread_start.max() * 1000
    pid = int(d.loc[d.voltage_spread_start.idxmax(), "cycle_id"])
    a2.annotate(f"cycle {pid}: {peak:.0f} mV\n(off scale)", xy=(pid, 505),
                xytext=(pid - 11, 430), fontsize=8.5, color=CRITICAL,
                linespacing=1.4,
                arrowprops=dict(arrowstyle="->", color=CRITICAL, lw=1.1))
    a2.legend(fontsize=9, labelcolor=INK, loc="upper left")
    theme.strip(a2)

    fig.text(0.5, -0.035, "data/cycle_history.json — 39 cycles, "
             "all data_quality_score 1.0, zero alerts raised",
             ha="center", fontsize=8.5, color=MUTED, style="italic")
    save(fig, "fig_cycle_history.png")


# --------------------------------------------------- 7. OOD detection panel
def ood_panel():
    """Numbers straight out of outputs/ood_evaluation_report.txt."""
    fig, ax = plt.subplots(figsize=(8.0, 3.9))
    ax.set_xlim(0, 12.6); ax.set_ylim(0, 5.4); ax.axis("off")
    cards = [("0.913", "AUROC", "separation power", ACCENT, ACCENT_TINT),
             ("100%", "precision", "never cried wolf", ACCENT, ACCENT_TINT),
             ("0.0%", "false positives", "0 of 49 known rejected", ACCENT, ACCENT_TINT),
             ("24.5%", "recall", "the honest weak spot", CRITICAL, CRITICAL_TINT)]
    w, gap = 2.73, 0.30
    for i, (big, mid, sub, col, tint) in enumerate(cards):
        x = 0.30 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 0.55), w, 3.75,
                     boxstyle="round,pad=0,rounding_size=0.14",
                     facecolor=tint, edgecolor=col, linewidth=1.5))
        ax.text(x + w/2, 3.24, big, ha="center", va="center", fontsize=27,
                fontweight="bold", color=col)
        ax.text(x + w/2, 2.30, mid, ha="center", va="center", fontsize=11.5, color=col)
        ax.text(x + w/2, 1.32, sub, ha="center", va="center", fontsize=8.8, color=MUTED)
    ax.text(6.3, 5.00, "Unknown-fault detection — IsolationForest gate",
            ha="center", va="center", fontsize=13.5, fontweight="bold", color=INK)
    ax.text(6.3, 0.16, "49 in-distribution vs 49 synthetic-unknown windows · "
            "outputs/ood_evaluation_report.txt",
            ha="center", va="center", fontsize=8.5, color=MUTED, style="italic")
    save(fig, "fig_ood_panel.png")


# ------------------------------------------------- 8. dataset composition
def dataset_composition():
    d = pd.read_excel(os.path.join(DATA, "augmented_telemetry_dataset.xlsx"),
                      sheet_name=0, usecols=["fault_label", "split"])
    lab = {0: "Normal", 1: "Cell Imbalance", 2: "Weak Cell",
           3: "Overvoltage", 4: "Undervoltage", 5: "Overtemperature"}
    vc = d["fault_label"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    names = [lab[k] for k in vc.index]
    cols = [ACCENT] + [WARNING]*4 + [CRITICAL]
    b = ax.bar(names, vc.values, color=cols, width=0.62, zorder=3)
    for bi, v in zip(b, vc.values):
        ax.text(bi.get_x()+bi.get_width()/2, v + vc.max()*0.022, f"{v:,}",
                ha="center", fontsize=9.5, color=MUTED)
    ax.set_ylabel("Rows")
    ax.set_ylim(0, vc.max()*1.16)
    ax.set_title(f"Training set after rebalancing — {vc.sum():,} rows", pad=14)
    ax.tick_params(axis="x", labelsize=9.5, rotation=18)
    for t in ax.get_xticklabels(): t.set_ha("right")
    ax.grid(axis="x", visible=False)
    theme.strip(ax)
    sp = d["split"].value_counts()
    fig.text(0.5, -0.06,
             f"70/15/15 split — train {sp.get('train',0):,} · val {sp.get('val',0):,} "
             f"· test {sp.get('test',0):,}   |   real Normal rows paired 50/50 with "
             "physics-informed synthetic faults",
             ha="center", fontsize=8.5, color=MUTED, style="italic")
    save(fig, "fig_dataset_composition.png")


if __name__ == "__main__":
    print("generating charts (batch 2) ->", os.path.relpath(OUT, ROOT))
    w = _window()
    cell_traces(w)
    thermal_zones(w)
    feature_importance()
    per_class_metrics()
    driving_modes()
    cycle_history()
    ood_panel()
    dataset_composition()
    print("done")
