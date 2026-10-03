import clsx from "clsx";
import { Activity, Pause, Play, RotateCcw, Waves } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, ComposedChart, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Scatter, Tooltip, XAxis, YAxis } from "recharts";
import { Badge } from "../ui/Badge";
import { Card, CardTitle } from "../ui/Card";
import { SimNote } from "../ui/SimNote";
import { Tip } from "../ui/Tip";
import { BAR_TO_M, DATA, hNom, p1FixedSpeed } from "../../utils/pumpModel";
import { num } from "../../utils/format";

const T = DATA.telemetry;
const REC = T.records;
const tipStyle = { background: "#FFFFFF", border: "1px solid #244574", borderRadius: 8, fontSize: 12 };
type Group = "power" | "pressure" | "elec";

export function LiveAudit() {
  const [idx, setIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [group, setGroup] = useState<Group>("power");
  const [calDays, setCalDays] = useState<number>(14);     // 0 = datasheet only
  const [curve, setCurve] = useState<"hq" | "pq">("hq");

  useEffect(() => {
    if (!playing) return;
    const t = setInterval(() => setIdx((i) => (i >= REC.length - 1 ? (setPlaying(false), i) : i + 1)), 90);
    return () => clearInterval(t);
  }, [playing]);

  const cur = REC[idx];
  const series = useMemo(() => REC.slice(0, idx + 1), [idx]);
  const cal = calDays === 0 ? null : T.calibration.find((c) => c.days === calDays)!;
  const sh = cal ? cal.sh : 1, sp = cal ? cal.sp : 1;
  const qInf = cal ? cal.qInferred : T.datasheetOnly.qInferred;

  const curveRows = useMemo(() => {
    const rows: any[] = [];
    for (let q = 40; q <= 130; q += 2) {
      rows.push({
        q,
        ds: curve === "hq" ? hNom(q) : p1FixedSpeed(q, 1),
        cal: curve === "hq" ? sh * hNom(q) : p1FixedSpeed(q, sp),
        tr: curve === "hq" ? T.truth.sh * hNom(q) : p1FixedSpeed(q, T.truth.sp),
      });
    }
    REC.slice(0, idx + 1).forEach((r, i) => rows.push({ q: qInf[i], inf: curve === "hq" ? (r.pd - r.ps) * BAR_TO_M : r.p1 }));
    return rows.sort((a, b) => a.q - b.q);
  }, [curve, sh, sp, idx, qInf]);

  const errData = [
    { name: "Datasheet only", study: 7.4, demo: T.datasheetOnly.error },
    ...[1, 3, 7, 14].map((d) => ({ name: `${d} day${d > 1 ? "s" : ""} of logs`, study: { 1: 1.8, 3: 1.4, 7: 1.3, 14: 1.2 }[d]!, demo: T.calibration.find((c) => c.days === d)!.error })),
  ];

  const tiles: [string, string, string][] = [
    ["Motor current Irms", num(cur.i_a, 1), "A"], ["Line voltage Vrms", num(cur.v, 0), "V"], ["Real power", num(cur.p1, 2), "kW"],
    ["Power factor", num(cur.pf, 2), ""], ["Discharge pressure", num(cur.pd, 2), "bar"], ["Suction pressure", num(cur.ps, 2), "bar"], ["Process-side pressure", num(cur.p3, 2), "bar"],
  ];

  return (
    <div className="space-y-4">
      <SimNote>
        <b>Simulated playback, not a live feed.</b> These 14 days (16 hourly records per day) are generated from the pump model with seeded 1% noise. Current, voltage and power factor use an assumed power-factor curve and a flooded suction of about 0.5 bar. A "true" pump with head ×0.96 and power ×1.05 vs the datasheet is hidden from the calibrator.
      </SimNote>

      <Card>
        <CardTitle icon={<Activity size={14} />} right={<Badge variant="amber">SIMULATED</Badge>}>ESP32 logger telemetry</CardTitle>
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <button onClick={() => setPlaying((p) => !p)} className="flex items-center gap-1.5 rounded-lg bg-brandtext px-3 py-1.5 text-sm font-semibold text-white hover:bg-[#14692b]">
            {playing ? <Pause size={14} /> : <Play size={14} />}{playing ? "Pause" : "Play"}
          </button>
          <button onClick={() => { setIdx(0); setPlaying(false); }} className="flex items-center gap-1.5 rounded-lg border border-green-300 px-3 py-1.5 text-sm text-slate-700 hover:text-slate-900"><RotateCcw size={14} />Reset</button>
          <input aria-label="Playback position" type="range" min={0} max={REC.length - 1} value={idx} onChange={(e) => { setIdx(+e.target.value); setPlaying(false); }} className="h-1.5 min-w-[160px] flex-1 accent-[#3DCD58]" />
          <span className="font-mono text-sm text-slate-700">Day {cur.day}/14 · hour {cur.hour + 1}/16</span>
        </div>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 xl:grid-cols-7">
          {tiles.map(([k, v, u]) => (
            <div key={k} className="rounded-lg border border-green-300 bg-mint p-2.5">
              <div className="text-[10px] uppercase tracking-wide text-slate-500">{k}</div>
              <div className="font-mono text-lg font-semibold text-slate-900">{v}<span className="ml-1 text-xs font-normal text-slate-600">{u}</span></div>
            </div>
          ))}
        </div>
        <div className="mt-3 flex gap-1.5">
          {([["power", "Power & current"], ["pressure", "Pressures"], ["elec", "Voltage & PF"]] as [Group, string][]).map(([g, l]) => (
            <button key={g} onClick={() => setGroup(g)} className={clsx("rounded-md px-3 py-1 text-xs font-semibold", group === g ? "bg-brand/25 text-slate-900" : "text-slate-600 hover:text-slate-900")}>{l}</button>
          ))}
        </div>
        <div className="h-60">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={series} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid />
              <XAxis dataKey="i" type="number" domain={[0, REC.length - 1]} tickFormatter={(v) => `D${Math.floor(v / 16) + 1}`} tick={{ fontSize: 11 }} ticks={[0, 16, 48, 96, 144, 192, 223]} />
              {group === "power" && <><YAxis yAxisId="a" tick={{ fontSize: 11 }} width={40} /><YAxis yAxisId="b" orientation="right" tick={{ fontSize: 11 }} width={40} /></>}
              {group === "pressure" && <YAxis yAxisId="a" tick={{ fontSize: 11 }} width={40} />}
              {group === "elec" && <><YAxis yAxisId="a" domain={[380, 420]} tick={{ fontSize: 11 }} width={40} /><YAxis yAxisId="b" orientation="right" domain={[0.5, 1]} tick={{ fontSize: 11 }} width={40} /></>}
              <Tooltip contentStyle={tipStyle} labelFormatter={(v) => `Day ${Math.floor(Number(v) / 16) + 1}, hour ${(Number(v) % 16) + 1}`} />
              <Legend />
              {group === "power" && <><Line yAxisId="a" dataKey="p1" name="Real power (kW)" stroke="#3DCD58" dot={false} strokeWidth={2} isAnimationActive={false} /><Line yAxisId="b" dataKey="i_a" name="Current (A)" stroke="#F59E0B" dot={false} strokeWidth={2} isAnimationActive={false} /></>}
              {group === "pressure" && <><Line yAxisId="a" dataKey="pd" name="Discharge (bar)" stroke="#3DCD58" dot={false} strokeWidth={2} isAnimationActive={false} /><Line yAxisId="a" dataKey="p3" name="Process side (bar)" stroke="#60A5FA" dot={false} strokeWidth={2} isAnimationActive={false} /><Line yAxisId="a" dataKey="ps" name="Suction (bar)" stroke="#475569" dot={false} strokeWidth={2} isAnimationActive={false} /></>}
              {group === "elec" && <><Line yAxisId="a" dataKey="v" name="Voltage (V)" stroke="#60A5FA" dot={false} strokeWidth={2} isAnimationActive={false} /><Line yAxisId="b" dataKey="pf" name="Power factor" stroke="#F59E0B" dot={false} strokeWidth={2} isAnimationActive={false} /></>}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <div className="grid gap-4 xl:grid-cols-5">
        <Card className="xl:col-span-3">
          <CardTitle icon={<Waves size={14} />} right={
            <div className="flex gap-1">{(["hq", "pq"] as const).map((c) => <button key={c} onClick={() => setCurve(c)} className={clsx("rounded-md px-2.5 py-1 text-xs font-semibold", curve === c ? "bg-brand/25 text-slate-900" : "text-slate-600 hover:text-slate-900")}>{c === "hq" ? "H–Q" : "P–Q"}</button>)}</div>
          }>
            Sensorless flow: {curve === "hq" ? "head vs flow" : "electrical power vs flow"}
          </CardTitle>
          <div className="mb-2 flex flex-wrap gap-1.5">
            {[0, 1, 3, 7, 14].map((d) => (
              <button key={d} onClick={() => setCalDays(d)} className={clsx("rounded-md border px-2.5 py-1 text-xs font-semibold", calDays === d ? "border-brand bg-brand/15 text-brandtext" : "border-green-300 text-slate-700 hover:text-slate-900")}>
                {d === 0 ? "Datasheet only" : `Calibrated: ${d} day${d > 1 ? "s" : ""}`}
              </button>
            ))}
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={curveRows} margin={{ top: 8, right: 16, left: 0, bottom: 14 }}>
                <CartesianGrid />
                <XAxis dataKey="q" type="number" domain={[40, 130]} tick={{ fontSize: 11 }} label={{ value: "Flow, m³/h", position: "insideBottom", offset: -6, fill: "#475569", fontSize: 11 }} />
                <YAxis domain={curve === "hq" ? [20, 36] : [6, 12]} tick={{ fontSize: 11 }} width={40} label={{ value: curve === "hq" ? "m" : "kW", angle: -90, position: "insideLeft", fill: "#475569", fontSize: 11 }} />
                <Tooltip contentStyle={tipStyle} formatter={(v: any) => Number(v).toFixed(2)} labelFormatter={(v) => `${v} m³/h`} />
                <Legend verticalAlign="top" height={28} />
                <Line dataKey="ds" name="Datasheet fit" stroke="#475569" dot={false} strokeWidth={2} connectNulls strokeDasharray="5 4" isAnimationActive={false} />
                <Line dataKey="cal" name={cal ? `Calibrated (${cal.days} d)` : "Calibrated (none)"} stroke="#3DCD58" dot={false} strokeWidth={2.5} connectNulls isAnimationActive={false} />
                <Line dataKey="tr" name="Simulation truth" stroke="#F59E0B" dot={false} strokeWidth={1.5} connectNulls isAnimationActive={false} />
                <Scatter dataKey="inf" name="Inferred operating points" fill="#60A5FA" isAnimationActive={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">Blue points = measured head (or power) plotted at the flow the calibrated model infers. Press Play above to add points. No flow meter is used anywhere.</p>
        </Card>

        <Card className="xl:col-span-2">
          <CardTitle right={<Tip>Forecast error = how far the predicted VFD saving is from the simulation truth, in percentage points. The model's own uncertainty band is NOT used: it is overconfident (holds the truth only 39–72% of the time). About ±3 points holds only when the system curve is measured; otherwise about ±10.</Tip>}>Calibration from logs</CardTitle>
          <div className="mb-3 grid grid-cols-2 gap-2 text-sm">
            {[["Head scale s_h", `${num(sh, 2)} (truth ${T.truth.sh})`], ["Power scale s_p", `${num(sp, 2)} (truth ${T.truth.sp})`],
              ["Forecast saving", `${num(cal ? cal.forecast : T.datasheetOnly.forecast)}% (truth ${num(T.truth.saving)}%)`],
              ["Error this demo run", `${num(cal ? cal.error : T.datasheetOnly.error, 2)} pts`]].map(([k, v]) => (
              <div key={k} className="rounded-lg border border-green-300 bg-mint p-2">
                <div className="text-[10px] uppercase text-slate-500">{k}</div><div className="font-mono text-sm text-slate-900">{v}</div>
              </div>
            ))}
          </div>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={errData} margin={{ top: 18, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 9 }} interval={0} />
                <YAxis hide domain={[0, 10]} />
                <Tooltip contentStyle={tipStyle} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <ReferenceLine y={3} stroke="#F59E0B" strokeDasharray="4 4" label={{ value: "±3 pts (needs measured system curve)", fill: "#F59E0B", fontSize: 10, position: "insideTopRight" }} />
                <Bar dataKey="study" name="Study mean (5 pump cases × 8 trials)" fill="#3DCD58" radius={[4, 4, 0, 0]} label={{ position: "top", fill: "#1e293b", fontSize: 10 }} />
                <Bar dataKey="demo" name="This single demo run" fill="#475569" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-2 text-xs text-slate-500">The demo run is one random draw and flatters the method; the study mean is the number to quote. Stress tests (3% noise, curve-shape error) raise learned-from-logs error to 10.5 points unless the system curve is measured.</p>
        </Card>
      </div>
    </div>
  );
}
