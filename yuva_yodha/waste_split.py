"""Waste-by-cause split: can a cheap logger recover WHY a pump wastes energy?

Simulated plant (generic pump from pump_sim.py) with three known causes:
  throttle : fixed speed with a throttle valve instead of speed matched to demand
  wear     : worn impeller / wear rings (head and efficiency below the new curve)
  foul     : clogged strainer or pipe (extra friction in the system)
Reference ("ideal") = healthy pump, clean system, speed matched to demand.

Attribution: Shapley value over the three causes (average over all 6 orderings), so the
parts add up exactly to actual minus ideal energy and do not depend on an arbitrary order.

Estimator test: from noisy measured (power, head) per hour, with the healthy pump curve known,
recover the split (a) with no extra sensor, (b) with a strainer pressure-drop sensor.
Key physical fact: with a throttle valve at fixed speed, fouling does not change pump power at a
given flow (the valve just absorbs less head), so (power, head) alone cannot see fouling.
"""
import itertools
import math
import random
import pump_sim as ps

DEMAND = [d * 0.85 for d in ps.DEMAND]       # keep the plant feasible with wear and fouling
DAYS, TARIFF = 300, ps.TARIFF


def power(q, throttled, w, f):
    k = ps.K * (1 + f)
    hsys = ps.H_STATIC + k * q * q
    if throttled:
        head = (1 - w) * (ps.H0 - ps.A * q * q)
        if head < hsys - 1e-9:
            raise ValueError("pump cannot deliver demand")
        eta = ps.eta_pump(q, 1.0) * (1 - 1.5 * w)
        return ps.RHO_G * q / 3600 * head / eta / ps.ETA_MOTOR
    n = math.sqrt((hsys / (1 - w) + ps.A * q * q) / ps.H0)
    n = max(ps.N_MIN, n)
    if n > 1 + 1e-9:
        raise ValueError("pump cannot deliver demand")
    eta = ps.eta_pump(q, n) * (1 - 1.5 * w)
    return ps.RHO_G * q / 3600 * hsys / eta / ps.ETA_MOTOR / ps.ETA_VFD


def day_kwh(qs, throttled, w, f):
    return sum(power(q, throttled, w, f) for q in qs)


def shapley(qs, w_act, f_act):
    players = ["throttle", "wear", "foul"]

    def v(s):
        return day_kwh(qs, "throttle" in s, w_act if "wear" in s else 0.0, f_act if "foul" in s else 0.0)

    contrib = {p: 0.0 for p in players}
    perms = list(itertools.permutations(players))
    for perm in perms:
        cur = set()
        for p in perm:
            contrib[p] += v(cur | {p}) - v(cur)
            cur.add(p)
    return {p: c / len(perms) for p, c in contrib.items()}


def estimate(qs_true, w_true, f_true, noise, rng):
    """Recover (flow, wear) per hour from noisy measured power and head at fixed speed."""
    qe, we = [], []
    for q in qs_true:
        head = (1 - w_true) * (ps.H0 - ps.A * q * q)
        p = power(q, True, w_true, f_true)
        hm, pm = head * (1 + rng.gauss(0, noise)), p * (1 + rng.gauss(0, noise))
        best, arg = 1e18, (q, 0.0)
        for qi in range(20, 131):
            for wi in range(0, 21):
                w = wi / 100.0
                h_mod = (1 - w) * (ps.H0 - ps.A * qi * qi)
                p_mod = ps.RHO_G * qi / 3600 * h_mod / (ps.eta_pump(qi, 1.0) * (1 - 1.5 * w)) / ps.ETA_MOTOR
                c = ((h_mod - hm) / hm) ** 2 + ((p_mod - pm) / pm) ** 2
                if c < best:
                    best, arg = c, (float(qi), w)
        qe.append(arg[0])
        we.append(arg[1])
    we.sort()
    return qe, we[len(we) // 2]


def shares(c):
    tot = sum(c.values())
    return [100 * c[p] / tot for p in ("throttle", "wear", "foul")], tot


def scenario(w, f, noise=0.01, seeds=20):
    truth = shapley(DEMAND, w, f)
    ts, tot = shares(truth)
    rs = random.Random(5)
    naive, with_dp = [], []
    for _ in range(seeds):
        qe, we = estimate(DEMAND, w, f, noise, rs)
        # (a) no extra sensor: fouling is invisible, assumed clean
        try:
            naive.append(shares(shapley(qe, we, 0.0))[0])
        except ValueError:
            pass
        # (b) strainer pressure-drop sensor gives fouling within +-15%
        f_est = f * (1 + rs.gauss(0, 0.15))
        try:
            with_dp.append(shares(shapley(qe, we, max(0.0, f_est)))[0])
        except ValueError:
            pass
    avg = lambda rows: [sum(r[i] for r in rows) / len(rows) for i in range(3)] if rows else [float("nan")] * 3
    return ts, avg(naive), avg(with_dp), truth, tot


if __name__ == "__main__":
    print("shares of total waste, %: [throttle, wear, foul]   (noise 1%, 20 simulated days each)")
    for w, f in [(0.05, 0.20), (0.10, 0.10), (0.00, 0.30), (0.08, 0.00)]:
        ts, nv, dp, truth, tot = scenario(w, f)
        rs_yr = tot * DAYS * TARIFF
        fmt = lambda x: "[" + ", ".join(f"{v:5.1f}" for v in x) + "]"
        print(f"\nwear={w:.2f} foul={f:.2f}  total waste vs ideal = {tot:6.1f} kWh/day = Rs {rs_yr:,.0f}/yr")
        print(f"  truth            {fmt(ts)}")
        print(f"  no extra sensor  {fmt(nv)}")
        print(f"  + strainer dP    {fmt(dp)}")
