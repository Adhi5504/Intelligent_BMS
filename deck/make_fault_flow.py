#!/usr/bin/env python3
"""Fault-detection architecture — the implemented pipeline as a flow diagram.

Same shape as the team's original flowchart (acquisition → mode → detection →
severity → action, with an independent hardware-protection lane), but every
block is what the code actually does:

  mode thresholds      backend/mode_classifier.py
  OOD gate             models/ood_config.json  (score < -0.5907, 2-of-3 hysteresis)
  classifier           models/bms_xgboost_model.json  (6 classes)
  confidence bands     backend/risk_scoring.py  classify_confidence()
  severity bands       backend/risk_scoring.py  classify_severity()
  persistence          backend/risk_scoring.py  5 samples to max factor
  final risk           confidence x severity, unless safety override
  hardware protection  JBD SP24S007 MOSFET gate + Arduino RUN-pin watchdog
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme
from theme import (ACCENT, WARNING, CRITICAL, INK, MUTED, HAIRLINE, PANEL, BG,
                   ACCENT_TINT, WARNING_TINT, CRITICAL_TINT)
theme.apply()
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "assets", "generated")

W, H = 44.0, 23.0          # data units
COLX = [0.55, 9.15, 17.75, 26.35, 34.95]
COLW = 7.55


def box(ax, x, y, w, h, title, sub=None, ec=ACCENT, fc=BG, fs=8.6, subfs=7.0, z=4):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0,rounding_size=0.22",
                 facecolor=fc, edgecolor=ec, linewidth=1.3, zorder=z))
    if sub:
        ax.text(x + w/2, y + h*0.66, title, ha="center", va="center", fontsize=fs,
                fontweight="bold", color=INK, zorder=z+1)
        ax.text(x + w/2, y + h*0.28, sub, ha="center", va="center", fontsize=subfs,
                color=MUTED, linespacing=1.42, zorder=z+1)
    else:
        ax.text(x + w/2, y + h/2, title, ha="center", va="center", fontsize=fs,
                fontweight="bold", color=INK, linespacing=1.38, zorder=z+1)


def diamond(ax, cx, cy, w, h, label, ec=WARNING, fc=WARNING_TINT):
    ax.add_patch(Polygon([[cx, cy+h/2], [cx+w/2, cy], [cx, cy-h/2], [cx-w/2, cy]],
                         closed=True, facecolor=fc, edgecolor=ec, linewidth=1.4, zorder=4))
    ax.text(cx, cy, label, ha="center", va="center", fontsize=8.2,
            fontweight="bold", color=INK, linespacing=1.35, zorder=5)


def arrow(ax, p0, p1, col=ACCENT, lw=1.35, rad=0.0, ls="-", ms=8):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms,
                 color=col, linewidth=lw, linestyle=ls, zorder=3,
                 connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1))


def chip(ax, x, y, w, h, label, col, fc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0,rounding_size=0.16",
                 facecolor=fc or BG, edgecolor=col, linewidth=1.15, zorder=5))
    ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=7.4,
            fontweight="bold", color=col, zorder=6)


def lane_header(ax, i, label, col=ACCENT):
    x = COLX[i]
    ax.add_patch(Rectangle((x, 21.35), COLW, 0.07, facecolor=col,
                           edgecolor="none", zorder=4))
    ax.text(x, 21.62, label, ha="left", va="bottom", fontsize=8.6,
            fontweight="bold", color=col)


def build():
    fig, ax = plt.subplots(figsize=(13.2, 6.9))
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off"); ax.grid(False)

    for i, (lab, c) in enumerate([("1 · ACQUISITION", ACCENT), ("2 · CONTEXT", ACCENT),
                                  ("3 · DETECTION", ACCENT), ("4 · RISK", WARNING),
                                  ("5 · ACTION", CRITICAL)]):
        lane_header(ax, i, lab, c)

    # lane-to-lane chevrons, on one clean band so nothing crosses a box
    for i in range(4):
        arrow(ax, (COLX[i] + COLW + 0.10, 12.4), (COLX[i + 1] - 0.10, 12.4),
              col=HAIRLINE, lw=2.2, ms=13)

    # ---------------------------------------------------- 1. acquisition
    x = COLX[0]
    box(ax, x, 18.30, COLW, 2.15, "8S2P battery pack",
        "16 × INR21700-M50 · 33.6 V · 8 Ah", fc=ACCENT_TINT, subfs=6.8)
    box(ax, x, 15.40, COLW, 2.30, "JBD SP24S007 sensing",
        "8 cell taps · 4 NTC\npack V / I · coulomb count")
    box(ax, x, 12.55, COLW, 2.25, "BLE @ 1 Hz  →  Pi 5",
        "bleak · notify 0xFF01\nframe reassembly")
    box(ax, x, 9.65, COLW, 2.30, "Data-integrity check",
        "NaN or all-zero row →\nDATA INTEGRITY FAULT", ec=WARNING)
    box(ax, x, 6.75, COLW, 2.30, "Feature engineering",
        "60-row buffer → 51 features\nrolling(10) · d/dt · cell rates", subfs=6.8)
    for y0, y1 in ((18.30, 17.70), (15.40, 14.80), (12.55, 11.95), (9.65, 9.05)):
        arrow(ax, (x + COLW/2, y0), (x + COLW/2, y1))

    # -------------------------------------------------------- 2. context
    x = COLX[1]
    diamond(ax, x + COLW/2, 19.30, 6.6, 2.7, "Operating\nmode ?")
    ax.text(x + COLW/2, 17.35, "|I| vs idle_threshold  ·  dI/dt vs stability_threshold\n"
            "5-sample hysteresis stops flapping",
            ha="center", va="center", fontsize=6.6, color=MUTED, linespacing=1.45)
    cw = (COLW - 0.5) / 2
    for k, (m, c) in enumerate([("IDLE", MUTED), ("ACCEL", CRITICAL),
                                ("CRUISE", ACCENT), ("DECEL", WARNING)]):
        chip(ax, x + (k % 2) * (cw + 0.5), 15.20 - (k // 2) * 1.12, cw, 0.92, m, c)
    arrow(ax, (x + COLW/2, 17.95), (x + COLW/2, 17.75), col=WARNING)
    arrow(ax, (x + COLW/2, 16.70), (x + COLW/2, 16.20), col=WARNING)
    box(ax, x, 11.35, COLW, 2.35, "Mode-specific thresholds",
        "a sag under ACCEL is normal,\nthe same sag at IDLE is not",
        ec=WARNING, fc=WARNING_TINT, subfs=6.8)
    arrow(ax, (x + COLW/2, 14.08), (x + COLW/2, 13.75), col=WARNING)
    box(ax, x, 8.20, COLW, 2.35, "One-hot into the vector",
        "4 mode flags → 12.4%\nof total model gain", subfs=6.8)
    arrow(ax, (x + COLW/2, 11.35), (x + COLW/2, 10.60), col=WARNING)

    # ------------------------------------------------------ 3. detection
    x = COLX[2]
    box(ax, x, 18.30, COLW, 2.15, "OOD gate — IsolationForest",
        "score < −0.5907 · 2-of-3 hysteresis", ec=WARNING, fc=WARNING_TINT,
        fs=8.2, subfs=6.6)
    box(ax, x + 0.55, 15.35, COLW - 1.1, 2.05, "UNKNOWN_FAULT_OOD",
        "escalated, never labelled", ec=CRITICAL, fc=CRITICAL_TINT,
        fs=8.2, subfs=6.8)
    arrow(ax, (x + COLW/2 - 1.1, 18.30), (x + COLW/2 - 1.1, 17.45), col=CRITICAL)
    ax.text(x + COLW/2 - 0.85, 17.88, "fail", ha="left", va="center",
            fontsize=6.6, fontweight="bold", color=CRITICAL)
    # pass path bypasses the dead-end box on the right
    ax.add_patch(FancyArrowPatch((x + COLW - 0.30, 18.30), (x + COLW - 0.30, 13.05),
                 arrowstyle="-|>", mutation_scale=8, color=ACCENT, lw=1.35,
                 zorder=3, connectionstyle="arc3,rad=0.0"))
    ax.text(x + COLW - 0.10, 16.4, "pass", ha="left", va="center", rotation=90,
            fontsize=6.6, fontweight="bold", color=ACCENT)
    box(ax, x, 12.55, COLW, 2.15, "XGBoost — 6 classes",
        "predicts on the last row · 0.46 ms", fc=ACCENT_TINT, subfs=6.8)
    six = ["Normal", "Cell Imbalance", "Weak Cell",
           "Overvoltage", "Undervoltage", "Overtemperature"]
    for k, nm in enumerate(six):
        chip(ax, x + 0.35, 11.35 - k * 1.00, COLW - 0.7, 0.84, nm,
             ACCENT if k == 0 else CRITICAL)
    arrow(ax, (x + COLW/2, 12.55), (x + COLW/2, 12.25))

    # ----------------------------------------------------------- 4. risk
    x = COLX[3]
    box(ax, x, 18.30, COLW, 2.15, "Prediction confidence",
        "low / moderate / high\nat 0.35 and 0.85", ec=WARNING, subfs=6.8)
    box(ax, x, 15.35, COLW, 2.35, "Physical severity",
        "distance warn → critical,\n× base weight per class", ec=WARNING, subfs=6.8)
    box(ax, x, 12.40, COLW, 2.35, "Persistence factor",
        "min(count / 5, 1.0) —\nrepeat frames raise severity", ec=WARNING, subfs=6.8)
    box(ax, x, 9.45, COLW, 2.35, "Final risk score",
        "confidence × severity,\nunless a safety override fires",
        ec=CRITICAL, fc=CRITICAL_TINT, subfs=6.8)
    for y0, y1 in ((18.30, 17.70), (15.35, 14.75), (12.40, 11.80)):
        arrow(ax, (x + COLW/2, y0), (x + COLW/2, y1), col=WARNING)
    bw = (COLW - 0.75) / 4
    for k, (lab, c) in enumerate([("Low", MUTED), ("Mod", ACCENT),
                                  ("High", WARNING), ("Crit", CRITICAL)]):
        chip(ax, x + k * (bw + 0.25), 7.95, bw, 0.92, lab, c)
    ax.text(x + COLW/2, 7.35, "band edges  0.35 · 0.65 · 0.85", ha="center",
            va="center", fontsize=6.6, color=MUTED)
    arrow(ax, (x + COLW/2, 9.45), (x + COLW/2, 8.87), col=CRITICAL)

    # --------------------------------------------------------- 5. action
    x = COLX[4]
    diamond(ax, x + COLW/2, 19.35, 6.6, 2.9, "Fault\npersistent ?", ec=CRITICAL,
            fc=CRITICAL_TINT)
    box(ax, x, 15.35, COLW, 2.15, "Corrective action",
        "operator instruction shown", ec=CRITICAL, subfs=6.8)
    arrow(ax, (x + COLW/2, 17.90), (x + COLW/2, 17.50), col=CRITICAL)
    ax.text(x + COLW/2 + 0.25, 17.70, "yes", ha="left", va="center", fontsize=6.6,
            fontweight="bold", color=CRITICAL)
    box(ax, x, 12.40, COLW, 2.25, "Alert history",
        "timestamp · type · severity\nmeasured · threshold · resolved", subfs=6.6)
    arrow(ax, (x + COLW/2, 15.35), (x + COLW/2, 14.65), col=CRITICAL)
    box(ax, x, 9.45, COLW, 2.25, "Cycle comparison",
        "expected vs actual sag\nagainst 39 logged cycles", subfs=6.8)
    arrow(ax, (x + COLW/2, 12.40), (x + COLW/2, 11.70))
    box(ax, x, 6.85, COLW, 1.90, "Continuous monitoring",
        "next sample, 1 s later  ↻", fc=PANEL, ec=HAIRLINE, subfs=6.8)
    arrow(ax, (x + COLW/2, 9.45), (x + COLW/2, 8.75))

    # ------------------------------- independent hardware-protection lane
    ax.add_patch(FancyBboxPatch((0.55, 0.45), W - 1.1, 5.35,
                 boxstyle="round,pad=0,rounding_size=0.26", facecolor=PANEL,
                 edgecolor=CRITICAL, linewidth=1.5, linestyle=(0, (6, 3)), zorder=1))
    ax.text(1.15, 5.10, "FAST HARDWARE PROTECTION — independent of everything above, "
            "runs even if the Pi is down",
            ha="left", va="center", fontsize=9, fontweight="bold", color=CRITICAL)
    hb = [("JBD protection logic", "over-/under-voltage · over-current\nover-temp · short circuit"),
          ("MOSFET gate control", "charge and discharge FETs\nswitched at the pack"),
          ("Immediate disconnect", "load isolated in hardware,\nno software in the path"),
          ("Arduino Uno R4 watchdog", "serial heartbeat from the Pi,\nmissed beat → RUN-pin reset")]
    bwid = (W - 3.4 - 3 * 0.85) / 4
    for k, (t, s_) in enumerate(hb):
        bx = 1.15 + k * (bwid + 0.85)
        box(ax, bx, 1.00, bwid, 3.25, t, s_, ec=CRITICAL, fc=BG, fs=8.2, subfs=6.9)
        if k < 3:
            arrow(ax, (bx + bwid, 2.62), (bx + bwid + 0.80, 2.62), col=CRITICAL, lw=1.3)

    p = os.path.join(OUT, "diag_fault_flow.png")
    fig.savefig(p, facecolor=theme.BG, transparent=False)
    plt.close(fig)
    print("  wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    build()
