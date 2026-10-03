"""Generates src/data/generated.json for the PumpRupee dashboard from the SIMULATION scripts in yuva_yodha/.
Everything in the output is simulated (real Grundfos NB 65-160/157 curve fits; synthetic logs with seeded noise).
Run from this folder:  python3 scripts/gen_data.py
"""
import json, math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import real_pump_sim as rp
import calibration_test as ct
import sensor_value as sv
import learning_layer as ll

OUT = os.path.join(HERE, "..", "src", "data", "generated.json")
PEAK = 0.90
QS90 = [f * PEAK * rp.Q_RATED for f in rp.PROFILE]
AH_T, AP_T = 0.96, 1.05                      # demo "true" pump vs datasheet (head x0.96, power x1.05) - ASSUMED mismatch

# ---------- pump model ----------
table = [{k: r[k] for k in ("Q_m3h", "H_m", "P2_shaft_kW", "P1_input_kW", "eta_pump_pct")} for r in rp.DATA]
pump = {
    "table": table, "hCoef": rp.H_COEF, "p2Coef": rp.P2_COEF, "motor": [list(x) for x in rp._MP],
    "qMin": rp.Q_MIN_FIT, "qMax": rp.Q_MAX_FIT, "qRated": rp.Q_RATED, "hRated": rp.H_RATED,
    "etaVfd": rp.ETA_VFD, "nMin": rp.N_MIN, "profile": rp.PROFILE, "ef": rp.EF,
}
curves = []
for q in range(10, 131, 5):
    h, p2 = rp.h_nom(q), rp.p2_nom(q)
    curves.append({"q": q, "h": round(h, 3), "p2": round(p2, 3), "p1": round(rp.p1_fixed_speed(q), 3),
                   "eta": round(100 * rp.RHO * rp.G * q * h / 3.6e6 / p2, 2)})

# ---------- reference results (for the TS port self-check) ----------
ref = rp.evaluate()
reference = {"base": ref["base"], "const": ref["const"], "prop": ref["prop"], "vol": ref["vol"], "hConst": ref["h_const"]}

# ---------- synthetic 14-day telemetry + calibration ----------
rng = random.Random(2026)
SH = [round(0.88 + 0.01 * i, 2) for i in range(25)]
SP = [round(0.92 + 0.01 * i, 2) for i in range(31)]
QG = list(range(40, 131))
HT = {q: rp.h_nom(q) for q in QG}
P1T = {sp: {q: ct.p1_fixed(q, 1.0, sp) for q in QG} for sp in SP}

records, pts = [], []
for day in range(14):
    for hr, q0 in enumerate(QS90):
        q = q0 * (1 + rng.gauss(0, 0.03))
        h_true, p1_true = AH_T * rp.h_nom(q), ct.p1_fixed(q, AH_T, AP_T)
        p2s = AP_T * rp.p2_nom(q)
        hm, pm = h_true * (1 + rng.gauss(0, 0.01)), p1_true * (1 + rng.gauss(0, 0.01))
        v = 400 * (1 + rng.gauss(0, 0.005))
        pf = (0.62 + 0.25 * min(1.0, p2s / 10.4)) * (1 + rng.gauss(0, 0.005))      # ASSUMED PF vs load
        irms = pm * 1000 / (math.sqrt(3) * v * pf)
        ps = 0.5 + rng.gauss(0, 0.01)                                              # ASSUMED flooded suction
        pd = ps + hm / 10.197
        hsys = ct.HS + ct.K0 * q * q
        p3 = ps + hsys / 10.197 * (1 + rng.gauss(0, 0.01))
        records.append({"i": day * 16 + hr, "day": day + 1, "hour": hr, "v": round(v, 1), "i_a": round(irms, 2), "p1": round(pm, 3),
                        "pf": round(pf, 3), "pd": round(pd, 3), "ps": round(ps, 3), "p3": round(p3, 3), "qTrue": round(q, 1)})
        pts.append((hm, pm))

def day_cost(points):
    cost = {}
    for sh in SH:
        for sp in SP:
            tot = 0.0
            for hm, pm in points:
                tot += min(((sh * HT[q] - hm) / hm) ** 2 + ((P1T[sp][q] - pm) / pm) ** 2 for q in QG)
            cost[(sh, sp)] = tot
    return cost

def infer(points, sh, sp):
    out = []
    for hm, pm in points:
        best, qe = 1e18, QG[0]
        for q in QG:
            c = ((sh * HT[q] - hm) / hm) ** 2 + ((P1T[sp][q] - pm) / pm) ** 2
            if c < best:
                best, qe = c, q
        out.append(qe)
    return out

def saving_from(points, qe_list, sh, sp):
    base = sum(pm for _, pm in points)
    var = sum(ct.p1_var(float(q), sh, sp) for q in qe_list)
    return 100 * (base - var) / base

b = sum(ct.p1_fixed(q, AH_T, AP_T) for q in QS90)
v = sum(ct.p1_var(q, AH_T, AP_T) for q in QS90)
truth_saving = 100 * (b - v) / b
day_costs = [day_cost(pts[d * 16:(d + 1) * 16]) for d in range(14)]
ref_pts = pts[13 * 16:14 * 16]
calib = []
for d in (1, 3, 7, 14):
    tot = {k: sum(c[k] for c in day_costs[:d]) for k in day_costs[0]}
    best = min(tot, key=tot.get)
    qe_all = infer(pts, *best)
    qe_ref = qe_all[13 * 16:]
    fc = saving_from(ref_pts, qe_ref, *best)
    qerr = sum(abs(qe - r["qTrue"]) / r["qTrue"] for qe, r in zip(qe_all, records)) / len(records) * 100
    calib.append({"days": d, "sh": best[0], "sp": best[1], "forecast": round(fc, 2), "error": round(abs(fc - truth_saving), 2),
                  "qInferred": qe_all, "meanFlowErrPct": round(qerr, 2)})
none_q = infer(pts, 1.0, 1.0)
fc_none = saving_from(ref_pts, none_q[13 * 16:], 1.0, 1.0)
telemetry = {"records": records, "truth": {"sh": AH_T, "sp": AP_T, "saving": round(truth_saving, 2)}, "calibration": calib,
             "datasheetOnly": {"forecast": round(fc_none, 2), "error": round(abs(fc_none - truth_saving), 2), "qInferred": none_q}}

# ---------- Shapley waste split + sensor value (peak demand 80%, as in sensor_value.py) ----------
RS = rp.DAYS * rp.TARIFF
scen = []
for w, f in [(0.05, 0.20), (0.10, 0.10), (0.00, 0.30), (0.08, 0.00), (0.03, 0.40)]:
    truth, mean = sv.scenario(w, f)
    tot = sum(truth.values())
    scen.append({"wear": w, "foul": f, "totalRsYr": round(tot * RS), "rsYr": {k: round(x * RS) for k, x in truth.items()},
                 "pct": {k: round(100 * x / tot, 1) for k, x in truth.items()},
                 "misattrib": {k: round(x) for k, x in mean.items()}})

# ---------- CUSUM paths ----------
def cusum_path(series, base_n=14, k=0.5, h=5.0):
    base = series[:base_n]
    mu = sum(base) / base_n
    sd = max((sum((x - mu) ** 2 for x in base) / (base_n - 1)) ** 0.5, 0.004)
    s, path, alarm = 0.0, [], None
    for i, x in enumerate(series):
        if i >= base_n:
            s = max(0.0, s + (x - mu - k * sd))
            if alarm is None and s > h * sd:
                alarm = i
        path.append(round(s, 5))
    return {"mu": mu, "sd": sd, "k": k, "h": h, "threshold": h * sd, "S": path, "alarm": alarm}

import stress_test as st            # drift under STRESS (3% noise, curve/system mismatch), same seed and run order as `stress_test.py drift`
rng2 = random.Random(9)
cv_s, sy_s, f_s = st.Curves(0.97, 1.04, 0.03, 0.03), st.System(10, 1.05), 0.05
defs = [
    ("control", "Control: no wear, 365 days", [0.0] * 365, 3),
    ("slow", "Slow wear: 0 to 10% over 180 days", [0.10 * min(d, 180) / 180 for d in range(240)], 4),
    ("fast", "Fast wear: 0 to 10% over 60 days", [0.10 * min(d, 60) / 60 for d in range(120)], 4),
    ("step", "Step wear: 6% from day 60", [0.0 if d < 60 else 0.06 for d in range(120)], 4),
]
cus = {}
for key, label, ws, runs in defs:
    res = []
    for _ in range(runs):
        est = [st.daily_w(w, cv_s, sy_s, f_s, rng2) for w in ws]
        res.append((cusum_path(est), est))
    alarms = [r[0]["alarm"] for r in res]
    hits = sorted(a_ for a_ in alarms if a_ is not None)
    if key == "control":
        pick = next((r for r in res if r[0]["alarm"] is None), res[0])
    else:
        med = hits[len(hits) // 2] if hits else None
        pick = next((r for r in res if r[0]["alarm"] == med), res[0])
    c, est = pick
    cus[key] = {"label": label, "trueWear": ws, "estWear": [round(x, 4) for x in est], **c,
                "wearAtAlarm": (ws[c["alarm"]] if c["alarm"] is not None else None),
                "runs": runs, "alarmsAllRuns": alarms,
                "medianWearAtAlarm": (sorted(ws[a_] for a_ in hits)[len(hits) // 2] if hits else None)}

data = {"pump": pump, "curves": curves, "reference": reference, "telemetry": telemetry, "waste": scen, "cusum": cus,
        "meta": {"peakTelemetry": PEAK, "peakWaste": 0.8, "ratedRpmNote": "Datasheet 2940-2950 rpm; table 2981 (near zero flow) to 2947 rpm (130 m3/h)"}}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, "w"))
print("written", OUT, round(os.path.getsize(OUT) / 1024), "KB")
for c in calib:
    print("calib", c["days"], c["sh"], c["sp"], c["forecast"], "truth", round(truth_saving, 2), "err", c["error"], "flowErr%", c["meanFlowErrPct"])
print("datasheet-only forecast", round(fc_none, 2), "err", round(abs(fc_none - truth_saving), 2))
for k, v_ in cus.items():
    print(k, "alarm", v_["alarm"], "wear@alarm", v_["wearAtAlarm"], "all", v_["alarmsAllRuns"], "median wear", v_["medianWearAtAlarm"])
for s_ in scen:
    print(s_["wear"], s_["foul"], s_["pct"], s_["misattrib"])
