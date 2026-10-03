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

  // ======= v3: 11-slide Yuva Yodha application deck with dashboard screenshots =======
  const fs = require("fs");
  const QRCode = require("qrcode");
  const LINK = "https://pumprupee-dashboard.vercel.app/";
  const SC = __dirname + "/screens/";
  const BOX = JSON.parse(fs.readFileSync(SC + "boxes.json", "utf8"));
  const CV = JSON.parse(fs.readFileSync(__dirname + "/curves.json", "utf8"));
  const qr = await QRCode.toDataURL(LINK, { margin: 1, width: 360, color: { dark: "#0E5A32", light: "#FFFFFF" } });
  const img = (f) => "image/png;base64," + fs.readFileSync(SC + f + ".png").toString("base64");
  const CROPS = JSON.parse(fs.readFileSync(SC + "crops.json", "utf8"));
  const ASPECT = { dash_1_overview: 1.6, dash_2_waste_split: 1.6, dash_3_vfd_payback: 1.6, dash_4_trends: 2160 / 1695 };
  const CSSW = 1440;

  /** browser frame + real screenshot + optional numbered callouts. Returns bottom y. */
  function shot(s, file, x, y, w, labels, tagText = "Working prototype dashboard · simulated data") {
    const meta = CROPS[file];
    const h = w / (meta ? meta.w / meta.h : ASPECT[file]), bar = 0.27;
    s.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h: h + bar, rectRadius: 0.06, fill: { color: "FFFFFF" }, line: { color: DG, width: 1.5 } });
    s.addShape(S.RECTANGLE, { x: x + 0.02, y: y + 0.02, w: w - 0.04, h: bar - 0.02, fill: { color: "E3F2E7" }, line: { color: "E3F2E7", width: 0 } });
    [0, 1, 2].forEach((i) => s.addShape(S.OVAL, { x: x + 0.12 + i * 0.16, y: y + 0.08, w: 0.1, h: 0.1, fill: { color: ["EF4444", "F59E0B", "3DCD58"][i] }, line: { color: "FFFFFF", width: 0 } }));
    s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.7, y: y + 0.05, w: w - 1.0, h: 0.17, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "BFE3C8", width: 0.5 } });
    T(s, "pumprupee-dashboard.vercel.app", { x: x + 0.7, y: y + 0.05, w: w - 1.0, h: 0.17, fontSize: 8, color: MUTED, align: "center", valign: "middle" });
    s.addImage({ data: img(file), x: x + 0.02, y: y + bar, w: w - 0.04, h: h - 0.02 * 0 });
    const k = (w - 0.04) / (meta ? meta.w : CSSW);
    (meta ? meta.boxes : BOX[file] || []).forEach((b, i) => {
      if (!labels || !labels[i] || !b) return;
      const bx = x + 0.02 + b.x * k, by = y + bar + b.y * k, bw = b.w * k, bh = b.h * k;
      s.addShape(S.RECTANGLE, { x: bx, y: by, w: bw, h: bh, fill: { color: "FFFFFF", transparency: 100 }, line: { color: ORANGE, width: 2 } });
      s.addShape(S.OVAL, { x: bx - 0.13, y: by - 0.13, w: 0.26, h: 0.26, fill: { color: ORANGE }, line: { color: "FFFFFF", width: 1 } });
      T(s, String(i + 1), { x: bx - 0.13, y: by - 0.13, w: 0.26, h: 0.26, fontSize: 10, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    });
    tag(s, tagText, x, y + h + bar + 0.05, Math.min(w, 4.2), ORANGE, "FFFFFF", 10);
    return y + h + bar + 0.05 + 0.34;
  }
  const legend = (s, items, x, y, w, fs = 11, st = 0.27) => items.forEach((t, i) => {
    s.addShape(S.OVAL, { x, y: y + i * st + 0.02, w: 0.2, h: 0.2, fill: { color: ORANGE }, line: { color: ORANGE, width: 0 } });
    T(s, String(i + 1), { x, y: y + i * st + 0.02, w: 0.2, h: 0.2, fontSize: 9, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    T(s, t, { x: x + 0.28, y: y + i * st, w: w - 0.3, h: 0.22, fontSize: fs, valign: "middle" });
  });
  const linkBlock = (s, x, y, qrSize = 0.95) => {
    s.addImage({ data: qr, x, y, w: qrSize, h: qrSize });
    T(s, [{ text: "Live prototype dashboard", options: { bold: true, fontSize: 13, color: DG, breakLine: true } }, { text: LINK, options: { fontSize: 12, color: DG, hyperlink: { url: LINK }, breakLine: true } },
      { text: "Simulated data · scan the QR code", options: { fontSize: 10, color: MUTED } }], { x: x + qrSize + 0.15, y: y + 0.08, w: 4.2, h: qrSize });
  };
  const ic = { Y: await icon("FaCheckCircle", DG), N: await icon("FaTimesCircle", RED), P: await icon("FaMinusCircle", "D99A00") };

  // ===== 1. TITLE =====
  let s = pres.addSlide({ masterName: "TITLE" });
  T(s, "PumpRupee", { x: 0.7, y: 0.75, w: 5.8, h: 0.95, fontSize: 54, bold: true, color: DG });
  T(s, "Find the rupees your pumps waste, before you buy a VFD", { x: 0.7, y: 1.8, w: 5.6, h: 1.3, fontSize: 25 });
  tag(s, "No flow meter", 0.7, 3.3, 1.7); tag(s, "No shutdown", 2.5, 3.3, 1.5); tag(s, "₹ waste by cause", 4.1, 3.3, 2.1);
  T(s, "Team ANS_4X", { x: 0.7, y: 4.0, w: 5.8, h: 0.4, fontSize: 22, bold: true });
  T(s, "Schneider Electric Yuva Yodha Energy Tech Hackathon 2026", { x: 0.7, y: 4.45, w: 5.7, h: 0.5, fontSize: 13, color: MUTED });
  T(s, "Track: Smart Manufacturing  ·  Electrify · Automate · Digitalise", { x: 0.7, y: 4.95, w: 5.7, h: 0.3, fontSize: 12, bold: true, color: DG });
  linkBlock(s, 0.7, 5.6);
  shot(s, "dash_1_overview", 6.75, 1.25, 6.0, null);
  T(s, "All results are simulated (Grundfos NB 65-160/157, 11 kW). Prices are indicative, not quotes.", { x: 6.75, y: 5.95, w: 6.0, h: 0.4, fontSize: 11, italic: true, color: MUTED });
  s.addNotes("Open the live dashboard from the QR code. Simulated data throughout. One sentence: PumpRupee tells an MSME owner how many rupees a pump wastes, why, and whether a VFD will pay back for that pump, using a cheap clamp-on kit and no flow meter.");

  // ===== 2. PROBLEM =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Problem Statement", "Oversized pumps run throttled. The extra energy is burnt across a valve, every hour, and nobody sees it.");
  const ps = [["FaIndustry", "Oversized pump", "Sized above the real duty"], ["FaFaucet", "Valve half shut", "Throttled to hold flow"], ["FaFire", "Energy lost as heat", "Head burnt in the valve"], ["FaRupeeSign", "₹ leaking", "On every bill"]];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.19;
    card(s, x, 1.5, 2.55, 1.75);
    await circ(s, x + 0.15, 1.65, 0.62, ps[i][0], i === 3 ? ORANGE : DG);
    T(s, [{ text: ps[i][1], options: { bold: true, fontSize: 16, breakLine: true } }, { text: ps[i][2], options: { fontSize: 12, color: MUTED } }], { x: x + 0.15, y: 2.38, w: 2.3, h: 0.8 });
    if (i < 3) arrow(s, x + 2.65, 2.2, 0.45, 0.32);
  }
  T(s, "You pay for the pump AND for fighting the valve.", { x: 0.6, y: 3.45, w: 12.1, h: 0.45, fontSize: 22, bold: true, color: ORANGE });
  const facts = [["FaCogs", "Oversizing is common", "An energy-audit practitioner: wrong sizing leading to throttling is the most common cause."], ["FaTint", "Flow is hard to measure", "Ultrasonic meters: 30–40% of readings go wrong (practitioner report). Pressure and power are easy."], ["FaFileInvoiceDollar", "Audits miss small plants", "Full audits are a poor fit for small plants; very small plants rarely prioritise this."]];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.1;
    card(s, x, 4.15, 3.95, 2.1);
    await circ(s, x + 0.2, 4.3, 0.55, facts[i][0]);
    T(s, facts[i][1], { x: x + 0.9, y: 4.3, w: 2.9, h: 0.55, fontSize: 16, bold: true, valign: "middle" });
    T(s, facts[i][2], { x: x + 0.2, y: 5.0, w: 3.55, h: 1.2, fontSize: 13, color: MUTED });
  }
  T(s, "Head (pressure) and electrical power are cheap to measure. Flow is not. PumpRupee infers flow from the two that are.", { x: 0.6, y: 6.4, w: 12.1, h: 0.5, fontSize: 14, bold: true, color: DG });
  s.addNotes("Anchor on the owner being blind. The 30-40% figure is an audit practitioner's report about ultrasonic meters, not our measurement.");

  // ===== 3. PROPOSED SOLUTION =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Proposed Solution", "A clamp-on kit and a web dashboard turn power + pressure into “₹ wasted per year, and why”.");
  skid(s, 0.55, 2.0, 0.78, true);
  T(s, "Concept illustration of the kit on a pump skid", { x: 0.6, y: 5.35, w: 5.5, h: 0.25, fontSize: 10, italic: true, color: MUTED });
  const outs3 = [["FaRupeeSign", "₹ waste per year, by cause"], ["FaSlidersH", "Cheapest fix first + safe setpoint"], ["FaSearchDollar", "VFD payback verdict for THIS pump"], ["FaCheckCircle", "Verified saving after the fix"]];
  const b3 = shot(s, "dash_3_vfd_payback", 6.9, 1.4, 5.5, null);
  for (let i = 0; i < 4; i++) {
    const x = 6.9 + (i % 2) * 2.85, y = b3 + 0.0 + Math.floor(i / 2) * 0.33;
    s.addImage({ data: ic.Y, x, y: y + 0.03, w: 0.24, h: 0.24 });
    T(s, outs3[i][1], { x: x + 0.34, y, w: 2.5, h: 0.32, fontSize: 10.5, bold: true, valign: "middle" });
  }
  T(s, "Clamp on → log 7–14 days → ₹ report → the right fix", { x: 0.6, y: 5.75, w: 5.6, h: 0.4, fontSize: 15, bold: true, color: DG });
  banner(s, "Audits and recommends. Does not control the pump.", 6.4, 0.55, DG, 18);
  s.addNotes("The dashboard shown is the working prototype with simulated data. The kit is clamp-on: no pipe cutting, no shutdown. It never controls the pump.");

  // ===== 4. ALIGNMENT =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Alignment to Smart Manufacturing", "Electrify · Automate · Digitalise, at an entry cost an MSME can afford.");
  const eda = [["FaPlug", "Electrify", ["Makes motor energy visible with a clamp-on power measurement", "Points owners to the pumps where a right-sized drive pays back"]],
    ["FaCogs", "Automate", ["Automatic diagnosis of waste by cause", "Wear-drift alarm (CUSUM) on the pump", "Lowest safe VFD setpoint; the drive does the controlling"]],
    ["FaChartLine", "Digitalise", ["Logs become a ₹ business case on a dashboard", "Before/after proof of the saving", "Owner keeps the data and can use any drive"]]];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.5, 3.95, 2.55);
    await circ(s, x + 0.15, 1.62, 0.58, eda[i][0]);
    T(s, eda[i][1], { x: x + 0.9, y: 1.62, w: 2.9, h: 0.58, fontSize: 22, bold: true, color: DG, valign: "middle" });
    T(s, bullets(eda[i][2]), { x: x + 0.2, y: 2.35, w: 3.6, h: 1.65, fontSize: 13 });
  }
  T(s, "How PumpRupee feeds drives and energy management", { x: 0.6, y: 4.25, w: 8, h: 0.35, fontSize: 16, bold: true, color: DG });
  const fl4 = [["PumpRupee audit", "Clamp-on, 7–14 days"], ["₹ business case", "Waste by cause + VFD verdict"], ["VFD installed", "e.g. Altivar Process"], ["PumpRupee re-measures", "Same kit, after the fix"], ["Verified saving", "Feeds energy management, e.g. EcoStruxure"]];
  for (let i = 0; i < 5; i++) {
    const x = 0.6 + i * 2.46, hl = i === 0 || i === 3;
    card(s, x, 4.7, 2.2, 1.5, { fill: { color: hl ? LGREEN : CARD }, line: { color: hl ? GREEN : LINE, width: hl ? 2 : 1 } });
    s.addShape(S.OVAL, { x: x + 0.12, y: 4.8, w: 0.36, h: 0.36, fill: { color: hl ? DG : GREY }, line: { color: hl ? DG : GREY, width: 0 } });
    T(s, String(i + 1), { x: x + 0.12, y: 4.8, w: 0.36, h: 0.36, fontSize: 13, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    T(s, [{ text: fl4[i][0], options: { bold: true, fontSize: 13, breakLine: true } }, { text: fl4[i][1], options: { fontSize: 11, color: MUTED } }], { x: x + 0.12, y: 5.22, w: 1.98, h: 0.95 });
    if (i < 4) arrow(s, x + 2.22, 5.3, 0.22, 0.28);
  }
  T(s, "A low-cost front door that expands VFD and energy-management adoption into MSMEs that skip audits today. Concept only: no drive or platform integration built.", { x: 0.6, y: 6.35, w: 12.1, h: 0.55, fontSize: 12, italic: true, color: MUTED });
  s.addNotes("Schneider products are named only as the natural next step after an audit. Say it positively: PumpRupee finds which pumps justify an Altivar-class drive.");

  // ===== 5. KEY FEATURES & USER JOURNEY =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Key Features & User Journey", "Seven steps from clamp-on to a verified saving.");
  const jr = [["FaPlug", "Clamp on", "Power clamp on the motor cable"], ["FaTools", "Fit sensors", "Pressure on existing gauge ports"], ["FaDatabase", "Log 7–14 days", "ESP32 saves a CSV of power + pressure"], ["FaClipboardList", "Upload to the dashboard", "₹ report by cause"],
    ["FaSlidersH", "Apply the fix", "Cheapest first; VFD verdict"], ["FaCheckCircle", "Re-measure", "Verify the saving"], ["FaRedo", "Move the kit", "Next pump"]];
  for (let i = 0; i < 7; i++) {
    const y = 1.4 + i * 0.54;
    await circ(s, 0.6, y, 0.46, jr[i][0], i === 3 ? ORANGE : DG);
    T(s, [{ text: jr[i][1] + "  ", options: { bold: true, fontSize: 13 } }, { text: jr[i][2], options: { fontSize: 11.5, color: MUTED } }], { x: 1.2, y, w: 4.3, h: 0.46, valign: "middle" });
  }
  const chips5 = ["₹ waste by cause", "No flow meter", "No shutdown", "VFD verdict", "Upload your logs", "Reusable kit"];
  chips5.forEach((c, i) => tag(s, c, 0.6 + (i % 3) * 1.8, 5.3 + Math.floor(i / 3) * 0.4, 1.7, i % 2 ? "2E7D5B" : DG, "FFFFFF", 10.5));
  linkBlock(s, 0.6, 6.2, 0.72);
  const b5 = shot(s, "crop_kpis", 5.95, 1.4, 6.8, [1, 1, 1]);
  legend(s, ["₹ saving per year with a VFD (simulated)", "Specific energy: before → after (kWh/m³)", "VFD payback range at ₹50,200–1,09,400"], 5.95, b5 + 0.04, 6.8, 11.5);
  card(s, 5.95, 5.75, 6.8, 1.1, { fill: { color: LGREEN }, line: { color: GREEN, width: 2 } });
  T(s, [{ text: "New: upload your own logs", options: { bold: true, fontSize: 15, color: DG, breakLine: true } }, { text: "Load a CSV of power and pressure; the dashboard calibrates the pump in your browser and prices the saving (slide 8).", options: { fontSize: 12 } }], { x: 6.1, y: 5.8, w: 6.5, h: 1.0, valign: "middle" });
  s.addNotes("Walk the numbered callouts on the dashboard: 1 the rupee saving, 2 the payback range, 3 the cheapest-fix-first order. Everything shown is simulated.");

  // ===== 6. TECHNICAL APPROACH =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Technical Approach", null);
  const inst = [["Motor", "3A4A45", "Power clamp"], ["Pump", "2E7D5B", "P1 suction (opt.)\nP2 discharge"], ["Throttle valve", ORANGE, "P3 process side\n(optional)"], ["Process", GREY, ""]];
  inst.forEach((b, i) => {
    const x = 0.6 + i * 1.7;
    s.addShape(S.ROUNDED_RECTANGLE, { x, y: 1.1, w: 1.4, h: 0.6, rectRadius: 0.08, fill: { color: b[1] }, line: { color: b[1], width: 0 } });
    T(s, b[0], { x, y: 1.1, w: 1.4, h: 0.6, fontSize: 13, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    if (b[2]) T(s, b[2], { x: x - 0.12, y: 1.75, w: 1.65, h: 0.5, fontSize: 10, bold: true, color: DG, align: "center" });
    if (i < 3) arrow(s, x + 1.42, 1.28, 0.24, 0.24);
  });
  T(s, "Minimum kit: clamp + P2. Add P3 before a VFD purchase.", { x: 0.6, y: 2.3, w: 6.5, h: 0.3, fontSize: 11.5, bold: true, color: ORANGE });
  const pl6 = ["Logs", "Calibrate", "Infer flow", "Shapley split", "CUSUM check", "₹ report"];
  pl6.forEach((p, i) => {
    const x = 0.6 + i * 1.09;
    s.addShape(S.ROUNDED_RECTANGLE, { x, y: 2.7, w: 0.98, h: 0.62, rectRadius: 0.06, fill: { color: i === 5 ? ORANGE : LGREEN }, line: { color: i === 5 ? ORANGE : GREEN, width: 1 } });
    T(s, p, { x, y: 2.7, w: 0.98, h: 0.62, fontSize: 10.5, bold: true, color: i === 5 ? "FFFFFF" : DG, align: "center", valign: "middle" });
  });
  T(s, [{ text: "Shapley = ", options: { bold: true } }, { text: "fair split of blame between causes.  " }, { text: "CUSUM = ", options: { bold: true } }, { text: "early alarm when the pump slowly wears.  " }, { text: "SEC = ", options: { bold: true } }, { text: "electricity units per m³ pumped." }],
    { x: 0.6, y: 3.4, w: 6.55, h: 0.5, fontSize: 10.5 });
  // chart drawn as an image (always renders, in every viewer)
  const NQ = 7, qs6 = CV.Q.slice(0, NQ);
  const GW = 760, GH = 450, ML = 70, MR = 20, MT = 24, MB = 150;
  const gx = (q) => ML + ((q - 10) / 60) * (GW - ML - MR), gy = (h) => MT + (1 - h / 40) * (GH - MT - MB);
  const poly = (arr, color, dash) => `<polyline fill="none" stroke="${color}" stroke-width="5" stroke-linejoin="round" ${dash ? 'stroke-dasharray="14 9"' : ""} points="${arr.slice(0, NQ).map((v, i) => gx(qs6[i]) + "," + gy(v)).join(" ")}"/>`;
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${GW}" height="${GH}" viewBox="0 0 ${GW} ${GH}" font-family="Arial, Helvetica, sans-serif"><rect width="${GW}" height="${GH}" fill="#FFFFFF"/>`;
  for (let h = 0; h <= 40; h += 10) svg += `<line x1="${ML}" x2="${GW - MR}" y1="${gy(h)}" y2="${gy(h)}" stroke="#E3EEE7" stroke-width="2"/><text x="${ML - 10}" y="${gy(h) + 8}" font-size="24" fill="#475569" text-anchor="end">${h}</text>`;
  for (let q = 10; q <= 70; q += 10) svg += `<text x="${gx(q)}" y="${GH - MB + 34}" font-size="24" fill="#475569" text-anchor="middle">${q}</text>`;
  svg += `<text x="${(ML + GW - MR) / 2}" y="${GH - MB + 68}" font-size="24" fill="#475569" text-anchor="middle">Flow, m³/h</text><text x="22" y="${MT + 120}" font-size="24" fill="#475569" transform="rotate(-90 22 ${MT + 120})">Head, m</text>`;
  svg += poly(CV.pump, "#0E5A32") + poly(CV.sys, "#9AA5A0") + poly(CV.thr, "#E07B00") + poly(CV.vfd, "#3DCD58", true);
  svg += `<line x1="${gx(61.6)}" x2="${gx(61.6)}" y1="${gy(31.7)}" y2="${gy(15.4)}" stroke="#C0392B" stroke-width="5"/><circle cx="${gx(61.6)}" cy="${gy(31.7)}" r="8" fill="#C0392B"/><circle cx="${gx(61.6)}" cy="${gy(15.4)}" r="8" fill="#C0392B"/><text x="${gx(61.6) - 14}" y="${gy(23.5) + 8}" font-size="24" font-weight="bold" fill="#C0392B" text-anchor="end">wasted head</text><text x="${gx(61.6) - 14}" y="${gy(23.5) + 36}" font-size="24" font-weight="bold" fill="#C0392B" text-anchor="end">16.3 m</text>`;
  [["#0E5A32", "Pump, full speed", 0], ["#9AA5A0", "System, valve open", 0], ["#E07B00", "System, throttled", 0], ["#3DCD58", "Pump slowed by VFD", 1]].forEach(([c, t, d], i) => {
    const lx = ML + (i % 2) * 340, ly = GH - 62 + Math.floor(i / 2) * 40;
    svg += `<line x1="${lx}" x2="${lx + 50}" y1="${ly}" y2="${ly}" stroke="${c}" stroke-width="6" ${d ? 'stroke-dasharray="12 8"' : ""}/><text x="${lx + 62}" y="${ly + 8}" font-size="23" fill="#16261F">${t}</text>`;
  });
  svg += "</svg>";
  const gpng = "image/png;base64," + (await sharp(Buffer.from(svg)).png().toBuffer()).toString("base64");
  card(s, 0.6, 3.95, 3.95, 2.95);
  T(s, "Grundfos NB 65-160/157 curves", { x: 0.72, y: 4.0, w: 3.75, h: 0.28, fontSize: 11, bold: true, color: DG });
  s.addImage({ data: gpng, x: 0.68, y: 4.3, w: 3.8, h: 3.8 * GH / GW });
  T(s, "Off-peak 61.6 m³/h. Simulated; the system curve is assumed.", { x: 0.72, y: 6.62, w: 3.75, h: 0.25, fontSize: 9, italic: true, color: MUTED });
  card(s, 4.7, 3.95, 2.45, 2.95, { fill: { color: LGREEN }, line: { color: GREEN, width: 1.5 } });
  T(s, "How flow is inferred", { x: 4.8, y: 4.0, w: 2.3, h: 0.3, fontSize: 12, bold: true, color: DG });
  T(s, bullets(["Head → flow from the pump curve H(Q)", "Power → shaft power via motor efficiency → flow", "Two scales, s_h and s_p, fitted from 7–14 days of logs", "Optional anchors: shut-off head, closed-valve power", "No flow meter used"], { paraSpaceAfter: 3 }), { x: 4.8, y: 4.32, w: 2.28, h: 2.55, fontSize: 10.5 });
  const b6 = shot(s, "crop_curves", 7.5, 1.1, 5.25, [1, 1]);
  legend(s, ["Choose datasheet-only or 1/3/7/14 days of logs", "Blue points: measured head at the flow the model infers (no flow meter)"], 7.5, b6 + 0.04, 5.25, 11);
  T(s, "About ±3 points only with a measured system curve; otherwise about ±10.", { x: 7.5, y: b6 + 0.65, w: 5.25, h: 0.5, fontSize: 12, bold: true, color: DG });
  s.addNotes("Calibration: two scale factors (head, power) are fitted from 7-14 days of logs by profile likelihood; no flow meter. The system curve is the biggest error source, which is why the optional P3 sensor exists.");

  // ===== 7. PROTOTYPE & SIMULATED RESULTS =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Prototype & Simulated Results", null);
  tag(s, "SIMULATED – Grundfos NB 65-160/157, 11 kW · 10 m lift · 5% margin · 16 h/day · 300 days · ₹8/kWh", 0.6, 0.98, 9.3, ORANGE, "FFFFFF", 11);
  const b7a = shot(s, "crop_waste", 0.6, 1.4, 5.9, [1, 1, 1]);
  const b7b = shot(s, "crop_roi", 6.9, 1.4, 4.85, [1, 1, 1]);
  legend(s, ["Valve share of waste (Shapley split)", "₹ per year, by cause", "Valve share is partly by construction"], 0.6, b7a + 0.02, 5.9, 10.5, 0.22);
  legend(s, ["GO / NO-GO verdict for this pump", "Annual saving in ₹", "Break-even month"], 6.9, b7b + 0.02, 4.85, 10.5, 0.22);
  T(s, "₹69,292 / ₹1,27,178 per year  ·  valve 83–93% of waste  ·  payback 4–19 months  ·  ±3 / ±10 points", { x: 0.6, y: 6.84, w: 12.15, h: 0.22, fontSize: 11, bold: true, color: DG });
  s.addNotes("Screenshots are from the working prototype dashboard, simulated data. Forecast error: 1.4 points with a process-side sensor vs 10.5 points without, under stress. A +/-30% flow reading is worse than no calibration.");

  // ===== 8. PROTOTYPE: UPLOAD YOUR LOGS =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Prototype: Upload Your Own Logs", "Not just a replay: the dashboard calibrates from a CSV you load.");
  const b8 = shot(s, "crop_upload", 0.6, 1.4, 4.75, [1, 1, 1], "Working prototype · sample data");
  const st8 = [["FaUpload", "Export a CSV", "power_kw, discharge_bar and optional suction_bar, from the ESP32 SD card or any logger."], ["FaShieldAlt", "Stays in your browser", "Nothing is uploaded to a server."],
    ["FaCogs", "Calibrate and infer flow", "Fits a head scale and a power scale, then infers flow per record. No flow meter."], ["FaRupeeSign", "₹ saving and payback", "SEC, ₹/m³, VFD saving per year and payback for your tariff and VFD price."]];
  for (let i = 0; i < 4; i++) {
    const y = 1.4 + i * 1.0;
    card(s, 5.7, y, 7.05, 0.88);
    await circ(s, 5.82, y + 0.17, 0.52, st8[i][0]);
    T(s, [{ text: st8[i][1], options: { bold: true, fontSize: 14, breakLine: true } }, { text: st8[i][2], options: { fontSize: 11.5, color: MUTED } }], { x: 6.5, y: y + 0.05, w: 6.15, h: 0.78, valign: "middle" });
  }
  legend(s, ["Calibrated pump scales found from the logs", "Forecast VFD saving, running cost, CO₂", "VFD payback and GO / NO-GO"], 5.7, 5.5, 7.05, 11.5);
  card(s, 5.7, 6.4, 7.05, 0.55, { fill: { color: AMBER }, line: { color: ORANGE, width: 1.5 } });
  T(s, "Limits: reference pump (Grundfos NB 65-160/157) only; system curve assumed, so about ±10 points unless measured.", { x: 5.8, y: 6.4, w: 6.85, h: 0.55, fontSize: 11, bold: true, color: ORANGE, valign: "middle" });
  s.addNotes("On the sample file the calibration recovers the hidden pump scales (0.96, 1.05) and a forecast within 1 point of the simulated truth. That is a software test on simulated data, not a field result.");

  // ===== 8. INNOVATION =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Innovation", "We build on proven tools. The new part is the integration for MSMEs.");
  card(s, 0.6, 1.45, 4.9, 2.35);
  T(s, "Already exists (we build on it)", { x: 0.75, y: 1.5, w: 4.6, h: 0.32, fontSize: 14, bold: true, color: MUTED });
  T(s, bullets(["KSB PumpMeter, US DOE PSAT", "Samotics (motor-current efficiency)", "Schneider Altivar Process (sensorless flow), EcoStruxure", "Indian IoT vendors and ESCOs", "Shapley split and CUSUM: known methods"]), { x: 0.75, y: 1.85, w: 4.6, h: 1.9, fontSize: 12 });
  card(s, 0.6, 3.95, 4.9, 2.4, { fill: { color: LGREEN }, line: { color: GREEN, width: 2.5 } });
  T(s, "Our integration", { x: 0.75, y: 4.0, w: 4.6, h: 0.32, fontSize: 14, bold: true, color: DG });
  T(s, bullets(["₹ waste split by cause", "Prices the value of an extra sensor", "Low-cost shared kit, no flow meter", "Built-in before/after verification", "Pump-specific VFD verdict before capex"]), { x: 0.75, y: 4.35, w: 4.6, h: 1.95, fontSize: 12 });
  const cols8 = ["Flow meter", "Manual audit", "Full platform", "PumpRupee"];
  const rows8 = [["Upfront cost, small plant", ["Meter + install", "Fee per visit", "Higher", "₹6,100–13,300"]], ["No shutdown", ["P", "Y", "P", "Y"]], ["Answer in ₹", ["N", "Y", "P", "Y"]], ["Cause breakdown", ["N", "Y", "P", "Y"]], ["VFD verdict", ["N", "Y", "P", "Y"]], ["Verified savings", ["P", "P", "Y", "Y"]], ["Fits small MSMEs", ["P", "N", "P", "Y"]]];
  const tx8 = 5.8, lw = 2.2, cw8 = 1.2;
  cols8.forEach((c, i) => { const x = tx8 + lw + i * cw8; s.addShape(S.ROUNDED_RECTANGLE, { x, y: 1.45, w: cw8 - 0.05, h: 0.55, rectRadius: 0.05, fill: { color: i === 3 ? DG : "E8EEEA" }, line: { color: i === 3 ? DG : LINE, width: 1 } }); T(s, c, { x, y: 1.45, w: cw8 - 0.05, h: 0.55, fontSize: 11, bold: true, color: i === 3 ? "FFFFFF" : INK, align: "center", valign: "middle" }); });
  rows8.forEach((r, ri) => {
    const y = 2.07 + ri * 0.53;
    s.addShape(S.RECTANGLE, { x: tx8, y, w: lw + 4 * cw8 - 0.05, h: 0.5, fill: { color: ri % 2 ? "EEF4F0" : CARD }, line: { color: LINE, width: 0.5 } });
    T(s, r[0], { x: tx8 + 0.1, y, w: lw - 0.1, h: 0.5, fontSize: 11.5, bold: true, valign: "middle" });
    r[1].forEach((v, i) => { const x = tx8 + lw + i * cw8; if (v.length === 1) s.addImage({ data: ic[v], x: x + cw8 / 2 - 0.2, y: y + 0.1, w: 0.3, h: 0.3 }); else T(s, v, { x, y, w: cw8 - 0.05, h: 0.5, fontSize: 10, bold: i === 3, color: i === 3 ? DG : INK, align: "center", valign: "middle" }); });
  });
  T(s, "✔ yes  ~ partly / varies  ✘ no. Our general assessment; PumpRupee's ticks are design targets (simulated).", { x: tx8, y: 5.8, w: 6.9, h: 0.3, fontSize: 9.5, italic: true, color: MUTED });
  banner(s, "We found no low-cost shared kit that combines these. Full platforms are the next step after PumpRupee.", 6.45, 0.55, DG, 14);
  s.addNotes("Never say 'none exists'. Altivar Process does sensorless flow inside the drive after it is bought; PumpRupee helps decide which pumps deserve one and verifies the saving.");

  // ===== 9. EXPECTED IMPACT =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Expected Impact", null);
  tag(s, "SIMULATED – per 11 kW pump; prices indicative, not quotes", 0.6, 0.98, 5.4, ORANGE, "FFFFFF", 11);
  card(s, 0.6, 1.5, 7.2, 3.45);
  T(s, "A one-time kit vs a yearly saving (₹)", { x: 0.75, y: 1.57, w: 6.9, h: 0.32, fontSize: 15, bold: true, color: DG });
  const bars9 = [["Kit, one-time and reusable (top tier)", 13300, GREY, "₹13,300"], ["Saving per year, constant pressure", 69292, GREEN, "₹69,292"], ["Saving per year, proportional pressure", 127178, DG, "₹1,27,178"]];
  bars9.forEach((b, i) => { const y = 2.0 + i * 0.85; T(s, b[0], { x: 0.75, y, w: 6.9, h: 0.3, fontSize: 12 }); s.addShape(S.RECTANGLE, { x: 0.75, y: y + 0.33, w: 5.2 * b[1] / 127178, h: 0.4, fill: { color: b[2] }, line: { color: b[2], width: 0 } }); T(s, b[3], { x: 0.85 + 5.2 * b[1] / 127178, y: y + 0.33, w: 1.4, h: 0.4, fontSize: 14, bold: true, valign: "middle" }); });
  T(s, "One kit ≈ 5–19% of a year's simulated saving on one pump.", { x: 0.75, y: 4.6, w: 6.9, h: 0.3, fontSize: 12, bold: true, color: DG });
  const st9 = [["FaLeaf", "6.1–11.3 t", "CO₂ avoided per pump per year (0.710 kg/kWh)"], ["FaSearchDollar", "₹50,200–1,09,400", "wrong VFD purchase avoided where it won't pay back"], ["FaClock", "4–19 months", "payback, oversized pump (2–4+ years if right-sized, high lift)"]];
  for (let i = 0; i < 3; i++) { const y = 1.5 + i * 1.18; card(s, 8.0, y, 4.75, 1.05); await circ(s, 8.15, y + 0.22, 0.6, st9[i][0], i === 1 ? ORANGE : DG); T(s, [{ text: st9[i][1], options: { bold: true, fontSize: 18, color: DG, breakLine: true } }, { text: st9[i][2], options: { fontSize: 10.5, color: MUTED } }], { x: 8.9, y: y + 0.08, w: 3.75, h: 0.9, valign: "middle" }); }
  T(s, "Who benefits", { x: 0.6, y: 5.15, w: 4, h: 0.3, fontSize: 14, bold: true, color: DG });
  ["MSME plant owners", "Maintenance teams", "Energy auditors / ESCOs", "Drive channel partners", "India's industrial efficiency goals"].forEach((c, i) => tag(s, c, 0.6 + [0, 2.2, 4.1, 6.5, 8.5][i], 5.5, [2.0, 1.8, 2.3, 1.9, 3.2][i], i % 2 ? "2E7D5B" : DG, "FFFFFF", 10.5));
  card(s, 0.6, 6.0, 12.15, 0.9, { fill: { color: AMBER }, line: { color: ORANGE, width: 1.5 } });
  T(s, [{ text: "Scale-up illustration, not a projection: ", options: { bold: true, color: ORANGE } }, { text: "total = N pumps × per-pump saving. For N = 10: ₹6,92,920–12,71,780 per year and 61–113 t CO₂ per year, using the 11 kW base case. The 54–60% saving for heavily oversized pumps is an upper bound only." }], { x: 0.8, y: 6.03, w: 11.8, h: 0.84, fontSize: 12, valign: "middle" });
  s.addNotes("5-19% = 6,100/127,178 = 4.8% up to 13,300/69,292 = 19.2%. N=10 is arithmetic, not a forecast.");

  // ===== 10. ROADMAP =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Implementation Roadmap", "What is done, what is next, and which limit each phase removes.");
  const rm = [["Simulation + dashboard", "DONE", GREEN, DG, "Real Grundfos curve fits, stress tests, working dashboard with CSV upload (simulated data).", "Limit removed: none yet"],
    ["Bench test", "NEXT", LORANGE, ORANGE, "Real pump, ESP32 kit and a reference flow meter.", "Removes: flow-inference accuracy, head = discharge − suction"],
    ["Pilot, 1–2 plants", "PLANNED", LINE, MUTED, "Measure the system curve on site; log 7–14 days.", "Removes: ±10 → ±3 points"],
    ["Validate forecast", "PLANNED", LINE, MUTED, "Compare the forecast with the measured saving after a fix.", "Removes: optimistic system-curve fit"],
    ["Rollout", "PLANNED", LINE, MUTED, "Multi-pump, multi-plant; ESCO and channel use.", "Widens: parallel pumps, drives, NPSH"]];
  s.addShape(S.LINE, { x: 1.2, y: 1.85, w: 10.9, h: 0, line: { color: GREY, width: 3 } });
  for (let i = 0; i < 5; i++) {
    const x = 0.6 + i * 2.46;
    s.addShape(S.OVAL, { x: x + 0.85, y: 1.6, w: 0.5, h: 0.5, fill: { color: rm[i][2] }, line: { color: rm[i][3], width: 2 } });
    T(s, String(i + 1), { x: x + 0.85, y: 1.6, w: 0.5, h: 0.5, fontSize: 15, bold: true, color: rm[i][3], align: "center", valign: "middle" });
    card(s, x, 2.3, 2.3, 2.75);
    T(s, [{ text: rm[i][0], options: { bold: true, fontSize: 15, breakLine: true, paraSpaceAfter: 4 } }, { text: rm[i][4], options: { fontSize: 11.5, breakLine: true, paraSpaceAfter: 6 } }, { text: rm[i][5], options: { fontSize: 10.5, bold: true, color: DG } }], { x: x + 0.1, y: 2.38, w: 2.1, h: 2.05 });
    tag(s, rm[i][1], x + 0.1, 4.58, 1.1, rm[i][2], rm[i][3], 10);
  }
  card(s, 0.6, 5.25, 12.15, 1.7, { fill: { color: AMBER }, line: { color: ORANGE, width: 2 } });
  T(s, "Honest limits we validate next", { x: 0.8, y: 5.3, w: 8, h: 0.32, fontSize: 15, bold: true, color: ORANGE });
  T(s, bullets(["Simulation and software prototype only: no lab or field data, no real quotes", "About ±3 points only with a measured system curve; otherwise about ±10; the curve fit is optimistic",
    "Single pump, steady state. Out of scope: parallel pumps, closed loops, pumps already on drives, min-flow/NPSH, control dynamics"]), { x: 0.85, y: 5.65, w: 11.7, h: 1.25, fontSize: 12.5 });
  s.addNotes("Lead with 'done' and 'next'. Ask: a pilot plant and a reference flow meter.");

  // ===== 11. TEAM + REFERENCES =====
  s = pres.addSlide({ masterName: "CONTENT" });
  head(s, "Team Introduction", "Team ANS_4X · Schneider Electric Yuva Yodha 2026 · Smart Manufacturing");
  const team = [["FaLaptopCode", "Akshaya V G", "Team Lead & Software/Dashboard", "Data pipeline and the PumpRupee web dashboard"], ["FaMicrochip", "Adithyaa J", "Embedded Hardware", "ESP32 logger, power clamp and pressure-sensor integration"],
    ["FaChartLine", "Nikilaesh B", "Energy Analytics", "Pump hydraulics model, Shapley waste split and VFD payback logic"], ["FaFlask", "Siva Subramaniam S", "Simulation & Validation", "Pump-curve simulation, CUSUM wear-drift testing, pilot and roadmap planning"]];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.077;
    card(s, x, 1.4, 2.9, 1.95);
    await circ(s, x + 0.15, 1.52, 0.5, team[i][0]);
    T(s, [{ text: team[i][1], options: { bold: true, fontSize: 15, breakLine: true } }, { text: team[i][2], options: { fontSize: 11, bold: true, color: DG } }], { x: x + 0.75, y: 1.5, w: 2.05, h: 0.6, valign: "middle" });
    T(s, team[i][3], { x: x + 0.15, y: 2.2, w: 2.6, h: 1.1, fontSize: 11.5, color: MUTED });
  }
  card(s, 0.6, 3.5, 12.15, 2.55);
  T(s, "References & data sources", { x: 0.75, y: 3.55, w: 6, h: 0.32, fontSize: 14, bold: true, color: DG });
  const refsL = ["Pump data: Grundfos Product Center duty-point readouts for NB 65-160/157 (product no. 97839240), retrieved 2026-10-02. Curve tolerance ISO 9906:2012 Grade 3B. Curves in this deck are cubic fits to those 14 points.",
    "Emission factor: CEA CO₂ Baseline Database for the Indian Power Sector, v21.0 (FY2024-25): 0.710 kg CO₂/kWh.",
    "Energy-audit practitioner input (paraphrased, not named): wrong sizing is the most common cause of throttling; 30–40% of ultrasonic flow readings go wrong.",
    "Method: affinity laws; Shapley value attribution; CUSUM change detection; IPMVP-style measurement and verification."];
  const refsR = ["Component prices (indicative online listings, 2026-10-02, not quotes): ESP32 (Robu); SCT-013 clamp (ElectronicsComp, Robodo, Robocraze); ZMPT101B voltage sensor; 4–20 mA pressure transmitters (Nishka, Utopia, Shri Instruments); VFDs (Delta MS300 listing, Industrybuying). Install cost ₹15,000 is an assumption.",
    "Prior art: KSB PumpMeter, US DOE PSAT, Samotics, Schneider Altivar Process and EcoStruxure, Indian IoT vendors and ESCOs.",
    "Simulation: our open Python scripts (fixed seeds) in the project repository, folder yuva_yodha/; dashboard source in yuva_yodha/dashboard/.",
    "All results are simulated. No lab or field data."];
  T(s, bullets(refsL, { paraSpaceAfter: 3 }), { x: 0.75, y: 3.9, w: 5.85, h: 2.1, fontSize: 9.5 });
  T(s, bullets(refsR, { paraSpaceAfter: 3 }), { x: 6.8, y: 3.9, w: 5.85, h: 2.1, fontSize: 9.5 });
  linkBlock(s, 0.6, 6.15, 0.85);
  T(s, "Cheap kit. Clever inference. Answers in rupees.", { x: 6.4, y: 6.2, w: 6.35, h: 0.75, fontSize: 22, bold: true, color: DG, valign: "middle" });
  s.addNotes("Every number traces to the Grundfos readouts, the CEA factor, indicative online prices, or our own simulation scripts. Close with the key message and the live link.");

  await pres.writeFile({ fileName: "PumpRupee_ANS_4X_Yuva_Yodha_Application.pptx" });
  console.log("written");
})();
