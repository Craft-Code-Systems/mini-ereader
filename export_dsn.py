#!/usr/bin/env python3
"""Refill the pours, lock the fanout escapes, export a Specctra DSN.

Locking matters: KiCad's Specctra exporter writes locked tracks and vias as
`(type protect)`, which tells Freerouting to route around them instead of
ripping them up. After fanout.py, the only tracks on the board ARE the
escapes, so "lock every track" is exactly "lock the escapes".

The export is verified, not assumed -- the script counts `protect` in the
DSN and says plainly whether the lock carried through.

Run with KiCad's Python (the one that can `import pcbnew`), and with the
board closed in the GUI so the save is not clobbered.

USAGE:  python3 export_dsn.py [ereader.kicad_pcb] [ereader.dsn]
"""
import os
import re
import sys
from collections import Counter

import pcbnew

pcb = sys.argv[1] if len(sys.argv) > 1 else "ereader.kicad_pcb"
dsn = sys.argv[2] if len(sys.argv) > 2 else "ereader.dsn"

if not os.path.exists(pcb):
    sys.exit("run this in the mini-ereader directory (no %s here)" % pcb)

b = pcbnew.LoadBoard(pcb)

# Best effort: KiCad 10's Zones() hands back a plain tuple, and ZONE_FILLER
# wants its own container. If this cannot run, the fills already in the file
# stand -- press B in the GUI and save before running this.
zones = b.Zones()
try:
    filler = pcbnew.ZONE_FILLER(b)
    try:
        filler.Fill(zones)
    except TypeError:
        vec = pcbnew.ZONES()
        for z in zones:
            vec.append(z)
        filler.Fill(vec)
    print("refilled %d zones" % len(zones))
except Exception as e:
    print("could not refill %d zones (%s: %s)" % (len(zones), type(e).__name__, e))
    print("  -> open the board, press B, save, and re-run this script")

n_trk = n_via = 0
for t in b.GetTracks():
    t.SetLocked(True)
    if isinstance(t, pcbnew.PCB_VIA):
        n_via += 1
    else:
        n_trk += 1
b.Save(pcb)
print("locked %d escape segments + %d escape vias" % (n_trk, n_via))

try:
    pcbnew.ExportSpecctraDSN(b, dsn)
except TypeError:
    pcbnew.ExportSpecctraDSN(dsn)

text = open(dsn, encoding="utf-8", errors="replace").read()

# Specctra has several fixed types and KiCad picks `fix` for a locked track.
# Counting only `protect` here once produced a false alarm that led to the
# escapes being downgraded from fix to protect -- count them all.
found = Counter(re.findall(r"\(type\s+(\w+)\)", text))
n_fixed = sum(found[t] for t in ("fix", "protect", "shove_fixed"))
n_loose = sum(found[t] for t in ("normal", "route"))
n_layer = len(re.findall(r"\(layer\s+\S+\s*\n?\s*\(type\s+signal\)", text))
print("wrote %s  (%.1f MB)" % (dsn, os.path.getsize(dsn) / 1e6))
print("  signal layers declared: %d" % n_layer)
print("  wire/via types        : %s"
      % (", ".join("%s=%d" % (k, v) for k, v in sorted(found.items())) or "none"))
print("  fixed (Freerouting will not rip these up): %d" % n_fixed)
if n_loose or not n_fixed:
    print("  -> %d item(s) are rippable. Run:  python3 protect_dsn.py %s"
          % (n_loose, dsn))
    print("     Freerouting reroutes anything not fixed, which would undo the")
    print("     pad escapes and put the board back where it started.")
