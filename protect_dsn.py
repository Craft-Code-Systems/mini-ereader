#!/usr/bin/env python3
"""Mark every wire and via in ereader.dsn as `(type protect)`.

KiCad 10 does not translate a locked track into Specctra's protect type on
export -- export_dsn.py locks 112 items and the DSN comes back with zero
protected ones. Freerouting treats an unprotected wire as its own work and
will happily rip it up, which would undo the pad escapes and put the board
back where it started.

Specctra wire/via types: normal | route | protect | fix | shove_fixed.
Freerouting leaves `protect` and `fix` alone. This walks the (wiring ...)
block with a real s-expression scanner -- quoted strings can and do contain
parentheses, so regex is not safe here -- and sets the type on each direct
child, adding the clause when there isn't one.

Refuses to write anything if the file isn't shaped the way it expects, and
prints the first wire and via verbatim so you can see what it acted on.

USAGE:  python3 protect_dsn.py [ereader.dsn] [type]   # after export_dsn.py
        type defaults to protect; use fix if Freerouting still reroutes them
"""
import os
import re
import shutil
import sys

DSN = sys.argv[1] if len(sys.argv) > 1 else "ereader.dsn"

# Freerouting maps protect/fix/shove_fixed onto its fixed states and leaves
# those traces alone; normal and route are fair game for rip-up. protect is
# the right level -- it is what a user-fixed trace is. If Freerouting still
# reroutes over the escapes, re-run with `fix`, which is the strongest.
TYPES = ("protect", "fix", "shove_fixed", "normal", "route")
WANT = sys.argv[2] if len(sys.argv) > 2 else "protect"
if WANT not in TYPES:
    sys.exit("type must be one of: %s" % ", ".join(TYPES))


def neutralize(s):
    """Blank the (string_quote ") clause.

    Specctra declares its own quote character with a literal quote, so a
    string-aware scan that starts at the top of the file opens a string there
    that never closes. Blanking it with the same number of spaces keeps every
    byte offset identical, so positions found in the neutralized copy apply
    unchanged to the real text.
    """
    return re.sub(r"\(string_quote\s+\S\s*\)",
                  lambda m: " " * len(m.group(0)), s)


def skip_string(s, i):
    """Index just past the string literal starting at s[i] == '\"'."""
    i += 1
    while i < len(s):
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == '"':
            return i + 1
        i += 1
    raise ValueError("unterminated string at %d" % i)


def match_paren(s, i):
    """Index of the ')' matching the '(' at s[i], strings respected."""
    depth = 0
    while i < len(s):
        c = s[i]
        if c == '"':
            i = skip_string(s, i)
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("unbalanced parens")


def name_at(s, i):
    """The keyword right after the '(' at s[i]."""
    m = re.match(r"\(\s*([^\s()\"]+)", s[i:])
    return m.group(1) if m else ""


def children(s, lo, hi):
    """(name, start, end) for each direct child element within s[lo:hi]."""
    out = []
    i = lo
    while i < hi:
        c = s[i]
        if c == '"':
            i = skip_string(s, i)
            continue
        if c == "(":
            j = match_paren(s, i)
            out.append((name_at(s, i), i, j))
            i = j + 1
            continue
        i += 1
    return out


def main():
    if not os.path.exists(DSN):
        sys.exit("no %s here -- run export_dsn.py first" % DSN)
    s = open(DSN, encoding="utf-8", errors="replace").read()
    scan = neutralize(s)
    assert len(scan) == len(s)

    top = children(scan, 0, len(scan))
    pcb = [t for t in top if t[0] == "pcb"]
    if not pcb:
        sys.exit("no top-level (pcb ...) -- is %s a Specctra DSN?" % DSN)
    _, plo, phi = pcb[0]

    wiring = [t for t in children(scan, plo + 1, phi) if t[0] == "wiring"]
    if not wiring:
        sys.exit("no (wiring ...) block in %s -- nothing was exported to protect" % DSN)
    _, wlo, whi = wiring[0]

    items = [t for t in children(scan, wlo + 1, whi) if t[0] in ("wire", "via")]
    if not items:
        sys.exit("(wiring ...) is empty -- the escapes did not reach the DSN")

    n = {"wire": 0, "via": 0}
    for t in items:
        n[t[0]] += 1
    print("found %d wire + %d via in (wiring ...)" % (n["wire"], n["via"]))
    for kind in ("wire", "via"):
        first = next((t for t in items if t[0] == kind), None)
        if first:
            body = s[first[1]:first[2] + 1]
            print("  first %s, as exported:" % kind)
            for line in body.splitlines()[:6]:
                print("    " + line.strip())

    # rewrite back-to-front so earlier offsets stay valid
    added = retyped = 0
    out = s
    for _, lo, hi in sorted(items, key=lambda t: -t[1]):
        kids = children(neutralize(out), lo + 1, hi)
        ty = [k for k in kids if k[0] == "type"]
        if ty:
            _, tlo, thi = ty[0]
            if out[tlo:thi + 1] != "(type %s)" % WANT:
                out = out[:tlo] + "(type %s)" % WANT + out[thi + 1:]
                retyped += 1
        else:
            out = out[:hi] + "(type %s)" % WANT + out[hi:]
            added += 1

    if added + retyped == 0:
        print("every wire and via was already (type %s) -- nothing to do" % WANT)
        return

    shutil.copy2(DSN, DSN + ".bak-protect")
    open(DSN, "w", encoding="utf-8").write(out)

    vscan = neutralize(out)
    check = children(vscan, 0, len(vscan))
    _, plo, phi = [t for t in check if t[0] == "pcb"][0]
    _, wlo, whi = [t for t in children(vscan, plo + 1, phi) if t[0] == "wiring"][0]
    good = 0
    for t in children(vscan, wlo + 1, whi):
        if t[0] not in ("wire", "via"):
            continue
        if any(out[k[1]:k[2] + 1] == "(type %s)" % WANT
               for k in children(vscan, t[1] + 1, t[2]) if k[0] == "type"):
            good += 1
    print("added %d type clauses, rewrote %d" % (added, retyped))
    print("verified: %d/%d wires+vias are (type %s)" % (good, len(items), WANT))
    print("backup: %s.bak-protect" % DSN)
    if good != len(items):
        sys.exit("*** not every item took the change -- do not route this file ***")


main()
