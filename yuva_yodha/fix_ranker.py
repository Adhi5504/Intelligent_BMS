"""Fix ranker: rank retrofit/maintenance options by cost and by payback.

ALL NUMBERS ARE PLACEHOLDER ASSUMPTIONS for a 15 kW-class throttled pump
(about Rs 6.4 lakh/year of electricity). Replace costs with dealer quotes and
savings with the audit's own estimates before quoting anything.

Savings are NOT additive: some fixes address the same waste (for example
impeller trimming and a VFD). The real tool must re-rank after each fix.
"""
from dataclasses import dataclass

ANNUAL_ENERGY_RS = 640_000      # 13.3 kW x 6,000 h x Rs 8/kWh


@dataclass
class Fix:
    name: str
    trigger: str
    cost: float                 # Rs, typical (assumption)
    energy_frac: float          # share of annual energy bill recovered (assumption)
    risk_rs: float              # expected yearly failure cost avoided (assumption)
    basis: str                  # where the saving figure comes from


FIXES = [
    Fix("Bearing grease / lubrication", "bearing temperature or vibration rising",
        300, 0.005, 10_000, "assumed; mainly failure prevention, tiny energy gain"),
    Fix("Clean strainer / suction line", "power and pressure drifting at same demand",
        500, 0.03, 2_000, "assumed"),
    Fix("Align coupling, tighten foundation", "1x/2x vibration pattern",
        1_500, 0.01, 8_000, "assumed"),
    Fix("Trim impeller (oversized pump)", "steady load, throttled valve",
        6_000, 0.10, 0, "assumed; not yet modelled"),
    Fix("Replace wear rings / refurbish impeller", "head and efficiency below new curve",
        20_000, 0.06, 5_000, "assumed"),
    Fix("IE3 motor replacement", "old or rewound motor",
        45_000, 0.05, 0, "BEE-linked sources quote about 5-6%"),
    Fix("Speed control (VFD) + kit", "variable demand with throttling",
        135_000, 0.30, 0, "simulated (pump_sim.py), generic pump"),
]


def rows():
    out = []
    for f in FIXES:
        saving = ANNUAL_ENERGY_RS * f.energy_frac + f.risk_rs
        payback_m = f.cost / saving * 12 if saving > 0 else float("inf")
        out.append((f, saving, payback_m))
    return out


def show(title, data):
    print(f"\n{title}")
    print(f"{'#':>2} {'Fix':42s} {'Cost Rs':>9} {'Saving Rs/yr':>13} {'Payback (months)':>17}")
    for i, (f, s, p) in enumerate(data, 1):
        print(f"{i:>2} {f.name:42s} {f.cost:9,.0f} {s:13,.0f} {p:17.1f}")


if __name__ == "__main__":
    data = rows()
    show("Ranked by COST (cheapest first)", sorted(data, key=lambda r: r[0].cost))
    show("Ranked by PAYBACK (fastest first)", sorted(data, key=lambda r: r[2]))
    print("\nTiers by cost: <= Rs 2,000 do now | Rs 2,000-25,000 plan | > Rs 25,000 decide with a quote")
