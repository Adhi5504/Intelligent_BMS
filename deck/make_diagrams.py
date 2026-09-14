#!/usr/bin/env python3
"""Programmatic, vector-style schematics for the AI-PBMS deck.

Everything is drawn with matplotlib primitives -- no clipart, no bitmaps.
Component values come from the brief.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme
from theme import (ACCENT, WARNING, CRITICAL, INK, MUTED, HAIRLINE, PANEL, BG,
                   ACCENT_TINT, WARNING_TINT, CRITICAL_TINT)
theme.apply()
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle, Polygon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "assets", "generated")
os.makedirs(OUT, exist_ok=True)


def canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_aspect("equal"); ax.axis("off")
    ax.grid(False)
    return fig, ax


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor=theme.BG, transparent=False)
    plt.close(fig)
    print("  wrote", os.path.relpath(p, ROOT))


def box(ax, x, y, w, h, label, sub=None, fc=BG, ec=ACCENT, lw=1.6,
        fs=11, subfs=8.6, tc=None, round_size=0.10):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f"round,pad=0,rounding_size={round_size}",
                 facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3))
    tc = tc or INK
    if sub:
        ax.text(x + w/2, y + h*0.63, label, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=tc, zorder=4)
        ax.text(x + w/2, y + h*0.27, sub, ha="center", va="center",
                fontsize=subfs, color=MUTED, linespacing=1.45, zorder=4)
    else:
        ax.text(x + w/2, y + h/2, label, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=tc,
                linespacing=1.45, zorder=4)


def arrow(ax, p0, p1, color=ACCENT, lw=1.7, style="-|>", ls="-", rad=0.0, ms=10):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms,
                 color=color, linewidth=lw, linestyle=ls, zorder=2,
                 connectionstyle=f"arc3,rad={rad}",
                 shrinkA=2, shrinkB=2))


# ============================================================ 1. 8S2P pack
def pack_topology():
    fig, ax = canvas(9.2, 4.6, (0, 18.4), (0, 9.2))
    x0, y0 = 1.45, 2.55
    cw, ch, gap = 1.34, 2.55, 0.52       # cell size + inter-group gap

    for s in range(8):
        gx = x0 + s * (cw + gap)
        # the 2P group outline
        ax.add_patch(FancyBboxPatch((gx - 0.17, y0 - 0.22), cw + 0.34, ch + 0.44,
                     boxstyle="round,pad=0,rounding_size=0.12",
                     facecolor=PANEL, edgecolor=HAIRLINE, linewidth=1.1, zorder=1))
        for p in range(2):                # two parallel cells, drawn as a stack
            cy = y0 + p * (ch/2 + 0.06)
            ax.add_patch(FancyBboxPatch((gx, cy), cw, ch/2 - 0.06,
                         boxstyle="round,pad=0,rounding_size=0.07",
                         facecolor=BG, edgecolor=ACCENT, linewidth=1.4, zorder=3))
            ax.plot([gx + 0.20, gx + cw - 0.20], [cy + ch/4 - 0.03]*2,
                    color=ACCENT, lw=1.2, zorder=4)
            ax.plot([gx + cw/2]*2, [cy + 0.12, cy + ch/2 - 0.18],
                    color=HAIRLINE, lw=0.9, zorder=3)
        ax.text(gx + cw/2, y0 - 0.62, f"S{s+1}", ha="center", va="top",
                fontsize=10, fontweight="bold", color=INK)
        # series link between adjacent groups
        if s < 7:
            ax.plot([gx + cw + 0.17, gx + cw + gap - 0.17], [y0 + ch/2]*2,
                    color=ACCENT, lw=2.0, zorder=2, solid_capstyle="round")
        # per-cell sense tap up to the BMS rail
        ax.plot([gx + cw/2, gx + cw/2], [y0 + ch + 0.22, 7.35],
                color=WARNING, lw=1.0, ls=(0, (3, 2)), zorder=2)
        ax.add_patch(Circle((gx + cw/2, 7.35), 0.085, facecolor=WARNING,
                            edgecolor="none", zorder=4))

    # BMS sense rail
    ax.plot([x0 + cw/2 - 0.35, x0 + 7*(cw+gap) + cw/2 + 0.35], [7.35]*2,
            color=WARNING, lw=2.0, zorder=3, solid_capstyle="round")
    ax.text(9.2, 7.72, "8 × per-cell voltage taps  →  JBD BMS",
            ha="center", va="bottom", fontsize=10.5, fontweight="bold", color=WARNING)

    # pack terminals
    for tx, lab, col in [(0.72, "+", CRITICAL), (17.6, "−", INK)]:
        ax.add_patch(Circle((tx, y0 + ch/2), 0.30, facecolor=BG,
                            edgecolor=col, linewidth=1.8, zorder=4))
        ax.text(tx, y0 + ch/2, lab, ha="center", va="center", fontsize=14,
                fontweight="bold", color=col, zorder=5)
    ax.plot([1.02, x0 - 0.17], [y0 + ch/2]*2, color=ACCENT, lw=2.0, zorder=2)
    ax.plot([x0 + 7*(cw+gap) + cw + 0.17, 17.30], [y0 + ch/2]*2, color=ACCENT, lw=2.0, zorder=2)

    ax.text(9.2, 1.28, "8S  →  33.6 V nominal bus          "
                       "2P  →  8 Ah capacity & current headroom",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color=INK)
    ax.text(9.2, 0.62, "16 cells · LG INR21700-M50 · per-cell resolution is what "
                       "makes imbalance detectable",
            ha="center", va="center", fontsize=9.2, color=MUTED)
    ax.text(9.2, 8.62, "8S2P pack topology", ha="center", va="center",
            fontsize=14, fontweight="bold", color=INK)
    save(fig, "diag_pack_8s2p.png")


# ====================================================== 2. 2RC Thevenin ECM
def _resistor(ax, x, y, w, label, value, col=ACCENT):
    """Zig-zag resistor centred on (x + w/2, y)."""
    n, amp = 6, 0.26
    xs = np.linspace(x + w*0.20, x + w*0.80, n*2 + 1)
    ys = [y] + [y + amp*(-1)**i for i in range(n*2 - 1)] + [y]
    ax.plot([x, xs[0]], [y, y], color=col, lw=1.8, zorder=3)
    ax.plot(xs, ys, color=col, lw=1.8, zorder=3, solid_joinstyle="miter")
    ax.plot([xs[-1], x + w], [y, y], color=col, lw=1.8, zorder=3)
    ax.text(x + w/2, y + 0.62, label, ha="center", va="bottom",
            fontsize=11.5, fontweight="bold", color=INK)
    ax.text(x + w/2, y - 0.66, value, ha="center", va="top",
            fontsize=10, color=ACCENT, fontweight="bold")


def _capacitor(ax, x, y, w, label, value, col=ACCENT):
    cx, g, ph = x + w/2, 0.13, 0.42
    ax.plot([x, cx - g], [y, y], color=col, lw=1.8, zorder=3)
    ax.plot([cx + g, x + w], [y, y], color=col, lw=1.8, zorder=3)
    ax.plot([cx - g]*2, [y - ph, y + ph], color=col, lw=2.4, zorder=3)
    ax.plot([cx + g]*2, [y - ph, y + ph], color=col, lw=2.4, zorder=3)
    ax.text(cx, y - 0.72, label, ha="center", va="top",
            fontsize=11.5, fontweight="bold", color=INK)
    ax.text(cx, y - 1.28, value, ha="center", va="top",
            fontsize=10, color=ACCENT, fontweight="bold")


def ecm_2rc():
    fig, ax = canvas(9.4, 4.9, (0, 18.8), (0, 9.8))
    yt, yb = 6.35, 1.75          # top rail, bottom rail

    # --- OCV source ---
    sx, sr = 2.05, 0.86
    ax.add_patch(Circle((sx, (yt + yb)/2), sr, facecolor=BG,
                        edgecolor=ACCENT, linewidth=1.9, zorder=3))
    ax.text(sx, (yt+yb)/2 + 0.30, "+", ha="center", va="center", fontsize=15,
            color=ACCENT, fontweight="bold", zorder=4)
    ax.text(sx, (yt+yb)/2 - 0.34, "−", ha="center", va="center", fontsize=15,
            color=ACCENT, fontweight="bold", zorder=4)
    ax.plot([sx, sx], [(yt+yb)/2 + sr, yt], color=ACCENT, lw=1.8, zorder=2)
    ax.plot([sx, sx], [yb, (yt+yb)/2 - sr], color=ACCENT, lw=1.8, zorder=2)
    ax.text(sx - 1.28, (yt+yb)/2, "OCV(SOC)", ha="center", va="center",
            fontsize=11.5, fontweight="bold", color=INK, rotation=90)

    # --- R0 in series on the top rail ---
    r0x, r0w = 4.15, 2.15
    ax.plot([sx, r0x], [yt, yt], color=ACCENT, lw=1.8, zorder=2)
    _resistor(ax, r0x, yt, r0w, "R₀", "0.06142 Ω")

    # --- the two RC branches ---
    def rc(x, w, rl, rv, cl, cv, tint):
        ax.add_patch(FancyBboxPatch((x - 0.30, yt - 2.62), w + 0.60, 4.05,
                     boxstyle="round,pad=0,rounding_size=0.14",
                     facecolor=tint, edgecolor=HAIRLINE, linewidth=1.0, zorder=1))
        _resistor(ax, x, yt, w, rl, rv)                    # resistor on top rail
        ax.plot([x, x], [yt - 1.62, yt], color=ACCENT, lw=1.8, zorder=2)
        ax.plot([x + w, x + w], [yt - 1.62, yt], color=ACCENT, lw=1.8, zorder=2)
        _capacitor(ax, x, yt - 1.62, w, cl, cv)            # capacitor below
        return x + w

    e1 = rc(7.05, 2.55, "R₁", "0.00820 Ω", "C₁", "22.268 F", ACCENT_TINT)
    ax.plot([r0x + r0w, 7.05], [yt, yt], color=ACCENT, lw=1.8, zorder=2)
    e2 = rc(11.05, 2.55, "R₂", "0.00882 Ω", "C₂", "119.37 F", ACCENT_TINT)
    ax.plot([e1, 11.05], [yt, yt], color=ACCENT, lw=1.8, zorder=2)

    # --- terminal ---
    tx = 16.35
    ax.plot([e2, tx], [yt, yt], color=ACCENT, lw=1.8, zorder=2)
    ax.plot([sx, tx], [yb, yb], color=ACCENT, lw=1.8, zorder=2)
    for ty, lab, col in [(yt, "+", CRITICAL), (yb, "−", INK)]:
        ax.add_patch(Circle((tx, ty), 0.24, facecolor=BG, edgecolor=col,
                            linewidth=1.8, zorder=4))
        ax.text(tx + 0.58, ty, lab, ha="center", va="center", fontsize=14,
                fontweight="bold", color=col)
    ax.annotate("", xy=(tx + 1.5, yb), xytext=(tx + 1.5, yt),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.2))
    ax.text(tx + 1.85, (yt + yb)/2, "V$_t$", ha="left", va="center",
            fontsize=13, fontweight="bold", color=INK)

    ax.text(9.4, 9.15, "2RC Thévenin equivalent-circuit model",
            ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
    ax.text(9.4, 0.52,
            "V$_t$ = OCV(SOC) − I·R₀ − V$_{RC1}$ − V$_{RC2}$        "
            "R₁C₁ fast transient (0.18 s)   ·   R₂C₂ slow relaxation (1.05 s)",
            ha="center", va="center", fontsize=10.2, color=MUTED)
    save(fig, "diag_2rc_ecm.png")


# ================================================== 3. hardware block diagram
def hardware_blocks():
    fig, ax = canvas(9.6, 5.2, (0, 19.2), (0, 10.4))
    bw, bh, by = 4.55, 2.70, 5.15

    box(ax, 0.75, by, bw, bh, "JBD BMS",
        "SP24S007 · 8 cell taps\n4 × NTC · pack V / I", ec=ACCENT, fc=BG)
    box(ax, 7.32, by, bw, bh, "Raspberry Pi 5",
        "jbd_logger v9 · 51 features\nXGBoost inference · OOD gate", ec=ACCENT, fc=ACCENT_TINT)
    box(ax, 13.90, by, bw, bh, "Arduino Uno R4 WiFi",
        "hardware watchdog\nindependent power rail", ec=WARNING, fc=WARNING_TINT)

    # BLE link
    arrow(ax, (0.75 + bw, by + bh*0.58), (7.32, by + bh*0.58), color=ACCENT, lw=2.0)
    ax.text(0.75 + bw + (7.32 - 0.75 - bw)/2, by + bh*0.58 + 0.40, "BLE",
            ha="center", va="bottom", fontsize=11, fontweight="bold", color=ACCENT)
    ax.text(0.75 + bw + (7.32 - 0.75 - bw)/2, by + bh*0.58 - 0.42,
            "bleak · notify", ha="center", va="top", fontsize=8.6, color=MUTED)
    # little BLE radio glyph
    gx, gy = 0.75 + bw + (7.32 - 0.75 - bw)/2, by + bh*0.58 + 1.18
    for r, a in [(0.22, 1.0), (0.42, 0.6), (0.62, 0.32)]:
        th = np.linspace(-0.85, 0.85, 40)
        ax.plot(gx + r*np.cos(th), gy + r*np.sin(th), color=ACCENT, lw=1.5, alpha=a)

    # heartbeat out
    arrow(ax, (7.32 + bw, by + bh*0.66), (13.90, by + bh*0.66), color=WARNING, lw=2.0)
    ax.text(7.32 + bw + (13.90 - 7.32 - bw)/2, by + bh*0.66 + 0.38, "heartbeat",
            ha="center", va="bottom", fontsize=10.5, fontweight="bold", color=WARNING)
    # RUN-pin reset back
    arrow(ax, (13.90 + bw/2, by), (7.32 + bw/2, by), color=CRITICAL, lw=2.0, rad=-0.30)
    ax.text(10.9, 3.42, "RUN pin  →  forced hardware reset on missed heartbeat",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color=CRITICAL)

    # tier captions
    for cx, t, col in [(0.75 + bw/2, "TIER 1 · sensing", ACCENT),
                       (7.32 + bw/2, "TIER 2 · edge inference", ACCENT),
                       (13.90 + bw/2, "TIER 3 · failsafe", WARNING)]:
        ax.text(cx, by + bh + 0.42, t, ha="center", va="bottom",
                fontsize=9.5, fontweight="bold", color=col)

    # acceleration path
    ax.add_patch(FancyBboxPatch((4.60, 1.00), 10.0, 1.65,
                 boxstyle="round,pad=0,rounding_size=0.14", facecolor=PANEL,
                 edgecolor=HAIRLINE, linewidth=1.1, linestyle=(0, (4, 3)), zorder=2))
    ax.text(9.60, 1.82, "Acceleration path  ·  Zynq-7000 SoC",
            ha="center", va="center", fontsize=10.8, fontweight="bold", color=INK)
    ax.text(9.60, 1.30, "PL-side tree traversal for the same XGBoost model — "
                        "inference off the CPU",
            ha="center", va="center", fontsize=8.8, color=MUTED)
    ax.text(9.60, 9.85, "Three-tier hardware architecture", ha="center",
            va="center", fontsize=14, fontweight="bold", color=INK)
    save(fig, "diag_hardware.png")


# ============================================== 4. multi-chemistry pipeline
def configurator_pipeline():
    """Vertical flow - sized to sit in one half of slide 8."""
    fig, ax = canvas(5.2, 7.0, (0, 10.4), (0, 14.0))
    stages = [
        ("Datasheet upload",   "manufacturer PDF",                              ACCENT_TINT,   ACCENT),
        ("Parser",             "chemistry · V$_{nom}$ / V$_{max}$ / V$_{min}$\ncapacity · current limits · thermal", BG, ACCENT),
        ("Pack sizing",        "S = ceil( V$_{bus}$ / V$_{nom}$ )\nP = ceil( Q$_{pack}$ / Q$_{cell}$ )",             BG, ACCENT),
        ("Compatibility tiering", "NMC → NCA/LCO → LFP → LTO",                   BG,            WARNING),
        ("Threshold matrix",   "OV warn 95% / critical 100%\nOC warn 90% · thermal zones",     BG,            WARNING),
        ("Active profile",     "active_profile.json + PostgreSQL\nlive sync · no server restart", CRITICAL_TINT, CRITICAL),
    ]
    bw, bh, gap = 9.2, 1.62, 0.52
    x = 0.60
    y = 14.0 - 1.15 - bh
    for i, (t, sub, fc, ec) in enumerate(stages):
        box(ax, x, y, bw, bh, t, sub, fc=fc, ec=ec, fs=11.0, subfs=8.0)
        if i < len(stages) - 1:
            arrow(ax, (x + bw/2, y), (x + bw/2, y - gap), color=ec, lw=1.7, ms=9)
        y -= bh + gap
    ax.text(5.2, 13.45, "Configurator pipeline", ha="center", va="center",
            fontsize=13.5, fontweight="bold", color=INK)
    save(fig, "diag_configurator.png")


def chemistry_tiering():
    """The four-step adaptation ladder, as its own panel."""
    fig, ax = canvas(5.0, 8.2, (0, 10.0), (0, 16.4))
    tiers = [("NMC",       "direct reuse",        "baseline model unchanged",       ACCENT),
             ("NCA / LCO", "threshold shift",     "same 4.2 V ceiling family",      ACCENT),
             ("LFP",       "2.50 – 3.65 V remap", "flat OCV, window rewritten",     WARNING),
             ("LTO",       "full rescale",        "2.4 V nominal, every limit",     CRITICAL)]
    bw, bh, gap = 8.8, 2.70, 0.95
    x = 0.60
    y = 16.4 - 1.55 - bh
    for i, (name, act, note, col) in enumerate(tiers):
        ax.add_patch(FancyBboxPatch((x, y), bw, bh,
                     boxstyle="round,pad=0,rounding_size=0.14", facecolor=BG,
                     edgecolor=col, linewidth=1.7, zorder=3))
        ax.add_patch(Rectangle((x, y), 0.26, bh, facecolor=col,
                               edgecolor="none", zorder=4))
        ax.text(x + 0.70, y + bh*0.70, name, ha="left", va="center",
                fontsize=13, fontweight="bold", color=col, zorder=5)
        ax.text(x + 0.70, y + bh*0.43, act, ha="left", va="center",
                fontsize=10.5, color=INK, zorder=5)
        ax.text(x + 0.70, y + bh*0.19, note, ha="left", va="center",
                fontsize=8.6, color=MUTED, zorder=5)
        if i < len(tiers) - 1:
            arrow(ax, (x + bw/2, y), (x + bw/2, y - gap), color=MUTED, lw=1.5, ms=9)
        y -= bh + gap
    ax.text(5.0, 15.85, "Chemistry compatibility tiering", ha="center", va="center",
            fontsize=14, fontweight="bold", color=INK)
    ax.text(5.0, 0.42, "increasing adaptation effort  ↓", ha="center", va="center",
            fontsize=9, color=MUTED, style="italic")
    save(fig, "diag_chemistry_tiering.png")


if __name__ == "__main__":
    print("generating diagrams ->", os.path.relpath(OUT, ROOT))
    pack_topology()
    ecm_2rc()
    hardware_blocks()
    configurator_pipeline()
    chemistry_tiering()
    print("done")
