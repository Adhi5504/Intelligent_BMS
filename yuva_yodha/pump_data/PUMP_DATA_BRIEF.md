# Pump Data Brief — Grundfos NB 65-160/157 (No. 97839240)

Context file for Claude Code. Data files in this folder:
- `pump_curve_NB65-160-157.csv` — performance curve (14 points)
- `pump_NB65-160-157.json` — same data + all metadata, machine-readable

## 1. Pump identification
| Item | Value |
|---|---|
| Manufacturer | Grundfos |
| Model | NB 65-160/157 A-F2-A-E-BAQE (current code: NB 65-160/157 AAF2AESBAQENW1) |
| Product no. | 97839240 |
| Type | Close-coupled, single-stage, end-suction centrifugal volute pump (EN 733 / ISO 5199) |
| Impeller | 157 mm actual (160 mm nominal), cast iron |
| Inlet / outlet | DN 80 / DN 65, PN 16 |
| Motor | 11 kW P2, 2-pole, 50 Hz, IE3, 3x400 V, motor type 160MB |
| HP | ~14.75 HP (**calculated** 11/0.746, not printed) |
| Rated speed | 2940–2950 rpm (datasheet) |
| Motor efficiency | 91.2 % full load, 91.8 % 3/4 load, 91.3 % 1/2 load |
| Fluid | Water, 20 °C, 998.2 kg/m³ |
| Curve tolerance | ISO 9906:2012 Grade 3B |
| Status | **Discontinued** (Product Center, 2026-10-02) |

## 2. Performance data (Grundfos Product Center duty-point readouts)
| Q (m³/h) | H (m) | η pump (%) | P2 shaft (kW) | η pump+motor (%) | P1 input (kW) | NPSHr (m) | n (rpm) |
|---|---|---|---|---|---|---|---|
| 0.5* | 33.26 | 1.0 | 4.733 | 0.9 | 5.126 | 2.17 | 2981 |
| 1 | 33.25 | 1.9 | 4.755 | 1.8 | 5.149 | 2.19 | 2981 |
| 10 | 33.15 | 17.5 | 5.163 | 16.2 | 5.580 | 2.40 | 2979 |
| 20 | 33.01 | 31.8 | 5.641 | 29.5 | 6.087 | 2.59 | 2976 |
| 40 | 32.61 | 53.4 | 6.641 | 49.5 | 7.160 | 2.85 | 2971 |
| 60 | 31.82 | 67.9 | 7.651 | 62.9 | 8.258 | 3.08 | 2965 |
| 80 | 30.44 | 76.9 | 8.612 | 71.1 | 9.316 | 3.40 | 2959 |
| 100 | 28.22 | 81.1 | 9.464 | 74.8 | 10.27 | 3.94 | 2953 |
| 105 | 27.51 | 81.4 | 9.652 | 75.0 | 10.48 | 4.12 | 2952 |
| 108 | 27.05 | 81.4 | 9.761 | 74.9 | 10.60 | 4.24 | 2952 |
| 110 | 26.73 | 81.4 | 9.830 | 74.9 | 10.68 | 4.33 | 2951 |
| 114 | 26.07 | 81.1 | 9.961 | 74.6 | 10.83 | 4.51 | 2950 |
| 120 | 24.96 | 80.3 | 10.15 | 73.8 | 11.04 | 4.82 | 2949 |
| 130 | 22.85 | 77.6 | 10.41 | 71.2 | 11.34 | 5.43 | 2947 |

\* Lowest Q the tool accepts. **True shut-off (Q = 0) is NOT given.**

## 3. Key points
- **Rated (duty) point:** Q = 114 m³/h, H = 26.5 m (datasheet). Product Center gives 26.07 m at 114 m³/h → 0.43 m discrepancy (likely curve/motor-model revision since the 2018 datasheet).
- **BEP:** η_pump,max = 81.4 % at Q ≈ 105–108 m³/h. Not resolvable finer (QH/P2 recomputation gives 81.40 / 81.41 / 81.36 % at 105 / 108 / 110 — below input rounding).
- **η pump+motor max:** 75.0 % at 105 m³/h.
- **Max P2 along curve:** 10.59 kW < 11 kW motor → non-overloading.
- **H curve:** stable / monotonically falling from Q ≈ 0 (NO droop). Ends at ~139 m³/h.
- Curves drawn bold only from ~13 m³/h; below that is low-flow region.

## 4. Data rules / caveats (IMPORTANT for any analysis)
1. Every number in the table is copied from the manufacturer's tool readout. **Do not invent, interpolate, or extrapolate and present it as data.** Fitted curves must be labelled as fits.
2. **Shut-off head is "not given".** If a model needs H(Q=0), state it is extrapolated from a fit, or use H(0.5) = 33.26 m and label it as such.
3. **Speed is NOT constant** — 2981 rpm (near zero flow) to 2947 rpm (130 m³/h), due to motor slip. If a fixed-speed curve is needed, correct each point with affinity laws (Q ∝ n, H ∝ n², P ∝ n³) and say so.
4. η pump = upper curve on chart; η pump+motor = lower curve (confirmed by tool labels).
5. Verified: η_pump = ρgQH / P2 and η_total = ρgQH / P1 match the tool to ±0.1 % at all points (ρ = 998.2 kg/m³, g = 9.81 m/s², Q in m³/s). Motor efficiency P2/P1 = 92.7 → 91.8 % across the range.
6. The tool has a quirk: after changing Q, it keeps the previous H until re-entered. All rows here were kept only when the readout Q exactly matched the target.

## 5. Formulas
- Hydraulic power: P_h [kW] = ρ · g · (Q/3600) · H / 1000
- Pump efficiency: η_p = P_h / P2
- Overall efficiency: η_o = P_h / P1
- Motor efficiency: η_m = P2 / P1
- Affinity laws (speed n1 → n2): Q2 = Q1·(n2/n1), H2 = H1·(n2/n1)², P2 = P1·(n2/n1)³

## 6. Rejected / superseded data (do not use)
- Earlier graph readings from the PDF chart (by Claude) — biased high by up to 1.35 m in H and ~2 % in η. Superseded by the table above.
- "HMB-1500 15 HP monoblock" table on Slideshare — not a real manufacturer datasheet (constant 11.2 kW power with rising efficiency; physically implausible).

## 7. Backup (Indian manufacturer, H–Q only)
Kirloskar KDS-1040+ (7.5 kW / 10 HP, 80×65 mm, 2-pole, 2900 rpm per Kirloskar e-shop). Catalogue SP-10-2017-01 prints only discharge vs head (no η, no power, no shut-off):

| H (m) | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | 28 | 30 | 32 | 34 | 36 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q (lps) | 23.5 | 23.0 | 22.6 | 22.2 | 21.6 | 20.9 | 20.3 | 19.5 | 18.7 | 17.9 | 17.0 | 15.7 | 14.6 | 13.4 | 9.6 |

(m³/h = lps × 3.6)

## 8. Sources
- Datasheet PDF (Grundfos Product Centre print, via Lenntech): https://www.lenntech.com/uploads/grundfos/97839240/Grundfos_NB-65-160-157-A-F2-A-E-BAQE.pdf
- Grundfos Product Center: https://product-selection.grundfos.com — search "NB 65-160/157", product 97839240; data via Operating point → Input, retrieved 2026-10-02
- Kirloskar catalogue: https://mittalmachinery.in/downloads/products/KIRLOSKAR_PUMP/KDS-KS-KDT-SRF-KDI%20Catalogue%20FINAL%20Folder_CTP%20V2.pdf
