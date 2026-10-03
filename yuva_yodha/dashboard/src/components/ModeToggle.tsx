import clsx from "clsx";
import { modeLabel, useMode } from "../utils/modeContext";
import type { ControlMode } from "../types";

export function ModeToggle() {
  const { mode, setMode } = useMode();
  return (
    <div className="inline-flex rounded-lg border border-navy-600 bg-navy-800 p-0.5 text-xs" role="group" aria-label="VFD control mode">
      {(["const", "prop"] as ControlMode[]).map((m) => (
        <button key={m} onClick={() => setMode(m)} className={clsx("rounded-md px-3 py-1.5 font-semibold transition", mode === m ? "bg-brand text-navy-950" : "text-slate-300 hover:text-white")}>
          {modeLabel(m)}
        </button>
      ))}
    </div>
  );
}
