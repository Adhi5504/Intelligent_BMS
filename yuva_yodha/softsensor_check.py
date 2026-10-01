"""Feasibility check: can flow (Q) and wear be recovered from cheap signals only?

Cheap signals: motor electrical power P, speed N (from the drive), discharge pressure/head H.
No flow meter. Unknowns: flow Q and a wear factor w (0 = healthy).

Wear model (illustrative): head curve scaled by (1 - w), pump efficiency scaled by (1 - 1.5*w).
We solve for (Q, w) from noisy (H, P) at known N and report the error.
Reuses the pump curves from pump_sim.py.
"""
import random
import math
import pump_sim as ps


def head_pump(q, n, w):
    return (1 - w) * (ps.H0 * n ** 2 - ps.A * q ** 2)


def power_elec(q, n, w):
    h = head_pump(q, n, w)
    eta = ps.eta_pump(q, n) * (1 - 1.5 * w)
    hyd = ps.RHO_G * (q / 3600.0) * h
    return hyd / eta / ps.ETA_MOTOR


def solve(h_meas, p_meas, n):
    """Grid search over (q, w); coarse but enough for a feasibility check."""
    best, arg = 1e18, None
    for qi in range(20, 131, 1):
        q = float(qi)
        for wi in range(0, 31):
            w = wi / 100.0
            eh = (head_pump(q, n, w) - h_meas) / max(h_meas, 1e-6)
            ep = (power_elec(q, n, w) - p_meas) / max(p_meas, 1e-6)
            c = eh * eh + ep * ep
            if c < best:
                best, arg = c, (q, w)
    return arg


def trial(noise_h, noise_p, runs=200, seed=1):
    random.seed(seed)
    eq, ew = [], []
    for _ in range(runs):
        n = random.uniform(0.7, 1.0)
        q_true = random.uniform(55, 100) * n
        w_true = random.choice([0.0, 0.05, 0.10, 0.15])
        h = head_pump(q_true, n, w_true) * (1 + random.gauss(0, noise_h))
        p = power_elec(q_true, n, w_true) * (1 + random.gauss(0, noise_p))
        q_est, w_est = solve(h, p, n)
        eq.append(abs(q_est - q_true) / q_true)
        ew.append(abs(w_est - w_true))
    eq.sort()
    ew.sort()
    return sum(eq) / runs, eq[int(0.9 * runs)], sum(ew) / runs, ew[int(0.9 * runs)]


if __name__ == "__main__":
    print("noise(H%, P%) -> flow err mean / p90 | wear err mean / p90 (absolute, 0.05 = 5 points)")
    for nh, np_ in [(0.0, 0.0), (0.01, 0.01), (0.02, 0.02), (0.03, 0.03)]:
        fq, fq90, fw, fw90 = trial(nh, np_)
        print(f"  ({nh*100:.0f}%, {np_*100:.0f}%) -> flow {fq*100:5.1f}% / {fq90*100:5.1f}% | wear {fw:.3f} / {fw90:.3f}")
