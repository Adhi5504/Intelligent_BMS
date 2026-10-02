# PumpRupee: results summary (all simulated; no field measurements yet)

**Idea:** a low-cost pump audit that prices energy waste by cause, recommends the cheapest fixes and the lowest safe drive setpoint, and verifies the saving. It does not control the pump.
**Real pump used:** Grundfos NB 65-160/157 (product 97839240), 11 kW IE3, manufacturer data in `pump_data/`. Fits are labelled as fits; the true shut-off head is not in the data.
**Scripts:** all in `yuva_yodha/`, run with `python3 <name>.py`.

## 0. Corrections after harsher testing (read this first)
Sections 1-5 were measured under FRIENDLY conditions (1% noise, curves a scaled copy of the datasheet, exact system curve). `stress_test.py` (section 9) repeats the key claims with 3% noise, curve-SHAPE errors, and a wrong static lift / friction. What changed:
- **The largest forecast error comes from the assumed system curve (required head), not from the pump curve.** Without measuring it, expect about 8-11 points of error, not 1-3.
- **Measuring the system curve with a process-side pressure sensor** brings the stressed forecast error to about 1.4 points on average (90th percentile 3.0) in simulation. This is the most valuable extra sensor, more than the strainer pressure-drop sensor.
- Shut-off-head anchors and log-learned calibration help under noise and curve-shape errors but **not** under a wrong system curve; the shut-off head alone can be worse than no calibration.
- The model-based uncertainty band is not trustworthy. Report the forecast as **+-3 points** (holds in 94-100% of 18 stressed runs per set) only when the system curve has been measured; otherwise assume about +-10 points.
- The valve share of the waste (72-87% under stress) is measured against a speed-matched, healthy, clean ideal, so it describes what a drive or trimmed impeller removes, not all pumps.
- Wear-drift detection under stress: alarm at about 2-4% wear, one false alarm in 3 x 365 days.
- The system-curve fit uses the same functional form as the simulated plant (static lift + friction x flow squared), so it is still optimistic; real systems have valves, branches and pressure setpoints.

## 1. Energy saving on the real pump (`real_pump_sim.py`)
Baseline: fixed speed with a throttle valve. Same delivered volume and required head in every case.
Assumed: static lift 10 m, 5% head margin, 16 h/day, 300 days, Rs 8/kWh, VFD efficiency 0.97, CO2 0.710 kg/kWh (CEA v21.0).

| Case (peak demand 90% of rated flow) | SEC kWh/m3 | Saving | Rs/year | t CO2/year |
|---|---|---|---|---|
| Fixed speed + throttle | 0.115 | | | |
| VFD, constant-pressure setpoint (24.2 m, 2.37 bar) | 0.093 | 19.3% | 69,292 | 6.1 |
| VFD, proportional pressure | 0.074 | 35.5% | 1,27,178 | 11.3 |

**Range (peak demand 80-95% of rated, static lift 10-20 m):** constant-pressure 8-33%, proportional 15-45%.
A heavily oversized pump (60-70% of rated) reaches 54-60% in the model: treat as an upper bound (an ESCO practitioner reports 5-40% in practice).
A right-sized pump (95% of rated, 20 m lift) saves only 8% / 15%.
Head margin 0 / 5 / 10%: 23.5 / 19.3 / 15.1% (constant), 38.7 / 35.5 / 32.3% (proportional).
Earlier generic pump: 30% (speed matched) and 21% / 39% (setpoint modes), consistent with the real-pump numbers.

## 2. Where the waste goes and what an extra sensor is worth (`sensor_value.py`)
Waste vs an ideal speed-matched, healthy, clean system is split by cause with a fair-share (Shapley) method. Peak demand 80%, 1% sensor noise.
- Valve (throttling) is **83-93%** of the waste (about Rs 1.6-1.8 lakh/year in the model). Part of this is by construction.
- With only power + discharge pressure, a **clogged strainer is invisible**; its rupees land under the valve (Rs 2,000-16,000/year misattributed).
- A strainer pressure-drop sensor or a process-side pressure sensor removes about **Rs 6,000-6,600/year** of misattribution on average (up to about Rs 13,000-14,000 with a heavy clog). A sensor is worth buying if its installed price is below that times the payback you accept. No real sensor prices were available.
- With no clog, the extra sensor does not help (the process-side one adds noise).
- Wear was recovered well from power + pressure (generic-pump test: within about 1 point).

## 3. Calibration without a flow meter (`calibration_test.py`)
Error of the forecast saving, in percentage points, when the real pump differs from its datasheet (head up to -8%, power up to +10%):

| Anchor | Average error |
|---|---|
| None (datasheet) | 8.3 |
| Shut-off head only | 6.0 |
| Shut-off head + closed-valve power | 1.0 (3.2 if closed-valve power represents normal operation only half; 6.2 if not at all) |
| Good flow reading (+-5%) | 3.5 |
| Unreliable flow reading (+-30%) | **16.8, worse than no calibration** |

The shut-off value used is the cubic fit extrapolated to Q = 0 (not data). Running against a closed valve must be brief and within the manufacturer's limits.

## 4. Learning layer (`learning_layer.py`)
**A. Calibration from the logs alone (no flow meter, no shut-off test).** Forecast error 7.4 points with the datasheet only, 1.8 / 1.4 / 1.3 / 1.2 points after 1 / 3 / 7 / 14 days of logs. About 90% of runs are within +-3 points after 7-14 days. The statistical band shrinks (3.9 to 0.2 points) but **becomes overconfident** (contains the truth only 39-72% of the time), so report the forecast as "+-3 points (+-5 after one day)".
**B. Wear drift detection (trend test).** No false alarms in a no-wear control (3 x 365 days); wear detected at about 1-3% in simulation. This is optimistic: the test pump has exactly the model's form.

## 5. Fix ranking (`fix_ranker.py`) and repair timing (`rupee_meter.py`)
Both use placeholder costs and savings. Cheap fixes (grease, strainer, alignment) pay back in weeks but address small shares of the waste; the large saving is in the valve loss (impeller trim or speed control). Replace with real quotes before quoting any payback.

## 6. External evidence (paraphrased; not for naming or quoting without permission)
An ESCO practitioner said: wrong sizing (incorrect head selection) leading to throttling is the most common cause; flow is the hardest measurement and ultrasonic meters are unreliable (30-40% of readings go wrong); head and power are easy to measure; savings from speed control range 5-40%; a tool giving 24-hour efficiency (kW/m3, Rs/m3 at a given pressure) and deviation from design is feasible and very useful as an ESCO pre-audit; very small plants do not prioritise this.

## 7. Prior art (so no new-invention claim)
KSB PumpMeter, US DOE PSAT, Samotics (motor-current pump efficiency), Altivar Process (sensorless flow), Indian IoT vendors (Einnosys, KRYFS, Agromation, Logic Tracks), ESCOs (SeeTech and BEE-empanelled). Not found (not proof of absence): a low-cost shared audit kit that prices waste by cause and prices the sensor that would resolve what it cannot see.

## 8. What is assumed or missing
- Assumed: static lift, demand profile, margin, hours, tariff, VFD efficiency, wear model, system curve known, healthy curve known, 1% noise.
- Not done: field or lab measurement, real cost quotes, validation on a worn pump, control dynamics, minimum-flow and NPSH checks.
- Single pump, steady-state hourly model. Parallel pumps, closed loops and pumps already on drives are out of scope.

## 9. Stress tests (`stress_test.py`; commands: cal, decomp, sysfit, band, sensor, drift)
Forecast-saving error in percentage points (mean / 90th percentile), 7 days of logs where used:

| Approach | Friendly (1% noise) | Stress (3% noise, shape error, wrong lift/friction) |
|---|---|---|
| Datasheet only | 7.2 / 13.1 | 8.4 / 18.2 |
| Shut-off head | 6.3 / 11.9 | 11.3 / 25.1 |
| Shut-off head + closed-valve power | 1.1 / 2.2 | 6.3 / 12.0 |
| Learned from logs | 1.6 / 3.5 | 10.5 / 16.9 |
| Learned + system curve fitted from a process-side pressure sensor | not run | **1.4 / 3.0** |

One factor at a time (mean error, datasheet / shut-off / shut-off+power / learned): noise 3% only 5.8 / 5.5 / 3.0 / 1.9; curve-shape error only 7.5 / 6.4 / 5.6 / 3.3; wrong static lift and friction only 9.4 / 9.8 / 7.7 / 8.8 (learned + process-side sensor: 0.4).
Uncertainty band: widening the likelihood band by x1 holds the truth in 67% / 83% (calibration / test runs, width 5.4 points); x10 holds 100% but is 19 points wide (useless); a fixed +-3 points holds 94% / 100% (18 runs each).
Waste split under stress (plant with curve-shape error and a different system): waste is 33-37% of baseline electricity; valve share 72-87%; per-hour flow estimates are off by 8-12%; rupees attributed to the wrong cause: 5,700-16,700 per year with power + pressure only. A strainer pressure-drop or process-side sensor roughly halves that only when clogging is present (for example 13,000 to 7,600; 14,600 to 4,200), does not help at 10% wear / 10% clog (16,700 to 14,300), and the process-side sensor made the no-clog case worse (5,700 to 14,000, false clog from noise).
Drift detection under stress: one false alarm in 3 x 365 days; slow wear (0 to 10% over 180 days) alarms around day 40 at about 2.2% wear; fast wear around day 22 at about 3.7%; a 6% step is caught the next day.
