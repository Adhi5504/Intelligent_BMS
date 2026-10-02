"""Flow-free calibration test on the real pump (Grundfos NB 65-160/157).

Question: the audit pump rarely matches its datasheet curve (age, tolerance, wear). Which cheap anchor
keeps the pre-retrofit saving forecast accurate: nothing, the shut-off head, shut-off head + closed-valve
power, a good flow reading (+-5%), or an unreliable flow reading (+-30%, like a bad ultrasonic meter)?

Simulated 'true' pump = manufacturer curve scaled by (a_h on head, a_p on shaft power).
The tool only knows the manufacturer curve. It logs hourly power + discharge head at fixed speed (1% noise),
estimates flow with the (possibly calibrated) model, and forecasts the saving from speed matching with a
5% head margin. Error = |forecast saving - true saving| in percentage points, mean over simulated days.

IMPORTANT: true shut-off head is NOT in the manufacturer data. Here the shut-off value used by the test is the
cubic FIT extrapolated to Q = 0 (a label, not data). Closed-valve power is assumed to scale like part-load power
(optimistic). Static lift and system curve are assumed known. One pump, simulated.
"""
import random

import real_pump_sim as rp

HS = 10.0
K0 = (rp.H_RATED - HS) / rp.Q_RATED ** 2
PEAK = 0.80
QS = [f * PEAK * rp.Q_RATED for f in rp.PROFILE]
MARGIN = 0.05
Q_GRID = list(range(40, 131))
H0_FIT = rp.h_nom(0.0)                    # extrapolated fit at Q = 0 (NOT data)
P1_0_FIT = rp.p2_nom(0.0) / rp.eta_motor(rp.p2_nom(0.0))


def p1_fixed(q, ah, ap):
    p2 = ap * rp.p2_nom(q)
    return p2 / rp.eta_motor(p2)


def speed(q, ah, head):
    def g(r):
        qe = q / r
        return -1e9 if qe > rp.Q_MAX_FIT else r * r * ah * rp.h_nom(qe) - head
    lo, hi = rp.N_MIN, 1.0
    if g(hi) < 0:
        raise ValueError("cannot deliver")
    if g(lo) > 0:
        return lo
    for _ in range(50):
        mid = (lo + hi) / 2
        if g(mid) > 0:
            hi = mid
        else:
            lo = mid
    return hi


def p1_var(q, ah, ap):
    head = (HS + K0 * q * q) * (1 + MARGIN)
    r = speed(q, ah, head)
    p2 = ap * r ** 3 * rp.p2_nom(q / r)
    return p2 / rp.eta_motor(p2) / rp.ETA_VFD


def true_saving(ah, ap):
    b = sum(p1_fixed(q, ah, ap) for q in QS)
    v = sum(p1_var(q, ah, ap) for q in QS)
    return 100 * (b - v) / b


def anchor_scales(kind, ah, ap, rng, noise=0.01):
    """Return (s_h, s_p): the model's head and power scale learned from the anchor."""
    if kind == "none":
        return 1.0, 1.0
    if kind == "shutoff":
        return ah * H0_FIT * (1 + rng.gauss(0, noise)) / H0_FIT, 1.0
    if kind == "shutoff+power":
        sh = ah * H0_FIT * (1 + rng.gauss(0, noise)) / H0_FIT
        sp = ap * P1_0_FIT * (1 + rng.gauss(0, noise)) / P1_0_FIT
        return sh, sp
    # flow anchor at q_c = 90: measured head and power are true, the assumed flow is off by err
    err = {"flow+-5%": 0.05, "flow+-30%": 0.30}[kind] * rng.choice([-1, 1])
    qc = 90.0
    qa = qc * (1 + err)
    hm = ah * rp.h_nom(qc) * (1 + rng.gauss(0, noise))
    pm = p1_fixed(qc, ah, ap) * (1 + rng.gauss(0, noise))
    return hm / rp.h_nom(qa), pm / p1_fixed(qa, 1.0, 1.0)


def forecast_error(ah, ap, kind, noise=0.01, days=30, seed=5):
    rng = random.Random(seed)
    truth = true_saving(ah, ap)
    errs = []
    for _ in range(days):
        sh, sp = anchor_scales(kind, ah, ap, rng)
        meas_base, est_var = 0.0, 0.0
        try:
            for q in QS:
                hm = ah * rp.h_nom(q) * (1 + rng.gauss(0, noise))
                pm = p1_fixed(q, ah, ap) * (1 + rng.gauss(0, noise))
                best, qe = 1e18, q
                for qi in Q_GRID:
                    c = ((sh * rp.h_nom(qi) - hm) / hm) ** 2 + ((p1_fixed(qi, 1.0, sp) - pm) / pm) ** 2
                    if c < best:
                        best, qe = c, float(qi)
                meas_base += pm
                est_var += p1_var(qe, sh, sp)
        except ValueError:
            continue
        errs.append(abs(100 * (meas_base - est_var) / meas_base - truth))
    return truth, (sum(errs) / len(errs) if errs else float("nan"))


if __name__ == "__main__":
    print(f"Real pump NB 65-160/157, peak demand 80% of rated, 10 m lift, 5% margin, 1% noise, 30 simulated days per cell")
    print(f"Shut-off head used = cubic FIT at Q=0: {H0_FIT:.2f} m  (table: 33.26 m at 0.5 m3/h; true shut-off not given)\n")
    kinds = ["none", "shutoff", "shutoff+power", "flow+-5%", "flow+-30%"]
    print("Mean forecast error, percentage points of saving (lower is better)")
    print(f"{'true pump vs datasheet':28s}{'true saving':>12s}" + "".join(f"{k:>15s}" for k in kinds))
    totals = {k: [] for k in kinds}
    for ah, ap in [(1.00, 1.00), (0.97, 1.04), (0.94, 1.08), (1.03, 0.97), (0.92, 1.10)]:
        row, tsave = [], None
        for k in kinds:
            tsave, e = forecast_error(ah, ap, k)
            row.append(e)
            totals[k].append(e)
        label = f"head x{ah:.2f}, power x{ap:.2f}"
        print(f"{label:28s}{tsave:11.1f}%" + "".join(f"{e:15.1f}" for e in row))
    print(f"{'average':28s}{'':>12s}" + "".join(f"{sum(totals[k]) / len(totals[k]):15.1f}" for k in kinds))
