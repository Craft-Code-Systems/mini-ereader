# Mini E-Reader

> A pocket, frontlit e-paper reader you can build and hack.
> ESP32-S3 + 4.26" E-Paper (800×480) + tunable-white frontlight,
> USB-C charged, LiPo powered.

This repository holds the open hardware (KiCad) and project documentation
for a small e-reader. Docs follow the [Colophon](https://usecolophon.dev)
method: a Brief (this file), Decisions (`docs/adr/`), a Log
(`docs/research-log.md`), a Runbook (`docs/runbook.md`), and a Changelog.

> **One KiCad project, one source of truth.** The board lives at the repo root:
> **`ereader.kicad_pcb`**, with the electrical design in the `ereader-*.md`
> docs — `ereader-connection-list.md` (net-by-net source of truth),
> `ereader-schematic.md` (subsystem schematic), `ereader-pcb-design.md`
> (full spec), `ereader-footprints.md` (BOM/footprint picklist) — and the
> `ereader-kicad.net` netlist. (Rev C — placed, planed, stitched, DRC-ruled;
> routing pending.) An earlier, simpler `hardware/` *reference spec* was
> removed once `ereader.*` superseded it; the historical comparison is in
> `docs/research-log.md`. The Rev C parts are reconciled into the ADRs:
> [0006](./docs/adr/0006-i2c-managed-power-path.md) (power) supersedes 0003
> and [0007](./docs/adr/0007-lm3630a-frontlight-driver.md) (frontlight)
> supersedes 0005.

## Why

Commercial e-readers are closed and hard to modify. This is a compact,
documented reference design — cheap parts, two-layer board, hand- or
JLCPCB-assemblable — for reading plain text / EPUB on a persistent,
sunlight-readable display with an adjustable frontlight and Wi-Fi sync.
A buildable learning platform, not a product.

## Scope & non-scope

**In scope**
- Schematic + 2-layer PCB: MCU, 4.26" SPI E-Paper, tunable frontlight,
  power (USB-C + 1S LiPo), buttons, optional microSD.
- A bill of materials and fabrication-ready outputs.
- Automated ERC/DRC + gerber export in CI.

**Out of scope (for now)**
- Enclosure / industrial design (CAD).
- Firmware (tracked separately once hardware is proven).
- Touch input, audio, multi-panel support.
- Certification / mass production.

## Success criteria

1. Schematic captured with **ERC clean** in KiCad 8.
2. PCB placed + routed with **DRC clean**; gerbers export in CI.
3. A built prototype: powers from USB and battery, charges, enumerates
   over native USB, refreshes the E-Paper, and lights the frontlight with
   independent brightness + colour-temperature control.

## Capabilities

- Render text/EPUB to a 4.26" 800×480 monochrome E-Paper panel over SPI.
- Tunable-white frontlight: independent cold/warm channels, PWM brightness
  and colour-temperature mixing.
- Wi-Fi/BLE (ESP32-S3) for fetching and syncing books.
- Battery power (1S LiPo) with USB-C charging and USB-priority power path.
- Battery state-of-charge and charge-status telemetry.
- Three navigation buttons; BOOT/RESET jumper pads (screwdriver-shortable) for flashing.
- Optional microSD for local library storage.

## Non-functional baseline

- **Power:** deep-sleep with the page retained in the µA range; runs from a
  single LiPo; charges over USB-C.
- **Cost/build:** two-layer FR-4, common parts, low-cost assembly.
- **Serviceability:** test points on key rails and buses; native-USB
  programming with no external bridge.
- **Docs:** every significant decision captured as an ADR before it is
  built.

## Stack

- **MCU:** ESP32-S3-WROOM-1 (Wi-Fi/BLE, PSRAM, native USB).
- **Display:** Good Display **GDEY0426T82-FL01C** — 4.26" 800×480 E-Paper,
  controller **SSD1677**, 4-wire SPI, 24-pin FPC, with an integrated dual
  frontlight (5+5 series white LEDs, VF≤15 V, IF≤15 mA).
- **Power:** MCP73831 charger, discrete USB-priority load-share,
  AP2112K-3.3 LDO; 2× TPS61165 frontlight boost drivers.
- **EDA:** KiCad 8. **CI:** GitHub Actions (`kicad-cli` ERC/DRC/export).

## Status & milestones

**v0.1 — design captured; reviewable schematic in `ereader-schematic.md`; native Eeschema `.kicad_sch` + routed PCB not yet drawn in KiCad.**

- [x] Architecture, power tree, net list, pin map — `ereader-pcb-design.md` + `ereader-connection-list.md`
- [x] Decisions recorded — `docs/adr/0001`–`0005`
- [x] KiCad board `ereader.*` placed + config that opens cleanly
- [x] BOM + SKiDL netlist generator
- [x] CI: `kicad-cli` ERC/DRC/export workflow
- [~] Schematic — reviewable subsystem diagrams in `ereader-schematic.md`; native Eeschema capture + **ERC clean** pending
- [ ] PCB placed, routed + **DRC clean**
- [ ] Prototype built + brought up

Live verification state: the milestone checklist above.

## Key decisions

| # | Decision |
|---|----------|
| [0001](./docs/adr/0001-mcu-esp32-s3.md) | ESP32-S3-WROOM-1 as the MCU |
| [0002](./docs/adr/0002-display-and-frontlight.md) | 4.26" 800×480 E-Paper + laminated tunable frontlight |
| [0003](./docs/adr/0003-power-architecture.md) | USB-C + 1S LiPo, load-share, 3.3 V LDO *(superseded by 0006)* |
| [0004](./docs/adr/0004-native-usb-programming.md) | Native-USB programming (no UART bridge) |
| [0005](./docs/adr/0005-frontlight-driver.md) | Dual boost constant-current frontlight driver *(superseded by 0007)* |
| [0006](./docs/adr/0006-i2c-managed-power-path.md) | I2C-managed power path: BQ25628E + TPS62840 + MAX17048 |
| [0007](./docs/adr/0007-lm3630a-frontlight-driver.md) | LM3630A single-boost dual-sink frontlight driver |
| [0008](./docs/adr/0008-navigation-input.md) | Navigation input: 3 side buttons + ALPS SLLB510200 lever switch |

## Getting started

```
# Open the board in KiCad 8
kicad ereader.kicad_pro

# Read the electrical design (source of truth)
less ereader-connection-list.md
```

See [`docs/runbook.md`](./docs/runbook.md) for capture, verification,
CI, fabrication, and bring-up. Component-level detail lives in
[`ereader-pcb-design.md`](./ereader-pcb-design.md) and
[`ereader-schematic.md`](./ereader-schematic.md).

## Repository layout

```
README.md              This Brief
CHANGELOG.md           Project history
ereader.*              The KiCad board (project, PCB, netlist, cmp)
ereader-*.md           Electrical source of truth: connection-list, schematic, pcb-design, footprints, README
ereader.pretty/        Project footprints (side tactile, ALPS SLLB5 lever)
ereader.3dshapes/      Simple 3D bodies for the project footprints
fp-lib-table           Registers the ereader.pretty footprint library
fab.py                 Gerber/drill export helper
docs/
  adr/                 Decisions (0001–0008 + template)
  research-log.md      Dated exploration notes
  runbook.md           Capture / verify / fabricate / bring-up
templates/             Colophon document templates (for ongoing use)
.github/workflows/     CI (KiCad ERC/DRC/export)
```

## License

[MIT](./LICENSE) for code, hardware, and documentation. *(This repository
started from the [Colophon](https://usecolophon.dev) template; the doc
method is reused under MIT here — the template's separate CC BY methodology
license has been removed.)*
