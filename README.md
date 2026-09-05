# Mini E-Reader

> A pocket, frontlit e-paper reader you can build and hack.
> ESP32-S3 + 4.26" E-Paper (800×480) + tunable-white frontlight,
> USB-C charged, LiPo powered.

This repository holds the open hardware (KiCad) and project documentation
for a small e-reader. Docs follow the [Colophon](https://usecolophon.dev)
method: a Brief (this file), Decisions (`docs/adr/`), a Log
(`docs/research-log.md`), a Runbook (`docs/runbook.md`), and a Changelog.

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
- Three navigation buttons; BOOT/RESET for flashing.
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
- **Display:** 4.26" 800×480 E-Paper (Good Display GDEQ0426T82 class),
  SSD-family controller, 4-wire SPI. Frontlight: Good Display
  FL0426-S01C (5+5 series white LEDs, VF≤15 V, IF≤15 mA).
- **Power:** MCP73831 charger, discrete USB-priority load-share,
  AP2112K-3.3 LDO; 2× TPS61165 frontlight boost drivers.
- **EDA:** KiCad 8. **CI:** GitHub Actions (`kicad-cli` ERC/DRC/export).

## Status & milestones

**v0.1 — design captured; schematic/PCB not yet drawn in KiCad.**

- [x] Architecture, power tree, net list, pin map — `hardware/DESIGN.md`
- [x] Decisions recorded — `docs/adr/0001`–`0005`
- [x] KiCad 8 project scaffold + config that opens cleanly
- [x] BOM + SKiDL netlist generator
- [x] CI: `kicad-cli` ERC/DRC/export workflow
- [ ] Schematic captured + **ERC clean**
- [ ] PCB placed, routed + **DRC clean**
- [ ] Prototype built + brought up

Live verification state: `hardware/DESIGN.md` §"Verification status".

## Key decisions

| # | Decision |
|---|----------|
| [0001](./docs/adr/0001-mcu-esp32-s3.md) | ESP32-S3-WROOM-1 as the MCU |
| [0002](./docs/adr/0002-display-and-frontlight.md) | 4.26" 800×480 E-Paper + laminated tunable frontlight |
| [0003](./docs/adr/0003-power-architecture.md) | USB-C + 1S LiPo, load-share, 3.3 V LDO |
| [0004](./docs/adr/0004-native-usb-programming.md) | Native-USB programming (no UART bridge) |
| [0005](./docs/adr/0005-frontlight-driver.md) | Dual boost constant-current frontlight driver |

## Getting started

```
# Open the hardware in KiCad 8
kicad hardware/mini-ereader.kicad_pro

# Read the electrical design (source of truth)
less hardware/DESIGN.md
```

See [`docs/runbook.md`](./docs/runbook.md) for capture, verification,
CI, fabrication, and bring-up. Component-level detail lives in
[`hardware/DESIGN.md`](./hardware/DESIGN.md).

## Repository layout

```
README.md              This Brief
CHANGELOG.md           Project history
docs/
  adr/                 Decisions (0001–0005 + template)
  research-log.md      Dated exploration notes
  runbook.md           Capture / verify / fabricate / bring-up
hardware/              KiCad project, DESIGN.md, BOM, netlist generator
templates/             Colophon document templates (for ongoing use)
.github/workflows/     CI (KiCad ERC/DRC/export)
```

## License

Code/hardware under [MIT](./LICENSE) unless noted. *(The repository began
as the Colophon template; `LICENSE-TEXT` is the methodology's CC BY 4.0
license and applies only to any retained Colophon prose — adjust licensing
to suit this project.)*
