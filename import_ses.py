#!/usr/bin/env python3
"""Import ereader.ses back onto the board, and report what actually landed.

Worth scripting rather than doing in the GUI: the last 4-layer attempt
produced a .ses that used In1.Cu and In2.Cu six times each, and after import
the board had ZERO inner-layer segments. The GUI import reports success
either way. This counts segments per layer so a silent drop is visible
immediately.

It refuses outright if the .ses is older than the .dsn: a Freerouting run
that fails leaves the previous session file in place, and importing that
lays a stale route over the board without a word of complaint.

It also checks that the pad escapes survived the round trip. If Freerouting
ripped them out despite the fixed type, the locked count drops and you see
it here rather than three steps later in DRC.

Run with KiCad's Python (the one that can `import pcbnew`), board closed.

USAGE:  python3 import_ses.py [ereader.kicad_pcb] [ereader.ses]
"""
import os
import re
import sys
from collections import Counter

pcb = sys.argv[1] if len(sys.argv) > 1 else "ereader.kicad_pcb"
ses = sys.argv[2] if len(sys.argv) > 2 else "ereader.ses"

for f in (pcb, ses):
    if not os.path.exists(f):
        sys.exit("no %s here -- run this in the mini-ereader directory" % f)

# A failed Freerouting run leaves the PREVIOUS .ses sitting there, and
# importing it silently lays a stale route over the board. That already
# happened once: the jar was missing, java exited, and this script cheerfully
# imported a session file from the run before the escapes existed.
dsn = os.path.splitext(ses)[0] + ".dsn"
if os.path.exists(dsn) and os.path.getmtime(ses) < os.path.getmtime(dsn):
    import datetime

    def when(p):
        return datetime.datetime.fromtimestamp(
            os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S")

    sys.exit("refusing to import a stale session file:\n"
             "  %s  %s\n  %s  %s\n"
             "The .ses predates the .dsn, so it is from an earlier run --\n"
             "Freerouting most likely failed or never started. Re-route, then\n"
             "run this again." % (ses, when(ses), dsn, when(dsn)))

import pcbnew  # noqa: E402  -- after the cheap checks above, which need no KiCad

# what the .ses itself claims, before KiCad gets a say
text = open(ses, encoding="utf-8", errors="replace").read()
claimed = Counter(re.findall(r"\(path\s+(\S+)\s", text))
print("layers used by %s:" % ses)
for lay, n in sorted(claimed.items(), key=lambda kv: -kv[1]):
    print("  %-10s %d path(s)" % (lay, n))
if not claimed:
    print("  (none -- the session file routed nothing)")

b = pcbnew.LoadBoard(pcb)
before = Counter()
for t in b.GetTracks():
    before[b.GetLayerName(t.GetLayer())] += 1
print("board before import: %d tracks+vias" % sum(before.values()))

try:
    pcbnew.ImportSpecctraSES(b, ses)
except TypeError:
    pcbnew.ImportSpecctraSES(ses)
b.Save(pcb)

after = Counter()
vias = 0
locked = 0
for t in b.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA):
        vias += 1
    else:
        after[b.GetLayerName(t.GetLayer())] += 1
    if t.IsLocked():
        locked += 1

print("board after import:")
for lay in ("F.Cu", "In1.Cu", "In2.Cu", "B.Cu"):
    print("  %-8s %d segment(s)%s"
          % (lay, after.get(lay, 0),
             "   <-- nothing routed here" if not after.get(lay, 0) else ""))
print("  vias     %d" % vias)
print("  locked   %d  (the escapes: expect 112 if they survived)" % locked)

if locked < 112:
    print()
    print("*** %d of the 112 locked escape items are gone -- Freerouting rewrote"
          % (112 - locked))
    print("    them despite the Specctra fixed type. Check the .dsn really")
    print("    says (type fix) on all 112:  python3 protect_dsn.py %s fix" % dsn)
