"""Learning layer on the real pump (Grundfos NB 65-160/157): statistical learning on top of the physics model.

A. Learn the pump's deviation from the datasheet from the logs alone (no flow meter, no shut-off test).
   Unknown: head scale s_h and power scale s_p (and the hourly flows). Method: for each (s_h, s_p) on a grid,
   explain every logged (head, power) pair with the best flow; the cost surface gives the best scales AND an
   uncertainty band (all scales within a chi-square-style threshold). The saving forecast is then reported as
   a range. We test: does the error shrink with more days of logs, and does the band contain the truth?

B. Wear drift detection: a CUSUM test on the daily wear estimate, tuned on the first 14 days, with a
   no-wear control run to count false alarms. We report the detection delay and the wear level at alarm.

Simulated, one pump, 1% sensor noise, system curve and static lift assumed known. Learning here is classical
statistics (profile-likelihood fitting, CUSUM), not a trained neural model. Not a field result.
"""
import random

import calibration_test as ct
import real_pump_sim as rp
import sensor_value as sv

QS = ct.QS
Q_GRID = list(range(40, 131, 2))
SH_GRID = [0.88 + 0.02 * i for i in range(10)]          # head scale 0.88 .. 1.06
SP_GRID = [0.92 + 0.02 * i for i in range(13)]          # power scale 0.92 .. 1.16
H_TAB = {q: rp.h_nom(q) for q in Q_GRID}
P1_TAB = {sp: {q: ct.p1_fixed(q, 1.0, sp) for q in Q_GRID} for sp in SP_GRID}
SIGMA = 0.01
THRESH = 6 * SIGMA ** 2                                  # ~95% region for two parameters


def day_points(ah, ap, rng):
    pts = []
    for q in QS:
        pts.append((ah * rp.h_nom(q) * (1 + rng.gauss(0, SIGMA)), ct.p1_fixed(q, ah, ap) * (1 + rng.gauss(0, SIGMA))))
    return pts


def day_cost(points):
    """cost[(sh, sp)] = sum over points of the best flow's squared relative residuals."""
    cost = {}
    for sh in SH_GRID:
        for sp in SP_GRID:
            tot = 0.0
            for hm, pm in points:
                best = 1e18
                for q in Q_GRID:
                    c = ((sh * H_TAB[q] - hm) / hm) ** 2 + ((P1_TAB[sp][q] - pm) / pm) ** 2
                    if c < best:
                        best = c
                tot += best
            cost[(sh, sp)] = tot
    return cost


def forecast(points, sh, sp):
    base, var = 0.0, 0.0
    for hm, pm in points:
        best, qe = 1e18, 0
        for q in Q_GRID:
            c = ((sh * H_TAB[q] - hm) / hm) ** 2 + ((P1_TAB[sp][q] - pm) / pm) ** 2
            if c < best:
                best, qe = c, q
        base += pm
        try:
            var += ct.p1_var(float(qe), sh, sp)
        except ValueError:
            return None                                      # this candidate model cannot deliver the duty
    return 100 * (base - var) / base


def part_a(cases, durations=(1, 3, 7, 14), trials=8, seed=21):
    rng = random.Random(seed)
    out = {d: {"learned": [], "none": [], "width": [], "cover": []} for d in durations}
    for ah, ap in cases:
        truth = ct.true_saving(ah, ap)
        for _ in range(trials):
            days = [day_points(ah, ap, rng) for _ in range(max(durations))]
            costs = [day_cost(d) for d in days]
            ref = days[-1]                                   # forecast from the most recent day's points
            f_none = forecast(ref, 1.0, 1.0)
            e_none = abs(f_none - truth) if f_none is not None else None
            for d in durations:
                tot = {k: sum(c[k] for c in costs[:d]) for k in costs[0]}
                cmin = min(tot.values())
                best = min(tot, key=tot.get)
                band = [k for k, v in tot.items() if v <= cmin + THRESH]
                vals = [v for v in (forecast(ref, *k) for k in band) if v is not None]
                est = forecast(ref, *best)
                if est is None or not vals or e_none is None:
                    continue
                out[d]["learned"].append(abs(est - truth))
                out[d]["none"].append(e_none)
                out[d]["width"].append(max(vals) - min(vals))
                out[d]["cover"].append(min(vals) - 0.5 <= truth <= max(vals) + 0.5)
    return out


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


def part_b(seed=33):
    rng = random.Random(seed)
    f = 0.10                                                  # constant clog, invisible to the wear estimate
    scenarios = {
        "control: no wear, 365 days": [0.0] * 365,
        "slow wear: 0 -> 10% over 180 days": [0.10 * min(d, 180) / 180 for d in range(240)],
        "fast wear: 0 -> 10% over 60 days": [0.10 * min(d, 60) / 60 for d in range(120)],
        "step: 6% from day 60": [0.0 if d < 60 else 0.06 for d in range(120)],
    }
    res = {}
    for name, ws in scenarios.items():
        runs = 3 if name.startswith("control") else 6
        alarms, wear_at = [], []
        for _ in range(runs):
            series = [sv.estimate(w, f, SIGMA, rng)[1] for w in ws]
            a = cusum(series)
            alarms.append(a)
            if a is not None:
                wear_at.append(ws[a])
        res[name] = (alarms, wear_at, runs)
    return res


if __name__ == "__main__":
    cases = [(1.00, 1.00), (0.97, 1.04), (0.94, 1.08), (1.03, 0.97), (0.92, 1.10)]
    print("A. LEARNED CALIBRATION FROM LOGS ONLY (no flow meter, no shut-off test)")
    print("   5 mismatch cases x 8 trials; error and band in percentage points of forecast saving\n")
    a = part_a(cases)
    print(f"{'days of logs':>12s}{'error: datasheet only':>24s}{'error: learned':>16s}{'mean band width':>17s}{'band holds truth':>18s}")
    for d, r in a.items():
        n = len(r["learned"])
        print(f"{d:12d}{sum(r['none']) / n:24.1f}{sum(r['learned']) / n:16.1f}{sum(r['width']) / n:17.1f}{100 * sum(r['cover']) / n:17.0f}%")
    print("\nB. WEAR DRIFT DETECTION (CUSUM on the daily wear estimate, baseline = first 14 days)")
    for name, (alarms, wear_at, runs) in part_b().items():
        hits = [x for x in alarms if x is not None]
        if name.startswith("control"):
            print(f"  {name}: {len(hits)} false alarms in {runs} x 365 days")
        else:
            if hits:
                print(f"  {name}: alarm in {len(hits)}/{runs} runs, median day {sorted(hits)[len(hits) // 2]}, true wear at alarm about {100 * sorted(wear_at)[len(wear_at) // 2]:.1f}%")
            else:
                print(f"  {name}: no alarm in {runs} runs")
