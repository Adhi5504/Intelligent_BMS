"""Option B: recommend drive settings and show the energy result in the model.

PumpRupee does not control the pump. For a pump that already has a VFD, it computes the
LOWEST pressure setpoint (and minimum speed) that still meets the required system head at
peak demand, and shows the modelled energy against three cases:

  1. baseline            : fixed speed, throttle valve (what the audit measures)
  2. constant pressure   : VFD holds ONE head setpoint = required head at peak demand + margin
                           (the simplest drive mode; operator enters one number)
  3. proportional press. : VFD lets the head setpoint follow the system curve + margin
                           (needs the drive's flow estimate / pump curve; more saving)

Steady-state hourly model on the generic pump from pump_sim.py (ASSUMED curves, not a real pump).
Not modelled: control dynamics, drive tuning, minimum-flow protection. The drive does the control.
"""
import math
import pump_sim as ps

SCALE = 0.90                        # keep peak demand inside the pump's capability
DEMAND = [d * SCALE for d in ps.DEMAND]
MARGIN = 0.05                       # 5% head safety margin on any setpoint
M_PER_BAR = 10.197


def h_sys(q):
    return ps.H_STATIC + ps.K * q * q


def speed_for_head(q, head):
    n = math.sqrt((head + ps.A * q * q) / ps.H0)
    return n


def power_vfd(q, head, n):
    if n > 1 + 1e-9:
        raise ValueError("setpoint not reachable at full speed")
    n = max(ps.N_MIN, n)
    hyd = ps.RHO_G * q / 3600 * head
    return hyd / ps.eta_pump(q, n) / ps.ETA_MOTOR / ps.ETA_VFD


def run():
    q_peak = max(DEMAND)
    h_const = h_sys(q_peak) * (1 + MARGIN)            # the ONE number the operator enters
    base = sum(ps.baseline(q) for q in DEMAND)

    const_kwh, prop_kwh, n_const, n_prop = 0.0, 0.0, [], []
    for q in DEMAND:
        n1 = speed_for_head(q, h_const)
        const_kwh += power_vfd(q, h_const, n1)
        n_const.append(max(ps.N_MIN, n1))
        hp = h_sys(q) * (1 + MARGIN)
        n2 = speed_for_head(q, hp)
        prop_kwh += power_vfd(q, hp, n2)
        n_prop.append(max(ps.N_MIN, n2))
        assert hp >= h_sys(q) and h_const >= h_sys(q), "required head not met"

    vol = sum(DEMAND)
    res = {
        "setpoint_head_m": h_const,
        "setpoint_bar": h_const / M_PER_BAR,
        "min_speed_const": min(n_const),
        "min_speed_prop": min(n_prop),
        "volume_m3_day": vol,
        "kwh_day": {"baseline": base, "constant": const_kwh, "proportional": prop_kwh},
        "sec": {"baseline": base / vol, "constant": const_kwh / vol, "proportional": prop_kwh / vol},
        "saving_pct": {"constant": 100 * (base - const_kwh) / base,
                       "proportional": 100 * (base - prop_kwh) / base},
    }
    for k in ("constant", "proportional"):
        saved = base - res["kwh_day"][k]
        res.setdefault("annual", {})[k] = (saved * ps.DAYS, saved * ps.DAYS * ps.TARIFF, saved * ps.DAYS * ps.EF)
    return res


if __name__ == "__main__":
    r = run()
    print(f"Recommended constant-pressure setpoint: {r['setpoint_head_m']:.1f} m  (= {r['setpoint_bar']:.2f} bar)")
    print(f"Recommended minimum speed: {r['min_speed_const']*100:.0f}% (constant) / {r['min_speed_prop']*100:.0f}% (proportional)")
    print(f"Delivered volume: {r['volume_m3_day']:.0f} m3/day (same in all cases; required head always met)\n")
    print(f"{'Case':32s}{'kWh/day':>10s}{'SEC kWh/m3':>13s}{'saving':>9s}")
    names = {"baseline": "Fixed speed + throttle valve", "constant": "VFD, constant-pressure setpoint",
             "proportional": "VFD, proportional pressure"}
    for k in ("baseline", "constant", "proportional"):
        sv = "" if k == "baseline" else f"{r['saving_pct'][k]:.1f}%"
        print(f"{names[k]:32s}{r['kwh_day'][k]:10.1f}{r['sec'][k]:13.3f}{sv:>9s}")
    print("\nPer pump per year (300 days, Rs 8/kWh, 0.71 kg CO2/kWh):")
    for k in ("constant", "proportional"):
        kwh, rs, co2 = r["annual"][k]
        print(f"  {names[k]:32s}{kwh:9,.0f} kWh  Rs {rs:9,.0f}  {co2/1000:5.1f} t CO2")
