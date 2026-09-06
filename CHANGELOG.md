# Changelog

All notable changes to the Mini E-Reader project. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); dates are ISO-8601.

## [Unreleased]

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
