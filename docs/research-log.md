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
- Enclosure + battery capacity (sets charge current, board outline, button
  placement).
- microSD: keep, or rely on on-module flash?

## 2026-09-05 — EPD panel datasheet received (GDEY0426T82-FL01C)

- Owner supplied the panel datasheet. Confirms **GDEY0426T82-FL01C**:
  4.26" 800×480, controller **SSD1677**, 4-wire SPI, 24-pin 0.5 mm FPC;
  active area 92.8 × 55.68 mm; module outline 105.33 × 62.37 × 1.8 mm.
- Locked the **24-pin EPD FPC pinout** and the **SSD1677 external DC-DC**
  reference circuit (L 47 µH / Q Si1308EDL / D×3 MBR0530 / R 2.2 Ω sense +
  1 M pulldown / caps ≥25 V), fed from +3V3. Rails: VGH≈+20, VGL≈−20,
  VSH≈+15, VSL≈−15, VCOM≈−2 V.
- The module's mechanical drawing shows the **same dual (cold+warm) 6-pin
  frontlight** as FL0426-S01C → dual-driver design (ADR 0005) confirmed.
- Updated DESIGN.md §5, BOM (J4 24-pin + boost parts), the SKiDL generator
  (real EPD block), and ADR 0002. Verification table: EPD FPC now ✅.

## 2026-09-05 — Tooling note

- The web/CI container has no KiCad, so ERC/DRC/routing can't run here.
  Added a GitHub Actions workflow using the `kicad/kicad:8.0` image to run
  `kicad-cli` ERC/DRC and export gerbers on push — the persistent
  "KiCad-capable environment". Interactive capture/layout is done locally
  in KiCad 8.
