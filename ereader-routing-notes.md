# Routing notes — pad escapes, and why the autorouter kept stalling

State of the board as of the `claude/pad-escape-fanout` branch. Read this
before touching the routing again.

---

## 1. The problem

Freerouting plateaued around **51 unconnected nets** and left **In2.Cu
completely unused**. Going from 2 layers to 4 changed nothing.

The cause was not the layer count. On this board the fine-pitch parts —
`J1` (USB-C), `J2` (24-pin 0.5 mm FPC), `U2` (0.4 mm-pitch WQFN-HR18),
`U3`, `U4` (0.4 mm DSBGA), `U5`, `J3` — have pads with **no room beside them
for a 0.8 mm Power-class via**. Measured on a board stripped to bare pads,
the largest via that fits next to the worst offenders:

| pad | largest via that fits |
|---|---|
| U2.15 | 0.501 mm |
| U5.3 / U5.6 / U3.6 | 0.452 mm |
| U4.B3 / U4.C1 | 0.406 mm |
| U4.C2 | 0.328 mm |

The manufacturable minimum here is 0.56 mm (0.3 drill + 2 × 0.13 annular).
So these pads could not take a via with *zero* routing on the board.

**A pad that cannot reach a via cannot reach an inner layer.** That is why
In2.Cu went unused and why the router gave up on the congested nets. It was
never going to solve this by trying harder.

## 2. The fix

Traces fit where vias don't: a 0.8 mm via needs 0.4 mm of radius, a 0.2 mm
trace needs 0.1 mm. So each trapped pad gets a **necked-down escape stub**
running out along **the pad's own axis** to a via in open copper.

Running the stub dead down the pad centreline is what makes it fit — a 5°
tilt eats the 0.30 mm of lateral room a 0.4 mm-pitch land gives you. The
first solver version searched free angles and failed on U2 by 2 µm.

**54 escapes: 58 segments + 54 vias.** Widths: 27 × 0.30, 11 × 0.20,
6 × 0.18, 5 × 0.40, 4 × 0.25, 1 × 0.15 (board minimum is 0.15).
Shapes: 49 straight down a pad axis, 4 L-shaped, 1 free-angle.

Every escape clears every other pad, every other escape, the board edge and
the U1 antenna keep-out at **full netclass clearance**, re-verified by an
independent re-parse of the written board file (`verify.py` logic — it
re-derives clearances from the netclass table rather than trusting the
solver's own bookkeeping).

## 3. The one rule change

`EPD_HV` netclass clearance **0.30 → 0.20 mm** (`set_epdhv.py`).

Not negotiable and not cosmetic: the GDEY0426T82 FPC land spaces
EPD_VGH / EPD_VGL / EPD_VSL / EPD_VSH1 / EPD_VSH2 **0.2 mm apart itself**,
so a 0.30 mm rule was never achievable at the connector — nothing the PCB
does can beat the panel vendor's own pad pitch. At 0.30 mm only a 0.10 mm
trace fits, and the board minimum track width is 0.15 mm, so **no escape
geometry can satisfy it**.

IPC-2221 table B4 (external conductors under permanent polymer coating,
i.e. solder mask) allows 0.13 mm at 31–50 V, so 0.20 mm keeps margin for the
±20 V rails. Table B1's 0.6 mm figure is for *bare* copper; these runs are
masked.

Left at 0.30, DRC reports 10 clearance errors, all of them the EPD rail
escapes at J2. **No other DRC rule was added or relaxed anywhere.**

## 4. Pipeline

| Step | Interpreter | Command |
|---|---|---|
| Netclass change | plain `python3`, **KiCad closed** | `python3 set_epdhv.py` |
| Strip + lay escapes | plain `python3` | `python3 fanout.py` |
| Refill + DRC | **KiCad GUI** | open, `B`, Inspect → DRC |
| Lock + export DSN | **KiCad's Python**, board closed | `python3 export_dsn.py` |
| Verify fixed type | plain `python3` | `python3 protect_dsn.py` |
| Route | `java` | `xvfb-run java -jar <path>/freerouting.jar -de ereader.dsn -do ereader.ses -mp 100` |
| Import result | **KiCad's Python** | `python3 import_ses.py` |
| Docs | plain `python3` | `python3 docs_4layer.py` |

Only `export_dsn.py` and `import_ses.py` need `pcbnew`. Freerouting needs a
**headful** JDK — a headless-only JVM throws `HeadlessException` even under
`xvfb-run` (`sudo dnf install -y java-25-openjdk`).

Run the route **on its own line** and check `ereader.ses` is newer than
`ereader.dsn` before importing. See §7.

## 5. Board facts worth not re-deriving

- 66 × 115 mm, 81 footprints, **333 copper pads**. A naive pad count gives
  342 — nine of those are `(layers "F.Paste")` stencil apertures on U1's
  thermal land, which are **not copper** and impose no clearance.
- Stack: `F.Cu` signal / `In1.Cu` **GND plane** / `In2.Cu` signal / `B.Cu`
  signal. Three GND zones: `GND_F.Cu`, `GND_In1.Cu`, `GND_B.Cu`.
- Every part is top-side. No B.Cu-only pads, so all escape stubs are F.Cu.
- Netclasses (`ereader.kicad_pro`), track / clearance / via Ø / drill:
  - `Default` 0.20 / 0.15 / 0.6 / 0.3
  - `Power` 0.40 / 0.20 / 0.8 / 0.4 — **GND is in Power**
  - `USB` 0.25 / 0.15 / 0.6 / 0.3
  - `EPD_HV` 0.30 / **0.20** / 0.8 / 0.4
  - `EPD_PREVGL` is **not** assigned to EPD_HV — it resolves to `Default`.
- Board constraints: min track 0.15, min clearance 0.15, hole-to-hole 0.25,
  hole clearance 0.25, edge clearance 0.30, annular ≥ 0.13.
- **Annular is checked against the netclass drill, not the via's own drill.**
  A 0.6/0.3 via on a Power net fails: KiCad uses drill 0.4 and computes
  (0.6−0.4)/2 = 0.100 < 0.130. Power/EPD_HV vias must be 0.8/0.4.
- `ereader.kicad_dru` carries a same-footprint clearance exception
  (`A.Parent == B.Parent` → 0.15 mm) for vendor land geometry. It applies to
  **pad-to-pad only** — a track's parent is the board, so escape stubs get
  no relief from it and were computed at full netclass clearance.

## 6. Known limitations

- **3 pads have no escape**: `U2.16` (CHG_SW), `U2.9` (+SYS), `U5.7`
  (BUCK_SW). Both parts are placeholder lands already flagged for
  replacement — U2 needs TI's real WQFN-HR18 **RYK** land, U5 the real
  **VSON-HR/DLC**. Recompute these once the real lands are in.
- **U2's placeholder land is off-grid by ~1 µm.** Pad centreline to
  neighbour measures 0.299999 mm where a 0.20 mm stub at 0.20 mm clearance
  needs 0.300000. KiCad works in nanometres, so that is a genuine violation,
  not float noise. It is why U2's escapes neck to 0.18 mm, and another
  symptom of a land that must be replaced before fab.
- **The escape table is keyed by `ref.num`, and `U1.41` names 13 physical
  pads** (the module's GND thermal array). Five U1 pads screened as needing
  an escape; they collapsed to one table entry, so four got none. Harmless
  here — they are all GND and the pours flood them — but the accounting is
  `54 written + 3 failed + 4 collapsed = 61 screened`, and a part with
  duplicate pad numbers on a *signal* net would lose escapes silently.
- The board still needs its **GND stitching ring** (~6 mm pitch perimeter)
  after routing. The escapes contribute 13 GND vias, which is not plane
  stitching.
- `U2` and `U1` raise `lib_footprint_mismatch` warnings — pre-existing; U2's
  land was hand-edited.

## 7. Traps that cost time

Recorded because each one looked like something else.

- **KiCad 10 writes a locked track as `(type fix)`, not `(type protect)`.**
  An early `export_dsn.py` grepped for the literal `protect`, found zero,
  and reported the lock had been dropped. It hadn't. Acting on that false
  alarm, `protect_dsn.py` rewrote all 112 items from `fix` *down* to
  `protect` — the weaker state. Both scripts now count every Specctra fixed
  type (`fix`, `protect`, `shove_fixed`) and default to `fix`.
- **A failed Freerouting run leaves the previous `.ses` in place.** The jar
  path was wrong, java exited, and the import silently pulled in a session
  from before the escapes existed — 604 F.Cu segments, both inner layers
  empty, old route stacked on the new escapes. `import_ses.py` now refuses a
  `.ses` older than the `.dsn`. Per-layer counts alone don't catch this;
  they looked like real data from a real run. Timestamps settle it.
- **Specctra declares its own quote character with `(string_quote ")`.** A
  lone `"` that opens a string which never closes. Any string-aware scan
  starting at the top of the file dies there. `protect_dsn.py` blanks that
  clause with equal-length spaces before scanning so offsets stay valid.
  Also: padstack names are quoted and **contain parentheses**
  (`Via[0-3]_800:400_um`), so regex is not safe on a DSN — use a real
  s-expression scanner.
- **`BOARD.Zones()` returns a plain tuple in KiCad 10.0.6** — no `.size()`.
  And `ZONE_FILLER.Fill()` wants its own container type.
- **`kicad-cli pcb export specctra-dsn` does not exist** in KiCad 10. Use
  `pcbnew.ExportSpecctraDSN` / `ImportSpecctraSES` from Python.
- **Footprint rotation sign is `−rot`** in the transform (verified against
  DRC). Getting it wrong produces phantom overlap reports on 90°-rotated
  pads.
- **Paste- and mask-only pads are not copper.** Counting them as copper
  invented a 9-pad "defect" on U1's thermal land and inflated the trapped-pad
  count. Filter on `(layers ...)` containing a `.Cu` entry.
- **KiCad's DRC report is the truth for connectivity.** Three separate
  geometric analyses of pour connectivity disagreed with it (71, then 69
  orphans vs KiCad's ~17) because `filled_polygon` data goes stale. Home-made
  geometry is trustworthy for *clearance*, not for connectivity.
- `island_removal_mode 1` made things worse: 49 → 128 violations, +79
  `isolated_copper`. The F.Cu pour is roughly 79 fragments.

## 8. Scripts on this branch

| File | Interpreter | What |
|---|---|---|
| `fanout.py` | plain | Strip all routing, write the 54 escapes. Backs up to `.bak-fanout`. Idempotent in effect — safe to re-run to clean a board. |
| `set_epdhv.py` | plain | EPD_HV clearance → 0.20 mm. One JSON key, backs up, idempotent. KiCad must be closed. |
| `export_dsn.py` | KiCad's | Refill pours, lock all tracks, export DSN, report the type breakdown. |
| `protect_dsn.py` | plain | Verify/set the Specctra fixed type on every wire and via. Defaults to `fix`. |
| `import_ses.py` | KiCad's | Import the `.ses`, report segments **per layer**, confirm the 112 locked escapes survived. Refuses a stale session file. |
| `docs_4layer.py` | plain | Bring the docs in line with the 4-layer board. Idempotent. |

## 9. What "done" looks like

1. DRC: zero errors. Silk warnings and `via_dangling` before routing are
   expected — a dangling via is an escape waiting for the router.
2. `import_ses.py` shows **non-zero In1.Cu and In2.Cu** segment counts. Zero
   on both means the inner layers were dropped again; stop and diagnose.
3. `locked` still reads **112** after import. Lower means Freerouting
   rewrote escapes despite the fixed type.
4. GND stitching ring added.
5. `U2` / `U5` real lands in, escapes recomputed for the 3 missing pads.
6. Then Gerbers (`fab.py`).
