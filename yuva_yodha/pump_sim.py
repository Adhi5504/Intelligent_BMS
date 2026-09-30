"""Specific-energy-consumption (SEC) simulation: throttle control vs speed control.

Baseline : fixed-speed pump, a throttle valve burns the excess head to hit the demanded flow.
Proposed : variable-speed pump, run at the lowest speed that still delivers the demanded
           flow at the pressure the system needs (system curve). Flow is never below demand,
           so throughput and required pressure are preserved by construction.

All parameters are ILLUSTRATIVE. Replace with the datasheet curves of the pump you study
(or with rig measurements) before quoting any result.
"""
import math

RHO_G = 9.81            # kN/m3 -> kW = 9.81 * Q[m3/s] * H[m]
N_RATED = 1.0           # speed as a fraction of rated
Q_BEP = 100.0           # m3/h at best efficiency point, rated speed
H0 = 40.0               # m, shut-off head at rated speed
A = 0.001               # pump curve: H = H0*(N)^2 - A*Q^2   (Q in m3/h)
H_STATIC = 10.0         # m, static lift of the plant
K = 0.002               # system curve: H = H_STATIC + K*Q^2
ETA_BEP = 0.75          # pump efficiency at BEP
ETA_MOTOR = 0.90        # held constant (simplification; real motors lose efficiency at part-load)
ETA_VFD = 0.97
N_MIN = 0.50            # minimum allowed speed fraction

# 16 operating hours; demanded flow in m3/h (illustrative shift profile)
DEMAND = [100, 100, 90, 80, 70, 60, 60, 60, 70, 80, 90, 100, 90, 80, 70, 60]
TARIFF = 8.0            # Rs/kWh
DAYS = 300
EF = 0.71               # kg CO2/kWh - VERIFY against the current CEA value


def eta_pump(q, n):
    """Pump efficiency from a parabola around the (speed-scaled) BEP."""
    q_eq = q / n                                   # equivalent flow at rated speed
    eta = ETA_BEP * (1 - 0.9 * (q_eq / Q_BEP - 1) ** 2)
    return max(eta, 0.20)


def power_kw(q, head, n, vfd):
    hyd = RHO_G * (q / 3600.0) * head
    elec = hyd / eta_pump(q, n) / ETA_MOTOR
    return elec / ETA_VFD if vfd else elec


def baseline(q):
    head_pump = H0 - A * q ** 2                    # fixed speed: pump head at this flow
    assert head_pump >= H_STATIC + K * q ** 2 - 1e-9, "pump cannot deliver demand"
    return power_kw(q, head_pump, N_RATED, vfd=False)


def proposed(q):
    n = math.sqrt((H_STATIC + (K + A) * q ** 2) / H0)
    n = max(N_MIN, min(N_RATED, n))
    head_sys = H_STATIC + K * q ** 2               # exactly the head the process needs
    # if N was clamped up to N_MIN a throttle would still be needed; check feasibility
    assert H0 * n ** 2 - A * q ** 2 >= head_sys - 1e-9, "speed limit violates required head"
    return power_kw(q, head_sys, n, vfd=True), n


def run():
    kwh_b = sum(baseline(q) for q in DEMAND)       # 1 hour per step
    kwh_p = 0.0
    speeds = []
    for q in DEMAND:
        p, n = proposed(q)
        kwh_p += p
        speeds.append(n)
    volume = sum(DEMAND)                           # m3 per day
    sec_b, sec_p = kwh_b / volume, kwh_p / volume
    saved = kwh_b - kwh_p
    return {
        "volume_m3_per_day": volume,
        "baseline_kwh_per_day": kwh_b,
        "proposed_kwh_per_day": kwh_p,
        "baseline_SEC_kwh_per_m3": sec_b,
        "proposed_SEC_kwh_per_m3": sec_p,
        "SEC_reduction_pct": 100 * saved / kwh_b,
        "annual_kwh_saved": saved * DAYS,
        "annual_rs_saved": saved * DAYS * TARIFF,
        "annual_co2_kg_saved": saved * DAYS * EF,
        "min_speed_fraction": min(speeds),
    }


if __name__ == "__main__":
    for k, v in run().items():
        print(f"{k:28s} {v:,.3f}")
    # sensitivity: how much of the saving survives if static lift is larger?
    print("\nSensitivity to static head (friction share falls => savings fall):")
    for hs in (5.0, 10.0, 15.0, 20.0):
        H_STATIC = hs
        K = (30.0 - hs) / 100.0 ** 2               # keep the design point at 100 m3/h, 30 m
        H0 = 40.0
        A = (H0 - 30.0) / 100.0 ** 2
        r = run()
        print(f"  static {hs:4.0f} m -> SEC reduction {r['SEC_reduction_pct']:5.1f}%")
