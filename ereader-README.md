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
| `ereader-footprints.md` | footprint picklist + ✓/⚑ status |
| `ereader-pcb-design.md` | full design spec (power, pinmap, compliance, layout) |

## Honest status — what this IS / IS NOT
**IS:** an openable project; every part positioned in a real floorplan; board outline; keep-out + magnet fiducials; ratsnest for the module, all passives, and most of USB-C.
**IS NOT:** routed, not a Gerber, not manufacturing-ready.

## Two manual steps remain (unavoidable — this is the engineering)
1. **Fix the flagged parts + name-only pins** (~29% of endpoints unconnected by design, listed below):
   - **Placeholder footprints (real land = wrong)** → replace with exact per datasheet: `U2` BQ25628E, `U3` MAX17048, `U4` LM3630A, `U5` TPS62840, `SW4` SLLB510200. Pull from SnapEDA / Ultra-Librarian.
   - **Name-only pins** don't auto-match numeric pads → assign in symbol or connect while routing: `J2` (EPD, 8 pins → map to GDEY0426T82 FPC numbers), `J4` (microSD, 6), `SW4` (CW/CCW/PUSH/COM→1-4), `U2-U5`/`U6` (IC function names→pads).
2. **Place-tune → route → DRC → Gerbers.** Follow §11 layout rules in the design spec (antenna keep-out, FL-boost + charger loops tight, USB 90Ω diff, GND plane).

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
  - `Power` 0.40mm track / 0.20 clearance / 0.8-0.4 via → GND, +VBUS, +SYS, +VBAT, +3V3, FL_OUT, FL_SW, CHG_SW, BUCK_SW.
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
1. Swap the 5 placeholder footprints (U2-U5, SW4) for exact parts; remap the name-only pins (EPD/microSD/SW4/ICs) so their nets connect.
2. **Route** every ratsnest line (Route → Route Tracks). Honor §11 of the design spec: antenna keep-out, tight FL-boost + charger switch loops, USB 90Ω diff pair, star-ground the analog returns.
3. Run **DRC** → zero unconnected, zero violations.
4. `python3 fab.py` (or Pcbnew → Plot) → upload `ereader-gerbers.zip` to JLCPCB.

**Why I don't autoroute it for you:** this is an RF (2.4GHz module) + USB + switching-converter board. An autorouter connects nets but wrecks the antenna keep-out, switch-node loops, and diff-pair impedance — i.e. exactly the FCC/CE compliance you specified. Routing is the engineering, and it's yours (or a layout contractor's). I can export a **Specctra DSN** for freerouting if you accept it won't be compliance-ready.
