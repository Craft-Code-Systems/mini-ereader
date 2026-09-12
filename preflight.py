#!/usr/bin/env python3
"""Fabrication preflight: is ereader.kicad_pcb in sync with ereader-kicad.net?

kicad-cli's DRC checks a board's *internal* connectivity only — it never
compares the board against the netlist. So a board that is simply missing
components (e.g. routed before "Update PCB from Netlist" was run) passes DRC
with zero errors while silently omitting whole subsystems. That exact gap let
a routed board reach main without the EPD external DC-DC block on it.

This script closes that gap: every component in the netlist MUST exist on the
board. Board-only parts that legitimately have no netlist entry (fiducials,
mounting holes, and unannotated placeholders) are allowed via ALLOW_BOARD_ONLY.

Exit 0 = in sync (safe to fab). Exit 1 = out of sync (do NOT fab).
Run standalone (`python3 preflight.py`) or import `check()` from fab.py.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NET = os.path.join(HERE, "ereader-kicad.net")
PCB = os.path.join(HERE, "ereader.kicad_pcb")

# Board-only references that are expected to have no netlist component.
ALLOW_BOARD_ONLY = re.compile(r"^(FID\d+|H\d+|REF\*\*|G\*\*+|\*\*)$")


def netlist_refs(path):
    s = open(path, encoding="utf-8").read()
    return set(re.findall(r'\(comp\s+\(ref\s+"([^"]+)"', s))


def board_refs(path):
    s = open(path, encoding="utf-8").read()
    # New KiCad format stores the ref as a property; older format as fp_text.
    refs = set(re.findall(r'\(property\s+"Reference"\s+"([^"]+)"', s))
    refs |= set(re.findall(r'fp_text\s+reference\s+"([^"]+)"', s))
    return refs


def check():
    net = netlist_refs(NET)
    board = board_refs(PCB)
    missing = sorted(net - board)                       # in netlist, not on board
    extra = sorted(r for r in (board - net)             # on board, not in netlist
                   if not ALLOW_BOARD_ONLY.match(r))

    print(f"preflight: netlist components = {len(net)}, board footprints = {len(board)}")
    ok = True
    if missing:
        ok = False
        print(f"\nERROR: {len(missing)} netlist component(s) are NOT on the board:")
        print("  " + ", ".join(missing))
        print("  -> In KiCad: Tools > Update PCB from Netlist (F8), then place + route them.")
    if extra:
        # Unexpected board-only parts: warn, do not fail (may be intentional).
        print(f"\nWARNING: {len(extra)} board footprint(s) have no netlist entry:")
        print("  " + ", ".join(extra))
    if ok:
        print("\nOK: every netlist component is present on the board.")
    return ok


if __name__ == "__main__":
    sys.exit(0 if check() else 1)
