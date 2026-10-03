import clsx from "clsx";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, BarChart, Bar, CartesianGrid, XAxis, YAxis, LabelList } from "recharts";
import { Scale, ScanSearch } from "lucide-react";
import { useState } from "react";
import { Badge } from "../ui/Badge";
import { Card, CardTitle } from "../ui/Card";
import { SimNote } from "../ui/SimNote";
import { Tip } from "../ui/Tip";
import { DATA } from "../../utils/pumpModel";
import { inr, num } from "../../utils/format";

const W = DATA.waste;
const COLORS = { throttle: "#EF4444", wear: "#F59E0B", foul: "#60A5FA" };
const LABEL = { throttle: "Throttle valve (speed mismatch)", wear: "Impeller wear / ageing", foul: "Clogged strainer / line friction" };
const SENSOR_PRICE = 3068;     // indicative 0-10 bar transmitter, upper basic listing
const tipStyle = { background: "#12294D", border: "1px solid #244574", borderRadius: 8, fontSize: 12 };
type Tier = "S0" | "S1" | "S2";
const TIERS: { id: Tier; name: string; sub: string }[] = [
  { id: "S0", name: "S0 · Power + P2", sub: "Minimum kit" },
  { id: "S1", name: "S1 · + strainer ΔP", sub: "Reveals clogging within ±15%" },
  { id: "S2", name: "S2 · + process-side P3", sub: "Measures the system curve" },
];

export function Shapley() {
  const [si, setSi] = useState(0);
  const [tier, setTier] = useState<Tier>("S0");
  const sc = W[si];
  const shares = (["throttle", "wear", "foul"] as const).map((k) => ({ key: k, name: LABEL[k], pct: sc.pct[k], rs: sc.rsYr[k], color: COLORS[k] }));
  const minV = Math.min(...W.map((w) => w.pct.throttle)), maxV = Math.max(...W.map((w) => w.pct.throttle));
  const avgS1 = W.reduce((a, w) => a + (w.misattrib.S0 - w.misattrib.S1), 0) / W.length;
  const avgS2 = W.reduce((a, w) => a + (w.misattrib.S0 - w.misattrib.S2), 0) / W.length;
  const mis = sc.misattrib;
  const cut = mis.S0 - mis[tier];
  const tierBars = TIERS.map((t) => ({ name: t.id, v: mis[t.id], color: t.id === tier ? "#3DCD58" : "#475569" }));
  const stress = tier === "S0" ? { v: "10.5 pts", note: "Learned from logs, stress test (3% noise, curve errors, wrong system curve)" } : tier === "S2" ? { v: "1.4 pts", note: "Learned + system curve fitted from a process-side sensor, stress test" } : { v: "not run", note: "Forecast error was not measured for the strainer ΔP tier" };

  return (
    <div className="space-y-4">
      <SimNote><b>Simulated.</b> Real Grundfos NB 65-160/157 fits, peak demand 80% of rated flow, 10 m static lift, 1% sensor noise, 12 simulated days per case. Wear and clog levels are assumed scenarios. Waste is measured against an ideal: healthy pump, clean system, speed matched to demand.</SimNote>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardTitle icon={<Scale size={14} />} right={<Tip>Shapley split = a fair way to share the blame among causes. The cost of every combination of causes is computed, and each cause's marginal contribution is averaged over all 3! = 6 orderings, so the three shares add up exactly to the total.</Tip>}>Who is to blame? Shapley fair-share split</CardTitle>
          <div className="mb-3 grid grid-cols-2 gap-2 sm:grid-cols-5">
            {W.map((w, i) => (
              <button key={i} onClick={() => setSi(i)} className={clsx("rounded-lg border p-2 text-left text-xs", si === i ? "border-brand bg-brand/10" : "border-navy-600 hover:border-slate-400")}>
                <div className="font-semibold text-white">Wear {Math.round(w.wear * 100)}%</div>
                <div className="text-slate-400">Clog {Math.round(w.foul * 100)}%</div>
              </button>
            ))}
          </div>
          <div className="grid items-center gap-4 sm:grid-cols-2">
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={shares} dataKey="pct" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2} isAnimationActive={false}>
                    {shares.map((s) => <Cell key={s.key} fill={s.color} />)}
                  </Pie>
                  <Tooltip contentStyle={tipStyle} formatter={(v: any) => `${v}%`} />
                  <text x="50%" y="48%" textAnchor="middle" fill="#fff" fontSize="22" fontWeight="700">{num(sc.pct.throttle, 0)}%</text>
                  <text x="50%" y="60%" textAnchor="middle" fill="#94a3b8" fontSize="11">valve share</text>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-2">
              {shares.map((s) => (
                <div key={s.key} className="rounded-lg border border-navy-600 bg-navy-800/70 p-2.5">
                  <div className="flex items-center gap-2 text-xs text-slate-300"><span className="h-2.5 w-2.5 rounded-full" style={{ background: s.color }} />{s.name}</div>
                  <div className="mt-0.5 flex items-baseline justify-between"><span className="text-lg font-bold text-white">{num(s.pct)}%</span><span className="font-mono text-sm text-slate-300">{inr(s.rs)}/yr</span></div>
                </div>
              ))}
              <div className="text-xs text-slate-500">Total simulated waste this case: <b className="text-slate-300">{inr(sc.totalRsYr)}/yr</b></div>
            </div>
          </div>
          <div className="mt-3 rounded-lg border border-warn/40 bg-warn/10 p-3 text-xs text-amber-200">
            Valve share across these five cases: <b>{num(minV, 0)}–{num(maxV, 0)}%</b> (72–87% under stress tests). It is partly by construction, because waste is measured against a speed-matched ideal: it tells you what a drive or trimmed impeller would remove, not that valves are always 83–93% of waste.
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardTitle icon={<ScanSearch size={14} />} right={<Badge variant="green">Value of an extra sensor</Badge>}>What the basic kit cannot see</CardTitle>
          <div className="mb-3 space-y-1.5">
            {TIERS.map((t) => (
              <button key={t.id} onClick={() => setTier(t.id)} className={clsx("w-full rounded-lg border p-2.5 text-left", tier === t.id ? "border-brand bg-brand/10" : "border-navy-600 hover:border-slate-400")}>
                <div className="text-sm font-semibold text-white">{t.name}</div><div className="text-xs text-slate-400">{t.sub}</div>
              </button>
            ))}
          </div>
          <div className="h-32">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tierBars} margin={{ top: 18, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid vertical={false} /><XAxis dataKey="name" tick={{ fontSize: 11 }} /><YAxis hide />
                <Bar dataKey="v" radius={[4, 4, 0, 0]}>{tierBars.map((b) => <Cell key={b.name} fill={b.color} />)}<LabelList dataKey="v" position="top" formatter={(v: any) => inr(Number(v))} style={{ fill: "#e2e8f0", fontSize: 11 }} /></Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="text-xs text-slate-400">Rupees per year attributed to the <b>wrong cause</b> with this sensor set (this case).</div>
          <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
            <div className="rounded-lg border border-navy-600 bg-navy-800/70 p-2"><div className="text-[10px] uppercase text-slate-500">Removed vs S0</div><div className={clsx("font-mono text-lg font-semibold", cut > 0 ? "text-brand" : "text-slate-300")}>{tier === "S0" ? "baseline" : cut > 0 ? inr(cut) + "/yr" : cut === 0 ? "₹0" : "worse by " + inr(-cut)}</div></div>
            <div className="rounded-lg border border-navy-600 bg-navy-800/70 p-2"><div className="text-[10px] uppercase text-slate-500">Forecast error</div><div className="font-mono text-lg font-semibold text-white">{stress.v}</div></div>
          </div>
          <p className="mt-1 text-[11px] text-slate-500">{stress.note}</p>
          {tier !== "S0" && (
            <div className="mt-3 rounded-lg border border-navy-600 bg-navy-800/70 p-2.5 text-xs text-slate-300">
              Sensor payback at an indicative {inr(SENSOR_PRICE)} (installed price may be higher):{" "}
              <b className="text-white">{cut > 0 ? `${num((SENSOR_PRICE / cut) * 12, 1)} months` : "no benefit in this case"}</b>.
              {cut <= 0 && " With no clog, the extra sensor adds noise (a false clog) instead of information."}
            </div>
          )}
          <p className="mt-3 text-xs text-slate-500">Average across the five cases: strainer ΔP removes <b className="text-slate-300">{inr(avgS1)}/yr</b>, process-side P3 removes <b className="text-slate-300">{inr(avgS2)}/yr</b> (about ₹6,000–6,600). A sensor is worth buying if its installed price is below this figure × the payback you accept.</p>
        </Card>
      </div>
    </div>
  );
}
