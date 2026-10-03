import * as Tabs from "@radix-ui/react-tabs";
import { Activity, BarChart3, Calculator, ClipboardCheck, LayoutDashboard, Scale } from "lucide-react";
import { Header } from "./components/Header";
import { ReportSheet } from "./components/ReportSheet";
import { Cusum } from "./components/pages/Cusum";
import { LiveAudit } from "./components/pages/LiveAudit";
import { Overview } from "./components/pages/Overview";
import { RoiSimulator } from "./components/pages/RoiSimulator";
import { Shapley } from "./components/pages/Shapley";
import { Verification } from "./components/pages/Verification";
import { ModeProvider } from "./utils/modeContext";

const TABS = [
  { id: "overview", label: "Executive Overview", icon: LayoutDashboard, el: <Overview /> },
  { id: "live", label: "Live Audit & Flow Inference", icon: Activity, el: <LiveAudit /> },
  { id: "waste", label: "Shapley Waste Split", icon: Scale, el: <Shapley /> },
  { id: "roi", label: "VFD Payback Simulator", icon: Calculator, el: <RoiSimulator /> },
  { id: "wear", label: "CUSUM Wear Monitor", icon: BarChart3, el: <Cusum /> },
  { id: "mv", label: "Before / After M&V", icon: ClipboardCheck, el: <Verification /> },
];

export default function App() {
  return (
    <ModeProvider>
      <div className="no-print min-h-full">
        <Header />
        <Tabs.Root defaultValue="overview" className="mx-auto max-w-[1400px] px-4 pb-10">
          <Tabs.List className="sticky top-0 z-20 -mx-4 mb-4 flex gap-1 overflow-x-auto border-b border-navy-700 bg-navy-950/95 px-4 py-2 backdrop-blur" aria-label="Dashboard sections">
            {TABS.map((t) => (
              <Tabs.Trigger key={t.id} value={t.id} className="flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold text-slate-400 transition hover:text-white data-[state=active]:bg-brand data-[state=active]:text-navy-950">
                <t.icon size={15} />{t.label}
              </Tabs.Trigger>
            ))}
          </Tabs.List>
          {TABS.map((t) => <Tabs.Content key={t.id} value={t.id} className="focus:outline-none">{t.el}</Tabs.Content>)}
          <footer className="mt-8 text-center text-xs text-slate-500">PumpRupee audits and recommends; it never controls the pump. All figures simulated (Grundfos NB 65-160/157). Indicative prices, not quotes.</footer>
        </Tabs.Root>
      </div>
      <ReportSheet />
    </ModeProvider>
  );
}
