#!/usr/bin/env python3
"""The model-selection figure — every number measured on this machine.

Accuracy is over the same 30,000-row held-out test split for all six models;
latency is the median single-row prediction, which is what the edge
deployment actually does.
"""
import os, sys, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme
from theme import (ACCENT, WARNING, CRITICAL, INK, MUTED, HAIRLINE, PANEL, BG,
                   ACCENT_TINT)
theme.apply()
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BM   = os.path.join(ROOT, "outputs", "benchmark")
OUT  = os.path.join(ROOT, "assets", "generated")

ORDER = ["XGBoost", "Transformer", "LSTM", "Random Forest", "SVM (RBF)", "Rule-based BMS"]


def load():
    r = {}
    for f in ("sklearn_results.json", "torch_results.json", "rule_results.json"):
        p = os.path.join(BM, f)
        if os.path.exists(p):
            r.update(json.load(open(p)))
    return r


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor=theme.BG, transparent=False)
    plt.close(fig)
    print("  wrote", os.path.relpath(p, ROOT))


def comparison(r):
    names = [n for n in ORDER if n in r]
    acc = [r[n]["accuracy"] * 100 for n in names]
    lat = [max(r[n]["latency_ms"], 0.003) for n in names]
    cols = [ACCENT if n == "XGBoost" else
            (CRITICAL if n == "Rule-based BMS" else HAIRLINE) for n in names]
    edge = [INK if n == "XGBoost" else
            (CRITICAL if n == "Rule-based BMS" else "#9AA9BC") for n in names]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.8, 4.6),
                                 gridspec_kw={"width_ratios": [1.25, 1]})
    y = np.arange(len(names))[::-1]

    a1.barh(y, acc, color=cols, edgecolor=edge, linewidth=1.0, height=0.62, zorder=3)
    for yi, v, n in zip(y, acc, names):
        a1.text(v + 1.4, yi, f"{v:.2f}%", va="center", fontsize=10.5,
                fontweight="bold" if n == "XGBoost" else "normal",
                color=ACCENT if n == "XGBoost" else MUTED)
    a1.set_yticks(y); a1.set_yticklabels(names, fontsize=10.5)
    a1.set_xlim(0, 108); a1.set_xlabel("Accuracy on the held-out test split (%)")
    a1.set_title("Accuracy", fontsize=12.5, pad=10)
    a1.grid(axis="y", visible=False)
    theme.strip(a1)

    a2.barh(y, lat, color=cols, edgecolor=edge, linewidth=1.0, height=0.62, zorder=3)
    for yi, v in zip(y, lat):
        a2.text(v * 1.35, yi, f"{v:.3g} ms", va="center", fontsize=10, color=MUTED)
    a2.set_xscale("log")
    a2.set_yticks(y); a2.set_yticklabels([])
    a2.set_xlim(0.002, 400)
    a2.set_xlabel("Median single-row inference (ms, log scale)")
    a2.set_title("Latency", fontsize=12.5, pad=10)
    a2.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    a2.grid(axis="y", visible=False)
    theme.strip(a2)

    fig.text(0.5, -0.04,
             "Same 30,000-row test split and same 51 features for every model. "
             "Sequence models additionally see a 60-row lookback window.",
             ha="center", fontsize=8.5, color=MUTED, style="italic")
    save(fig, "fig_model_benchmark.png")


def tradeoff(r):
    """Accuracy against model size — the deployability view."""
    names = [n for n in ORDER if n in r]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for n in names:
        x = max(r[n]["size_mb"], 0.02)
        y = r[n]["accuracy"] * 100
        big = n == "XGBoost"
        ax.scatter(x, y, s=260 if big else 150,
                   color=ACCENT if big else (CRITICAL if n == "Rule-based BMS" else "#B9C6D6"),
                   edgecolor=INK if big else "none", linewidth=1.6, zorder=4)
        ax.annotate(n, (x, y), xytext=(0, 15 if not big else 20),
                    textcoords="offset points", ha="center", fontsize=9.5,
                    fontweight="bold" if big else "normal",
                    color=ACCENT if big else MUTED)
    ax.set_xscale("log")
    ax.set_xlabel("Model size on disk (MB, log scale)")
    ax.set_ylabel("Test accuracy (%)")
    ax.set_ylim(10, 106)
    ax.set_title("Accuracy per megabyte", pad=14)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.axhspan(90, 106, color=ACCENT_TINT, alpha=0.35, zorder=1)
    ax.text(ax.get_xlim()[1]*0.85, 92, "deployable band", fontsize=9,
            color=ACCENT, ha="right", style="italic")
    theme.strip(ax)
    save(fig, "fig_model_tradeoff.png")


if __name__ == "__main__":
    r = load()
    print("models loaded:", list(r))
    comparison(r)
    if len(r) >= 4:
        tradeoff(r)
