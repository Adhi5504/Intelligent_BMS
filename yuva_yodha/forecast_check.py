"""Pre-retrofit savings forecast from cheap logs on an EXISTING fixed-speed throttled pump.

Audit-in-a-box idea: log kW and discharge pressure for a few days, estimate the flow
profile from a nameplate-based pump model, and forecast how much a VFD would save.

Honesty check: the estimator uses a deliberately WRONG model (nameplate-scaled curves,
the way a real audit would) while the 'plant' uses the true curves from pump_sim.py.
We report how far the forecast saving is from the true saving.
"""
import math
import random
import pump_sim as ps


class Model:
    def __init__(self, h0, eta_bep):
        self.h0, self.eta_bep = h0, eta_bep
        self.a = (h0 - 30.0) / 100.0 ** 2          # forced through the nameplate design point
        self.sh = 1.0                               # head scale learned from one calibration point
        self.sp = 1.0                               # power scale learned from one calibration point

    def calibrate(self, q, h_meas, p_meas):
        p, h = self.p_base(q)
        self.sh *= h_meas / h
        self.sp *= p_meas / p

    def eta(self, q, n):
        q_eq = q / n
        return max(self.eta_bep * (1 - 0.9 * (q_eq / 100.0 - 1) ** 2), 0.20)

    def p_base(self, q):                            # fixed speed, throttled
        h = (self.h0 - self.a * q * q) * self.sh
        return ps.RHO_G * q / 3600 * h / self.eta(q, 1.0) / ps.ETA_MOTOR * self.sp, h

    def p_vfd(self, q, hs, k):
        n = max(0.5, min(1.0, math.sqrt((hs + (k + self.a) * q * q) / self.h0)))
        hsys = hs + k * q * q
        return ps.RHO_G * q / 3600 * hsys / self.eta(q, n) / ps.ETA_MOTOR / ps.ETA_VFD * self.sp


def day(rng):
    return [min(100.0, max(55.0, rng.gauss(78, 14))) for _ in range(16)]


def run(h0_est, eta_est, noise, runs=200, seed=3, cal_err=None):
    rng = random.Random(seed)
    true = Model(ps.H0, ps.ETA_BEP)
    est = Model(h0_est, eta_est)
    hs = ps.H_STATIC
    k = (30.0 - hs) / 100.0 ** 2
    if cal_err is not None:                         # one measured flow point (e.g. tank fill timing)
        qc = 90.0
        pc, hc = true.p_base(qc)
        est.calibrate(qc * (1 + cal_err), hc, pc)   # flow itself is only known to +-cal_err
    errs, rel = [], []
    for _ in range(runs):
        qs = day(rng)
        tb = tv = eb = ev = 0.0
        for q in qs:
            p, h = true.p_base(q)
            pm = p * (1 + rng.gauss(0, noise))
            hm = h * (1 + rng.gauss(0, noise))
            # estimate q from (h, p) with the wrong model
            best, qe = 1e18, 78.0
            for qi in range(20, 131):
                pe, he = est.p_base(float(qi))
                c = ((he - hm) / hm) ** 2 + ((pe - pm) / pm) ** 2
                if c < best:
                    best, qe = c, float(qi)
            tb += p
            tv += true.p_vfd(q, hs, k)
            eb += pm
            ev += est.p_vfd(qe, hs, k)
        true_save = (tb - tv) / tb
        est_save = (eb - ev) / eb
        errs.append(abs(est_save - true_save))
        rel.append(est_save - true_save)
    errs.sort()
    return sum(errs) / runs, errs[int(0.9 * runs)], sum(rel) / runs


if __name__ == "__main__":
    print("estimator model (shut-off head, eta_bep) | noise -> saving-forecast error in %-points (mean abs / p90 / bias)")
    for h0e, ee in [(40.0, 0.75), (38.0, 0.70), (36.0, 0.65), (44.0, 0.80)]:
        for nz in (0.01, 0.03):
            m, p90, bias = run(h0e, ee, nz)
            c, c90, cb = run(h0e, ee, nz, cal_err=0.05)
            print(f"  H0={h0e:4.0f}, eta={ee:.2f} | {nz*100:.0f}% -> {m*100:5.1f} / {p90*100:5.1f} / {bias*100:+5.1f}"
                  f"   || with one flow point (+-5%): {c*100:5.1f} / {c90*100:5.1f} / {cb*100:+5.1f}")
