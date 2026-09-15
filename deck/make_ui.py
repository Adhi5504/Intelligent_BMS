#!/usr/bin/env python3
"""Vector recreations of the AI-PBMS web application screens.

The screenshots were pasted into the conversation rather than supplied as
files, so the two screens are redrawn here from the layout shown, in the
deck's own light palette. Swap in the real PNGs when they are available --
`build_deck.py` only needs the same filenames.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme
from theme import (ACCENT, WARNING, CRITICAL, INK, MUTED, HAIRLINE, PANEL, BG,
                   ACCENT_TINT, WARNING_TINT, CRITICAL_TINT)
theme.apply()
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch, Polygon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "assets", "generated")
os.makedirs(OUT, exist_ok=True)

NAVY = "#1B1B3A"          # the hero band in the live app
INDIGO = "#4F46E5"        # the app's primary button colour


def canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.axis("off"); ax.grid(False)
    ax.set_aspect("auto")
    return fig, ax


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor=theme.BG, transparent=False)
    plt.close(fig)
    print("  wrote", os.path.relpath(p, ROOT))


def card(ax, x, y, w, h, fc=BG, ec=HAIRLINE, lw=1.1, r=0.22, z=3):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f"round,pad=0,rounding_size={r}",
                 facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z))


def dashed(ax, x, y, w, h, ec=HAIRLINE, r=0.18, z=4):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f"round,pad=0,rounding_size={r}",
                 facecolor="none", edgecolor=ec, linewidth=1.3,
                 linestyle=(0, (5, 4)), zorder=z))


def upload_glyph(ax, cx, cy, s, col):
    """Tray-and-arrow upload mark, drawn rather than imported."""
    ax.add_patch(Polygon([[cx, cy + s*0.95], [cx - s*0.42, cy + s*0.28],
                          [cx + s*0.42, cy + s*0.28]], closed=True,
                         facecolor=col, edgecolor="none", zorder=6))
    ax.plot([cx, cx], [cy - s*0.45, cy + s*0.35], color=col, lw=s*7, zorder=6,
            solid_capstyle="round")
    ax.plot([cx - s*0.85, cx - s*0.85, cx + s*0.85, cx + s*0.85],
            [cy - s*0.30, cy - s*0.92, cy - s*0.92, cy - s*0.30],
            color=col, lw=s*6, zorder=6, solid_capstyle="round",
            solid_joinstyle="round")


# ================================================== 1. platform landing page
def landing():
    fig, ax = canvas(8.8, 5.4, (0, 17.6), (0, 10.8))

    # dark hero band
    ax.add_patch(FancyBboxPatch((0, 4.35), 17.6, 6.45,
                 boxstyle="round,pad=0,rounding_size=0.30",
                 facecolor=NAVY, edgecolor="none", zorder=1))
    ax.add_patch(Rectangle((0, 8.9), 17.6, 1.9, facecolor=NAVY,
                           edgecolor="none", zorder=1))
    ax.text(8.8, 9.42, "Intelligent Battery Management System", ha="center",
            va="center", fontsize=19, fontweight="bold", color="#FFFFFF", zorder=3)
    ax.text(8.8, 8.44, "Edge-to-cloud AI platform for battery parameter extraction,\n"
            "multi-chemistry configuration and time-series ML fault detection.",
            ha="center", va="center", fontsize=9.4, color="#B9BCD8",
            linespacing=1.55, zorder=3)

    # the two product cards, overlapping the hero edge like the real page
    cw, ch, cy = 7.85, 5.55, 1.15
    for i, (x, eyebrow, title, body, btn, btn_fc, btn_tc) in enumerate([
        (0.85, "LIVE STREAM  (LAYER 1 & 2)", "Real-Time Telemetry\n& Fault Detection",
         "Stream live pack data, monitor per-cell\nvoltages, and run the classifier to flag\n"
         "imbalance or weak-cell anomalies.",
         "Open Live Monitor  →", INDIGO, "#FFFFFF"),
        (8.90, "CONFIGURATION ENGINE", "Multi-Chemistry\nConfigurator",
         "Upload cell specification PDFs to extract\nchemistry profiles, size the pack, and\n"
         "retrain XGBoost on your own field CSV.",
         "Open Configurator  →", INK, "#FFFFFF"),
    ]):
        card(ax, x, cy, cw, ch, fc=BG, ec=HAIRLINE, lw=1.0, r=0.26, z=4)
        # icon chip
        card(ax, x + 0.45, cy + ch - 1.25, 0.85, 0.85, fc=PANEL, ec="none", r=0.15, z=5)
        if i == 0:
            ax.add_patch(Polygon([[x+0.875, cy+ch-0.53], [x+1.15, cy+ch-0.73],
                                  [x+1.15, cy+ch-1.02], [x+0.875, cy+ch-1.13],
                                  [x+0.60, cy+ch-1.02], [x+0.60, cy+ch-0.73]],
                                 closed=True, facecolor="none", edgecolor=INDIGO,
                                 linewidth=1.7, zorder=6))
        else:
            for k, yy in enumerate([-0.62, -0.83, -1.04]):
                ax.plot([x+0.60, x+1.15], [cy+ch+yy]*2, color=INDIGO, lw=1.5, zorder=6)
                ax.add_patch(Circle((x + 0.72 + 0.23*k, cy+ch+yy), 0.070,
                                    facecolor=BG, edgecolor=INDIGO, lw=1.4, zorder=7))
        ax.text(x + 1.46, cy + ch - 0.82, eyebrow, ha="left", va="center",
                fontsize=7.0, fontweight="bold", color=MUTED, zorder=6)
        ax.text(x + 0.45, cy + ch - 1.68, title, ha="left", va="top",
                fontsize=12.0, fontweight="bold", color=INK, linespacing=1.22, zorder=6)
        ax.text(x + 0.45, cy + ch - 2.92, body, ha="left", va="top",
                fontsize=7.3, color=MUTED, linespacing=1.52, zorder=6)
        card(ax, x + 0.45, cy + 0.40, 3.35, 0.76, fc=btn_fc, ec="none", r=0.38, z=6)
        ax.text(x + 2.125, cy + 0.78, btn, ha="center", va="center",
                fontsize=8.2, fontweight="bold", color=btn_tc, zorder=7)
    save(fig, "mock_landing.png")


# =============================================== 2. battery parameters screen
def battery_params():
    fig, ax = canvas(8.8, 4.6, (0, 17.6), (0, 9.2))
    ax.add_patch(Rectangle((0, 0), 17.6, 9.2, facecolor="#F7F8FC",
                           edgecolor=HAIRLINE, linewidth=1.0, zorder=1))

    # page heading with a pulse glyph
    px, py = 0.78, 8.30
    xs = np.array([0, .14, .26, .36, .46, .58, .74])
    ys = np.array([0, 0, .30, -.34, .16, 0, 0])
    ax.plot(px + xs - 0.42, py + ys, color=ACCENT, lw=1.9, zorder=3)
    ax.text(1.10, 8.30, "Battery Parameters", ha="left", va="center",
            fontsize=15, fontweight="bold", color=INK, zorder=3)

    cw, ch, cy = 5.35, 5.55, 1.55
    # --- card 1: cell datasheet ---
    x = 0.55
    card(ax, x, cy, cw, ch, r=0.24)
    ax.text(x + 0.48, cy + ch - 0.68, "Cell Datasheet", ha="left", va="center",
            fontsize=11.5, fontweight="bold", color=INK, zorder=5)
    dashed(ax, x + 0.42, cy + 0.55, cw - 0.84, ch - 1.72)
    upload_glyph(ax, x + cw/2, cy + 3.28, 0.34, ACCENT)
    ax.text(x + cw/2, cy + 2.52, "Drag and drop your\nPDF datasheet here",
            ha="center", va="center", fontsize=7.8, color=MUTED,
            linespacing=1.5, zorder=6)
    card(ax, x + cw/2 - 1.05, cy + 1.02, 2.10, 0.68, fc="#5B7FA6", ec="none", r=0.15, z=6)
    ax.text(x + cw/2, cy + 1.36, "Browse Files", ha="center", va="center",
            fontsize=9, fontweight="bold", color="#FFFFFF", zorder=7)

    # --- card 2: dataset upload ---
    x = 6.15
    card(ax, x, cy + 1.05, cw, ch - 1.05, r=0.24)
    card(ax, x + 0.45, cy + ch - 1.42, 0.80, 0.80, fc="#EFE9FB", ec="none", r=0.15, z=5)
    ax.add_patch(FancyBboxPatch((x + 0.66, cy + ch - 1.26), 0.40, 0.50,
                 boxstyle="round,pad=0,rounding_size=0.05", facecolor="none",
                 edgecolor="#8B5CF6", linewidth=1.4, zorder=6))
    for k in range(3):
        ax.plot([x + 0.74, x + 0.98], [cy + ch - 0.90 - 0.11*k]*2,
                color="#8B5CF6", lw=1.0, zorder=7)
    ax.text(x + 1.44, cy + ch - 0.78, "DATASET UPLOAD", ha="left", va="center",
            fontsize=10.5, fontweight="bold", color=INK, zorder=6)
    ax.text(x + 1.44, cy + ch - 1.24, "Supported files: CSV, XLSX, XLS, ODS",
            ha="left", va="center", fontsize=7.2, color=MUTED, zorder=6)
    dashed(ax, x + 0.45, cy + 1.62, cw - 0.90, 2.35, ec="#C9BDEB")
    upload_glyph(ax, x + cw/2, cy + 3.20, 0.30, "#8B5CF6")
    ax.text(x + cw/2, cy + 2.22, "Click or drag file to upload", ha="center",
            va="center", fontsize=8.0, fontweight="bold", color=INK, zorder=6)

    # --- card 3: dataset info ---
    x = 11.75
    card(ax, x, cy, cw, ch, r=0.24)
    ax.text(x + cw/2, cy + ch/2, "Upload a dataset\nto view its information.",
            ha="center", va="center", fontsize=8.4, color=MUTED,
            style="italic", linespacing=1.6, zorder=5)
    save(fig, "mock_battery_params.png")


# ============================================== 3. end-to-end system flow
def system_flow():
    fig, ax = canvas(9.6, 3.9, (0, 19.2), (0, 7.8))

    lanes = [("EDGE", 0.35, 6.05, ACCENT), ("CLOUD", 6.70, 6.05, ACCENT),
             ("INTERFACE", 13.05, 5.80, INDIGO)]
    blocks = [
        # (lane_x, y, w, h, title, sub, edge colour, fill)
        (0.35, 4.40, 6.05, 2.05, "8S2P pack + JBD BMS", "8 cell taps · 4 NTC · pack V/I", ACCENT, BG),
        (0.35, 1.95, 6.05, 2.05, "Raspberry Pi 5", "jbd_logger v9 · 51 features\nXGBoost inference · OOD gate", ACCENT, ACCENT_TINT),
        (6.70, 4.40, 6.05, 2.05, "Flask dashboard", "on Railway · REST + SSE\nrisk scoring · cycle engine", ACCENT, BG),
        (6.70, 1.95, 6.05, 2.05, "PostgreSQL", "telemetry · cycle history\nactive_profile sync", ACCENT, BG),
        (6.70, 0.30, 6.05, 1.25, "Outbound only", "the Pi dials out — no inbound port", MUTED, PANEL),
        (13.05, 4.40, 5.80, 2.05, "Live Monitor", "per-cell V · modes · ETA\nalert history", INDIGO, "#EEF0FE"),
        (13.05, 1.95, 5.80, 2.05, "Configurator", "datasheet parse · pack sizing\nin-browser retraining", INDIGO, "#EEF0FE"),
        (13.05, 0.30, 5.80, 1.25, "Battery Parameters", "PDF + dataset ingestion", INDIGO, BG),
    ]
    for x, y, w, h, t, s, ec, fc in blocks:
        card(ax, x, y, w, h, fc=fc, ec=ec, lw=1.5, r=0.16, z=3)
        ax.text(x + w/2, y + h*(0.66 if s else 0.5), t, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=INK, zorder=5)
        if s:
            ax.text(x + w/2, y + h*0.27, s, ha="center", va="center",
                    fontsize=7.6, color=MUTED, linespacing=1.5, zorder=5)

    for lx, lw_, lab, col in [(0.35, 6.05, "EDGE — on the pack", ACCENT),
                              (6.70, 6.05, "CLOUD — Railway", ACCENT),
                              (13.05, 5.80, "INTERFACE — any browser", INDIGO)]:
        ax.text(lx + lw_/2, 6.90, lab, ha="center", va="center", fontsize=9,
                fontweight="bold", color=col)

    for x0, x1, y, lab in [(6.40, 6.70, 5.42, "HTTPS"), (12.75, 13.05, 5.42, "HTTPS")]:
        ax.add_patch(FancyArrowPatch((x0, y), (x1 + 0.02, y), arrowstyle="-|>",
                     mutation_scale=11, color=ACCENT, lw=1.8, zorder=4))
    ax.add_patch(FancyArrowPatch((6.40, 2.97), (6.70, 2.97), arrowstyle="-|>",
                 mutation_scale=11, color=ACCENT, lw=1.8, zorder=4))
    ax.add_patch(FancyArrowPatch((12.75, 2.97), (13.05, 2.97), arrowstyle="-|>",
                 mutation_scale=11, color=INDIGO, lw=1.8, zorder=4))
    ax.text(9.60, 7.48, "End-to-end data path", ha="center", va="center",
            fontsize=13.5, fontweight="bold", color=INK)
    save(fig, "diag_system_flow.png")


# ============================================ 4. inference decision ladder
def confidence_ladder():
    """How a single window is actually adjudicated: OOD gate first, then the
    six-class model, then the confidence band."""
    fig, ax = canvas(9.0, 3.35, (0, 18.0), (0, 6.7))

    def node(x, y, w, h, t, sub, ec, fc):
        card(ax, x, y, w, h, fc=fc, ec=ec, lw=1.5, r=0.14, z=3)
        ax.text(x + w/2, y + h*0.63, t, ha="center", va="center", fontsize=10,
                fontweight="bold", color=INK, zorder=5)
        ax.text(x + w/2, y + h*0.26, sub, ha="center", va="center", fontsize=7.4,
                color=MUTED, zorder=5)

    def arrow(p0, p1, col, lab=None, up=True):
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=10,
                     color=col, lw=1.6, zorder=2))
        if lab:
            ax.text((p0[0]+p1[0])/2, (p0[1]+p1[1])/2 + (0.30 if up else -0.42),
                    lab, ha="center", va="center", fontsize=7.6,
                    fontweight="bold", color=col, zorder=5)

    node(0.25, 2.55, 2.95, 1.35, "60-row window", "51 features", ACCENT, BG)
    node(3.95, 2.55, 3.05, 1.35, "OOD gate", "IsolationForest", WARNING, WARNING_TINT)
    node(7.85, 2.55, 2.95, 1.35, "XGBoost", "six-class p(y)", ACCENT, ACCENT_TINT)

    node(11.55, 4.35, 6.20, 1.25, "ALERT   p ≥ 0.85", "corrective action shown", CRITICAL, CRITICAL_TINT)
    node(11.55, 2.62, 6.20, 1.25, "WARNING   0.50 – 0.85", "logged, non-blocking", WARNING, WARNING_TINT)
    node(11.55, 0.88, 6.20, 1.25, "ABSTAIN   p < 0.50", "routed to human review", MUTED, PANEL)

    node(3.30, 0.55, 4.35, 1.25, "UNKNOWN_FAULT_OOD", "escalated, never labelled", CRITICAL, CRITICAL_TINT)

    arrow((3.20, 3.22), (3.95, 3.22), ACCENT)
    ax.add_patch(FancyArrowPatch((7.00, 3.22), (7.85, 3.22), arrowstyle="-|>",
                 mutation_scale=10, color=ACCENT, lw=1.6, zorder=2))
    ax.text(7.42, 3.74, "pass", ha="center", va="center", fontsize=7.6,
            fontweight="bold", color=ACCENT, zorder=5)
    ax.add_patch(FancyArrowPatch((5.47, 2.55), (5.47, 1.82), arrowstyle="-|>",
                 mutation_scale=10, color=CRITICAL, lw=1.6, zorder=2))
    ax.text(6.62, 2.18, "below threshold", ha="left", va="center", fontsize=7.6,
            fontweight="bold", color=CRITICAL, zorder=5)
    for ty in (4.97, 3.24, 1.50):
        ax.add_patch(FancyArrowPatch((10.80, 3.22), (11.55, ty), arrowstyle="-|>",
                     mutation_scale=10, color=ACCENT, lw=1.4, zorder=2))
    ax.text(0.25, 6.30, "One window, one decision", ha="left", va="center",
            fontsize=12.5, fontweight="bold", color=INK)
    save(fig, "diag_confidence_ladder.png")


if __name__ == "__main__":
    print("generating UI mockups ->", os.path.relpath(OUT, ROOT))
    landing()
    battery_params()
    system_flow()
    confidence_ladder()
    print("done")
