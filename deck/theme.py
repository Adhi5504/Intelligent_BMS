"""AI-PBMS deck design system — light technical theme.

Single source of truth for colours, fonts and matplotlib defaults so that
every generated PNG and every PPTX shape stay visually identical.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ---- palette (hex, per design spec) -------------------------------------
BG        = "#FFFFFF"   # slide + figure background
PANEL     = "#F1F5F9"   # section panels / table header fill
INK       = "#0F172A"   # body text / headings
MUTED     = "#475569"   # secondary text, slide numbers
HAIRLINE  = "#CBD5E1"   # rules, gridlines, 1px borders
ACCENT    = "#0E7490"   # primary accent (teal)
WARNING   = "#B45309"   # amber
CRITICAL  = "#B91C1C"   # red

ACCENT_TINT   = "#CFF0F3"
WARNING_TINT  = "#FBE8D0"
CRITICAL_TINT = "#F6D6D6"

DPI = 300

# ---- fonts ---------------------------------------------------------------
_AVAILABLE = {f.name for f in fm.fontManager.ttflist}
for _cand in ("Inter", "Montserrat", "Open Sans", "Calibri", "Liberation Sans", "DejaVu Sans"):
    if _cand in _AVAILABLE:
        FONT = _cand
        break
else:                                     # pragma: no cover
    FONT = "DejaVu Sans"

HEAD_FONT = FONT          # name written into the PPTX for headings
BODY_FONT = FONT          # name written into the PPTX for body copy


def apply():
    """Install the light theme as the matplotlib rcParams default."""
    plt.rcParams.update({
        "figure.facecolor":  BG,
        "figure.edgecolor":  BG,
        "savefig.facecolor": BG,
        "savefig.edgecolor": BG,
        "savefig.transparent": False,
        "axes.facecolor":    BG,
        "axes.edgecolor":    HAIRLINE,
        "axes.labelcolor":   INK,
        "axes.titlecolor":   INK,
        "axes.grid":         True,
        "axes.axisbelow":    True,
        "grid.color":        HAIRLINE,
        "grid.linewidth":    0.8,
        "grid.alpha":        1.0,
        "xtick.color":       MUTED,
        "ytick.color":       MUTED,
        "text.color":        INK,
        "font.family":       FONT,
        "font.size":         11,
        "axes.titlesize":    14,
        "axes.titleweight":  "bold",
        "axes.labelsize":    11,
        "legend.frameon":    False,
        "figure.dpi":        DPI,
        "savefig.dpi":       DPI,
        "savefig.bbox":      "tight",
        "savefig.pad_inches": 0.12,
    })


def strip(ax, keep=("left", "bottom")):
    """Remove chart junk: drop unused spines, tint the ones we keep."""
    for side, sp in ax.spines.items():
        sp.set_visible(side in keep)
        sp.set_color(HAIRLINE)
        sp.set_linewidth(0.9)
