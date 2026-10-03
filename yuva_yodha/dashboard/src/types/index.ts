export type ControlMode = "const" | "prop";

export interface PumpTableRow {
  Q_m3h: number;
  H_m: number;
  P2_shaft_kW: number;
  P1_input_kW: number;
  eta_pump_pct: number;
}

export interface CurvePoint { q: number; h: number; p2: number; p1: number; eta: number }

export interface TelemetryRecord {
  i: number; day: number; hour: number;
  v: number; i_a: number; p1: number; pf: number;
  pd: number; ps: number; p3: number; qTrue: number;
}

export interface CalibrationRun {
  days: number; sh: number; sp: number; forecast: number; error: number;
  qInferred: number[]; meanFlowErrPct: number;
}

export interface WasteScenario {
  wear: number; foul: number; totalRsYr: number;
  rsYr: { throttle: number; wear: number; foul: number };
  pct: { throttle: number; wear: number; foul: number };
  misattrib: { S0: number; S1: number; S2: number };
}

export interface CusumRun {
  label: string; trueWear: number[]; estWear: number[]; mu: number; sd: number; k: number; h: number;
  threshold: number; S: number[]; alarm: number | null; wearAtAlarm: number | null;
  runs: number; alarmsAllRuns: (number | null)[]; medianWearAtAlarm: number | null;
}

export interface GeneratedData {
  pump: {
    table: PumpTableRow[]; hCoef: number[]; p2Coef: number[]; motor: [number, number][];
    qMin: number; qMax: number; qRated: number; hRated: number; etaVfd: number; nMin: number; profile: number[]; ef: number;
  };
  curves: CurvePoint[];
  reference: { base: number; const: number; prop: number; vol: number; hConst: number };
  telemetry: {
    records: TelemetryRecord[];
    truth: { sh: number; sp: number; saving: number };
    calibration: CalibrationRun[];
    datasheetOnly: { forecast: number; error: number; qInferred: number[] };
  };
  waste: WasteScenario[];
  cusum: Record<"control" | "slow" | "fast" | "step", CusumRun>;
  meta: { peakTelemetry: number; peakWaste: number; ratedRpmNote: string };
}
