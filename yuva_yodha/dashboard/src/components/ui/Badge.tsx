import clsx from "clsx";
import type { ReactNode } from "react";

const variants = {
  green: "bg-brand/15 text-brandtext border-brand/40",
  amber: "bg-warn/15 text-amber-700 border-warn/40",
  red: "bg-danger/15 text-red-600 border-danger/40",
  slate: "bg-slate-500/15 text-slate-700 border-slate-500/40",
  navy: "bg-mintdark text-slate-800 border-green-300",
};
export function Badge({ variant = "slate", className, children }: { variant?: keyof typeof variants; className?: string; children: ReactNode }) {
  return <span className={clsx("inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold", variants[variant], className)}>{children}</span>;
}
