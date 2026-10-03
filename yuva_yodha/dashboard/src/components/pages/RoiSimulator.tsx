import clsx from "clsx";
import { Calculator, CheckCircle2, CircleAlert, XCircle } from "lucide-react";
import { useMemo, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Badge } from "../ui/Badge";
import { Card, CardTitle } from "../ui/Card";
import { SimNote } from "../ui/SimNote";
import { SliderField } from "../ui/SliderField";
import { DEFAULTS, evaluate, paybackMonths, type ScenarioInput } from "../../utils/pumpModel";
import { inr, num } from "../../utils/format";
import { modeLabel, useMode } from "../../utils/modeContext";

const tipStyle = { background: "#12294D", border: "1px solid #244574", borderRadius: 8, fontSize: 12 };
const PRESETS = [
  { name: "Oversized pump", peak: 80, lift: 10, note: "Peak demand 80% of rated flow, 10 m lift" },
  { name: "Base case", peak: 90, lift: 10, note: "Peak demand 90%, 10 m lift" },
  { name: "Right-sized, high lift", peak: 95, lift: 20, note: "Peak demand 95%, 20 m lift" },
];

export function RoiSimulator() {
  const { mode } = useMode();
  const [hours, setHours] = useState(16);
  const [days, setDays] = useState(300);
  const [tariff, setTariff] = useState(8);
  const [peak, setPeak] = useState(90);
  const [lift, setLift] = useState(10);
  const [capex, setCapex] = useState(50200);

  const inp: ScenarioInput = { ...DEFAULTS, hoursPerDay: hours, daysPerYear: days, tariff, peakFrac: peak / 100, hStatic: lift };
  const r = useMemo(() => evaluate(inp), [hours, days, tariff, peak, lift]);   // eslint-disable-line react-hooks/exhaustive-deps

  let verdict: { label: string; sub: string; variant: "green" | "amber" | "red"; icon: JSX.Element } | null = null;
  let pb = Infinity, annual = 0, monthly = 0, chart: any[] = [];
  if (r.ok) {
    annual = r.savingRsYr[mode];
    monthly = annual / 12;
    pb = paybackMonths(capex, annual);
    verdict = pb <= 12 ? { label: "GO", sub: `Highly recommended: ${num(pb)} months payback`, variant: "green", icon: <CheckCircle2 /> }
      : pb <= 24 ? { label: "CONDITIONAL", sub: `${num(pb)} months payback. Check VFD price and fix cheaper items first`, variant: "amber", icon: <CircleAlert /> }
      : { label: "NO-GO (for now)", sub: isFinite(pb) ? `${num(pb / 12, 1)} years payback. Fix cheaper items first` : "No saving at these settings", variant: "red", icon: <XCircle /> };
    chart = Array.from({ length: 37 }, (_, m) => ({ m, const: -capex + (r.savingRsYr.const / 12) * m, prop: -capex + (r.savingRsYr.prop / 12) * m }));
  }

  return (
    <div className="space-y-4">
      <SimNote><b>Simulated model, editable assumptions.</b> The same pump model as the Overview, re-run live as you move the sliders. Verdict rule (our design choice): payback ≤ 12 months = GO, 12–24 months = CONDITIONAL, longer = NO-GO for now. Install cost and VFD price are indicative, not quotes.</SimNote>
      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-2">
          <CardTitle icon={<Calculator size={14} />}>Your pump and plant</CardTitle>
          <div className="mb-4 flex flex-wrap gap-1.5">
            {PRESETS.map((p) => (
              <button key={p.name} title={p.note} onClick={() => { setPeak(p.peak); setLift(p.lift); }} className={clsx("rounded-md border px-2.5 py-1 text-xs font-semibold", peak === p.peak && lift === p.lift ? "border-brand bg-brand/10 text-brand" : "border-navy-600 text-slate-300 hover:text-white")}>{p.name}</button>
            ))}
          </div>
          <div className="space-y-5">
            <SliderField label="Operating hours per day" value={hours} min={4} max={24} step={1} unit="h" onChange={setHours} />
            <SliderField label="Operating days per year" value={days} min={150} max={365} step={5} unit="days" onChange={setDays} />
            <SliderField label="Grid electricity tariff" value={tariff} min={5} max={14} step={0.5} format={(v) => `₹${v.toFixed(1)}`} unit="/kWh" onChange={setTariff} />
            <SliderField label="Average peak demand (% of rated flow)" value={peak} min={60} max={95} step={1} unit="%" onChange={setPeak} />
            <SliderField label="Static lift / elevation head" value={lift} min={5} max={25} step={1} unit="m" onChange={setLift} />
            <SliderField label="VFD + installation cost" value={capex} min={40000} max={120000} step={100} format={(v) => inr(v)} onChange={setCapex} />
          </div>
        </Card>

        <div className="space-y-4 lg:col-span-3">
          {r.ok && verdict ? (
            <>
              <div className={clsx("flex items-center gap-4 rounded-xl border-2 p-4", verdict.variant === "green" ? "border-brand bg-brand/10 text-brand" : verdict.variant === "amber" ? "border-warn bg-warn/10 text-warn" : "border-danger bg-danger/10 text-danger")}>
                <div className="[&>svg]:h-10 [&>svg]:w-10">{verdict.icon}</div>
                <div>
                  <div className="text-2xl font-extrabold tracking-tight">{verdict.label}</div>
                  <div className="text-sm text-slate-200">{verdict.sub} · {modeLabel(mode)}</div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[["Annual saving", inr(annual)], ["Monthly saving", inr(monthly)], ["Energy saved", `${num(r.savingPct[mode])}%`], ["CO₂ avoided", `${num(r.co2TYr[mode])} t/yr`]].map(([k, v]) => (
                  <Card key={k} className="!p-3"><div className="text-[10px] uppercase tracking-wide text-slate-500">{k}</div><div className="text-lg font-bold text-white">{v}</div></Card>
                ))}
              </div>
              <Card>
                <CardTitle right={<Badge variant="navy">Break-even {isFinite(pb) && pb <= 36 ? `month ${num(pb, 1)}` : "beyond 36 months"}</Badge>}>Cumulative cash position after buying the VFD</CardTitle>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chart} margin={{ top: 22, right: 16, left: 8, bottom: 22 }}>
                      <CartesianGrid />
                      <XAxis dataKey="m" tick={{ fontSize: 11 }} label={{ value: "Months after installation", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${v < 0 ? "-" : ""}${Math.abs(v / 1000).toFixed(0)}k`} width={44} />
                      <Tooltip contentStyle={tipStyle} formatter={(v: any) => inr(Number(v))} labelFormatter={(m) => `Month ${m}`} />
                      <Legend verticalAlign="top" height={24} />
                      <ReferenceLine y={0} stroke="#94a3b8" />
                      {isFinite(pb) && pb <= 36 && <ReferenceLine x={Math.round(pb)} stroke="#3DCD58" strokeDasharray="4 4" label={{ value: "break-even", fill: "#3DCD58", fontSize: 11, position: "insideBottomRight" }} />}
                      <Line dataKey="const" name="Constant pressure" stroke={mode === "const" ? "#3DCD58" : "#2f7d44"} strokeWidth={mode === "const" ? 3 : 1.5} dot={false} isAnimationActive={false} />
                      <Line dataKey="prop" name="Proportional pressure" stroke={mode === "prop" ? "#3DCD58" : "#60A5FA"} strokeWidth={mode === "prop" ? 3 : 1.5} dot={false} isAnimationActive={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <p className="text-xs text-slate-500">Setpoint if a constant-pressure drive is fitted: {num(r.hConst)} m ({num(r.hConst / 10.197, 2)} bar). The saving scales the 16-step daily profile by hours/16. Both modes are plotted; the selected mode is bold.</p>
              </Card>
            </>
          ) : (
            <Card className="border-danger/50"><div className="flex items-center gap-2 text-danger"><XCircle /><b>This combination is outside the model</b></div><p className="mt-2 text-sm text-slate-300">{!r.ok && r.reason}</p></Card>
          )}
        </div>
      </div>
    </div>
  );
}
