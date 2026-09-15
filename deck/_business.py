

# ================================================ business & adoption slide
def business_slide(prs, n):
    """Cost, adoption path, who pays, and the one axis we win on.

    Every rupee figure is a [FILL] placeholder — the team supplies real BOM
    numbers. Competitor capabilities are marked for verification against
    vendor datasheets rather than asserted.
    """
    s = new_slide(prs, n, "What it costs, who pays, and why they switch")

    # ---- BOM of the build that exists today -------------------------------
    mini_head(s, M, BODY_Y + 0.02, LEFT_W, "BOM — THE UNIT WE BUILT")
    bom = [("Raspberry Pi 5 (8 GB) + cooler + PSU", "₹15,000"),
           ("8S2P NMC pack + JBD 8S BMS (NTCs included)", "₹13,000"),
           ("Harness, enclosure", "[FILL: ₹...]")]
    y = BODY_Y + 0.34
    for lab, val in bom:
        text(s, M + 0.04, y, LEFT_W - 1.70, 0.26, lab, size=11.5, color=INK)
        text(s, M + LEFT_W - 1.66, y, 1.62, 0.26, val, size=11.5, color=WARNING,
             bold=True, align=PP_ALIGN.RIGHT)
        ln = rect(s, M, y + 0.29, LEFT_W, 0.008, fill=HAIRLINE)
        ln.line.fill.background()
        y += 0.42
    rect(s, M, y + 0.06, LEFT_W, 0.48, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.04, y + 0.17, LEFT_W - 1.70, 0.26, "Total, one retrofit unit",
         size=11.5, color=INK, bold=True)
    text(s, M + LEFT_W - 1.66, y + 0.17, 1.62, 0.26, "[FILL: ₹...]", size=11.5,
         color=CRITICAL, bold=True, align=PP_ALIGN.RIGHT)

    # ---- two routes to market --------------------------------------------
    mini_head(s, M, 3.94, LEFT_W, "TWO ROUTES IN")
    pw = (LEFT_W - 0.20) / 2
    for i, (t_, d_, col) in enumerate([
        ("RETROFIT", "Pi 5 alongside the BMS already in the pack.\nNo redesign, no recertification.", ACCENT),
        ("OEM INTEGRATION", "Zynq-7000 on the BMS board itself.\nPer-unit cost falls at volume.", WARNING)]):
        px = M + i * (pw + 0.20)
        rect(s, px, 4.24, pw, 1.46, fill=BG, line=col, lw=1.2)
        text(s, px + 0.16, 4.40, pw - 0.32, 0.24, t_, size=9.5, color=col, bold=True)
        text(s, px + 0.16, 4.68, pw - 0.32, 0.88, d_, size=9.5, color=INK, line=1.26)

    # ---- the one axis we win on ------------------------------------------
    mini_head(s, VIS_X, BODY_Y + 0.02, VIS_W, "WHERE WE ARE DIFFERENT")
    headers = ["", "Per-cell\nsensing", "Learned\nfault classes", "Abstains\nwhen unsure",
               "Datasheet\nreconfig"]
    rows = [
        ["Orion BMS",     ("✓", MUTED, False), ("—", MUTED, False), ("—", MUTED, False), ("✓", MUTED, False)],
        ["Nuvation BMS",  ("✓", MUTED, False), ("—", MUTED, False), ("—", MUTED, False), ("✓", MUTED, False)],
        ["JBD-class BMS", ("✓", MUTED, False), ("—", MUTED, False), ("—", MUTED, False), ("—", MUTED, False)],
        ["AI-PBMS",       ("✓", ACCENT, True), ("6 classes", ACCENT, True),
                          ("3 bands", ACCENT, True), ("PDF → profile", ACCENT, True)],
    ]
    end_y = table(s, VIS_X, BODY_Y + 0.30, VIS_W, headers, rows,
                  col_w=[1.55, 0.95, 1.15, 1.10, 1.20],
                  head_h=0.56, row_h=0.46, fs=9.5, hfs=8, highlight=3)
    text(s, VIS_X, end_y + 0.10, VIS_W, 0.40,
         "Competitor rows compiled from public product pages — "
         "[VERIFY against vendor datasheets]",
         size=8.2, color=CRITICAL, line=1.22)

    rect(s, VIS_X, 4.80, VIS_W, 1.10, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, VIS_X + 0.22, 4.90, VIS_W - 0.44, "THE ARGUMENT IN ONE LINE")
    text(s, VIS_X + 0.22, 5.14, VIS_W - 0.44, 0.70,
         "Every product there protects the pack once a threshold breaks. None "
         "tells a technician which cell is failing, how confident that call is, "
         "or adapts to a new chemistry from a PDF.",
         size=11, color=INK, line=1.26)
    mini_head(s, VIS_X, 6.04, VIS_W, "WHO PAYS", CRITICAL)
    text(s, VIS_X, 6.30, VIS_W, 0.56,
         "Fleet operator — avoids an early pack replacement  [FILL: ₹ per pack]\n"
         "OEM — fewer warranty claims per 1,000 packs  [FILL: ₹ or % exposure]",
         size=10.5, color=INK, line=1.40)

    notes(s, """
Cost first. The unit we built is a Raspberry Pi 5 with its cooler and supply at
fifteen thousand rupees, and the 8S2P pack with its JBD BMS — bought together at
thirteen thousand, thermistors included. Add the harness and enclosure and that
is the whole retrofit box: it sits alongside a pack already in service, with no
redesign and no recertification. At volume the same logic moves onto a Zynq on
the BMS board itself and the per-unit cost drops. Who pays: the fleet operator,
because catching one weak cell early avoids replacing an otherwise healthy pack;
and the OEM, because the same signal cuts warranty claims. Now the table on the
right, and I want to be precise about this. Orion, Nuvation and the JBD-class
boards all do per-cell sensing — we are not claiming otherwise. What none of
them does is classify what kind of fault it is, tell you how confident it is, or
let you point it at a different chemistry by uploading a datasheet. They protect
the pack after a threshold breaks. We tell a technician which cell, what is wrong
with it, and how sure we are — and we abstain when we are not sure. That is the
axis we compete on.""")
    return s
