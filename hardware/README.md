# Mini E-Reader — Hardware

> The electronics sub-project: a 4.26" 800×480 frontlit e-paper reader —
> ESP32-S3, tunable-white frontlight, USB-C + 1S LiPo. KiCad 8 + design docs.

Project-level orientation, decisions, and the runbook live at the repo root
(`/README.md`, `/docs/`). This folder holds the KiCad project and the
electrical source-of-truth.

## Files

```
DESIGN.md              Electrical source-of-truth: block diagram, power tree,
                       net list, pin map, display + frontlight, PCB guidance,
                       verification status.
BOM.csv                Bill of materials (example MPNs).
gen_netlist_skidl.py   SKiDL generator -> mini-ereader.net.
mini-ereader.kicad_pro Project + config.
mini-ereader.kicad_sch Root schematic (scaffold; capture from DESIGN.md).
mini-ereader.kicad_pcb Board (2-layer, outline + stackup; lay out here).
sym-lib-table          Inherits KiCad global symbol libs.
fp-lib-table           Inherits KiCad global footprint libs.
docs/                  (leftover pointers to /docs — safe to delete)
```

## Key decisions

See [`/docs/adr/`](../docs/adr/):

| # | Decision |
|---|----------|
| [0001](../docs/adr/0001-mcu-esp32-s3.md) | ESP32-S3-WROOM-1 |
| [0002](../docs/adr/0002-display-and-frontlight.md) | 4.26" 800×480 E-Paper + laminated frontlight |
| [0003](../docs/adr/0003-power-architecture.md) | USB-C + 1S LiPo, load-share, 3.3 V LDO |
| [0004](../docs/adr/0004-native-usb-programming.md) | Native-USB programming |
| [0005](../docs/adr/0005-frontlight-driver.md) | Dual boost constant-current frontlight driver |

## Getting started

```
# Open in KiCad 8
kicad mini-ereader.kicad_pro

# Or bootstrap a netlist (needs `pip install skidl` + KiCad libs)
python gen_netlist_skidl.py
```

Capture, verification, CI, and fabrication steps are in
[`/docs/runbook.md`](../docs/runbook.md).

## Caveats (read before ordering parts)

- **Display + frontlight locked** to Good Display GDEY0426T82-FL01C
  (SSD1677, 24-pin EPD FPC + 6-pin frontlight FPC); pinout + SSD1677
  external DC-DC captured in `DESIGN.md` §5.
- **The KiCad schematic/PCB are scaffolds**, not a verified, routed design.
  Capture + run ERC/DRC in KiCad (or via CI) before trusting them.
- **Verify the SKiDL EPD negative charge-pump (D4/D5) orientation** against
  the datasheet reference circuit when you generate the netlist.
- **Example MPNs in `BOM.csv`** need a stock/footprint check for your fab.
