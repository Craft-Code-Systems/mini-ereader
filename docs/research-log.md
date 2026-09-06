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

## 2026-09-05 — Branch merge + design comparison

Merged `claude/schematics-pcb-review-rq1i2t` into `main` (the
`colophon-standard-compliance` branch had no unique commits). Main now holds
two design tracks; **`ereader.*` (Rev C) is canonical**.

Comparison — first-try board (`ereader.*`) vs the `hardware/` reference spec:

| Area | ereader.* (Rev C, canonical) | hardware/ (reference spec) |
|------|------------------------------|----------------------------|
| MCU | ESP32-S3-WROOM-1-**N16R8** | ...-N8R2 (same family) |
| Charger | **BQ25628E** I2C buck 2A, SoC-managed 80/50 | MCP73831 linear 500 mA |
| 3V3 reg | **TPS62840** buck (60 nA Iq) | AP2112 LDO |
| Fuel gauge | **MAX17048** ModelGauge (I2C) | resistor divider → ADC |
| Frontlight | **LM3630A** single-boost/dual-sink (I2C) | 2× TPS61165 (2 inductors) |
| Input | 3 buttons + **rotary encoder** | 3 buttons |
| EPD | SSD1677 24-pin + boost ("copy ref schematic") | SSD1677 24-pin + boost **with exact values** |
| USB ESD | USBLC6-2 (placed) | USBLC6-2 (recommended) |
| PCB | **real: 56 fp, 237 nets, 4-layer, placed/planed/stitched, DRC-ruled, NOT routed** | scaffold outline only |
| Compliance | detailed FCC/CE + magnet/phone-attach analysis | notes |
| Fab | `fab.py` + `ereader-gerbers.zip` | CI (`kicad-cli`) |

Verdict: `ereader.*` is more advanced and is the real board → **canonical**.
`hardware/` keeps value only as (a) the CI, now retargeted to
`ereader.kicad_pcb`; (b) repo hygiene (Colophon cleanup, e-reader docs);
(c) the **exact SSD1677 boost values** worth porting into
`ereader-pcb-design.md` §6.

Recommended consolidation (deferred to owner): adopt Rev C parts as
canonical (write a superseding ADR; my `docs/adr/0003` power + `0005`
frontlight describe the simpler variant), fold the SSD1677 boost values
into `ereader-pcb-design.md`, then remove the `hardware/` scaffold KiCad
files and remaining cruft (`.history`, `ereader-gerbers.zip`).

## 2026-09-06 — Consolidation executed (single project + ADRs reconciled)

- Removed the `hardware/` scaffold KiCad project (`mini-ereader.*` + empty
  lib tables). The board is now a single canonical KiCad project, `ereader.*`
  at the repo root; `hardware/` keeps only the electrical source-of-truth
  docs. Docs/runbook/CI/ADR-0002 references retargeted.
- Reconciled the ADRs to the Rev C parts: **0006** (I2C-managed power path —
  BQ25628E + TPS62840 + MAX17048, two I2C buses) supersedes **0003**;
  **0007** (LM3630A single-boost dual-sink frontlight) supersedes **0005**.
  0003/0005 marked Superseded, reasoning preserved.
- The `-N16R8` module variant is treated as a selection under ADR 0001, not a
  new decision. Still open (deferred): the input change (3 buttons +
  SLLB510200 rotary encoder) has no ADR yet; folding the exact SSD1677 boost
  values from `hardware/DESIGN.md` §5 into `ereader-pcb-design.md` §6; and
  removing the remaining `ereader-gerbers.zip` build artifact.
