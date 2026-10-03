import { describe, expect, it } from "vitest";
import { CAPEX_HIGH, CAPEX_LOW, DATA, DEFAULTS, evaluate, paybackMonths } from "../src/utils/pumpModel";
import { analyse, parseCsv, sampleCsv } from "../src/utils/calibrate";
import { inr } from "../src/utils/format";

describe("pump model reproduces the Python simulation (real_pump_sim.py)", () => {
  const r = evaluate(DEFAULTS);
  it("base case savings", () => {
    if (!r.ok) throw new Error("infeasible");
    expect(r.savingPct.const).toBeCloseTo(19.3, 1);
    expect(r.savingPct.prop).toBeCloseTo(35.5, 1);
    expect(Math.round(r.savingRsYr.const)).toBe(69292);
    expect(Math.round(r.savingRsYr.prop)).toBe(127178);
    expect(r.co2TYr.const).toBeCloseTo(6.1, 1);
    expect(r.co2TYr.prop).toBeCloseTo(11.3, 1);
    expect(r.hConst).toBeCloseTo(24.17, 2);
  });
  it("paybacks", () => {
    if (!r.ok) throw new Error("infeasible");
    expect(paybackMonths(CAPEX_LOW, r.savingRsYr.const)).toBeCloseTo(8.7, 1);
    expect(paybackMonths(CAPEX_LOW, r.savingRsYr.prop)).toBeCloseTo(4.7, 1);
    expect(paybackMonths(CAPEX_HIGH, r.savingRsYr.const)).toBeCloseTo(18.9, 1);
    expect(paybackMonths(CAPEX_HIGH, r.savingRsYr.prop)).toBeCloseTo(10.3, 1);
  });
  it("right-sized pump saves little", () => {
    const p = evaluate({ ...DEFAULTS, peakFrac: 0.95, hStatic: 20 });
    if (!p.ok) throw new Error("infeasible");
    expect(Math.round(p.savingRsYr.const)).toBe(28526);
  });
  it("matches the reference numbers from Python in generated.json", () => {
    if (!r.ok) throw new Error("infeasible");
    expect(r.kwhDay.base).toBeCloseTo(DATA.reference.base, 3);
    expect(r.kwhDay.prop).toBeCloseTo(DATA.reference.prop, 3);
  });
});

describe("Indian number format", () => {
  it("groups like 1,27,178", () => { expect(inr(127178)).toBe("₹1,27,178"); expect(inr(69292)).toBe("₹69,292"); expect(inr(692920)).toBe("₹6,92,920"); });
});

describe("CSV upload and calibration", () => {
  const csv = sampleCsv(DATA.telemetry.records);
  it("parses the sample", () => { const p = parseCsv(csv); expect(p.rows.length).toBe(224); expect(p.skipped).toBe(0); });
  it("reports a missing power column", () => { expect(parseCsv("a,b\n1,2").rows.length).toBe(0); });
  it("accepts bare numeric columns", () => { expect(parseCsv("9.5,3.4,0.5\n9.1,3.5,0.5").rows.length).toBe(2); });
  it("recovers the hidden pump scales and the saving", () => {
    const res = analyse(parseCsv(csv).rows);
    if (!res.ok) throw new Error(res.reason);
    expect(Math.abs(res.cal.sh - DATA.telemetry.truth.sh)).toBeLessThanOrEqual(0.02);
    expect(Math.abs(res.cal.sp - DATA.telemetry.truth.sp)).toBeLessThanOrEqual(0.03);
    expect(Math.abs(res.savingPct - DATA.telemetry.truth.saving)).toBeLessThan(3);
  });
  it("rejects too few rows", () => { const r2 = analyse(parseCsv("power_kw,discharge_bar\n9,3\n9,3").rows); expect(r2.ok).toBe(false); });
});
