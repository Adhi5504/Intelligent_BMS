# AI-PBMS decks — build notes

Two cuts of the same material, sharing one design system:

| File | Slides | Talk time | For |
|---|---|---|---|
| `AI_PBMS_8Slide.pptx` | 8 | ~4.6 min | the short pitch |
| `AI_PBMS_Full_Deck.pptx` | 20 | ~12.1 min | the full technical review |

Both are 16:9 (13.333 × 7.5 in), light technical theme, with a speaker note on
every slide. Rebuild everything with:

```bash
python3 deck/make_charts.py       # figures batch 1   -> assets/generated/
python3 deck/make_charts2.py      # figures batch 2   -> assets/generated/
python3 deck/make_diagrams.py     # vector schematics -> assets/generated/
python3 deck/make_ui.py           # UI mockups + flow -> assets/generated/
python3 deck/build_deck.py        # -> AI_PBMS_8Slide.pptx
python3 deck/build_deck_full.py   # -> AI_PBMS_Full_Deck.pptx
```

`deck/theme.py` holds the single palette/font definition shared by the matplotlib
figures and the PPTX shapes; `deck/_helpers.py` holds the shared slide primitives.

## The 20-slide running order

1. Title · 2. Why we built the dataset · 3. **What the logging showed** ·
4. Why 8S2P · 5. 1RC → 2RC and OCV · 6. Data pipeline and labelling ·
7. **Feature engineering** · 8. **Training-set construction** · 9. Why XGBoost ·
10. **Per-class performance** · 11. Six classes and confidence ·
12. **Out-of-distribution gate** · 13. Hardware tiers · 14. **End-to-end system** ·
15. Live dashboard · 16. **Thermal and driving context** · 17. **Cycle prognosis** ·
18. **Battery Parameters screen** · 19. Multi-chemistry engine · 20. **Roadmap**

Bold = new in the 20-slide cut.

---

## Read this before you present

**1. The 98.55% headline does not match any model in this repository.** The brief
gives 98.55% accuracy / 0.85 ms, and slide 4 states exactly that. But the shipped
checkpoint `models/bms_xgboost_model.json`, re-evaluated here against the held-out
test split of `data/augmented_telemetry_dataset.xlsx` (30,000 rows), scores
**94.21%**. `outputs/xgboost_training_report.txt`, from an earlier run, records
**91.68%**. The confusion matrix on slide 7 is generated from the 94.21% run —
it is real measured output, not the 98.55% run, which I do not have. Either point
me at the 98.55% artefacts and I will regenerate the matrix, or drop slide 4 to
94.21% so the deck is internally consistent. Raw numbers:
`assets/generated/confusion_matrix_source.json`.

**2. Two brief-supplied figures could not be drawn as specified.**

- *Fault class distribution, six bars.* Only one proportion exists — Cell
  Imbalance at 70.2%. The per-class split of the remaining 29.8% is not in the
  brief and no labelled file in `data/` reproduces a 70.2% distribution
  (`bms_data_corrected (3).csv` is 155,023 rows but 100% label 0;
  `augmented_telemetry_dataset.xlsx` is the rebalanced 208k-row set). The chart
  therefore shows **two bars, 70.2% vs 29.8%**, with the aggregation stated on
  the figure. Give me the six counts and it becomes a six-bar chart.
- *Model comparison, accuracy vs inference latency, grouped bars.* The brief
  gives accuracy and latency for XGBoost only. Plotting five more model pairs
  would mean inventing ten numbers, so slide 4 carries the qualitative comparison
  **table** (which the brief made table-dominant anyway) with "—" in the two
  measured columns, plus a two-card panel stating the XGBoost figures. If you
  want the grouped bar chart, send me measured accuracy and latency for the other
  five. Note `outputs/training_report.txt` does record **86.32%** for the
  Transformer over five classes — I left it out because the brief said to use only
  its own numbers, but it is available.

**3. What the OCV–SOC chart actually plots.** The NMC curve is real: the
breakpoint table `[43.3 … 90.9]% → [27.3 … 32.58] V` lifted from the 1-D Lookup
Table block inside `E2RC_FINAL_4000sec_model.mdl`, this project's own 2RC
parameter-estimation model, divided by 8 for per-cell. No LFP cell was
characterised here, so **LFP is drawn as its 2.50–3.65 V datasheet window from the
brief, labelled as a window, not as a curve.** The measured NMC slope
(13.4 mV per 1% SOC) is computed from those breakpoints.

**4. Dark-theme extracted images — flagged, not used.** Five images in the source
deck are dark-background MATLAB output: the 3-D module render
(`p10_img1_x76.png`), the measured-vs-simulated voltage plot
(`p11_img2_x90.jpeg`), the parameter-estimation convergence plot
(`p11_img3_x91.png`), and the Scope windows (`p13_img4_x112.png`). None is in the
deck. The measured-vs-simulated and Scope plots are the valuable ones — if you
send the underlying time series I will regenerate them on the light theme.

**5. The web-app screenshots were pasted into chat, not supplied as files**, so
there was nothing on disk to embed. Both screens — the landing page and the
Battery Parameters upload screen — are therefore **redrawn as vector mockups**
(`deck/make_ui.py`) in the deck's own palette, matching the layout, copy and
accent colours of the screenshots. Send the actual PNGs and I will swap them in;
`build_deck_full.py` only needs the same two filenames.

**6. Two numbers come from repo file sizes, not the brief.** The "~1.4 MB" and
"~1.6 MB" in slide 4's Size column are the on-disk sizes of
`models/bms_xgboost_model.json` (1,395,670 B) and
`models/battery_fault_transformer.pth` (1,591,456 B). Say the word and they go.

---

## Visual provenance

### Generated (matplotlib, 300 DPI, light theme) — `assets/generated/`

Batch 2 (`deck/make_charts2.py`) is entirely measured from repository files —
no brief numbers are involved in any of it:

| File | Slide | Data source |
|---|---|---|
| `fig_cell_traces.png` | 3 | **Measured** — 2,400 consecutive rows of `data/bms_data_corrected (3).csv`; the 289 mV cell_v1 gap is computed from that window |
| `fig_feature_importance.png` | 7 | **Measured** — gain importances read from `models/bms_xgboost_model.json` |
| `fig_dataset_composition.png` | 8 | **Measured** — class and split counts from `data/augmented_telemetry_dataset.xlsx` (208,010 rows) |
| `fig_per_class_metrics.png` | 10 | **Measured** — precision/recall/F1 derived from the same confusion matrix as slide 11 |
| `fig_ood_panel.png` | 12 | **Measured** — `outputs/ood_evaluation_report.txt` (AUROC 0.913, 100% precision, 0% FPR, 24.5% recall) |
| `fig_thermal_zones.png` | 16 | **Measured** — four NTC channels over the same logged window |
| `fig_driving_modes.png` | 16 | **Measured** — `driving_mode` distribution over 155,023 rows |
| `fig_cycle_history.png` | 17 | **Measured** — all 39 cycles in `data/cycle_history.json` |
| `mock_landing.png` | 1 | Vector recreation of the supplied screenshot — see note 5 |
| `mock_battery_params.png` | 18 | Vector recreation of the supplied screenshot — see note 5 |
| `diag_system_flow.png` | 14 | Drawn — edge / service / interface data path |
| `diag_confidence_ladder.png` | 12 | Drawn — OOD gate → classifier → confidence band |

Batch 1 (`deck/make_charts.py`, `deck/make_diagrams.py`):

| File | Slide | Data source |
|---|---|---|
| `fig_class_distribution.png` | 3 | Brief (70.2%); remainder by closure — see note 2 |
| `fig_confusion_matrix.png` | 7 | **Measured** — `models/bms_xgboost_model.json` on the test split, row-normalised recall |
| `fig_model_performance.png` | 4 | Brief (98.55%, 0.85 ms) — replaces the grouped bar chart, see note 2 |
| `fig_confidence_bands.png` | 7 | Brief (0–0.50 / 0.50–0.85 / 0.85–1.00) |
| `fig_ocv_soc.png` | 8 | **Measured NMC** from `E2RC_FINAL_4000sec_model.mdl`; LFP window from brief — see note 3 |
| `diag_pack_8s2p.png` | 2 | Drawn — 8S2P topology, per-cell taps to the BMS rail |
| `diag_2rc_ecm.png` | 2 | Drawn — OCV source, R0, R1‖C1, R2‖C2, values from the brief |
| `diag_hardware.png` | 5 | Drawn — BMS → Pi 5 → Arduino R4, BLE and RUN-pin arrows |
| `diag_configurator.png` | 8 | Drawn — datasheet → parser → sizing → tiering → thresholds → profile |
| `diag_chemistry_tiering.png` | 19 (full deck) | Drawn — NMC/NCA/LFP/LTO ladder. Unused in the 8-slide cut, where the OCV–SOC chart takes that slot. |

All figures are written with an explicit `#FFFFFF` figure and axes facecolor and
`transparent=False`; none has a dark or transparent background.

### Extracted (from the supplied PDF) — `assets/extracted/`

Five of 23 images are reused; the rest are inventoried with a background
judgement in `assets/extracted/MANIFEST.md` (+ `manifest_raw.json`).

| File | Slide | What it is |
|---|---|---|
| `p03_img1_x38.jpeg` | 1 | Bench photo: pack, JBD BMS, electronic load |
| `p06_img1_x51.jpeg` | 5 | Raspberry Pi 5 |
| `p06_img2_x52.jpeg` | 5 | Arduino Uno R4 WiFi |
| `p07_img1_x61.jpeg` | 6 | Dashboard live sensing tiles |
| `p08_img2_x68.png` | 6 | Dashboard critical-alarm path |

Every extracted image sits inside a white card with a 1 px `#CBD5E1` border, so
the photo and screenshot backgrounds do not clash with the slide.

### Not reused

`693e915a-...pptx` was never available — only `6c4007b5-ppt-_cat.pdf`. Likewise
`bms_data_labeled.xlsx` and `HPCC_one_last_time.xlsx` are not in the repo; the
closest equivalents used were `data/bms_data_corrected (3).csv` (155,023 rows,
confirms cell_v1 at −0.253 V vs row median) and
`data/augmented_telemetry_dataset.xlsx`.

---

## Spec compliance

| Requirement | Status |
|---|---|
| 16:9, 13.333 × 7.5 in | 13.333 × 7.500 |
| Palette #FFFFFF / #F1F5F9 / #0F172A / #475569 / #CBD5E1 / #0E7490 / #B45309 / #B91C1C | one definition in `deck/theme.py` |
| Inter or Montserrat headings, fallback Calibri | **Inter** — not on the system, so installed to `/usr/share/fonts/truetype/inter` for matplotlib; `theme.py` falls back through Montserrat → Open Sans → Calibri → Liberation Sans if absent |
| Headings 32–36 pt bold #0F172A | 33 pt bold |
| Body 16–18 pt | 15.5–17 pt (15.5 on slide 8, which carries six bullets) |
| Max 6 bullets / 12 words | max 6 bullets, longest bullet 12 words |
| Title top-left, content ~55%, visual ~45% | content 6.34 in, visual 5.87 in |
| Slide 4 table-dominant; slide 8 two visuals side by side | yes |
| Slide number bottom-right, muted; accent rule under title | yes |
| Light-theme plots, no dark/transparent PNG | verified per figure |
| Speaker note on every slide | 8/8, 74–98 words (~30–39 s) |
| No "Thermal Runaway Risk" / "Sensor Drift" | verified absent from body text and notes |
| Opens without repair | validated: zip integrity, all 85 XML parts well-formed, reopens in python-pptx, converts in LibreOffice Impress |
