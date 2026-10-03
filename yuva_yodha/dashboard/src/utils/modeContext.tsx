import { createContext, useContext, useState, type ReactNode } from "react";
import type { ControlMode } from "../types";

interface Ctx { mode: ControlMode; setMode: (m: ControlMode) => void; openReport: () => void; reportOpen: boolean; setReportOpen: (o: boolean) => void }
const C = createContext<Ctx>(null as unknown as Ctx);

export function ModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ControlMode>("const");
  const [reportOpen, setReportOpen] = useState(false);
  return <C.Provider value={{ mode, setMode, reportOpen, setReportOpen, openReport: () => setReportOpen(true) }}>{children}</C.Provider>;
}
export const useMode = () => useContext(C);
export const modeLabel = (m: ControlMode) => (m === "const" ? "Constant pressure" : "Proportional pressure");
