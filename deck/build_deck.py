#!/usr/bin/env python3
"""Assemble AI_PBMS_8Slide.pptx from the generated and extracted assets."""
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
OUT  = os.path.join(ROOT, "AI_PBMS_8Slide.pptx")

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
    ["XGBoost", ("94.19%", ACCENT, True), ("0.905", MUTED, False), ("0.462 ms", ACCENT, True), ("1.40 MB", MUTED, False), ("Yes", ACCENT, False), ("Deployed — 1 row, no buffer", ACCENT, True)],
    ["Transformer", ("95.11%", INK, False), ("0.918", MUTED, False), ("0.419 ms", MUTED, False), ("0.31 MB", MUTED, False), ("Warn", WARNING, False), ("Best accuracy; 60-row warm-up", WARNING, False)],
    ["LSTM", ("87.03%", INK, False), ("0.776", MUTED, False), ("0.532 ms", MUTED, False), ("0.28 MB", MUTED, False), ("Warn", WARNING, False), ("Sequential, weakest F1", MUTED, False)],
    ["Random Forest", ("89.37%", INK, False), ("0.824", MUTED, False), ("33.770 ms", MUTED, False), ("176.41 MB", MUTED, False), ("No", CRITICAL, False), ("176 MB, 73× the latency", CRITICAL, False)],
    ["SVM (RBF)", ("88.53%", INK, False), ("0.807", MUTED, False), ("0.568 ms", MUTED, False), ("2.82 MB", MUTED, False), ("Yes", ACCENT, False), ("Would not scale past 20k rows", MUTED, False)],
    ["Rule-based BMS", ("22.09%", INK, False), ("0.224", MUTED, False), ("5 µs", MUTED, False), ("~0 MB", MUTED, False), ("Yes", ACCENT, False), ("0% recall on Weak Cell", CRITICAL, False)],
]

BENCH_FOOT = (
    "All six trained and scored here on the identical 30,000-row held-out split with the same 51 features; "
    "latency is the median single-row prediction on a 4-core CPU, not a Pi 5. "
    "Sequence models additionally see a 60-row lookback. SVM trained on a stratified 20k subsample — "
    "full-data RBF did not converge in usable time, which is part of the verdict."
)

BENCH_NOTES = """
We did not argue about which model to use — we trained all six on the identical
split and measured them. The Transformer is actually the most accurate at 95.11
percent, a point ahead of XGBoost. We still shipped XGBoost, and here is the
honest reason: the Transformer needs a sixty-row lookback, which at one hertz
means a full minute of buffered data before it can say anything, plus a torch
runtime on the Pi and no feature attribution an engineer can interrogate.
XGBoost predicts from a single row, instantly, and tells you which features
drove it. Random Forest is 176 megabytes and seventy-three times slower for
worse accuracy. And look at the bottom row: a conventional rule-based BMS scores
twenty-two percent — because cell one's chronic gap puts eighty-four percent of
healthy rows over the imbalance threshold, so it false-alarms constantly and
still never detects a weak cell.
"""


# ===================================================================
#  AI_PBMS_8Slide.pptx — the full 20-slide story condensed into eight.
#  Every slide carries what was previously two or three slides, so the
#  layouts run denser: a left content column, a stat or parameter strip,
#  and a stacked pair of visuals on the right.
# ===================================================================

def two_col_bullets(slide, x, y, w, h, items, size=14.5, gap=7):
    """Two-column bullet block, for the slides that carry six-plus points."""
    half = (w - 0.30) / 2
    n = (len(items) + 1) // 2
    bullets(slide, x, y, half, h, items[:n], size=size, gap=gap)
    bullets(slide, x + half + 0.30, y, half, h, items[n:], size=size, gap=gap)


def mini_head(slide, x, y, w, label, color=None):
    text(slide, x, y, w, 0.24, label, size=9.5, color=color or ACCENT, bold=True)


def build():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)
    G = lambda n: os.path.join(GEN, n)
    E = lambda n: os.path.join(EXT, n)

    # =============================================================== 1
    s = new_slide(prs, 1, "We could not buy this dataset, so we built it",
                  eyebrow="AI-PBMS — AI-Powered Predictive Battery Management System  ·  "
                          "Team ANS_4X  ·  PSG iTech")
    bullets(s, M, BODY_Y + 0.26, LEFT_W, 2.35, [
        "Public BMS datasets hide per-cell voltages behind pack totals.",
        "Imbalance and weak-cell faults are invisible at pack level.",
        "So we instrumented a physical 8S2P NMC pack end to end.",
        "Programmable supply charges; electronic load drives discharge.",
    ], size=15)
    stat_strip(s, M, 4.28, LEFT_W, [
        ("~50", "cycles", ACCENT), ("~3 hrs", "each", ACCENT),
        (">100 hrs", "logged", ACCENT), ("~155,000", "rows", CRITICAL),
    ])
    rect(s, M, 5.34, LEFT_W, 1.30, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, M + 0.22, 5.46, LEFT_W - 0.44, "WHAT THE DATA SHOWED", CRITICAL)
    text(s, M + 0.22, 5.74, LEFT_W - 0.44, 0.80,
         "Cell 1 runs 289 mV below its neighbours in every cycle. A pack-level "
         "voltmeter reads 30.5 V and calls this healthy.",
         size=12, color=INK, line=1.26)
    picture(s, E("p03_img1_x38.jpeg"), VIS_X, BODY_Y + 0.14, VIS_W, 1.78, card=True)
    picture(s, G("fig_cell_traces.png"), VIS_X, BODY_Y + 2.06, VIS_W, 3.10)
    notes(s, """
Every public battery dataset reports pack-level voltage and current, which is
useless to us: imbalance and weak-cell faults only show in the spread between
individual cells. So we built the dataset — an 8S2P NMC pack, a JBD BMS on all
eight taps, roughly fifty cycles and 155,000 rows. The chart bottom right is
what a hundred hours bought us: seven cells tracking together, and cell one
sitting 289 millivolts below them for the entire discharge. That one defect
shaped everything that follows.""")

    # =============================================================== 2
    s = new_slide(prs, 2, "The pack, and the model of the pack")
    two_col_bullets(s, M, BODY_Y + 0.10, LEFT_W, 2.20, [
        "8S sets the 33.6 V nominal bus voltage.",
        "2P buys 8 Ah and current headroom.",
        "Sixteen LG INR21700-M50 cells.",
        "Eight taps make imbalance observable.",
        "Four NTCs give thermal resolution.",
        "1RC missed the slow relaxation.",
    ], size=13.5)
    mini_head(s, M, 4.02, LEFT_W, "2RC PARAMETERS — FITTED ON THE 0–4000 s HPPC SEGMENT", MUTED)
    stat_strip(s, M, 4.32, LEFT_W, [
        ("R₀ 0.06142 Ω", "ohmic drop", ACCENT),
        ("R₁ 0.00820 Ω", "fast branch", ACCENT),
        ("C₁ 22.268 F", "τ₁ ≈ 0.18 s", MUTED),
    ])
    stat_strip(s, M, 5.30, LEFT_W, [
        ("R₂ 0.00882 Ω", "slow branch", ACCENT),
        ("C₂ 119.37 F", "τ₂ ≈ 1.05 s", MUTED),
        ("13.4 mV", "per 1% SOC", INK),
    ])
    text(s, M, 6.38, LEFT_W, 0.30,
         "Vt = OCV(SOC) − I·R₀ − V_RC1 − V_RC2",
         size=12, color=ACCENT, bold=True)
    picture(s, G("diag_pack_8s2p.png"), VIS_X, BODY_Y + 0.02, VIS_W, 2.12)
    picture(s, G("diag_2rc_ecm.png"), VIS_X, BODY_Y + 2.42, VIS_W, 2.55)
    notes(s, """
Eight in series gives the 33.6-volt bus the drivetrain wants; two in parallel
gives eight amp-hours and the current headroom for realistic profiles. Eight
series groups means eight sense taps, so imbalance is measured rather than
inferred. On modelling, one RC branch caught the instant ohmic drop but missed
the slow recovery after a load step, so we went to two — fast at 0.18 seconds,
slow at 1.05. All five parameters were fitted on a clean HPPC segment, and the
same estimation gave us the OCV curve: 13.4 millivolts per percent of charge.""")

    # =============================================================== 3
    s = new_slide(prs, 3, "From BLE frames to a balanced training set")
    two_col_bullets(s, M, BODY_Y + 0.10, LEFT_W, 2.35, [
        "JBD BMS → BLE (bleak) → jbd_logger v9.",
        "Fragmented BLE frames reassembled first.",
        "NTC byte-offset fix realigned four channels.",
        "17 raw channels become 51 features.",
        "Rolling stats, derivatives, per-cell rates.",
        "cell_v1 skew labelled 70.2% Cell Imbalance.",
    ], size=13.5)
    rect(s, M, 4.14, LEFT_W, 1.22, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, M + 0.22, 4.26, LEFT_W - 0.44, "HANDLING THE SKEW", WARNING)
    text(s, M + 0.22, 4.54, LEFT_W - 0.44, 0.74,
         "Physics-informed synthetic faults generated against datasheet limits, "
         "then balanced to an equal count per class — 50/50 real to synthetic.",
         size=11.5, color=INK, line=1.24)
    rect(s, M, 5.48, LEFT_W, 1.16, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, M + 0.22, 5.60, LEFT_W - 0.44, "LEAKAGE CONTROL")
    text(s, M + 0.22, 5.88, LEFT_W - 0.44, 0.70,
         "Windows and derivatives computed inside each (split, label) group, so "
         "none straddles a train/test boundary. 208,010 rows, 70/15/15.",
         size=11.5, color=INK, line=1.24)
    picture(s, G("fig_feature_importance.png"), VIS_X, BODY_Y + 0.02, VIS_W, 2.75)
    picture(s, G("fig_dataset_composition.png"), VIS_X, BODY_Y + 2.88, VIS_W, 2.30)
    notes(s, """
The pipeline is short on purpose. Two things bit us: BLE fragments long
responses across frames, so early logs were silently truncated, and the four
thermistors were read at the wrong byte offset. From seventeen raw channels we
derive fifty-one features — rolling statistics, first derivatives, per-cell rise
and drop rates, driving-mode flags. The chart top right is read out of the
trained model, not our opinion. Because cell one is chronically low, a
rule-based labeller marked seventy percent of rows as imbalance, so we balanced
with physics-informed synthetic faults rather than discarding real data.""")

    # =============================================================== 4
    s = new_slide(prs, 4, "We benchmarked all six on the same split")
    headers = ["Model", "Accuracy", "Macro F1", "Latency", "Size", "Edge", "Verdict"]
    rows = BENCH_ROWS
    end_y = table(s, M, BODY_Y + 0.02, SW - 2*M, headers, rows,
                  col_w=[1.60, 1.05, 1.00, 1.00, 0.95, 0.80, 2.30],
                  head_h=0.42, row_h=0.44, fs=11, hfs=10)
    picture(s, G("fig_model_benchmark.png"), M + 0.30, end_y + 0.14,
            SW - 2*M - 0.60, 1.56)
    text(s, M, end_y + 1.80, SW - 2*M, 0.42, BENCH_FOOT, size=8.2,
         color=MUTED, line=1.24)
    notes(s, BENCH_NOTES)

    # =============================================================== 5
    s = new_slide(prs, 5, "Six classes, honest confidence, one gate")
    two_col_bullets(s, M, BODY_Y + 0.08, LEFT_W, 2.05, [
        "Normal, Overvoltage, Overtemp clear 97% F1.",
        "Cell Imbalance recall 65% — the weak spot.",
        "Misses land on Undervoltage, physically adjacent.",
        "Below 0.50 the model abstains outright.",
        "0.50–0.85 warns; above 0.85 alerts.",
        "An IsolationForest gate runs before the classifier.",
    ], size=13.5)
    stat_strip(s, M, 3.90, LEFT_W, [
        ("0.913", "OOD AUROC", ACCENT),
        ("100%", "OOD precision", ACCENT),
        ("0.0%", "false positives", ACCENT),
        ("24.5%", "OOD recall", CRITICAL),
    ])
    rect(s, M, 4.96, LEFT_W, 1.66, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, M + 0.22, 5.08, LEFT_W - 0.44, "WE ARE NOT HIDING THIS", CRITICAL)
    text(s, M + 0.22, 5.36, LEFT_W - 0.44, 1.18,
         "28.7% of true Cell Imbalance samples are predicted Undervoltage — one "
         "cell drops, pack voltage follows. Separating them needs more real "
         "imbalance events, not more synthetic ones. A confident wrong answer is "
         "worse than an honest abstention.",
         size=11.5, color=INK, line=1.24)
    picture(s, G("fig_per_class_metrics.png"), VIS_X, BODY_Y + 0.02, VIS_W, 2.10)
    picture(s, G("fig_confusion_matrix.png"), VIS_X + 1.45, BODY_Y + 2.18, VIS_W - 2.90, 1.55)
    picture(s, G("diag_confidence_ladder.png"), VIS_X, BODY_Y + 3.82, VIS_W, 1.45)
    notes(s, """
Normal, Overvoltage and Overtemperature all clear ninety-seven percent F1. Cell
Imbalance recall is sixty-five, and that is the weakest number here — its misses
go to Undervoltage, which is physically sensible: one cell drops and pack
voltage follows. Around the classifier we wrap two things. A confidence band:
below zero-point-five we abstain, up to zero-eight-five we warn, above that we
alert. And in front of it, an IsolationForest gate for failure modes we have
never seen — AUROC nine-one-three, a hundred percent precision, zero false
positives, catching one unknown in four. Tuned that way deliberately.""")

    # =============================================================== 6
    s = new_slide(prs, 6, "Three tiers at the edge, three surfaces in the browser")
    two_col_bullets(s, M, BODY_Y + 0.08, LEFT_W, 2.10, [
        "JBD BMS senses eight taps and four NTCs.",
        "Pi 5 runs logger, inference and dashboard.",
        "Arduino R4 watches the Pi's heartbeat.",
        "Missed beat pulls RUN pin, resets the Pi.",
        "Inference stays local: no link, no safety gap.",
        "Cloudflare tunnel opens no inbound port.",
    ], size=13.5)
    rect(s, M, 3.94, LEFT_W, 1.18, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, M + 0.22, 4.06, LEFT_W - 0.44, "ACCELERATION PATH")
    text(s, M + 0.22, 4.34, LEFT_W - 0.44, 0.70,
         "Zynq-7000 SoC moves the same tree traversal into programmable logic, "
         "freeing the CPU for the dashboard and the BLE link.",
         size=11.5, color=INK, line=1.24)
    hy = 5.26
    picture(s, E("p06_img1_x51.jpeg"), M, hy, LEFT_W/2 - 0.12, 1.10, card=True)
    picture(s, E("p06_img2_x52.jpeg"), M + LEFT_W/2 + 0.12, hy, LEFT_W/2 - 0.12, 1.10, card=True)
    caption(s, M, hy + 1.13, LEFT_W/2 - 0.12, "Raspberry Pi 5")
    caption(s, M + LEFT_W/2 + 0.12, hy + 1.13, LEFT_W/2 - 0.12, "Arduino Uno R4 WiFi")
    picture(s, G("diag_hardware.png"), VIS_X, BODY_Y + 0.06, VIS_W, 2.45)
    picture(s, G("diag_system_flow.png"), VIS_X, BODY_Y + 2.62, VIS_W, 2.55)
    notes(s, """
Three tiers, each doing what the others cannot. The BMS senses, the Pi 5 runs
the logger and the inference and the dashboard, and an Arduino on its own power
rail watches for a heartbeat — if it stops, it pulls the Pi's RUN pin and forces
a reset. Inference sits at the edge deliberately: push it to a server and every
network hiccup becomes an unmonitored window. The lower diagram is the whole
data path — edge, service, interface — with everything published through a
Cloudflare tunnel so we never open an inbound port on the Pi.""")

    # =============================================================== 7
    s = new_slide(prs, 7, "The platform an operator actually uses")
    two_col_bullets(s, M, BODY_Y + 0.08, LEFT_W, 2.10, [
        "Flask on the Pi, live per-cell voltages.",
        "Pack current and four temperature zones.",
        "Charge/discharge ETA smoothed by EMA.",
        "Four driving modes from |I(T)| vs |I(T-1)|.",
        "39 cycles compared against their own history.",
        "Alert log: value, threshold, severity, resolution.",
    ], size=13.5)
    modes = [("IDLE", MUTED), ("ACCEL", CRITICAL), ("CRUISE", ACCENT), ("DECEL", WARNING)]
    mw = (LEFT_W - 3 * 0.12) / 4
    for i, (m, col) in enumerate(modes):
        mx = M + i * (mw + 0.12)
        rect(s, mx, 3.92, mw, 0.52, fill=BG, line=col, lw=1.2)
        text(s, mx, 3.92, mw, 0.52, m, size=12, color=col, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, M, 4.62, LEFT_W, 2.00, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, M + 0.22, 4.74, LEFT_W - 0.44, "CONTEXT IS A FEATURE")
    text(s, M + 0.22, 5.02, LEFT_W - 0.44, 1.50,
         "A sag under ACCEL is normal; the same sag at IDLE is a fault, so "
         "thresholds follow the mode. The three mode flags carry 12.4% of the "
         "model's total gain and ntc_spread another 5.0% — nearly a fifth of the "
         "decision comes from context pack-level sensors cannot provide.",
         size=11.5, color=INK, line=1.24)
    picture(s, G("mock_landing.png"), VIS_X, BODY_Y + 0.04, VIS_W, 1.95, card=True)
    picture(s, E("p07_img1_x61.jpeg"), VIS_X, BODY_Y + 2.08, VIS_W, 1.50, card=True)
    picture(s, G("fig_cycle_history.png"), VIS_X, BODY_Y + 3.68, VIS_W, 1.55)
    notes(s, """
The platform is Flask on the Pi behind a Cloudflare tunnel. It is
operator-facing: live per-cell voltages, pack current with direction, four
thermal zones, and an ETA smoothed with an EMA so it does not jitter. The piece
worth calling out is driving context — four modes derived from the change in
current magnitude, because a voltage sag under hard acceleration is normal and
the same sag at idle is a fault. And the cycle engine compares each live cycle
against the average of all thirty-nine before it, so degradation shows up before
any absolute threshold is breached.""")

    # =============================================================== 8
    s = new_slide(prs, 8, "Swap the chemistry, not the codebase")
    two_col_bullets(s, M, BODY_Y + 0.08, LEFT_W, 2.05, [
        "Upload a datasheet PDF; the parser reads limits.",
        "V_nom, V_max, V_min, capacity, current, thermal.",
        "Pack sizing derives S and P from the bus target.",
        "NMC reuse → NCA/LCO shift → LFP remap → LTO rescale.",
        "Overvoltage warns 95%, critical 100%.",
        "active_profile.json + PostgreSQL sync, no restart.",
    ], size=13.5)
    rect(s, M, 3.88, LEFT_W, 1.06, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, M + 0.22, 3.99, LEFT_W - 0.44, "IN-BROWSER RETRAINING", WARNING)
    text(s, M + 0.22, 4.26, LEFT_W - 0.44, 0.62,
         "Upload field telemetry from the new pack and retrain XGBoost from the "
         "dashboard — the adaptation loop closes without a developer.",
         size=11.5, color=INK, line=1.24)
    mini_head(s, M, 5.08, LEFT_W, "WHAT WE WOULD BUILD NEXT", MUTED)
    nxt = [("Close the Cell Imbalance gap", CRITICAL),
           ("Lift OOD recall above 24.5%", WARNING),
           ("Move inference onto the Zynq-7000", ACCENT),
           ("Characterise LFP on a real bench", ACCENT),
           ("SOH and remaining useful life from dV/dt", ACCENT)]
    ny = 5.38
    for t, col in nxt:
        b = rect(s, M, ny, 0.06, 0.22, fill=col); b.line.fill.background()
        text(s, M + 0.22, ny - 0.02, LEFT_W - 0.22, 0.26, t, size=11.5, color=INK)
        ny += 0.27
    picture(s, G("diag_configurator.png"), VIS_X, BODY_Y + 0.04, 2.34, 4.34)
    picture(s, G("fig_ocv_soc.png"), VIS_X + 2.52, BODY_Y + 0.42, VIS_W - 2.52, 3.15)
    caption(s, VIS_X + 2.52, BODY_Y + 3.66, VIS_W - 2.52,
            "Why LFP needs a remap, not an offset")
    notes(s, """
The last piece is what makes this reusable. Upload the manufacturer datasheet,
the parser pulls chemistry and every limit, pack sizing derives the series and
parallel counts, and the chemistry gets tiered: NMC is direct reuse, NCA and LCO
share the ceiling so they only shift, LFP needs a genuine remap to 2.50 to 3.65
volts because of that flat OCV curve, and LTO needs everything rescaled. And you
can retrain on your own field telemetry from the browser. What is not finished:
imbalance recall, OOD recall, the Zynq path, a real LFP bench, and state of
health. Thank you — happy to take questions.""")

    prs.save(OUT)
    print("wrote", os.path.relpath(OUT, ROOT), "| 8 slides")
    return OUT
