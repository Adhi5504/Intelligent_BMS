

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
    bom = [("Raspberry Pi 5 (8 GB) + cooler", "[FILL: ₹...]"),
           ("Arduino Uno R4 WiFi watchdog", "[FILL: ₹...]"),
           ("JBD SP24S007 BMS, 8S", "[FILL: ₹...]"),
           ("16 × LG INR21700-M50 cells", "[FILL: ₹...]"),
           ("Harness, NTCs, enclosure", "[FILL: ₹...]")]
    y = BODY_Y + 0.32
    for lab, val in bom:
        text(s, M + 0.04, y, LEFT_W - 1.70, 0.24, lab, size=11, color=INK)
        text(s, M + LEFT_W - 1.66, y, 1.62, 0.24, val, size=11, color=WARNING,
             bold=True, align=PP_ALIGN.RIGHT)
        ln = rect(s, M, y + 0.26, LEFT_W, 0.008, fill=HAIRLINE)
        ln.line.fill.background()
        y += 0.34
    rect(s, M, y + 0.02, LEFT_W, 0.40, fill=PANEL, line=HAIRLINE, lw=0.75)
    text(s, M + 0.04, y + 0.09, LEFT_W - 1.70, 0.26, "Total, one retrofit unit",
         size=11, color=INK, bold=True)
    text(s, M + LEFT_W - 1.66, y + 0.09, 1.62, 0.26, "[FILL: ₹...]", size=11,
         color=CRITICAL, bold=True, align=PP_ALIGN.RIGHT)

    # ---- two routes to market --------------------------------------------
    mini_head(s, M, 4.34, LEFT_W, "TWO ROUTES IN")
    pw = (LEFT_W - 0.20) / 2
    for i, (t_, d_, col) in enumerate([
        ("RETROFIT", "Pi 5 alongside the BMS already in the pack.\nNo redesign, no recertification.", ACCENT),
        ("OEM INTEGRATION", "Zynq-7000 on the BMS board itself.\nPer-unit cost falls at volume.", WARNING)]):
        px = M + i * (pw + 0.20)
        rect(s, px, 4.62, pw, 1.02, fill=BG, line=col, lw=1.2)
        text(s, px + 0.16, 4.72, pw - 0.32, 0.24, t_, size=9.5, color=col, bold=True)
        text(s, px + 0.16, 4.98, pw - 0.32, 0.60, d_, size=9.5, color=INK, line=1.22)

    mini_head(s, M, 5.82, LEFT_W, "WHO PAYS", CRITICAL)
    text(s, M, 6.10, LEFT_W, 0.62,
         "Fleet operator — avoids an early pack replacement  [FILL: ₹ per pack]\n"
         "OEM — fewer warranty claims per 1,000 packs  [FILL: ₹ or % exposure]",
         size=10.5, color=INK, line=1.40)

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
    end_y = table(s, VIS_X, BODY_Y + 0.32, VIS_W, headers, rows,
                  col_w=[1.55, 0.95, 1.15, 1.10, 1.20],
                  head_h=0.62, row_h=0.50, fs=9.5, hfs=8, highlight=3)
    text(s, VIS_X, end_y + 0.14, VIS_W, 0.44,
         "Competitor rows compiled from public product pages — "
         "[VERIFY against vendor datasheets]",
         size=8.5, color=CRITICAL, line=1.24)

    rect(s, VIS_X, 4.62, VIS_W, 2.10, fill=PANEL, line=HAIRLINE, lw=0.75)
    mini_head(s, VIS_X + 0.22, 4.74, VIS_W - 0.44, "THE ARGUMENT IN ONE LINE")
    text(s, VIS_X + 0.22, 5.02, VIS_W - 0.44, 1.58,
         "Every product in that table protects the pack once a threshold breaks. "
         "None of them tells a technician which cell is failing, how confident "
         "that call is, or adapts to a different chemistry from a PDF. That is "
         "the whole product.",
         size=11.5, color=INK, line=1.28)

    notes(s, """
Cost first. The unit we built is a Raspberry Pi, an Arduino, a JBD BMS and the
cells — a retrofit box that sits alongside a pack already in service, with no
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
