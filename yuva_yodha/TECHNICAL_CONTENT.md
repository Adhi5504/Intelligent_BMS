# PumpRupee: complete technical content

Team ANS_4X | Schneider Electric Yuva Yodha 2026 | Track: Smart Manufacturing

**How to read the labels in this document**
- **[Simulated]**: result from the scripts in `yuva_yodha/` on the real Grundfos NB 65-160/157 curves. No lab or field data exists.
- **[Design]**: an engineering choice or estimate that has not been built or tested.
- **[Price]**: an indicative online price found on 2026-10-02. Not a quote.
- **[Assumption]**: an input value I chose, not measured.
- **[Data]**: a value copied from the manufacturer's tool readout.

Nothing in this document has been measured on hardware.

---

## 1. One-paragraph summary

PumpRupee is a low-cost, clamp-on audit kit for industrial centrifugal pumps. An ESP32 logger records motor electrical power and one to three pressures for 7–14 days. Software calibrates the pump's real curve from those logs, infers flow without a flow meter, splits the energy waste by cause (throttle valve, impeller wear, clogged strainer) with a Shapley fair-share method, watches for slow wear with a CUSUM test, and reports the result in rupees: ₹/year wasted, SEC (kWh/m³), ₹/m³, the cheapest fix first, the lowest safe VFD setpoint, and a payback verdict for a VFD on that specific pump. After the fix, the same kit re-measures and verifies the saving. It audits and recommends. It never controls the pump.

---

## 2. Engineering background

### 2.1 Pump and system curves
A centrifugal pump delivers head H that falls as flow Q rises. The piping network demands head
`H_sys(Q) = H_static + k·Q²` (lift plus friction). The pump runs where the two curves cross.

If the plant needs less flow than that crossing point, the common fix is a partly closed throttle valve. This steepens the system curve (higher k) so the crossing moves to the lower flow. The pump still pushes at high head, and the head above what the process needs is burnt across the valve as heat.

### 2.2 Why a variable-speed drive saves energy
Affinity laws, for speed ratio r = n / n_rated:
- Q ∝ r
- H ∝ r²
- P ∝ r³

Slowing the pump moves its curve down so it crosses the system curve at the required flow without a valve. The ideal saving is large when the pump is oversized and the static lift is small. It is small when the pump is already near the duty point or the static lift dominates (head cannot fall much with speed).

### 2.3 Key relations used throughout
| Quantity | Formula |
|---|---|
| Hydraulic power | `P_h [kW] = ρ·g·Q·H / 3.6×10⁶` (Q in m³/h, H in m, ρ = 998.2 kg/m³, g = 9.81) |
| Pump efficiency | `η_pump = P_h / P2` (P2 = shaft power) |
| Motor efficiency | `η_motor = P2 / P1` (P1 = electrical input) |
| Head from pressure | `H [m] = p [bar] × 10.197` for water |
| Specific energy | `SEC [kWh/m³] = P1 [kW] / Q [m³/h]` |
| Cost of energy | `₹/m³ = SEC × tariff` |
| CO₂ | `kg = kWh × 0.710` (CEA v21.0 factor) |

Check against manufacturer data [Data]: at Q = 114 m³/h, H = 26.07 m, P2 = 9.961 kW, the formula gives η_pump = 81.1%, matching the tool's printed 81.1%.

### 2.4 Why flow is the problem
Flow is the only quantity that makes waste visible, and it is the hardest to measure: it needs a flow meter (cost, installation, often pipe access) or a clamp-on ultrasonic meter. An energy-audit practitioner told us wrong sizing leading to throttling is the most common cause, and that 30–40% of ultrasonic flow readings go wrong. Electrical power and pressure are easy and cheap to measure. PumpRupee's central idea is to infer flow from those two instead.

---

## 3. System architecture

```
Motor cable ──► Power clamp (CT) ─┐
Mains voltage ─► Voltage sensor ──┤
Discharge port ► Pressure Tx (P2) ┼─► ESP32 logger ─► SD / Wi-Fi ─► Analysis ─► ₹ report (PDF/phone)
Suction port ──► Pressure Tx (P1, optional) ┤
Process side ──► Pressure Tx (P3, optional) ┘
```

### 3.1 Sensors
| Measurement | Part in the BOM | Notes |
|---|---|---|
| Motor current | SCT-013 split-core CT, 100 A | [Price] ₹349 + 18% GST (about ₹412) to ₹729. Hobby-grade, not a certified meter. |
| Mains voltage | ZMPT101B module | [Price] ₹92–289. Single-phase module. Mains wiring must be done by a qualified electrician. |
| Discharge pressure P2 | 0–10 bar, 4–20 mA transmitter | [Price] ₹2,100–3,068 basic; ₹7,500–12,000 for a 1/2 in BSP flush-diaphragm spec. |
| Process-side pressure P3 | same type | Measures the system curve and reveals clogging. About ₹3,068. |
| Suction pressure P1 / strainer ΔP | same type | Optional. See 3.5. |
| Logger | ESP32 dev board | [Price] ₹399–449. |
| Enclosure, supply, 4–20 mA interface, wiring | | [Assumption] ₹2,000, not priced. |

**Kit totals [Price, computed]:** about ₹6,100 (basic single-phase), ₹10,200 (three-phase with a second transmitter), ₹13,300 (three-phase with a third, process-side transmitter), about ₹40,100 with ₹12,000 industrial transmitters.

### 3.2 Electrical measurement [Design]
- Real power should be computed from sampled voltage and current, not from current alone: `P = mean(v(t)·i(t))`, `Vrms`, `Irms`, `PF = P / (Vrms·Irms)`. Using a fixed assumed power factor would leave a part-load error, because induction-motor power factor falls as load falls.
- At 50 Hz one cycle is 20 ms. At least about 2 kHz sampling (40 samples per cycle) over whole cycles is needed to compute P properly.
- The ESP32 internal ADC is nonlinear and noisy near the rails. Options: a dedicated energy-metering module or IC, or an external ADC for the slow pressure channels with the internal ADC reserved for current and voltage. This choice must be settled on the bench.
- **CT range:** the pump's rated-point input power is about 10.8 kW [Data]. On 400 V three-phase, assuming a power factor of 0.87 [Assumption], the line current is about 18 A. A 100 A CT is oversized for that current and loses accuracy at low load. A lower-range CT (for example 30–50 A) would be a better match. Final choice on the bench.
- **Three phases:** measuring one phase and assuming balance is cheapest. Measuring all three costs more but removes the unbalance error. Both are [Design] options; the cost tiers in 3.1 follow the summary.
- **Electrical safety:** a split-core CT clamps around an insulated conductor without touching live metal. Voltage sensing needs a connection to live conductors and must be done by a qualified electrician, inside a rated enclosure, with fuse protection.

### 3.3 Pressure measurement [Design]
- A two-wire 4–20 mA transmitter is powered from a 24 V DC loop supply. Reading it with a precision shunt resistor (for example 150 Ω) gives 0.6–3.0 V for 4–20 mA. An external 16-bit ADC avoids the ESP32 ADC problems on this slow channel.
- Conversion: `p = range × (I − 4 mA) / 16 mA`; `H = p × 10.197` m.
- Mount on existing gauge ports with the right adapters; no pipe cutting. Zero each transmitter with the pump stopped and the line open or at known static pressure.
- **Head is a difference, not a single reading.** Total dynamic head is discharge pressure head minus suction pressure head, plus the elevation difference between the two gauge points and the difference in velocity heads. The simulation uses a single "head" value. If the suction side is a flooded tank at a roughly constant level, a one-time suction reading may be enough. Otherwise P1 is needed. This caveat is not in the simulation summary and should be tested on the bench.

### 3.4 Logging [Design]
- Sample electrical and pressure signals at the fast rate needed, then store **averaged records** (for example one-minute means of Vrms, Irms, P, PF, p_discharge, p_other). All simulation results use **one-hour steady-state steps**, so the analysis must aggregate to that resolution or the model must be re-validated at finer steps.
- Timestamps from an RTC or Wi-Fi time. Store to SD card; Wi-Fi upload is optional. The owner keeps the data; no cloud service is required for the audit.
- 7–14 days of logs gives the calibration enough operating points. Simulated calibration error falls from 7.4 points (datasheet only) to 1.8, 1.4, 1.3 and 1.2 points after 1, 3, 7 and 14 days.

### 3.5 Minimum kit and when to add sensors
- **Minimum kit:** power clamp + discharge pressure (P2). This is enough to price the waste.
- **Add P3 (process-side pressure) when a VFD purchase is on the table.** It measures the system curve and exposes a clogged strainer. Under stress this lowers simulated forecast error from 10.5 to 1.4 points [Simulated].
- **Add a strainer ΔP or suction transmitter** where clogging is suspected.

---

## 4. Analytics: methods in detail

All analytics are classical physics-based modelling and statistics (curve fitting, profile-likelihood calibration, fair-share attribution, CUSUM). There are no trained neural models. The reference implementation is plain Python in `yuva_yodha/`.

### 4.1 Pump model [Data → fit]
- Manufacturer readouts for the Grundfos NB 65-160/157: 14 points of Q, H, η, P2, P1, NPSHr, speed. Product number 97839240. 11 kW, 2-pole, IE3, 157 mm impeller, curve tolerance ISO 9906:2012 Grade 3B.
- The two lowest-flow points (0.5 and 1 m³/h) are **not** used. They are the lowest values the tool accepts, not the true shut-off head, which is not given.
- Cubic least-squares fits of H(Q) and P2(Q) over Q = 10–130 m³/h. These are labelled **fits**, not data. Motor efficiency `P2/P1` is a piecewise-linear function of shaft power from the table.
- Speed in the table is not constant (2981 rpm near zero flow to 2947 rpm at 130 m³/h, motor slip). The model treats the table as one fixed-speed curve and uses affinity laws for other speeds, a roughly 1% approximation.
- The datasheet rated point (26.5 m) differs from the Product Center readout at 114 m³/h (26.07 m) by 0.43 m; the model uses the readout.

### 4.2 Flow inference without a flow meter
At fixed speed the pump's operating point lies on its own curve, so a measured head or a measured electrical power each map to a flow:
- From head: `Q = H⁻¹(H_meas)`
- From power: `P2 = η_motor(P2)·P1_meas`, then `Q = P2⁻¹(P2)`

Because the true pump differs from its datasheet (age, wear, tolerance), the model carries two unknown scales: a head scale `s_h` and a power scale `s_p`. Each logged pair (head, power) is explained by the flow that best fits both under the current scales. Because the head curve is flat near shut-off and the power curve is steep, head and power each constrain flow differently, and together they allow the scales to be separated.

### 4.3 Calibration
**A. From logs alone (no flow meter, no shut-off test).** For every (s_h, s_p) on a grid, each logged hour is explained by its best flow; the summed residual gives a cost surface. The best scales minimise it. The scales within a chi-square-style threshold form an uncertainty band, and the saving forecast is reported as a range [Simulated].

**B. Optional anchors:**
- *Shut-off head:* the head with the discharge valve closed. Gives `s_h` directly. The shut-off value in the simulation is the cubic fit extrapolated to Q = 0, which is a label, not data.
- *Closed-valve power:* the electrical power at that point. Gives `s_p`. Assumed to transfer to normal operation (see 4.9 for how much that matters).
- *A flow reading (±5%)* helps. *An unreliable flow reading (±30%)* is worse than none (4.9).
- Closed-valve running must be brief and within the manufacturer's limits.

### 4.4 System curve
`H_sys(Q) = H_static + k·Q²`. H_static (lift) and the friction coefficient k are unknown for a real plant. With a process-side pressure sensor P3 and the inferred flow, both parameters can be fitted from the logs. This is the single most valuable extra measurement in the stress tests (4.9).

### 4.5 Savings forecast
For each hourly flow q and the chosen control strategy, find the speed ratio r such that the slowed pump delivers q at the head the process needs, solving `r²·H(q/r) = H_target` by bisection (rejecting flows beyond the fitted range, with a minimum speed of 0.5 [Assumption]). Then `P = r³·P2(q/r)`, electrical input `= P / η_motor / η_VFD` with η_VFD = 0.97 [Assumption].

Strategies compared against **fixed speed + throttle valve**:
- *Constant-pressure setpoint:* H_target = H_sys(peak flow) × (1 + margin), margin 5% [Assumption]. For the main case this is 24.2 m (2.37 bar).
- *Proportional pressure:* H_target follows H_sys(q) × (1 + margin).

### 4.6 Waste decomposition (Shapley fair share)
Waste is measured against an **ideal** reference: healthy pump, clean system, speed matched to demand. Three causes are modelled in the simulation:
| Cause | Model [Assumption] |
|---|---|
| Throttling | fixed speed with a throttle instead of speed matching |
| Impeller wear | head × (1 − w), efficiency × (1 − 1.5·w) |
| Fouling / clogged strainer | system friction × (1 + f) |

The cost of each of the 2³ combinations is computed. A cause's Shapley value is its marginal contribution averaged over all 3! = 6 orderings, so the three parts add up **exactly** to the total waste. This answers "who is to blame" fairly even though the causes interact.

Important properties:
- The valve share (83–93% in the simulation; 72–87% under stress) is **partly by construction** because the reference is speed-matched. It tells the owner what a drive or trimmed impeller would remove, not that valves are always 83–93% of waste on every pump.
- With only power + discharge pressure, **a clogged strainer is invisible**: its rupees are assigned to the valve.

### 4.7 Value of an extra sensor
Three sensor sets are compared: S0 = power + discharge pressure; S1 = S0 + strainer ΔP (gives fouling within ±15%); S2 = S0 + process-side pressure (gives system head, hence fouling). The output is the rupees of waste attributed to the wrong cause that the sensor removes. A sensor is worth buying if its installed price is below that figure times the payback the owner accepts.

### 4.8 Wear drift detection (CUSUM)
A daily wear estimate is monitored with a one-sided CUSUM: `S_t = max(0, S_{t-1} + (x_t − μ₀ − k))`, alarm when `S_t > h`. The reference mean and variance are set from the first 14 days; k and h are tuned from that baseline. A no-wear control run counts false alarms.

### 4.9 Outputs
| Output | Definition |
|---|---|
| SEC | kWh/m³ |
| Running cost | ₹/m³ = SEC × tariff |
| Waste | ₹/year, split by cause |
| Setpoint | lowest safe constant-pressure setpoint |
| Fix ranking | cheapest first, with placeholder costs (replace with quotes) |
| VFD verdict | payback = (VFD + install) / annual saving |
| Verification | the same kit re-measured after the fix, saving expressed in SEC |

For before/after verification the right frame is a measurement-and-verification (M&V) approach in the spirit of IPMVP: compare energy per volume pumped at comparable operating conditions, not raw kWh.

---

## 5. Results [Simulated]

### 5.1 Setup
Real Grundfos NB 65-160/157 curve fits. Assumed: static lift 10 m, head margin 5%, 16 h/day, 300 days/yr, tariff ₹8/kWh, VFD efficiency 0.97, CO₂ factor 0.710 kg/kWh, a 16-step demand profile (fractions of peak) [Assumption], peak demand 90% of rated flow in the main case. One hour per step, steady state.

### 5.2 Energy saving
| Case (peak demand 90%) | SEC (kWh/m³) | Saving | ₹/year | t CO₂/year |
|---|---|---|---|---|
| Fixed speed + throttle | 0.115 | n/a | n/a | n/a |
| VFD, constant pressure (24.2 m, 2.37 bar) | 0.093 | 19.3% | 69,292 | 6.1 |
| VFD, proportional pressure | 0.074 | 35.5% | 1,27,178 | 11.3 |

- Range across the sweep (peak demand 80–95% of rated, static lift 5–20 m): constant pressure 8–33%, proportional 15–45%.
- A right-sized pump (95% of rated, 20 m lift) saves only 8% / 15%.
- A heavily oversized pump (60–70% of rated) reaches 54–60%: **upper bound only**.
- Head margin 0 / 5 / 10%: 23.5 / 19.3 / 15.1% (constant) and 38.7 / 35.5 / 32.3% (proportional).
- An energy-audit practitioner reports 5–40% in practice.
- Consistency: ₹ ÷ 8 gives kWh saved (about 8,660 and 15,900 per year); × 0.710 gives the CO₂ above.

### 5.3 Waste by cause (peak demand 80%, 1% noise)
- Valve 83–93% of waste (about ₹1.6–1.8 lakh/year in the model).
- With only power + pressure, ₹2,000–16,000/year of clog waste lands under the valve.
- A strainer ΔP or process-side sensor removes about ₹6,000–6,600/year of misattribution (up to about ₹13,000–14,000 with heavy clogging). With no clog it does not help.

### 5.4 Calibration anchors (forecast error, percentage points; datasheet curves differing from the real pump by head up to −8%, power up to +10%)
| Anchor | Mean error |
|---|---|
| None (datasheet) | 8.3 |
| Shut-off head only | 6.0 |
| Shut-off head + closed-valve power | 1.0 (3.2 if closed-valve power represents normal operation only half; 6.2 if not at all) |
| Good flow reading (±5%) | 3.5 |
| Unreliable flow reading (±30%) | 16.8 |

### 5.5 Learning from logs
Forecast error 7.4 points (datasheet only) → 1.8 / 1.4 / 1.3 / 1.2 after 1 / 3 / 7 / 14 days. About 90% of runs within ±3 points after 7–14 days. The model's own uncertainty band shrinks (3.9 to 0.2 points) but becomes overconfident (holds the truth only 39–72% of the time), so **report a fixed ±3 points (±5 after one day), not the model's band.**

### 5.6 Stress tests (3% noise, curve-shape error, wrong static lift/friction)
| Approach | Friendly (1% noise) mean / 90th pct | Stress mean / 90th pct |
|---|---|---|
| Datasheet only | 7.2 / 13.1 | 8.4 / 18.2 |
| Shut-off head | 6.3 / 11.9 | 11.3 / 25.1 |
| Shut-off head + closed-valve power | 1.1 / 2.2 | 6.3 / 12.0 |
| Learned from logs | 1.6 / 3.5 | 10.5 / 16.9 |
| Learned + system curve from a process-side sensor | not run | 1.4 / 3.0 |

- One factor at a time, mean error (datasheet / shut-off / shut-off+power / learned): noise 3% only 5.8 / 5.5 / 3.0 / 1.9; curve-shape error only 7.5 / 6.4 / 5.6 / 3.3; wrong lift and friction only 9.4 / 9.8 / 7.7 / 8.8 (learned + process-side sensor: 0.4).
- **The largest error comes from the assumed system curve, not the pump curve.**
- Anchors and log-learning help under noise and curve-shape errors but **not** under a wrong system curve. The shut-off head alone can be worse than none.
- A fixed ±3 points held in 94–100% of 18 stressed runs per set. A x10-widened model band held 100% but was 19 points wide (useless).
- Waste split under stress: valve share 72–87%; per-hour flow estimates off by 8–12%; ₹5,700–16,700/year attributed to the wrong cause with power + pressure only. A strainer or process-side sensor roughly halves that only when clogging exists, does nothing at 10% wear / 10% clog (16,700 to 14,300), and the process-side sensor made the no-clog case worse (5,700 to 14,000, a false clog from noise).
- Drift detection under stress: one false alarm in 3 × 365 days; slow wear (0 to 10% over 180 days) alarms about day 40 at about 2.2% wear; fast wear about day 22 at about 3.7%; a 6% step is caught the next day.

---

## 6. Economics

### 6.1 Kit cost [Price]
See 3.1. Volume cost: not estimated (no quotes). A certified power meter would cost more than the hobby-grade clamps.

### 6.2 VFD cost and payback [Price + Assumption]
VFD for about 11 kW (15 HP), three-phase: about ₹29,230–35,200 (Delta MS300) to about ₹94,400 (Delta 11 kW listing); install [Assumption] ₹15,000. Total ₹50,200 (low) to ₹1,09,400 (high). Months = total / annual saving.

| Case | Annual saving (constant / proportional) | Payback, low VFD price | Payback, high VFD price |
|---|---|---|---|
| Main: peak 90%, lift 10 m | ₹69,292 / ₹1,27,178 | 8.7 / 4.7 months | 18.9 / 10.3 months |
| More oversized: peak 80%, lift 10 m | ₹1,11,890 / ₹1,54,215 | 5.4 / 3.9 months | 11.7 / 8.5 months |
| Pessimistic: peak 95%, lift 20 m | ₹28,526 / ₹55,118 | 21.1 / 10.9 months | 46.0 / 23.8 months |

Reading: roughly 4–19 months for an oversized, throttled pump; for a nearly right-sized pump with high lift it can exceed 2–4 years. The audit's job is to say which case the owner is in.

### 6.3 Kit economics [Arithmetic, illustrative]
- Cost per pump audited = kit cost ÷ N pumps. N = 10: ₹610–1,330.
- Throughput: 7–14 days of logging per pump gives roughly 25–50 pumps per kit per year, excluding travel and setup (365/14 ≈ 26; 365/7 ≈ 52).
- Kit payback: ₹10,200 equals about 1.8 months of the base-case saving of ₹69,292/yr, **if** the audit leads to that VFD.
- Also: the audit can stop a wrong VFD purchase of ₹50,200–1,09,400.

### 6.4 Scale-up illustration (not a projection)
Total = N × per-pump saving. For N = 10: ₹6,92,920–12,71,780 per year and 61–113 t CO₂ per year, using the 11 kW base case.

---

## 7. Validation plan (designed, not run)
Detailed in `submission/BENCH_TEST_PLAN.md`. Summary:
1. **Flow inference:** small pump with a reference flow meter; compare inferred flow at several operating points; report error against the reference.
2. **Waste split:** close a valve in steps at fixed speed; confirm the valve share rises.
3. **Blocked strainer:** partly block suction; confirm it is invisible with power + P2 only and visible with P3 or strainer ΔP.
4. **Wear drift:** substitute a trimmed or worn impeller; check the CUSUM alarm level.
5. **System-curve fit:** measure P3 over flow steps; target forecast within about 3 points of the measured saving.
6. **Before/after:** fit a VFD or trim the impeller and re-measure.
7. **Pilot:** 1–2 plants with a measured system curve, then multi-pump.

Acceptance thresholds must be agreed before testing.

---

## 8. Technical risks and mitigations
| Risk | Mitigation |
|---|---|
| Hobby-grade CT/voltage sensors and uncertain power factor | Calibrate against a reference meter on the bench; compute real power from sampled v and i; choose a CT range that matches the motor current. |
| Head requires suction and discharge pressures and elevation | Measure P1 or fix suction conditions; test on the bench. |
| Wrong system curve dominates forecast error | Measure it with P3; otherwise state ±10 points, not ±3. |
| Real pumps differ from the datasheet (tolerance ISO 9906 Grade 3B, age, wear) | Calibrate from logs; optional anchors; do not trust a ±30% flow reading. |
| Model fits use the same functional form as the simulated plant | State it as optimistic; test on real plants. |
| Pumps already on drives, parallel pumps, closed loops | Out of scope; detect and refuse rather than guess. |
| Closed-valve test damages the pump | Brief, within the maker's limits, optional. |
| Electrical noise near VFDs | Shielded cables, proper grounding, test on the bench. |
| Safety | Non-invasive CT, rated enclosure, fuse-protected voltage tap by a qualified electrician; kit never controls the pump. |
| Data privacy | Local storage by default; the owner keeps the data. |

---

## 9. Standards and context
- Pump type: close-coupled single-stage end-suction centrifugal (EN 733 / ISO 5199); curve tolerance ISO 9906:2012 Grade 3B.
- Savings verification: IPMVP-style M&V.
- Emission factor: CEA v21.0, 0.710 kg CO₂/kWh.
- Drive context: variable-speed drives such as Schneider Altivar Process (sensorless flow inside the drive) and energy-management platforms such as EcoStruxure are complementary: they come after the audit decides which pumps need a drive.

---

## 10. Prior art and the honest innovation claim
KSB PumpMeter, US DOE PSAT, Samotics (motor-current pump efficiency), Schneider Altivar Process (sensorless flow), Indian IoT vendors and ESCOs all exist. Pump monitoring, sensorless flow, VFD savings, Shapley attribution and CUSUM are **not** new.

What PumpRupee integrates, for MSMEs:
1. Waste priced in ₹ by cause.
2. The value of an extra sensor priced in ₹.
3. A low-cost shared kit with no flow meter.
4. Built-in before/after verification.
5. A pump-specific VFD payback verdict before capex.

Say: "we found no low-cost shared kit that combines these", never "none exists".

---

## 11. Likely judge questions and honest answers
**How do you get flow without a flow meter?** From the pump's own curve: measured head and electrical power each map to a flow. Calibrating two scale factors from 7–14 days of logs corrects the datasheet. It is simulated, not field-proven.

**How accurate is it?** About ±3 percentage points on the predicted saving, only when the system curve is measured. Otherwise about ±10. Under stress the learned-from-logs error is 10.5 points without the system curve.

**Why not just use Altivar's sensorless flow?** It works inside the drive after the drive is bought. PumpRupee decides which pumps deserve a drive and verifies the saving.

**Is 83–93% valve waste real?** It is partly by construction: waste is measured against a speed-matched ideal. It tells the owner what a drive or trimmed impeller removes.

**Has it been tested?** No. Simulation only on the real Grundfos curve data. A bench test with a reference meter is the next step.

**What about pumps already on a VFD or in parallel?** Out of scope for now.

**What is the real saving?** ₹69,292 / ₹1,27,178 per year for the base-case 11 kW pump; 8–45% across simulated cases; 5–40% reported in practice.

**Why should an MSME care?** The kit costs about ₹6,100–13,300 and answers a ₹50,000–1,09,400 question: should I buy a VFD for this pump?

---

## 12. Reproducibility: files in this repository (`yuva_yodha/`)
| File | Purpose |
|---|---|
| `real_pump_sim.py` | Pump model, savings for fixed speed vs constant-pressure vs proportional-pressure VFD, sweeps |
| `sensor_value.py` | Shapley waste split and the value of extra sensors |
| `calibration_test.py` | Flow-free calibration anchors |
| `learning_layer.py` | Calibration from logs and CUSUM drift detection |
| `stress_test.py` | Harsher tests (`cal`, `decomp`, `sysfit`, `band`, `sensor`, `drift`) |
| `extra_checks.py` | Two quoted checks |
| `RESULTS_SUMMARY.md`, `PRICES_AND_PAYBACK.md` | Result and price summaries |
| `pump_data/` | Manufacturer data and brief |
| `submission/` | Slide decks, build script, bench test plan |

All scripts use fixed seeds, are plain Python, and are deterministic. Every script is a simulation.

---

## 13. Glossary
- **VFD**: variable-frequency drive; controls motor speed instead of strangling the pipe.
- **SEC**: specific energy consumption; units of electricity per m³ pumped.
- **System curve**: the head the pipe network demands at each flow.
- **Shapley split**: a fair way to share the blame among causes.
- **CUSUM**: an alarm that notices slow drift.
- **TDH**: total dynamic head.
- **NPSH**: net positive suction head (not checked in the model).
- **ESCO**: energy service company.
- **MSME**: micro, small and medium enterprise.
- **IPMVP**: International Performance Measurement and Verification Protocol.
- **CT**: current transformer (the clamp).
