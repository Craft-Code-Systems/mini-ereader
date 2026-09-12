# Changelog

All notable changes to the Mini E-Reader project. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); dates are ISO-8601.

## [Unreleased]

### Fab preflight gate + honest CI, after a routed board reached main out of sync (2026-09-12)
The board was routed and pushed to `main` (commit `board routed and gerber file
generated incl. DRC report`), but it was routed **before** *Update PCB from
Netlist* was run, so the 19 Rev C4 parts never landed on it. Analysis of that
commit:
- **Board ≠ netlist.** The routed `ereader.kicad_pcb` carries the original 56
  footprints; the EPD external DC-DC block (LE/QE/DE1-3/RE1-2/CE1-9) and the
  decoupling caps (CGA/CGB/C4I) added to `ereader-kicad.net` in Rev C4 are
  **absent**. The EPD panel therefore still has no boost/charge-pump and cannot
  display. `kicad-cli` DRC does not compare board vs netlist, so it stayed
  silent about this.
- **Placeholder footprints still in place.** U2 is still on the wrong 24-pin
  QFN 4x4 (BQ25628E is 18-pin WQFN 2.5x3.0) and U5 on the oversized SON-8 3x2
  (should be VSON-HR 2x2). Traces route to lands the real parts do not fit.
- **DRC (CI, KiCad 10.0.0, --refill-zones):** 0 violations, 0 footprint errors,
  **3 unconnected items** — all isolated `GND_F.Cu` pour islands at the antenna
  keepout corner (1, 8). Real (routing-induced): stitch to the GND plane or trim
  the pour. `unconnected_items` is `error` severity in this project.
- **Gerbers/DRC report were NOT committed** despite the message — `.gitignore`
  excludes `fab/`, `gerbers/`, `*.zip`; only the routed board was committed.
- Positives: routing is complete for the placed parts (0 pad-to-pad gaps), net
  classes were honored (Power 0.4mm, USB 0.25mm, default 0.2mm), and the antenna
  keepout is clean (0 copper in the band).

Fixes applied here (tooling/process — the board-layout fixes require KiCad and
are listed as the remaining manual steps):
- **`preflight.py`** — fails if any `ereader-kicad.net` component is missing from
  `ereader.kicad_pcb`. Closes the board/netlist parity gap kicad-cli can't see.
- **CI is now a hard gate** (`.github/workflows/kicad.yml`): runs `preflight.py`,
  then DRC with `--exit-code-violations` (no more `continue-on-error`), and only
  exports gerbers when both pass. CI will be **red until** the board is synced
  and the 3 GND islands are fixed — by design.
- **`fab.py`** refuses to emit gerbers from an out-of-sync board (override:
  `--force`).
- Remaining manual steps (KiCad): *Update PCB from Netlist* to place the 19
  parts; swap U2-U5 to the datasheet lands; place+route the EPD DC-DC block
  (tight boost loop, transcribe the interconnect + J2 FPC pins 1:1 from the
  Good Display reference); stitch/trim the 3 GND_F.Cu islands; re-run DRC.

### Rev C4 — capture the missing EPD DC-DC block, reconcile decoupling, correct IC packages, fix doc drift (2026-09-11)
Design-review pass before a possible manufacturing hand-off found several gaps
that would produce a non-working or non-buildable board. Addressed at the
netlist-first source-of-truth level (`ereader-kicad.net` drives the PCB on
re-import):

- **EPD SSD1677 external DC-DC now captured as real parts.** ADR 0002 /
  `ereader-pcb-design.md` §6 require an external boost + charge-pump for the
  panel's ±20V gate / ±15V source rails, but no such parts existed in the
  netlist/BOM/board — the panel could never have displayed. Added `LE` (47µH),
  `QE` (Si1308EDL N-FET), `DE1–DE3` (MBR0530), `RE1` (2.2Ω RESE sense), `RE2`
  (1MΩ GDR pulldown), `CE1–CE6` (4.7µF/25V rail reservoirs), `CE7–CE9`
  (1µF/25V), wired to J2's support pins (GDR/RESE/VGH/VGL/VSH1/VSH2/VSL/VCOM/
  VCI) with BS1 tied low for 4-wire SPI. **The diode/charge-pump interconnect,
  diode orientation, and J2 FPC pin numbers are a functional placeholder** —
  flagged in-file to be transcribed 1:1 from the Good Display reference before
  route (rail cap values non-negotiable, ≥25V).
- **Decoupling reconciled to spec.** Added the local caps the connection-list
  called for but that were missing: `CGA`/`CGB` (MAX17048 CELL 0.1µF+1µF),
  `C4I` (LM3630A IN 1µF).
- **IC package facts corrected** (verified against vendor datasheets): U2
  BQ25628E is an **18-pin WQFN 2.5×3.0mm (RYK)** — the placeholder
  `HVQFN-24-1EP_4x4mm` is the wrong pincount/size; U5 TPS62840DLCR is
  **VSON-HR 8-pin 2.0×2.0mm** — the placeholder `SON-8_3x2mm` is oversized (and
  it is not SOT-563); U4 LM3630A is DSBGA-only (no WSON variant). Netlist
  footprints left as import-clean placeholders; corrections documented in
  `ereader-footprints.md` so the right vendor land gets pulled.
- **Net classes extended:** the new EPD boost node + ±20V/±15V rails (EPD_SW,
  EPD_VGH/VGL, EPD_VSH1/VSH2/VSL, EPD_PREVGL) added to the `Power` class in
  `ereader.kicad_pro`.
- **Pin-map status clarified:** J4 microSD uses the DM3AT pad names so it maps
  on import; J2's function-name pins (incl. the new rails) still need the
  GDEY0426T82 FPC numbers from the datasheet — the one genuinely
  datasheet-blocked remap.
- **Doc drift fixed:** ADR 0002 got a non-normative Rev C reconciliation note
  (its J4/J5 and L2/Q2/D4-D6 designators predate Rev C); runbook bring-up step 6
  corrected (frontlight is LM3630A over I2C1 + FL_HWEN, not direct GPIO15/16 PWM).
- **Not changed:** routing (still 0 track segments — an RF+USB+switcher board
  whose compliance depends on hand/contractor layout, per the README ROUTING
  gate) and the vendor-exact U2–U5 lands (pull from SnapEDA/Ultra-Librarian).
  The new parts are in the netlist/`.cmp` but not yet placed on `.kicad_pcb`;
  re-import the netlist in KiCad to bring them onto the board.

### Found why the GUI kept showing the stale 3-entry GND_F.Cu result after the fix (2026-09-11)
- The board-level fix was confirmed correct twice over (a real KiCad 7.0.11
  `ZONE_FILLER` run locally, and CI forced to do a genuine from-scratch
  refill on KiCad 10.0.0 - see the two entries below), yet the project
  owner kept seeing the identical stale 3-entry `Zone 'GND_F.Cu'` report
  after every fix, including after fully quitting/reopening KiCad. Confirmed
  the report is generated via the KiCad GUI's own DRC dialog
  (Inspect -> Design Rules Checker), not `kicad-cli` or a CI artifact - so
  the CLI/CI proof didn't rule out something GUI-specific.
- Found it in KiCad's own source (`pcbnew/dialogs/dialog_drc.cpp`): the DRC
  dialog has a "Refill zones before performing DRC" checkbox
  (`m_cbRefillZones`), and its checked/unchecked state **persists across
  sessions** (`cfg->m_DrcDialog.refill_zones`), independent of the project
  file. If it was left unchecked from an earlier run, the dialog reuses
  whatever zone fill happens to already be in memory/on-disk instead of
  recomputing - so closing and reopening KiCad, or pulling new board
  changes, doesn't clear it. This is the same default-off behavior that
  `kicad-cli pcb drc` has (and that `--refill-zones` was added to this
  project's CI to work around, below).
- Action for the project owner: in the DRC dialog, check "Refill zones
  before performing DRC" before clicking "Run DRC". No further board
  changes were made in this entry - the board file itself has been correct
  since the keepout-zone fix two entries below.

### Confirmed the GND_F.Cu fix holds; the CI's pinned KiCad 8.0 was the actual source of the persistent false positive (2026-09-11)
- The previous entry's keepout-zone fix *did* work - the "3 unconnected_items
  between Zone 'GND_F.Cu' and itself" that survived three rounds of board
  fixes turned out to be a false positive specific to KiCad 8.0, not a real
  remaining board defect:
  - A `kicad-cli pcb drc --format json` run on a locally-installed KiCad
    10.0.0 (same version the project owner already runs locally) shows
    **zero** zone-related entries at all - every one of its ~60
    `unconnected_items` is a plain pad-to-pad gap on an unrouted signal net
    (`+3V3`, `I2C0_SDA`, `BTN_A`, `USB_DP`, `LEV_CW`, ... - expected, since
    this board has 0 routed track segments; it's placed but not routed, a
    separate later phase).
  - A `kicad-cli pcb drc` text-report run from this repo's CI - pinned to
    `kicad/kicad:8.0` - kept reproducing the exact same 3 zone entries,
    identical down to the anchor point, across every fix in this pass
    (pad nets, a 23-pad zone_connect sweep, the keepout removal). Two
    different KiCad major versions given the *identical* board file
    disagreeing this completely, with 10.0.0 matching what a ground-up
    KiCad 7.0.11 source read and engine test also predicted, points at an
    8.0-era zone-fill/connectivity bug, not the board.
- Repinned `.github/workflows/kicad.yml` from `kicad/kicad:8.0` to
  `kicad/kicad:10.0.0` so CI's DRC output matches what's actually
  authoritative for this board going forward.

### Remove a mis-scaled antenna keepout zone embedded in U1 that blocked GND fill outside the actual antenna area (2026-09-11)
- The previous pass's pad-level fixes (U1 EPAD net, broad zone_connect sweep)
  had zero effect on unconnected_items - still exactly 3, unchanged across
  three consecutive reports despite a from-scratch local refill confirming
  those fixes merge the zone into 1 island. Since nothing pad-level moved
  the number at all, went looking for something structural that no pad
  setting could route around.
- Found it: U1 (`ESP32-S3-WROOM-1`) carries its own footprint-embedded
  keepout zone (`copperpour not_allowed` on F.Cu/In1.Cu/B.Cu) with polygon
  `(9,6.25)-(57,6.25)-(57,-14.75)-(9,-14.75)` in the footprint's *local*
  frame. At U1's placement (33,13, no rotation) that's absolute
  x:42-90, y:-1.75-19.25 - 48x21mm, dwarfing the module's own ~18mm silk
  outline and running 24mm past the board's right edge and above the top
  edge. The real, documented antenna keep-out (the board-level "ANTENNA
  KEEPOUT" silk strip at y=0-7, full width) is already respected without
  this zone, since GND_F.Cu's own outline starts at y=8 - this extra zone
  only ate into the y=8-19.25 strip, which `ereader-pcb-design.md` explicitly
  wants as continuous ground ("Continuous GND plane under everything except
  antenna keep-out"). Almost certainly leftover data from whatever reference
  footprint this was built from, never rescaled for this board. Removed it.
- This exact keepout was present through every previous local KiCad 7.0.11
  refill test (all of which already showed 1 merged island), so it can't be
  blamed for anything observed locally - but keepout-vs-zone-fill clipping
  is exactly the kind of thing that could differ between the 7.0.11 engine
  available here and the CI's KiCad 8.0, and it's unambiguously a
  placement/scaling bug regardless of whether it's the cause. Re-filled and
  re-spliced the 3 GND zones after removing it - still 1 island, no
  regression.

### Harden every remaining thermal-relief GND pad to a solid zone connection (2026-09-11)
- hole_clearance and lib_footprint_mismatch are confirmed clear (0 DRC
  violations in the latest report). unconnected_items held steady at 3,
  unchanged by the previous pass's net/zone_connect fixes or the spliced-in
  fresh zone fill - strong evidence the CI's KiCad 8.0 zone-fill algorithm
  forms different islands than the KiCad 7.0.11 engine available in this
  sandbox for the *same* pad/net input, since a from-scratch refill in 7.0.11
  now shows a single, fully-merged island on every GND layer.
- Since the fill algorithm itself isn't reliably reproducible here, stopped
  trying to predict exactly which thermal-relief spokes a different KiCad
  version will or won't resolve, and instead removed the dependency:
  swept every GND-net copper/thru-hole pad on the board and gave the 23 that
  were still on default thermal relief a solid connection (`zone_connect 2`)
  - 6 previously-missed 0805 decoupling caps (CS/CF/CB/CU1/CI/CO), SW4's COM
    pad, JP5/JP6's pad 2, J5's pad 2, and all 13 copper features of U1's
    exposed pad/pin 41 (only 1 of which got a net at all in the previous
    pass). `zone_connect` is one of the fields `FootprintNeedsUpdate()`
    explicitly excludes from the library-parity comparison (confirmed in
    source), so this doesn't reopen the footprint-mismatch warnings that
    pass just cleared.
- Re-filled all 3 GND zones with KiCad 7.0.11's real `ZONE_FILLER` again
  after this change (still 1 island each - no regression) and spliced the
  fresh fill into the board file, same as last time.
- Still unverified against the actual `kicad-cli` 8.0 the CI runs - if
  unconnected_items persists after this, the next step is isolating which
  specific pad differs between the two engines' island formation, since
  broad-brush solid-fill sweeps don't have much further room to run.

### Fix remaining DRC errors and warnings, verified against the real KiCad 7 engine (2026-09-10)
- **Root-caused the previous pass's two open items by reading KiCad's own DRC source**
  (`pcbnew/drc/drc_test_provider_library_parity.cpp`, `drc_rule_parser.cpp`,
  `pcb_expr_evaluator.cpp`, `pad.cpp`) and cross-checking every fix against a
  locally-installed KiCad 7.0.11 (`kicad-cli`/`pcbnew` Python bindings aren't
  available in the normal sandbox - installed via apt for this pass only):
  - `FOOTPRINT::FootprintNeedsUpdate()` compares each pad's orientation
    *relative to its parent* (`pad->GetOrientation() - parent->GetOrientation()`),
    not the raw stored angle. KiCad's writer omits the `at` angle for pads
    where rotation doesn't change the rendered shape (circles, squares), but
    the parity check still computes a relative angle from whatever's stored
    (0) minus the footprint's placement rotation - so every omitted-angle pad
    in a rotated footprint instance compared as mismatched even though it
    looks identical on screen. Added the explicit matching angle (matching
    the footprint's own placement rotation, like the already-correct pads in
    the same instance) to: SW4's 2 locator NPTH holes (+90), SW1/SW2/SW3's 2
    boss NPTH holes each (+270), and JP5/JP6's 2 pads each (+270).
  - `FootprintNeedsUpdate()` also compares `descr` and `tags` verbatim - the
    board instances and the library copies had diverged wording for SW4
    (`ALPS_SLLB5_Lever`) and SW1-3 (`WE_WS-TASU_436351045816`). Re-synced the
    library text to the board's (shorter, already-accurate) copy. JP5/JP6
    (`JumperPad_2P_P2.0mm`) had board text hardcoded per-instance ("pull IO0
    low for BOOT" vs "...EN low for RESET") that can't simultaneously match
    one library description - genericized the library + both instances to
    "pull the associated signal low".
  - Verified via `FOOTPRINT.FootprintNeedsUpdate()` (the exact C++ method the
    DRC check calls) through Python bindings: all 6 previously-flagged
    footprints (SW1-4, JP5, JP6) now return `False`.
  - The `ereader.kicad_dru` custom rule from the previous pass used
    `(condition "A.Reference == B.Reference")`, but `Reference` is only
    registered as a property on `FOOTPRINT`, not `PAD` - on a pad the
    expression evaluates to an undefined value, so the condition never
    matched and the rule silently never applied (board setup's global
    0.25mm stayed in force). `PAD` instead registers `Parent` (returns the
    parent footprint's reference). Fixed to `(condition "A.Parent ==
    B.Parent")`. The `hole_clearance` constraint keyword itself was already
    correct (confirmed against `drc_test_provider_copper_clearance.cpp`,
    which is what actually emits this violation and whose implicit rule name
    - "board setup constraints hole" - matches the DRC report verbatim).
  - Re-filled all 3 GND zones with KiCad's real `ZONE_FILLER` to check
    whether the U1/J1 net fixes from the previous pass actually reconnected
    the copper: `GND_F.Cu` now fills as a single island (was 3 disjoint
    islands before those fixes), confirming the unconnected_items fix holds.
    Spliced the freshly-computed `filled_polygon` data for all 3 GND zones
    back into the hand-edited board file (surgical text replacement, not a
    full `pcbnew` re-save, to avoid KiCad 7's writer reformatting/reordering
    the rest of the file) so the committed fill isn't stale relative to the
    net/zone_connect changes.
  - Could not reproduce the exact `kicad-cli pcb drc` command the project's
    CI uses (KiCad 8.0): apt on this box only has KiCad 7.0.11, whose
    `kicad-cli` predates the `pcb drc` subcommand, and kicad.org/PPA hosts
    are blocked by this sandbox's egress policy. All of the above was cross-
    checked against KiCad 7.0.11's real DRC/library-parity source and engine
    instead - a real re-run in KiCad 8 is still worth doing to confirm.

### Fix remaining DRC errors and warnings: U1 EPAD net, J1 shield thermals, SW4 library parity, mechanical hole clearance (2026-09-08)
- **U1 (ESP32-S3-WROOM-1) exposed pad (pin 41/EPAD) wasn't actually on GND.**
  Of the 13 copper features that make up the module's exposed thermal pad
  (the 3.9x3.9mm SMD land plus its 12 small heatsink through-holes), only one
  through-hole carried `(net 5 "GND")` - the rest were floating, even though
  `ereader-connection-list.md` documents `U1.41(EPAD)` as GND. The floating
  copper forced the F.Cu GND zone to clear around most of the pad instead of
  merging with it, splitting the zone into a ~16x17mm island under U1 that
  DRC reported as 2 "unconnected_items" pairs (4 identical entries - KiCad
  lists each ratsnest edge both directions). Added the missing net to all 12
  pads.
- **J1 (USB-C) shield/mechanical pads (S1) starved their own thermal
  reliefs.** All 4 S1 pads were on GND with default (spoke) zone connection;
  one of them resolved to only 1 of the usual spokes on In1.Cu, leaving an
  isolated copper island (`starved_thermal`) - the same failure mode already
  fixed for J1's small SMD GND pads (A1/A12/B1/B12) in an earlier pass, just
  not extended to S1. Also pinched off a second, tiny F.Cu island right next
  to A12/B1 (the other 2 "unconnected_items" pairs). Gave all 4 S1 pads a
  solid zone connection (`zone_connect 2`), matching A1/A12/B1/B12.
- **SW4 (`ereader:ALPS_SLLB5_Lever`) library/board parity - actually fixed
  this time.** The previous "sync footprint library" pass edited the
  library's 2 corner solder-lug pad rotations from 45°/135° to 135°/225° to
  match the board's raw stored angle at SW4's 90° placement - but a pad's
  stored angle in the `.kicad_pcb` already bakes in the footprint's own
  rotation (angle = local + placement), so the *pre*-edit library values
  were the correct local design angles all along; the edit introduced a
  real 90° mismatch instead of fixing one. Reverted to 45°/135°. (SW1-3,
  JP5, JP6 already matched their library copies on inspection - the other 5
  `lib_footprint_mismatch` warnings in the last report look stale.)
- **SW4 hole-clearance errors (CW/COM/PUSH/CCW pads vs. the switch's own
  Ø1.1mm locator holes) are the ALPS SLLB5 datasheet land, not a placement
  bug** - the physical part puts signal pads as close as ~0.05mm from its
  own locator holes, under the board's global 0.25mm min hole clearance.
  Added `ereader.kicad_dru` with a custom rule that relaxes hole clearance
  to 0.02mm only between pads/holes sharing the same footprint reference,
  leaving the global rule intact for every other part on the board.

### 3D views: SW4 lever corrected + self-contained bodies for every component (2026-09-06)
- **SW4 (ALPS SLLB5) 3D body fixed.** The old `ereader.3dshapes/ALPS_SLLB5_Lever.wrl`
  rendered as a tall block with an upward box knob — an "odd big switch". The SLLB5 is
  actually a **flat semicircular "fan" puck** (W 9.5 × D 8.8 × **H 2.2 mm**, the
  datasheet Lever-Return family) that lies on the board with a **low sideways
  rocker/toggle lever** on top (flick left↔right = CW/CCW, press = PUSH). Rebuilt the
  body as the flat puck + sideways lever to match the ALPS datasheet drawing/photo.
- **The whole board now renders in the 3D viewer without KiCad's stock 3D libraries.**
  Every placed component previously pointed at stock `${KICAD6/7_3DMODEL_DIR}` packs,
  which go missing on any machine/CI without the KiCad 3D-model add-on — so most parts
  showed no 3D body. Added simplified project-local bodies for all remaining footprints
  (R/C/L passives, `SOT-23-6`, `SON-8`, `DFN-8`, `HVQFN-24`, `ESP32-S3-WROOM-1`,
  `Maxim_WLP-12`, `D_SOD-123`, `USB_C_Receptacle_HRO_TYPE-C-31-M-12`, `JST_PH_S2B-PH-K`,
  `Hirose_FH12-6S/24S`, `microSD_HC_Hirose_DM3AT`) in `ereader.3dshapes/*.wrl`, and
  repointed all 43 stock `(model …)` refs in `ereader.kicad_pcb` to
  `${KIPRJMOD}/ereader.3dshapes/…` at `scale 0.3937`. Bodies are box/cylinder stand-ins
  sized from each part's datasheet/footprint outline (colour-coded by class) — for
  visualisation only; swap in vendor STEP/WRL before fab. Fiducials, M2 mounting holes,
  and the bare `JumperPad_2P_P2.0mm` keep no body. Updated `ereader-footprints.md`.

### BOOT/RESET switches replaced with bare jumper pads (2026-09-06)
- **SW5/SW6 → JP5/JP6.** BOOT and RESET are no longer Würth WS-TASU tactiles —
  they're bare 2-pad exposed jumpers (`ereader:JumperPad_2P_P2.0mm`, hand-drawn,
  two 1.2×1.2 mm pads on 2 mm pitch, no switch part), momentarily shorted with a
  screwdriver tip or tweezers to pull `IO0_BOOT`/`EN` low. Same board position and
  nets as the tactiles they replace (pad 1 → `IO0_BOOT`/`EN`, pad 2 → `GND`), so
  routing/placement elsewhere is unaffected; drops two tactile switches from the
  BOM. Updated `ereader-connection-list.md`, `ereader-schematic.md`,
  `ereader-pcb-design.md`, `ereader-footprints.md`, `ereader-kicad.net`,
  `ereader.cmp`, `ereader.kicad_pcb`, `ereader-placement.svg`, and ADR 0008.
  Hand-drawn pad geometry (no datasheet, since there's no part to order) —
  still to be DRC'd against fab minimum clearance and the case cutout before fab.

### Switch footprints locked to datasheets (2026-09-06)
- **Tactiles → Würth WS-TASU 436351045816** (4.7×3.5 mm side push with boss).
  Replaced the generic `Tact_Side_TS1187A` stand-in with `ereader:WE_WS-TASU_436351045816`,
  its land drawn from the WE datasheet (rev 001.003): 4 pads 1.2×0.7 mm at x=±2.8 /
  y=±1.35 plus **two Ø0.75 boss holes** at y=±1.375 (pins 1≡3 top, 2≡4 bottom). SW1–SW3
  and SW5/SW6 rotated **270°** so the actuator faces the right board edge.
- **SW4 → exact ALPS SLLB5 land.** Rebuilt `ereader:ALPS_SLLB5_Lever` from the ALPS
  datasheet (p.491): 4 signal pads 1.0×1.3 mm on **2 mm pitch** in terminal order
  **CW / COM / PUSH / CCW**, plus **two Ø1.1 locator holes** at x=±1.9 and side solder
  lugs; body 9.5×8.8 mm. Rotated **90°** so the lever faces the left edge. Nets
  unchanged (LEV_CW/CCW/PUSH + COM→GND).
- 3D bodies (`ereader.3dshapes/*.wrl`) and `ereader-kicad.net` / `ereader.cmp` updated
  to the new footprint ids. Lands are datasheet-drawn but still to be DRC'd against the
  ordered part before fab.

### Switches + schematic (2026-09-06)
- **Navigation buttons are now genuinely side-actuated.** SW1–SW3 (and BOOT/RESET
  SW5/SW6) moved off the top-actuated `Button_Switch_SMD:SW_SPST_TL3342` stand-in
  onto a new project footprint `ereader:Tact_Side_TS1187A_4P_3.5x4.7mm` (TS-1187A /
  YD-3414 class), with the actuator facing the board edge — required because the
  screen covers the whole front and magnets hold the back to the phone, so top/bottom
  actuation is unreachable. SW1–SW3 rotation set to 0° so the actuators point at the
  right edge; nets (BTN_A/B/C, IO0_BOOT, EN, GND) preserved.
- **SW4 lever land built.** Replaced the `PinHeader_1x04` placeholder with
  `ereader:ALPS_SLLB5_Lever` (ALPS SLLB5, ~9.5×8.8×2.2 mm) whose pads are named
  **CW/CCW/PUSH/COM**, so `LEV_CW`(23)/`LEV_CCW`(24)/`LEV_PUSH`(25) and `COM→GND`(5)
  now connect on netlist import instead of sitting unconnected. Noted SLLB510100 as a
  pin-compatible alternative.
- Added project footprint library `ereader.pretty` (registered in a new `fp-lib-table`)
  and simplified 3D bodies in `ereader.3dshapes/*.wrl` (referenced with `scale 0.3937`)
  so the switches render in the 3D viewer without KiCad's stock libraries. Updated
  `ereader-kicad.net` + `ereader.cmp` footprint IDs to match. Lands are approximate
  stand-ins — DRC vs the ordered MPN before fab.
- **Added a reviewable schematic, `ereader-schematic.md`** (subsystem Mermaid
  diagrams built from the connection list; renders on GitHub). Documents why the
  netlist-first design has no native Eeschema `.kicad_sch` and how to draw one. Updated
  `ereader-footprints.md`, `ereader-README.md`, `ereader-pcb-design.md`, and ADR 0008.
- **Removed the legacy `hardware/` reference spec** (`DESIGN.md`, `BOM.csv`,
  `gen_netlist_skidl.py`, its `README.md`) — the older 3-button lineage with a
  conflicting parts list (MCP73831 / AP2112K / TPS61165), superseded by the canonical
  `ereader.*` docs. Redirected all live references (README, `docs/runbook.md`, the
  CI workflow trigger paths + comment, ADRs 0001/0002/0003/0008, and the
  `ereader-pcb-design.md` DC-DC provenance note) to the `ereader-*` docs so there is a
  single source of truth. Historical entries in this changelog and `docs/research-log.md`
  are left as-is.

### Merged / consolidated (2026-09-05)
- Merged `claude/schematics-pcb-review-rq1i2t` into `main` alongside the
  first-try board `ereader.*` (`colophon-standard-compliance` had no unique
  commits). Clean merge (disjoint paths).
- Established the actual KiCad board **`ereader.*` (Rev C) as canonical**;
  `hardware/` is now labelled a reference spec. Full comparison in
  `docs/research-log.md`.
- Retargeted the KiCad CI workflow at `ereader.kicad_pcb` (DRC + gerber
  export). Removed a stray `~ereader.kicad_pro.lck`; git-ignore KiCad/lock/
  history/gerber cruft going forward.
- **Consolidated to a single KiCad project.** Removed the redundant
  `hardware/` scaffold KiCad files (`mini-ereader.kicad_pro`, `.kicad_sch`,
  `.kicad_pcb`, `fp-lib-table`, `sym-lib-table`); the canonical board is now
  the only KiCad project, `ereader.*` at the repo root. `hardware/` keeps the
  electrical source-of-truth (`DESIGN.md`, `BOM.csv`, `gen_netlist_skidl.py`).
  Docs, the runbook, ADR 0002, and CI updated to point at `ereader.*`.
- **Reconciled the ADRs to the canonical Rev C parts.** Added
  [ADR 0006](docs/adr/0006-i2c-managed-power-path.md) (I2C-managed power path:
  BQ25628E charger + TPS62840 buck + MAX17048 gauge, two I2C buses) which
  supersedes ADR 0003, and
  [ADR 0007](docs/adr/0007-lm3630a-frontlight-driver.md) (LM3630A
  single-boost dual-sink frontlight driver) which supersedes ADR 0005. ADRs
  0003 and 0005 are marked Superseded, with their reasoning preserved.
- Documented the navigation input scheme in
  [ADR 0008](docs/adr/0008-navigation-input.md): three side tactile buttons +
  an ALPS SLLB510200 multi-directional lever switch (CW/CCW/press), all on
  RTC-capable wake GPIOs. (New decision; the reference spec had three buttons
  only.)
- Folded the exact SSD1677 external DC-DC values from `hardware/DESIGN.md` §5
  into `ereader-pcb-design.md` §6 (L 47 µH, Si1308EDL FET, MBR0530 ×3,
  2.2 Ω sense + 1 MΩ pulldown, 4.7 µF/1 µF ≥25 V caps, and the VGH/VGL/VSH/
  VSL/VCOM rails) so the canonical spec no longer defers to the vendor zip.
- Removed the committed `ereader-gerbers.zip` build artifact (regenerable with
  `python3 fab.py`; already git-ignored); docs now describe it as a generated
  output, not a shipped file.

### Added
- Hardware design for a 4.26" 800×480 frontlit e-paper reader:
  `hardware/DESIGN.md` (block diagram, power tree, net list, ESP32-S3 pin
  map, frontlight subsystem, PCB guidance, verification status).
- KiCad 8 project scaffold + config: `hardware/mini-ereader.kicad_pro`,
  `.kicad_sch`, `.kicad_pcb`, library tables.
- `hardware/BOM.csv` and `hardware/gen_netlist_skidl.py` (SKiDL netlist
  generator).
- Decisions `docs/adr/0001`–`0005` (MCU, display + frontlight, power,
  native-USB programming, frontlight driver).
- CI: `.github/workflows/kicad.yml` runs `kicad-cli` ERC/DRC and exports a
  schematic PDF + gerbers as build artifacts.

### Changed
- Repository adapted from the Colophon documentation template into the
  Mini E-Reader project: Brief (`README.md`), Log, Runbook, and Changelog
  rewritten; methodology decisions replaced with product decisions.
- Display target corrected from an initial 2.13" assumption to **4.26"
  800×480** after the owner supplied the FL0426-S01C frontlight datasheet;
  a tunable-white frontlight subsystem was added (see ADR 0002 / 0005).
- Display **locked to Good Display GDEY0426T82-FL01C** (controller SSD1677)
  from the panel datasheet: 24-pin EPD FPC pinout and the SSD1677 external
  DC-DC reference circuit captured in DESIGN.md §5; BOM gains J4 + boost
  parts (L2, Q2, D4-D6, R11/R12, ≥25 V caps); the SKiDL generator now emits
  the real EPD block.

### Removed
- Colophon methodology content that no longer applies to this project:
  `docs/faq.md`, `docs/adoption.md`, the methodology ADRs
  (`docs/adr/000{1..5}-*` Colophon versions), the duplicate `hardware/docs/`
  tree, and `LICENSE-TEXT` (the methodology's CC BY 4.0 license). The
  project is MIT (`LICENSE`).

### Notes
- Schematic/PCB are valid scaffolds, not yet captured/routed; ERC/DRC must
  pass in KiCad (now also runnable in CI).
- Two switching subsystems (EPD DC-DC + frontlight boost) must be laid out
  away from the antenna and the battery-sense ADC.
