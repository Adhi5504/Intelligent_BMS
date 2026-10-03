// PumpRupee, Schneider Electric Yuva Yodha 2026, Team ANS_4X. 12 slides. Numbers: ../RESULTS_SUMMARY.md, ../PRICES_AND_PAYBACK.md.
// Run: NODE_PATH=<dir>/node_modules node build_ppt_v2.js
const pptxgen = require("pptxgenjs");
const React = require("react");
const RDS = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

const GREEN = "3DCD58", DG = "0E5A32", INK = "16261F", MUTED = "55655D", BG = "F6FAF7", CARD = "FFFFFF",
  LINE = "D3DFD7", ORANGE = "E07B00", LORANGE = "F8D9B0", GREY = "9AA5A0", LGREEN = "E3F6E8", RED = "C0392B", AMBER = "FFF4E5";
const FONT = "Calibri";

async function icon(name, color = "FFFFFF") {
  const svg = RDS.renderToStaticMarkup(React.createElement(fa[name], { color: "#" + color, size: 256 }));
  return "image/png;base64," + (await sharp(Buffer.from(svg)).png().toBuffer()).toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.title = "PumpRupee - Schneider Electric Yuva Yodha 2026 - Team ANS_4X";
  pres.author = "ANS_4X";
  const S = pres.shapes;
  pres.defineSlideMaster({
    title: "CONTENT", background: { color: BG },
    objects: [{ text: { text: "PumpRupee  |  Team ANS_4X  |  Yuva Yodha 2026, Smart Manufacturing  |  All results simulated; prices indicative, not quotes",
      options: { x: 0.6, y: 7.08, w: 10.8, h: 0.3, fontFace: FONT, fontSize: 10, color: MUTED, margin: 0 } } }],
    slideNumber: { x: 12.3, y: 7.08, w: 0.5, h: 0.3, fontFace: FONT, fontSize: 10, color: MUTED },
  });
  pres.defineSlideMaster({ title: "TITLE", background: { color: BG } });

  const T = (s, text, o = {}) => s.addText(text, Object.assign({ isTextBox: true, fontFace: FONT, color: INK, margin: 0, valign: "top" }, o));
  const card = (s, x, y, w, h, o = {}) => s.addShape(S.ROUNDED_RECTANGLE, Object.assign({ x, y, w, h, rectRadius: 0.08, fill: { color: CARD }, line: { color: LINE, width: 1 } }, o));
  const head = (s, title, msg) => {
    T(s, title, { x: 0.6, y: 0.3, w: 12.1, h: 0.65, fontSize: 30, bold: true, color: DG });
    if (msg) T(s, msg, { x: 0.6, y: 0.95, w: 12.1, h: 0.4, fontSize: 16, color: MUTED });
  };
  const circ = async (s, x, y, d, ic, fill = DG) => {
    s.addShape(S.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 } });
    s.addImage({ data: await icon(ic), x: x + d * 0.24, y: y + d * 0.24, w: d * 0.52, h: d * 0.52 });
  };
  const arrow = (s, x, y, w = 0.4, h = 0.3, color = GREEN) => s.addShape(S.RIGHT_ARROW, { x, y, w, h, fill: { color }, line: { color, width: 0 } });
  const tag = (s, text, x, y, w, fill = DG, color = "FFFFFF", fs = 12) => {
    s.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h: 0.34, rectRadius: 0.17, fill: { color: fill }, line: { color: fill, width: 0 } });
    T(s, text, { x, y, w, h: 0.34, fontSize: fs, bold: true, color, align: "center", valign: "middle" });
  };
  const banner = (s, text, y, h = 0.65, fill = DG, fs = 20) => {
    s.addShape(S.ROUNDED_RECTANGLE, { x: 0.6, y, w: 12.15, h, rectRadius: 0.1, fill: { color: fill }, line: { color: fill, width: 0 } });
    T(s, text, { x: 0.6, y, w: 12.15, h, fontSize: fs, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  };
  const bullets = (arr, o = {}) => arr.map((t, k) => ({ text: t, options: Object.assign({ bullet: true, breakLine: k < arr.length - 1, paraSpaceAfter: 4 }, o) }));

  function skid(s, ox, oy, sc, labels = true) {
    const R = (x, y, w, h, o) => s.addShape(o.shape || S.RECTANGLE, Object.assign({ x: ox + x * sc, y: oy + y * sc, w: w * sc, h: h * sc, line: { color: o.fill, width: 0 } }, o, { fill: { color: o.fill } }));
    const L = (x1, y1, x2, y2, color, w = 1.5, dash) => s.addShape(S.LINE, { x: ox + x1 * sc, y: oy + y1 * sc, w: (x2 - x1) * sc, h: (y2 - y1) * sc, line: { color, width: w, dashType: dash } });
    const TX = (t, x, y, w, h, o = {}) => T(s, t, Object.assign({ x: ox + x * sc, y: oy + y * sc, w: w * sc, h: h * sc, fontSize: 12 }, o));
    R(0.3, 3.55, 6.6, 0.3, { fill: GREY });
    R(0.6, 2.0, 2.4, 1.55, { fill: "3A4A45", shape: S.ROUNDED_RECTANGLE, rectRadius: 0.1 });
    for (let i = 0; i < 6; i++) R(0.85 + i * 0.33, 2.1, 0.12, 1.35, { fill: "55675F" });
    R(3.0, 2.6, 0.45, 0.4, { fill: "7C8A84" }); R(3.4, 1.9, 1.6, 1.6, { fill: "2E7D5B", shape: S.OVAL });
    R(4.05, 0.5, 0.3, 1.5, { fill: "B0BEC5" }); R(4.05, 0.5, 2.85, 0.3, { fill: "B0BEC5" }); R(4.8, 2.75, 2.1, 0.3, { fill: "B0BEC5" });
    R(5.7, 2.6, 0.5, 0.6, { fill: "C9A227" }); R(5.35, 0.35, 0.6, 0.6, { fill: ORANGE, shape: S.DIAMOND });
    R(5.62, 0.12, 0.06, 0.25, { fill: "444444" }); R(5.5, 0.06, 0.3, 0.08, { fill: "444444" }); R(4.67, 0.3, 0.1, 0.22, { fill: "444444" });
    R(4.55, 0.0, 0.35, 0.3, { fill: GREEN, shape: S.ROUNDED_RECTANGLE, rectRadius: 0.05 });
    R(5.78, 2.3, 0.3, 0.3, { fill: GREEN, shape: S.ROUNDED_RECTANGLE, rectRadius: 0.05 });
    R(2.37, 0.8, 0.06, 1.2, { fill: "222222" }); R(2.0, 0.0, 1.6, 0.8, { fill: DG, shape: S.ROUNDED_RECTANGLE, rectRadius: 0.08 }); R(3.42, 0.08, 0.1, 0.1, { fill: GREEN, shape: S.OVAL });
    s.addShape(S.DONUT, { x: ox + 2.2 * sc, y: oy + 1.2 * sc, w: 0.4 * sc, h: 0.4 * sc, fill: { color: GREEN }, line: { color: GREEN, width: 0 } });
    L(3.6, 0.15, 4.55, 0.15, GREEN, 1.5, "dash");
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
  const chartBase = { catGridLine: { style: "none" }, valGridLine: { style: "none" }, valAxisHidden: true, catAxisLabelFontFace: FONT, dataLabelFontFace: FONT, legendFontFace: FONT };

  // ===== 1. TITLE =====
  let s = pres.addSlide({ masterName: "TITLE" });
  T(s, "PumpRupee", { x: 0.7, y: 1.0, w: 5.8, h: 1.0, fontSize: 56, bold: true, color: DG });
  T(s, "Pricing pump energy waste in rupees", { x: 0.7, y: 2.1, w: 5.7, h: 1.0, fontSize: 28 });
  T(s, "A clamp-on audit kit that tells you if a VFD will pay back for THAT pump.", { x: 0.7, y: 3.25, w: 5.6, h: 0.8, fontSize: 18, color: MUTED });
  tag(s, "No flow meter", 0.7, 4.2, 1.7); tag(s, "No shutdown", 2.5, 4.2, 1.5); tag(s, "₹ waste by cause", 4.1, 4.2, 2.1);
  T(s, "Schneider Electric Yuva Yodha Energy Tech Hackathon 2026", { x: 0.7, y: 4.85, w: 5.8, h: 0.6, fontSize: 14, bold: true, color: DG });
  T(s, "Track: Smart Manufacturing\nElectrify · Automate · Digitalise", { x: 0.7, y: 5.5, w: 5.8, h: 0.6, fontSize: 13, color: MUTED });
  T(s, "Team ANS_4X", { x: 0.7, y: 6.25, w: 5.8, h: 0.4, fontSize: 20, bold: true });
  skid(s, 6.3, 2.5, 0.95, true);
  T(s, "All results are simulated (Grundfos NB 65-160/157, 11 kW). Prices are indicative online prices, not quotes.", { x: 6.3, y: 6.4, w: 6.6, h: 0.5, fontSize: 12, italic: true, color: MUTED });
  s.addNotes("30 seconds: pumps are oversized and run throttled; the energy is burnt across the valve. Owners cannot see it because flow is hard to measure. PumpRupee is a clamp-on kit that prices the waste in rupees and says whether a VFD will pay back for that pump. It audits and recommends; it never controls the pump.");

  // ===== 2. PROBLEM =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Problem: Invisible Waste", "Oversized pumps run throttled. The extra energy is burnt across a valve, every hour.");
  const ps = [["FaIndustry", "Oversized pump", "Sized above the real duty"], ["FaFaucet", "Valve half shut", "Throttled to hold flow"],
    ["FaFire", "Energy lost as heat", "Head burnt in the valve"], ["FaRupeeSign", "₹ leaking", "On every bill"]];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.19;
    card(s, x, 1.5, 2.55, 1.65);
    await circ(s, x + 0.15, 1.62, 0.6, ps[i][0], i === 3 ? ORANGE : DG);
    T(s, [{ text: ps[i][1], options: { bold: true, fontSize: 16, breakLine: true } }, { text: ps[i][2], options: { fontSize: 12, color: MUTED } }], { x: x + 0.15, y: 2.32, w: 2.3, h: 0.75 });
    if (i < 3) arrow(s, x + 2.65, 2.15, 0.45, 0.32);
  }
  card(s, 0.6, 3.4, 12.15, 1.15, { fill: { color: AMBER }, line: { color: ORANGE, width: 1.5 } });
  await circ(s, 0.8, 3.65, 0.65, "FaSearchDollar", ORANGE);
  T(s, [{ text: "The owner is blind to it.", options: { bold: true, fontSize: 20, color: ORANGE, breakLine: true } },
    { text: "Flow is hard and costly to measure. An energy-audit practitioner reports that 30–40% of ultrasonic flow readings go wrong. Head (pressure) and electrical power are easy to measure.", options: { fontSize: 14 } }],
    { x: 1.65, y: 3.47, w: 10.9, h: 1.0, valign: "middle" });
  const st2 = [["Most common cause", "Wrong sizing leads to throttling (practitioner report)", GREY], ["83–93%", "of simulated waste is the valve (72–87% under stress)", ORANGE], ["8–45%", "VFD saving across simulated cases; 5–40% reported in practice", DG]];
  st2.forEach((c, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 4.8, 3.95, 1.55);
    T(s, c[0], { x: x + 0.2, y: 4.9, w: 3.6, h: 0.6, fontSize: i === 0 ? 20 : 32, bold: true, color: c[2] === GREY ? INK : c[2], valign: "middle" });
    T(s, c[1], { x: x + 0.2, y: 5.55, w: 3.6, h: 0.75, fontSize: 13, color: MUTED });
  });
  T(s, "Simulated figures: Grundfos NB 65-160/157, 11 kW. The 83–93% valve share is measured against a speed-matched, healthy, clean ideal.", { x: 0.6, y: 6.5, w: 12.1, h: 0.4, fontSize: 12, italic: true, color: MUTED });
  s.addNotes("The 5-40% is the practitioner's reported range; 8-45% is our simulated range across oversizing and lift cases. Keep the two separate.");

  // ===== 3. WHY EXISTING OPTIONS DON'T REACH MSMEs =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Why Today's Options Rarely Reach MSMEs", "Each option is valuable. None is a low-cost entry point that ends in a ₹ decision.");
  const cols = ["Flow-meter retrofit", "One-time manual audit", "Full monitoring platform", "PumpRupee"];
  const rowsT = [["Upfront cost, small plant", ["Meter + install", "Fee per visit", "Typically higher", "₹6,100–13,300"]],
    ["No plant shutdown", ["P", "Y", "P", "Y"]], ["Answer in ₹", ["N", "Y", "P", "Y"]], ["Waste split by cause", ["N", "Y", "P", "Y"]],
    ["Pump-specific VFD verdict", ["N", "Y", "P", "Y"]], ["Verifies saving afterwards", ["P", "P", "Y", "Y"]], ["Suited to small MSMEs", ["P", "N", "P", "Y"]]];
  const ic = { Y: await icon("FaCheckCircle", DG), N: await icon("FaTimesCircle", RED), P: await icon("FaMinusCircle", "D99A00") };
  const x0 = 3.65, cw = 2.2, gap = 0.07;
  cols.forEach((c, i) => {
    const x = x0 + i * (cw + gap), last = i === 3;
    s.addShape(S.ROUNDED_RECTANGLE, { x, y: 1.5, w: cw, h: 0.7, rectRadius: 0.06, fill: { color: last ? DG : "E8EEEA" }, line: { color: last ? DG : LINE, width: 1 } });
    T(s, c, { x, y: 1.5, w: cw, h: 0.7, fontSize: 14, bold: true, color: last ? "FFFFFF" : INK, align: "center", valign: "middle" });
  });
  rowsT.forEach((r, ri) => {
    const y = 2.3 + ri * 0.56;
    s.addShape(S.RECTANGLE, { x: 0.6, y, w: 12.13, h: 0.5, fill: { color: ri % 2 ? "EEF4F0" : CARD }, line: { color: LINE, width: 0.5 } });
    T(s, r[0], { x: 0.75, y, w: 2.85, h: 0.52, fontSize: 14, bold: true, valign: "middle" });
    r[1].forEach((v, i) => {
      const x = x0 + i * (cw + gap);
      if (v.length === 1) s.addImage({ data: ic[v], x: x + cw / 2 - 0.17, y: y + 0.09, w: 0.34, h: 0.34 });
      else T(s, v, { x, y, w: cw, h: 0.52, fontSize: 13, bold: i === 3, color: i === 3 ? DG : INK, align: "center", valign: "middle" });
    });
  });
  T(s, "✔ yes    ~ partly / varies by product    ✘ no.  Our general assessment, not a product test. PumpRupee's ticks are design targets (simulated, not field-proven).",
    { x: 0.6, y: 6.28, w: 12.1, h: 0.3, fontSize: 11, italic: true, color: MUTED });
  banner(s, "Full platforms are the natural NEXT step after PumpRupee, not a rival.", 6.62, 0.4, DG, 15);
  s.addNotes("Fair comparison. Say clearly that platforms such as EcoStruxure are what an MSME graduates to once the audit has shown where the money is.");

  // ===== 4. SOLUTION =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Our Solution: A ₹ Audit Kit", "A clamp-on kit turns power + pressure readings into “₹ wasted per year, and why”.");
  skid(s, 0.7, 2.1, 0.95, true);
  const outs = [["FaRupeeSign", "₹ waste per year", "Pump energy waste priced in rupees"], ["FaChartPie", "Waste by cause", "Valve, impeller wear, clogged strainer"],
    ["FaSlidersH", "Cheapest fix first + setpoint", "Lowest safe VFD setpoint"], ["FaSearchDollar", "VFD payback verdict", "For THIS pump, before capex"]];
  for (let i = 0; i < 4; i++) {
    const y = 1.55 + i * 1.08;
    card(s, 7.9, y, 4.85, 0.93);
    await circ(s, 8.05, y + 0.15, 0.6, outs[i][0]);
    T(s, [{ text: outs[i][1], options: { bold: true, fontSize: 17, breakLine: true } }, { text: outs[i][2], options: { fontSize: 13, color: MUTED } }], { x: 8.85, y: y + 0.1, w: 3.8, h: 0.75 });
  }
  T(s, "VFD = control speed instead of strangling the pipe.", { x: 7.9, y: 5.9, w: 4.85, h: 0.3, fontSize: 12, italic: true, color: MUTED });
  banner(s, "Audits and recommends. Does not control the pump.", 6.25, 0.65, DG, 22);
  s.addNotes("The kit is read-only: clamp on the motor cable, sensors on existing gauge ports. The owner keeps the data.");

  // ===== 5. HOW IT WORKS =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "How It Works: Install & Pump Curve", "Clamp on, log for a week or two, and let the maths find the waste.");
  const bx = [["Motor", "Power clamp\n(CT on cable)", "3A4A45"], ["Pump", "P1 suction (optional)\nP2 discharge", "2E7D5B"], ["Throttle valve", "P3 process-side\n(optional)", ORANGE], ["Process", "", GREY]];
  bx.forEach((b, i) => {
    const x = 0.6 + i * 1.7;
    s.addShape(S.ROUNDED_RECTANGLE, { x, y: 1.6, w: 1.4, h: 0.9, rectRadius: 0.08, fill: { color: b[2] }, line: { color: b[2], width: 0 } });
    T(s, b[0], { x, y: 1.6, w: 1.4, h: 0.9, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    if (b[1]) T(s, b[1], { x: x - 0.1, y: 2.6, w: 1.6, h: 0.7, fontSize: 11, bold: true, color: DG, align: "center" });
    if (i < 3) arrow(s, x + 1.43, 1.9, 0.24, 0.3);
  });
  card(s, 0.6, 3.5, 6.5, 1.25, { fill: { color: LGREEN }, line: { color: GREEN, width: 1.5 } });
  T(s, [{ text: "Minimum kit: power clamp + discharge pressure (P2).", options: { bold: true, fontSize: 14, breakLine: true } },
    { text: "Add P3 (process-side) when a VFD purchase is on the table: it measures the system curve and reveals a clogged strainer.", options: { fontSize: 13 } }],
    { x: 0.75, y: 3.55, w: 6.2, h: 1.15, valign: "middle" });
  const rv = [["P2 + power", "Waste priced in ₹ (basic)"], ["+ P3 (about ₹3,068)", "Error 10.5 → 1.4 pts (stress, simulated)"], ["+ P1 / strainer ΔP", "Clog made visible"]];
  rv.forEach((r, i) => {
    T(s, [{ text: r[0] + "  ", options: { bold: true, color: DG } }, { text: r[1] }], { x: 0.75, y: 4.85 + i * 0.36, w: 6.3, h: 0.34, fontSize: 13 });
  });
  T(s, "System curve = what the pipe network demands.  Pump curve = what the pump can deliver at a given speed.", { x: 0.6, y: 6.1, w: 6.5, h: 0.6, fontSize: 12, italic: true, color: MUTED });
  // chart: schematic curves
  const Q = [0, 1, 2, 3, 4, 5, 6, 7], f = v => Math.round(v * 10) / 10;
  const pump = Q.map(q => f(40 - 0.35 * q * q)), sysOpen = Q.map(q => f(12 + 0.12 * q * q)), sysThr = Q.map(q => f(12 + 0.428 * q * q)), vfd = Q.map(q => f(28.9 - 0.35 * q * q));
  card(s, 7.35, 1.5, 5.4, 5.2);
  T(s, "Throttled point vs VFD point (schematic)", { x: 7.5, y: 1.58, w: 5.1, h: 0.35, fontSize: 15, bold: true, color: DG });
  s.addChart(pres.charts.LINE, [
    { name: "Pump curve, full speed", labels: Q.map(String), values: pump }, { name: "System, valve open", labels: Q.map(String), values: sysOpen },
    { name: "System, throttled", labels: Q.map(String), values: sysThr }, { name: "Pump curve, slowed by VFD", labels: Q.map(String), values: vfd }],
    { x: 7.45, y: 1.95, w: 5.2, h: 3.4, chartColors: [DG, GREY, ORANGE, GREEN], lineSize: 3, lineDataSymbol: "none", lineDash: ["solid", "solid", "solid", "dash"],
      showLegend: true, legendPos: "b", legendFontSize: 10, legendFontFace: FONT, catAxisLabelFontSize: 10, catAxisLabelFontFace: FONT, valAxisLabelFontSize: 10, valAxisLabelFontFace: FONT,
      valGridLine: { color: "E6ECE8", size: 0.5 }, catGridLine: { style: "none" }, showCatAxisTitle: true, catAxisTitle: "Flow →", catAxisTitleFontSize: 11,
      showValAxisTitle: true, valAxisTitle: "Head →", valAxisTitleFontSize: 11, valAxisMinVal: 0, valAxisMaxVal: 45 });
  T(s, [{ text: "Same flow, two ways to get it.", options: { bold: true, fontSize: 13, breakLine: true } },
    { text: "Throttled: pump pushes at full head, the valve burns the gap. VFD: the pump slows to just what the pipe needs. The gap is the wasted head, and it is priced in ₹.", options: { fontSize: 12 } }],
    { x: 7.5, y: 5.4, w: 5.1, h: 1.25 });
  s.addNotes("Curves are schematic and illustrative shapes, not the Grundfos data. Real fits are in the simulation scripts.");

  // ===== 6. ANALYTICS + ACCURACY =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Analytics & Honest Accuracy", "Six plain steps from raw logs to a ₹ report, with the uncertainty stated.");
  const pl = [["FaDatabase", "Raw logs", "Power + pressure, 7–14 days"], ["FaSlidersH", "Calibration", "Fit the real pump from its logs; optional anchors: shut-off head, closed-valve power"],
    ["FaTint", "Flow inference", "Pump curve + power + head give flow"], ["FaBalanceScale", "Shapley split", "A fair split of blame between causes"],
    ["FaBell", "CUSUM check", "Early alarm when the pump slowly wears"], ["FaFileInvoiceDollar", "₹ report", "₹/yr, SEC, fixes, setpoint. SEC = units of electricity per m³ pumped"]];
  for (let i = 0; i < 6; i++) {
    const x = 0.6 + i * 2.046;
    card(s, x, 1.45, 1.9, 1.75);
    await circ(s, x + 0.12, 1.55, 0.45, pl[i][0], i === 5 ? ORANGE : DG);
    T(s, pl[i][1], { x: x + 0.62, y: 1.55, w: 1.25, h: 0.45, fontSize: 13, bold: true, valign: "middle" });
    T(s, pl[i][2], { x: x + 0.1, y: 2.1, w: 1.72, h: 1.05, fontSize: 11 });
    if (i < 5) arrow(s, x + 1.9, 2.15, 0.14, 0.2);
  }
  card(s, 0.6, 3.4, 6.3, 3.55);
  T(s, "Forecast error, percentage points (simulated)", { x: 0.75, y: 3.47, w: 6, h: 0.35, fontSize: 14, bold: true, color: DG });
  const cl = ["Datasheet", "Logs", "Logs + P3"];
  s.addChart(pres.charts.BAR, [{ name: "Friendly test (1% noise)", labels: cl, values: [7.2, 1.6, null] }, { name: "Stress test (3% noise, curve errors)", labels: cl, values: [8.4, 10.5, 1.4] }],
    Object.assign({}, chartBase, { x: 0.7, y: 3.8, w: 6.1, h: 2.15, barDir: "col", barGrouping: "clustered", chartColors: [GREY, ORANGE], showValue: true, dataLabelFontSize: 11, dataLabelFormatCode: "0.0",
      dataLabelPosition: "outEnd", catAxisLabelFontSize: 10, catAxisLabelRotate: 0, showLegend: true, legendPos: "r", legendFontSize: 9, valAxisMinVal: 0, valAxisMaxVal: 13 }));
  T(s, [{ text: "The system curve, not the pump curve, is the main error source. A ±30% flow reading is worse than none (16.8 vs 8.3). ", options: { fontSize: 12 } },
    { text: "About ±3 points only with a measured system curve; otherwise about ±10.", options: { fontSize: 12, bold: true, color: DG } }], { x: 0.75, y: 6.0, w: 6.0, h: 0.9 });
  card(s, 7.1, 3.4, 5.65, 3.55);
  T(s, "Wear-drift check (CUSUM), simulated", { x: 7.25, y: 3.47, w: 5.3, h: 0.35, fontSize: 14, bold: true, color: DG });
  const tx = 7.5, tw = 4.85, ty = 4.35;
  s.addShape(S.LINE, { x: tx, y: ty, w: tw, h: 0, line: { color: INK, width: 2 } });
  for (const d of [0, 15, 30, 45]) { const xx = tx + tw * d / 45; s.addShape(S.LINE, { x: xx, y: ty - 0.06, w: 0, h: 0.12, line: { color: INK, width: 1 } }); T(s, String(d), { x: xx - 0.2, y: ty + 0.08, w: 0.4, h: 0.25, fontSize: 11, color: MUTED, align: "center" }); }
  T(s, "Day", { x: tx, y: ty - 0.4, w: 1, h: 0.25, fontSize: 11, color: MUTED });
  [[1, "6% step: caught next day", 4.75, ORANGE], [22, "Fast wear: alarm ~day 22 at ≈3.7%", 5.1, DG], [40, "Slow wear (0→10% in 180 d): alarm ~day 40 at ≈2.2%", 5.45, DG]].forEach(([d, t, yy, c]) => {
    const xx = tx + tw * d / 45; s.addShape(S.OVAL, { x: xx - 0.09, y: ty - 0.09, w: 0.18, h: 0.18, fill: { color: c }, line: { color: c, width: 0 } });
    T(s, t, { x: tx - 0.1, y: yy, w: tw + 0.2, h: 0.3, fontSize: 12, bold: true, color: c });
  });
  card(s, 7.25, 6.0, 5.35, 0.8, { fill: { color: LGREEN }, line: { color: GREEN, width: 1.5 } });
  T(s, "Wear caught at about 2–4%.  1 false alarm in 3 × 365 simulated days.", { x: 7.35, y: 6.0, w: 5.15, h: 0.8, fontSize: 14, bold: true, valign: "middle" });
  s.addNotes("Friendly = 1% noise and exact system curve. Stress = 3% noise, curve-shape errors, wrong static lift/friction. The stress numbers are the honest ones. The learned-from-logs number gets WORSE under stress unless the system curve is measured; that is exactly why P3 exists.");

  // ===== 7. RESULTS =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Results (Simulated)", null);
  tag(s, "SIMULATED – Grundfos NB 65-160/157, 11 kW, IE3", 0.6, 0.98, 5.4, ORANGE);
  T(s, "Assumed: 10 m static lift | 5% head margin | 16 h/day | 300 days/yr | ₹8/kWh | VFD efficiency 0.97 | 0.710 kg CO₂/kWh. Peak demand 90% of rated flow.",
    { x: 0.6, y: 1.42, w: 12.1, h: 0.35, fontSize: 12, color: MUTED });
  card(s, 0.6, 1.9, 6.6, 5.05);
  [["VFD, constant pressure", "19.3%", "₹69,292/yr | 6.1 t CO₂ | ≈8,660 kWh"], ["VFD, proportional", "35.5%", "₹1,27,178/yr | 11.3 t CO₂ | ≈15,900 kWh"]].forEach((c, i) => {
    const x = 0.75 + i * 3.2;
    card(s, x, 2.0, 3.05, 1.35, { fill: { color: LGREEN }, line: { color: GREEN, width: 1.5 } });
    T(s, c[0], { x: x + 0.1, y: 2.04, w: 2.85, h: 0.28, fontSize: 12, bold: true, color: DG });
    T(s, c[1] + " saved", { x: x + 0.1, y: 2.3, w: 2.85, h: 0.5, fontSize: 26, bold: true, color: DG });
    T(s, c[2], { x: x + 0.1, y: 2.85, w: 2.85, h: 0.45, fontSize: 11, bold: true });
  });
  s.addChart(pres.charts.BAR, [{ name: "Base case (peak 90%, 10 m lift)", labels: ["Constant pressure", "Proportional pressure"], values: [19.3, 35.5] }, { name: "Right-sized pump, 20 m lift", labels: ["Constant pressure", "Proportional pressure"], values: [8, 15] }],
    Object.assign({}, chartBase, { x: 0.7, y: 3.45, w: 6.4, h: 2.35, barDir: "col", barGrouping: "clustered", chartColors: [DG, GREY], showValue: true, dataLabelFontSize: 12, dataLabelFormatCode: "0.0",
      dataLabelPosition: "outEnd", catAxisLabelFontSize: 11, showLegend: true, legendPos: "b", legendFontSize: 10, valAxisMinVal: 0, valAxisMaxVal: 45, showTitle: true, title: "Energy saving, %", titleFontSize: 12, titleColor: MUTED }));
  T(s, [{ text: "Range: 8–33% (constant), 15–45% (proportional). ", options: { bold: true } }, { text: "54–60% for heavily oversized pumps is an upper bound only. ₹, kWh and CO₂ are consistent: kWh = ₹ ÷ 8; CO₂ = kWh × 0.710 (arithmetic)." }],
    { x: 0.8, y: 5.85, w: 6.3, h: 1.05, fontSize: 12, color: MUTED });
  card(s, 7.4, 1.9, 5.35, 5.05);
  T(s, "Where the waste goes", { x: 7.55, y: 1.98, w: 5, h: 0.35, fontSize: 15, bold: true, color: DG });
  s.addChart(pres.charts.DOUGHNUT, [{ name: "Waste", labels: ["Valve (throttling)", "Wear, clog, other"], values: [83, 17] }],
    { x: 7.45, y: 2.3, w: 2.6, h: 2.5, holeSize: 55, chartColors: [ORANGE, LINE], showLegend: false, showPercent: false, showValue: false, showLabel: false, dataBorder: { pt: 1, color: "FFFFFF" } });
  T(s, "≥83%", { x: 8.0, y: 3.25, w: 1.5, h: 0.6, fontSize: 24, bold: true, color: ORANGE, align: "center" });
  T(s, [{ text: "Valve share 83–93%", options: { bold: true, fontSize: 14, breakLine: true } }, { text: "(72–87% under stress). Donut shows the low end. Measured against a speed-matched, healthy, clean ideal.", options: { fontSize: 12, color: MUTED } }],
    { x: 10.1, y: 2.5, w: 2.55, h: 2.0 });
  card(s, 7.55, 4.95, 5.05, 1.85, { fill: { color: AMBER }, line: { color: ORANGE, width: 1.5 } });
  T(s, [{ text: "Clog blind spot", options: { bold: true, color: ORANGE, fontSize: 14, breakLine: true } },
    { text: "A clogged strainer is invisible with power + pressure alone. One extra pressure sensor recovers about ₹6,000–6,600/yr of misattributed waste.", options: { fontSize: 13 } }], { x: 7.7, y: 5.0, w: 4.8, h: 1.75, valign: "middle" });
  s.addNotes("Per-pump numbers are simulated. kWh derived as rupees divided by 8; CO2 as kWh times 0.710: 69,292/8 = 8,661 kWh -> 6.1 t; 1,27,178/8 = 15,897 kWh -> 11.3 t.");

  // ===== 8. COST & VERDICT =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Cost & VFD Verdict", null);
  tag(s, "INDICATIVE ONLINE PRICES, NOT QUOTES", 0.6, 0.98, 4.2, ORANGE);
  card(s, 0.6, 1.5, 4.3, 4.8);
  T(s, "Bill of materials (preliminary)", { x: 0.75, y: 1.57, w: 4, h: 0.35, fontSize: 15, bold: true, color: DG });
  const bom = [["ESP32 dev board", "₹399–449"], ["Power clamp, SCT-013 100 A", "₹349 + GST to ₹729"], ["Voltage sensor ZMPT101B", "₹92–289"], ["Pressure transmitter, basic", "₹2,100–3,068"],
    ["Enclosure, supply, 4–20 mA, wiring", "₹2,000 (assumed)"]];
  bom.forEach((r, i) => { const y = 1.95 + i * 0.44; T(s, r[0], { x: 0.75, y, w: 2.45, h: 0.42, fontSize: 12, valign: "middle" }); T(s, r[1], { x: 3.1, y, w: 1.7, h: 0.42, fontSize: 12, bold: true, color: DG, align: "right", valign: "middle" }); s.addShape(S.LINE, { x: 0.75, y: y + 0.43, w: 4.0, h: 0, line: { color: LINE, width: 0.5 } }); });
  [["Basic single-phase", "≈ ₹6,100"], ["3-phase + 2nd transmitter", "≈ ₹10,200"], ["3-phase + process-side (P3)", "≈ ₹13,300"], ["With ₹12,000 transmitters", "≈ ₹40,100"]].forEach((r, i) => {
    const y = 4.25 + i * 0.36; T(s, r[0], { x: 0.75, y, w: 2.8, h: 0.34, fontSize: 12, bold: true, valign: "middle" }); T(s, r[1], { x: 3.4, y, w: 1.4, h: 0.34, fontSize: 13, bold: true, color: i === 3 ? GREY : DG, align: "right", valign: "middle" });
  });
  T(s, "Hobby-grade clamps; not a certified meter. Volume cost: not estimated (no quotes).", { x: 0.75, y: 5.78, w: 4.1, h: 0.45, fontSize: 10, italic: true, color: MUTED });
  card(s, 5.1, 1.5, 3.75, 4.8);
  T(s, "Value per pump", { x: 5.25, y: 1.57, w: 3.5, h: 0.35, fontSize: 15, bold: true, color: DG });
  const vp = [["Cost per pump audited", "Kit ÷ N pumps. N = 10: ₹610–1,330"], ["Audit time per pump", "Install (assumed ½ day) + 7–14 days logging + report"], ["Kit throughput", "About 25–50 pumps/yr per kit at 7–14 days each (arithmetic, excludes travel)"],
    ["Kit payback", "₹10,200 ≈ 1.8 months of the base-case saving of ₹69,292/yr, if the audit leads to that VFD (illustrative)"]];
  vp.forEach((r, i) => T(s, [{ text: r[0], options: { bold: true, fontSize: 13, color: INK, breakLine: true } }, { text: r[1], options: { fontSize: 12, color: MUTED } }], { x: 5.25, y: 2.0 + i * 1.07, w: 3.5, h: 1.0 }));
  card(s, 9.05, 1.5, 3.7, 4.8);
  T(s, "VFD verdict (simulated)", { x: 9.2, y: 1.57, w: 3.5, h: 0.35, fontSize: 15, bold: true, color: DG });
  card(s, 9.2, 2.0, 3.4, 1.6, { fill: { color: LGREEN }, line: { color: GREEN, width: 2 } });
  T(s, [{ text: "Oversized pump", options: { fontSize: 13, bold: true, breakLine: true } }, { text: "4–19 months", options: { fontSize: 26, bold: true, color: DG, breakLine: true } }, { text: "GO: buy the VFD", options: { fontSize: 14, bold: true, color: DG } }], { x: 9.3, y: 2.05, w: 3.2, h: 1.5, valign: "middle" });
  card(s, 9.2, 3.75, 3.4, 1.6, { fill: { color: AMBER }, line: { color: ORANGE, width: 2 } });
  T(s, [{ text: "Right-sized, high lift", options: { fontSize: 13, bold: true, breakLine: true } }, { text: "2–4+ years", options: { fontSize: 26, bold: true, color: ORANGE, breakLine: true } }, { text: "WAIT: fix cheaper things first", options: { fontSize: 14, bold: true, color: ORANGE } }], { x: 9.3, y: 3.8, w: 3.2, h: 1.5, valign: "middle" });
  T(s, "VFD ₹29,000–94,000 + about ₹15,000 install (assumed): ₹50,200–1,09,400 in total.", { x: 9.2, y: 5.45, w: 3.4, h: 0.8, fontSize: 12, color: MUTED });
  banner(s, "A ~₹10k kit can stop a wrong ₹50k–1.1 lakh VFD buy, or unlock ₹69,292–1,27,178/yr (simulated)", 6.4, 0.55, DG, 14);//, 6.4, 0.55, DG, 16);
  s.addNotes("Arithmetic: 6,100/10 = 610 and 13,300/10 = 1,330. 365/14 = 26 and 365/7 = 52. 10,200/69,292 = 0.147 yr = 1.8 months. The kit payback is illustrative because it assumes the audit leads to the base-case VFD.");

  // ===== 9. ECOSYSTEM FIT =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Ecosystem Fit: Audit → Drive → Verify", "PumpRupee is the low-cost front door to VFD and energy-management adoption.");
  const eda = [["FaPlug", "Electrify", "Makes motor electrical energy visible with a clamp-on power measurement and points owners to efficient drives."],
    ["FaCogs", "Automate", "Shows which pumps justify a drive and the lowest safe setpoint. The drive does the controlling; PumpRupee never does."],
    ["FaChartLine", "Digitalise", "Logs become a ₹ business case and a before/after proof. The owner keeps the data and can use any drive."]];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.5, 3.95, 2.0);
    await circ(s, x + 0.15, 1.62, 0.55, eda[i][0]);
    T(s, eda[i][1], { x: x + 0.85, y: 1.62, w: 2.9, h: 0.55, fontSize: 20, bold: true, color: DG, valign: "middle" });
    T(s, eda[i][2], { x: x + 0.15, y: 2.3, w: 3.65, h: 1.15, fontSize: 13 });
  }
  const fl = [["PumpRupee audit", "Clamp-on, 7–14 days"], ["₹ business case", "Waste by cause + VFD verdict"], ["VFD installed", "e.g. Altivar Process"], ["PumpRupee re-measures", "Same kit, after the fix"], ["Verified saving", "Feeds energy management, e.g. EcoStruxure"]];
  for (let i = 0; i < 5; i++) {
    const x = 0.6 + i * 2.46, hl = i === 0 || i === 3;
    card(s, x, 3.85, 2.2, 1.45, { fill: { color: hl ? LGREEN : CARD }, line: { color: hl ? GREEN : LINE, width: hl ? 2 : 1 } });
    s.addShape(S.OVAL, { x: x + 0.12, y: 3.95, w: 0.38, h: 0.38, fill: { color: hl ? DG : GREY }, line: { color: hl ? DG : GREY, width: 0 } });
    T(s, String(i + 1), { x: x + 0.12, y: 3.95, w: 0.38, h: 0.38, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    T(s, [{ text: fl[i][0], options: { bold: true, fontSize: 14, breakLine: true } }, { text: fl[i][1], options: { fontSize: 12, color: MUTED } }], { x: x + 0.12, y: 4.4, w: 1.98, h: 0.85 });
    if (i < 4) arrow(s, x + 2.22, 4.4, 0.22, 0.28);
  }
  card(s, 0.6, 5.5, 7.4, 1.4, { fill: { color: LGREEN }, line: { color: GREEN, width: 1.5 } });
  T(s, [{ text: "Why this helps drive and EMS adoption", options: { bold: true, fontSize: 15, color: DG, breakLine: true } },
    { text: "MSMEs that skip audits today get a ₹ case they understand, a pump-specific verdict before capex, and proof after.", options: { fontSize: 13 } }], { x: 0.8, y: 5.55, w: 7.0, h: 1.3, valign: "middle" });
  card(s, 8.2, 5.5, 4.55, 1.4);
  T(s, [{ text: "Smart Manufacturing fit", options: { bold: true, fontSize: 15, color: DG, breakLine: true } }, { text: "Energy efficiency · productivity · digitalisation · sustainability", options: { fontSize: 13, breakLine: true } },
    { text: "Concept only: no drive or platform integration built.", options: { fontSize: 11, italic: true, color: MUTED } }], { x: 8.35, y: 5.55, w: 4.3, h: 1.3, valign: "middle" });
  s.addNotes("Schneider products are named only as examples of where an audited MSME goes next. No integration claim.");

  // ===== 10. EASE OF USE + SAFETY =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Ease of Use & Safety", "Clamp → Fit → Log → Read ₹ report → Fix → Verify.");
  const wf = [["Clamp", "On the motor cable"], ["Fit", "Sensors on gauge ports"], ["Log", "7–14 days"], ["Read", "₹ report"], ["Fix", "Cheapest first"], ["Verify", "Re-measure"], ["Move", "Kit to next pump"]];
  for (let i = 0; i < 7; i++) {
    const x = 0.6 + i * 1.75;
    card(s, x, 1.5, 1.6, 1.3);
    s.addShape(S.OVAL, { x: x + 0.1, y: 1.58, w: 0.4, h: 0.4, fill: { color: DG }, line: { color: DG, width: 0 } });
    T(s, String(i + 1), { x: x + 0.1, y: 1.58, w: 0.4, h: 0.4, fontSize: 15, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    T(s, [{ text: wf[i][0], options: { bold: true, fontSize: 15, breakLine: true } }, { text: wf[i][1], options: { fontSize: 12, color: MUTED } }], { x: x + 0.1, y: 2.05, w: 1.42, h: 0.7 });
    if (i < 6) arrow(s, x + 1.6, 2.0, 0.15, 0.22);
  }
  const no = ["A flow meter", "Pipe cutting", "Production shutdown", "Hydraulic expertise", "Reading graphs"];
  card(s, 0.6, 3.05, 5.9, 3.85);
  T(s, "The owner or technician does NOT need", { x: 0.75, y: 3.12, w: 5.6, h: 0.4, fontSize: 17, bold: true, color: DG });
  for (let i = 0; i < no.length; i++) {
    s.addImage({ data: ic.N, x: 0.8, y: 3.7 + i * 0.55, w: 0.34, h: 0.34 });
    T(s, no[i], { x: 1.3, y: 3.65 + i * 0.55, w: 5, h: 0.45, fontSize: 16, valign: "middle" });
  }
  const sf = ["Non-invasive power clamp", "Pressure sensors on existing gauge ports", "Rated enclosure; installed by a plant electrician", "Kit only recommends, never controls the pump", "Owner keeps the data"];
  card(s, 6.85, 3.05, 5.9, 3.85);
  T(s, "Safety & reliability by design", { x: 7.0, y: 3.12, w: 5.6, h: 0.4, fontSize: 17, bold: true, color: DG });
  for (let i = 0; i < sf.length; i++) {
    s.addImage({ data: ic.Y, x: 7.05, y: 3.7 + i * 0.55, w: 0.34, h: 0.34 });
    T(s, sf[i], { x: 7.55, y: 3.65 + i * 0.6, w: 5.1, h: 0.45, fontSize: 15, valign: "middle" });
  }
  T(s, "Closed-valve power / shut-off head anchors are optional, brief, and within the pump maker's limits.", { x: 7.0, y: 6.4, w: 5.6, h: 0.4, fontSize: 11, italic: true, color: MUTED });
  s.addNotes("The workflow is a design intent. No hardware has been field-tested yet.");

  // ===== 11. IMPACT, SCALABILITY, ROADMAP =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Impact, Scalability & Roadmap", null);
  tag(s, "IMPACT = SIMULATED, per 11 kW pump", 0.6, 0.98, 4.0, ORANGE);
  card(s, 0.6, 1.5, 6.1, 5.45);
  [["₹69k–1.27 lakh", "per year"], ["≈8,660–15,900", "kWh per year"], ["6.1–11.3", "t CO₂ per year"]].forEach((c, i) => {
    const x = 0.75 + i * 1.98;
    card(s, x, 1.62, 1.88, 1.2, { fill: { color: LGREEN }, line: { color: GREEN, width: 1 } });
    T(s, [{ text: c[0], options: { bold: true, fontSize: i === 0 ? 15 : 14, color: DG, breakLine: true } }, { text: c[1], options: { fontSize: 11, color: MUTED } }], { x: x + 0.05, y: 1.65, w: 1.78, h: 1.14, align: "center", valign: "middle" });
  });
  T(s, [{ text: "Scale-up illustration, not a projection: ", options: { bold: true, color: DG } }, { text: "N pumps × per-pump saving. N = 10: ₹6,92,920–12,71,780/yr and 61–113 t CO₂/yr." }], { x: 0.8, y: 2.95, w: 5.8, h: 0.75, fontSize: 12 });
  T(s, "Scalability", { x: 0.8, y: 3.75, w: 3, h: 0.3, fontSize: 14, bold: true, color: DG });
  ["Single pump", "Plant (shared kit)", "Cluster / ESCO / channel partner", "Bundled with VFD & EMS offers"].forEach((t, i) => {
    const y = 4.1 + i * 0.42;
    s.addShape(S.ROUNDED_RECTANGLE, { x: 0.8 + i * 0.25, y, w: 3.7, h: 0.36, rectRadius: 0.06, fill: { color: i === 0 ? GREEN : i === 1 ? "8ADB9B" : i === 2 ? "B8E8C2" : LGREEN }, line: { color: GREEN, width: 0.5 } });
    T(s, t, { x: 0.9 + i * 0.25, y, w: 3.5, h: 0.36, fontSize: 12, bold: true, valign: "middle" });
  });
  T(s, [{ text: "Applications: ", options: { bold: true, color: DG } }, { text: "MSME factories, water utilities, textile/dyeing, food processing, commercial HVAC chilled-water pumps. Agricultural pumping: future scope only." }], { x: 0.8, y: 5.85, w: 5.8, h: 1.0, fontSize: 12 });
  card(s, 6.9, 1.5, 5.85, 5.45);
  T(s, "Roadmap", { x: 7.05, y: 1.57, w: 3, h: 0.3, fontSize: 15, bold: true, color: DG });
  [["Simulation", "DONE", GREEN, DG], ["Bench test, real pump + sensors", "NEXT", LORANGE, ORANGE], ["Pilot, 1–2 plants, measured system curve", "PLANNED", LINE, MUTED], ["Validate forecast error", "PLANNED", LINE, MUTED], ["Multi-pump / multi-plant rollout", "PLANNED", LINE, MUTED]].forEach((r, i) => {
    const y = 1.95 + i * 0.5;
    T(s, (i + 1) + ".  " + r[0], { x: 7.05, y, w: 4.35, h: 0.42, fontSize: 13, valign: "middle" });
    tag(s, r[1], 11.5, y + 0.04, 1.1, r[2], r[3], 10);
  });
  T(s, "Validation status", { x: 7.05, y: 4.55, w: 3, h: 0.3, fontSize: 15, bold: true, color: DG });
  card(s, 7.05, 4.9, 2.75, 1.95, { fill: { color: AMBER }, line: { color: ORANGE, width: 1.5 } });
  T(s, [{ text: "SIMULATED / DESIGNED", options: { bold: true, fontSize: 11, color: ORANGE, breakLine: true } }, { text: "Savings, waste split, calibration, drift detection, cost estimates", options: { fontSize: 12 } }], { x: 7.15, y: 4.95, w: 2.55, h: 1.85 });
  card(s, 9.95, 4.9, 2.65, 1.95, { fill: { color: "EEF4F0" }, line: { color: GREY, width: 1.5 } });
  T(s, [{ text: "TO BE TESTED", options: { bold: true, fontSize: 11, color: MUTED, breakLine: true } }, { text: "Flow inference vs a reference meter; throttled-valve and blocked-strainer cases; wear drift; pilots; before/after VFD saving", options: { fontSize: 11 } }], { x: 10.05, y: 4.95, w: 2.45, h: 1.85 });
  s.addNotes("ACTUALLY TESTED: nothing yet, no hardware or field data. Say this out loud.");

  // ===== 12. ONE-VISUAL SUMMARY =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "PumpRupee on One Page", "Cheap kit. Clever inference. Answers in rupees. Honest about limits.");
  const sm = [["FaFaucet", "Oversized pump, throttled valve", ORANGE], ["FaPlug", "Clamp-on kit\n₹6,100–13,300", DG], ["FaRupeeSign", "₹ report by cause", DG], ["FaSearchDollar", "VFD verdict\nGO or WAIT", DG], ["FaCheckCircle", "Verified before/after saving", DG]];
  for (let i = 0; i < 5; i++) {
    const x = 0.6 + i * 2.46;
    card(s, x, 1.5, 2.2, 1.7);
    await circ(s, x + 0.8, 1.6, 0.6, sm[i][0], sm[i][2]);
    T(s, sm[i][1], { x: x + 0.1, y: 2.3, w: 2.0, h: 0.85, fontSize: 14, bold: true, align: "center" });
    if (i < 4) arrow(s, x + 2.22, 2.3, 0.22, 0.28);
  }
  const kt = [["19.3–35.5%", "VFD saving, base case"], ["₹69,292–1,27,178", "per year, per 11 kW pump"], ["4–19 mo vs 2–4+ yr", "payback: oversized vs right-sized"], ["≈ ±3 points", "only with a measured system curve; else ≈ ±10"]];
  kt.forEach((k, i) => {
    const x = 0.6 + i * 3.077;
    card(s, x, 3.4, 2.9, 1.3, { fill: { color: LGREEN }, line: { color: GREEN, width: 1.5 } });
    T(s, [{ text: k[0], options: { bold: true, fontSize: i === 0 ? 24 : i === 1 ? 19 : 17, color: DG, breakLine: true } }, { text: k[1], options: { fontSize: 12 } }], { x: x + 0.12, y: 3.42, w: 2.66, h: 1.26, valign: "middle", align: "center" });
  });
  T(s, "All SIMULATED (Grundfos NB 65-160/157, 11 kW; 10 m lift, 5% margin, 16 h/day, 300 days, ₹8/kWh).", { x: 0.6, y: 4.75, w: 12, h: 0.3, fontSize: 12, italic: true, color: MUTED });
  card(s, 0.6, 5.15, 12.15, 1.85, { fill: { color: AMBER }, line: { color: ORANGE, width: 2 } });
  T(s, "Honest limits: what we validate next", { x: 0.8, y: 5.2, w: 6, h: 0.3, fontSize: 14, bold: true, color: ORANGE });
  T(s, bullets(["Simulation only: no lab/field data, no real quotes", "System-curve fit uses the simulated plant's own form, so it is optimistic",
    "Single pump, steady state. Out of scope: parallel pumps, closed loops, pumps already on drives, minimum-flow/NPSH, control dynamics", "Part of the valve share is by construction; 54–60% is an upper bound"]),
    { x: 0.85, y: 5.55, w: 11.7, h: 1.4, fontSize: 12 });
  s.addNotes("Close with: cheap kit, clever inference, answers in rupees, honest about limits, brings VFD savings to MSMEs that never get audited.");

  await pres.writeFile({ fileName: "PumpRupee_ANS_4X_Yuva_Yodha.pptx" });
  console.log("written");
})();
