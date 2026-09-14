# Extracted assets — inventory

Source: `6c4007b5-ppt-_cat.pdf` (14 pages), the only deck supplied for this task.
The brief named `693e915a-587c-4c9a-963f-88d4c99d9ec6.pptx`; that file is not in
this repository or in the uploads, so images were extracted from the PDF instead
(PyMuPDF, `doc.extract_image` on every XObject).

`bg` is judged from the mean of the four corner pixels: LIGHT > 190 luma,
DARK < 110, MID in between.

| File | Src page | Size | bg | What it is | Used in new deck |
|---|---|---|---|---|---|
| `p03_img1_x38.jpeg` | 3 | 770×576 | MID | Photo: 8S2P pack, JBD BMS and BK Precision electronic load on the bench | **Slide 1** (in a light card) |
| `p03_img2_x39.jpeg` | 3 | 747×397 | DARK | Photo: KORAD programmable DC supply at 30.5 V / 10 A | no |
| `p06_img1_x51.jpeg` | 6 | 620×542 | LIGHT | Product photo: Raspberry Pi 5 with active cooler | **Slide 5** |
| `p06_img2_x52.jpeg` | 6 | 391×297 | LIGHT | Product photo: Arduino Uno R4 WiFi | **Slide 5** |
| `p07_img1_x61.jpeg` | 7 | 1518×573 | MID | Dashboard: live sensing tiles — pack V/I, temp, SOC, max/min cell, ΔV, dV/dt, charge state | **Slide 6** |
| `p07_img2_x62.jpeg` | 7 | 1495×642 | MID | Dashboard: cycle health analysis / historical comparison engine | no |
| `p08_img1_x66.png` | 8 | 1471×712 | LIGHT | Dashboard: cell-voltage + temperature chart above the alert-history table | no |
| `p08_img2_x68.png` | 8 | 1536×530 | MID | Dashboard: critical-alarm banner (BMS disconnected) + inference window | **Slide 6** |
| `p09_img1_x72.png` | 9 | 1495×720 | LIGHT | Dashboard: Battery Parameters — pack config and extracted cell parameters | no |
| `p10_img1_x76.png` | 10 | 736×482 | **DARK** | MATLAB 3-D render of the 16-cell module | no — dark theme |
| `p11_img1_x89.png` | 11 | 245×108 | DARK | Small label graphic | no |
| `p11_img2_x90.jpeg` | 11 | 347×377 | **DARK** | MATLAB plot: measured vs simulated terminal voltage, 0–4000 s | no — dark theme |
| `p11_img3_x91.png` | 11 | 343×371 | **DARK** | MATLAB plot: parameter-estimation convergence (R0/R1/R2/C1/C2) | no — dark theme |
| `p12_img1_x96.jpeg` | 12 | 1600×557 | LIGHT | Simulink screenshot of the 2RC model (R0, R1C1, R2C2, coulomb counting, OCV LUT) | no — redrawn as clean vector |
| `p12_img2..6_x102..106.png` | 12 | ~210×100 | LIGHT | Five small caption chips | no |
| `p13_img1_x109.png` | 13 | 272×197 | LIGHT | "INPUTS" caption card | no |
| `p13_img2_x110.png` | 13 | 297×187 | DARK | Teal "block" caption card | no |
| `p13_img3_x111.png` | 13 | 285×192 | LIGHT | "OUTPUTS" caption card | no |
| `p13_img4_x112.png` | 13 | 1397×557 | **DARK** | MATLAB Scope windows: voltage sag and SOC under a 30 A / 30 s discharge | no — dark theme |

Machine-readable version with exact byte sizes and corner RGB: `manifest_raw.json`.
