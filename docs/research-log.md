# Research Log

Dated, append-only exploration notes for the Mini E-Reader. Newest last.

---

## 2026-09-05 — Project kickoff / hardware design captured

- Repository started from the Colophon docs template; adapted into the
  Mini E-Reader project.
- Chose the core stack (ESP32-S3, 1S LiPo + USB-C, SPI E-Paper). Recorded
  as ADRs 0001, 0003, 0004.

## 2026-09-05 — Display identified from frontlight datasheet

- Owner supplied **Good Display FL0426-S01C** — this is a **frontlight**
  module (light guide + LEDs), *not* the e-paper panel. It fixes the
  display size at **4.26", 480×800 dots**.
- Frontlight electricals (from the drawing): two channels, **5 series
  white LEDs each, VF ≤ 15 V, IF ≤ 15 mA**; 6-pin 0.5 mm FPC
  (1 LEDC+, 2 LEDC−, 3 NC, 4 NC, 5 LEDW+, 6 LEDW−); LGP 61.40 × 104.10 mm,
  total thickness 0.685 mm; operating 0–50 °C.
- Implication: need a **dual constant-current boost driver** (~15 V,
  ≤15 mA/channel, independent PWM) for brightness + colour temperature.
  Recorded as ADR 0002 (display) and ADR 0005 (frontlight driver).
- Corrected the earlier 2.13" assumption; grew the board outline.

### Open questions
- **EPD panel datasheet** still needed to lock the display FPC pinout and
  controller (matching part: Good Display GDEQ0426T82 class, 4.26" 800×480).
- Confirm frontlight LED VF/IF/series count against the full datasheet
  before finalising R_SET and boost Cout voltage rating.
- Enclosure + battery capacity (sets charge current, board outline, button
  placement).
- microSD: keep, or rely on on-module flash?

## 2026-09-05 — Tooling note

- The web/CI container has no KiCad, so ERC/DRC/routing can't run here.
  Added a GitHub Actions workflow using the `kicad/kicad:8.0` image to run
  `kicad-cli` ERC/DRC and export gerbers on push — the persistent
  "KiCad-capable environment". Interactive capture/layout is done locally
  in KiCad 8.
