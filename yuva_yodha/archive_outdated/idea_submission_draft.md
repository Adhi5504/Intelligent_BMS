# PumpProof (working title): forecast the saving before you buy, prove it after

**Challenge 04: Smart Manufacturing.** Team: [names, college]

**One line:** A very low-cost digital energy audit for SME pumps. From about three days of power and pressure logs on the existing pump, it forecasts what speed control would save, with an error band. After the retrofit, the same logger verifies the real saving, so an energy-service company (ESCO) or lender can be repaid out of it.

## 1. The problem
Pumps and motors take a large share of an SME's process electricity. A common set-up is a fixed-speed pump with a throttle valve setting the flow, so the motor burns energy against the valve. A variable-speed drive (VFD) can remove most of this loss, and BEE-linked sources put the saving potential of motor and VFD measures at roughly 25 to 30%.

The owner still cannot get a cheap, trusted answer to three questions:
1. How much will I save on *this* pump?
2. Is it worth the money?
3. Did it really save after I bought it?

Without them, small units do not invest. Documented financing programmes in India already let MSMEs repay energy upgrades from the money saved, but that model depends on savings someone can trust. Very small units also struggle to access formal finance.

## 2. The solution
| Step | What happens |
|---|---|
| 1. Audit (about 3 days) | A clamp-on power logger and a pressure sensor go on the existing pump. No drive and no flow meter are needed. The user enters nameplate data and does one flow check, for example timing a tank fill. |
| 2. Forecast | A physics model estimates the flow profile and the throttling loss, then reports the predicted specific energy consumption (SEC, kWh per m³), the predicted saving with an error band, and the payback. |
| 3. Retrofit | Any drive, including a Schneider Electric Altivar. We do not replace the drive; we answer whether to buy one. |
| 4. Verify | The same logger measures after the change and reports the baseline-adjusted saving, in the style of IPMVP Option B (retrofit isolation). The report supports ESCO payments, lender confidence and Scope 2 CO2 requests from buyers. |

Everything runs on a small edge device and keeps working without internet. The owner sees a short report in plain language: forecast saving in rupees, payback, and later the verified saving.

## 3. How the forecast works, and its limits
The audit model uses the pump's curves (head and efficiency against flow) and the plant's system curve (static lift plus friction). With logged power and pressure at fixed speed, it estimates the flow at each hour, then computes the energy the same flow would need at the lowest speed that still meets the system curve.

The main error source is the pump curve, not sensor noise. Real pumps often lack a trusted curve, so we anchor the model with one measured flow point. Where a manufacturer supplies factory curves for the exact model, the error falls further.

## 4. Evidence so far (simulation of a generic pump, not measured)
The simulated pump is a made-up centrifugal pump: 100 m³/h at 30 m, 40 m shut-off head, 75% best-point efficiency, 90% motor efficiency, 10 m static lift, 16-hour shift with demand of 60 to 100 m³/h, tariff ₹8/kWh. It must be replaced with a real datasheet curve.

**Saving (`pump_sim.py`).** Metric: SEC, kWh per m³ delivered. Baseline: fixed speed with throttle valve. Constraint: flow is never below demand and the required head is always met.

| | Baseline | With speed control |
|---|---|---|
| SEC (kWh/m³) | 0.142 | 0.099 |
| Energy per day (kWh) | 178.8 | 124.9 |

That is a **30% SEC reduction**, about 16,200 kWh and ₹1.29 lakh per pump per year, and about 11.5 t CO2 (grid factor 0.71 kg/kWh, to be verified against the current CEA value). The saving falls as static lift grows: about 35%, 30%, 25% and 20% at 5, 10, 15 and 20 m of static lift. Motor efficiency is held constant, which slightly overstates part-load savings.

**Forecast accuracy (`forecast_check.py`).** Error in the forecast saving, in percentage points:

| Case | Mean error |
|---|---|
| Pump curve exactly right | 0.5 to 1.4 |
| Curve wrong by a moderate amount | 5.5 to 17.5, systematic |
| Same, after one measured flow point (±5%) | about 1 to 3 in three of four cases |
| Head over-estimated by about 10% | not fixed by one point (about 7) |

So the honest claim is: good to roughly ±3 points in most mismatch cases after one flow check, with a larger error otherwise, and the verification step then replaces the forecast with a measured result.

## 5. What is new, honestly
We do not claim a new algorithm. Sensorless flow and efficiency estimation already exists in academic work and in commercial drives, including Schneider Electric's Altivar Process, which estimates flow from pump curves entered by the user. Measurement and verification (IPMVP) and ESCO financing for MSMEs also exist, and at least one Indian ESCO already offers an AI-based motor programme [to be compared against its offering before submission].

Our contribution is narrower: a pre-purchase forecast with an explicit error band for pumps that have no drive, no flow meter and no trusted curve, tied to a post-retrofit verification report on the same cheap hardware, aimed at small plants that incumbent tools do not reach.

## 6. Fit with Indian SME conditions
- **Power quality:** sags, imbalance and outages are common; the logger records through them and flags gaps.
- **Site conditions:** dust, heat and humidity; clamp-on and bolt-on sensors in sealed enclosures.
- **Legacy equipment:** old motors, no PLC; it works on the pump already installed.
- **Skills and connectivity:** no data scientist and patchy internet; local-language report and edge processing.
- **Capital:** low entry cost; the verified saving can fund the upgrade through an ESCO.
- **Existing systems:** accounts software rather than full ERP; CSV and API export.

## 7. Deployment and business model
- **Customers:** (a) ESCOs and VFD dealers who need cheap audits and trusted verification; (b) pump manufacturers and dealers who can bundle it with new pumps and use the factory curves; (c) the SME owner directly. [Choose one pilot segment, for example textile processing, dairy or small water utilities, and add a verified count.]
- **Installation:** one visit per pump to fit the clamp and pressure sensor, plus one flow check.
- **Cost and payback [to be filled from real quotes]:** payback = (drive cost + logger cost) ÷ annual saving. With the simulated ₹1.29 lakh/year, an assumed ₹1.2 lakh drive and ₹15,000 logger give about 12 to 13 months.
- **Revenue:** per-audit fee, verification subscription, or a share of the verified saving through an ESCO.
- **Scale-up:** (1) pilot with an ESCO or pump dealer on 3 to 5 pumps; (2) channel through dealers and SME clusters; (3) extend the same model to fans and compressors; (4) pool anonymised audits to improve the starting curves for new pump models.

## 8. Risks and assumptions
- All results so far are simulated for a generic pump. A real pump curve, and ideally a few measurements, are needed before claims are made about a named pump.
- The forecast depends on the pump curve and on the share of static lift; the error band must be shown to users.
- Demand for this tool is a hypothesis; it should be tested with at least one ESCO, dealer or pump owner.
- Only speed control is modelled. Impeller trimming and right-sizing could use the same model but are not validated.
- Savings verified by a pump seller may carry less trust than third-party verification.

## 9. Fit with the challenge
Primary: the digital energy-audit tool with a prioritised retrofit roadmap, and IoT energy monitoring with an edge dashboard. Secondary: Scope 2 CO2 reporting for buyer requests, benchmarking SEC against BEE norms [benchmark to be verified], and off-peak load shifting.

## 10. Artefacts
1. `pump_sim.py`: SEC simulation, throttle vs speed control
2. `forecast_check.py`: forecast accuracy under pump-curve error, with one-point calibration
3. `softsensor_check.py`: earlier flow and wear estimation check
4. `rupee_meter.py`: earlier repair-timing model (optional module)
5. `architecture.svg`: **to be redrawn** for the audit, retrofit and verify loop
6. **Still to add:** audit-report wireframe, data model, real pump curve, real cost quotes
