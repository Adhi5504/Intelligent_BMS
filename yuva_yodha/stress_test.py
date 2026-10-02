"""Harsher tests of the main claims, on the real pump (Grundfos NB 65-160/157).

The earlier tests were friendly: the 'true' pump was a scaled copy of the datasheet curve, sensor noise was 1%,
the system curve and static lift were exactly known, and the healthy curve was exact. Here the TRUE plant differs
from what the tool assumes:
  * curve SHAPE differs from the datasheet (head +-3% bowed, power +-3% tilted) on top of scale errors,
  * static lift is wrong by up to +-3 m and system friction by +-10% (the tool assumes 10 m and the nominal curve),
  * sensor noise is 3%,
  * in the drift test, each day also has a random demand mix, voltage/temperature-like power and head offsets.
The tool still uses only datasheet curves + its own calibration. Results are therefore a more honest (still simulated) test.

Usage: python3 stress_test.py cal | decomp | band | sensor | drift
"""
import itertools
import math
import random
import sys

import real_pump_sim as rp

HS_NOM = 10.0
K0 = (rp.H_RATED - HS_NOM) / rp.Q_RATED ** 2
PEAK = 0.80
QS = [f * PEAK * rp.Q_RATED for f in rp.PROFILE]
MARGIN = 0.05
RS_DAY = rp.DAYS * rp.TARIFF


class Curves:
    """Pump curves: datasheet scaled by (ah, ap) plus optional shape distortion."""
    def __init__(self, ah=1.0, ap=1.0, hshape=0.0, pshape=0.0):
        self.ah, self.ap, self.hshape, self.pshape = ah, ap, hshape, pshape

    def h(self, q):
        return self.ah * rp.h_nom(q) * (1 + self.hshape * ((q - 80) / 50) ** 2)

    def p2(self, q):
        return self.ap * rp.p2_nom(q) * (1 + self.pshape * ((q - 85) / 45))


class System:
    def __init__(self, hs=HS_NOM, kf=1.0):
        self.hs, self.kf = hs, kf

    def h(self, q, f=0.0):
        return self.hs + K0 * self.kf * (1 + f) * q * q


NOM = System()


def speed(cv, q, head, w=0.0):
    def g(r):
        qe = q / r
        return -1e9 if qe > rp.Q_MAX_FIT else r * r * (1 - w) * cv.h(qe) - head
    lo, hi = rp.N_MIN, 1.0
    if g(hi) < 0:
        raise ValueError("cannot deliver")
    if g(lo) > 0:
        return lo
    for _ in range(45):
        mid = (lo + hi) / 2
        if g(mid) > 0:
            hi = mid
        else:
            lo = mid
    return hi


def p1(cv, q, throttled, hsys, w=0.0):
    wear = (1 - w) / (1 - 1.5 * w)
    if throttled:
        if (1 - w) * cv.h(q) < hsys - 1e-9:
            raise ValueError("cannot deliver")
        p2 = cv.p2(q) * wear
        return p2 / rp.eta_motor(p2)
    r = speed(cv, q, hsys, w)
    p2 = r ** 3 * cv.p2(q / r) * wear
    return p2 / rp.eta_motor(p2) / rp.ETA_VFD


def true_saving(cv, sy):
    b = sum(p1(cv, q, True, sy.h(q)) for q in QS)
    v = sum(p1(cv, q, False, sy.h(q) * (1 + MARGIN)) for q in QS)
    return 100 * (b - v) / b


# ------------------------------------------------------------------ calibration / learning
Q_GRID = list(range(40, 131, 2))
SH_GRID = [round(0.88 + 0.02 * i, 2) for i in range(10)]
SP_GRID = [round(0.92 + 0.02 * i, 2) for i in range(13)]
_TAB = {}


def table(sh, sp):
    key = (round(sh, 3), round(sp, 3))
    if key not in _TAB:
        cv = Curves(sh, sp)
        _TAB[key] = [(q, cv.h(q), cv.p2(q) / rp.eta_motor(cv.p2(q))) for q in Q_GRID]
    return _TAB[key]


def logs(cv, sy, noise, rng):
    return [(cv.h(q) * (1 + rng.gauss(0, noise)), p1(cv, q, True, sy.h(q)) * (1 + rng.gauss(0, noise))) for q in QS]


def forecast(points, sh, sp):
    cvm = Curves(sh, sp)
    tab = table(sh, sp)
    base = var = 0.0
    for hm, pm in points:
        best, qe = 1e18, tab[0][0]
        for q, h, pw in tab:
            c = ((h - hm) / hm) ** 2 + ((pw - pm) / pm) ** 2
            if c < best:
                best, qe = c, q
        base += pm
        try:
            var += p1(cvm, float(qe), False, NOM.h(qe) * (1 + MARGIN))
        except ValueError:
            return None
    return 100 * (base - var) / base


def day_cost(points):
    out = {}
    for sh in SH_GRID:
        for sp in SP_GRID:
            tab = table(sh, sp)
            tot = 0.0
            for hm, pm in points:
                tot += min(((h - hm) / hm) ** 2 + ((pw - pm) / pm) ** 2 for _, h, pw in tab)
            out[(sh, sp)] = tot
    return out


H0_FIT = rp.h_nom(0.0)
P1_0_FIT = rp.p2_nom(0.0) / rp.eta_motor(rp.p2_nom(0.0))


def anchor(kind, cv, rng, noise):
    if kind == "none":
        return 1.0, 1.0
    sh = cv.h(0.0) * (1 + rng.gauss(0, noise)) / H0_FIT                      # measured closed-valve head
    if kind == "shutoff":
        return sh, 1.0
    p2c = cv.p2(0.0)
    return sh, (p2c / rp.eta_motor(p2c)) * (1 + rng.gauss(0, noise)) / P1_0_FIT


STRESS = [  # (ah, ap, hshape, pshape, static lift, friction factor)
    (1.00, 1.00, 0.03, 0.03, 10, 1.0), (0.97, 1.04, 0.03, -0.03, 7, 1.1), (0.94, 1.08, -0.03, 0.03, 13, 0.9),
    (1.03, 0.97, 0.03, 0.03, 13, 1.1), (0.92, 1.10, -0.03, -0.03, 7, 0.9), (0.95, 1.05, 0.0, 0.0, 10, 1.1)]
BENIGN = [(a, b, 0.0, 0.0, 10, 1.0) for a, b, *_ in STRESS]


def run_cal(plants, noise, trials, seed):
    rng = random.Random(seed)
    res = {k: [] for k in ("none", "shutoff", "shutoff+power", "learned (7 days)")}
    for ah, ap, hs_, ps_, hs, kf in plants:
        cv, sy = Curves(ah, ap, hs_, ps_), System(hs, kf)
        truth = true_saving(cv, sy)
        for _ in range(trials):
            days = [logs(cv, sy, noise, rng) for _ in range(7)]
            ref = days[-1]
            for kind in ("none", "shutoff", "shutoff+power"):
                sh, sp = anchor(kind, cv, rng, noise)
                f = forecast(ref, sh, sp)
                if f is not None:
                    res[kind].append(abs(f - truth))
            costs = [day_cost(d) for d in days]
            tot = {k: sum(c[k] for c in costs) for k in costs[0]}
            best = min(tot, key=tot.get)
            f = forecast(ref, *best)
            if f is not None:
                res["learned (7 days)"].append(abs(f - truth))
    return res


def summarize(res):
    for k, v in res.items():
        v = sorted(v)
        print(f"  {k:20s} mean {sum(v) / len(v):5.1f}   90th pct {v[int(0.9 * len(v))]:5.1f}   worst {v[-1]:5.1f}   (n={len(v)})")


def cmd_cal():
    print("Forecast-saving error (percentage points) for each calibration approach")
    print("\nA. FRIENDLY (1% noise, scaled datasheet curves, exact system curve) - as in earlier tests")
    summarize(run_cal(BENIGN, 0.01, 4, 101))
    print("\nB. STRESS (3% noise, curve-shape error, wrong static lift/friction)")
    summarize(run_cal(STRESS, 0.03, 4, 202))


def est_flows(points, sh, sp):
    tab = table(sh, sp)
    out = []
    for hm, pm in points:
        best, qe = 1e18, tab[0][0]
        for q, h, pw in tab:
            c = ((h - hm) / hm) ** 2 + ((pw - pm) / pm) ** 2
            if c < best:
                best, qe = c, q
        out.append(float(qe))
    return out


def fit_system(qe, hsys_meas):
    """Least-squares hs + c*q^2 from process-side pressure vs estimated flow -> System(hs, kf)."""
    x = [q * q for q in qe]
    n = len(x)
    mx, my = sum(x) / n, sum(hsys_meas) / n
    sxx = sum((a - mx) ** 2 for a in x)
    slope = sum((a - mx) * (b - my) for a, b in zip(x, hsys_meas)) / sxx
    hs = my - slope * mx
    return System(min(max(hs, 0.0), 25.0), min(max(slope / K0, 0.5), 1.8))


def forecast_sys(points, sh, sp, sysm):
    cvm = Curves(sh, sp)
    qe = est_flows(points, sh, sp)
    base = sum(pm for _, pm in points)
    var = 0.0
    for q in qe:
        try:
            var += p1(cvm, q, False, sysm.h(q) * (1 + MARGIN))
        except ValueError:
            return None
    return 100 * (base - var) / base


def run_sysfit(plants, noise, trials, seed):
    rng = random.Random(seed)
    res = {"learned, system assumed (10 m, nominal friction)": [], "learned + process-side pressure sensor (system fitted)": []}
    for ah, ap, hs_, ps_, hs, kf in plants:
        cv, sy = Curves(ah, ap, hs_, ps_), System(hs, kf)
        truth = true_saving(cv, sy)
        for _ in range(trials):
            days = [logs(cv, sy, noise, rng) for _ in range(7)]
            costs = [day_cost(d) for d in days]
            tot = {k: sum(c[k] for c in costs) for k in costs[0]}
            best = min(tot, key=tot.get)
            f1 = forecast_sys(days[-1], *best, NOM)
            # process-side pressure measured on the last 3 days (true flow -> system head, with sensor noise)
            qe_all, hm_all = [], []
            for d in days[-3:]:
                qe_all += est_flows(d, *best)
                hm_all += [sy.h(q) * (1 + rng.gauss(0, noise)) for q in QS]
            f2 = forecast_sys(days[-1], *best, fit_system(qe_all, hm_all))
            if f1 is not None:
                res["learned, system assumed (10 m, nominal friction)"].append(abs(f1 - truth))
            if f2 is not None:
                res["learned + process-side pressure sensor (system fitted)"].append(abs(f2 - truth))
    return res


def cmd_sysfit():
    print("Does measuring the system curve (process-side pressure) fix the dominant error? Forecast error, percentage points")
    shape = [(a, b, hs_, ps_, 10, 1.0) for a, b, hs_, ps_, _, _ in STRESS]
    sysonly = [(a, b, 0.0, 0.0, hs, kf) for a, b, _, _, hs, kf in STRESS]
    for name, plants, noise in (("wrong static lift / friction only (1% noise)", sysonly, 0.01),
                                ("FULL STRESS (3% noise, shape error, wrong lift/friction)", STRESS, 0.03)):
        print(f"\n{name}")
        summarize(run_sysfit(plants, noise, 4, 404))


def cmd_decomp():
    """Which stress factor causes the degradation? One factor at a time."""
    shape = [(a, b, hs_, ps_, 10, 1.0) for a, b, hs_, ps_, _, _ in STRESS]
    sysonly = [(a, b, 0.0, 0.0, hs, kf) for a, b, _, _, hs, kf in STRESS]
    for name, plants, noise in (("noise 3% only", BENIGN, 0.03), ("curve-shape error only (1% noise)", shape, 0.01),
                                ("wrong static lift / friction only (1% noise)", sysonly, 0.01)):
        print(f"\n{name}")
        summarize(run_cal(plants, noise, 4, 303))


def cmd_band():
    """Calibrate the uncertainty-band width on one set of runs, test coverage on separate runs.
    Uses the recommended method (learned calibration + system curve fitted from a process-side pressure sensor)."""
    noise, thresh0 = 0.03, 6 * 0.03 ** 2
    mults = (1, 10, 100, 1000)

    def collect(seed):
        rng = random.Random(seed)
        rows = []
        for ah, ap, hs_, ps_, hs, kf in STRESS:
            cv, sy = Curves(ah, ap, hs_, ps_), System(hs, kf)
            truth = true_saving(cv, sy)
            for _ in range(3):
                days = [logs(cv, sy, noise, rng) for _ in range(7)]
                costs = [day_cost(d) for d in days]
                tot = {k: sum(c[k] for c in costs) for k in costs[0]}
                cmin = min(tot.values())
                best = min(tot, key=tot.get)
                qe_all, hm_all = [], []                      # recommended method: process-side pressure fits the system curve
                for d in days[-3:]:
                    qe_all += est_flows(d, *best)
                    hm_all += [sy.h(q) * (1 + rng.gauss(0, noise)) for q in QS]
                sysm = fit_system(qe_all, hm_all)
                est = forecast_sys(days[-1], *best, sysm)
                bands = {}
                for m in mults:
                    vals = [forecast_sys(days[-1], *k, sysm) for k, v in tot.items() if v <= cmin + m * thresh0]
                    vals = [v for v in vals if v is not None]
                    bands[m] = (min(vals), max(vals))
                if est is not None:
                    rows.append((truth, est, bands))
        return rows

    cal, test = collect(31), collect(32)

    def cover(rows, m):
        ok = sum(1 for t, e, b in rows if b[m][0] - 0.5 <= t <= b[m][1] + 0.5)
        w = sum(b[m][1] - b[m][0] for _, _, b in rows) / len(rows)
        return 100 * ok / len(rows), w

    print("Model-based band: widen the likelihood threshold by a factor, check how often the band holds the truth")
    print(f"{'factor':>8s}{'cover (calib runs)':>20s}{'cover (test runs)':>19s}{'mean width, pts':>17s}")
    for m in mults:
        c1, _ = cover(cal, m)
        c2, w2 = cover(test, m)
        print(f"{m:8d}{c1:19.0f}%{c2:18.0f}%{w2:17.1f}")
    print("\nSimple alternative: point forecast +- a fixed margin")
    for pm in (2, 3, 4, 5, 6):
        c1 = 100 * sum(1 for t, e, b in cal if abs(t - e) <= pm) / len(cal)
        c2 = 100 * sum(1 for t, e, b in test if abs(t - e) <= pm) / len(test)
        print(f"  +-{pm} points: holds the truth in {c1:.0f}% (calib) / {c2:.0f}% (test) of runs")


# ------------------------------------------------------------------ sensor value
def shapley(cv, sy, qs, w, f):
    def v(s):
        return sum(p1(cv, q, "throttle" in s, sy.h(q, f if "foul" in s else 0.0), w if "wear" in s else 0.0) for q in qs)
    contrib = dict.fromkeys(("throttle", "wear", "foul"), 0.0)
    perms = list(itertools.permutations(contrib))
    for perm in perms:
        cur = set()
        for p in perm:
            contrib[p] += v(cur | {p}) - v(cur)
            cur.add(p)
    return {p: c / len(perms) for p, c in contrib.items()}


W_GRID = [i / 100 for i in range(21)]
Q1 = list(range(40, 131))
DS = Curves()
_MT = {}


def model_tab():
    if not _MT:
        for q in Q1:
            for w in W_GRID:
                p2 = DS.p2(q) * (1 - w) / (1 - 1.5 * w)
                _MT[(q, w)] = ((1 - w) * DS.h(q), p2 / rp.eta_motor(p2))
    return _MT


def est_flow_wear(hms_pms):
    tab = model_tab()
    qe, we = [], []
    for hm, pm in hms_pms:
        best, arg = 1e18, (80.0, 0.0)
        for (q, w), (h, pw) in tab.items():
            c = ((h - hm) / hm) ** 2 + ((pw - pm) / pm) ** 2
            if c < best:
                best, arg = c, (float(q), w)
        qe.append(arg[0])
        we.append(arg[1])
    return qe, we


def shapley_feasible(cv, sy, qs, w, f):
    """Shapley split summed over the hours whose estimated duty is physically feasible in all 8 states."""
    tot = dict.fromkeys(("throttle", "wear", "foul"), 0.0)
    used = 0
    for q in qs:
        try:
            part = shapley(cv, sy, [q], w, f)
        except ValueError:
            continue
        for k in tot:
            tot[k] += part[k]
        used += 1
    return (tot, used) if used else (None, 0)


def cmd_sensor(noise=0.03, days=6, seed=7):
    rng = random.Random(seed)
    print("Real pump, STRESS plant (3% noise, curve-shape error, wrong lift/friction). Rs/year attributed to the wrong cause.")
    print("(shares compared on hours whose estimated duty is feasible; error in Rs = misplaced share x true total waste)")
    print(f"{'wear/foul':>10s}{'waste % of baseline kWh':>25s}{'valve share %':>15s}{'flow err %':>12s}{'S0 wrong':>10s}{'S1 wrong':>10s}{'S2 wrong':>10s}")
    plant = (0.97, 1.04, 0.03, 0.03, 13, 1.1)
    cv, sy = Curves(*plant[:4]), System(plant[4], plant[5])
    for w, f in [(0.05, 0.20), (0.10, 0.10), (0.00, 0.30), (0.08, 0.00), (0.03, 0.25)]:
        try:
            truth = shapley(cv, sy, QS, w, f)
        except ValueError:
            print(f"{w:4.2f}/{f:4.2f}  plant cannot deliver the duty (skipped)")
            continue
        tot = sum(truth.values())
        share_t = {k: v / tot for k, v in truth.items()}
        base = sum(p1(cv, q, True, sy.h(q, f), w) for q in QS)
        errs = {"S0": [], "S1": [], "S2": []}
        flow_err = []
        for _ in range(days):
            hp = [(cv.h(q) * (1 - w) * (1 + rng.gauss(0, noise)), p1(cv, q, True, sy.h(q, f), w) * (1 + rng.gauss(0, noise))) for q in QS]
            qe, we = est_flow_wear(hp)
            flow_err += [abs(a - b) / b for a, b in zip(qe, QS)]
            w_e = sorted(we)[len(we) // 2]
            fs2 = sorted(((sy.h(q, f) * (1 + rng.gauss(0, noise))) - HS_NOM) / (K0 * qq * qq) - 1 for q, qq in zip(QS, qe))
            for name, f_e in (("S0", 0.0), ("S1", max(0.0, f * (1 + rng.gauss(0, 0.15)))), ("S2", max(0.0, fs2[len(fs2) // 2]))):
                est, used = shapley_feasible(DS, NOM, qe, w_e, f_e)
                if est is None or sum(est.values()) <= 0:
                    continue
                st_ = sum(est.values())
                errs[name].append(0.5 * sum(abs(est[k] / st_ - share_t[k]) for k in est) * tot * RS_DAY)
        m = {k: (sum(v) / len(v) if v else float("nan")) for k, v in errs.items()}
        print(f"{w:4.2f}/{f:4.2f}{100 * tot / base:24.0f}%{100 * share_t['throttle']:15.0f}{100 * sum(flow_err) / len(flow_err):12.0f}"
              f"{m['S0']:10,.0f}{m['S1']:10,.0f}{m['S2']:10,.0f}")
    print("\nThe valve share is measured against an ideal speed-matched, healthy, clean pump: it is the part a speed-matched drive")
    print("(or a trimmed impeller) removes, not a general fact about all pumps.")


# ------------------------------------------------------------------ drift detection
def cusum(series, base_n=14, k=0.5, h=5.0):
    base = series[:base_n]
    mu = sum(base) / base_n
    sd = max((sum((x - mu) ** 2 for x in base) / (base_n - 1)) ** 0.5, 0.004)
    s = 0.0
    for i, x in enumerate(series):
        if i < base_n:
            continue
        s = max(0.0, s + (x - mu - k * sd))
        if s > h * sd:
            return i
    return None


def daily_w(w, cv, sy, f, rng, noise=0.03):
    u = rng.uniform(0.95, 1.05)                      # day-to-day demand mix
    sp_, sh_ = rng.gauss(1, 0.01), rng.gauss(1, 0.005)   # voltage/temperature-like offsets
    hp = []
    for q in QS:
        qq = min(max(q * u, 41), 129)
        hp.append((cv.h(qq) * (1 - w) * sh_ * (1 + rng.gauss(0, noise)), p1(cv, qq, True, sy.h(qq, f), w) * sp_ * (1 + rng.gauss(0, noise))))
    _, we = est_flow_wear(hp)
    return sorted(we)[len(we) // 2]


def cmd_drift(seed=9):
    rng = random.Random(seed)
    cv, sy, f = Curves(0.97, 1.04, 0.03, 0.03), System(10, 1.05), 0.05   # a feasible stressed plant even at 10% wear
    scen = {
        "control: no wear, 365 days": ([0.0] * 365, 3),
        "slow wear: 0 -> 10% over 180 days": ([0.10 * min(d, 180) / 180 for d in range(240)], 4),
        "fast wear: 0 -> 10% over 60 days": ([0.10 * min(d, 60) / 60 for d in range(120)], 4),
        "step: 6% from day 60": ([0.0 if d < 60 else 0.06 for d in range(120)], 4),
    }
    print("Wear drift detection under STRESS (3% noise, curve/system mismatch, daily demand mix and offsets)")
    for name, (ws, runs) in scen.items():
        alarms, wear_at = [], []
        for _ in range(runs):
            series = [daily_w(w, cv, sy, f, rng) for w in ws]
            a = cusum(series)
            alarms.append(a)
            if a is not None:
                wear_at.append(ws[a])
        hits = [x for x in alarms if x is not None]
        if name.startswith("control"):
            print(f"  {name}: {len(hits)} false alarms in {runs} x 365 days")
        elif hits:
            print(f"  {name}: alarm in {len(hits)}/{runs} runs, median day {sorted(hits)[len(hits) // 2]}, wear at alarm about {100 * sorted(wear_at)[len(wear_at) // 2]:.1f}%")
        else:
            print(f"  {name}: no alarm in {runs} runs")


if __name__ == "__main__":
    {"cal": cmd_cal, "decomp": cmd_decomp, "sysfit": cmd_sysfit, "band": cmd_band, "sensor": cmd_sensor, "drift": cmd_drift}[sys.argv[1]]()
