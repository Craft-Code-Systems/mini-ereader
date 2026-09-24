#!/usr/bin/env python3
"""Bring ereader-README.md and ereader-pcb-design.md in line with the board.

The board went 4-layer -> 2-layer -> 4-layer during review; the docs were
edited to 2-layer on the way through. This rewrites both to describe what the
board actually is now, and documents the EPD_HV clearance change and the pad
escapes. Safe to run whichever wording is currently in the files.

USAGE:  python3 docs_4layer.py      # in the mini-ereader directory
"""
import os, re, sys

STACK_NEW = ("- **4-layer stackup**: **F.Cu signal / In1.Cu GND plane / "
             "In2.Cu signal / B.Cu signal**.")
POURS_NEW = ("- **GND pours**: filled zones on In1.Cu (plane), F.Cu and B.Cu "
             "— poured everywhere except the antenna keep-out band. "
             "Re-fill with `B` after you move parts.")
NETCLASS_NEW = """  - `Power` 0.40mm track / 0.20 clearance / 0.8-0.4 via → GND, +VBUS, +SYS, +VBAT, +3V3, FL_OUT, FL_SW, CHG_SW, BUCK_SW, PMID, REGN, EPD_RESE.
  - `USB` 0.25mm, diff-pair 0.20/0.13 → USB_DP, USB_DM (tune to 90Ω against your real stackup).
  - `EPD_HV` 0.30mm track / **0.20 clearance** / 0.8-0.4 via → EPD_SW, EPD_NODEX, EPD_VGH, EPD_VGL, EPD_VSH1,
    EPD_VSH2, EPD_VSL, EPD_VCOM (EPD boost node + ±20V/±15V rails — keep the EPD_SW loop tight).
    Clearance is 0.20, not 0.30: the GDEY0426T82 FPC land itself spaces these rails 0.2mm apart, so 0.30mm was
    never achievable at the connector, and IPC-2221 B4 (external, under solder mask) allows 0.13mm at 40V."""

REV4 = """## Rev 4 — pad escapes (fanout), so the router can use the inner layers

Freerouting stalled around 51 unconnected nets and left In2.Cu completely
unused. The cause was not the layer count. The fine-pitch parts — `J1`
(USB-C), `J2` (24-pin 0.5mm FPC), `U2` (0.4mm-pitch WQFN-HR18), `U3`, `U4`
(0.4mm DSBGA), `U5`, `J3` — have pads with **no room beside them for a 0.8mm
Power-class via**. A pad that cannot reach a via cannot reach an inner layer,
so the router had nowhere to go and gave up on the congested nets.

`fanout.py` fixes that the way a layout engineer does: each such pad gets a
**necked-down escape stub** (0.15–0.40mm; the board minimum is 0.15mm) running
out along the pad's own axis to a via in open copper. Traces fit where vias
don't — that is what makes the escape possible.

- Every escape is checked against every other pad, every other escape, the
  board edge and the U1 antenna keep-out, at **full netclass clearance**, and
  re-verified independently after being written to the board file.
- **No DRC rules were added or relaxed** for them. The one rule change is the
  `EPD_HV` netclass clearance (0.30 → 0.20mm), which the FPC land forced
  anyway — see Net classes above.
- Escapes are **locked** before the DSN export so Freerouting routes around
  them instead of ripping them up.

Run order: `python3 fanout.py` → open in KiCad, `B` to re-fill the pours, DRC
→ `python3 export_dsn.py` → Freerouting → import the `.ses`.

"""


def sub1(text, pattern, repl, what, flags=0):
    new, n = re.subn(pattern, lambda m: repl, text, count=1, flags=flags)
    print(("  ok   " if n else "  skip ") + what)
    return new


def readme(path):
    s = open(path, encoding="utf-8").read()
    print(os.path.basename(path))
    s = sub1(s, r"^- \*\*[24]-layer stackup\*\*.*$", STACK_NEW, "stackup line", re.M)
    s = sub1(s, r"^- \*\*GND (?:pours|planes)\*\*:.*$", POURS_NEW, "GND pour line", re.M)
    s = sub1(s, r"^  - `Power` 0\.40mm.*?\n(?:  - `USB`.*?\n)?(?:  - `EPD_HV`.*?\n(?:    .*?\n)*)?",
             NETCLASS_NEW + "\n", "net class list", re.M | re.S)
    s = sub1(s, r"^- \*\*GND via stitching\*\*.*$",
             "- **GND via stitching** — add a ~6mm-pitch perimeter ring of GND vias after routing to knit "
             "the pours to the In1.Cu plane (the pre-route slate ships with all vias stripped bar the pad escapes).",
             "stitching line", re.M)
    s = sub1(s, r"\*\*DRC ruleset \(JLCPCB [24]-layer\)\*\*",
             "**DRC ruleset (JLCPCB 4-layer)**", "DRC ruleset line")
    if "## Rev 4 — pad escapes" not in s:
        s = sub1(s, r"^## ⛔ The one gate that remains: ROUTING",
                 REV4 + "## ⛔ The one gate that remains: ROUTING", "Rev 4 section", re.M)
    else:
        print("  skip Rev 4 section (already present)")
    open(path, "w", encoding="utf-8").write(s)


def spec(path):
    s = open(path, encoding="utf-8").read()
    print(os.path.basename(path))
    s = sub1(s, r"^- Solid uninterrupted GND.*?stitch vias around edge \+ keep-out\.$",
             "- Solid uninterrupted GND plane on In1.Cu, backed by GND pours on F.Cu and B.Cu; "
             "stitch vias around edge + keep-out.", "GND plane line", re.M)
    s = sub1(s, r"^- [24]-layer .*?ENIG finish \(FPC \+ fine pitch\)\.$",
             "- 4-layer: **F.Cu signal / In1.Cu GND plane / In2.Cu signal / B.Cu signal**, with GND pours also on "
             "F.Cu and B.Cu.\n  Controlled-Z for USB pair. ENIG finish (FPC + fine pitch).\n"
             "- The inner layers are not optional. J1/J2/U2-U5 are 0.4-0.5 mm pitch; their pads have no room beside "
             "them for a\n  0.8 mm Power-class via, so each is given a pre-computed escape (a necked stub out to a "
             "via in open copper)\n  before routing. Without those escapes an inner layer is unreachable and the "
             "router cannot use it.", "stack line", re.M)
    open(path, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    for f, fn in (("ereader-README.md", readme), ("ereader-pcb-design.md", spec)):
        if os.path.exists(f):
            fn(f)
        else:
            sys.exit("run this in the mini-ereader directory (no %s here)" % f)
