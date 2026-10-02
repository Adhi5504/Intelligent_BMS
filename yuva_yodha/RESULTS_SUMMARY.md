# PumpRupee: results summary (all simulated; no field measurements yet)

**Idea:** a low-cost pump audit that prices energy waste by cause, recommends the cheapest fixes and the lowest safe drive setpoint, and verifies the saving. It does not control the pump.
**Real pump used:** Grundfos NB 65-160/157 (product 97839240), 11 kW IE3, manufacturer data in `pump_data/`. Fits are labelled as fits; the true shut-off head is not in the data.
**Scripts:** all in `yuva_yodha/`, run with `python3 <name>.py`.

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
