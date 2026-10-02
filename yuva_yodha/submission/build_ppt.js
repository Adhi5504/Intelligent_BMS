// Builds PumpRupee_Yuva_Yodha.pptx (11 slides). All numbers come from ../RESULTS_SUMMARY.md and ../PRICES_AND_PAYBACK.md.
// Run: NODE_PATH=<dir with pptxgenjs, react-icons, react, react-dom, sharp>/node_modules node build_ppt.js
const pptxgen = require("pptxgenjs");
const React = require("react");
const RDS = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

const GREEN = "3DCD58", DG = "0E5A32", INK = "16261F", MUTED = "55655D", BG = "F6FAF7",
  CARD = "FFFFFF", LINE = "D3DFD7", ORANGE = "E07B00", LORANGE = "F8D9B0", GREY = "9AA5A0", LGREEN = "E3F6E8";
const FONT = "Calibri";

async function icon(name, color = "FFFFFF") {
  const svg = RDS.renderToStaticMarkup(React.createElement(fa[name], { color: "#" + color, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  pres.title = "PumpRupee - Yuva Yodha Idea Submission";
  pres.author = "[Team name]";
  const S = pres.shapes;

  pres.defineSlideMaster({
    title: "CONTENT", background: { color: BG },
    objects: [{ text: { text: "PumpRupee  |  Yuva Yodha, Challenge 04 Smart Manufacturing  |  All results simulated; prices indicative, not quotes",
      options: { x: 0.6, y: 7.08, w: 10.5, h: 0.3, fontFace: FONT, fontSize: 10, color: MUTED, margin: 0 } } }],
    slideNumber: { x: 12.3, y: 7.08, w: 0.5, h: 0.3, fontFace: FONT, fontSize: 10, color: MUTED },
  });
  pres.defineSlideMaster({ title: "TITLE", background: { color: BG } });

  const T = (s, text, o = {}) => s.addText(text, Object.assign({ isTextBox: true, fontFace: FONT, color: INK, margin: 0, valign: "top" }, o));
  const card = (s, x, y, w, h, o = {}) => s.addShape(S.ROUNDED_RECTANGLE, Object.assign({ x, y, w, h, rectRadius: 0.08,
    fill: { color: CARD }, line: { color: LINE, width: 1 } }, o));
  const head = (s, title, msg) => {
    T(s, title, { x: 0.6, y: 0.3, w: 12.1, h: 0.65, fontSize: 30, bold: true, color: DG });
    if (msg) T(s, msg, { x: 0.6, y: 0.95, w: 12.1, h: 0.4, fontSize: 16, color: MUTED });
  };
  const circ = async (s, x, y, d, ic, fill = DG) => {
    s.addShape(S.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 } });
    s.addImage({ data: await icon(ic), x: x + d * 0.24, y: y + d * 0.24, w: d * 0.52, h: d * 0.52 });
  };
  const arrow = (s, x, y, w = 0.4, h = 0.3, color = GREEN) =>
    s.addShape(S.RIGHT_ARROW, { x, y, w, h, fill: { color }, line: { color, width: 0 } });
  const tag = (s, text, x, y, w, fill = DG, color = "FFFFFF", fs = 12) => {
    s.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h: 0.34, rectRadius: 0.17, fill: { color: fill }, line: { color: fill, width: 0 } });
    T(s, text, { x, y, w, h: 0.34, fontSize: fs, bold: true, color, align: "center", valign: "middle" });
  };

  // ---- pump skid drawing (shared by slides 1 and 3) ----
  function skid(s, ox, oy, sc, labels = true) {
    const R = (x, y, w, h, o) => s.addShape(o.shape || S.RECTANGLE, Object.assign({ x: ox + x * sc, y: oy + y * sc, w: w * sc, h: h * sc, line: { color: o.fill, width: 0 } }, o, { fill: { color: o.fill } }));
    const L = (x1, y1, x2, y2, color, w = 1.5, dash) => s.addShape(S.LINE, { x: ox + x1 * sc, y: oy + y1 * sc, w: (x2 - x1) * sc, h: (y2 - y1) * sc, line: { color, width: w, dashType: dash } });
    const TX = (t, x, y, w, h, o = {}) => T(s, t, Object.assign({ x: ox + x * sc, y: oy + y * sc, w: w * sc, h: h * sc, fontSize: 12 }, o));
    R(0.3, 3.55, 6.6, 0.3, { fill: GREY });                                  // base
    R(0.6, 2.0, 2.4, 1.55, { fill: "3A4A45", shape: S.ROUNDED_RECTANGLE, rectRadius: 0.1 }); // motor
    for (let i = 0; i < 6; i++) R(0.85 + i * 0.33, 2.1, 0.12, 1.35, { fill: "55675F" });
    R(3.0, 2.6, 0.45, 0.4, { fill: "7C8A84" });                              // coupling
    R(3.4, 1.9, 1.6, 1.6, { fill: "2E7D5B", shape: S.OVAL });                // pump casing
    R(4.05, 0.5, 0.3, 1.5, { fill: "B0BEC5" });                              // discharge riser
    R(4.05, 0.5, 2.85, 0.3, { fill: "B0BEC5" });                             // discharge line
    R(4.8, 2.75, 2.1, 0.3, { fill: "B0BEC5" });                              // suction
    R(5.7, 2.6, 0.5, 0.6, { fill: "C9A227" });                               // strainer
    R(5.35, 0.35, 0.6, 0.6, { fill: ORANGE, shape: S.DIAMOND });             // throttle valve
    R(5.62, 0.12, 0.06, 0.25, { fill: "444444" }); R(5.5, 0.06, 0.3, 0.08, { fill: "444444" });
    R(4.67, 0.3, 0.1, 0.22, { fill: "444444" });                             // transmitter stem
    R(4.55, 0.0, 0.35, 0.3, { fill: GREEN, shape: S.ROUNDED_RECTANGLE, rectRadius: 0.05 });
    R(5.78, 2.3, 0.3, 0.3, { fill: GREEN, shape: S.ROUNDED_RECTANGLE, rectRadius: 0.05 }); // optional 2nd transmitter
    R(2.37, 0.8, 0.06, 1.2, { fill: "222222" });                             // motor cable
    R(2.0, 0.0, 1.6, 0.8, { fill: DG, shape: S.ROUNDED_RECTANGLE, rectRadius: 0.08 }); // ESP32
    R(3.42, 0.08, 0.1, 0.1, { fill: GREEN, shape: S.OVAL });
    s.addShape(S.DONUT, { x: ox + 2.2 * sc, y: oy + 1.2 * sc, w: 0.4 * sc, h: 0.4 * sc, fill: { color: GREEN }, line: { color: GREEN, width: 0 } }); // clamp
    L(3.6, 0.15, 4.55, 0.15, GREEN, 1.5, "dash");
    L(5.93, 2.45, 5.93, 2.45, GREEN);
    TX("ESP32", 2.0, 0.08, 1.4, 0.3, { color: "FFFFFF", bold: true, align: "center", fontSize: 13 });
    TX("logger", 2.0, 0.4, 1.4, 0.3, { color: "FFFFFF", align: "center", fontSize: 11 });
    TX("Motor", 0.6, 2.55, 2.4, 0.4, { color: "FFFFFF", bold: true, align: "center", fontSize: 14, valign: "middle" });
    TX("Pump", 3.4, 2.5, 1.6, 0.4, { color: "FFFFFF", bold: true, align: "center", fontSize: 14, valign: "middle" });
    if (labels) {
      TX("Power clamp (on motor cable)", -0.3, 1.0, 2.35, 0.5, { align: "right", fontSize: 12, bold: true, color: DG });
      TX("Pressure transmitter", 4.3, -0.38, 2.2, 0.3, { fontSize: 12, bold: true, color: DG });
      TX("Throttle valve", 5.1, 1.0, 1.7, 0.3, { fontSize: 12, bold: true, color: ORANGE });
      TX("Strainer + optional\n2nd transmitter", 4.9, 3.25, 2.1, 0.5, { fontSize: 12, bold: true, color: DG, align: "right" });
    }
  }

  // ================= 1. TITLE =================
  let s = pres.addSlide({ masterName: "TITLE" });
  T(s, "PumpRupee", { x: 0.7, y: 1.2, w: 5.8, h: 1.0, fontSize: 56, bold: true, color: DG });
  T(s, "Pricing pump energy waste in rupees", { x: 0.7, y: 2.3, w: 5.7, h: 1.0, fontSize: 28, color: INK });
  T(s, "A low-cost, clamp-on audit kit. No flow meter.", { x: 0.7, y: 3.45, w: 5.6, h: 0.4, fontSize: 18, color: MUTED });
  tag(s, "No flow meter", 0.7, 4.2, 1.7); tag(s, "Clamp-on", 2.5, 4.2, 1.4); tag(s, "₹ waste by cause", 4.0, 4.2, 2.1);
  T(s, "Challenge 04 – Smart Manufacturing", { x: 0.7, y: 5.2, w: 5.8, h: 0.4, fontSize: 18, bold: true, color: DG });
  T(s, "Yuva Yodha | Schneider Electric Energy Tech Hackathon", { x: 0.7, y: 5.6, w: 5.8, h: 0.35, fontSize: 14, color: MUTED });
  T(s, "[Team name]  |  [Institution]", { x: 0.7, y: 6.0, w: 5.8, h: 0.35, fontSize: 14, color: MUTED });
  skid(s, 6.3, 2.7, 0.95, true);
  T(s, "All results in this deck are simulated (Grundfos NB 65-160/157, 11 kW). Prices are indicative, not quotes.",
    { x: 6.3, y: 6.55, w: 6.6, h: 0.5, fontSize: 12, italic: true, color: MUTED });
  s.addNotes("30-second pitch: oversized pumps run throttled and burn energy across a valve. Owners can't see it because flow is hard to measure. PumpRupee is a clamp-on kit (power + pressure) that prices the waste in rupees, splits it by cause, and tells you if a VFD pays back for YOUR pump. Audits and recommends; does not control the pump.");

  // ================= 2. PROBLEM =================
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Problem Statement", "Pumps are oversized and run throttled, so energy is burnt across a valve every hour.");
  const steps = [["FaIndustry", "Oversized pump", "Sized above the real duty"],
    ["FaFaucet", "Valve half shut", "Throttled to hold flow"],
    ["FaFire", "Energy lost as heat", "Head burnt in the valve"],
    ["FaRupeeSign", "₹ meter spinning", "Paid on every bill"]];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.19;
    card(s, x, 1.5, 2.55, 1.75);
    await circ(s, x + 0.15, 1.65, 0.62, steps[i][0], i === 3 ? ORANGE : DG);
    T(s, [{ text: steps[i][1], options: { bold: true, fontSize: 16, breakLine: true } }, { text: steps[i][2], options: { fontSize: 12, color: MUTED } }],
      { x: x + 0.15, y: 2.35, w: 2.3, h: 0.85 });
    if (i < 3) arrow(s, x + 2.65, 2.2, 0.45, 0.32);
  }
  T(s, "You pay for the pump AND for fighting the valve.", { x: 0.6, y: 3.35, w: 12.1, h: 0.4, fontSize: 20, bold: true, color: ORANGE });
  T(s, "Owners can't see it because flow is hard to measure: an energy-audit practitioner reports that 30–40% of ultrasonic flow readings go wrong.",
    { x: 0.6, y: 3.75, w: 12.1, h: 0.35, fontSize: 13, color: MUTED });
  T(s, "Existing approaches, and where each fits", { x: 0.6, y: 4.2, w: 8, h: 0.35, fontSize: 16, bold: true, color: DG });
  const comp = [
    ["Flow-meter retrofit", "Fits: a direct flow reading.", "Falls short: meter cost and installation; ultrasonic readings misread 30–40% (practitioner report)."],
    ["Full ESCO audit", "Fits: expert judgement and a trusted baseline.", "Falls short: a point-in-time exercise and costly, not continuous."],
    ["Vendor platforms", "Fits: deep integration with the vendor's own equipment.", "Falls short: often vendor-locked or subscription-based."],
    ["PumpRupee", "Fits: ₹ waste by cause at ₹6,100–13,300 per kit; no flow meter.", "Limit: audits only, and results are simulated so far."]];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.077, last = i === 3;
    card(s, x, 4.6, 2.9, 2.35, { fill: { color: last ? LGREEN : CARD }, line: { color: last ? GREEN : LINE, width: last ? 2.5 : 1 } });
    T(s, comp[i][0], { x: x + 0.15, y: 4.7, w: 2.6, h: 0.4, fontSize: 16, bold: true, color: last ? DG : INK });
    T(s, [{ text: comp[i][1], options: { breakLine: true, paraSpaceAfter: 6 } }, { text: comp[i][2], options: { color: MUTED } }],
      { x: x + 0.15, y: 5.15, w: 2.6, h: 1.75, fontSize: 13 });
  }
  s.addNotes("Be fair to alternatives: flow meters, ESCO audits and vendor platforms each have a place. PumpRupee's gap: continuous, low-cost, vendor-neutral, and prices waste by cause.");

  // ================= 3. SOLUTION =================
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Proposed Solution", "A clamp-on kit turns power + pressure readings into “₹ wasted per year, and why”.");
  skid(s, 0.7, 2.1, 0.95, true);
  const outs = [["FaRupeeSign", "₹ waste per year", "The pump's energy waste priced in rupees"],
    ["FaChartPie", "Waste by cause", "Valve, impeller wear, clogged strainer"],
    ["FaSlidersH", "Ranked fixes + setpoint", "Cheapest fix first; lowest safe VFD setpoint"],
    ["FaCheckCircle", "Verified saving", "Re-measure after the fix"]];
  for (let i = 0; i < 4; i++) {
    const y = 1.6 + i * 1.1;
    card(s, 7.9, y, 4.85, 0.95);
    await circ(s, 8.05, y + 0.17, 0.6, outs[i][0]);
    T(s, [{ text: outs[i][1], options: { bold: true, fontSize: 18, breakLine: true } }, { text: outs[i][2], options: { fontSize: 13, color: MUTED } }],
      { x: 8.85, y: y + 0.13, w: 3.8, h: 0.75 });
  }
  s.addShape(S.ROUNDED_RECTANGLE, { x: 0.6, y: 6.2, w: 12.15, h: 0.65, rectRadius: 0.1, fill: { color: DG }, line: { color: DG, width: 0 } });
  T(s, "Audits and recommends. Does not control the pump.", { x: 0.6, y: 6.2, w: 12.15, h: 0.65, fontSize: 22, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  s.addNotes("Hardware: ESP32 logger, power clamp on the motor cable, pressure transmitter on the discharge, optional second transmitter at the strainer / process side. No pipe cutting for the clamp.");

  // ================= 4. ALIGNMENT =================
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Alignment to Challenge 04 – Smart Manufacturing", "Asset-level energy visibility, priced in rupees, at MSME entry cost.");
  T(s, "Challenge goal", { x: 0.6, y: 1.55, w: 4.8, h: 0.35, fontSize: 16, bold: true, color: MUTED });
  T(s, "PumpRupee feature", { x: 6.5, y: 1.55, w: 6, h: 0.35, fontSize: 16, bold: true, color: DG });
  const al = [["FaBolt", "Energy visibility at the asset level", "SEC (kWh/m³) and ₹/m³ for each pump, plus the waste split by cause"],
    ["FaTools", "Data-driven maintenance", "CUSUM wear-drift alarm (wear caught at about 2–4%); strainer clog made visible with one extra pressure sensor"],
    ["FaLeaf", "Measurable kWh and CO₂ reduction", "Before/after re-measurement; CO₂ at 0.710 kg/kWh (CEA); simulated 6.1–11.3 t CO₂/yr per 11 kW pump"],
    ["FaHandHoldingUsd", "Low-cost entry for MSMEs", "Clamp-on kit from readily available parts, about ₹6,100–13,300; no flow meter"]];
  for (let i = 0; i < 4; i++) {
    const y = 2.0 + i * 1.22;
    card(s, 0.6, y, 4.9, 1.05);
    await circ(s, 0.75, y + 0.2, 0.65, al[i][0], DG);
    T(s, al[i][1], { x: 1.55, y: y + 0.1, w: 3.85, h: 0.85, fontSize: 18, bold: true, valign: "middle" });
    arrow(s, 5.6, y + 0.36, 0.7, 0.34);
    card(s, 6.4, y, 6.35, 1.05, { fill: { color: LGREEN }, line: { color: GREEN, width: 1.5 } });
    T(s, al[i][2], { x: 6.6, y: y + 0.08, w: 6.0, h: 0.9, fontSize: 15, valign: "middle" });
  }
  s.addNotes("Challenge goals are our reading of 'Smart Manufacturing': visibility, maintenance, measurable savings, accessible to MSMEs.");

  // ================= 5. FEATURES & JOURNEY =================
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Key Features & User Journey", "From clamp-on to a verified saving, in seven steps.");
  const jr = [["Clamp on", "No pipe cutting"], ["Log 7–14 days", "Power + pressure"], ["Get ₹/yr report", "Split by cause"],
    ["Cheapest fix first", "Valve, setpoint, strainer"], ["Decide on VFD", "Payback estimate"], ["Re-measure", "Verify the saving"], ["Keep monitoring", "Wear-drift alarm"]];
  for (let i = 0; i < 7; i++) {
    const x = 0.6 + i * 1.75;
    card(s, x, 1.5, 1.6, 1.5);
    s.addShape(S.OVAL, { x: x + 0.1, y: 1.6, w: 0.42, h: 0.42, fill: { color: i === 5 ? ORANGE : DG }, line: { color: DG, width: 0 } });
    T(s, String(i + 1), { x: x + 0.1, y: 1.6, w: 0.42, h: 0.42, fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    T(s, [{ text: jr[i][0], options: { bold: true, fontSize: 14, breakLine: true } }, { text: jr[i][1], options: { fontSize: 12, color: MUTED } }],
      { x: x + 0.1, y: 2.1, w: 1.42, h: 0.85 });
    if (i < 6) arrow(s, x + 1.6, 2.1, 0.15, 0.22);
  }
  // mock owner report
  card(s, 0.6, 3.3, 7.3, 3.65, { line: { color: DG, width: 2 } });
  s.addShape(S.RECTANGLE, { x: 0.6, y: 3.3, w: 7.3, h: 0.5, fill: { color: DG }, line: { color: DG, width: 0 } });
  T(s, "Owner report: Pump P-01", { x: 0.75, y: 3.3, w: 4.3, h: 0.5, fontSize: 15, bold: true, color: "FFFFFF", valign: "middle" });
  T(s, "EXAMPLE LAYOUT | SIMULATED VALUES", { x: 5.0, y: 3.3, w: 2.8, h: 0.5, fontSize: 11, bold: true, color: GREEN, align: "right", valign: "middle" });
  const rows = [["Waste by cause", "Valve 83–93% of the waste; wear and clog share the rest"],
    ["Top fixes, in order", "1. Strainer, grease, alignment (cheap)  2. Speed control or impeller trim (largest saving)"],
    ["Recommended setpoint", "24.2 m (2.37 bar), constant pressure"],
    ["VFD saving", "19.3% = ₹69,292/yr, 6.1 t CO₂/yr"],
    ["VFD payback", "8.7–18.9 months. Example verdict: worth buying"]];
  rows.forEach((r, i) => {
    const y = 3.9 + i * 0.6;
    T(s, r[0], { x: 0.8, y, w: 2.1, h: 0.55, fontSize: 13, bold: true, color: DG, valign: "middle" });
    T(s, r[1], { x: 2.95, y, w: 4.85, h: 0.55, fontSize: 13, valign: "middle" });
    if (i < 4) s.addShape(S.LINE, { x: 0.8, y: y + 0.575, w: 6.9, h: 0, line: { color: LINE, width: 0.75 } });
  });
  const feats = [["FaMicrochip", "No flow meter", "Flow inferred from pump curve, power and head"],
    ["FaPlug", "Clamp-on install", "Off-the-shelf parts, no pipe cutting"],
    ["FaSearchDollar", "VFD verdict before you buy", "Payback for YOUR pump"],
    ["FaCheckCircle", "Before/after verification", "Re-measure after the fix"],
    ["FaBell", "Wear-drift alarm", "Catches slow impeller wear"]];
  for (let i = 0; i < 5; i++) {
    const y = 3.3 + i * 0.74;
    await circ(s, 8.2, y + 0.05, 0.52, feats[i][0]);
    T(s, [{ text: feats[i][1], options: { bold: true, fontSize: 15, breakLine: true } }, { text: feats[i][2], options: { fontSize: 12, color: MUTED } }],
      { x: 8.85, y, w: 3.95, h: 0.65 });
  }
  s.addNotes("The report is the product. Values shown are the simulated base case (peak demand 90% of rated flow), not field data.");

  // ================= 6. TECH APPROACH: ARCHITECTURE =================
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Technical Approach: Architecture & Method", "Sensors → ESP32 logger → calibration & analysis → owner report.");
  const arch = [["FaPlug", "1. Sensors", ["Power clamp (+ voltage sensor)", "Discharge pressure transmitter", "Optional strainer / process-side transmitter"]],
    ["FaMicrochip", "2. ESP32 logger", ["Logs power + pressure", "Keeps 7–14 days of records", "Clamp-on, no pipe cutting"]],
    ["FaCogs", "3. Calibration & analysis", ["Flow from pump curve", "Calibrate from logs", "Shapley split", "CUSUM wear drift"]],
    ["FaClipboardList", "4. Owner report", ["₹/yr waste, SEC kWh/m³, ₹/m³", "Ranked fixes + setpoint", "Re-measure to verify"]]];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.19;
    card(s, x, 1.5, 2.55, 2.75);
    await circ(s, x + 0.15, 1.62, 0.55, arch[i][0], i === 2 ? ORANGE : DG);
    T(s, arch[i][1], { x: x + 0.8, y: 1.62, w: 1.7, h: 0.55, fontSize: 15, bold: true, valign: "middle" });
    T(s, arch[i][2].map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < arch[i][2].length - 1, paraSpaceAfter: 4 } })),
      { x: x + 0.15, y: 2.3, w: 2.3, h: 1.9, fontSize: 13 });
    if (i < 3) arrow(s, x + 2.65, 2.7, 0.45, 0.32);
  }
  T(s, "Method in plain words", { x: 0.6, y: 4.45, w: 6, h: 0.35, fontSize: 16, bold: true, color: DG });
  const meth = [["Flow without a meter", "Pump curve + logged power + head give an estimate of flow."],
    ["Calibration", "Learn from 7–14 days of logs. Optional anchors: shut-off head, closed-valve power."],
    ["Shapley split", "A fair way to share the blame among valve, wear and clog."],
    ["CUSUM drift", "An alarm that notices slow drift, such as impeller wear."],
    ["SEC", "Units of electricity per m³ pumped (kWh/m³)."]];
  for (let i = 0; i < 5; i++) {
    const x = 0.6 + i * 2.46;
    card(s, x, 4.85, 2.3, 1.45, { fill: { color: LGREEN }, line: { color: GREEN, width: 1 } });
    T(s, [{ text: meth[i][0], options: { bold: true, fontSize: 14, color: DG, breakLine: true } }, { text: meth[i][1], options: { fontSize: 12 } }],
      { x: x + 0.1, y: 4.92, w: 2.1, h: 1.35 });
  }
  T(s, "Flow is inferred, never measured. A bad flow reading (±30%) is worse than no calibration, so PumpRupee does not depend on one.",
    { x: 0.6, y: 6.45, w: 12.1, h: 0.5, fontSize: 14, bold: true, color: ORANGE });
  s.addNotes("Be ready to explain: Shapley split = average each cause's contribution over all orders in which causes could be removed.");

  // ================= 7. TECH APPROACH: VALIDATION =================
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Technical Approach: Simulated Validation", null);
  tag(s, "SIMULATED – Grundfos NB 65-160/157, 11 kW, IE3", 0.6, 0.98, 5.4, ORANGE);
  T(s, "Assumed: 10 m static lift | 5% head margin | 16 h/day | 300 days/yr | ₹8/kWh | VFD efficiency 0.97 | 0.710 kg CO₂/kWh (CEA)",
    { x: 0.6, y: 1.42, w: 12.1, h: 0.35, fontSize: 13, color: MUTED });
  const pw = 3.9, py = 1.9, ph = 5.05, px = [0.6, 4.715, 8.83];
  ["Where the waste goes", "Forecast accuracy", "Wear-drift detection"].forEach((t, i) => {
    card(s, px[i], py, pw, ph);
    T(s, t, { x: px[i] + 0.15, y: py + 0.1, w: pw - 0.3, h: 0.4, fontSize: 17, bold: true, color: DG });
  });
  // A: waste bar
  const bx = px[0] + 0.2, bw = 3.5, by = py + 0.75;
  T(s, "Valve (throttling) share of waste", { x: bx, y: by - 0.05, w: bw, h: 0.3, fontSize: 13, bold: true });
  s.addShape(S.RECTANGLE, { x: bx, y: by + 0.35, w: bw * 0.83, h: 0.5, fill: { color: ORANGE }, line: { color: ORANGE, width: 0 } });
  s.addShape(S.RECTANGLE, { x: bx + bw * 0.83, y: by + 0.35, w: bw * 0.10, h: 0.5, fill: { color: LORANGE }, line: { color: LORANGE, width: 0 } });
  s.addShape(S.RECTANGLE, { x: bx + bw * 0.93, y: by + 0.35, w: bw * 0.07, h: 0.5, fill: { color: LINE }, line: { color: LINE, width: 0 } });
  T(s, "83–93%", { x: bx, y: by + 0.35, w: bw * 0.83, h: 0.5, fontSize: 18, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  T(s, "Rest: wear, clog, other.  Under stress tests the valve share is 72–87%. Measured against a speed-matched, healthy, clean ideal.",
    { x: bx, y: by + 0.95, w: bw, h: 0.8, fontSize: 12, color: MUTED });
  card(s, bx, by + 1.95, bw, 1.85, { fill: { color: "FFF4E5" }, line: { color: ORANGE, width: 1.5 } });
  T(s, [{ text: "Clog blind spot", options: { bold: true, color: ORANGE, fontSize: 14, breakLine: true } },
    { text: "A clogged strainer is invisible with power + pressure alone. One extra pressure sensor recovers about ₹6,000–6,600/yr of misattributed waste.", options: { fontSize: 13 } }],
    { x: bx + 0.12, y: by + 2.03, w: bw - 0.24, h: 1.7 });
  // B: chart
  s.addChart(pres.charts.BAR, [
    { name: "Friendly test (1% noise)", labels: ["Datasheet", "Learned (logs)", "+ process sensor"], values: [7.2, 1.6, null] },
    { name: "Stress test (3% noise, curve errors)", labels: ["Datasheet", "Learned (logs)", "+ process sensor"], values: [8.4, 10.5, 1.4] }],
    { x: px[1] + 0.1, y: py + 0.55, w: pw - 0.2, h: 2.55, barDir: "col", barGrouping: "clustered", chartColors: [GREY, ORANGE],
      showValue: true, dataLabelFontSize: 12, dataLabelFontFace: FONT, dataLabelFormatCode: "0.0", dataLabelPosition: "outEnd",
      catAxisLabelFontSize: 10, catAxisLabelRotate: 0, catAxisLabelFontFace: FONT, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: FONT, valAxisMinVal: 0, valAxisMaxVal: 13 });
  T(s, [{ text: "Mean error, percentage points.", options: { fontSize: 12, bold: true, breakLine: true } },
    { text: "The system curve, not the pump curve, is the main error source. A ±30% flow reading is worse than none (16.8 vs 8.3).", options: { fontSize: 12, breakLine: true } },
    { text: "About ±3 points only with a measured system curve; else about ±10.", options: { fontSize: 12, bold: true, color: DG } }],
    { x: px[1] + 0.2, y: py + 3.15, w: pw - 0.4, h: 1.85 });
  // C: drift timeline
  const tx = px[2] + 0.3, tw = 3.3, ty = py + 1.0;
  s.addShape(S.LINE, { x: tx, y: ty, w: tw, h: 0, line: { color: INK, width: 2 } });
  for (const d of [0, 15, 30, 45]) {
    const xx = tx + tw * d / 45;
    s.addShape(S.LINE, { x: xx, y: ty - 0.06, w: 0, h: 0.12, line: { color: INK, width: 1 } });
    T(s, String(d), { x: xx - 0.2, y: ty + 0.08, w: 0.4, h: 0.25, fontSize: 11, color: MUTED, align: "center" });
  }
  T(s, "Day (simulated)", { x: tx, y: ty - 0.4, w: tw, h: 0.28, fontSize: 11, color: MUTED });
  const ev = [[1, "6% step in wear: caught the next day", 1.55, ORANGE], [22, "Fast wear: alarm ~day 22 at ≈3.7% wear", 2.35, DG], [40, "Slow wear (0→10% in 180 days): alarm ~day 40 at ≈2.2% wear", 3.15, DG]];
  ev.forEach(([d, t, yy, c]) => {
    const xx = tx + tw * d / 45;
    s.addShape(S.OVAL, { x: xx - 0.09, y: ty - 0.09, w: 0.18, h: 0.18, fill: { color: c }, line: { color: c, width: 0 } });
    T(s, t, { x: tx - 0.1, y: py + yy - 0.3, w: tw + 0.2, h: 0.55, fontSize: 12, bold: true, color: c });
  });
  card(s, px[2] + 0.2, py + 3.95, 3.5, 0.9, { fill: { color: LGREEN }, line: { color: GREEN, width: 1.5 } });
  T(s, [{ text: "Wear caught at about 2–4%", options: { bold: true, fontSize: 14, breakLine: true } }, { text: "1 false alarm in 3 × 365 simulated days", options: { fontSize: 13 } }],
    { x: px[2] + 0.32, y: py + 4.0, w: 3.3, h: 0.8, valign: "middle" });
  s.addNotes("Everything on this slide is simulation. Friendly = 1% noise, curves a scaled copy of the datasheet, exact system curve. Stress = 3% noise, curve-shape errors, wrong static lift/friction. We report the stress numbers because they are the honest ones.");

  // ================= 8. INNOVATION =================
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Innovation: System-Level Packaging", "We do not claim pump monitoring, sensorless flow or VFD savings are new.");
  card(s, 0.6, 1.55, 5.7, 4.3);
  T(s, "Existing technology (we build on it)", { x: 0.8, y: 1.65, w: 5.3, h: 0.4, fontSize: 18, bold: true, color: MUTED });
  const ex = [["KSB PumpMeter", "pump monitoring"], ["US DOE PSAT", "pump energy assessment tool"], ["Samotics", "motor-current pump efficiency"],
    ["Schneider Altivar Process", "sensorless flow in the drive"], ["Indian IoT vendors, ESCOs", "monitoring and audits"]];
  ex.forEach((e, i) => {
    const y = 2.2 + i * 0.7;
    s.addShape(S.OVAL, { x: 0.85, y: y + 0.12, w: 0.2, h: 0.2, fill: { color: GREY }, line: { color: GREY, width: 0 } });
    T(s, [{ text: e[0], options: { bold: true, fontSize: 16 } }, { text: "  " + e[1], options: { fontSize: 14, color: MUTED } }], { x: 1.2, y, w: 4.95, h: 0.5, valign: "middle" });
  });
  s.addShape(S.MATH_PLUS, { x: 6.5, y: 3.3, w: 0.55, h: 0.55, fill: { color: GREEN }, line: { color: GREEN, width: 0 } });
  card(s, 7.25, 1.55, 5.5, 4.3, { fill: { color: LGREEN }, line: { color: GREEN, width: 2.5 } });
  T(s, "Our integration", { x: 7.45, y: 1.65, w: 5.1, h: 0.4, fontSize: 18, bold: true, color: DG });
  const ig = ["₹/year waste split by cause, not just an efficiency number", "Prices the extra sensor that would reveal what the basic kit cannot see",
    "Low-cost shared audit kit with no flow meter", "Before/after verification built in", "A VFD payback verdict for the owner's own pump"];
  for (let i = 0; i < 5; i++) {
    const y = 2.2 + i * 0.7;
    s.addImage({ data: await icon("FaCheckCircle", DG), x: 7.45, y: y + 0.08, w: 0.32, h: 0.32 });
    T(s, ig[i], { x: 7.95, y, w: 4.65, h: 0.62, fontSize: 15, valign: "middle" });
  }
  s.addShape(S.ROUNDED_RECTANGLE, { x: 0.6, y: 6.1, w: 12.15, h: 0.75, rectRadius: 0.1, fill: { color: DG }, line: { color: DG, width: 0 } });
  T(s, "We found no low-cost shared kit that combines all four. (A search result, not proof that none exists.)", { x: 0.6, y: 6.1, w: 12.15, h: 0.75, fontSize: 18, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  s.addNotes("Never say 'no such solution exists'. Say what we searched and what we did not find.");

  // ================= 9. IMPACT =================
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Expected Impact: Savings & Cost", null);
  tag(s, "SIMULATED – per 11 kW pump, peak demand 90% of rated flow", 0.6, 0.98, 6.3, ORANGE);
  const st = [["VFD, constant pressure", "19.3%", "₹69,292/yr", "6.1 t CO₂/yr"], ["VFD, proportional pressure", "35.5%", "₹1,27,178/yr", "11.3 t CO₂/yr"]];
  st.forEach((c, i) => {
    const x = 0.6 + i * 3.2;
    card(s, x, 1.5, 3.05, 1.55, { fill: { color: LGREEN }, line: { color: GREEN, width: 1.5 } });
    T(s, c[0], { x: x + 0.12, y: 1.55, w: 2.85, h: 0.3, fontSize: 12, bold: true, color: DG });
    T(s, c[1] + " saved", { x: x + 0.12, y: 1.85, w: 2.85, h: 0.5, fontSize: 28, bold: true, color: DG });
    T(s, c[2] + "  |  " + c[3], { x: x + 0.12, y: 2.5, w: 2.85, h: 0.45, fontSize: 13, bold: true });
  });
  s.addChart(pres.charts.BAR, [
    { name: "Base case (peak 90%, 10 m lift)", labels: ["Constant pressure", "Proportional pressure"], values: [19.3, 35.5] },
    { name: "Right-sized pump, 20 m lift", labels: ["Constant pressure", "Proportional pressure"], values: [8, 15] }],
    { x: 0.5, y: 3.1, w: 6.5, h: 2.5, barDir: "col", barGrouping: "clustered", chartColors: [DG, GREY], showValue: true, dataLabelFontSize: 12,
      dataLabelFormatCode: "0.0", dataLabelPosition: "outEnd", dataLabelFontFace: FONT, catAxisLabelFontSize: 12, catAxisLabelFontFace: FONT, valAxisHidden: true,
      valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: FONT, valAxisMinVal: 0, valAxisMaxVal: 45,
      showTitle: true, title: "Energy saving, % (simulated)", titleFontSize: 12, titleFontFace: FONT, titleColor: MUTED });
  T(s, [{ text: "Range across cases: 8–33% (constant), 15–45% (proportional). ", options: { bold: true } },
    { text: "Heavily oversized pumps reach 54–60% in the model: an upper bound only. An energy-audit practitioner reports 5–40% in practice." }],
    { x: 0.6, y: 5.6, w: 6.4, h: 0.75, fontSize: 12, color: MUTED });
  // right: cost
  card(s, 7.25, 1.5, 5.5, 5.4);
  T(s, "Cost & payback (indicative prices)", { x: 7.4, y: 1.57, w: 5.2, h: 0.35, fontSize: 14, bold: true, color: DG });
  const kit = [["Basic single-phase", 6100], ["3-phase + 2nd transmitter", 10200], ["3-phase + process-side transmitter", 13300], ["With ₹12,000 industrial transmitters", 40100]];
  const fmt = n => n >= 1000 ? (n >= 100000 ? n : String(n).replace(/\B(?=(\d{2})*\d{3}$)/g, ",")) : String(n);
  kit.forEach((k, i) => {
    const y = 2.0 + i * 0.5, wmax = 2.0;
    T(s, k[0], { x: 7.4, y, w: 2.2, h: 0.45, fontSize: 11, valign: "middle" });
    s.addShape(S.RECTANGLE, { x: 9.65, y: y + 0.07, w: wmax * k[1] / 40100, h: 0.3, fill: { color: i === 3 ? GREY : GREEN }, line: { color: i === 3 ? GREY : GREEN, width: 0 } });
    T(s, "₹" + fmt(k[1]), { x: 9.7 + wmax * k[1] / 40100, y, w: 1.0, h: 0.45, fontSize: 12, bold: true, valign: "middle" });
  });
  T(s, [{ text: "VFD for 11 kW: ", options: { bold: true } }, { text: "₹29,000–94,000 + ₹15,000 install (assumed)" }],
    { x: 7.4, y: 4.0, w: 5.2, h: 0.4, fontSize: 12 });
  T(s, "VFD payback (simulated)", { x: 7.4, y: 4.45, w: 5.2, h: 0.3, fontSize: 13, bold: true, color: DG });
  s.addShape(S.ROUNDED_RECTANGLE, { x: 7.4, y: 4.8, w: 2.45, h: 0.95, rectRadius: 0.06, fill: { color: LGREEN }, line: { color: GREEN, width: 1.5 } });
  T(s, [{ text: "Oversized pump", options: { fontSize: 11, bold: true, breakLine: true } }, { text: "4–19 months", options: { fontSize: 20, bold: true, color: DG } }], { x: 7.5, y: 4.85, w: 2.3, h: 0.85, valign: "middle" });
  s.addShape(S.ROUNDED_RECTANGLE, { x: 10.0, y: 4.8, w: 2.6, h: 0.95, rectRadius: 0.06, fill: { color: "FFF4E5" }, line: { color: ORANGE, width: 1.5 } });
  T(s, [{ text: "Right-sized, high lift", options: { fontSize: 11, bold: true, breakLine: true } }, { text: "2–4 years+", options: { fontSize: 20, bold: true, color: ORANGE } }], { x: 10.1, y: 4.85, w: 2.45, h: 0.85, valign: "middle" });
  T(s, "The audit tells you which case you are in BEFORE you spend on a VFD.", { x: 7.4, y: 5.85, w: 5.2, h: 0.55, fontSize: 14, bold: true, color: DG });
  T(s, "Audit kit cost is shared across pumps and is not included in the payback.", { x: 7.4, y: 6.45, w: 5.2, h: 0.35, fontSize: 11, color: MUTED });
  T(s, [{ text: "Who benefits: ", options: { bold: true, color: DG } }, { text: "MSME plant owners, maintenance teams, energy auditors.   " },
    { text: "Scale-up (illustration, not a projection): ", options: { bold: true, color: DG } },
    { text: "N pumps × per-pump saving. For N = 10 on the base case: ₹6,92,920/yr and 61 t CO₂/yr (constant pressure)." }],
    { x: 0.6, y: 6.4, w: 6.5, h: 0.62, fontSize: 11 });
  s.addNotes("Per-pump savings are from the simulated model with the stated assumptions. The N = 10 line is arithmetic (10 x 69,292 and 10 x 6.1), not a forecast.");

  // ================= 10. ROADMAP =================
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Implementation Roadmap", "From a simulated result to a field-validated audit kit.");
  const rm = [["Simulation", "Real Grundfos NB 65-160/157 curves; stress-tested", "DONE", GREEN, DG],
    ["Bench test", "Real pump and sensors; check inferred flow and calibration", "NEXT", LORANGE, ORANGE],
    ["Pilot, 1–2 plants", "Measure the system curve; log 7–14 days", "PLANNED", LINE, MUTED],
    ["Validate error", "Compare forecast error with the ±3-point claim", "PLANNED", LINE, MUTED],
    ["Rollout", "Multi-pump, multi-plant", "PLANNED", LINE, MUTED]];
  s.addShape(S.LINE, { x: 1.2, y: 2.15, w: 10.9, h: 0, line: { color: GREY, width: 3 } });
  for (let i = 0; i < 5; i++) {
    const x = 0.6 + i * 2.46;
    s.addShape(S.OVAL, { x: x + 0.85, y: 1.9, w: 0.5, h: 0.5, fill: { color: rm[i][3] }, line: { color: rm[i][4], width: 2 } });
    T(s, String(i + 1), { x: x + 0.85, y: 1.9, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: rm[i][4], align: "center", valign: "middle" });
    card(s, x, 2.6, 2.3, 1.75);
    T(s, [{ text: rm[i][0], options: { bold: true, fontSize: 16, breakLine: true } }, { text: rm[i][1], options: { fontSize: 12, color: MUTED, breakLine: true } }],
      { x: x + 0.1, y: 2.65, w: 2.1, h: 1.3 });
    tag(s, rm[i][2], x + 0.1, 3.95, 1.1, rm[i][3], rm[i][4], 11);
  }
  s.addShape(S.ROUNDED_RECTANGLE, { x: 0.6, y: 4.6, w: 12.15, h: 2.3, rectRadius: 0.08, fill: { color: "FFF4E5" }, line: { color: ORANGE, width: 2 } });
  T(s, "What we validate next (honest limits)", { x: 0.8, y: 4.68, w: 8, h: 0.4, fontSize: 18, bold: true, color: ORANGE });
  const lim = ["Simulation only: no lab or field data yet, and no real quotes", "About ±3 points only with a measured system curve; otherwise about ±10",
    "The system-curve fit uses the same form as the simulated plant, so it is optimistic",
    "Single pump, steady state, hourly. Next: parallel pumps, closed loops, pumps already on drives, minimum-flow and NPSH checks, control dynamics"];
  T(s, lim.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < lim.length - 1, paraSpaceAfter: 5 } })), { x: 0.85, y: 5.15, w: 11.7, h: 1.7, fontSize: 15 });
  s.addNotes("Present limits as the validation plan. Judges trust a team that states what it has not yet proven.");

  // ================= 11. TEAM =================
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Team Introduction", "[Team name]  |  [Institution]");
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.077;
    card(s, x, 1.7, 2.9, 4.3);
    s.addShape(S.OVAL, { x: x + 0.7, y: 1.95, w: 1.5, h: 1.5, fill: { color: LGREEN }, line: { color: GREEN, width: 2 } });
    s.addImage({ data: await icon("FaUser", GREEN), x: x + 1.05, y: 2.3, w: 0.8, h: 0.8 });
    T(s, [{ text: "[Name]", options: { bold: true, fontSize: 20, breakLine: true, paraSpaceAfter: 4 } }, { text: "[Role]", options: { fontSize: 15, color: DG, bold: true, breakLine: true, paraSpaceAfter: 8 } },
      { text: "[Skill: one line relevant to pumps, sensors, data or energy]", options: { fontSize: 13, color: MUTED } }],
      { x: x + 0.15, y: 3.7, w: 2.6, h: 2.2, align: "center" });
  }
  T(s, "Replace the photo circles and [placeholders]; delete unused cards (1–4 members).", { x: 0.6, y: 6.3, w: 12, h: 0.4, fontSize: 13, italic: true, color: MUTED });

  await pres.writeFile({ fileName: "PumpRupee_Yuva_Yodha.pptx" });
  console.log("written");
})();
