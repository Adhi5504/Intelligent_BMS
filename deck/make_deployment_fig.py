#!/usr/bin/env python3
"""Head-to-head on the constraints that decided the deployment.

Accuracy is not on this figure on purpose — the table above it already
carries accuracy, and accuracy is not why XGBoost shipped. Every number
here is measured: parameter counts and the lookback from the benchmark
run, package sizes from the installed runtimes on this machine.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme
from theme import (ACCENT, WARNING, CRITICAL, INK, MUTED, HAIRLINE, PANEL, BG,
                   ACCENT_TINT, WARNING_TINT)
theme.apply()
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "assets", "generated")
BM   = os.path.join(ROOT, "outputs", "benchmark")

ROWS = [
    ("Cold start",          "1 row  ·  first call at t = 1 s",
                            "60 rows  ·  blind for 60 s", True),
    ("Runtime on the Pi",   "xgboost — 239 MB",
                            "torch — 1,199 MB  (5×)", True),
    ("Fixed input shape",   "any row, any time",
                            "positional encoding pins it to 60", True),
    ("Feature attribution", "per-feature gain, auditable",
                            "attention only, not per-feature", True),
    ("In-browser retrain",  "ships today on the dashboard",
                            "not feasible on a Pi", True),
]


def main():
    fig, ax = plt.subplots(figsize=(10.2, 3.55))
    ax.set_xlim(0, 20.4); ax.set_ylim(0, 7.5); ax.axis("off"); ax.grid(False)

    ax.text(0.25, 7.08, "Why XGBoost ships anyway — the constraints that actually decided it",
            ha="left", va="center", fontsize=12.5, fontweight="bold", color=INK)
    ax.text(8.05, 6.32, "XGBoost", ha="center", va="center", fontsize=11,
            fontweight="bold", color=ACCENT)
    ax.text(15.1, 6.32, "Transformer", ha="center", va="center", fontsize=11,
            fontweight="bold", color=MUTED)

    y = 5.42
    for label, a, b, win in ROWS:
        ax.add_patch(FancyBboxPatch((5.05, y - 0.40), 6.0, 0.82,
                     boxstyle="round,pad=0,rounding_size=0.10",
                     facecolor=ACCENT_TINT, edgecolor=ACCENT, linewidth=1.2, zorder=3))
        ax.add_patch(FancyBboxPatch((11.85, y - 0.40), 6.0, 0.82,
                     boxstyle="round,pad=0,rounding_size=0.10",
                     facecolor=PANEL, edgecolor=HAIRLINE, linewidth=1.0, zorder=3))
        ax.text(4.30, y, label, ha="right", va="center", fontsize=10,
                fontweight="bold", color=INK)
        ax.text(8.05, y, a, ha="center", va="center", fontsize=9.4,
                color=ACCENT, zorder=5)
        ax.text(14.85, y, b, ha="center", va="center", fontsize=9.4,
                color=MUTED, zorder=5)
        ax.text(4.72, y, "✓", ha="center", va="center", fontsize=13,
                fontweight="bold", color=ACCENT, zorder=5)
        y -= 1.02

    ax.text(0.25, 0.24,
            "Transformer is 74,630 parameters, 3,840 of them positional encoding — "
            "that encoding is what fixes the input at exactly 60 rows.",
            ha="left", va="center", fontsize=8.4, color=MUTED, style="italic")
    p = os.path.join(OUT, "fig_deployment_tradeoff.png")
    fig.savefig(p, facecolor=theme.BG, transparent=False)
    plt.close(fig)
    print("  wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
