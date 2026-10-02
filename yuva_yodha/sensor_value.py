"""Value of each extra sensor, in rupees, on the real pump (Grundfos NB 65-160/157).

Question: with only power + discharge pressure, how many rupees of waste does the tool put under
the WRONG cause, and how much of that does an extra sensor remove?

Plant (simulated, known truth): real pump curves from real_pump_sim.py plus three causes of waste
  throttle : fixed speed + throttle valve instead of speed matched to demand
  wear     : worn impeller / wear rings (head x(1-w), efficiency x(1-1.5w))   [wear model is ASSUMED]
  foul     : clogged strainer / pipe (system friction x(1+f))
Reference ("ideal") = healthy pump, clean system, speed matched to demand.
Attribution = Shapley (average over all orderings), so the three parts add up exactly.

Sensor sets
  S0 : power + discharge pressure (noise 1%)
  S1 : S0 + pressure drop across the strainer (gives fouling within +-15%)
  S2 : S0 + process-side (post-valve) pressure (gives the system head, hence fouling)
The test does NOT price sensors (no real quotes). It reports the rupees of misattribution a sensor
removes; a sensor is worth buying if its price is below that figure times your payback tolerance.

Limits: simulated; healthy pump curve assumed known exactly; 1% sensor noise; one pump; wear is a model.
"""
import itertools
import math
import random

import real_pump_sim as rp

HS = 10.0                                # ASSUMED static lift
K0 = (rp.H_RATED - HS) / rp.Q_RATED ** 2
PEAK = 0.80                              # ASSUMED peak demand as a fraction of rated flow
QS = [f * PEAK * rp.Q_RATED for f in rp.PROFILE]
RS_PER_KWH_DAY = rp.DAYS * rp.TARIFF


def power(q, throttled, w, f):
    hsys = HS + K0 * (1 + f) * q * q
    wear_p = (1 - w) / (1 - 1.5 * w)
    if throttled:
        if (1 - w) * rp.h_nom(q) < hsys - 1e-9:
            raise ValueError("cannot deliver")
        p2 = rp.p2_nom(q) * wear_p
        return p2 / rp.eta_motor(p2)

    def g(r):
        qe = q / r
        return -1e9 if qe > rp.Q_MAX_FIT else r * r * (1 - w) * rp.h_nom(qe) - hsys
    lo, hi = rp.N_MIN, 1.0
    if g(hi) < 0:
        raise ValueError("cannot deliver")
    if g(lo) > 0:
        r = lo
    else:
        for _ in range(50):
            mid = (lo + hi) / 2
            if g(mid) > 0:
                hi = mid
            else:
                lo = mid
        r = hi
    p2 = r ** 3 * rp.p2_nom(q / r) * wear_p
    return p2 / rp.eta_motor(p2) / rp.ETA_VFD


def shapley(qs, w, f):
    players = ("throttle", "wear", "foul")

    def v(s):
        return sum(power(q, "throttle" in s, w if "wear" in s else 0.0, f if "foul" in s else 0.0) for q in qs)
    contrib = dict.fromkeys(players, 0.0)
    perms = list(itertools.permutations(players))
    for perm in perms:
        cur = set()
        for p in perm:
            contrib[p] += v(cur | {p}) - v(cur)
            cur.add(p)
    return {p: c / len(perms) for p, c in contrib.items()}


# precomputed model grid for the estimator (healthy curve known exactly)
Q_GRID = list(range(40, 131))
W_GRID = [i / 100 for i in range(0, 21)]
H_NOM = {q: rp.h_nom(q) for q in Q_GRID}
P2_NOM = {q: rp.p2_nom(q) for q in Q_GRID}


def estimate(w, f, noise, rng):
    q_est, w_est = [], []
    for q in QS:
        head = (1 - w) * rp.h_nom(q)
        p1 = power(q, True, w, f)
        hm, pm = head * (1 + rng.gauss(0, noise)), p1 * (1 + rng.gauss(0, noise))
        best, arg = 1e18, (q, 0.0)
        for qi in Q_GRID:
            for wi in W_GRID:
                p2 = P2_NOM[qi] * (1 - wi) / (1 - 1.5 * wi)
                c = (((1 - wi) * H_NOM[qi] - hm) / hm) ** 2 + ((p2 / rp.eta_motor(p2) - pm) / pm) ** 2
                if c < best:
                    best, arg = c, (float(qi), wi)
        q_est.append(arg[0])
        w_est.append(arg[1])
    w_est.sort()
    return q_est, w_est[len(w_est) // 2]


def misattributed_rs(est, truth):
    return 0.5 * sum(abs(est[p] - truth[p]) for p in truth) * RS_PER_KWH_DAY


def scenario(w, f, noise=0.01, days=12, seed=11):
    rng = random.Random(seed)
    truth = shapley(QS, w, f)
    res = {"S0": [], "S1": [], "S2": []}
    for _ in range(days):
        q_est, w_est = estimate(w, f, noise, rng)
        try:
            res["S0"].append(misattributed_rs(shapley(q_est, w_est, 0.0), truth))
            res["S1"].append(misattributed_rs(shapley(q_est, w_est, max(0.0, f * (1 + rng.gauss(0, 0.15)))), truth))
            fs = []                                           # S2: system head from the process-side pressure
            for q_t, q_e in zip(QS, q_est):
                hsys_meas = (HS + K0 * (1 + f) * q_t * q_t) * (1 + rng.gauss(0, noise))
                fs.append((hsys_meas - HS) / (K0 * q_e * q_e) - 1)
            fs.sort()
            res["S2"].append(misattributed_rs(shapley(q_est, w_est, max(0.0, fs[len(fs) // 2])), truth))
        except ValueError:
            continue
    mean = {k: sum(v) / len(v) for k, v in res.items()}
    return truth, mean


if __name__ == "__main__":
    print("Real pump NB 65-160/157, peak demand 80% of rated, 10 m static lift, 1% sensor noise, 12 simulated days per case")
    print("Rupees per year attributed to the WRONG cause (mean), and the true split\n")
    print(f"{'wear/foul':>10s} {'true waste Rs/yr':>17s} {'true split thr/wear/foul %':>28s} {'S0 wrong':>10s} {'S1 wrong':>10s} {'S2 wrong':>10s}")
    revealed1, revealed2 = [], []
    for w, f in [(0.05, 0.20), (0.10, 0.10), (0.00, 0.30), (0.08, 0.00), (0.03, 0.40)]:
        truth, m = scenario(w, f)
        tot = sum(truth.values())
        split = "/".join(f"{100 * truth[p] / tot:4.1f}" for p in ("throttle", "wear", "foul"))
        print(f"{w:4.2f}/{f:4.2f} {tot * RS_PER_KWH_DAY:17,.0f} {split:>28s} {m['S0']:10,.0f} {m['S1']:10,.0f} {m['S2']:10,.0f}")
        revealed1.append(m["S0"] - m["S1"])
        revealed2.append(m["S0"] - m["S2"])
    n = len(revealed1)
    print(f"\nAverage rupees/year of misattribution removed:  strainer dP sensor (S1): Rs {sum(revealed1) / n:,.0f}   process-side pressure (S2): Rs {sum(revealed2) / n:,.0f}")
    print("A sensor is worth buying if its installed price is below this figure times the payback you accept (for example 1 year).")
