import { FileDown, Info } from "lucide-react";
import { useState } from "react";
import { Badge } from "./ui/Badge";
import { Modal } from "./ui/Modal";
import { ModeToggle } from "./ModeToggle";
import { useMode } from "../utils/modeContext";

export function Header() {
  const { openReport } = useMode();
  const [about, setAbout] = useState(false);
  return (
    <header className="border-b border-navy-700 bg-navy-900">
      <div className="mx-auto flex max-w-[1400px] flex-wrap items-center justify-between gap-3 px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-navy-950 text-2xl font-extrabold text-brand ring-1 ring-brand/50">₹</div>
          <div>
            <h1 className="text-lg font-extrabold leading-tight tracking-tight text-white">PumpRupee <span className="font-medium text-slate-400">Audit Dashboard</span></h1>
            <p className="text-[11px] text-slate-400">Schneider Electric Yuva Yodha 2026 · Smart Manufacturing · Team ANS_4X</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="amber">SIMULATED DATA · no field measurements</Badge>
          <ModeToggle />
          <button onClick={() => setAbout(true)} className="flex items-center gap-1.5 rounded-lg border border-navy-600 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white"><Info size={14} />About the data</button>
          <button onClick={openReport} className="flex items-center gap-1.5 rounded-lg bg-brand px-3 py-1.5 text-xs font-bold text-navy-950 hover:bg-brand-dark"><FileDown size={14} />Export report</button>
        </div>
      </div>
      <Modal open={about} onOpenChange={setAbout} title="What is real and what is simulated">
        <div className="space-y-3 text-sm text-slate-300">
          <p><b className="text-white">Real:</b> the 14 manufacturer readouts for the Grundfos NB 65-160/157 (product 97839240), the CEA v21.0 emission factor (0.710 kg CO₂/kWh), and indicative online prices found on 2026-10-02 (not quotes).</p>
          <p><b className="text-white">Fitted:</b> the pump H(Q) and P(Q) curves are cubic least-squares fits to those readouts. The true shut-off head is not given by the maker and is not used.</p>
          <p><b className="text-white">Assumed:</b> static lift, demand profile, head margin, running hours, tariff, VFD efficiency 0.97, the wear and clog models, power-factor curve, suction pressure.</p>
          <p><b className="text-white">Simulated:</b> every telemetry sample, calibration run, waste split, wear-drift run and saving. There is no lab or field data and no live hardware feed.</p>
          <p className="text-slate-400">Reproduce everything with the Python scripts in <code>yuva_yodha/</code> (fixed seeds) and <code>npm run gen-data</code>.</p>
        </div>
      </Modal>
    </header>
  );
}
