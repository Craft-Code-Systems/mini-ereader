# Changelog

All notable changes to the Mini E-Reader project. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); dates are ISO-8601.

## [Unreleased]

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

### Removed
- Colophon methodology content that no longer applies to this project:
  `docs/faq.md`, `docs/adoption.md`, the methodology ADRs
  (`docs/adr/000{1..5}-*` Colophon versions), the duplicate `hardware/docs/`
  tree, and `LICENSE-TEXT` (the methodology's CC BY 4.0 license). The
  project is MIT (`LICENSE`).

### Notes
- Schematic/PCB are valid scaffolds, not yet captured/routed; ERC/DRC must
  pass in KiCad (now also runnable in CI).
- The EPD panel's own datasheet is still needed to lock the display FPC
  pinout and controller.
