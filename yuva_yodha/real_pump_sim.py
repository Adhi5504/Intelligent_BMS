"""Real-pump energy model: Grundfos NB 65-160/157 (product 97839240).

Data: pump_data/pump_curve_NB65-160-157.csv (manufacturer Product Center readouts, 14 points).
Rules from pump_data/PUMP_DATA_BRIEF.md that this script follows:
  * Table values are manufacturer data. Anything between table points is a FIT and is labelled as such.
  * True shut-off head (Q = 0) is NOT given. The two lowest points (0.5 and 1 m3/h) are NOT used
    in any fit and no flow below 10 m3/h is ever simulated.
  * Speed is not constant in the table (2981 -> 2947 rpm, motor slip). Variable-speed operation uses
    affinity laws relative to the table, treating it as one fixed-speed curve (about 1% approximation).

ASSUMED (not from the datasheet): static lift of the plant, the demand profile, the head safety margin,
VFD efficiency, running hours, tariff. These are varied in the sweep at the end.
Steady-state hourly model. No control dynamics, no minimum-flow protection, no NPSH check.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "pump_data", "pump_curve_NB65-160-157.csv")

RHO, G = 998.2, 9.81
Q_RATED, H_RATED = 114.0, 26.07        # Product Center readout at rated flow (datasheet prints 26.5 m)
ETA_VFD = 0.97                         # ASSUMED
N_MIN = 0.50                           # ASSUMED minimum speed ratio
HOURS_PER_DAY, DAYS = 16, 300          # ASSUMED
TARIFF = 8.0                           # Rs/kWh, ASSUMED
EF = 0.710                             # kg CO2/kWh, CEA v21.0 FY2024-25
PROFILE = [1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.6, 0.6, 0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7, 0.6]  # ASSUMED fractions of peak


def load():
    rows = []
    with open(CSV_PATH, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({k: float(r[k]) for k in ("Q_m3h", "H_m", "P2_shaft_kW", "P1_input_kW", "eta_pump_pct")})
    return [r for r in rows if r["Q_m3h"] >= 10]          # drop the two low-flow points (not shut-off)


def polyfit(xs, ys, deg):
    """Least squares polynomial in x/100 (normal equations, plain Python)."""
    n = deg + 1
    a = [[sum((x / 100) ** (i + j) for x in xs) for j in range(n)] for i in range(n)]
    b = [sum(y * (x / 100) ** i for x, y in zip(xs, ys)) for i in range(n)]
    for i in range(n):                                     # gaussian elimination
        p = max(range(i, n), key=lambda r: abs(a[r][i]))
        a[i], a[p], b[i], b[p] = a[p], a[i], b[p], b[i]
        for r in range(i + 1, n):
            f = a[r][i] / a[i][i]
            for c in range(i, n):
                a[r][c] -= f * a[i][c]
            b[r] -= f * b[i]
    coef = [0.0] * n
    for i in range(n - 1, -1, -1):
        coef[i] = (b[i] - sum(a[i][j] * coef[j] for j in range(i + 1, n))) / a[i][i]
    return coef


def poly(coef, x):
    return sum(c * (x / 100) ** i for i, c in enumerate(coef))


DATA = load()
QS = [r["Q_m3h"] for r in DATA]
H_COEF = polyfit(QS, [r["H_m"] for r in DATA], 3)           # FIT (cubic)
P2_COEF = polyfit(QS, [r["P2_shaft_kW"] for r in DATA], 3)  # FIT (cubic)
Q_MIN_FIT, Q_MAX_FIT = min(QS), max(QS)


def fit_errors():
    eh = max(abs(poly(H_COEF, r["Q_m3h"]) - r["H_m"]) for r in DATA)
    ep = max(abs(poly(P2_COEF, r["Q_m3h"]) - r["P2_shaft_kW"]) for r in DATA)
    return eh, ep


# motor efficiency P2/P1 from the table, as a function of shaft power (FIT, linear between table points)
_MP = sorted((r["P2_shaft_kW"], r["P2_shaft_kW"] / r["P1_input_kW"]) for r in DATA)


def eta_motor(p2):
    if p2 <= _MP[0][0]:
        return _MP[0][1]
    if p2 >= _MP[-1][0]:
        return _MP[-1][1]
    for (x0, y0), (x1, y1) in zip(_MP, _MP[1:]):
        if x0 <= p2 <= x1:
            return y0 + (y1 - y0) * (p2 - x0) / (x1 - x0)


def h_nom(q):
    return poly(H_COEF, q)


def p2_nom(q):
    return poly(P2_COEF, q)


def speed_for_head(q, head):
    """Speed ratio r such that the pump delivers flow q at head: r^2 * H(q/r) = head. Bisection."""
    def f(r):
        qe = q / r
        if qe > Q_MAX_FIT:
            return -1e9                                     # beyond the data range: not allowed
        return r * r * h_nom(qe) - head
    lo, hi = N_MIN, 1.0
    if f(hi) < 0:
        raise ValueError("pump cannot deliver this duty at full speed")
    if f(lo) > 0:
        return lo
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return hi


def p1_fixed_speed(q):
    p2 = p2_nom(q)
    return p2 / eta_motor(p2)


def p1_variable(q, r):
    p2 = (r ** 3) * p2_nom(q / r)
    return p2 / eta_motor(p2) / ETA_VFD


def evaluate(peak_frac=0.9, h_static=10.0, margin=0.05):
    """peak_frac: peak demand as a fraction of rated flow (lower = more oversized pump)."""
    k = (H_RATED - h_static) / Q_RATED ** 2                # system curve through the rated point
    h_sys = lambda q: h_static + k * q * q
    qs = [f * peak_frac * Q_RATED for f in PROFILE]
    if min(qs) < Q_MIN_FIT:
        raise ValueError("demand below the fitted range")
    for q in qs:
        if h_nom(q) < h_sys(q) - 1e-9:
            raise ValueError("pump cannot meet the demand")
    h_const = h_sys(max(qs)) * (1 + margin)
    base = const = prop = 0.0
    for q in qs:
        base += p1_fixed_speed(q)
        const += p1_variable(q, speed_for_head(q, h_const))
        prop += p1_variable(q, speed_for_head(q, h_sys(q) * (1 + margin)))
    vol = sum(qs)
    return {"qs": qs, "h_const": h_const, "base": base, "const": const, "prop": prop, "vol": vol}


def report_main():
    eh, ep = fit_errors()
    print("Grundfos NB 65-160/157 (product 97839240), 11 kW IE3, 2-pole, water 20 C")
    print(f"Cubic fits over Q = {Q_MIN_FIT:.0f}-{Q_MAX_FIT:.0f} m3/h: max error vs table  H {eh:.2f} m,  P2 {ep:.2f} kW  (FITS, not data)")
    print("Shut-off head is not given; flows below 10 m3/h are not used.\n")
    r = evaluate()
    vol = r["vol"]
    print("MAIN CASE (ASSUMED: peak demand 90% of rated flow, static lift 10 m, 5% head margin, 16 h/day)")
    print(f"Peak flow {max(r['qs']):.0f} m3/h, delivered {vol:.0f} m3/day, recommended constant-pressure setpoint {r['h_const']:.1f} m ({r['h_const']/10.197:.2f} bar)")
    print(f"{'Case':34s}{'kWh/day':>9s}{'SEC kWh/m3':>12s}{'saving':>9s}{'Rs/yr':>10s}{'t CO2/yr':>10s}")
    for key, name in (("base", "Fixed speed + throttle valve"), ("const", "VFD, constant-pressure setpoint"), ("prop", "VFD, proportional pressure")):
        kwh = r[key]                                        # 1 hour per profile step
        sv = "" if key == "base" else f"{100 * (r['base'] - kwh) / r['base']:.1f}%"
        rs = "" if key == "base" else f"{(r['base'] - kwh) * DAYS * TARIFF:,.0f}"
        co2 = "" if key == "base" else f"{(r['base'] - kwh) * DAYS * EF / 1000:.1f}"
        print(f"{name:34s}{kwh:9.1f}{kwh / vol:12.3f}{sv:>9s}{rs:>10s}{co2:>10s}")


def report_sweep():
    print("\nSWEEP: saving (%) vs fixed-speed throttled baseline  [constant-pressure / proportional]")
    print("rows: peak demand as % of rated flow (lower = pump more oversized); columns: static lift of the plant")
    lifts = (5.0, 10.0, 15.0, 20.0)
    print(f"{'peak demand':>12s}" + "".join(f"{('lift ' + str(int(h)) + ' m'):>17s}" for h in lifts))
    allc, allp = [], []
    for pf in (0.60, 0.70, 0.80, 0.90, 0.95):
        row = f"{int(pf * 100):>11d}%"
        for hs in lifts:
            try:
                r = evaluate(peak_frac=pf, h_static=hs)
                c = 100 * (r["base"] - r["const"]) / r["base"]
                p = 100 * (r["base"] - r["prop"]) / r["base"]
                allc.append(c)
                allp.append(p)
                row += f"{c:8.1f} / {p:4.1f}  "
            except ValueError:
                row += f"{'n/a':>17s}"
        print(row)
    print(f"\nRange across the sweep: constant-pressure {min(allc):.0f}-{max(allc):.0f}%, proportional {min(allp):.0f}-{max(allp):.0f}%")
    print("\nMargin sensitivity at 90% peak demand, 10 m lift (constant / proportional):")
    for m in (0.0, 0.05, 0.10):
        r = evaluate(margin=m)
        print(f"  margin {int(m * 100):>2d}%: {100 * (r['base'] - r['const']) / r['base']:.1f}% / {100 * (r['base'] - r['prop']) / r['base']:.1f}%")


if __name__ == "__main__":
    report_main()
    report_sweep()
