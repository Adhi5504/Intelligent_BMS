import { AlertTriangle, Banknote, CheckCircle2, Cpu, Gauge, Leaf, Timer, Wrench } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, LabelList } from "recharts";
import { Badge } from "../ui/Badge";
import { Card, CardTitle } from "../ui/Card";
import { SimNote } from "../ui/SimNote";
import { Stat } from "../ui/Stat";
import { Tip } from "../ui/Tip";
import { CAPEX_HIGH, CAPEX_LOW, DEFAULTS, evaluate, paybackMonths } from "../../utils/pumpModel";
import { inr, num } from "../../utils/format";
import { modeLabel, useMode } from "../../utils/modeContext";

export function Overview() {
  const { mode } = useMode();
  const r = evaluate(DEFAULTS);
  if (!r.ok) return null;
  const other = mode === "const" ? "prop" : "const";
  const pbLow = paybackMonths(CAPEX_LOW, r.savingRsYr[mode]);
  const pbHigh = paybackMonths(CAPEX_HIGH, r.savingRsYr[mode]);
  const pbLowC = paybackMonths(CAPEX_LOW, r.savingRsYr.const), pbLowP = paybackMonths(CAPEX_LOW, r.savingRsYr.prop);
  const pbHighC = paybackMonths(CAPEX_HIGH, r.savingRsYr.const), pbHighP = paybackMonths(CAPEX_HIGH, r.savingRsYr.prop);
  const secData = [
    { name: "Fixed speed", sec: r.sec.base, color: "#EF4444" },
    { name: "VFD const. P", sec: r.sec.const, color: mode === "const" ? "#3DCD58" : "#2f7d44" },
    { name: "VFD prop. P", sec: r.sec.prop, color: mode === "prop" ? "#3DCD58" : "#2f7d44" },
  ];

  return (
    <div className="space-y-4">
      <SimNote>
        <b>Simulated results.</b> Grundfos NB 65-160/157 curve fits, assumed 10 m static lift, 5% head margin, 16 h/day, 300 days/yr, ₹8/kWh, VFD efficiency 0.97, peak demand 90% of rated flow. No lab or field data exists yet.
      </SimNote>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Stat icon={<Banknote size={14} />} label="Recoverable saving with a VFD" accent="text-brand"
          value={`${inr(r.savingRsYr[mode])} / yr`}
          sub={<>{modeLabel(mode)} · {num(r.savingPct[mode])}% of energy. {modeLabel(other)}: {inr(r.savingRsYr[other])}/yr</>}
          tip={<Tip>This is the saving versus throttling at fixed speed, not the total electricity bill. Range across simulated cases: 8–33% (constant), 15–45% (proportional). An energy-audit practitioner reports 5–40% in practice.</Tip>} />
        <Stat icon={<Gauge size={14} />} label="Specific energy (SEC)"
          value={<span>{num(r.sec.base, 3)} <span className="text-slate-500">→</span> <span className="text-brandtext">{num(r.sec[mode], 3)}</span> <span className="text-sm font-medium text-slate-600">kWh/m³</span></span>}
          sub={<>₹{num(r.rsPerM3.base, 2)}/m³ → ₹{num(r.rsPerM3[mode], 2)}/m³ at ₹8/kWh</>}
          tip={<Tip>SEC = units of electricity per m³ pumped. Same delivered volume ({Math.round(r.volPerDay)} m³/day) in every case.</Tip>} />
        <Stat icon={<Leaf size={14} />} label="CO₂ reduction" accent="text-brand"
          value={`${num(r.co2TYr[mode])} t / yr`}
          sub={<>≈{Math.round(r.savingKwhYr[mode]).toLocaleString("en-IN")} kWh/yr at 0.710 kg CO₂/kWh (CEA v21.0). Range {num(r.co2TYr.const)}–{num(r.co2TYr.prop)} t</>} />
        <Stat icon={<Timer size={14} />} label="VFD payback" accent="text-slate-900"
          value={`${num(pbLow)}–${num(pbHigh)} months`}
          sub={<>{modeLabel(mode)}, VFD + install {inr(CAPEX_LOW)}–{inr(CAPEX_HIGH)}. Both modes: {num(Math.min(pbLowC, pbLowP))}–{num(Math.max(pbHighC, pbHighP))} mo</>}
          tip={<Tip>Payback = (VFD + install) ÷ annual saving. The low end uses the cheaper VFD listing, the high end the dearer one. Install cost ₹15,000 is an assumption. Prices are indicative online prices, not quotes.</Tip>} />
      </div>

      <Card className="border-brand/50">
        <CardTitle icon={<Wrench size={14} />} right={<Badge variant="green">Cheapest fix first</Badge>}>Recommended action order for this pump</CardTitle>
        <ol className="grid gap-3 md:grid-cols-3">
          {[
            { n: 1, t: "Check strainer, grease, alignment", d: "Cheap fixes that pay back in weeks but address a small share of the waste. A clog is invisible to power + pressure alone; one process-side pressure sensor reveals about ₹6,000–6,600/yr of misattributed waste.", b: "Small share, low cost" },
            { n: 2, t: "Decide on speed control or impeller trim", d: `The valve is 83–93% of the simulated waste. A VFD is the main lever: ${inr(r.savingRsYr[mode])}/yr in ${modeLabel(mode).toLowerCase()} mode (simulated). Impeller trim cost is not estimated.`, b: "Largest saving" },
            { n: 3, t: `If a VFD is fitted: set the constant-pressure setpoint to ${num(r.hConst)} m (${num(r.hConst / 10.197, 2)} bar)`, d: `Lowest safe setpoint = system head at peak flow + 5% margin. Payback ${num(pbLowC)} months (low VFD price) to ${num(pbHighC)} months (high price). A setpoint exists only once a drive is installed.`, b: "After the drive" },
          ].map((s) => (
            <li key={s.n} className="rounded-lg border border-green-300 bg-mint p-3">
              <div className="mb-1 flex items-center gap-2"><span className="flex h-6 w-6 items-center justify-center rounded-full bg-brandtext text-xs font-bold text-white">{s.n}</span><span className="text-sm font-semibold text-slate-900">{s.t}</span></div>
              <p className="text-xs leading-relaxed text-slate-600">{s.d}</p>
              <Badge variant="navy" className="mt-2">{s.b}</Badge>
            </li>
          ))}
        </ol>
      </Card>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardTitle icon={<Gauge size={14} />}>Specific energy by control strategy (kWh/m³, simulated)</CardTitle>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={secData} margin={{ top: 20, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} />
                <YAxis hide domain={[0, 0.14]} />
                <Tooltip contentStyle={{ background: "#FFFFFF", border: "1px solid #244574", borderRadius: 8 }} formatter={(v: any) => [`${Number(v).toFixed(3)} kWh/m³`, "SEC"]} />
                <Bar dataKey="sec" radius={[6, 6, 0, 0]}>
                  {secData.map((d) => <Cell key={d.name} fill={d.color} />)}
                  <LabelList dataKey="sec" position="top" formatter={(v: any) => Number(v).toFixed(3)} style={{ fill: "#1e293b", fontSize: 12 }} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card className="lg:col-span-2">
          <CardTitle icon={<Cpu size={14} />}>Reference pump</CardTitle>
          <dl className="grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
            {[["Model", "Grundfos NB 65-160/157"], ["Motor", "11 kW, 2-pole, IE3"], ["Speed", "≈2,950 rpm (datasheet 2,940–2,950)"], ["Rated duty", "26.07 m @ 114 m³/h"], ["Best efficiency", "81.4% pump at 105–108 m³/h"], ["Curve tolerance", "ISO 9906 Grade 3B"]].map(([k, v]) => (
              <div key={k} className="contents"><dt className="text-slate-500">{k}</dt><dd className="text-slate-800">{v}</dd></div>
            ))}
          </dl>
          <p className="mt-3 text-xs text-slate-500">Manufacturer readouts; the datasheet prints 26.5 m at the rated flow, the Product Center readout used here 26.07 m. Shut-off head is not given by the maker.</p>
        </Card>
      </div>

      <Card className="border-warn/40">
        <CardTitle icon={<AlertTriangle size={14} className="text-amber-700" />}>Honest limits</CardTitle>
        <ul className="grid gap-x-6 gap-y-1 text-xs text-slate-700 md:grid-cols-2">
          {["Simulation only: no lab or field data, no real quotes", "About ±3 points only with a measured system curve; otherwise about ±10", "System-curve fit uses the same form as the simulated plant, so it is optimistic", "Single pump, steady state. Out of scope: parallel pumps, closed loops, pumps on drives, NPSH, control dynamics", "Valve share is partly by construction (measured against a speed-matched ideal)", "54–60% saving for heavily oversized pumps is an upper bound only"].map((t) => (
            <li key={t} className="flex gap-2"><CheckCircle2 size={13} className="mt-0.5 shrink-0 text-amber-700" />{t}</li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
