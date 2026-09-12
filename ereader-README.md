# Mini E-Reader — KiCad Package (README)

Open **`ereader.kicad_pro`** in KiCad 7/8 → open the **PCB Editor** (Pcbnew). Press `Home` to zoom-to-fit.

## What's here
| File | What |
|------|------|
| `ereader.kicad_pro` | project |
| `ereader.kicad_pcb` | **board: all 49 parts placed by subsystem + outline (66×115mm) + antenna keep-out silk + magnet markers + 71% of nets wired (ratsnest)** |
| `ereader-kicad.net` | netlist (import to refresh nets) |
| `ereader.cmp` | ref↔footprint map |
| `ereader-connection-list.md` | master net-by-net (source of truth) |
| `ereader-schematic.md` | schematic (subsystem Mermaid diagrams; renders on GitHub) |
| `ereader-footprints.md` | footprint picklist + ✓/⚑ status |
| `ereader.pretty/` + `ereader.3dshapes/` | project footprints (side tactile, SLLB5 lever, bare jumper pad) + simple 3D bodies for the switches |
| `ereader-pcb-design.md` | full design spec (power, pinmap, compliance, layout) |

## Honest status — what this IS / IS NOT
**IS:** an openable project; every part positioned in a real floorplan; board outline; keep-out + magnet fiducials; ratsnest for the module, all passives, and most of USB-C; a reviewable schematic (`ereader-schematic.md`).
**IS NOT:** routed, not a Gerber, not manufacturing-ready, **not** a native Eeschema `.kicad_sch` — the design is netlist-first (see `ereader-schematic.md` for why, and how to draw one).

## Manual steps remain (unavoidable — this is the engineering)

> **First:** in the PCB editor, `File → Import → Netlist… → ereader-kicad.net`
> (match **by Reference**, leave **"Delete extra footprints" unchecked** so the
> FID/H board-only parts survive, then **Update PCB**).
> Rev C4 added the **EPD external DC-DC block** (LE/QE/DE1-3/RE1-2/CE1-9) plus
> local decoupling (CGA/CGB/C4I). These are in the netlist/`.cmp` but **not yet
> placed on the .kicad_pcb** — the re-import brings them in as unplaced parts.
>
> ⚠ **Not** *Update PCB from Schematic* (F8) and **do not open the Schematic
> Editor** — there is no `.kicad_sch`, so those error with "The schematic for
> this board cannot be found." This project is netlist-first; import the `.net`.

1. **Fix the flagged parts + name-only pins** (~29% of endpoints unconnected by design, listed below):
   - **Placeholder footprints (real land = wrong)** → replace with exact per datasheet: `U2` BQ25628E (**18-pin WQFN 2.5×3.0mm RYK** — current placeholder is a wrong 24-pin QFN), `U3` MAX17048 (µDFN-8 2×2), `U4` LM3630A (DSBGA-12 0.4mm), `U5` TPS62840 (**VSON-HR/DLC 8-pin 2×2mm** — current placeholder is oversized 3×2). Pull from SnapEDA / Ultra-Librarian; see `ereader-footprints.md`. (`SW1-4` use the project-local `ereader.pretty` lands — still DRC vs the ordered MPN. `JP5`/`JP6` bare jumper pads — check pad spacing vs fab minimum.)
   - **Name-only pins** don't auto-match numeric pads → assign in symbol or connect while routing:
     - `J2` (EPD FPC): logic + the new support rails (GDR, RESE, VGH, VGL, VSH1, VSH2, VSL, VCOM, VCI, BS1) → **map each to the GDEY0426T82 24-pin FPC number from the panel datasheet.** This is the one genuinely datasheet-blocked remap.
     - `J4` (microSD): the netlist uses the DM3AT pad names (CLK/CMD/DAT0/DAT3/VDD/VSS) so it should map on import — just add DAT1/DAT2 pull-ups + wire the card-detect/shield pads.
     - `U2-U5`/`U6`: IC function-name pins → pads of the real symbol.
     (`SW4` resolved — pads named CW/CCW/PUSH/COM.)
   - **EPD DC-DC interconnect** → the diode/charge-pump wiring + orientation are a functional placeholder; **copy 1:1 from the Good Display GDEY0426T82-FL01C reference schematic** (see `ereader-connection-list.md` → *EPD external DC-DC*).
2. **Place-tune → route → DRC → Gerbers.** Follow §11 layout rules in the design spec (antenna keep-out, FL-boost + charger loops tight, EPD boost loop tight, USB 90Ω diff, GND plane).

## EasyEDA instead?
EasyEDA **Pro** → File → Import → *KiCad* accepts `ereader.kicad_pcb`. No separate EasyEDA project provided (KiCad is the cleaner base here).

## Notes baked into the board
- Antenna keep-out = top silk band + label. No copper any layer there; keep magnets ≥10-15mm away.
- Magnet fiducials = 2 silk crosshair circles (align the printed shell magnets; magnets NOT on PCB).
- BQ25628E `CE` low = charge enabled → `R7`→GND = charge-on default; GPIO14 drives high to hard-disable.

## Rev 2 — route-ready additions
- **4-layer stackup** (SIG / GND / PWR / SIG).
- **GND planes**: filled zones on In1.Cu (plane), F.Cu, B.Cu — poured everywhere except the antenna keep-out band. Re-fill with `B` after you move parts.
- **Net classes** (Board Setup → Net Classes):
  - `Power` 0.40mm track / 0.20 clearance / 0.8-0.4 via → GND, +VBUS, +SYS, +VBAT, +3V3, FL_OUT, FL_SW, CHG_SW, BUCK_SW, **EPD_SW, EPD_VGH, EPD_VGL, EPD_VSH1, EPD_VSH2, EPD_VSL, EPD_PREVGL** (EPD boost node + ±20V/±15V rails — keep the EPD_SW loop tight, and give the ±20V rails clearance for their ~40V swing).
  - `USB` 0.25mm, diff-pair 0.20/0.13 → USB_DP, USB_DM (tune to 90Ω against your real stackup).
  - `Default` 0.20/0.15 → everything else.
- **`ereader-placement.svg`** = subsystem floorplan to eyeball before you commit.

## Rev 3 — mechanical + fab pipeline
- **Mounting holes** H1-H4 (M2, 2.2mm) at corners — relocate to match your shell.
- **Fiducials** FID1-3 (bottom edge) for assembly.
- **GND via stitching** — 58 vias, ~6mm pitch perimeter ring, tied to GND, knitting the planes.
- **DRC ruleset (JLCPCB 4-layer)** baked into `ereader.kicad_pro`: min track 0.15mm, clearance 0.15mm, via 0.45/0.30, edge clearance 0.30, annular ≥0.13. Track/via/diff-pair presets loaded.
- **`fab.py`** — one command to emit Gerbers + Excellon drill + zip:  `python3 fab.py`  → `ereader-gerbers.zip` (11 layers + PTH/NPTH). The zip is a build artifact (git-ignored) — regenerate it, don't commit it.

## ⛔ The one gate that remains: ROUTING
The board is **placed, planed, stitched, and DRC-ruled — but NOT routed** (no signal traces).
Gerbers from `fab.py` at this stage = pours + pads + vias, **no traces between pads → not manufacturable yet.** Fab them and you get a dead board.

To finish:
1. Swap the 4 placeholder footprints (U2-U5) for exact parts; remap the name-only pins (EPD/microSD/ICs) so their nets connect. (SW1-6 lands are in `ereader.pretty` — still DRC vs the ordered switch datasheets.)
2. **Route** every ratsnest line (Route → Route Tracks). Honor §11 of the design spec: antenna keep-out, tight FL-boost + charger switch loops, USB 90Ω diff pair, star-ground the analog returns.
3. Run **DRC** → zero unconnected, zero violations.
4. `python3 fab.py` (or Pcbnew → Plot) → upload `ereader-gerbers.zip` to JLCPCB.

**Why I don't autoroute it for you:** this is an RF (2.4GHz module) + USB + switching-converter board. An autorouter connects nets but wrecks the antenna keep-out, switch-node loops, and diff-pair impedance — i.e. exactly the FCC/CE compliance you specified. Routing is the engineering, and it's yours (or a layout contractor's). I can export a **Specctra DSN** for freerouting if you accept it won't be compliance-ready.
