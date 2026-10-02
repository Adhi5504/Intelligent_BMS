# Indicative prices and payback (found online 2026-10-02; NOT quotes)

Prices come from search-result listings of Indian sellers. They vary by seller, date, quantity and GST. Treat them as indicative and get a real quote before quoting a payback.

## Logger parts (retail, India)
| Part | Indicative price | Source / note |
|---|---|---|
| ESP32 dev board (ESP-WROOM-32) | Rs 399-449 | Robu listings |
| Split-core current clamp SCT-013-000 100 A | Rs 349 + 18% GST (about Rs 412); Rs 619-729 elsewhere | ElectronicsComp, Robodo, Robocraze. Hobby-grade sensor, not a certified meter |
| AC voltage sensor ZMPT101B | Rs 92-289 (typical Rs 115-140) | Several retailers. Single-phase module; mains wiring by a qualified electrician |
| Pressure transmitter 0-10 bar, 4-20 mA | Rs 2,100-3,068 (basic); Rs 7,500-12,000 (1/2 in BSP flush-diaphragm spec) | Nishka, Utopia, Shri Instruments listings |
| Enclosure, supply, 4-20 mA interface, wiring | **Not priced; assumed Rs 2,000** | assumption |

**Kit totals (computed):** basic single-phase audit kit about **Rs 6,100**; three-phase kit with a second transmitter for strainer pressure drop about **Rs 10,200**; pessimistic (Rs 12,000 pressure sensors) about **Rs 28,100**. A certified power meter would cost more than hobby-grade clamps.
**Stress tests show a process-side pressure sensor is the most valuable extra sensor**: a third transmitter adds about Rs 3,068, taking the three-phase kit to about **Rs 13,300** (about Rs 31,200 with Rs 12,000 industrial transmitters).

## VFD, about 11 kW (15 HP), 3-phase
| Listing | Price |
|---|---|
| Delta MS300 VFD25AMS43ANSAA | about Rs 29,230-35,200 |
| Delta 11 kW VFD110V43B-2 (Industrybuying) | Rs 79,999 + 18% GST (about Rs 94,400) |
| Other listings seen | Rs 21,240 (a trader, 15 HP Delta, unverified); Danfoss 15 kW and ABB 73 A are larger classes, not used |

Installation (panel, wiring, commissioning): **not found; assumed Rs 15,000**.

## Payback of the VFD on the real pump model
Months = (VFD + Rs 15,000 install) / annual saving. Annual saving from `real_pump_sim.py` (300 days, 16 h, Rs 8/kWh).

| Case | Annual saving (constant / proportional pressure) | Payback, low VFD price (Rs 50,200 total) | Payback, high VFD price (Rs 1,09,400 total) |
|---|---|---|---|
| Main: peak 90%, lift 10 m | Rs 69,292 / 1,27,178 | 8.7 / 4.7 months | 18.9 / 10.3 months |
| More oversized: peak 80%, lift 10 m | Rs 1,11,890 / 1,54,215 | 5.4 / 3.9 months | 11.7 / 8.5 months |
| Pessimistic: peak 95%, lift 20 m | Rs 28,526 / 55,118 | 21.1 / 10.9 months | 46.0 / 23.8 months |

Reading: for an oversized, throttled pump the payback is roughly 4-19 months; for a nearly right-sized pump with high static lift it can exceed 2-4 years, so the audit's job is to tell the owner which case they are in.
The audit kit itself is shared across pumps and is not included in these paybacks.
