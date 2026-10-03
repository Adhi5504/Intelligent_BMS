// TypeScript port of yuva_yodha/real_pump_sim.py (Grundfos NB 65-160/157). SIMULATION ONLY.
// Pump curves are cubic FITS to the manufacturer table (coefficients come from generated.json), not manufacturer data.
import raw from "../data/generated.json";
import type { GeneratedData } from "../types";

export const DATA = raw as unknown as GeneratedData;
const P = DATA.pump;

export const RHO = 998.2;
export const G = 9.81;
export const Q_RATED = P.qRated;       // 114 m3/h
export const H_RATED = P.hRated;       // 26.07 m (Product Center readout; datasheet prints 26.5 m)
export const Q_MIN_FIT = P.qMin;       // 10
export const Q_MAX_FIT = P.qMax;       // 130
export const ETA_VFD = P.etaVfd;       // 0.97 (assumed)
export const N_MIN = P.nMin;           // 0.5 (assumed)
export const EF = P.ef;                // 0.710 kg CO2/kWh (CEA v21.0)
export const PROFILE = P.profile;      // demand profile, fractions of peak (assumed)
export const BAR_TO_M = 10.197;

export const poly = (coef: number[], x: number) => coef.reduce((s, c, i) => s + c * Math.pow(x / 100, i), 0);
export const hNom = (q: number) => poly(P.hCoef, q);
export const p2Nom = (q: number) => poly(P.p2Coef, q);

export function etaMotor(p2: number): number {
  const m = P.motor;
  if (p2 <= m[0][0]) return m[0][1];
  if (p2 >= m[m.length - 1][0]) return m[m.length - 1][1];
  for (let i = 0; i < m.length - 1; i++) {
    const [x0, y0] = m[i], [x1, y1] = m[i + 1];
    if (p2 >= x0 && p2 <= x1) return y0 + ((y1 - y0) * (p2 - x0)) / (x1 - x0);
  }
  return m[m.length - 1][1];
}

/** speed ratio r with r^2 * H(q/r) = head; null if the pump cannot deliver it */
export function speedForHead(q: number, head: number): number | null {
  const f = (r: number) => {
    const qe = q / r;
    return qe > Q_MAX_FIT ? -1e9 : r * r * hNom(qe) - head;
  };
  let lo = N_MIN, hi = 1.0;
  if (f(hi) < 0) return null;
  if (f(lo) > 0) return lo;
  for (let i = 0; i < 60; i++) {
    const mid = (lo + hi) / 2;
    if (f(mid) > 0) hi = mid; else lo = mid;
  }
  return hi;
}

/** electrical input power (kW) at fixed speed; ah/ap scale head/power for a "real pump differs from datasheet" case */
export function p1FixedSpeed(q: number, ap = 1): number {
  const p2 = ap * p2Nom(q);
  return p2 / etaMotor(p2);
}
export function p1Variable(q: number, r: number): number {
  const p2 = Math.pow(r, 3) * p2Nom(q / r);
  return p2 / etaMotor(p2) / ETA_VFD;
}

export interface ScenarioInput {
  peakFrac: number;       // peak demand as a fraction of rated flow
  hStatic: number;        // static lift, m
  margin: number;         // head margin, e.g. 0.05
  hoursPerDay: number;
  daysPerYear: number;
  tariff: number;         // Rs/kWh
}
export const DEFAULTS: ScenarioInput = { peakFrac: 0.9, hStatic: 10, margin: 0.05, hoursPerDay: 16, daysPerYear: 300, tariff: 8 };

export interface ScenarioResult {
  ok: true;
  qs: number[];
  hConst: number;                       // recommended constant-pressure setpoint (m)
  volPerDay: number;                    // m3/day
  kwhDay: { base: number; const: number; prop: number };
  sec: { base: number; const: number; prop: number };            // kWh/m3
  rsPerM3: { base: number; const: number; prop: number };
  savingPct: { const: number; prop: number };
  savingRsYr: { const: number; prop: number };
  savingKwhYr: { const: number; prop: number };
  co2TYr: { const: number; prop: number };
  baseRsYr: number;
}
export interface ScenarioError { ok: false; reason: string }

export function evaluate(inp: ScenarioInput = DEFAULTS): ScenarioResult | ScenarioError {
  const k = (H_RATED - inp.hStatic) / (Q_RATED * Q_RATED);
  const hSys = (q: number) => inp.hStatic + k * q * q;
  const qs = PROFILE.map((f) => f * inp.peakFrac * Q_RATED);
  if (Math.min(...qs) < Q_MIN_FIT) return { ok: false, reason: "Off-peak demand falls below the fitted range (10 m³/h). Raise average demand." };
  for (const q of qs) if (hNom(q) < hSys(q) - 1e-9) return { ok: false, reason: "At this lift and flow the pump cannot meet the demand at full speed." };
  const hConst = hSys(Math.max(...qs)) * (1 + inp.margin);
  let base = 0, cst = 0, prp = 0;
  for (const q of qs) {
    base += p1FixedSpeed(q);
    const rc = speedForHead(q, hConst);
    const rp = speedForHead(q, hSys(q) * (1 + inp.margin));
    if (rc == null || rp == null) return { ok: false, reason: "The head margin pushes the setpoint above what the pump can deliver." };
    cst += p1Variable(q, rc);
    prp += p1Variable(q, rp);
  }
  const hourScale = inp.hoursPerDay / PROFILE.length;       // the profile has 16 hourly steps
  const vol = qs.reduce((a, b) => a + b, 0) * hourScale;
  const kwh = { base: base * hourScale, const: cst * hourScale, prop: prp * hourScale };
  const yrs = inp.daysPerYear;
  const sv = (key: "const" | "prop") => (kwh.base - kwh[key]) * yrs;
  return {
    ok: true, qs, hConst, volPerDay: vol, kwhDay: kwh,
    sec: { base: kwh.base / vol, const: kwh.const / vol, prop: kwh.prop / vol },
    rsPerM3: { base: (kwh.base / vol) * inp.tariff, const: (kwh.const / vol) * inp.tariff, prop: (kwh.prop / vol) * inp.tariff },
    savingPct: { const: (100 * (kwh.base - kwh.const)) / kwh.base, prop: (100 * (kwh.base - kwh.prop)) / kwh.base },
    savingRsYr: { const: sv("const") * inp.tariff, prop: sv("prop") * inp.tariff },
    savingKwhYr: { const: sv("const"), prop: sv("prop") },
    co2TYr: { const: (sv("const") * EF) / 1000, prop: (sv("prop") * EF) / 1000 },
    baseRsYr: kwh.base * yrs * inp.tariff,
  };
}

export const paybackMonths = (capex: number, savingPerYear: number) => (savingPerYear > 0 ? (capex / savingPerYear) * 12 : Infinity);

/** VFD cost range used in the deck: Rs 29,000-94,000 + assumed Rs 15,000 install, rounded to the paybacks in PRICES_AND_PAYBACK.md */
export const CAPEX_LOW = 50200;
export const CAPEX_HIGH = 109400;
