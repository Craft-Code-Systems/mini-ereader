# Changelog

All notable changes to the Mini E-Reader project. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); dates are ISO-8601.

## [Unreleased]

### 3D views: SW4 lever corrected + self-contained bodies for every component (2026-09-06)
- **SW4 (ALPS SLLB5) 3D body fixed.** The old `ereader.3dshapes/ALPS_SLLB5_Lever.wrl`
  rendered as a tall block with an upward box knob — an "odd big switch". The SLLB5 is
  actually a **flat semicircular "fan" puck** (W 9.5 × D 8.8 × **H 2.2 mm**, the
  datasheet Lever-Return family) that lies on the board with a **low sideways
  rocker/toggle lever** on top (flick left↔right = CW/CCW, press = PUSH). Rebuilt the
  body as the flat puck + sideways lever to match the ALPS datasheet drawing/photo.
- **The whole board now renders in the 3D viewer without KiCad's stock 3D libraries.**
  Every placed component previously pointed at stock `${KICAD6/7_3DMODEL_DIR}` packs,
  which go missing on any machine/CI without the KiCad 3D-model add-on — so most parts
  showed no 3D body. Added simplified project-local bodies for all remaining footprints
  (R/C/L passives, `SOT-23-6`, `SON-8`, `DFN-8`, `HVQFN-24`, `ESP32-S3-WROOM-1`,
  `Maxim_WLP-12`, `D_SOD-123`, `USB_C_Receptacle_HRO_TYPE-C-31-M-12`, `JST_PH_S2B-PH-K`,
  `Hirose_FH12-6S/24S`, `microSD_HC_Hirose_DM3AT`) in `ereader.3dshapes/*.wrl`, and
  repointed all 43 stock `(model …)` refs in `ereader.kicad_pcb` to
  `${KIPRJMOD}/ereader.3dshapes/…` at `scale 0.3937`. Bodies are box/cylinder stand-ins
  sized from each part's datasheet/footprint outline (colour-coded by class) — for
  visualisation only; swap in vendor STEP/WRL before fab. Fiducials, M2 mounting holes,
  and the bare `JumperPad_2P_P2.0mm` keep no body. Updated `ereader-footprints.md`.

### BOOT/RESET switches replaced with bare jumper pads (2026-09-06)
- **SW5/SW6 → JP5/JP6.** BOOT and RESET are no longer Würth WS-TASU tactiles —
  they're bare 2-pad exposed jumpers (`ereader:JumperPad_2P_P2.0mm`, hand-drawn,
  two 1.2×1.2 mm pads on 2 mm pitch, no switch part), momentarily shorted with a
  screwdriver tip or tweezers to pull `IO0_BOOT`/`EN` low. Same board position and
  nets as the tactiles they replace (pad 1 → `IO0_BOOT`/`EN`, pad 2 → `GND`), so
  routing/placement elsewhere is unaffected; drops two tactile switches from the
  BOM. Updated `ereader-connection-list.md`, `ereader-schematic.md`,
  `ereader-pcb-design.md`, `ereader-footprints.md`, `ereader-kicad.net`,
  `ereader.cmp`, `ereader.kicad_pcb`, `ereader-placement.svg`, and ADR 0008.
  Hand-drawn pad geometry (no datasheet, since there's no part to order) —
  still to be DRC'd against fab minimum clearance and the case cutout before fab.

### Switch footprints locked to datasheets (2026-09-06)
- **Tactiles → Würth WS-TASU 436351045816** (4.7×3.5 mm side push with boss).
  Replaced the generic `Tact_Side_TS1187A` stand-in with `ereader:WE_WS-TASU_436351045816`,
  its land drawn from the WE datasheet (rev 001.003): 4 pads 1.2×0.7 mm at x=±2.8 /
  y=±1.35 plus **two Ø0.75 boss holes** at y=±1.375 (pins 1≡3 top, 2≡4 bottom). SW1–SW3
  and SW5/SW6 rotated **270°** so the actuator faces the right board edge.
- **SW4 → exact ALPS SLLB5 land.** Rebuilt `ereader:ALPS_SLLB5_Lever` from the ALPS
  datasheet (p.491): 4 signal pads 1.0×1.3 mm on **2 mm pitch** in terminal order
  **CW / COM / PUSH / CCW**, plus **two Ø1.1 locator holes** at x=±1.9 and side solder
  lugs; body 9.5×8.8 mm. Rotated **90°** so the lever faces the left edge. Nets
  unchanged (LEV_CW/CCW/PUSH + COM→GND).
- 3D bodies (`ereader.3dshapes/*.wrl`) and `ereader-kicad.net` / `ereader.cmp` updated
  to the new footprint ids. Lands are datasheet-drawn but still to be DRC'd against the
  ordered part before fab.

### Switches + schematic (2026-09-06)
- **Navigation buttons are now genuinely side-actuated.** SW1–SW3 (and BOOT/RESET
  SW5/SW6) moved off the top-actuated `Button_Switch_SMD:SW_SPST_TL3342` stand-in
  onto a new project footprint `ereader:Tact_Side_TS1187A_4P_3.5x4.7mm` (TS-1187A /
  YD-3414 class), with the actuator facing the board edge — required because the
  screen covers the whole front and magnets hold the back to the phone, so top/bottom
  actuation is unreachable. SW1–SW3 rotation set to 0° so the actuators point at the
  right edge; nets (BTN_A/B/C, IO0_BOOT, EN, GND) preserved.
- **SW4 lever land built.** Replaced the `PinHeader_1x04` placeholder with
  `ereader:ALPS_SLLB5_Lever` (ALPS SLLB5, ~9.5×8.8×2.2 mm) whose pads are named
  **CW/CCW/PUSH/COM**, so `LEV_CW`(23)/`LEV_CCW`(24)/`LEV_PUSH`(25) and `COM→GND`(5)
  now connect on netlist import instead of sitting unconnected. Noted SLLB510100 as a
  pin-compatible alternative.
- Added project footprint library `ereader.pretty` (registered in a new `fp-lib-table`)
  and simplified 3D bodies in `ereader.3dshapes/*.wrl` (referenced with `scale 0.3937`)
  so the switches render in the 3D viewer without KiCad's stock libraries. Updated
  `ereader-kicad.net` + `ereader.cmp` footprint IDs to match. Lands are approximate
  stand-ins — DRC vs the ordered MPN before fab.
- **Added a reviewable schematic, `ereader-schematic.md`** (subsystem Mermaid
  diagrams built from the connection list; renders on GitHub). Documents why the
  netlist-first design has no native Eeschema `.kicad_sch` and how to draw one. Updated
  `ereader-footprints.md`, `ereader-README.md`, `ereader-pcb-design.md`, and ADR 0008.
- **Removed the legacy `hardware/` reference spec** (`DESIGN.md`, `BOM.csv`,
  `gen_netlist_skidl.py`, its `README.md`) — the older 3-button lineage with a
  conflicting parts list (MCP73831 / AP2112K / TPS61165), superseded by the canonical
  `ereader.*` docs. Redirected all live references (README, `docs/runbook.md`, the
  CI workflow trigger paths + comment, ADRs 0001/0002/0003/0008, and the
  `ereader-pcb-design.md` DC-DC provenance note) to the `ereader-*` docs so there is a
  single source of truth. Historical entries in this changelog and `docs/research-log.md`
  are left as-is.

### Merged / consolidated (2026-09-05)
- Merged `claude/schematics-pcb-review-rq1i2t` into `main` alongside the
  first-try board `ereader.*` (`colophon-standard-compliance` had no unique
  commits). Clean merge (disjoint paths).
- Established the actual KiCad board **`ereader.*` (Rev C) as canonical**;
  `hardware/` is now labelled a reference spec. Full comparison in
  `docs/research-log.md`.
- Retargeted the KiCad CI workflow at `ereader.kicad_pcb` (DRC + gerber
  export). Removed a stray `~ereader.kicad_pro.lck`; git-ignore KiCad/lock/
  history/gerber cruft going forward.
- **Consolidated to a single KiCad project.** Removed the redundant
  `hardware/` scaffold KiCad files (`mini-ereader.kicad_pro`, `.kicad_sch`,
  `.kicad_pcb`, `fp-lib-table`, `sym-lib-table`); the canonical board is now
  the only KiCad project, `ereader.*` at the repo root. `hardware/` keeps the
  electrical source-of-truth (`DESIGN.md`, `BOM.csv`, `gen_netlist_skidl.py`).
  Docs, the runbook, ADR 0002, and CI updated to point at `ereader.*`.
- **Reconciled the ADRs to the canonical Rev C parts.** Added
  [ADR 0006](docs/adr/0006-i2c-managed-power-path.md) (I2C-managed power path:
  BQ25628E charger + TPS62840 buck + MAX17048 gauge, two I2C buses) which
  supersedes ADR 0003, and
  [ADR 0007](docs/adr/0007-lm3630a-frontlight-driver.md) (LM3630A
  single-boost dual-sink frontlight driver) which supersedes ADR 0005. ADRs
  0003 and 0005 are marked Superseded, with their reasoning preserved.
- Documented the navigation input scheme in
  [ADR 0008](docs/adr/0008-navigation-input.md): three side tactile buttons +
  an ALPS SLLB510200 multi-directional lever switch (CW/CCW/press), all on
  RTC-capable wake GPIOs. (New decision; the reference spec had three buttons
  only.)
- Folded the exact SSD1677 external DC-DC values from `hardware/DESIGN.md` §5
  into `ereader-pcb-design.md` §6 (L 47 µH, Si1308EDL FET, MBR0530 ×3,
  2.2 Ω sense + 1 MΩ pulldown, 4.7 µF/1 µF ≥25 V caps, and the VGH/VGL/VSH/
  VSL/VCOM rails) so the canonical spec no longer defers to the vendor zip.
- Removed the committed `ereader-gerbers.zip` build artifact (regenerable with
  `python3 fab.py`; already git-ignored); docs now describe it as a generated
  output, not a shipped file.

### Added
- Hardware design for a 4.26" 800×480 frontlit e-paper reader:
  `hardware/DESIGN.md` (block diagram, power tree, net list, ESP32-S3 pin
  map, frontlight subsystem, PCB guidance, verification status).
- KiCad 8 project scaffold + config: `hardware/mini-ereader.kicad_pro`,
  `.kicad_sch`, `.kicad_pcb`, library tables.
- `hardware/BOM.csv` and `hardware/gen_netlist_skidl.py` (SKiDL netlist
  generator).
- Decisions `docs/adr/0001`–`0005` (MCU, display + frontlight, power,
  native-USB programming, frontlight driver).
- CI: `.github/workflows/kicad.yml` runs `kicad-cli` ERC/DRC and exports a
  schematic PDF + gerbers as build artifacts.

### Changed
- Repository adapted from the Colophon documentation template into the
  Mini E-Reader project: Brief (`README.md`), Log, Runbook, and Changelog
  rewritten; methodology decisions replaced with product decisions.
- Display target corrected from an initial 2.13" assumption to **4.26"
  800×480** after the owner supplied the FL0426-S01C frontlight datasheet;
  a tunable-white frontlight subsystem was added (see ADR 0002 / 0005).
- Display **locked to Good Display GDEY0426T82-FL01C** (controller SSD1677)
  from the panel datasheet: 24-pin EPD FPC pinout and the SSD1677 external
  DC-DC reference circuit captured in DESIGN.md §5; BOM gains J4 + boost
  parts (L2, Q2, D4-D6, R11/R12, ≥25 V caps); the SKiDL generator now emits
  the real EPD block.

### Removed
- Colophon methodology content that no longer applies to this project:
  `docs/faq.md`, `docs/adoption.md`, the methodology ADRs
  (`docs/adr/000{1..5}-*` Colophon versions), the duplicate `hardware/docs/`
  tree, and `LICENSE-TEXT` (the methodology's CC BY 4.0 license). The
  project is MIT (`LICENSE`).

### Notes
- Schematic/PCB are valid scaffolds, not yet captured/routed; ERC/DRC must
  pass in KiCad (now also runnable in CI).
- Two switching subsystems (EPD DC-DC + frontlight boost) must be laid out
  away from the antenna and the battery-sense ADC.
