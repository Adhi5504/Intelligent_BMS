import clsx from "clsx";
import type { ReactNode } from "react";
import { Card } from "./Card";

export function Stat({ icon, label, value, sub, accent = "text-slate-900", tip }: { icon?: ReactNode; label: string; value: ReactNode; sub?: ReactNode; accent?: string; tip?: ReactNode }) {
  return (
    <Card>
      <div className="mb-1 flex items-center justify-between text-xs font-medium uppercase tracking-wide text-slate-600">
        <span className="flex items-center gap-1.5">{icon}{label}</span>
        {tip}
      </div>
      <div className={clsx("text-2xl font-bold leading-tight sm:text-[1.7rem]", accent)}>{value}</div>
      {sub && <div className="mt-1 text-xs text-slate-600">{sub}</div>}
    </Card>
  );
}
