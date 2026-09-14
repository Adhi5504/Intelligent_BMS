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

# Both models run behind the same 60-row pipeline buffer today
# (BUFFER_MAX_SIZE in bms_dashboard_backend.py). The difference is whether
# that 60 is a constant we chose or a shape baked into the weights.
ROWS = [
    ("Buffer today",        "60 rows  ·  pipeline constant",
                            "60 rows  ·  same buffer", False),
    ("Minimum it needs",    "10 rows  ·  rolling(10) is deepest",
                            "60 rows  ·  fixed by the weights", True),
    ("What the model eats", "the last row  ·  1 × 51",
                            "the whole window  ·  60 × 51", True),
    ("Runtime on the Pi",   "xgboost — 239 MB",
                            "torch — 1,199 MB  (5×)", True),
    ("Feature attribution", "per-feature gain, auditable",
                            "attention only, not per-feature", True),
    ("In-browser retrain",  "ships today on the dashboard",
                            "not feasible on a Pi", True),
]


def main():
    fig, ax = plt.subplots(figsize=(10.2, 3.95))
    ax.set_xlim(0, 20.4); ax.set_ylim(0, 8.3); ax.axis("off"); ax.grid(False)

    ax.text(0.25, 7.90, "Why XGBoost ships — both buffer 60 rows, only one of them has to",
            ha="left", va="center", fontsize=12.5, fontweight="bold", color=INK)
    ax.text(8.05, 7.16, "XGBoost", ha="center", va="center", fontsize=11,
            fontweight="bold", color=ACCENT)
    ax.text(15.1, 7.16, "Transformer", ha="center", va="center", fontsize=11,
            fontweight="bold", color=MUTED)

    y = 6.30
    for label, a, b, win in ROWS:
        ax.add_patch(FancyBboxPatch((5.05, y - 0.40), 6.0, 0.82,
                     boxstyle="round,pad=0,rounding_size=0.10",
                     facecolor=ACCENT_TINT if win else PANEL,
                     edgecolor=ACCENT if win else HAIRLINE,
                     linewidth=1.2 if win else 1.0, zorder=3))
        ax.add_patch(FancyBboxPatch((11.85, y - 0.40), 6.0, 0.82,
                     boxstyle="round,pad=0,rounding_size=0.10",
                     facecolor=PANEL, edgecolor=HAIRLINE, linewidth=1.0, zorder=3))
        ax.text(4.30, y, label, ha="right", va="center", fontsize=10,
                fontweight="bold", color=INK)
        ax.text(8.05, y, a, ha="center", va="center", fontsize=9.4,
                color=ACCENT if win else MUTED, zorder=5)
        ax.text(14.85, y, b, ha="center", va="center", fontsize=9.4,
                color=MUTED, zorder=5)
        if win:
            ax.text(4.72, y, "✓", ha="center", va="center", fontsize=13,
                    fontweight="bold", color=ACCENT, zorder=5)
        y -= 1.02

    ax.text(0.25, 0.22,
            "Transformer: 3,840 positional-encoding parameters shaped (1 × 60 × 64) — the 60 is in the weights.   "
            "XGBoost: 60 is BUFFER_MAX_SIZE, a constant we chose.",
            ha="left", va="center", fontsize=8.2, color=MUTED, style="italic")
    p = os.path.join(OUT, "fig_deployment_tradeoff.png")
    fig.savefig(p, facecolor=theme.BG, transparent=False)
    plt.close(fig)
    print("  wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
