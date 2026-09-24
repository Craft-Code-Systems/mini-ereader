#!/usr/bin/env python3
"""Set the EPD_HV netclass clearance to 0.20 mm in ereader.kicad_pro.

0.20, not 0.30: the GDEY0426T82 FPC land itself spaces EPD_VGH / EPD_VGL /
EPD_VSL / EPD_VSH1 / EPD_VSH2 0.2 mm apart, so a 0.30 mm rule was never
achievable at the connector -- nothing the PCB does can beat the panel
vendor's own pad pitch. IPC-2221 table B4 (external conductors, permanent
polymer coating i.e. under solder mask) allows 0.13 mm at 31-50 V, so 0.20 mm
still has margin for the +-20 V rails. Bare-copper spacing (table B1) would
want 0.6 mm, but these runs are masked.

Leaving it at 0.30 makes DRC report 10 clearance errors, all of them the EPD
rail escapes at J2 -- and no escape geometry can fix that, because only a
0.10 mm trace fits at 0.30 mm clearance and the board minimum is 0.15 mm.

Run with KiCad CLOSED, or KiCad will write the old value back on exit.

USAGE:  python3 set_epdhv.py
"""
import json
import os
import shutil
import sys

PRO = sys.argv[1] if len(sys.argv) > 1 else "ereader.kicad_pro"
WANT = 0.2

if not os.path.exists(PRO):
    sys.exit("run this in the mini-ereader directory (no %s here)" % PRO)

with open(PRO, encoding="utf-8") as f:
    d = json.load(f)

classes = d.get("net_settings", {}).get("classes", [])
hit = [c for c in classes if c.get("name") == "EPD_HV"]
if not hit:
    sys.exit("no EPD_HV netclass in %s -- found: %s"
             % (PRO, ", ".join(repr(c.get("name")) for c in classes)))

was = hit[0].get("clearance")
if was == WANT:
    print("EPD_HV clearance is already %s mm -- nothing to do" % WANT)
    sys.exit(0)

shutil.copy2(PRO, PRO + ".bak-epdhv")
hit[0]["clearance"] = WANT
with open(PRO, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2)
    f.write("\n")
print("EPD_HV clearance %s -> %s mm" % (was, WANT))
print("backup: %s.bak-epdhv" % PRO)
print("now reopen the board in KiCad, press B to refill, and run DRC")
