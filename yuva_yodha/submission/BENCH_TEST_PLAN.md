# Bench test plan (DESIGNED, NOT YET RUN)

Nothing below has been tested. Acceptance targets are proposals to be agreed before the test, not results.

| Test | Method | Pass idea (to agree beforehand) |
|---|---|---|
| Flow inference | Small pump + reference flow meter; log power and pressure; compare inferred flow | Error stated against the reference meter, per operating point |
| Throttling waste split | Close the valve in steps at fixed speed | Valve share rises as the valve closes |
| Blocked strainer | Partly block the suction strainer | Visible only with P1 / strainer-dP or P3; invisible with power + P2 alone (as simulated) |
| Wear drift | Substitute a worn or trimmed impeller | CUSUM alarms before ~4% performance loss |
| System-curve fit | Measure P3 across flow steps | Forecast within ~3 points of measured saving |
| Before/after | Fit a VFD (or trim) and re-measure | Measured saving vs forecast |

Minimum kit: power clamp + voltage sensor + discharge pressure (P2). Add P3 (process side) to measure the system curve.
Run only within the pump maker's limits (brief closed-valve operation).
