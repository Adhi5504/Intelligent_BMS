

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
    ("LG Energy Solution INR21700-M50", "NMC tier reference"),
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
