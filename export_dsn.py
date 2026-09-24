#!/usr/bin/env python3
"""Refill the pours, lock the fanout escapes, export a Specctra DSN.

Locking matters: KiCad's Specctra exporter writes locked tracks and vias as
`(type protect)`, which tells Freerouting to route around them instead of
ripping them up.  After stripping, the only tracks on the board ARE the
escapes, so "lock every track" is exactly "lock the escapes".

The export is verified, not assumed -- the script counts `protect` in the
DSN and says plainly whether the lock carried through.

USAGE:  python3 export_dsn.py [ereader.kicad_pcb] [ereader.dsn]
"""
import re, sys, os
import pcbnew

pcb = sys.argv[1] if len(sys.argv) > 1 else "ereader.kicad_pcb"
dsn = sys.argv[2] if len(sys.argv) > 2 else "ereader.dsn"

b = pcbnew.LoadBoard(pcb)

filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
print(f"refilled {b.Zones().size()} zones")

n_trk = n_via = 0
for t in b.GetTracks():
    t.SetLocked(True)
    if isinstance(t, pcbnew.PCB_VIA):
        n_via += 1
    else:
        n_trk += 1
b.Save(pcb)
print(f"locked {n_trk} escape segments + {n_via} escape vias")

try:
    pcbnew.ExportSpecctraDSN(b, dsn)
except TypeError:
    pcbnew.ExportSpecctraDSN(dsn)

text = open(dsn, encoding="utf-8", errors="replace").read()
n_prot = len(re.findall(r'\(type\s+protect\)', text))
n_layer = len(re.findall(r'\(layer\s+\S+\s*\n?\s*\(type signal\)', text))
print(f"wrote {dsn}  ({os.path.getsize(dsn)/1e6:.1f} MB)")
print(f"  signal layers declared : {n_layer}")
print(f"  protected (locked) items: {n_prot}"
      + ("" if n_prot else "   <-- lock did NOT survive the export;"
                           " Freerouting may rip the escapes up"))
