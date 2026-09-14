#!/usr/bin/env python3
"""Assemble AI_PBMS_Full_Deck.pptx — the 20-slide review deck.

Shares its design system with build_deck.py (the 8-slide pitch cut); both
pull from deck/theme.py so the two decks stay visually identical.
"""
import os, sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN  = os.path.join(ROOT, "assets", "generated")
EXT  = os.path.join(ROOT, "assets", "extracted")
OUT  = os.path.join(ROOT, "AI_PBMS_Full_Deck.pptx")

def C(h): return RGBColor.from_string(h.lstrip("#"))
BG, PANEL, INK  = C(theme.BG), C(theme.PANEL), C(theme.INK)
MUTED, HAIRLINE = C(theme.MUTED), C(theme.HAIRLINE)
ACCENT, WARNING, CRITICAL = C(theme.ACCENT), C(theme.WARNING), C(theme.CRITICAL)

HEAD_FONT, BODY_FONT = theme.HEAD_FONT, theme.BODY_FONT

SW, SH = 13.333, 7.5                      # slide size, inches
M      = 0.62                             # outer margin
TITLE_Y, TITLE_H = 0.40, 0.78
RULE_Y = 1.26                             # thin accent rule under the title
BODY_Y = 1.56
BODY_B = 6.86                             # bottom of the content band
LEFT_W = 6.34                             # ~55% content column (net of margin)
VIS_X  = M + LEFT_W + 0.36
VIS_W  = SW - M - VIS_X                   # ~45% visual column


# ----------------------------------------------------------------- helpers
def rect(slide, x, y, w, h, fill=None, line=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.shadow.inherit = False
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(lw)
    s.text_frame.text = ""
    return s


def text(slide, x, y, w, h, runs, size=17, color=INK, bold=False, font=None,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space_after=0, line=1.18):
    """runs: a string, or a list of (string, {overrides}) for per-para styling."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    items = [runs] if isinstance(runs, str) else runs
    for i, item in enumerate(items):
        s, ov = (item, {}) if isinstance(item, str) else item
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ov.get("align", align)
        p.line_spacing = ov.get("line", line)
        p.space_after = Pt(ov.get("space_after", space_after))
        r = p.add_run(); r.text = s
        f = r.font
        f.name = ov.get("font", font or BODY_FONT)
        f.size = Pt(ov.get("size", size))
        f.bold = ov.get("bold", bold)
        f.color.rgb = ov.get("color", color)
    return tb


def bullets(slide, x, y, w, h, items, size=17, dot_col=None, gap=9):
    """Body copy as genuine bulleted paragraphs.

    Uses real DrawingML bullet properties (buChar + buClr + hanging indent) so
    spacing stays even regardless of how many lines each bullet wraps to --
    a fixed-pitch layout drifts as soon as one bullet is longer than another.
    """
    dot_col = dot_col or ACCENT
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    marL, ind = Emu(int(0.30 * 914400)), Emu(int(-0.30 * 914400))
    for i, txt in enumerate(items):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.line_spacing = 1.16
        para.space_after = Pt(gap)
        pPr = para._p.get_or_add_pPr()
        pPr.set("marL", str(marL)); pPr.set("indent", str(ind))
        _bullet_glyph(pPr, dot_col, size)
        r = para.add_run(); r.text = txt
        r.font.name = BODY_FONT; r.font.size = Pt(size); r.font.color.rgb = INK
    return tb


def _bullet_glyph(pPr, colour, size):
    """Attach <a:buClr>/<a:buSzPct>/<a:buFont>/<a:buChar> in schema order."""
    from pptx.oxml.ns import qn
    from lxml import etree
    ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
    clr = etree.SubElement(pPr, qn("a:buClr"))
    srgb = etree.SubElement(clr, qn("a:srgbClr")); srgb.set("val", str(colour))
    sz = etree.SubElement(pPr, qn("a:buSzPct")); sz.set("val", "62000")
    fnt = etree.SubElement(pPr, qn("a:buFont"))
    fnt.set("typeface", "Arial"); fnt.set("pitchFamily", "34"); fnt.set("charset", "0")
    ch = etree.SubElement(pPr, qn("a:buChar")); ch.set("char", "\u25cf")


def fit(path, bx, by, bw, bh):
    """Letterbox an image inside a box, preserving aspect ratio."""
    iw, ih = Image.open(path).size
    sc = min(bw / iw, bh / ih)
    w, h = iw * sc, ih * sc
    return bx + (bw - w) / 2, by + (bh - h) / 2, w, h


def picture(slide, path, bx, by, bw, bh, card=False, pad=0.13):
    """Place an image; `card` wraps it in a white 1px #CBD5E1 panel so that
    photos and screenshots with non-white backgrounds do not clash."""
    if card:
        x, y, w, h = fit(path, bx + pad, by + pad, bw - 2*pad, bh - 2*pad)
        rect(slide, x - pad, y - pad, w + 2*pad, h + 2*pad,
             fill=BG, line=HAIRLINE, lw=1.0)
    else:
        x, y, w, h = fit(path, bx, by, bw, bh)
    slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    return x, y, w, h


def caption(slide, x, y, w, s):
    text(slide, x, y, w, 0.26, s, size=9.5, color=MUTED, align=PP_ALIGN.CENTER)


def new_slide(prs, n, title, eyebrow=None):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    bgf = sl.background.fill; bgf.solid(); bgf.fore_color.rgb = BG
    ty = TITLE_Y
    if eyebrow:
        text(sl, M, TITLE_Y - 0.06, LEFT_W + 3.0, 0.26, eyebrow,
             size=11, color=ACCENT, bold=True)
        ty = TITLE_Y + 0.24
    text(sl, M, ty, SW - 2*M, TITLE_H, title, size=33, color=INK,
         bold=True, font=HEAD_FONT, line=1.02)
    # thin accent rule under the title
    r = rect(sl, M, RULE_Y + (0.22 if eyebrow else 0), 2.15, 0.035, fill=ACCENT)
    r.line.fill.background()
    r2 = rect(sl, M + 2.15, RULE_Y + (0.22 if eyebrow else 0), SW - 2*M - 2.15,
              0.035, fill=HAIRLINE)
    r2.line.fill.background()
    # running footer + slide number
    text(sl, M, SH - 0.50, 5.0, 0.26, "AI-PBMS  ·  Team ANS_4X", size=9.5, color=MUTED)
    text(sl, SW - M - 1.2, SH - 0.50, 1.2, 0.26, str(n), size=10.5, color=MUTED,
         align=PP_ALIGN.RIGHT)
    return sl


def notes(slide, s):
    slide.notes_slide.notes_text_frame.text = s.strip()


def stat_strip(slide, x, y, w, items):
    """Row of small key-figure cards."""
    n = len(items); gap = 0.16
    cw = (w - gap * (n - 1)) / n
    for i, (big, cap, col) in enumerate(items):
        cx = x + i * (cw + gap)
        rect(slide, cx, y, cw, 0.86, fill=PANEL, line=HAIRLINE, lw=0.75)
        text(slide, cx, y + 0.10, cw, 0.36, big, size=16, color=col, bold=True,
             align=PP_ALIGN.CENTER)
        text(slide, cx, y + 0.50, cw, 0.28, cap, size=9, color=MUTED,
             align=PP_ALIGN.CENTER)


def table(slide, x, y, w, headers, rows, col_w, head_h=0.46, row_h=0.52,
          fs=11, hfs=10.5):
    """Hand-built table: rectangles + textboxes, so every colour is ours."""
    total = sum(col_w)
    col_w = [c / total * w for c in col_w]
    # header
    cx = x
    rect(slide, x, y, w, head_h, fill=PANEL, line=HAIRLINE, lw=0.75)
    for cwi, h in zip(col_w, headers):
        text(slide, cx + 0.09, y, cwi - 0.18, head_h, h, size=hfs, color=INK,
             bold=True, anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.LEFT if cx == x else PP_ALIGN.CENTER)
        cx += cwi
    # body
    ry = y + head_h
    for ri, row in enumerate(rows):
        if ri == 0:                                    # highlight the chosen model
            rect(slide, x, ry, w, row_h, fill=C("#E6F4F6"), line=ACCENT, lw=1.1)
        else:
            ln = rect(slide, x, ry + row_h, w, 0.012, fill=HAIRLINE)
            ln.line.fill.background()
        cx = x
        for ci, (cwi, cell) in enumerate(zip(col_w, row)):
            val, col, bold = cell if isinstance(cell, tuple) else (cell, INK, False)
            text(slide, cx + 0.09, ry, cwi - 0.18, row_h, val, size=fs, color=col,
                 bold=bold or ri == 0 and ci == 0, anchor=MSO_ANCHOR.MIDDLE,
                 align=PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER)
            cx += cwi
        ry += row_h
    return ry



BENCH_ROWS = [
    ["XGBoost", ("94.19%", ACCENT, True), ("0.905", MUTED, False), ("0.462 ms", ACCENT, True), ("1.40 MB", MUTED, False), ("Yes", ACCENT, False), ("Deployed — 1-row input, 10-row context", ACCENT, True)],
    ["Transformer", ("95.11%", INK, False), ("0.918", MUTED, False), ("0.419 ms", MUTED, False), ("0.31 MB", MUTED, False), ("Warn", WARNING, False), ("+0.92% acc; 60 rows locked in", WARNING, False)],
    ["LSTM", ("87.03%", INK, False), ("0.776", MUTED, False), ("0.532 ms", MUTED, False), ("0.28 MB", MUTED, False), ("Warn", WARNING, False), ("Sequential, weakest F1", MUTED, False)],
    ["Random Forest", ("89.37%", INK, False), ("0.824", MUTED, False), ("33.770 ms", MUTED, False), ("176.41 MB", MUTED, False), ("No", CRITICAL, False), ("176 MB, 73× the latency", CRITICAL, False)],
    ["SVM (RBF)", ("88.53%", INK, False), ("0.807", MUTED, False), ("0.568 ms", MUTED, False), ("2.82 MB", MUTED, False), ("Yes", ACCENT, False), ("Would not scale past 20k rows", MUTED, False)],
    ["Rule-based BMS", ("22.09%", INK, False), ("0.224", MUTED, False), ("5 µs", MUTED, False), ("~0 MB", MUTED, False), ("Yes", ACCENT, False), ("0% recall on Weak Cell", CRITICAL, False)],
]

BENCH_FOOT = (
    "All six trained and scored on the identical 30,000-row held-out split with the same 51 features; latency is the "
    "median single-row prediction on a 4-core CPU, not a Pi 5. Both models sit behind the same 60-row pipeline buffer, "
    "but XGBoost consumes only the last row and its deepest feature is a 10-sample rolling window, so that 60 is a "
    "constant we chose; the Transformer consumes all 60 and its positional encoding fixes the length in the weights. "
    "SVM trained on a stratified 20k subsample: full-data RBF did not converge."
)

BENCH_NOTES = """
We did not argue about which model to use — we trained all six on the identical
split and measured them. Two rows matter. The bottom one: a conventional
rule-based BMS scores twenty-two percent, because cell one\u2019s chronic gap puts
eighty-four percent of healthy rows over the imbalance threshold. It false-alarms
constantly and never detects a weak cell at all. And the second row: the
Transformer edges us by under a point — but look at what it costs. Both models
sit behind the same sixty-row buffer in our pipeline. The difference is that
XGBoost only eats the last row of it, and its deepest feature is a ten-sample
rolling window, so that sixty is a constant we chose and could shorten to ten
tomorrow. The Transformer eats all sixty, and its positional encoding fixes that
length inside the weights — you cannot shorten it without retraining. On top of
that, torch is five times the runtime footprint of xgboost on the Pi, it gives no
per-feature attribution an engineer can audit, and it cannot be retrained from
the browser the way our configurator retrains XGBoost today. That is why it
ships.
"""




# --------------------------------------------------------- extra slide parts
def title_slide(prs, title, sub, meta):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    bgf = sl.background.fill; bgf.solid(); bgf.fore_color.rgb = BG
    text(sl, M, 0.96, 8.2, 0.30, "CATERPILLAR TECH CHALLENGE 2026", size=11.5,
         color=ACCENT, bold=True)
    text(sl, M, 1.36, 6.20, 0.62, "AI-PBMS", size=30, color=ACCENT, bold=True,
         font=HEAD_FONT)
    text(sl, M, 2.10, 6.20, 1.70, title, size=29, color=INK, bold=True,
         font=HEAD_FONT, line=1.12)
    r = rect(sl, M, 4.02, 2.15, 0.045, fill=ACCENT); r.line.fill.background()
    text(sl, M, 4.32, 6.05, 1.10, sub, size=13.5, color=MUTED, line=1.34)
    text(sl, M, 5.72, 6.05, 0.90, meta, size=12, color=INK, line=1.42)
    picture(sl, os.path.join(GEN, "mock_landing.png"), 7.05, 1.30, 5.68, 4.60)
    text(sl, SW - M - 5.68, 6.10, 5.68, 0.26,
         "The delivered platform — live monitor and configuration engine",
         size=9.5, color=MUTED, align=PP_ALIGN.CENTER)
    notes(sl, """
Good morning. We are Team ANS_4X from PSG Institute of Technology and Applied
Research. What we are presenting is not a slide-deck concept — it is a working
system. A physical 8S2P lithium-ion pack, instrumented end to end, feeding a
machine-learning fault classifier that runs on the pack itself, behind a web
platform you can open in a browser right now. Over the next ten minutes I will
walk you from the cells, through the data, through the model, to the interface
on the right of this slide.""")
    return sl


def closing_slide(prs, n):
    sl = new_slide(prs, n, "What we would build next")
    items = [
        ("Close the Cell Imbalance gap", "65% recall is the weakest class. More real "
         "imbalance events, not more synthetic ones.", CRITICAL),
        ("Lift OOD recall", "The gate never cries wolf, but catches one unknown in four. "
         "A tighter score threshold trades that off.", WARNING),
        ("Move inference to the Zynq-7000", "Tree traversal in programmable logic frees the "
         "CPU for the logger and the BLE link.", ACCENT),
        ("Characterise a second chemistry", "LFP is remapped from its datasheet; it has not "
         "been driven on a bench the way NMC has.", ACCENT),
        ("SOH and remaining useful life", "dV/dt during CC-CV charging is the signal; the "
         "39-cycle history is the starting corpus.", ACCENT),
    ]
    y = BODY_Y + 0.04
    for t, d, col in items:
        rect(sl, M, y, SW - 2*M, 0.82, fill=PANEL, line=HAIRLINE, lw=0.75)
        b = rect(sl, M, y, 0.075, 0.82, fill=col); b.line.fill.background()
        text(sl, M + 0.34, y + 0.09, 4.15, 0.34, t, size=14, color=INK, bold=True)
        text(sl, M + 4.70, y + 0.08, SW - 2*M - 5.05, 0.66, d, size=11,
             color=MUTED, line=1.26)
        y += 0.94
    text(sl, M, y + 0.06, SW - 2*M, 0.34,
         "Everything shown today is reproducible from this repository — "
         "figures, model and deck all rebuild from source.",
         size=12, color=ACCENT, bold=True, align=PP_ALIGN.CENTER)
    notes(sl, """
I want to close on what is not finished. Cell Imbalance recall sits at sixty-five
percent — that is the weakest number in the deck and it needs real imbalance
events, not more synthetic ones. The unknown-fault gate never raises a false
alarm but only catches one unknown in four. The Zynq path would take inference
off the CPU. LFP is remapped from a datasheet, not characterised on a bench.
And state of health is the natural next model. Everything you have seen rebuilds
from the repository — the figures, the model evaluation and this deck.""")
    return sl


# =================================================== references slide (shared)
def mini_head(slide, x, y, w, label, color=None):
    text(slide, x, y, w, 0.24, label, size=9.5, color=color or ACCENT, bold=True)


LITERATURE = [
    ("Bimodal images + BFRN",
     "Energy, 2024  ·  doi.org/10.1016/j.energy.2024.131700"),
    ("Single-cycle charging",
     "Energy, 2025  ·  doi.org/10.1016/j.energy.2025.138351"),
    ("Multidomain features + CatBoost",
     "Energy Science & Engineering, 2023  ·  doi.org/10.1002/ese3.1506"),
    ("CNN-BiLSTM-BiGRU with attention",
     "Journal of Energy Storage, 2024  ·  doi.org/10.1016/j.est.2024.113074"),
    ("Yang, S., Xu, B., Peng, H. — “Isolation and Grading of Faults in\n"
     "Battery Packs Based on Machine Learning Methods”",
     "Electronics, 11(9), 1494, 2022  ·  mdpi.com/2079-9292/11/9/1494"),
]

PRIMARY = [
    ("LG Energy Solution INR21700-M50", "cell used in the 8S2P pack"),
    ("DMEGC INR21700-45E", "alternate NMC cell, parsed"),
    ("Panasonic NCR18650B", "NCA tier reference"),
    ("P3 3232 LFP 26650", "LFP tier reference"),
    ("JBD SP24S007 V1.1", "BMS protocol + registers"),
]

METHODS = [
    ("Chen, T. & Guestrin, C.", "“XGBoost: A Scalable Tree Boosting System”, KDD 2016"),
    ("Liu, F. T., Ting, K. M. & Zhou, Z.-H.", "“Isolation Forest”, ICDM 2008"),
    ("Vaswani, A. et al.", "“Attention Is All You Need”, NeurIPS 2017"),
    ("Pedregosa, F. et al.", "“Scikit-learn: Machine Learning in Python”, JMLR 12, 2011"),
]

STACK = ("xgboost 3.2.0  ·  scikit-learn 1.9.1  ·  torch 2.14.0  ·  numpy 2.4.6\n"
         "bleak  ·  Flask  ·  PostgreSQL  ·  Railway  ·  MATLAB / Simulink")


def references_slide(prs, n):
    s = new_slide(prs, n, "References")

    # ---- left column: the literature the approach is built on -------------
    mini_head(s, M, BODY_Y + 0.02, LEFT_W, "LITERATURE — SOC, RUL AND FAULT GRADING")
    y = BODY_Y + 0.36
    for i, (title, src) in enumerate(LITERATURE, 1):
        lines = title.count("\n") + 1
        h = 0.24 * lines
        num = rect(s, M, y + 0.015, 0.26, 0.26, fill=PANEL, line=HAIRLINE, lw=0.6)
        text(s, M, y + 0.015, 0.26, 0.26, str(i), size=10, color=ACCENT, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(s, M + 0.40, y, LEFT_W - 0.40, h + 0.06, title, size=11.5,
             color=INK, line=1.22)
        text(s, M + 0.40, y + h + 0.04, LEFT_W - 0.40, 0.22, src, size=9,
             color=MUTED)
        y += h + 0.44

    # ---- right column: what the system was actually built against ---------
    ry = BODY_Y + 0.02
    rect(s, VIS_X, ry, VIS_W, 2.34, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, VIS_X + 0.22, ry + 0.14, VIS_W - 0.44,
              "PRIMARY SOURCES — MANUFACTURER DATASHEETS")
    yy = ry + 0.46
    for name, role in PRIMARY:
        d = rect(s, VIS_X + 0.24, yy + 0.09, 0.09, 0.09, fill=ACCENT,
                 shape=MSO_SHAPE.OVAL); d.line.fill.background()
        text(s, VIS_X + 0.46, yy, 3.05, 0.26, name, size=10.5, color=INK)
        text(s, VIS_X + 3.50, yy + 0.01, VIS_W - 3.72, 0.24, role, size=9,
             color=MUTED)
        yy += 0.38

    ry2 = ry + 2.50
    rect(s, VIS_X, ry2, VIS_W, 2.06, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, VIS_X + 0.22, ry2 + 0.14, VIS_W - 0.44, "METHODS", WARNING)
    yy = ry2 + 0.46
    for who, what in METHODS:
        text(s, VIS_X + 0.24, yy, VIS_W - 0.48, 0.22, who, size=10.5,
             color=INK, bold=True)
        text(s, VIS_X + 0.24, yy + 0.19, VIS_W - 0.48, 0.22, what, size=9,
             color=MUTED)
        yy += 0.40

    ry3 = ry2 + 2.22
    mini_head(s, VIS_X, ry3, VIS_W, "STACK", MUTED)
    text(s, VIS_X, ry3 + 0.26, VIS_W, 0.52, STACK, size=9, color=MUTED, line=1.32)

    notes(s, """
Five papers shaped the approach. The first four are the state-of-the-art we
benchmarked our thinking against for state-of-charge and remaining-useful-life
prediction — bimodal image encoding, single-cycle charging features, multidomain
features with CatBoost, and the CNN-BiLSTM-BiGRU attention stack. The fifth,
Yang, Xu and Peng in Electronics, is where our confidence-scoring and fault
grading framework comes from — that is the source of the three-tier abstain,
warn, alert structure on slide five. On the right are the primary sources: the
manufacturer datasheets the threshold matrix is parsed from, and the JBD
protocol spec the logger was written against. Happy to take questions.""")
    return s

# =========================================================== the slides
def build():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)
    G = lambda n: os.path.join(GEN, n)
    E = lambda n: os.path.join(EXT, n)

    # ------------------------------------------------------------ 1 title
    title_slide(prs,
        "AI-Powered Predictive\nBattery Management System",
        "An 8S2P lithium-ion pack, 155,000 rows of our own telemetry, and a "
        "six-class fault classifier running at the edge.",
        "Team ANS_4X  ·  PSG Institute of Technology and Applied Research, Coimbatore")

    # -------------------------------------------------- 2 problem / dataset
    s = new_slide(prs, 2, "We could not buy this dataset, so we built it")
    bullets(s, M, BODY_Y + 0.24, LEFT_W, 3.20, [
        "Public BMS datasets hide per-cell voltages behind pack totals.",
        "Imbalance and weak-cell faults are invisible at pack level.",
        "So we instrumented a physical 8S2P NMC pack end to end.",
        "Programmable DC supply charges; electronic load drives discharge profiles.",
        "Every row the model ever sees came from this rig.",
    ], size=16.5)
    stat_strip(s, M, 5.30, LEFT_W, [
        ("~50", "charge–discharge cycles", ACCENT),
        ("~3 hrs", "per cycle", ACCENT),
        (">100 hrs", "supervised logging", ACCENT),
        ("~155,000", "rows logged", CRITICAL),
    ])
    picture(s, E("p03_img1_x38.jpeg"), VIS_X, BODY_Y + 0.18, VIS_W, 4.30, card=True)
    caption(s, VIS_X, BODY_Y + 4.58, VIS_W,
            "8S2P pack, JBD BMS and programmable electronic load on the bench")
    notes(s, """
Every public battery dataset reports pack-level voltage and current. That is
useless to us: imbalance and weak-cell faults only show in the spread between
individual cells. So we built the dataset. An 8S2P NMC pack, a JBD BMS on all
eight taps, a programmable supply charging and an electronic load discharging.
Around fifty cycles, three hours each, over a hundred hours logged, roughly
155,000 rows. Every number in this deck came off that bench.""")

    # ------------------------------------------------ 3 what's in the data
    s = new_slide(prs, 3, "What a hundred hours of logging actually showed us")
    bullets(s, M, BODY_Y + 0.16, LEFT_W, 2.95, [
        "Cell 1 runs 289 mV below its neighbours, every cycle.",
        "Not noise, not a sensor fault — a genuinely weaker cell.",
        "The gap widens under load and never fully recovers.",
        "This one defect defined the whole labelling problem.",
    ], size=16.5)
    rect(s, M, 4.62, LEFT_W, 1.92, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.22, 4.76, LEFT_W - 0.44, 0.26, "WHY THIS MATTERS",
         size=10, color=ACCENT, bold=True)
    text(s, M + 0.22, 5.06, LEFT_W - 0.44, 1.34,
         "A pack-level voltmeter reads 30.5 V and reports a healthy pack. "
         "The same instant, cell 1 is 289 mV down and heading for the undervoltage "
         "cutoff first. Per-cell resolution is the difference between noticing "
         "and not noticing.",
         size=12.5, color=INK, line=1.26)
    picture(s, G("fig_cell_traces.png"), VIS_X, BODY_Y + 0.30, VIS_W, 4.70)
    notes(s, """
This is the single most important chart in the deck. Eight cell voltages over
forty minutes of real logged discharge. Seven of them track each other closely —
that is the grey band. The red trace is cell one, sitting 289 millivolts below
its neighbours for the entire cycle, and the gap widens under load. A
pack-level voltmeter would read thirty and a half volts here and call the pack
healthy. Cell one is the one that will hit the undervoltage cutoff first. That
is the case for per-cell sensing in one picture.""")

    # ------------------------------------------------------ 4 pack topology
    s = new_slide(prs, 4, "Why 8S2P, specifically")
    bullets(s, M, BODY_Y + 0.20, LEFT_W, 3.05, [
        "8S sets the 33.6 V nominal bus the drivetrain expects.",
        "2P buys 8 Ah capacity and the current headroom.",
        "Sixteen LG INR21700-M50 cells, 5000 mAh each.",
        "Eight sense taps make imbalance observable, not inferred.",
        "Four NTC thermistors give spatial thermal resolution.",
    ], size=16.5)
    stat_strip(s, M, 5.34, LEFT_W, [
        ("33.6 V", "nominal bus", ACCENT),
        ("8 Ah", "usable capacity", ACCENT),
        ("16", "cells", ACCENT),
        ("8 + 4", "V taps + NTCs", WARNING),
    ])
    picture(s, G("diag_pack_8s2p.png"), VIS_X, BODY_Y + 0.85, VIS_W, 3.30)
    notes(s, """
Eight in series gives the 33.6-volt bus the drivetrain wants. Two in parallel
gives eight amp-hours and, just as importantly, the current headroom to run
realistic discharge profiles without abusing individual cells. Sixteen LG
INR21700-M50 cells in total. And eight series groups means eight sense taps,
which is what makes imbalance a measurement rather than an inference. Four
thermistors on top of that give us spatial thermal resolution — we can tell
which end of the pack is running hot, not just that it is hot.""")

    # -------------------------------------------------- 5 modelling / 2RC
    s = new_slide(prs, 5, "From 1RC to 2RC, and what OCV buys us")
    bullets(s, M, BODY_Y + 0.04, LEFT_W, 2.05, [
        "1RC caught the instant drop but missed slow recovery.",
        "A second branch separates fast transient from slow relaxation.",
        "Parameters fitted on a clean 0–4000 s HPPC segment.",
    ], size=16.5)
    text(s, M, 3.82, LEFT_W, 0.28, "2RC PARAMETERS", size=10, color=MUTED, bold=True)
    stat_strip(s, M, 4.14, LEFT_W, [
        ("R₀ 0.06142 Ω", "ohmic drop", ACCENT),
        ("R₁ 0.00820 Ω", "fast branch", ACCENT),
        ("C₁ 22.268 F", "τ₁ ≈ 0.18 s", MUTED),
    ])
    stat_strip(s, M, 5.12, LEFT_W, [
        ("R₂ 0.00882 Ω", "slow branch", ACCENT),
        ("C₂ 119.37 F", "τ₂ ≈ 1.05 s", MUTED),
        ("2RC", "Vt = OCV − IR₀ − V₁ − V₂", INK),
    ])
    text(s, M, 6.22, LEFT_W, 0.38,
         "Measured OCV moves 13.4 mV per 1% SOC — enough to observe charge state.",
         size=12, color=ACCENT, bold=True, line=1.22)
    picture(s, G("diag_2rc_ecm.png"), VIS_X, BODY_Y - 0.04, VIS_W, 2.30)
    picture(s, G("fig_ocv_soc.png"), VIS_X + 0.72, BODY_Y + 2.30, VIS_W - 1.44, 2.70)
    notes(s, """
We started with a single RC branch. It captured the instant ohmic drop but
consistently missed the slow recovery after a load step. Adding a second branch
fixed that — a fast branch at about 0.18 seconds and a slow one at about 1.05
seconds. All five parameters were fitted on a clean four-thousand-second HPPC
segment. The chart below is the measured open-circuit voltage curve from that
same estimation. It moves 13.4 millivolts per percent of state of charge, which
means voltage is a usable observer of charge state on this chemistry. Hold that
thought — it comes back at the end.""")

    # ------------------------------------------------------- 6 data pipeline
    s = new_slide(prs, 6, "From BLE frames to labelled rows")
    bullets(s, M, BODY_Y + 0.10, LEFT_W, 3.05, [
        "JBD BMS → BLE via bleak → jbd_logger v9 on the Pi.",
        "BLE fragmented long responses; frames reassembled before any parsing.",
        "NTC byte-offset fix realigned all four thermistor channels.",
        "cell_v1 sat ~0.25 V below pack median in every cycle.",
        "That one weak cell labelled 70.2% of rows Cell Imbalance.",
    ], size=16.5)
    rect(s, M, 5.02, LEFT_W, 1.62, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.22, 5.18, LEFT_W - 0.44, 0.26, "HANDLING THE SKEW",
         size=10, color=WARNING, bold=True)
    text(s, M + 0.22, 5.48, LEFT_W - 0.44, 1.06,
         "Physics-informed synthetic faults generated against datasheet limits, then "
         "down-sampled to an equal count per class — a 50/50 real-to-synthetic split "
         "that removes the normalcy bias without discarding real rows.",
         size=12.5, color=INK, line=1.24)
    picture(s, G("fig_class_distribution.png"), VIS_X, BODY_Y + 0.28, VIS_W, 4.55)
    notes(s, """
The pipeline is short on purpose: BMS, BLE through bleak, jbd_logger v9. Two
things bit us. BLE fragments long responses across frames, so early logs were
silently truncated — we now reassemble before parsing. And the four thermistors
were read at the wrong byte offset, scrambling the thermal channels. The bigger
problem was the labelling: because cell one is chronically low, a rule-based
labeller marked over seventy percent of rows as Cell Imbalance. We fixed that
with physics-informed synthetic faults rather than throwing real rows away.""")

    # ------------------------------------------------ 7 feature engineering
    s = new_slide(prs, 7, "Fifty-one features, and which ones matter")
    bullets(s, M, BODY_Y + 0.16, LEFT_W, 3.10, [
        "Raw frame gives 17 channels; we derive 51 features.",
        "Rolling mean and std over a ten-sample window.",
        "First derivatives: dV/dt, dI/dt, dSOC/dt, dT/dt.",
        "Per-cell rise and drop rates — sixteen directional features.",
        "Four one-hot driving modes and the NTC spread.",
    ], size=16.5)
    rect(s, M, 5.14, LEFT_W, 1.44, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.22, 5.28, LEFT_W - 0.44, 0.26, "LEAKAGE CONTROL",
         size=10, color=WARNING, bold=True)
    text(s, M + 0.22, 5.58, LEFT_W - 0.44, 0.92,
         "Rolling windows and derivatives are computed inside each (split, label) "
         "group, so no window ever straddles a train/test boundary.",
         size=12.5, color=INK, line=1.24)
    picture(s, G("fig_feature_importance.png"), VIS_X, BODY_Y + 0.12, VIS_W, 4.95)
    notes(s, """
The BMS frame gives us seventeen raw channels. We derive fifty-one features from
them: rolling means and standard deviations over a ten-sample window, first
derivatives of voltage, current, charge state and temperature, per-cell rise and
drop rates, the four one-hot driving modes and the thermistor spread. The chart
on the right is not our opinion — it is read straight out of the trained model.
Rolling voltage standard deviation dominates at fourteen percent, and notice the
orange bars: the driving-mode flags account for twelve percent between them.
Context genuinely matters to this classifier.""")

    # ------------------------------------------------------ 8 training set
    s = new_slide(prs, 8, "Building a training set that is not 70% one class")
    bullets(s, M, BODY_Y + 0.16, LEFT_W, 3.10, [
        "Real Normal rows anchor the healthy operating baseline.",
        "Synthetic faults generated against datasheet safety limits.",
        "Balanced to roughly 50/50 real-to-synthetic across six classes.",
        "Stratified 70/15/15 train, validation and test split.",
        "Test split never touched until final evaluation.",
    ], size=16.5)
    stat_strip(s, M, 5.28, LEFT_W, [
        ("208,010", "total rows", ACCENT),
        ("140,000", "train", ACCENT),
        ("30,000", "validation", MUTED),
        ("30,000", "test", CRITICAL),
    ])
    picture(s, G("fig_dataset_composition.png"), VIS_X, BODY_Y + 0.35, VIS_W, 4.50)
    notes(s, """
Given that skew, the training set had to be constructed rather than just
collected. Real Normal rows anchor what healthy operation looks like. On top of
that we generate synthetic faults — but generated against the datasheet safety
limits, so an overvoltage sample is physically plausible rather than random
noise. That gets us to 208,010 rows, roughly half real and half synthetic, split
seventy-fifteen-fifteen. The thirty-thousand-row test split is untouched until
final evaluation, and every number on the next two slides comes from it.""")

    # ------------------------------------------------------- 9 why xgboost
    s = new_slide(prs, 9, "We benchmarked all six — XGBoost still ships")
    headers = ["Model", "Accuracy", "Macro F1", "Latency", "Size", "Edge", "Verdict"]
    end_y = table(s, M, BODY_Y + 0.02, SW - 2*M, BENCH_ROWS and headers, BENCH_ROWS,
                  col_w=[1.60, 1.05, 1.00, 1.00, 0.95, 0.80, 2.30],
                  head_h=0.42, row_h=0.46, fs=11, hfs=10)
    picture(s, G("fig_deployment_tradeoff.png"), M, end_y + 0.10,
            SW - 2*M, 1.60)
    text(s, M, end_y + 1.78, SW - 2*M, 0.44, BENCH_FOOT, size=8.0,
         color=MUTED, line=1.24)
    notes(s, BENCH_NOTES)

    # -------------------------------------------------- 10 model performance
    s = new_slide(prs, 10, "Where the model is strong, and where it is not")
    bullets(s, M, BODY_Y + 0.14, LEFT_W, 2.40, [
        "Normal, Overvoltage, Overtemperature all clear 97% F1.",
        "Cell Imbalance recall is 65% — the weakest number here.",
        "Its misses land on Undervoltage, which is physically adjacent.",
        "A sagging weak cell looks like an undervoltage event.",
    ], size=15.5, gap=8)
    rect(s, M, 4.24, LEFT_W, 2.34, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.22, 4.38, LEFT_W - 0.44, 0.26, "WE ARE NOT HIDING THIS",
         size=10, color=CRITICAL, bold=True)
    text(s, M + 0.22, 4.70, LEFT_W - 0.44, 1.74,
         "28.7% of true Cell Imbalance samples are predicted Undervoltage. The two "
         "share a signature: one cell drops, pack voltage follows. Separating them "
         "needs more real imbalance events, not more synthetic ones — which is "
         "exactly what the next data campaign is for.",
         size=12.5, color=INK, line=1.26)
    picture(s, G("fig_per_class_metrics.png"), VIS_X, BODY_Y + 0.02, VIS_W, 2.45)
    picture(s, G("fig_confusion_matrix.png"), VIS_X + 0.62, BODY_Y + 2.52, VIS_W - 1.24, 2.70)
    notes(s, """
Here is the honest breakdown. Normal, Overvoltage and Overtemperature all clear
ninety-seven percent F1 — those classes are solved. Cell Imbalance recall is
sixty-five percent, and that is the weakest number in this deck. Look at where
the misses go: twenty-eight point seven percent of true imbalance samples get
predicted as Undervoltage. That is not a random error. A sagging weak cell and
an undervoltage event share a signature — one cell drops and the pack voltage
follows. Separating them needs more real imbalance events, and that is what our
next data campaign is for.""")

    # --------------------------------------------- 11 classes + confidence
    s = new_slide(prs, 11, "Six classes, and the confidence to say “I don't know”")
    text(s, M, BODY_Y + 0.06, LEFT_W, 0.28, "THE SIX FAULT CLASSES", size=10,
         color=ACCENT, bold=True)
    classes = ["Normal", "Cell Imbalance", "Weak Cell",
               "Overvoltage", "Undervoltage", "Overtemperature"]
    cw = (LEFT_W - 0.16) / 2
    for i, cname in enumerate(classes):
        cx = M + (i % 2) * (cw + 0.16)
        cy = BODY_Y + 0.40 + (i // 2) * 0.56
        rect(s, cx, cy, cw, 0.46, fill=PANEL, line=HAIRLINE, lw=0.75)
        d = rect(s, cx + 0.16, cy + 0.175, 0.11, 0.11,
                 fill=ACCENT if i == 0 else CRITICAL, shape=MSO_SHAPE.OVAL)
        d.line.fill.background()
        text(s, cx + 0.40, cy, cw - 0.50, 0.46, cname, size=13.5, color=INK,
             anchor=MSO_ANCHOR.MIDDLE)
    bullets(s, M, 3.68, LEFT_W, 2.30, [
        "Below 0.50 the model abstains — no alert is raised.",
        "0.50–0.85 raises a logged warning, non-blocking for the operator.",
        "Above 0.85 becomes an alert with a corrective action.",
        "A confident wrong answer is worse than an honest abstention.",
    ], size=16)
    picture(s, G("fig_confidence_bands.png"), VIS_X, BODY_Y + 0.16, VIS_W, 1.55)
    picture(s, G("fig_confusion_matrix.png"), VIS_X + 0.30, BODY_Y + 1.92, VIS_W - 0.60, 3.30)
    notes(s, """
Six classes. The part I care more about is the confidence framework around them.
The classifier returns a probability and we split it three ways. Below 0.50 we
abstain outright — nothing is raised and the sample goes for review. Between
0.50 and 0.85 we log a warning that does not block the operator. Only above 0.85
do we raise an alert with a corrective action. In a safety-critical system a
confidently wrong prediction is worse than none: an abstention sends someone to
look, a false alert teaches them to ignore the dashboard.""")

    # ------------------------------------------------------------- 12 OOD
    s = new_slide(prs, 12, "The seventh case: a fault we have never seen")
    bullets(s, M, BODY_Y + 0.16, LEFT_W, 3.05, [
        "A six-class model will force every input into one of six.",
        "An unseen failure mode gets a confident, wrong label.",
        "An IsolationForest gate sits in front of the classifier.",
        "Score below threshold routes the window to UNKNOWN_FAULT_OOD.",
        "Tested on 49 in-distribution and 49 synthetic-unknown windows.",
    ], size=16)
    rect(s, M, 5.10, LEFT_W, 1.48, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.22, 5.24, LEFT_W - 0.44, 0.26, "THE TRADE WE CHOSE",
         size=10, color=WARNING, bold=True)
    text(s, M + 0.22, 5.54, LEFT_W - 0.44, 0.96,
         "We tuned the gate for zero false positives. It never wrongly rejects a "
         "known-good window — and it only catches one unknown in four. On a "
         "safety dashboard, that is the right way round.",
         size=12.5, color=INK, line=1.24)
    picture(s, G("fig_ood_panel.png"), VIS_X, BODY_Y + 0.55, VIS_W, 2.35)
    picture(s, G("diag_confidence_ladder.png"), VIS_X, BODY_Y + 3.05, VIS_W, 2.00)
    notes(s, """
There is a failure mode every classifier has: give it something it has never
seen, and it will still return one of its six labels, often confidently. So
before the classifier runs, an IsolationForest scores the window. If that score
falls below threshold, we do not classify at all — we flag it as an unknown
fault and escalate. Tested on forty-nine in-distribution and forty-nine
synthetic-unknown windows: AUROC of 0.913, one hundred percent precision, zero
false positives. It catches one unknown in four. We tuned it that way
deliberately — on a safety dashboard, never crying wolf matters more.""")

    # ------------------------------------------------------- 13 hardware
    s = new_slide(prs, 13, "Three tiers, no single point of failure")
    bullets(s, M, BODY_Y + 0.10, LEFT_W, 3.10, [
        "Tier 1 — JBD BMS senses eight cell taps and four NTCs.",
        "Tier 2 — Pi 5 runs logger, XGBoost inference and dashboard.",
        "Tier 3 — Arduino Uno R4 watches the Pi's heartbeat.",
        "Missed heartbeat pulls the RUN pin and resets the Pi.",
        "Inference stays at the edge: no link, no safety gap.",
    ], size=16.5)
    rect(s, M, 5.16, LEFT_W, 1.30, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.22, 5.30, LEFT_W - 0.44, 0.26, "ACCELERATION PATH",
         size=10, color=ACCENT, bold=True)
    text(s, M + 0.22, 5.60, LEFT_W - 0.44, 0.76,
         "Zynq-7000 SoC moves the same tree traversal into programmable logic, "
         "freeing the CPU for the logger and the BLE link.",
         size=13, color=INK, line=1.22)
    picture(s, G("diag_hardware.png"), VIS_X, BODY_Y + 0.02, VIS_W, 3.05)
    hy = BODY_Y + 3.20
    picture(s, E("p06_img1_x51.jpeg"), VIS_X, hy, VIS_W/2 - 0.10, 1.55, card=True)
    picture(s, E("p06_img2_x52.jpeg"), VIS_X + VIS_W/2 + 0.10, hy, VIS_W/2 - 0.10, 1.55, card=True)
    caption(s, VIS_X, hy + 1.58, VIS_W/2 - 0.10, "Raspberry Pi 5")
    caption(s, VIS_X + VIS_W/2 + 0.10, hy + 1.58, VIS_W/2 - 0.10, "Arduino Uno R4 WiFi")
    notes(s, """
Three tiers, each doing what the others cannot. The JBD BMS senses: eight taps,
four thermistors, pack voltage and current. The Pi 5 runs the logger and the
inference. Inference sits at the edge deliberately — push it
to a server and every network hiccup becomes an unmonitored window. The third
tier exists because general-purpose computers hang. An Arduino on its own rail
watches for a heartbeat and pulls the Pi's RUN pin if it stops. Zynq-7000 is our
path to take inference off the CPU entirely.""")

    # ---------------------------------------------------- 14 system flow
    s = new_slide(prs, 14, "How the whole thing fits together")
    picture(s, G("diag_system_flow.png"), M, BODY_Y + 0.12, SW - 2*M, 3.35)
    cols = [
        ("EDGE", "Sampling, feature engineering and inference all happen on the pack. "
                 "The Pi never needs the network to keep the pack safe.", ACCENT),
        ("CLOUD", "Railway hosts the Flask dashboard — REST and server-sent events — "
                 "with PostgreSQL for telemetry, cycle history and the active profile.", ACCENT),
        ("INTERFACE", "Three browser surfaces served from Railway; the Pi only ever "
                      "dials out, so no inbound port is opened on the pack.", CRITICAL),
    ]
    cwid = (SW - 2*M - 2*0.24) / 3
    for i, (t, d, col) in enumerate(cols):
        cx = M + i * (cwid + 0.24)
        rect(s, cx, 5.20, cwid, 1.42, fill=PANEL, line=HAIRLINE, lw=0.75)
        b = rect(s, cx, 5.20, cwid, 0.065, fill=col); b.line.fill.background()
        text(s, cx + 0.22, 5.36, cwid - 0.44, 0.26, t, size=10.5, color=col, bold=True)
        text(s, cx + 0.22, 5.66, cwid - 0.44, 0.88, d, size=11.5, color=INK, line=1.26)
    notes(s, """
This is the whole system on one slide. Three columns. On the edge, sampling,
feature engineering and inference all happen on the pack itself — the Pi never
needs the network to keep the battery safe. In the middle, Railway hosts the Flask
dashboard — REST and server-sent events — with PostgreSQL holding telemetry,
cycle history and the active chemistry profile. On the right, three browser surfaces.
The Pi pushes results up to Railway, which means we never open an
inbound port on the pack — a reviewer can open the dashboard from anywhere and
the attack surface on the hardware stays closed.""")

    # ------------------------------------------------------- 15 dashboard
    s = new_slide(prs, 15, "The dashboard an operator actually reads")
    bullets(s, M, BODY_Y + 0.10, LEFT_W, 3.10, [
        "Flask dashboard deployed on Railway.",
        "Live per-cell voltages, pack current and four temperature zones.",
        "Charge and discharge ETA smoothed with an EMA filter.",
        "Driving context from current magnitude at T versus T-1.",
        "Alert history logs value, threshold, severity and resolution time.",
    ], size=16.5)
    text(s, M, 5.18, LEFT_W, 0.28, "FOUR-MODE DRIVING CONTEXT", size=10,
         color=ACCENT, bold=True)
    modes = [("IDLE", MUTED), ("ACCEL", CRITICAL), ("CRUISE", ACCENT), ("DECEL", WARNING)]
    mw = (LEFT_W - 3 * 0.14) / 4
    for i, (m, col) in enumerate(modes):
        mx = M + i * (mw + 0.14)
        rect(s, mx, 5.52, mw, 0.62, fill=BG, line=col, lw=1.25)
        text(s, mx, 5.52, mw, 0.62, m, size=14, color=col, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, M, 6.26, LEFT_W, 0.30,
         "Thresholds follow the mode — a sag under ACCEL is not a sag at IDLE.",
         size=11.5, color=MUTED)
    picture(s, E("p07_img1_x61.jpeg"), VIS_X, BODY_Y + 0.20, VIS_W, 2.20, card=True)
    picture(s, E("p08_img2_x68.png"),  VIS_X, BODY_Y + 2.62, VIS_W, 2.10, card=True)
    caption(s, VIS_X, BODY_Y + 4.78, VIS_W,
            "Live sensing tiles (top) and the critical-alarm path (bottom)")
    notes(s, """
The dashboard is a Flask service on Railway, fed by the Pi. It is
operator-facing, not engineer-facing: live per-cell voltages, pack current with
direction, four thermal zones, and a charge or discharge ETA smoothed with an
EMA so it does not jitter. The piece worth noting is driving context. Four modes
from the change in current magnitude between samples — because a voltage sag
under hard acceleration is normal, and the same sag at idle is a fault.
Thresholds follow the mode.""")

    # ------------------------------------------ 16 thermal + driving context
    s = new_slide(prs, 16, "Context is a feature, not a label on a chart")
    bullets(s, M, BODY_Y + 0.14, LEFT_W, 2.55, [
        "Four NTCs diverge by up to 8.3 °C within one pack.",
        "That spread is fed to the model as ntc_spread.",
        "Mode is set from |I(T)| versus |I(T-1)|, with hysteresis.",
        "Five-sample hysteresis stops mode flapping on noise.",
    ], size=16)
    rect(s, M, 4.36, LEFT_W, 2.22, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.22, 4.50, LEFT_W - 0.44, 0.26, "WHY THE MODEL CARES",
         size=10, color=ACCENT, bold=True)
    text(s, M + 0.22, 4.80, LEFT_W - 0.44, 1.64,
         "mode_IDLE, mode_DECEL and mode_CRUISE together carry 12.4% of the model's "
         "total gain, and ntc_spread another 5.0%. Nearly a fifth of the decision "
         "comes from context the pack-level sensors alone could never provide.",
         size=12.5, color=INK, line=1.26)
    picture(s, G("fig_thermal_zones.png"), VIS_X, BODY_Y + 0.02, VIS_W, 3.10)
    picture(s, G("fig_driving_modes.png"), VIS_X, BODY_Y + 3.20, VIS_W, 1.85)
    notes(s, """
Two things the model leans on that are easy to overlook. First, thermal
resolution: the four thermistors diverge by as much as eight point three degrees
within a single pack, and that spread goes into the model as a feature rather
than just onto the dashboard. Second, operating mode, set from the change in
current magnitude with a five-sample hysteresis so it does not flap on noise.
Together, the mode flags and the thermal spread account for nearly a fifth of
the model's total gain. That is context the pack-level sensors alone could never
give us.""")

    # ------------------------------------------------- 17 cycle prognosis
    s = new_slide(prs, 17, "Comparing this cycle against every cycle before it")
    bullets(s, M, BODY_Y + 0.14, LEFT_W, 3.05, [
        "39 cycles logged: 21 discharge, 18 charge.",
        "Every cycle scored 1.0 on data quality; zero alerts raised.",
        "Expected sag is computed from load, then compared to actual.",
        "Deviation from history flags degradation before a threshold breaks.",
        "Balancing is visible: end-of-cycle spread falls below start.",
    ], size=16)
    stat_strip(s, M, 5.28, LEFT_W, [
        ("39", "cycles logged", ACCENT),
        ("21 / 18", "discharge / charge", ACCENT),
        ("1.0", "data quality", ACCENT),
        ("0", "alerts raised", MUTED),
    ])
    picture(s, G("fig_cycle_history.png"), VIS_X, BODY_Y + 0.45, VIS_W, 3.30)
    picture(s, E("p07_img2_x62.jpeg"), VIS_X, BODY_Y + 3.92, VIS_W, 1.35, card=True)
    notes(s, """
The last analytical layer is prognosis. We keep a history of every cycle the
pack has run — thirty-nine so far, twenty-one discharge and eighteen charge, all
scoring one point zero on data quality. For each live cycle the system computes
an expected voltage sag from the load, then compares it to the actual sag. A
cycle that sags worse than its own history is degrading, and we can say that
long before any absolute threshold is breached. The chart on the right also
shows the balancing working: end-of-cycle spread is consistently below
start-of-cycle spread.""")

    # ------------------------------------------------- 18 battery params UI
    s = new_slide(prs, 18, "Two uploads is the entire onboarding flow")
    bullets(s, M, BODY_Y + 0.14, LEFT_W, 3.05, [
        "Drop the manufacturer PDF: chemistry and limits are parsed out.",
        "Drop a CSV or XLSX: the dataset is profiled and previewed.",
        "No YAML, no config file, no redeploy, no developer.",
        "Parsed values are editable before they become the active profile.",
        "The same screen feeds both the thresholds and the retrainer.",
    ], size=16)
    rect(s, M, 5.28, LEFT_W, 1.32, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.22, 5.42, LEFT_W - 0.44, 0.26, "WHAT GETS EXTRACTED",
         size=10, color=ACCENT, bold=True)
    text(s, M + 0.22, 5.72, LEFT_W - 0.44, 0.80,
         "Manufacturer · cell model · chemistry · V_nom · V_max · V_min · "
         "nominal capacity · charge and discharge current limits · thermal envelopes.",
         size=12, color=INK, line=1.26)
    picture(s, G("mock_battery_params.png"), VIS_X, BODY_Y + 0.55, VIS_W, 2.55, card=True)
    picture(s, E("p09_img1_x72.png"), VIS_X, BODY_Y + 3.30, VIS_W, 1.85, card=True)
    caption(s, VIS_X, BODY_Y + 5.20, VIS_W, "Upload screen, and the parsed result")
    notes(s, """
This is the onboarding flow in full. Two upload targets. Drop the manufacturer
PDF and the parser pulls out chemistry, nominal, maximum and minimum voltage,
capacity, current limits and thermal envelopes. Drop a CSV or spreadsheet and
the dataset gets profiled and previewed. There is no YAML file, no redeploy and
no developer in the loop. The parsed values land in an editable form — shown
underneath — so an engineer can correct anything the parser got wrong before it
becomes the active profile. That same screen feeds both the threshold matrix and
the retrainer.""")

    # ----------------------------------------------- 19 multi-chemistry
    s = new_slide(prs, 19, "Swap the chemistry, not the codebase")
    bullets(s, M, BODY_Y + 0.06, LEFT_W, 3.32, [
        "Upload a datasheet PDF; the parser reads the limits.",
        "Extracts V_nom, V_max, V_min, capacity, current, thermal.",
        "Pack sizing derives S and P from the bus target.",
        "Tiering: NMC reuse, NCA/LCO shift, LFP remap, LTO rescale.",
        "Overvoltage warns 95%, critical 100%; overcurrent 90%.",
        "active_profile.json and PostgreSQL sync live, no restart.",
    ], size=15.5, gap=8)
    rect(s, M, 5.34, LEFT_W, 1.16, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.22, 5.46, LEFT_W - 0.44, 0.26, "IN-BROWSER RETRAINING",
         size=10, color=WARNING, bold=True)
    text(s, M + 0.22, 5.74, LEFT_W - 0.44, 0.66,
         "Upload field telemetry from the new pack and retrain XGBoost from the "
         "dashboard — the adaptation loop closes without a developer.",
         size=13, color=INK, line=1.22)
    lw_ = 2.42
    picture(s, G("diag_configurator.png"), VIS_X, BODY_Y + 0.06, lw_, 4.46)
    picture(s, G("diag_chemistry_tiering.png"), VIS_X + lw_ + 0.20,
            BODY_Y + 0.06, VIS_W - lw_ - 0.20, 4.46)
    notes(s, """
This is what makes it reusable. The parser pulls the limits, pack sizing derives
the series and parallel counts, and then the chemistry gets tiered. NMC is
direct reuse because that is what we characterised. NCA and LCO share the 4.2
volt ceiling, so they only need a threshold shift. LFP needs a real remap to a
2.50 to 3.65 volt window — remember that flat OCV curve. And LTO, at 2.4 volts
nominal, needs every limit rescaled. Thresholds are two-tier, and the active
profile syncs to PostgreSQL live with no server restart.""")

    # ------------------------------------------------------------ 20 close
    closing_slide(prs, 20)

    # ------------------------------------------------------------ 21 refs
    references_slide(prs, 21)

    prs.save(OUT)
    print("wrote", os.path.relpath(OUT, ROOT), "|", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
    return OUT


if __name__ == "__main__":
    build()
