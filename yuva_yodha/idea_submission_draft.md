# PumpRupee (working title): a rupee meter for SME motors and pumps

**Challenge 04: Smart Manufacturing.** Team: [names, college]

**One line:** Tell an SME owner in rupees what a motor or pump is silently wasting today, cut that waste by slowing the pump only when the process allows it, and say when repair is worth paying for.

## 1. The problem
Motors and pumps run most of an SME's process load, yet most small factories have no real-time energy monitoring. Two losses go unseen:
- **Throttled or oversized pumps.** Flow is often controlled by a valve while the motor runs at full speed. By the affinity laws, power falls roughly with the cube of speed, so a 20% speed cut can cut power by about half.
- **Wear.** A worn pump draws more power for the same flow, and nobody sees it until it fails. Existing alerts say "something is wrong" but not what it costs or when fixing it pays off.

## 2. Our solution
A retrofit kit with three layers, running on an edge device (ESP32 or Raspberry Pi) with no cloud needed for control.
1. **Sense.** A CT clamp for current and power, a vibration sensor, and a pressure sensor (plus flow where available).
2. **Know.** A physics baseline of power against speed and load. Excess power over the healthy baseline is the *waste*. Vibration trends feed a small *failure-risk* model. Together they give a rupee-per-day number.
3. **Decide.** (a) A speed controller drives a VFD to the lowest speed that still meets the flow and pressure the process needs. (b) A cost model compares the running cost of waiting with the repair cost and outputs "repair by [date], here is the math". (c) Where a tank buffers the flow, pumping is shifted to off-peak hours.

The owner sees three numbers: today's waste in rupees, savings this month, and the repair date.

## 3. Architecture
See `architecture.svg`: sensors → edge gateway (acquire, physics baseline, failure-risk model, speed controller, local dashboard) → VFD over Modbus RTU; owner view, ERP/accounts export and Scope 2 CO₂ report on the business side. A manual bypass to fixed speed is always kept.

## 4. What is new, honestly
We do not claim a new algorithm. Published work already covers self-supervised fault diagnosis of motors and wear prediction. We did not find prior work that (i) turns wear and failure risk into a rupee and repair-date decision, (ii) combines it with speed control, and (iii) is designed for low-cost SME hardware and quantified in simulation against a defined baseline. Multi-site learning is shown as a small simulation only.

## 5. Quantified improvement against a defined baseline
**Metric:** specific energy consumption, SEC = electrical kWh per m³ delivered.
**Baseline:** the usual SME set-up: a fixed-speed pump with a throttle valve setting the flow.
**Constraint (throughput and quality preserved):** delivered flow is never below the demanded flow, and the required system head (pressure) is always met. The speed controller only lowers speed to the point where the pump curve meets the system curve.

Simulation (`pump_sim.py`): a 100 m³/h, 30 m design-point pump, a 16-hour shift with flow demand between 60 and 100 m³/h, static lift 10 m.

| | Baseline (throttled) | Proposed (speed control) |
|---|---|---|
| SEC (kWh/m³) | 0.142 | 0.099 |
| Energy per day (kWh) | 178.8 | 124.9 |

**SEC reduction: about 30%** at the same delivered volume (1,260 m³/day). Over 300 days at ₹8/kWh that is about 16,200 kWh, about ₹1.29 lakh and about 11.5 t CO₂ per pump per year (grid factor 0.71 kg/kWh, to be verified against the current CEA value).

**Sensitivity, stated openly:** the saving shrinks when a larger share of the head is static lift, because the cube-law gain applies to friction head. With static lift of 5, 10, 15 and 20 m the SEC reduction is about 35%, 30%, 25% and 20%. The simulation also holds motor efficiency constant, which slightly overstates savings at part load. We will replace the assumed curves with the datasheet curves of a real pump and validate on a bench rig if time allows.

**Repair timing (separate illustrative model, `rupee_meter.py`):** for a 15 kW pump with 8% extra power draw, energy waste alone justifies repair in about 386 days; adding vibration-based failure risk moves the recommendation to about 49 days.

## 6. Fit with Indian SME conditions
- **Power quality:** voltage sags, phase imbalance and outages are common. The edge device logs and recovers on its own, and the controller returns to fixed speed on any fault.
- **Site conditions:** dust, heat and humidity. Sensors are clamp-on or bolt-on, with sealed enclosures.
- **Legacy equipment:** old motors and no PLC. The kit is retrofit and vendor-agnostic; it works with the pump already installed.
- **Skills and connectivity:** no data scientist, patchy internet. Everything runs on the edge with a three-number display in the local language, and it syncs when the network returns.
- **Money:** low capital. Payback is stated up front, and a shared-savings option lowers the entry cost.
- **Existing systems:** most SMEs use accounts software, not a full ERP. We export CSV and API data, not deep integration.

## 7. Deployment and business model
- **Target segment:** SMEs with continuous pumping or fan load, such as textile processing units, food and dairy plants, foundry cooling circuits, and small campuses or water utilities. [Choose one segment for the pilot and add a verified count of units.]
- **Installation:** one day per pump: clamp sensors, pressure tap, edge box, VFD commissioning, with the manual bypass kept.
- **Cost and payback (to be filled from quotes):** payback = (kit cost + drive cost) ÷ annual saving. With the simulated saving of ₹1.29 lakh/year, an assumed ₹1.2 lakh drive plus a ₹15,000 kit gives about 12–13 months. For sites that already have a VFD, only the kit is needed and payback is much shorter.
- **Pricing options:** outright purchase, or shared savings paid out of the measured rupee saving, with no upfront risk for the SME.
- **Scale-up:** (1) 3–5 pilots through a local SME cluster or industry association; (2) channel partners such as electrical distributors and VFD integrators; (3) extend the same model to compressors and fans; (4) anonymised multi-site learning so a new machine gets a good starting model.

## 8. Risks and assumptions
- Converting vibration into failure risk needs real degradation data. We will use emulated wear on a test rig or public run-to-failure datasets and label them as such.
- Savings depend on the process load profile and the static-lift share (see the sensitivity above).
- Tariff, repair-cost and downtime inputs should come from an SME's bills and invoices.
- Multi-site learning is a simulation, not a deployment.

## 9. Fit with the challenge
Primary: IoT energy monitoring with an edge dashboard, and predictive maintenance for motors. Secondary: off-peak load shifting, BEE benchmarking of specific energy consumption (benchmark to be verified), and Scope 2 CO₂ reporting.

## 10. Attached artefacts
1. `architecture.svg`: system and data-flow diagram
2. `pump_sim.py`: SEC simulation (throttle vs speed control)
3. `rupee_meter.py`: waste, repair-date and payback model
4. Still to add: dashboard wireframe and data model
