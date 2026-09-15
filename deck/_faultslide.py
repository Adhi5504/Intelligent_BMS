

# ============================================= fault-detection architecture
def fault_flow_slide(prs, n):
    """Full-bleed architecture diagram — the flow the deck has been describing,
    end to end, with the independent hardware-protection lane underneath."""
    s = new_slide(prs, n, "Fault detection, end to end")
    picture(s, os.path.join(GEN, "diag_fault_flow.png"), M, BODY_Y - 0.08,
            SW - 2*M, 4.12)
    cards = [
        ("FIVE STAGES", "Acquire → establish context → detect → score risk → act. "
                        "Every block maps to a module in the repository.", ACCENT),
        ("MODE FIRST", "Context is resolved before detection: the same voltage sag "
                       "means different things in ACCEL and IDLE.", WARNING),
        ("TWO PATHS", "The ML lane can abstain or be wrong. The hardware lane "
                      "cannot — it runs at the pack, with no software in it.", CRITICAL),
        ("KNOWN BIAS", "Trained on one pack with one chronic defect (cell_v1), so "
                       "generalisation is unproven. The datasheet configurator and "
                       "in-browser retraining are the mitigation. Telemetry stays in "
                       "the operator's own instance.", CRITICAL),
    ]
    cw = (SW - 2*M - 3*0.20) / 4
    for i, (t, d, col) in enumerate(cards):
        cx = M + i * (cw + 0.20)
        rect(s, cx, 5.68, cw, 1.25, fill=PANEL, line=HAIRLINE, lw=0.75)
        b = rect(s, cx, 5.68, cw, 0.055, fill=col); b.line.fill.background()
        text(s, cx + 0.16, 5.81, cw - 0.32, 0.22, t, size=8.5, color=col, bold=True)
        text(s, cx + 0.16, 6.06, cw - 0.32, 0.84, d, size=8.4, color=INK, line=1.20)
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
protection logic switching the MOSFETs at the pack. If every line of our
software failed, that lane still opens the
contactor. That lane is the BMS's own protection logic, not something we wrote.
And the honest caveat, bottom right: this model has seen one physical
pack with one chronic defect, so generalisation to other packs is unproven. The
datasheet configurator and the in-browser retraining loop are how an operator
adapts it to their own pack, and their telemetry stays in their own
instance — we never pool it.""")
    return s
