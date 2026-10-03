import clsx from "clsx";
import { BellRing, Radar } from "lucide-react";
import { useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Badge } from "../ui/Badge";
import { Card, CardTitle } from "../ui/Card";
import { SimNote } from "../ui/SimNote";
import { Tip } from "../ui/Tip";
import { DATA } from "../../utils/pumpModel";
import { num } from "../../utils/format";

const C = DATA.cusum;
type Key = keyof typeof C;
const tipStyle = { background: "#FFFFFF", border: "1px solid #244574", borderRadius: 8, fontSize: 12 };
const NAMES: Record<Key, string> = { slow: "Slow wear", fast: "Fast wear", step: "Step wear", control: "No wear (control)" };

export function Cusum() {
  const [key, setKey] = useState<Key>("slow");
  const [day, setDay] = useState(240);
  const s = C[key];
  const n = s.S.length;
  const d = Math.min(day, n - 1);
  const rows = Array.from({ length: n }, (_, i) => ({ day: i, S: s.S[i] / s.sd, thr: s.h, trueW: 100 * s.trueWear[i], estW: 100 * s.estWear[i] })).slice(0, d + 1);
  const alarmed = s.alarm !== null && d >= s.alarm;
  const status = d < 14 ? { l: "Learning baseline (first 14 days)", v: "slate" as const } : alarmed ? { l: key === "step" ? "Step change in wear detected" : "Slow wear drift detected", v: "red" as const } : { l: "Normal operation", v: "green" as const };
  const hits = s.alarmsAllRuns.filter((a): a is number => a !== null).sort((a, b) => a - b);

  return (
    <div className="space-y-4">
      <SimNote><b>Simulated under stress</b> (3% noise, pump-curve and system mismatch, daily demand mix and offsets). The daily wear estimate is inferred from power + pressure. Each scenario is the median run of {s.runs}. The model detects a head/efficiency loss; it does not diagnose cavitation (NPSH is not modelled).</SimNote>
      <div className="grid gap-4 lg:grid-cols-4">
        <Card className="lg:col-span-1">
          <CardTitle icon={<Radar size={14} />}>Scenario</CardTitle>
          <div className="space-y-1.5">
            {(Object.keys(C) as Key[]).map((k) => (
              <button key={k} onClick={() => { setKey(k); setDay(C[k].S.length - 1); }} className={clsx("w-full rounded-lg border p-2.5 text-left", key === k ? "border-brand bg-brand/10" : "border-green-300 hover:border-slate-400")}>
                <div className="text-sm font-semibold text-slate-900">{NAMES[k]}</div><div className="text-xs text-slate-600">{C[k].label.split(": ")[1]}</div>
              </button>
            ))}
          </div>
          <div className="mt-4"><label className="text-xs text-slate-600">Day {d}</label>
            <input type="range" min={0} max={n - 1} value={d} onChange={(e) => setDay(+e.target.value)} className="w-full accent-[#3DCD58]" aria-label="Day" /></div>
          <div className="mt-3"><Badge variant={status.v === "red" ? "red" : status.v === "green" ? "green" : "slate"} className="!text-sm"><BellRing size={14} />{status.l}</Badge></div>
          {alarmed && s.alarm !== null && <p className="mt-2 text-xs text-slate-700">Alarm on day <b>{s.alarm}</b> at true wear <b>{num(100 * (s.wearAtAlarm ?? 0), 1)}%</b>.</p>}
          <div className="mt-4 rounded-lg border border-green-300 bg-mint p-2.5 text-xs text-slate-700">
            <div className="mb-1 font-semibold text-slate-900">Across {s.runs} simulated runs</div>
            {key === "control" ? <>{hits.length} false alarm{hits.length === 1 ? "" : "s"} in {s.runs} × 365 days{hits.length ? ` (day ${hits.join(", ")})` : ""}.</> : <>Alarm days: {s.alarmsAllRuns.map((a) => a ?? "none").join(", ")}. Median wear at alarm ≈ {num(100 * (s.medianWearAtAlarm ?? 0), 1)}%.</>}
          </div>
        </Card>

        <div className="space-y-4 lg:col-span-3">
          <Card>
            <CardTitle right={<Tip>CUSUM = an alarm that notices slow drift. S_t = max(0, S_(t−1) + (x_t − μ₀ − k)). x_t is the daily wear estimate, μ₀ the mean of the first 14 days, k = 0.5σ, alarm when S_t exceeds h = 5σ (σ from the first 14 days). The chart shows S_t in units of σ.</Tip>}>CUSUM statistic S_t vs alarm threshold h</CardTitle>
            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={rows} margin={{ top: 24, right: 16, left: 0, bottom: 20 }}>
                  <CartesianGrid />
                  <XAxis dataKey="day" type="number" domain={[0, n - 1]} tick={{ fontSize: 11 }} label={{ value: "Day", position: "insideBottom", offset: -14, fill: "#475569", fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} width={44} domain={[0, s.h * 4]} allowDataOverflow tickFormatter={(v) => `${v}σ`} />
                  <Tooltip contentStyle={tipStyle} formatter={(v: any) => `${Number(v).toFixed(2)}σ`} />
                  <Legend verticalAlign="top" height={22} />
                  <ReferenceLine y={s.h} stroke="#EF4444" strokeDasharray="5 4" label={{ value: `threshold h = ${s.h}σ`, fill: "#EF4444", fontSize: 11, position: "insideTopLeft" }} />
                  <ReferenceLine x={14} stroke="#475569" strokeDasharray="2 4" label={{ value: "baseline ends", fill: "#475569", fontSize: 10, position: "insideTopRight" }} />
                  {s.alarm !== null && <ReferenceLine x={s.alarm} stroke="#F59E0B" label={{ value: `alarm day ${s.alarm}`, fill: "#F59E0B", fontSize: 11, position: "top" }} />}
                  <Line dataKey="S" name="S_t (in units of σ, clipped at 20σ)" stroke="#3DCD58" strokeWidth={2.5} dot={false} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
          <Card>
            <CardTitle>Daily wear: simulation truth vs estimate from power + pressure (%)</CardTitle>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={rows} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid /><XAxis dataKey="day" type="number" domain={[0, n - 1]} tick={{ fontSize: 11 }} /><YAxis tick={{ fontSize: 11 }} width={34} domain={[0, 14]} ticks={[0, 4, 8, 12]} />
                  <Tooltip contentStyle={tipStyle} formatter={(v: any) => `${Number(v).toFixed(1)}%`} /><Legend />
                  <Line dataKey="estW" name="Estimated wear" stroke="#60A5FA" strokeWidth={1.5} dot={false} isAnimationActive={false} />
                  <Line dataKey="trueW" name="True wear (simulation)" stroke="#F59E0B" strokeWidth={2} dot={false} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-slate-500">Headline: wear caught at about 2–4%; slow wear alarms around day 40 at ≈2.2%, fast wear around day 22 at ≈3.7%, a 6% step the next day; one false alarm in 3 × 365 simulated days.</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
