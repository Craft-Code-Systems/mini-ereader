# Mini E-Reader — Hardware

> A pocket e-reader: ESP32-S3 driving a small SPI E-Paper panel, USB-C
> charged, LiPo powered. This folder is the electronics sub-project
> (KiCad + design docs), documented Colophon-style.

## Why

Small, cheap, hackable e-reader hardware for reading plain text / EPUB with
a persistent, sunlight-readable display and Wi-Fi book sync — a buildable
reference design, not a product.

## Scope

- **In:** schematic + 2-layer PCB for MCU, E-Paper, power (USB-C + 1S LiPo),
  buttons, optional microSD; a BOM; fabrication-ready outputs.
- **Out (for now):** enclosure/CAD, firmware, multi-panel support, mass
  production / compliance testing.

## Status & milestones

**v0.1 — design captured, not yet drawn in KiCad.**

- [x] Architecture, power tree, net list, pin map — `DESIGN.md`
- [x] KiCad 8 project scaffold + config that opens cleanly
- [x] BOM with example part numbers — `BOM.csv`
- [x] SKiDL netlist generator — `gen_netlist_skidl.py`
- [ ] Schematic captured + **ERC clean** in KiCad
- [ ] PCB placed, routed + **DRC clean**
- [ ] Fabrication outputs (gerbers/drill/CPL)
- [ ] Prototype built + brought up

Live verification state: `DESIGN.md` §11.

## Key decisions

| # | Decision | Why (one line) |
|---|----------|----------------|
| [0001](./docs/adr/0001-mcu-esp32-s3.md) | ESP32-S3-WROOM-1 | Wi-Fi + PSRAM + native USB, big ecosystem |
| [0002](./docs/adr/0002-display-and-storage.md) | SPI E-Paper (SSD1680) + optional microSD | Cheap, low-pin, on-chip charge pump |
| [0003](./docs/adr/0003-power-architecture.md) | USB-C + 1S LiPo, load-share, 3.3 V LDO | Smallest sane BOM; upgrade paths noted |
| [0004](./docs/adr/0004-native-usb-programming.md) | Native-USB programming | Drops the UART bridge + auto-reset circuit |

## Layout of this folder

```
hardware/
  README.md              This Brief
  DESIGN.md              Electrical source-of-truth (block diagram, power,
                         net list, pin map, EPD notes, PCB guidance)
  BOM.csv                Bill of materials (example MPNs)
  gen_netlist_skidl.py   SKiDL generator -> mini-ereader.net
  mini-ereader.kicad_pro Project + config
  mini-ereader.kicad_sch Root schematic (scaffold; capture from DESIGN.md)
  mini-ereader.kicad_pcb Board (2-layer, outline + stackup; lay out here)
  sym-lib-table          Inherits KiCad global symbol libs
  fp-lib-table           Inherits KiCad global footprint libs
  docs/
    runbook.md           Open / verify / fabricate / bring-up
    adr/                 Decisions 0001–0004 (+ template)
```

## Getting started

```
# Open in KiCad 8
kicad hardware/mini-ereader.kicad_pro

# Or bootstrap a netlist (needs `pip install skidl` + KiCad libs)
cd hardware && python gen_netlist_skidl.py
```

See [`docs/runbook.md`](./docs/runbook.md) for verification and fabrication.

## Caveats (read before ordering parts)

- **E-Paper FPC pinout is panel-specific.** `DESIGN.md` §5 uses a reference
  panel; confirm every FPC pin against *your* panel's datasheet.
- **The KiCad schematic/PCB are scaffolds**, not a verified, routed design —
  they were prepared without a KiCad instance to run ERC/DRC. Capture and
  verify in KiCad before trusting them.
- **Example MPNs in `BOM.csv`** need a stock/footprint check for your fab.
