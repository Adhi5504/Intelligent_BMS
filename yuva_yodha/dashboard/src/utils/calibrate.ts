// Browser-side calibration of the reference pump (Grundfos NB 65-160/157) from uploaded logs. Port of the profile-likelihood
// idea in learning_layer.py: fit a head scale s_h and a power scale s_p, infer flow per record, forecast the VFD saving.
// Runs entirely in the browser: nothing is uploaded to a server. SIMULATION-GRADE: the system curve is ASSUMED (static lift + margin).
import { BAR_TO_M, ETA_VFD, H_RATED, N_MIN, Q_MAX_FIT, Q_RATED, etaMotor, hNom, p1FixedSpeed, p2Nom } from "./pumpModel";

export interface LogRow { powerKw: number; pdBar: number; psBar: number | null }
export interface ParseResult { rows: LogRow[]; skipped: number; notes: string[] }

const splitLine = (l: string) => l.split(/[,;\t]/).map((c) => c.trim().replace(/^"|"$/g, ""));

/** Accepts a header row (power_kw / kw / p1, discharge / pd / p2, suction / ps) or three/two bare numeric columns. */
export function parseCsv(text: string): ParseResult {
  const lines = text.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  const notes: string[] = [];
  if (!lines.length) return { rows: [], skipped: 0, notes: ["The file is empty."] };
  let ip = 0, id = 1, is = 2, start = 0;
  const first = splitLine(lines[0]);
  if (first.some((c) => isNaN(parseFloat(c)))) {
    const low = first.map((c) => c.toLowerCase());
    const find = (re: RegExp) => low.findIndex((c) => re.test(c));
    const p = find(/power|kw|p1_?kw|p_el/), d = find(/disch|^pd|p2_?bar|pressure/), s = find(/suct|^ps/);
    if (p < 0 || d < 0) return { rows: [], skipped: lines.length, notes: ["Could not find a power column (power_kw) and a discharge pressure column (discharge_bar) in the header."] };
    ip = p; id = d; is = s;
    start = 1;
  } else notes.push("No header found: assuming columns power_kw, discharge_bar, suction_bar (optional).");
  const rows: LogRow[] = [];
  let skipped = 0;
  for (let i = start; i < lines.length; i++) {
    const c = splitLine(lines[i]);
    const power = parseFloat(c[ip]), pd = parseFloat(c[id]), ps = is >= 0 && c[is] !== undefined ? parseFloat(c[is]) : NaN;
    if (!isFinite(power) || !isFinite(pd) || power <= 0.5 || power > 30 || pd < 0 || pd > 16) { skipped++; continue; }
    rows.push({ powerKw: power, pdBar: pd, psBar: isFinite(ps) ? ps : null });
  }
  if (skipped) notes.push(`${skipped} row(s) skipped (non-numeric or outside 0.5–30 kW / 0–16 bar).`);
  return { rows, skipped, notes };
}

const QG: number[] = [];
for (let q = 40; q <= 130; q++) QG.push(q);
const SH = Array.from({ length: 25 }, (_, i) => Math.round((0.88 + 0.01 * i) * 100) / 100);
const SP = Array.from({ length: 31 }, (_, i) => Math.round((0.92 + 0.01 * i) * 100) / 100);
const H0 = QG.map(hNom);
const P1T = SP.map((sp) => QG.map((q) => p1FixedSpeed(q, sp)));

export interface Calibration { sh: number; sp: number; qInferred: number[]; heads: number[]; used: number }

export function calibrate(rows: LogRow[], psDefault = 0.5, maxUse = 300): Calibration {
  const heads = rows.map((r) => (r.pdBar - (r.psBar ?? psDefault)) * BAR_TO_M);
  const step = Math.max(1, Math.floor(rows.length / maxUse));
  const idx = rows.map((_, i) => i).filter((i) => i % step === 0);
  let best = Infinity, bi = 0, bj = 0;
  for (let si = 0; si < SH.length; si++) {
    for (let pj = 0; pj < SP.length; pj++) {
      let tot = 0;
      for (const i of idx) {
        const hm = heads[i], pm = rows[i].powerKw;
        let m = Infinity;
        for (let k = 0; k < QG.length; k++) {
          const a = (SH[si] * H0[k] - hm) / hm, b = (P1T[pj][k] - pm) / pm;
          const c = a * a + b * b;
          if (c < m) m = c;
        }
        tot += m;
      }
      if (tot < best) { best = tot; bi = si; bj = pj; }
    }
  }
  const qInferred = rows.map((r, i) => {
    let m = Infinity, qb = QG[0];
    for (let k = 0; k < QG.length; k++) {
      const a = (SH[bi] * H0[k] - heads[i]) / heads[i], b = (P1T[bj][k] - r.powerKw) / r.powerKw;
      const c = a * a + b * b;
      if (c < m) { m = c; qb = QG[k]; }
    }
    return qb;
  });
  return { sh: SH[bi], sp: SP[bj], qInferred, heads, used: idx.length };
}

/** speed ratio with a head-scaled pump: r^2 * sh * H(q/r) = head */
function speedScaled(q: number, sh: number, head: number): number | null {
  const f = (r: number) => { const qe = q / r; return qe > Q_MAX_FIT ? -1e9 : r * r * sh * hNom(qe) - head; };
  let lo = N_MIN, hi = 1;
  if (f(hi) < 0) return null;
  if (f(lo) > 0) return lo;
  for (let i = 0; i < 50; i++) { const mid = (lo + hi) / 2; if (f(mid) > 0) hi = mid; else lo = mid; }
  return hi;
}

export interface UploadInputs { psDefault: number; hStatic: number; margin: number; hoursPerDay: number; daysPerYear: number; tariff: number; capex: number }
export const UPLOAD_DEFAULTS: UploadInputs = { psDefault: 0.5, hStatic: 10, margin: 0.05, hoursPerDay: 16, daysPerYear: 300, tariff: 8, capex: 50200 };

export interface UploadResult {
  ok: true; cal: Calibration; n: number; meanPowerKw: number; meanQ: number; sec: number; rsPerM3: number;
  savingPct: number; savingRsYr: number; savingKwhYr: number; co2TYr: number; paybackMonths: number; skippedInfeasible: number; baseRsYr: number;
}
export interface UploadError { ok: false; reason: string }

export function analyse(rows: LogRow[], inp: UploadInputs = UPLOAD_DEFAULTS): UploadResult | UploadError {
  if (rows.length < 16) return { ok: false, reason: "Need at least 16 valid rows (one day of hourly records, or more). 7–14 days is recommended." };
  const cal = calibrate(rows, inp.psDefault);
  const k = (H_RATED - inp.hStatic) / (Q_RATED * Q_RATED);
  let base = 0, varp = 0, infeasible = 0;
  rows.forEach((r, i) => {
    const q = cal.qInferred[i];
    const head = (inp.hStatic + k * q * q) * (1 + inp.margin);
    const rr = speedScaled(q, cal.sh, head);
    if (rr == null) { infeasible++; return; }
    const p2 = cal.sp * Math.pow(rr, 3) * p2Nom(q / rr);
    varp += p2 / etaMotor(p2) / ETA_VFD;
    base += r.powerKw;
  });
  if (!base) return { ok: false, reason: "The calibrated pump cannot meet the inferred duty at this static lift. Lower the static lift or check the columns." };
  const savingPct = (100 * (base - varp)) / base;
  const meanPowerKw = rows.reduce((a, r) => a + r.powerKw, 0) / rows.length;
  const meanQ = cal.qInferred.reduce((a, b) => a + b, 0) / rows.length;
  const hours = inp.hoursPerDay * inp.daysPerYear;
  const baseKwhYr = meanPowerKw * hours;
  const savingKwhYr = (baseKwhYr * Math.max(0, savingPct)) / 100;
  const savingRsYr = savingKwhYr * inp.tariff;
  return {
    ok: true, cal, n: rows.length, meanPowerKw, meanQ, sec: meanPowerKw / meanQ, rsPerM3: (meanPowerKw / meanQ) * inp.tariff,
    savingPct, savingRsYr, savingKwhYr, co2TYr: (savingKwhYr * 0.71) / 1000, paybackMonths: savingRsYr > 0 ? (inp.capex / savingRsYr) * 12 : Infinity,
    skippedInfeasible: infeasible, baseRsYr: baseKwhYr * inp.tariff,
  };
}

export function sampleCsv(records: { p1: number; pd: number; ps: number }[]): string {
  return "power_kw,discharge_bar,suction_bar\n" + records.map((r) => `${r.p1},${r.pd},${r.ps}`).join("\n") + "\n";
}
