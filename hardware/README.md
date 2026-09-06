# Mini E-Reader — Hardware

> The electronics sub-project: a 4.26" 800×480 frontlit e-paper reader —
> ESP32-S3, tunable-white frontlight, USB-C + 1S LiPo. KiCad 8 + design docs.

Project-level orientation, decisions, and the runbook live at the repo root
(`/README.md`, `/docs/`). The **KiCad board is at the repo root**
(`/ereader.kicad_pro`, the single canonical project). This folder holds the
electrical source-of-truth docs and the netlist generator.

## Files

```
DESIGN.md              Electrical source-of-truth: block diagram, power tree,
                       net list, pin map, display + frontlight, PCB guidance,
                       verification status.
BOM.csv                Bill of materials (example MPNs).
gen_netlist_skidl.py   SKiDL generator -> a netlist you can import in KiCad.
```

> The KiCad project that used to live here (`mini-ereader.*`) was an empty
> scaffold and has been removed. Open the real board at the repo root:
> `/ereader.kicad_pro`. Where this folder's docs describe simpler parts than
> the root board (see `/docs/research-log.md`), `ereader.*` is authoritative.

## Key decisions

See [`/docs/adr/`](../docs/adr/):

| # | Decision |
|---|----------|
| [0001](../docs/adr/0001-mcu-esp32-s3.md) | ESP32-S3-WROOM-1 |
| [0002](../docs/adr/0002-display-and-frontlight.md) | 4.26" 800×480 E-Paper + laminated frontlight |
| [0003](../docs/adr/0003-power-architecture.md) | USB-C + 1S LiPo, load-share, 3.3 V LDO *(superseded by 0006)* |
| [0004](../docs/adr/0004-native-usb-programming.md) | Native-USB programming |
| [0005](../docs/adr/0005-frontlight-driver.md) | Dual boost constant-current frontlight driver *(superseded by 0007)* |
| [0006](../docs/adr/0006-i2c-managed-power-path.md) | I2C-managed power path: BQ25628E + TPS62840 + MAX17048 |
| [0007](../docs/adr/0007-lm3630a-frontlight-driver.md) | LM3630A single-boost dual-sink frontlight driver |

## Getting started

```
# Open the board in KiCad 8 (it lives at the repo root)
kicad ../ereader.kicad_pro

# Or bootstrap a netlist (needs `pip install skidl` + KiCad libs)
python gen_netlist_skidl.py
```

Capture, verification, CI, and fabrication steps are in
[`/docs/runbook.md`](../docs/runbook.md).

## Caveats (read before ordering parts)

- **Display + frontlight locked** to Good Display GDEY0426T82-FL01C
  (SSD1677, 24-pin EPD FPC + 6-pin frontlight FPC); pinout + SSD1677
  external DC-DC captured in `DESIGN.md` §5.
- **The root board (`/ereader.*`) is placed but not routed**, and its
  schematic is not yet captured — not a verified, routed design. Capture +
  run ERC/DRC in KiCad (or via CI) before trusting it.
- **Verify the SKiDL EPD negative charge-pump (D4/D5) orientation** against
  the datasheet reference circuit when you generate the netlist.
- **Example MPNs in `BOM.csv`** need a stock/footprint check for your fab.
