import clsx from "clsx";
import type { ReactNode } from "react";

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={clsx("rounded-xl border border-navy-700 bg-navy-900/80 p-4 shadow-sm", className)}>{children}</div>;
}
export function CardTitle({ icon, children, right }: { icon?: ReactNode; children: ReactNode; right?: ReactNode }) {
  return (
    <div className="mb-3 flex items-center justify-between gap-2">
      <h3 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-300">
        {icon}
        {children}
      </h3>
      {right}
    </div>
  );
}
