import { Printer, X } from "lucide-react";
import { CAPEX_HIGH, CAPEX_LOW, DEFAULTS, evaluate, paybackMonths } from "../utils/pumpModel";
import { inr, num } from "../utils/format";
import { modeLabel, useMode } from "../utils/modeContext";
import { mvRows } from "./pages/Verification";

export function ReportSheet() {
  const { mode, reportOpen, setReportOpen } = useMode();
  if (!reportOpen) return null;
  const r = evaluate(DEFAULTS);
  const mv = mvRows(mode);
  if (!r.ok || !mv) return null;
  const today = new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "long", year: "numeric" });
  return (
    <div className="report-overlay fixed inset-0 z-50 overflow-auto bg-black/80 p-4 print:p-0">
      <div className="report-sheet mx-auto max-w-3xl rounded-lg bg-white p-8 text-[13px] leading-relaxed text-slate-800 shadow-2xl">
        <div className="no-print mb-4 flex justify-end gap-2">
          <button onClick={() => window.print()} className="flex items-center gap-1.5 rounded-lg bg-[#0C1E3C] px-3 py-1.5 text-sm font-semibold text-white"><Printer size={14} />Print / Save as PDF</button>
          <button onClick={() => setReportOpen(false)} className="flex items-center gap-1.5 rounded-lg border border-slate-300 px-3 py-1.5 text-sm"><X size={14} />Close</button>
        </div>
        <div className="flex items-start justify-between border-b-4 border-[#3DCD58] pb-3">
          <div>
            <div className="text-2xl font-extrabold text-[#0C1E3C]">PumpRupee · Executive Audit Report</div>
            <div className="text-slate-600">Pump: Grundfos NB 65-160/157, 11 kW, IE3 · {today}</div>
          </div>
          <div className="text-right text-xs text-slate-600"><div className="font-semibold text-[#0C1E3C]">Schneider Electric Yuva Yodha 2026</div><div>Smart Manufacturing · Team ANS_4X</div></div>
        </div>
        <div className="my-3 rounded border border-amber-400 bg-amber-50 p-2 text-xs text-amber-900"><b>SIMULATED RESULTS.</b> Based on the Grundfos NB 65-160/157 curve fits and stated assumptions. No lab or field measurements. Prices are indicative online prices, not quotes.</div>

        <h2 className="mt-3 text-base font-bold text-[#0C1E3C]">1. Headline ({modeLabel(mode)})</h2>
        <ul className="list-disc pl-5">
          <li>Recoverable saving vs throttling: <b>{inr(r.savingRsYr[mode])}/year</b> ({num(r.savingPct[mode])}% of energy).</li>
          <li>SEC: {num(r.sec.base, 3)} → <b>{num(r.sec[mode], 3)} kWh/m³</b> (₹{num(r.rsPerM3.base, 2)} → ₹{num(r.rsPerM3[mode], 2)} per m³).</li>
          <li>CO₂ avoided: <b>{num(r.co2TYr[mode])} t/year</b> (0.710 kg/kWh, CEA v21.0).</li>
          <li>VFD payback: <b>{num(paybackMonths(CAPEX_LOW, r.savingRsYr[mode]))}–{num(paybackMonths(CAPEX_HIGH, r.savingRsYr[mode]))} months</b> for a total of {inr(CAPEX_LOW)}–{inr(CAPEX_HIGH)} (VFD + assumed ₹15,000 install).</li>
        </ul>

        <h2 className="mt-3 text-base font-bold text-[#0C1E3C]">2. Recommended actions, cheapest first</h2>
        <ol className="list-decimal pl-5">
          <li>Check the strainer, lubrication and alignment (cheap, small share of waste).</li>
          <li>Decide on speed control (VFD) or impeller trim: the valve is 83–93% of the simulated waste.</li>
          <li>If a VFD is fitted, set the constant-pressure setpoint to <b>{num(r.hConst)} m ({num(r.hConst / 10.197, 2)} bar)</b>.</li>
          <li>Re-measure for 7–14 days and verify the saving as SEC.</li>
        </ol>

        <h2 className="mt-3 text-base font-bold text-[#0C1E3C]">3. Before / after (simulated)</h2>
        <table className="w-full border-collapse text-xs">
          <thead><tr className="bg-slate-100 text-left"><th className="border p-1.5">Metric</th><th className="border p-1.5 text-right">Before</th><th className="border p-1.5 text-right">After</th><th className="border p-1.5 text-right">Change</th></tr></thead>
          <tbody>{mv.rows.map((x) => <tr key={x.k}><td className="border p-1.5">{x.k}</td><td className="border p-1.5 text-right">{x.before}</td><td className="border p-1.5 text-right">{x.after}</td><td className="border p-1.5 text-right">{x.delta}</td></tr>)}</tbody>
        </table>

        <h2 className="mt-3 text-base font-bold text-[#0C1E3C]">4. Assumptions</h2>
        <p>Static lift {DEFAULTS.hStatic} m · head margin 5% · {DEFAULTS.hoursPerDay} h/day · {DEFAULTS.daysPerYear} days/yr · ₹{DEFAULTS.tariff}/kWh · VFD efficiency 0.97 · peak demand 90% of rated flow (114 m³/h) · assumed demand profile. Range across simulated cases: 8–33% (constant) and 15–45% (proportional); an energy-audit practitioner reports 5–40% in practice.</p>

        <h2 className="mt-3 text-base font-bold text-[#0C1E3C]">5. Honest limits</h2>
        <ul className="list-disc pl-5">
          <li>Simulation only; no lab or field data and no real quotes.</li>
          <li>About ±3 points forecast accuracy only with a measured system curve; otherwise about ±10.</li>
          <li>The system-curve fit uses the same form as the simulated plant, so it is optimistic.</li>
          <li>Single pump, steady state. Out of scope: parallel pumps, closed loops, pumps already on drives, minimum-flow and NPSH checks, control dynamics.</li>
        </ul>
        <div className="mt-6 grid grid-cols-2 gap-8 text-xs text-slate-600"><div className="border-t border-slate-400 pt-1">Audited by</div><div className="border-t border-slate-400 pt-1">Reviewed by (plant)</div></div>
      </div>
    </div>
  );
}
