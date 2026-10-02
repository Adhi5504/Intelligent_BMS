# Which files are current (yuva_yodha/)

## Current, use these
| File | Purpose |
|---|---|
| `RESULTS_SUMMARY.md` | One-page summary of all results and limits |
| `PRICES_AND_PAYBACK.md` | Indicative prices (not quotes) and VFD payback |
| `real_pump_sim.py` | Energy saving on the real Grundfos NB 65-160/157, oversizing/lift/margin sweep |
| `sensor_value.py` | Waste split by cause and what an extra sensor is worth |
| `calibration_test.py` | Flow-free calibration anchors vs a good/bad flow reading |
| `learning_layer.py` | Calibration from logs with uncertainty band, wear drift detection |
| `extra_checks.py` | Reproduces two checks quoted in the summary |
| `pump_data/` | Manufacturer data and the data brief for the real pump |

## Earlier work on an ASSUMED generic pump (kept for reference; superseded by the real-pump files)
`pump_sim.py` (imported by other scripts), `forecast_check.py`, `softsensor_check.py`, `waste_split.py`, `setpoint_reco.py`, `fix_ranker.py`, `rupee_meter.py`.
`fix_ranker.py` still holds the cost-ranking logic (placeholder costs).

## Outdated, do not copy from these
- `idea_submission_draft.md`: describes an older version of the idea (audit/verify with different numbers).
- `architecture.svg` / `architecture.png`: show the older control-and-repair design, not the current audit + setpoint-recommendation design.

Every script is a simulation. Nothing here is a field measurement.
