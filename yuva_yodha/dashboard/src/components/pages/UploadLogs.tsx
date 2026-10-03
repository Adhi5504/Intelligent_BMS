import clsx from "clsx";
import { Download, FileUp, ShieldCheck, TriangleAlert } from "lucide-react";
import { useMemo, useRef, useState } from "react";
import { CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Scatter, Tooltip, XAxis, YAxis } from "recharts";
import { Badge } from "../ui/Badge";
import { Card, CardTitle } from "../ui/Card";
import { SimNote } from "../ui/SimNote";
import { SliderField } from "../ui/SliderField";
import { Tip } from "../ui/Tip";
import { analyse, parseCsv, sampleCsv, UPLOAD_DEFAULTS, type LogRow, type UploadInputs } from "../../utils/calibrate";
import { DATA, hNom, p1FixedSpeed } from "../../utils/pumpModel";
import { inr, num } from "../../utils/format";

const tipStyle = { background: "#FFFFFF", border: "1px solid #BFE3C8", borderRadius: 8, fontSize: 12 };

export function UploadLogs() {
  const [rows, setRows] = useState<LogRow[]>([]);
  const [name, setName] = useState("");
  const [notes, setNotes] = useState<string[]>([]);
  const [inp, setInp] = useState<UploadInputs>(UPLOAD_DEFAULTS);
  const [busy, setBusy] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const set = (k: keyof UploadInputs) => (v: number) => setInp((p) => ({ ...p, [k]: v }));

  const load = (text: string, label: string) => {
    setBusy(true);
    setTimeout(() => { const p = parseCsv(text); setRows(p.rows); setNotes(p.notes); setName(label); setBusy(false); }, 20);
  };
  const onFile = async (f?: File) => { if (f) load(await f.text(), f.name); };
  const sample = useMemo(() => sampleCsv(DATA.telemetry.records), []);
  const res = useMemo(() => (rows.length ? analyse(rows, inp) : null), [rows, inp]);

  const downloadSample = () => {
    const url = URL.createObjectURL(new Blob([sample], { type: "text/csv" }));
    const a = document.createElement("a"); a.href = url; a.download = "pumprupee_sample_logs.csv"; a.click(); URL.revokeObjectURL(url);
  };

  const chartRows = useMemo(() => {
    if (!res || !res.ok) return [];
    const out: any[] = [];
    for (let q = 40; q <= 130; q += 2) out.push({ q, ds: hNom(q), cal: res.cal.sh * hNom(q) });
    rows.forEach((_, i) => { if (i % 2 === 0) out.push({ q: res.cal.qInferred[i], pt: res.cal.heads[i] }); });
    return out.sort((a, b) => a.q - b.q);
  }, [res, rows]);
  const pbVariant = res && res.ok ? (res.paybackMonths <= 12 ? "green" : res.paybackMonths <= 24 ? "amber" : "red") : "slate";

  return (
    <div className="space-y-4">
      <SimNote>
        <b>Your files stay in your browser.</b> Nothing is uploaded to a server. The analysis uses the <b>reference pump (Grundfos NB 65-160/157)</b> curves, so it is valid only for that pump model. The system curve is <b>assumed</b> (static lift + margin below): treat the forecast as about ±10 points unless you have measured the system curve. Simulation-grade, not a certified audit.
      </SimNote>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-2">
          <CardTitle icon={<FileUp size={14} />}>1. Load pump logs (CSV)</CardTitle>
          <p className="mb-3 text-xs text-slate-600">Columns: <code className="rounded bg-mint px-1">power_kw</code>, <code className="rounded bg-mint px-1">discharge_bar</code>, optional <code className="rounded bg-mint px-1">suction_bar</code>. One row per record (hourly means work best), 7–14 days.</p>
          <input ref={fileRef} id="log-file" type="file" accept=".csv,text/csv,text/plain" className="sr-only" onChange={(e) => onFile(e.target.files?.[0])} />
          <div className="flex flex-wrap gap-2">
            <button onClick={() => fileRef.current?.click()} className="flex items-center gap-1.5 rounded-lg bg-brandtext px-3 py-2 text-sm font-bold text-white hover:bg-[#14692b]"><FileUp size={14} />Choose CSV file</button>
            <button onClick={() => load(sample, "sample (simulated 14 days)")} className="rounded-lg border border-green-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:text-slate-900">Load sample data</button>
            <button onClick={downloadSample} className="flex items-center gap-1.5 rounded-lg border border-green-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:text-slate-900"><Download size={14} />Sample CSV</button>
          </div>
          {name && <div className="mt-3 flex items-center gap-2 text-xs text-slate-700"><ShieldCheck size={14} className="text-brandtext" />{busy ? "Calibrating…" : <>{rows.length} valid rows from <b>{name}</b></>}</div>}
          {notes.map((n) => <div key={n} className="mt-1 flex gap-1.5 text-xs text-amber-700"><TriangleAlert size={13} className="mt-0.5 shrink-0" />{n}</div>)}
          <div className="mt-5 space-y-5">
            <SliderField label="Suction pressure if not in the file" value={inp.psDefault} min={0} max={3} step={0.05} format={(v) => v.toFixed(2)} unit="bar" onChange={set("psDefault")} />
            <SliderField label="Static lift (assumed system curve)" value={inp.hStatic} min={5} max={25} step={1} unit="m" onChange={set("hStatic")} />
            <SliderField label="Operating hours per day" value={inp.hoursPerDay} min={4} max={24} step={1} unit="h" onChange={set("hoursPerDay")} />
            <SliderField label="Operating days per year" value={inp.daysPerYear} min={150} max={365} step={5} unit="days" onChange={set("daysPerYear")} />
            <SliderField label="Electricity tariff" value={inp.tariff} min={5} max={14} step={0.5} format={(v) => `₹${v.toFixed(1)}`} unit="/kWh" onChange={set("tariff")} />
            <SliderField label="VFD + installation cost" value={inp.capex} min={40000} max={120000} step={100} format={(v) => inr(v)} onChange={set("capex")} />
          </div>
        </Card>

        <div className="space-y-4 lg:col-span-3">
          {!res && <Card><div className="py-10 text-center text-sm text-slate-600">Load a CSV or the sample to see the calibrated pump, inferred flow, ₹ saving and VFD payback.</div></Card>}
          {res && !res.ok && <Card className="border-danger/50"><div className="flex items-center gap-2 text-red-600"><TriangleAlert size={18} /><b>Cannot analyse this file</b></div><p className="mt-2 text-sm text-slate-700">{res.reason}</p></Card>}
          {res && res.ok && (
            <>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[["Head scale s_h", num(res.cal.sh, 2)], ["Power scale s_p", num(res.cal.sp, 2)], ["Mean inferred flow", `${num(res.meanQ, 0)} m³/h`], ["SEC", `${num(res.sec, 3)} kWh/m³`]].map(([k, v]) => (
                  <Card key={k} className="!p-3"><div className="text-[10px] uppercase tracking-wide text-slate-500">{k}</div><div className="text-lg font-bold text-slate-900">{v}</div></Card>
                ))}
              </div>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[["Running cost", `₹${num(res.rsPerM3, 2)}/m³`], ["Forecast VFD saving", `${num(res.savingPct)}%`], ["Saving per year", inr(res.savingRsYr)], ["CO₂ avoided", `${num(res.co2TYr)} t/yr`]].map(([k, v]) => (
                  <Card key={k} className="!p-3 border-brand/40"><div className="text-[10px] uppercase tracking-wide text-slate-500">{k}</div><div className="text-lg font-bold text-brandtext">{v}</div></Card>
                ))}
              </div>
              <Card className="flex flex-wrap items-center justify-between gap-2">
                <div className="text-sm text-slate-700">VFD payback at {inr(inp.capex)}: <b className="text-slate-900">{isFinite(res.paybackMonths) ? `${num(res.paybackMonths)} months` : "no saving"}</b> · proportional-pressure strategy · ±10 points unless the system curve is measured</div>
                <Badge variant={pbVariant as any} className="!text-sm">{res.paybackMonths <= 12 ? "GO" : res.paybackMonths <= 24 ? "CONDITIONAL" : "NO-GO for now"}</Badge>
              </Card>
              <Card>
                <CardTitle right={<Tip>Each blue point is a record: measured head plotted at the flow the calibrated model infers. The green line is the datasheet curve scaled by s_h. No flow meter is used.</Tip>}>Calibrated pump and inferred flow (head vs flow)</CardTitle>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={chartRows} margin={{ top: 8, right: 16, left: 0, bottom: 14 }}>
                      <CartesianGrid />
                      <XAxis dataKey="q" type="number" domain={[40, 130]} tick={{ fontSize: 11 }} label={{ value: "Flow, m³/h", position: "insideBottom", offset: -6, fill: "#475569", fontSize: 11 }} />
                      <YAxis domain={["auto", "auto"]} tick={{ fontSize: 11 }} width={40} />
                      <Tooltip contentStyle={tipStyle} formatter={(v: any) => Number(v).toFixed(2)} />
                      <Legend verticalAlign="top" height={26} />
                      <Line dataKey="ds" name="Datasheet fit" stroke="#94a3b8" strokeDasharray="5 4" dot={false} connectNulls isAnimationActive={false} />
                      <Line dataKey="cal" name="Calibrated" stroke="#3DCD58" strokeWidth={2.5} dot={false} connectNulls isAnimationActive={false} />
                      <Scatter dataKey="pt" name="Your records" fill="#2563eb" isAnimationActive={false} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
                <p className="text-xs text-slate-500">Calibration searched {res.cal.used} records on a grid of s_h (0.88–1.12) and s_p (0.92–1.22). Mean power {num(res.meanPowerKw, 2)} kW. Annual bill at this duty {inr(res.baseRsYr)}.</p>
                {res.skippedInfeasible > 0 && <p className={clsx("mt-1 text-xs text-amber-700")}>{res.skippedInfeasible} record(s) could not be speed-matched at this static lift and were left out of the forecast.</p>}
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
