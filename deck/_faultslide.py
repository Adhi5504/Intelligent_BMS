

# ============================================= fault-detection architecture
def fault_flow_slide(prs, n):
    """Full-bleed architecture diagram — the flow the deck has been describing,
    end to end, with the independent hardware-protection lane underneath."""
    s = new_slide(prs, n, "Fault detection, end to end")
    picture(s, os.path.join(GEN, "diag_fault_flow.png"), M, BODY_Y - 0.08,
            SW - 2*M, 4.28)
    cards = [
        ("FIVE STAGES", "Acquire → establish context → detect → score risk → act. "
                        "Every block maps to a module in the repository.", ACCENT),
        ("MODE FIRST", "Context is resolved before detection, because the same "
                       "voltage sag means different things in ACCEL and IDLE.", WARNING),
        ("TWO PATHS", "The ML lane can abstain or be wrong. The hardware lane "
                      "cannot — it runs at the pack, with no software in it.", CRITICAL),
    ]
    cw = (SW - 2*M - 2*0.24) / 3
    for i, (t, d, col) in enumerate(cards):
        cx = M + i * (cw + 0.24)
        rect(s, cx, 5.82, cw, 1.10, fill=PANEL, line=HAIRLINE, lw=0.75)
        b = rect(s, cx, 5.82, cw, 0.055, fill=col); b.line.fill.background()
        text(s, cx + 0.20, 5.96, cw - 0.40, 0.22, t, size=9, color=col, bold=True)
        text(s, cx + 0.20, 6.22, cw - 0.40, 0.64, d, size=9.5, color=INK, line=1.22)
    notes(s, """
This is the whole fault path on one slide. Five stages. Acquisition: the BMS
senses, BLE carries it at one hertz, and we reject any row that is NaN or all
zeros before it reaches the model. Context: we resolve the operating mode first,
because a voltage sag under acceleration is normal and the same sag at idle is a
fault — the mode flags are twelve percent of the model's gain. Detection: the
IsolationForest gate runs before the classifier, so an unfamiliar window is
escalated rather than forced into one of six labels. Risk: the class probability
is multiplied by a physical severity derived from how far past the datasheet
warning limit we are, raised further if the fault persists. Action: corrective
instruction, logged alert, and comparison against the cycle history. And
underneath all of it, the lane that does not depend on any of this — the JBD
protection logic switching the MOSFETs at the pack, and the Arduino watchdog that
resets the Pi. If every line of our software failed, that lane still opens the
contactor.""")
    return s
