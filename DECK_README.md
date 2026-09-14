# AI-PBMS decks — build notes

Two cuts of the same material, sharing one design system:

| File | Slides | Talk time | For |
|---|---|---|---|
| `AI_PBMS_8Slide.pptx` | 9 | ~6.2 min | the whole story, condensed (8 + references) |
| `AI_PBMS_Full_Deck.pptx` | 21 | ~13.3 min | the same material, room to breathe |

The 8-slide cut is not a subset — it carries all twenty slides' content at two to
three topics per slide, with a two-column bullet block and stacked visuals.

Both are 16:9 (13.333 × 7.5 in), light technical theme, with a speaker note on
every slide. Rebuild everything with:

```bash
python3 deck/make_charts.py       # figures batch 1   -> assets/generated/
python3 deck/make_charts2.py      # figures batch 2   -> assets/generated/
python3 deck/make_diagrams.py     # vector schematics -> assets/generated/
python3 deck/make_ui.py           # UI mockups + flow -> assets/generated/

# the model benchmark (once; results are committed under outputs/benchmark/)
python3 deck/prepare_benchmark_data.py   # identical splits for every model
python3 deck/bench_sklearn.py            # XGBoost, Random Forest, SVM
python3 deck/bench_torch.py              # LSTM, Transformer (60-row lookback)
python3 deck/bench_rules.py              # threshold-based BMS baseline
python3 deck/make_benchmark_chart.py     # -> fig_model_benchmark.png
python3 deck/build_deck.py        # -> AI_PBMS_8Slide.pptx
python3 deck/build_deck_full.py   # -> AI_PBMS_Full_Deck.pptx
```

`deck/theme.py` holds the single palette/font definition shared by the matplotlib
figures and the PPTX shapes; `deck/_helpers.py` holds the shared slide primitives.

## The 8-slide running order

1. Why we built the dataset (+ the 289 mV evidence) · 2. Pack topology and the 2RC
model · 3. Pipeline, features and the balanced training set · 4. **The six-model
benchmark** · 5. Per-class performance, confidence bands and the OOD gate ·
6. Hardware tiers and end-to-end system · 7. The platform, driving context and
cycle prognosis · 8. Multi-chemistry adaptation and roadmap · 9. **References**

## References (slide 9 / slide 21)

The five literature entries are taken **verbatim** from the literature slide of
the supplied source deck (`6c4007b5-ppt-_cat.pdf`, page 14) — titles, venues and
DOIs unchanged. Nothing was added to that list.

The other two blocks are sourced from this repository and this machine, not
invented: the **primary sources** are the five datasheet PDFs actually filed
under `cell datasheet/` (LG INR21700-M50, DMEGC INR21700-45E, Panasonic
NCR18650B, P3 3232 LFP 26650, JBD SP24S007 V1.1), and the **stack** line lists
the library versions the benchmark actually ran against.

The four **method** citations (Chen & Guestrin 2016; Liu, Ting & Zhou 2008;
Vaswani et al. 2017; Pedregosa et al. 2011) are the canonical papers for
XGBoost, Isolation Forest, positional encoding and scikit-learn. They are given
in author/title/venue/year form with **no DOI**, because I did not want to risk
transcribing a link I could not verify from here. If you want DOIs on those
four, add them and I will format them to match.

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

**1. Every model in the comparison is now measured, and XGBoost is not the most
accurate.** All six were trained and scored here on the identical 30,000-row
held-out split with the same 51 features (`deck/bench_*.py`,
`outputs/benchmark/all_results.json`):

| Model | Accuracy | Macro F1 | Latency | Size | How |
|---|---|---|---|---|---|
| XGBoost | 94.19% | 0.905 | 0.462 ms | 1.40 MB | shipped checkpoint |
| Transformer | 95.11% | 0.918 | 0.419 ms | 0.31 MB | 60-row lookback, 6 epochs, trained in 190s |
| LSTM | 87.03% | 0.776 | 0.532 ms | 0.28 MB | 60-row lookback, 6 epochs, trained in 59s |
| Random Forest | 89.37% | 0.824 | 33.770 ms | 176.41 MB | 200 trees, trained in 30s |
| SVM (RBF) | 88.53% | 0.807 | 0.568 ms | 2.82 MB | 20k subsample, trained in 3s |
| Rule-based BMS | 22.09% | 0.224 | 0.005 ms | 0.00 MB | project's own NMC thresholds; no Weak Cell rule exists |

The **Transformer beats XGBoost by 0.92 points**. Slide 4 does not claim
otherwise. It argues the deployment constraints instead, and every one of them
is measured (`fig_deployment_tradeoff.png`):

| Constraint | XGBoost | Transformer |
|---|---|---|
| Cold start | 1 row → first prediction at t = 1 s | 60 rows → blind for 60 s at 1 Hz |
| Runtime on the Pi | xgboost, 239 MB | torch, 1,199 MB (5×) |
| Input shape | any row, any time | positional encoding pins it to exactly 60 |
| Attribution | per-feature gain, auditable | attention only, not per-feature |
| In-browser retrain | ships today | not feasible on a Pi |

That is a sound engineering case and it survives scrutiny. **Two related claims
do not, and are deliberately absent from the deck:**

*"XGBoost is more accurate."* It is not, on this data — 94.19% vs 95.11%, printed
in the same table. Writing the opposite next to those numbers would discredit
every other figure on the slide.

*"The Transformer needs a heavy dataset."* Tested directly
(`deck/bench_data_efficiency.py`): both models trained on 5/10/25/50/100% of the
same split, scored on the same untouched test set.

| Train rows | XGBoost | Transformer | XGBoost − Transformer |
|---|---|---|---|
| 7,000 | 72.27% | 74.20% | -1.93 |
| 14,000 | 82.26% | 84.06% | -1.80 |
| 35,000 | 86.11% | 88.53% | -2.42 |
| 70,000 | 89.28% | 93.06% | -3.78 |
| 140,000 | 91.70% | 94.80% | -3.10 |

The Transformer is ahead at **every** data scale, including 7,000 rows. It is
also only 74,630 parameters and 0.31 MB — smaller on disk than XGBoost's 1.40 MB.
"Heavy" is true of the *runtime* (torch) and the *input window*, not of the model
or its data appetite. The deck says it that way.

Two caveats stated on the slide itself: latency is measured on this 4-core
container, **not on a Pi 5**; and the RBF SVM was trained on a stratified 20k
subsample because full-data RBF did not converge in usable time.

The rule-based baseline at **22.09%** is the most useful number on the slide.
It fails because cell 1's chronic 289 mV gap puts **83.6% of healthy rows over
the 0.15 V imbalance threshold**, so a conventional controller false-alarms on
71% of Normal rows — and still scores **0% recall on Weak Cell**, because no
threshold can express "degrading but inside limits".

**2. The brief's 98.55% does not match any model in this repository.** The brief
gives 98.55% accuracy / 0.85 ms, and slide 4 states exactly that. But the shipped
checkpoint `models/bms_xgboost_model.json`, re-evaluated here against the held-out
test split of `data/augmented_telemetry_dataset.xlsx` (30,000 rows), scores
**94.21%**. `outputs/xgboost_training_report.txt`, from an earlier run, records
**91.68%**. The confusion matrix on slide 7 is generated from the 94.21% run —
it is real measured output, not the 98.55% run, which I do not have. Either point
me at the 98.55% artefacts and I will regenerate the matrix, or drop slide 4 to
94.21% so the deck is internally consistent. Raw numbers:
`assets/generated/confusion_matrix_source.json`.

**3. Two brief-supplied figures could not be drawn as specified.**

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

**4. What the OCV–SOC chart actually plots.** The NMC curve is real: the
breakpoint table `[43.3 … 90.9]% → [27.3 … 32.58] V` lifted from the 1-D Lookup
Table block inside `E2RC_FINAL_4000sec_model.mdl`, this project's own 2RC
parameter-estimation model, divided by 8 for per-cell. No LFP cell was
characterised here, so **LFP is drawn as its 2.50–3.65 V datasheet window from the
brief, labelled as a window, not as a curve.** The measured NMC slope
(13.4 mV per 1% SOC) is computed from those breakpoints.

**5. Dark-theme extracted images — flagged, not used.** Five images in the source
deck are dark-background MATLAB output: the 3-D module render
(`p10_img1_x76.png`), the measured-vs-simulated voltage plot
(`p11_img2_x90.jpeg`), the parameter-estimation convergence plot
(`p11_img3_x91.png`), and the Scope windows (`p13_img4_x112.png`). None is in the
deck. The measured-vs-simulated and Scope plots are the valuable ones — if you
send the underlying time series I will regenerate them on the light theme.

**6. The web-app screenshots were pasted into chat, not supplied as files**, so
there was nothing on disk to embed. Both screens — the landing page and the
Battery Parameters upload screen — are therefore **redrawn as vector mockups**
(`deck/make_ui.py`) in the deck's own palette, matching the layout, copy and
accent colours of the screenshots. Send the actual PNGs and I will swap them in;
`build_deck_full.py` only needs the same two filenames.

**7. Model sizes are now measured, not estimated.** Every Size figure is the serialised
model written to disk during the benchmark run, not an estimate.

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
