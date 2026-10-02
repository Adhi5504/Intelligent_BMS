"""Reproducible versions of two checks quoted in RESULTS_SUMMARY.md that were first run interactively.

1. How much the best flow-free anchor depends on closed-valve power being representative of normal-operation
   power (fraction t of the true power mismatch transferred): quoted as 1.0 / 3.2 / 6.2 points for t = 1 / 0.5 / 0.
2. Error distribution of the log-learned calibration forecast (share of runs within +-1/2/3 points, 90th percentile).

Simulated, real pump curve from real_pump_sim.py. Fixed seeds; results are deterministic.
"""
import calibration_test as ct
import learning_layer as ll

CASES = [(1.00, 1.00), (0.97, 1.04), (0.94, 1.08), (1.03, 0.97), (0.92, 1.10)]


def closed_valve_transfer():
    orig = ct.anchor_scales

    def make(t):
        def f(kind, ah, ap, rng, noise=0.01):
            if kind == "sp_partial":
                sh = ah * ct.H0_FIT * (1 + rng.gauss(0, noise)) / ct.H0_FIT
                sp = (1 + t * (ap - 1)) * (1 + rng.gauss(0, noise))
                return sh, sp
            return orig(kind, ah, ap, rng, noise)
        return f
    print("Average forecast error (points) when closed-valve power transfers a fraction t of the true power mismatch:")
    for t in (1.0, 0.5, 0.0):
        ct.anchor_scales = make(t)
        errs = [ct.forecast_error(ah, ap, "sp_partial")[1] for ah, ap in CASES]
        print(f"  t = {t:.1f}: {sum(errs) / len(errs):5.1f}")
    ct.anchor_scales = orig


def learned_error_quantiles():
    a = ll.part_a(CASES, durations=(1, 7, 14), trials=8, seed=77)
    print("\nLearned-calibration forecast: share of runs within +-X points, 90th percentile and max error")
    print(f"{'days':>5s}{'<=1pt':>8s}{'<=2pt':>8s}{'<=3pt':>8s}{'90th pct':>10s}{'max':>7s}")
    for d, r in a.items():
        e = sorted(r["learned"])
        n = len(e)
        share = lambda x: 100 * sum(1 for v in e if v <= x) / n
        print(f"{d:5d}{share(1):7.0f}%{share(2):7.0f}%{share(3):7.0f}%{e[int(0.9 * n)]:10.1f}{e[-1]:7.1f}")


if __name__ == "__main__":
    closed_valve_transfer()
    learned_error_quantiles()
