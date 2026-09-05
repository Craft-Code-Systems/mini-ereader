# Hardware Runbook

How to open, verify, and fabricate the Mini E-Reader board.

## Prerequisites

- **KiCad 8.x** (the project files are KiCad 8 format: schematic
  `version 20231120`, board `version 20240108`).
- KiCad's standard symbol/footprint libraries installed (they ship with
  KiCad). `sym-lib-table` / `fp-lib-table` here are empty and inherit the
  global tables.
- Optional: `pip install skidl` to use `gen_netlist_skidl.py`.

## Open the project

```
kicad hardware/mini-ereader.kicad_pro
```

The schematic and board currently contain a **valid scaffold** (title
block, sheet, board outline, notes) — not the captured design. The design
itself lives in `DESIGN.md`. First thing after opening: confirm both
editors open without file errors. If KiCad reports a version mismatch, let
it upgrade the files in place and re-save.

## Capture the schematic

Two routes:

1. **By hand in Eeschema** (recommended for a reviewable schematic):
   draw each block from `DESIGN.md` §2–§9. Assign footprints from `BOM.csv`.
2. **Bootstrap with SKiDL** (faster to a netlist):
   ```
   cd hardware && python gen_netlist_skidl.py   # -> mini-ereader.net
   ```
   Then in the PCB editor: *File → Import → Netlist…* to pull in parts.
   Note the `TODO` markers in the script — a few lib_ids/pin names depend on
   the exact connector/panel and your library revision.

## Verify (this is the "review" step)

- **ERC** in Eeschema: *Inspect → Electrical Rules Checker*. Resolve every
  error; justify any warning you keep.
- **Footprint assignment**: every symbol → a real footprint (Tools →
  Assign Footprints or CvPcb).
- **DRC** in PCB editor after layout: *Inspect → Design Rules Checker*.
  Zero unrouted, zero clearance errors.
- Update `DESIGN.md` §11 (Verification status) as each item goes green.

## Layout checklist

See `DESIGN.md` §10. Key items: module antenna keep-out at a board edge;
USB D± as a ~90 Ω pair; wide power traces; decoupling close to pins; EPD
pump caps hugging the FPC connector.

## Export fabrication files (JLCPCB / generic)

From the PCB editor once DRC is clean:

- **Gerbers**: *File → Plot* → layers F.Cu, B.Cu, F/B.SilkS, F/B.Mask,
  F/B.Paste, Edge.Cuts → output dir `fab/`. Then *Generate Drill Files*
  (Excellon, PTH+NPTH in one, or per fab spec).
- **BOM**: *Tools → Generate BOM* (or use `BOM.csv` as the master).
- **Placement (CPL)**: *File → Fabrication Outputs → Component Placement*
  for assembly.
- Zip the `fab/` gerbers + drill for the fab house.

> `fab/`, `gerbers/`, `*.zip`, and `*.kicad_prl` are git-ignored — they are
> regenerated outputs / per-user state, not design source.

## Bring-up (first power-on)

1. Inspect solder, check for shorts VBUS/VBAT/VSYS/+3V3 → GND (ohmmeter).
2. Power via USB-C only (no battery). Confirm +3V3 = 3.3 V.
3. Confirm the board enumerates as a USB serial/JTAG device.
4. Flash a blinky / serial test over native USB (hold BOOT + tap RESET if
   the toolchain can't auto-enter the bootloader).
5. Bring up the E-Paper with an SSD1680 driver matched to your panel.
6. Add battery; confirm charging (STAT LED) and battery-sense ADC reading.
