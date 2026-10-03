import { ClipboardCheck, FileDown } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Badge } from "../ui/Badge";
import { Card, CardTitle } from "../ui/Card";
import { SimNote } from "../ui/SimNote";
import { DEFAULTS, EF, evaluate } from "../../utils/pumpModel";
import { inr, num } from "../../utils/format";
import { modeLabel, useMode } from "../../utils/modeContext";

export function mvRows(mode: "const" | "prop") {
  const r = evaluate(DEFAULTS);
  if (!r.ok) return null;
  const yr = DEFAULTS.daysPerYear, t = DEFAULTS.tariff;
  const bKwhYr = r.kwhDay.base * yr, aKwhYr = r.kwhDay[mode] * yr;
  const rows: { k: string; before: string; after: string; delta: string }[] = [
    { k: "Delivered volume (m³/day), normalised", before: num(r.volPerDay, 0), after: num(r.volPerDay, 0), delta: "same" },
    { k: "Electricity (kWh/day)", before: num(r.kwhDay.base), after: num(r.kwhDay[mode]), delta: `−${num(r.kwhDay.base - r.kwhDay[mode])}` },
    { k: "SEC (kWh/m³)", before: num(r.sec.base, 3), after: num(r.sec[mode], 3), delta: `−${num(r.sec.base - r.sec[mode], 3)}` },
    { k: "Running cost (₹/m³)", before: num(r.rsPerM3.base, 2), after: num(r.rsPerM3[mode], 2), delta: `−${num(r.rsPerM3.base - r.rsPerM3[mode], 2)}` },
    { k: "Annual electricity (kWh)", before: Math.round(bKwhYr).toLocaleString("en-IN"), after: Math.round(aKwhYr).toLocaleString("en-IN"), delta: `−${Math.round(bKwhYr - aKwhYr).toLocaleString("en-IN")}` },
    { k: "Annual electricity cost", before: inr(bKwhYr * t), after: inr(aKwhYr * t), delta: `−${inr((bKwhYr - aKwhYr) * t)}` },
    { k: "Annual CO₂ (t, 0.710 kg/kWh)", before: num((bKwhYr * EF) / 1000), after: num((aKwhYr * EF) / 1000), delta: `−${num(((bKwhYr - aKwhYr) * EF) / 1000)}` },
  ];
  return { r, rows };
}

export function Verification() {
  const { mode, openReport } = useMode();
  const mv = mvRows(mode);
  if (!mv) return null;
  const { r, rows } = mv;
  const bars = [{ n: "Before: fixed speed + throttle", v: r.kwhDay.base, c: "#EF4444" }, { n: `After: VFD, ${modeLabel(mode).toLowerCase()}`, v: r.kwhDay[mode], c: "#3DCD58" }];
  return (
    <div className="space-y-4">
      <SimNote><b>Simulated before/after.</b> No post-fix measurement exists yet. This table shows how PumpRupee would report a verified saving, using the simulated base case: same delivered volume, fixed speed + throttle vs a VFD in {modeLabel(mode).toLowerCase()} mode.</SimNote>
      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardTitle icon={<ClipboardCheck size={14} />} right={<Badge variant="amber">SIMULATED</Badge>}>Measurement &amp; verification (IPMVP-style)</CardTitle>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-green-300 text-left text-xs uppercase tracking-wide text-slate-500"><th className="py-2 pr-3">Metric</th><th className="px-3 text-right">Before</th><th className="px-3 text-right">After</th><th className="pl-3 text-right">Change</th></tr></thead>
              <tbody>
                {rows.map((x) => (
                  <tr key={x.k} className="border-b border-green-100">
                    <td className="py-2 pr-3 text-slate-700">{x.k}</td><td className="px-3 text-right font-mono text-slate-800">{x.before}</td>
                    <td className="px-3 text-right font-mono text-slate-900">{x.after}</td><td className="pl-3 text-right font-mono text-brandtext">{x.delta}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bars} layout="vertical" margin={{ top: 0, right: 40, left: 10, bottom: 0 }}>
                <CartesianGrid horizontal={false} /><XAxis type="number" hide domain={[0, 150]} /><YAxis type="category" dataKey="n" width={210} tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#FFFFFF", border: "1px solid #244574", borderRadius: 8, fontSize: 12 }} formatter={(v: any) => `${Number(v).toFixed(1)} kWh/day`} />
                <Bar dataKey="v" radius={[0, 4, 4, 0]}>{bars.map((b) => <Cell key={b.n} fill={b.c} />)}<LabelList dataKey="v" position="right" formatter={(v: any) => `${Number(v).toFixed(1)}`} style={{ fill: "#1e293b", fontSize: 12 }} /></Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <div className="space-y-4 lg:col-span-2">
          <Card>
            <CardTitle>How the saving would be verified</CardTitle>
            <ul className="space-y-2 text-xs text-slate-700">
              {[["Measurement boundary", "Motor input power at the starter + discharge (and process-side) pressure"], ["Baseline period", "7–14 days logged before the fix"], ["Reporting period", "7–14 days logged after the VFD or impeller trim"], ["Normalising variable", "Volume pumped: compare SEC (kWh/m³), not raw kWh"], ["Adjustments", "Tariff, demand mix and non-routine events documented"], ["Approach", "IPMVP-style retrofit isolation. A framing for the audit, not a certification"]].map(([k, v]) => (
                <li key={k} className="flex gap-2"><span className="w-36 shrink-0 font-semibold text-slate-800">{k}</span><span>{v}</span></li>
              ))}
            </ul>
          </Card>
          <Card>
            <CardTitle>Verification status</CardTitle>
            <ul className="space-y-1.5 text-xs">
              {[["Baseline logs", "Simulated", "amber"], ["Post-fix logs", "Not yet collected", "red"], ["Normalisation (SEC)", "Designed", "slate"], ["Independent reference meter check", "To be tested on the bench", "red"]].map(([k, v, c]) => (
                <li key={k} className="flex items-center justify-between"><span className="text-slate-700">{k}</span><Badge variant={c as any}>{v}</Badge></li>
              ))}
            </ul>
          </Card>
          <button onClick={openReport} className="flex w-full items-center justify-center gap-2 rounded-xl bg-brandtext px-4 py-3 text-sm font-bold text-white shadow hover:bg-[#14692b]">
            <FileDown size={16} />Export Executive Audit Report
          </button>
        </div>
      </div>
    </div>
  );
}
