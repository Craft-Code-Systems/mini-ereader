# Runbook

How to work on the Mini E-Reader: open the design, verify it, run CI,
produce fabrication files, and bring up a board.

## Prerequisites

- **KiCad 8.x** with its standard symbol/footprint libraries (they ship
  with KiCad). The project files are KiCad 8 format. The switch footprints
  come from the project-local `ereader.pretty` library (`fp-lib-table`).

## Open the project

```
kicad ereader.kicad_pro
```

This is the single canonical KiCad project (at the repo root). The board
(`ereader.kicad_pcb`) is **placed but not routed**; no native Eeschema
schematic is captured yet. The electrical design itself is
`ereader-connection-list.md` (net-by-net source of truth) +
`ereader-pcb-design.md`, drawn up in `ereader-schematic.md`.
First check: the PCB editor opens without file errors. If KiCad offers to
upgrade the file version, accept and re-save.

## Capture the schematic

Two routes:

1. **By hand in Eeschema** (recommended for a reviewable schematic): draw
   each block from `ereader-schematic.md` / `ereader-connection-list.md`.
   Assign footprints from `ereader-footprints.md` (switches resolve from the
   project `ereader.pretty` library).
2. **Refresh nets from the netlist**: in the PCB editor, *File → Import →
   Netlist…* → `ereader-kicad.net`. This is the connectivity source; it does
   not draw a schematic (see `ereader-schematic.md` for why the design is
   netlist-first and how to get a native `.kicad_sch`).

## Verify (the "review" step)

- **ERC** in Eeschema: *Inspect → Electrical Rules Checker*. Resolve every
  error; justify any warning kept.
- **Footprint assignment**: every symbol → a real footprint.
- **DRC** in the PCB editor after layout: *Inspect → Design Rules Checker*.
  Zero unrouted, zero clearance errors.
- Update the milestone checklist in `/README.md` as items go green.

## CI: KiCad in the cloud

`.github/workflows/kicad.yml` runs on pushes/PRs that touch
`ereader.kicad_pcb`, `ereader-kicad.net`, or the workflow itself (and on demand
via *Run workflow*). In the `kicad/kicad:8.0` container it:

- prints `kicad-cli version`,
- runs **DRC** on the board (`ereader.kicad_pcb`),
- exports **gerbers** + drill, uploaded as the `kicad-outputs`
  build artifact.

While the board is placed but not yet routed, DRC is informational (the
workflow does not hard-fail). Once the schematic/PCB are captured, flip
`--exit-code-violations` handling in the workflow to make CI gate on a
clean ERC/DRC. This is the persistent "KiCad-capable environment"; day-to-
day capture and routing happen locally in KiCad 8.

## Fabrication outputs (JLCPCB / generic)

From the PCB editor once DRC is clean (or download the CI artifact):

- **Gerbers**: *File → Plot* → F.Cu, B.Cu, F/B.SilkS, F/B.Mask, F/B.Paste,
  Edge.Cuts → `fab/`. Then *Generate Drill Files* (Excellon).
- **BOM**: *Tools → Generate BOM*, or use `ereader-footprints.md` as the master picklist.
- **Placement (CPL)**: *File → Fabrication Outputs → Component Placement*.
- Zip the gerbers + drill for the fab house.

`fab/`, `gerbers/`, `*.zip`, and `*.kicad_prl` are git-ignored (outputs /
per-user state, not source).

## Bring-up (first power-on)

1. Inspect solder; ohmmeter-check VBUS/VBAT/VSYS/+3V3 → GND for shorts.
2. Power via USB-C only (no battery). Confirm +3V3 = 3.3 V.
3. Confirm the board enumerates as a USB serial/JTAG device.
4. Flash a blinky/serial test over native USB (if the toolchain can't
   auto-enter the bootloader: bridge the JP5 BOOT pads with a screwdriver tip
   or tweezers and hold, briefly bridge the JP6 RESET pads and release them,
   then release JP5).
5. Bring up the E-Paper with a controller driver matched to the panel.
6. Bring up the frontlight (LM3630A over **I2C1**, addr 0x36 — SDA=GPIO16,
   SCL=GPIO38): drive **FL_HWEN=GPIO21 high** to enable, then set each bank's
   brightness/current over I2C (Bank A = cool, Bank B = warm). Start at a low
   current setting and confirm ≤ 15 mA/channel before going bright. (There is no
   direct-GPIO PWM to the LEDs — GPIO15/16 are LEV_PUSH / I2C1_SDA, not backlight
   PWM; the LM3630A does the boost + per-bank PWM internally.)
7. Add battery; confirm charging (STAT LED) and the battery-sense ADC.

## Adding a decision

When you make a real design choice, copy `docs/adr/0000-template.md` to the
next number and fill it in. Decisions are immutable once accepted — write a
superseding Decision rather than editing an old one.
