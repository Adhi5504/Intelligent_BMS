#!/usr/bin/env python3
"""Generate the data-driven figures for the AI-PBMS deck.

Every number here is either taken verbatim from the project brief or
measured from a file in this repository. Nothing is interpolated to make
a chart look fuller -- where the source data is missing the figure says so.
"""
import os, sys, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme
from theme import (ACCENT, WARNING, CRITICAL, INK, MUTED, HAIRLINE, PANEL, BG,
                   ACCENT_TINT, WARNING_TINT, CRITICAL_TINT)
theme.apply()
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "assets", "generated")
os.makedirs(OUT, exist_ok=True)

def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor=theme.BG, transparent=False)
    plt.close(fig)
    print("  wrote", os.path.relpath(p, ROOT))


# ---------------------------------------------------------------- 1. skew
def fault_class_distribution():
    """Only two proportions are given in the brief: Cell Imbalance = 70.2%
    and, by closure, everything else = 29.8%. The per-class split of that
    remainder is not in the brief and is not recoverable from any labelled
    file in data/, so it is shown as one aggregate bar rather than invented."""
    labels = ["Cell Imbalance", "Other five classes\n(Normal, Weak Cell, Over-/Under-\nvoltage, Overtemperature)"]
    vals   = [70.2, 29.8]
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    bars = ax.bar(labels, vals, width=0.52,
                  color=[CRITICAL, HAIRLINE], zorder=3)
    bars[0].set_edgecolor(CRITICAL); bars[1].set_edgecolor(HAIRLINE)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v + 2.0, f"{v:.1f}%",
                ha="center", va="bottom", fontsize=17, fontweight="bold",
                color=CRITICAL if v > 50 else MUTED)
    ax.set_ylim(0, 88)
    ax.set_ylabel("Share of labelled rows (%)")
    ax.set_title("Label skew in the logged dataset", pad=14)
    ax.xaxis.set_tick_params(labelsize=10)
    ax.grid(axis="x", visible=False)
    theme.strip(ax)
    ax.annotate("driven by cell_v1 sitting\n~0.25 V below pack median",
                xy=(0, 70.2), xytext=(0.42, 52),
                fontsize=10, color=MUTED, ha="left",
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))
    fig.text(0.5, -0.035,
             "Remaining 29.8% shown as one bar — per-class split not "
             "characterised in the source data.",
             ha="center", fontsize=8.5, color=MUTED, style="italic")
    save(fig, "fig_class_distribution.png")


# ------------------------------------------------------ 2. confusion matrix
def confusion_matrix_fig(cm, names):
    """Row-normalised (recall) heatmap of the shipped XGBoost model."""
    cmn = cm / cm.sum(axis=1, keepdims=True) * 100.0
    fig, ax = plt.subplots(figsize=(7.6, 6.2))
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("acc", [BG, "#9FD9DF", ACCENT])
    im = ax.imshow(cmn, cmap=cmap, vmin=0, vmax=100)
    ax.set_xticks(range(len(names))); ax.set_yticks(range(len(names)))
    ax.set_xticklabels(names, rotation=38, ha="right", fontsize=9.5, color=INK)
    ax.set_yticklabels(names, fontsize=9.5, color=INK)
    ax.set_xlabel("Predicted class", labelpad=8)
    ax.set_ylabel("True class", labelpad=8)
    ax.set_title("XGBoost confusion matrix — row-normalised recall (%)", pad=14)
    for i in range(len(names)):
        for j in range(len(names)):
            v = cmn[i, j]
            if v < 0.05:
                continue
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=9.5,
                    fontweight="bold" if i == j else "normal",
                    color=BG if v > 55 else (INK if v > 5 else MUTED))
    ax.set_xticks(np.arange(-.5, len(names), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(names), 1), minor=True)
    ax.grid(which="minor", color=HAIRLINE, linewidth=1.0)
    ax.grid(which="major", visible=False)
    ax.tick_params(which="minor", length=0)
    for sp in ax.spines.values():
        sp.set_color(HAIRLINE)
    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
    cb.set_label("recall (%)", color=MUTED, fontsize=9)
    cb.outline.set_edgecolor(HAIRLINE)
    cb.ax.tick_params(colors=MUTED, labelsize=8.5)
    save(fig, "fig_confusion_matrix.png")


def build_confusion_matrix():
    """Run models/bms_xgboost_model.json over the held-out test split."""
    import pandas as pd, joblib, xgboost as xgb
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    from train_xgboost import engineer_features
    names = ["Normal", "Cell Imbalance", "Weak Cell",
             "Overvoltage", "Undervoltage", "Overtemperature"]
    raw = pd.read_excel(os.path.join(ROOT, "data",
                                     "augmented_telemetry_dataset.xlsx"), sheet_name=0)
    feats = json.load(open(os.path.join(ROOT, "models", "feature_columns.json")))
    parts = [engineer_features(g.reset_index(drop=True))
             for _, g in raw.groupby(["split", "fault_label"])]
    dfp = pd.concat(parts, ignore_index=True)
    te = dfp[dfp["split"] == "test"]
    X = joblib.load(os.path.join(ROOT, "models", "bms_scaler.joblib")).transform(te[feats].values)
    y = te["fault_label"].values
    m = xgb.XGBClassifier(); m.load_model(os.path.join(ROOT, "models", "bms_xgboost_model.json"))
    yp = m.predict(X)
    from sklearn.metrics import confusion_matrix, accuracy_score
    cm = confusion_matrix(y, yp)
    acc = accuracy_score(y, yp)
    json.dump({"accuracy": float(acc), "rows": int(len(y)),
               "matrix": cm.tolist(), "classes": names},
              open(os.path.join(OUT, "confusion_matrix_source.json"), "w"), indent=2)
    print(f"  [measured] shipped-checkpoint test accuracy = {acc*100:.2f}% on {len(y)} rows")
    confusion_matrix_fig(cm, names)
    return acc


# ------------------------------------------------- 3. measured XGBoost panel
def xgboost_performance_panel():
    """The brief supplies accuracy and latency for XGBoost only; no accuracy
    or latency figures are given for the Transformer, LSTM, Random Forest,
    SVM or the rule-based baseline, so a grouped comparison bar chart cannot
    be drawn without inventing five pairs of numbers. Slide 4 carries the
    qualitative comparison as a table instead; this panel states the two
    values that do exist."""
    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.6); ax.axis("off")

    def card(x, w, big, unit, cap, col, tint):
        ax.add_patch(FancyBboxPatch((x, 0.55), w, 4.3,
                                    boxstyle="round,pad=0,rounding_size=0.16",
                                    facecolor=tint, edgecolor=col, linewidth=1.4))
        ax.text(x + w/2, 3.35, big, ha="center", va="center",
                fontsize=34, fontweight="bold", color=col)
        ax.text(x + w/2, 2.45, unit, ha="center", va="center",
                fontsize=12, color=col)
        ax.text(x + w/2, 1.35, cap, ha="center", va="center",
                fontsize=10, color=MUTED, linespacing=1.5)

    card(0.3, 4.5, "98.55", "% test accuracy", "six-class fault\nclassifier", ACCENT, ACCENT_TINT)
    card(5.2, 4.5, "0.85", "ms per inference", "measured on\nRaspberry Pi 5", WARNING, WARNING_TINT)
    ax.text(5.0, 5.25, "XGBoost — deployed edge model", ha="center", va="center",
            fontsize=14, fontweight="bold", color=INK)
    save(fig, "fig_model_performance.png")


# ------------------------------------------------ 4. confidence band diagram
def confidence_bands():
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    segs = [(0.00, 0.50, "ABSTAIN",  "no action issued\nsample routed to review", MUTED,    PANEL),
            (0.50, 0.85, "WARNING",  "operator advisory\nlogged, non-blocking",   WARNING,  WARNING_TINT),
            (0.85, 1.00, "ALERT",    "acted on\ncorrective action shown",         CRITICAL, CRITICAL_TINT)]
    y0, h = 0.46, 0.30
    for lo, hi, name, sub, col, tint in segs:
        ax.add_patch(Rectangle((lo, y0), hi - lo, h, facecolor=tint,
                               edgecolor=col, linewidth=1.6, zorder=2))
        ax.text((lo + hi)/2, y0 + h*0.60, name, ha="center", va="center",
                fontsize=13, fontweight="bold", color=col, zorder=3)
        ax.text((lo + hi)/2, y0 + h*0.22, f"{lo:.2f} – {hi:.2f}", ha="center",
                va="center", fontsize=9.5, color=col, zorder=3)
        ax.text((lo + hi)/2, y0 - 0.11, sub, ha="center", va="top",
                fontsize=9, color=MUTED, linespacing=1.5)
    for t in (0.00, 0.50, 0.85, 1.00):
        ax.plot([t, t], [y0 - 0.03, y0], color=HAIRLINE, lw=1.1, zorder=1)
        ax.text(t, y0 + h + 0.055, f"{t:.2f}", ha="center", va="bottom",
                fontsize=9.5, color=MUTED)
    ax.annotate("", xy=(1.0, 0.95), xytext=(0.0, 0.95),
                arrowprops=dict(arrowstyle="->", color=HAIRLINE, lw=1.2))
    ax.text(0.5, 0.99, "model confidence  p(class)", ha="center", va="bottom",
            fontsize=10, color=MUTED)
    save(fig, "fig_confidence_bands.png")


# ------------------------------------------------------- 5. OCV–SOC overlay
def ocv_soc():
    """NMC curve is the measured OCV(SOC) breakpoint table lifted from the
    project's own 2RC parameter-estimation model (E2RC_FINAL_4000sec_model.mdl,
    1-D Lookup Table block). No LFP cell was characterised in this project, so
    the LFP side is drawn as its datasheet voltage window from the brief
    (2.50-3.65 V), explicitly labelled as a window and not as a measured curve."""
    import matplotlib as _mpl
    _prev = dict(_mpl.rcParams)
    _mpl.rcParams.update({"font.size": 15, "axes.titlesize": 18,
                          "axes.labelsize": 15, "xtick.labelsize": 13.5,
                          "ytick.labelsize": 13.5})
    soc = np.array([43.3, 50, 55, 60, 65, 70, 75, 80, 85, 90.9])
    pack = np.array([27.3, 28.2, 28.9, 29.6, 30.3, 30.9, 31.4, 31.8, 32.2, 32.58])
    cell = pack / 8.0

    fig, ax = plt.subplots(figsize=(6.2, 6.4))
    ax.axhspan(2.50, 3.65, facecolor=PANEL, edgecolor=HAIRLINE,
               linewidth=1.0, zorder=1)
    ax.text(44.6, 3.12, "LFP operating window  2.50 – 3.65 V/cell",
            fontsize=10, color=MUTED, va="center", zorder=3)
    ax.text(44.6, 2.88, "curve not characterised in this project",
            fontsize=8.5, color=MUTED, style="italic", va="center", zorder=3)

    ax.plot(soc, cell, marker="o", ms=5.5, lw=2.4, color=ACCENT,
            markerfacecolor=theme.BG, markeredgewidth=1.8, zorder=4,
            label="NMC (measured, 8S2P pack ÷ 8)")

    # quantify the usable slope of the measured segment
    dv = (cell[-1] - cell[1]) * 1000.0
    ds = soc[-1] - soc[1]
    ax.annotate(f"{dv/ds:.1f} mV per 1% SOC\n→ OCV is a usable SOC observer",
                xy=(70, cell[5]), xytext=(50.5, 4.18), fontsize=13, color=ACCENT,
                ha="left", linespacing=1.5,
                arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.2))

    ax.set_xlim(42, 93); ax.set_ylim(2.35, 4.35)
    ax.set_xlabel("State of charge (%)")
    ax.set_ylabel("Open-circuit voltage (V / cell)")
    ax.set_title("OCV–SOC: why chemistry swap is not a constant offset", pad=14)
    ax.legend(loc="lower right", fontsize=12, labelcolor=INK)
    theme.strip(ax)
    fig.text(0.5, -0.075,
             "NMC breakpoints from this project's 2RC parameter-estimation "
             "lookup table;\nLFP shown as its datasheet window only.",
             ha="center", fontsize=11, color=MUTED, style="italic", linespacing=1.4)
    save(fig, "fig_ocv_soc.png")
    _mpl.rcParams.update(_prev)


if __name__ == "__main__":
    print("generating charts ->", os.path.relpath(OUT, ROOT))
    fault_class_distribution()
    xgboost_performance_panel()
    confidence_bands()
    ocv_soc()
    build_confusion_matrix()
    print("done")
