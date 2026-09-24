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
n_prot = len(re.findall(r"\(type\s+protect\)", text))
n_layer = len(re.findall(r"\(layer\s+\S+\s*\n?\s*\(type\s+signal\)", text))
print("wrote %s  (%.1f MB)" % (dsn, os.path.getsize(dsn) / 1e6))
print("  signal layers declared  : %d" % n_layer)
print("  protected (locked) items: %d" % n_prot)
if not n_prot:
    print("  -> KiCad 10 does not carry a locked track into Specctra's protect")
    print("     type. Run:  python3 protect_dsn.py %s" % dsn)
    print("     Without it Freerouting will rip the escapes out and you are")
    print("     back where you started.")
