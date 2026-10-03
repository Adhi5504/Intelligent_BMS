import * as Tooltip from "@radix-ui/react-tooltip";
import { Info } from "lucide-react";
import type { ReactNode } from "react";

/** Info icon with a hover/focus tooltip (Radix). */
export function Tip({ children }: { children: ReactNode }) {
  return (
    <Tooltip.Provider delayDuration={100}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <button type="button" aria-label="More information" className="inline-flex text-slate-400 hover:text-brand focus:outline-none focus-visible:ring-2 focus-visible:ring-brand rounded">
            <Info size={14} />
          </button>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content side="top" sideOffset={6} className="z-50 max-w-xs rounded-lg border border-navy-600 bg-navy-800 px-3 py-2 text-xs leading-relaxed text-slate-200 shadow-xl">
            {children}
            <Tooltip.Arrow className="fill-navy-800" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
