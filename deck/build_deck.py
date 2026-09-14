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


# ============================================================ the eight slides
def build():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)

    G = lambda n: os.path.join(GEN, n)
    E = lambda n: os.path.join(EXT, n)

    # ---------------------------------------------------------------- 1
    s = new_slide(prs, 1, "We could not buy this dataset, so we built it",
                  eyebrow="AI-PBMS — AI-Powered Predictive Battery Management System  ·  Team ANS_4X")
    bullets(s, M, BODY_Y + 0.30, LEFT_W, 3.30, [
        "Public BMS datasets hide per-cell voltages behind pack totals.",
        "Imbalance and weak-cell faults are invisible at pack level.",
        "So we instrumented a physical 8S2P NMC pack end to end.",
        "Programmable DC supply charges; electronic load drives discharge profiles.",
        "Every row the model ever sees came from this rig.",
    ], size=16.5)
    stat_strip(s, M, 5.34, LEFT_W, [
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
individual cells. So we built the dataset. An 8S2P NMC pack, a JBD BMS on all eight
taps, a programmable supply charging and an electronic load discharging. Around fifty
cycles, three hours each, over a hundred hours logged, roughly 155,000 rows. Every
number in this deck came off that bench.""")

    # ---------------------------------------------------------------- 2
    s = new_slide(prs, 2, "Pack topology and the model behind it")
    bullets(s, M, BODY_Y + 0.04, LEFT_W, 2.62, [
        "8S sets the 33.6 V nominal bus the drivetrain expects.",
        "2P buys 8 Ah capacity and the current headroom.",
        "Eight per-cell taps make imbalance observable rather than inferred.",
        "1RC caught the instant drop but missed slow recovery.",
    ], size=16.5)
    text(s, M, 4.44, LEFT_W, 0.28, "2RC PARAMETERS — FITTED ON THE 0–4000 s HPPC SEGMENT",
         size=10, color=MUTED, bold=True)
    stat_strip(s, M, 4.78, LEFT_W, [
        ("R₀ 0.06142 Ω", "ohmic drop", ACCENT),
        ("R₁ 0.00820 Ω", "fast branch", ACCENT),
        ("C₁ 22.268 F", "τ₁ ≈ 0.18 s", MUTED),
    ])
    stat_strip(s, M, 5.76, LEFT_W, [
        ("R₂ 0.00882 Ω", "slow branch", ACCENT),
        ("C₂ 119.37 F", "τ₂ ≈ 1.05 s", MUTED),
        ("2RC", "Vt = OCV − IR₀ − V₁ − V₂", INK),
    ])
    picture(s, G("diag_pack_8s2p.png"), VIS_X, BODY_Y - 0.02, VIS_W, 2.42)
    picture(s, G("diag_2rc_ecm.png"),  VIS_X, BODY_Y + 2.46, VIS_W, 2.50)
    notes(s, """
Eight in series gives the 33.6-volt bus the drivetrain wants. Two in parallel
gives 8 amp-hours and the current headroom to run realistic profiles. Eight series
groups means eight sense taps, so imbalance is measured, not inferred. On modelling,
one RC branch caught the instant ohmic drop but missed the slow recovery after a load
step. A second branch fixed it — fast at about 0.18 seconds, slow at about 1.05.
These five parameters were fitted on a clean HPPC segment.""")

    # ---------------------------------------------------------------- 3
    s = new_slide(prs, 3, "From BLE frames to labelled rows")
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
silently truncated — we now reassemble before parsing. And the four thermistors were
read at the wrong byte offset, scrambling the thermal channels. The bigger finding
was in the data: cell one sat a quarter-volt below median every cycle, which labelled
over seventy percent of rows Cell Imbalance. We balanced with physics-informed
synthetic faults rather than throwing real rows away.""")

    # ---------------------------------------------------------------- 4
    s = new_slide(prs, 4, "Why XGBoost, and not the obvious alternatives")
    headers = ["Model", "Accuracy", "Latency", "Size", "Edge", "Interpretable", "Verdict"]
    rows = [
        ["XGBoost", ("98.55%", ACCENT, True), ("0.85 ms", ACCENT, True), "~1.4 MB",
         ("Yes", ACCENT, True), ("Yes", ACCENT, True), ("Deployed", ACCENT, True)],
        ["Transformer", ("—", MUTED, False), ("—", MUTED, False), "~1.6 MB",
         ("Marginal", WARNING, False), ("No", CRITICAL, False), "Needs sequence buffer"],
        ["LSTM", ("—", MUTED, False), ("—", MUTED, False), ("—", MUTED, False),
         ("Marginal", WARNING, False), ("No", CRITICAL, False), "Sequential, hard to batch"],
        ["Random Forest", ("—", MUTED, False), ("—", MUTED, False), ("—", MUTED, False),
         ("Yes", ACCENT, False), ("Yes", ACCENT, False), "Larger for same accuracy"],
        ["SVM", ("—", MUTED, False), ("—", MUTED, False), ("—", MUTED, False),
         ("Yes", ACCENT, False), ("Partly", WARNING, False), "Poor on 50-feature tabular"],
        ["Rule-based BMS", ("—", MUTED, False), ("—", MUTED, False), "trivial",
         ("Yes", ACCENT, False), ("Yes", ACCENT, False), ("Reacts, never predicts", CRITICAL, False)],
    ]
    end_y = table(s, M, BODY_Y + 0.06, SW - 2*M, headers, rows,
                  col_w=[1.55, 1.00, 1.00, 0.85, 0.85, 1.20, 2.25],
                  head_h=0.44, row_h=0.50, fs=11.5, hfs=10.5)
    text(s, M, end_y + 0.30, 6.10, 0.34,
         "WHAT DECIDED IT", size=10, color=ACCENT, bold=True)
    text(s, M, end_y + 0.62, 6.10, 0.90,
         "Fifty engineered tabular features, a hard latency budget on the Pi and a "
         "reviewer who has to be able to ask why — gradient-boosted trees win all "
         "three. “—” means not measured here: we instrumented the model we shipped.",
         size=11.5, color=MUTED, line=1.28)
    picture(s, G("fig_model_performance.png"), M + 6.45, end_y + 0.16,
            SW - M - (M + 6.45), 1.52)
    notes(s, """
Tabular sensor data with fifty engineered features is what gradient-boosted
trees are good at, and each alternative fails a constraint we actually have. The
Transformer and the LSTM need a sequence buffer — latency and memory we do not have
— and neither gives an attribution an engineer can argue with. Random Forest needs a
much bigger model for the same accuracy. A rule-based BMS only reacts after a
threshold is already breached. XGBoost: 98.55 percent, 0.85 milliseconds on the Pi 5,
and inspectable.""")

    # ---------------------------------------------------------------- 5
    s = new_slide(prs, 5, "Three tiers, no single point of failure")
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
         "freeing the CPU for the dashboard and the BLE link.",
         size=13, color=INK, line=1.22)
    picture(s, G("diag_hardware.png"), VIS_X, BODY_Y + 0.02, VIS_W, 3.05)
    hy = BODY_Y + 3.20
    picture(s, E("p06_img1_x51.jpeg"), VIS_X, hy, VIS_W/2 - 0.10, 1.55, card=True)
    picture(s, E("p06_img2_x52.jpeg"), VIS_X + VIS_W/2 + 0.10, hy, VIS_W/2 - 0.10, 1.55, card=True)
    caption(s, VIS_X, hy + 1.58, VIS_W/2 - 0.10, "Raspberry Pi 5")
    caption(s, VIS_X + VIS_W/2 + 0.10, hy + 1.58, VIS_W/2 - 0.10, "Arduino Uno R4 WiFi")
    notes(s, """
Three tiers, each doing what the others cannot. The JBD BMS senses: eight taps,
four thermistors, pack voltage and current. The Pi 5 runs the logger, the inference
and the dashboard. Inference sits at the edge deliberately — push it to a server and
every network hiccup becomes an unmonitored window. The third tier exists because
general-purpose computers hang. An Arduino on its own rail watches for a heartbeat
and pulls the Pi's RUN pin if it stops. Zynq-7000 is our path to take inference off
the CPU entirely.""")

    # ---------------------------------------------------------------- 6
    s = new_slide(prs, 6, "The dashboard an operator actually reads")
    bullets(s, M, BODY_Y + 0.10, LEFT_W, 3.10, [
        "Flask on the Pi, exposed over a Cloudflare tunnel.",
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
Flask on the Pi, published through a Cloudflare tunnel so a reviewer can open it
without us opening a port. It is operator-facing, not engineer-facing: live per-cell
voltages, pack current with direction, four thermal zones, and a charge or discharge
ETA smoothed with an EMA so it does not jitter. The piece worth noting is driving
context. Four modes from the change in current magnitude between samples — because a
voltage sag under hard acceleration is normal, and the same sag at idle is a fault.
Thresholds follow the mode.""")

    # ---------------------------------------------------------------- 7
    s = new_slide(prs, 7, "Six classes, and the confidence to say “I don't know”")
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
abstain outright — nothing is raised and the sample goes for review. Between 0.50 and
0.85 we log a warning that does not block the operator. Only above 0.85 do we raise
an alert with a corrective action. In a safety-critical system a confidently wrong
prediction is worse than none: an abstention sends someone to look, a false alert
teaches them to ignore the dashboard.""")

    # ---------------------------------------------------------------- 8
    s = new_slide(prs, 8, "Swap the chemistry, not the codebase")
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
    lw_, rw_ = 2.42, VIS_W - 2.42 - 0.20
    picture(s, G("diag_configurator.png"), VIS_X, BODY_Y + 0.06, lw_, 4.46)
    picture(s, G("fig_ocv_soc.png"), VIS_X + lw_ + 0.20, BODY_Y + 0.22, rw_, 3.92)
    caption(s, VIS_X + lw_ + 0.20, BODY_Y + 4.24, rw_,
            "Why LFP needs a remap, not a constant offset")
    notes(s, """
This is what makes it reusable. Upload the datasheet for whatever cell you are
running; the parser pulls chemistry, voltages, capacity, current and thermal limits,
and derives series and parallel counts. Then it tiers the chemistry: NMC is direct
reuse, NCA and LCO share the 4.2-volt ceiling so they only shift, LFP needs a real
remap to 2.50–3.65 volts, and LTO at 2.4 nominal needs everything rescaled. The chart
shows why — our measured NMC curve moves about 13 millivolts per percent SOC, so
voltage tracks charge. On LFP's plateau it does not, and no offset fixes that.""")

    prs.save(OUT)
    print("wrote", os.path.relpath(OUT, ROOT))
    return OUT


if __name__ == "__main__":
    build()
