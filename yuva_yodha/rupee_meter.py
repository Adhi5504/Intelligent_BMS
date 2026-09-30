"""Rupee-meter cost model for a motor/pump (Yuva Yodha, Challenge 04).

All defaults are ILLUSTRATIVE ASSUMPTIONS. Replace them with values measured on
the rig or taken from a real SME (tariff bill, maintenance invoice, run hours).
"""
from dataclasses import dataclass


@dataclass
class Pump:
    shaft_kw: float = 12.0          # mechanical load on the shaft
    motor_eff: float = 0.90
    hours_per_year: float = 6000.0
    tariff: float = 8.0             # Rs/kWh (check the SME's bill)
    wear_loss: float = 0.08         # extra power drawn vs healthy baseline (fraction)
    wear_growth_per_day: float = 0.0002  # wear_loss increases by this much each day
    repair_parts_labour: float = 40000.0
    planned_downtime_hours: float = 8.0
    downtime_cost_per_hour: float = 5000.0
    unplanned_failure_cost: float = 300000.0
    monthly_fail_prob: float = 0.15  # from the vibration-based risk model
    emission_factor: float = 0.71    # kg CO2/kWh - VERIFY against the current CEA value
    vfd_saving_fraction: float = 0.30  # conservative average from speed control
    vfd_cost: float = 120000.0       # get a real quote

    @property
    def input_kw(self):
        return self.shaft_kw / self.motor_eff

    @property
    def repair_cost(self):
        return self.repair_parts_labour + self.planned_downtime_hours * self.downtime_cost_per_hour


def report(p: Pump) -> dict:
    hours_per_day = p.hours_per_year / 365
    annual_kwh = p.input_kw * p.hours_per_year
    annual_cost = annual_kwh * p.tariff

    # today's silent waste
    waste_kwh_day = p.input_kw * p.wear_loss * hours_per_day
    waste_rs_day = waste_kwh_day * p.tariff
    risk_rs_day = p.monthly_fail_prob / 30 * p.unplanned_failure_cost

    # waiting cost accumulates (wear keeps growing); repair when it reaches the repair bill
    def waiting_cost(days, with_risk):
        total = 0.0
        for t in range(days):
            wear = p.wear_loss + p.wear_growth_per_day * t
            total += p.input_kw * wear * hours_per_day * p.tariff
            if with_risk:
                total += risk_rs_day
        return total

    def breakeven(with_risk):
        for d in range(1, 3651):
            if waiting_cost(d, with_risk) >= p.repair_cost:
                return d
        return None

    vfd_kwh = annual_kwh * p.vfd_saving_fraction
    vfd_rs = vfd_kwh * p.tariff
    return {
        "annual_kwh": annual_kwh,
        "annual_cost_rs": annual_cost,
        "waste_rs_per_day": waste_rs_day,
        "risk_rs_per_day": risk_rs_day,
        "repair_cost_rs": p.repair_cost,
        "repair_by_days_energy_only": breakeven(False),
        "repair_by_days_with_risk": breakeven(True),
        "vfd_saving_kwh": vfd_kwh,
        "vfd_saving_rs": vfd_rs,
        "vfd_payback_months": p.vfd_cost / vfd_rs * 12,
        "vfd_co2_kg": vfd_kwh * p.emission_factor,
    }


if __name__ == "__main__":
    for k, v in report(Pump()).items():
        print(f"{k:28s} {v:,.1f}" if isinstance(v, float) else f"{k:28s} {v}")
