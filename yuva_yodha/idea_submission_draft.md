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
Sensors → edge device (feature extraction, physics baseline, risk model, controller) → VFD / local dashboard → optional sync for multi-site learning.

## 4. What is new, honestly
We do not claim a new algorithm. Published work already covers self-supervised fault diagnosis of motors and wear prediction. We did not find prior work that (i) turns wear and failure risk into a rupee and repair-date decision, (ii) combines it with speed control, and (iii) is validated on low-cost hardware aimed at SMEs. Multi-site learning is shown as a small simulation only.

## 5. Impact (illustrative, to be replaced by measured values)
Example: a 15 kW pump running 6,000 h/year at ₹8/kWh costs about ₹6.4 lakh/year in energy.
- Speed control at a conservative 30% saving is about **₹1.9 lakh/year**, or about **24,000 kWh** and **17 tonnes CO₂** (grid factor to be verified). Payback is about **7.5 months** on an assumed ₹1.2 lakh drive.
- Repair timing: with energy waste alone, repair pays back in about 386 days. Adding vibration-based failure risk brings the recommended repair date forward to about 49 days.
- Estimated kit cost: [to be priced from real suppliers].

We will measure the actual saving on our rig as kWh per m³ at equal flow and pressure.

## 6. Feasibility and plan (Phase 2, 11 Oct to 22 Nov)
- Weeks 1–2: build the rig, log baseline data at several speeds and loads.
- Weeks 3–4: physics baseline, waste and risk models, edge deployment.
- Weeks 5–6: controller and dashboard, then a measured before/after test and the demo.

## 7. Risks and assumptions
- Converting vibration into failure risk needs real degradation data, so we will emulate wear on the rig (for example a partly closed valve or a loosened coupling) and label it as emulated.
- Savings depend on the process load profile. We will state the conditions of each test.
- Tariff, repair-cost and downtime inputs come from an SME's bills and invoices where possible.

## 8. Fit with the challenge
Primary: IoT energy monitoring with an edge dashboard, and predictive maintenance for motors. Secondary: off-peak load shifting, BEE benchmarking of specific energy consumption, and Scope 2 CO₂ reporting.
