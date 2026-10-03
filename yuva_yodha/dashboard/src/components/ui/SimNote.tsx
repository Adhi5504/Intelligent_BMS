import { FlaskConical } from "lucide-react";
import type { ReactNode } from "react";

export function SimNote({ children }: { children: ReactNode }) {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-warn/40 bg-warn/10 px-3 py-2 text-xs text-amber-200">
      <FlaskConical size={14} className="mt-0.5 shrink-0" />
      <div>{children}</div>
    </div>
  );
}
