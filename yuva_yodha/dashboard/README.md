# PumpRupee Audit Dashboard

Interactive dashboard for **PumpRupee**, a clamp-on pump energy-audit kit.
Schneider Electric Yuva Yodha 2026 · Track: Smart Manufacturing · Team ANS_4X.

> **Every number is simulated.** There is no lab data, no field data and no live hardware feed.
> Curves are fits to the Grundfos NB 65-160/157 manufacturer readouts; prices are indicative online prices, not quotes.

## Run locally
```bash
cd yuva_yodha/dashboard
npm install
npm run dev          # http://localhost:5173, bound to 0.0.0.0 (reachable on your LAN)
```
Production build served on port 4173:
```bash
npm run serve        # builds, then vite preview --host 0.0.0.0 --port 4173
```
Type-check only: `npm run typecheck`.

## Share it with judges anywhere
Run `npm run serve` first (or `npm run dev`), then use ONE of these.

### 1. Cloudflare quick tunnel (no account, fastest)
```bash
# install: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
cloudflared tunnel --url http://localhost:4173      # or: npm run tunnel:cloudflare
```
It prints a public `https://<random>.trycloudflare.com` link. The link lives only while the command runs.

### 2. ngrok
```bash
ngrok config add-authtoken <YOUR_TOKEN>             # once, free account
ngrok http 4173                                     # or: npm run tunnel:ngrok
```

### 3. Vercel (permanent link, nothing needs to stay running)
```bash
npm i -g vercel
cd yuva_yodha/dashboard
vercel --prod        # framework Vite, build `npm run build`, output `dist` (see vercel.json)
```
Or import the repo in the Vercel dashboard and set the **Root Directory** to `yuva_yodha/dashboard`.

`vite.config.ts` sets `allowedHosts: true`, otherwise Vite rejects tunnel hostnames.

## Structure
```
src/
  components/         Header, ModeToggle, ReportSheet, pages/ (6 tabs), ui/ (Radix-based Card, Badge, Tip, Slider, Modal, ...)
  data/generated.json simulation output (pump fits, 14-day telemetry, calibration, Shapley splits, CUSUM runs)
  types/              TypeScript types
  utils/              pumpModel.ts (port of real_pump_sim.py), format.ts (Indian ₹ grouping), modeContext.tsx
scripts/gen_data.py   regenerates generated.json from ../*.py (fixed seeds)  ->  npm run gen-data
```
`src/utils/pumpModel.ts` reproduces the Python results exactly for the base case (19.3% / 35.5%, ₹69,292 / ₹1,27,178, paybacks 8.7 / 4.7 / 18.9 / 10.3 months).

## What each tab shows
1. **Executive Overview**: KPIs for constant vs proportional pressure, cheapest-fix-first order, SEC chart, honest limits.
2. **Live Audit**: simulated playback of 14 days of ESP32 telemetry, sensorless-flow calibration (1/3/7/14 days), H–Q and P–Q curves.
3. **Shapley Waste Split**: who is to blame, and what S0/S1/S2 sensor tiers remove.
4. **VFD Payback Simulator**: sliders re-run the pump model live, GO / CONDITIONAL / NO-GO verdict.
5. **CUSUM Wear Monitor**: stress-tested drift detection (slow, fast, step, control).
6. **Before / After M&V**: IPMVP-style table and a printable executive report.
