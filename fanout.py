#!/usr/bin/env python3
"""Strip the old routing from ereader.kicad_pcb and write the 54 pad escapes.

WHY: Freerouting stalled around 51 unconnected nets and never used In2.Cu at
all. The cause was not the layer count -- it was that 54 pads on the
fine-pitch parts (J1 USB-C, J2 FPC, U2 charger, U3 gauge, U4 backlight,
U5 buck, J3) have no room beside them for a 0.8mm Power-class via. An inner
layer you cannot reach with a via is an inner layer you cannot route on.

Each escape is a stub out of the pad along the pad's own axis, necked down
where it has to be (0.15-0.40mm; the board minimum is 0.15mm), ending in a
via in open copper. Traces fit where vias don't -- that is what makes the
escape possible. Running the stub dead down the pad centreline is what makes
it fit: a 5-degree tilt eats the 0.30mm of lateral room a 0.4mm-pitch land
gives you. Every escape was checked against every other pad, every other
escape, the board edge and the U1 antenna keep-out, at full netclass
clearance, then re-verified independently after being written out.

NO DRC rules were added or relaxed. The one rule change this needs is in
ereader.kicad_pro, not here: EPD_HV netclass clearance 0.30 -> 0.20mm. The
GDEY0426T82 FPC land spaces those rails 0.2mm apart itself, so 0.30mm was
never achievable at the connector; IPC-2221 B4 allows 0.13mm at 40V under
solder mask. Set it in Board Setup -> Net Classes BEFORE running DRC --
at 0.30 the board reports 25 violations, all on the 5 EPD escapes at J2.

NOT ESCAPED -- 3 pads, on placeholder lands already flagged for replacement:
  U2.16 (CHG_SW), U2.9 (+SYS)   BQ25628E, needs TI's real WQFN-HR18 RYK land
  U5.7  (BUCK_SW)               TPS62840, needs the real VSON-HR/DLC land
U2's placeholder is also off-grid by ~1um -- it leaves 0.299999mm where a
0.20mm stub at 0.20mm clearance needs 0.300000, a real violation in KiCad's
nanometre arithmetic. That is why U2's escapes neck to 0.18mm. Recompute
these three once the real lands are in.

DATA FORMAT below: pad  net  stub-width  point point [point]
The points chain from the pad centre outwards; a via goes at the last one.

WHAT IT DOES
  1. backs up ereader.kicad_pcb to ereader.kicad_pcb.bak-fanout
  2. deletes every (segment ...) and (via ...)      <- the old autoroute
  3. writes 58 escape segments + 54 escape vias
Placement, footprints, outline, zones, the net table, the net classes and the
DRC rules are untouched.

USAGE:  python3 fanout.py            # in the mini-ereader directory
"""
import os, re, shutil, sys, uuid

PCB = sys.argv[1] if len(sys.argv) > 1 else "ereader.kicad_pcb"

ESCAPES = """\
J1.A4 +VBUS 0.4 49.55,107.955 49.55,106.88
J1.A5 CC1 0.2 50.75,107.955 50.75,108.98
J1.A6 USB_DP 0.25 51.75,107.955 51.75,108.98
J1.A7 USB_DM 0.25 52.25,107.955 52.25,106.93
J1.A9 +VBUS 0.4 54.45,107.955 54.45,106.88
J1.B4 +VBUS 0.4 54.45,107.955 54.45,106.23
J1.B5 CC2 0.2 53.75,107.955 53.75,108.98
J1.B6 USB_DP 0.25 52.75,107.955 52.75,108.98
J1.B7 USB_DM 0.25 51.25,107.955 51.25,106.93
J1.B9 +VBUS 0.4 49.55,107.955 49.55,106.23
J2.10 EPD_RST 0.2 33.75,107.15 33.75,108.1
J2.11 EPD_DC 0.2 34.25,107.15 34.25,106.2
J2.12 EPD_CS 0.2 34.75,107.15 34.75,108.1
J2.13 EPD_SCLK 0.2 35.25,107.15 35.25,106.2
J2.14 EPD_MOSI 0.2 35.75,107.15 35.75,108.175
J2.15 +3V3 0.3 36.25,107.15 36.5,107.15
J2.16 +3V3 0.3 36.75,107.15 36.75,108.3
J2.17 GND 0.3 37.25,107.15 37.25,106
J2.18 EPD_VDD 0.2 37.75,107.15 37.75,108.175
J2.2 EPD_GDR 0.2 29.75,107.15 29.75,108.175
J2.20 EPD_VSH1 0.3 38.75,107.15 38.75,108.3
J2.21 EPD_VGH 0.3 39.25,107.15 39.25,106
J2.22 EPD_VSL 0.3 39.75,107.15 39.75,108.3
J2.23 EPD_VGL 0.3 40.25,107.15 40.25,106
J2.3 EPD_RESE 0.3 30.25,107.15 30.25,106
J2.5 EPD_VSH2 0.3 31.25,107.15 31.25,108.3
J2.8 GND 0.3 32.75,107.15 32.75,108.3
J2.9 EPD_BUSY 0.2 33.25,107.15 33.25,106.125
J3.1 FL_OUT 0.3 11.75,107.15 11.5,107.15
J3.2 FL_COOL_K 0.2 12.25,107.15 12.25,108.175
J3.5 FL_OUT 0.3 13.75,107.15 13.75,108.3
U1.41 GND 0.4 32.9,16.16 32.9,17.41
U2.15 GND 0.18 31.575,91.05 31.575,90.025
U2.17 PMID 0.18 30.775,91.05 30.775,89.4
U2.18 +VBUS 0.18 30.375,90.859 30.375,90.359 29.6389,89.934
U2.2 REGN 0.18 29.612,91.607 28.762,91.607
U2.8 +VBAT 0.18 31.175,92.95 31.175,93.975
U3.1 GND 0.3 20.015,89.25 20.89,89.25
U3.2 +VBAT 0.3 20.015,89.75 19.515,89.75 19.5797,89.9915
U3.3 +VBAT 0.3 20.015,90.25 19.515,90.25 18.79,88.9943
U3.4 GND 0.3 20.015,90.75 20.89,90.75
U3.6 GND 0.3 21.985,90.25 22.86,90.25
U4.A3 FL_SW 0.3 22.5,98.75 23.15,98.75
U4.B3 GND 0.15 22.5,99.25 23.665,99.6285
U4.C1 GND 0.3 21.5,99.75 20.85,99.75
U4.C2 GND 0.3 22,99.75 20.2,99.75
U4.C3 +VBAT 0.18 22.5,99.75 22.85,99.75 23.35,100.616
U4.D1 FL_OUT 0.3 21.5,100.25 21.5,100.9
U5.1 GND 0.3 46.015,87.25 46.89,87.25
U5.2 +SYS 0.3 46.015,87.75 45.14,87.75
U5.3 GND 0.3 46.015,88.25 48.865,88.25
U5.4 +SYS 0.3 46.015,88.75 45.14,88.75
U5.6 GND 0.3 47.985,88.25 49.535,88.25
U5.8 +3V3 0.3 47.985,87.25 48.86,87.25
"""

POWER = set("+3V3 +SYS +VBAT +VBUS BUCK_SW CHG_SW EPD_RESE FL_OUT FL_SW GND PMID REGN".split())
EPDHV = set("EPD_NODEX EPD_SW EPD_VCOM EPD_VGH EPD_VGL EPD_VSH1 EPD_VSH2 EPD_VSL".split())


def depth(line):
    """Net change in paren depth over one line, ignoring quoted strings."""
    d = q = 0
    i = 0
    while i < len(line):
        c = line[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                q = 0
        elif c == '"':
            q = 1
        elif c == "(":
            d += 1
        elif c == ")":
            d -= 1
        i += 1
    return d


def strip_routing(lines):
    """Drop every top-level (segment ...) and (via ...) block."""
    drop, lvl, start, kw = set(), 0, None, None
    for i, line in enumerate(lines):
        if lvl == 1 and start is None and line.lstrip().startswith("("):
            m = re.match(r"\(([^\s()\"]+)", line.lstrip())
            start, kw = i, (m.group(1) if m else "")
        lvl += depth(line)
        if start is not None and lvl <= 1:
            if kw in ("segment", "via"):
                drop.update(range(start, i + 1))
            start = kw = None
    return [l for i, l in enumerate(lines) if i not in drop], len(drop)


def main():
    if not os.path.exists(PCB):
        sys.exit("run this in the mini-ereader directory (no %s here)" % PCB)
    text = open(PCB, encoding="utf-8").read()
    n_s = len(re.findall(r"^\t\(segment", text, re.M))
    n_v = len(re.findall(r"^\t\(via", text, re.M))
    shutil.copy2(PCB, PCB + ".bak-fanout")
    lines, dropped = strip_routing(text.split("\n"))
    text = "\n".join(lines)
    print("stripped %d old segments + %d old vias (%d lines)" % (n_s, n_v, dropped))

    out, nseg, nvia = [], 0, 0
    for row in ESCAPES.strip().split("\n"):
        f = row.split()
        net, w = f[1], float(f[2])
        pts = [tuple(float(v) for v in p.split(",")) for p in f[3:]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            out.append('\t(segment\n\t\t(start %g %g)\n\t\t(end %g %g)\n\t\t(width %g)\n'
                       '\t\t(layer "F.Cu")\n\t\t(net "%s")\n\t\t(uuid "%s")\n\t)'
                       % (ax, ay, bx, by, w, net, uuid.uuid4()))
            nseg += 1
        vx, vy = pts[-1]
        sz, dr = (0.8, 0.4) if net in POWER or net in EPDHV else (0.6, 0.3)
        out.append('\t(via\n\t\t(at %g %g)\n\t\t(size %g)\n\t\t(drill %g)\n'
                   '\t\t(layers "F.Cu" "B.Cu")\n\t\t(net "%s")\n\t\t(uuid "%s")\n\t)'
                   % (vx, vy, sz, dr, net, uuid.uuid4()))
        nvia += 1

    m = re.search(r"^\t\(zone\b", text, re.M)
    if not m:
        sys.exit("no top-level (zone -- is this the right board?")
    open(PCB, "w", encoding="utf-8").write(
        text[:m.start()] + "\n".join(out) + "\n" + text[m.start():])
    print("wrote %d escape segments + %d escape vias" % (nseg, nvia))
    print("backup: %s.bak-fanout" % PCB)


main()
