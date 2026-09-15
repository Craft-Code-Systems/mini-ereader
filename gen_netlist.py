#!/usr/bin/env python3
"""SKiDL generator for the Mini E-Reader netlist.

WHY: `ereader-kicad.net` was hand-authored with IC pins named by *function*
(IN, SDA, SW...). KiCad binds netlist pins to footprint *pads* by name/number,
so those function names never match numbered pads -> the "pad X not found"
errors on import. This script instead builds the design from real *symbols*:
the symbol carries the pin-name -> pad-number map, so the generated netlist
references correct pad numbers and imports cleanly.

RUN (in your KiCad environment, where the symbol libraries live):
    pip install skidl
    python3 gen_netlist.py
It writes `ereader-kicad.net`, then in Pcbnew: File > Import > Netlist... >
match **by Reference**, "Delete extra footprints" UNCHECKED, Update PCB.

FIRST RUN WILL LIKELY REPORT ISSUES, and that is the intended loop:
  * "Can't find library ..." / "Can't find part ..."  -> a CFG symbol below is
    not installed yet (see CFG: add the SnapEDA symbol to ereader.kicad_sym,
    or point lib_id at your stock lib).
  * "... has no pin named X"  -> the symbol names that pin differently; fix the
    name here (or rename in the symbol). Paste the output back and I'll adjust.
Nothing is guessed: net membership is transcribed verbatim from
`ereader-connection-list.md`; pin identifiers are the datasheet function names.

SAFETY: verify diode anode/cathode and every IC power/EP pin against the real
symbol before you fabricate. See "KNOWN ITEMS TO VERIFY" at the bottom.
"""
import os, glob, re

# ---------------------------------------------------------------------------
# Point SKiDL at the installed KiCad symbol libraries. KiCad does NOT export
# KICAD*_SYMBOL_DIR to the shell, so a script run outside KiCad cannot find the
# stock libs -> "Can't open file: RF_Module". Auto-detect the symbols folder
# (override by exporting KICAD_SYMBOL_DIR), and add this project dir so the
# project library `ereader.kicad_sym` (U2-U5, J2, SW4) resolves too.
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
_ENV_KEYS = ("KICAD_SYMBOL_DIR", "KICAD10_SYMBOL_DIR", "KICAD9_SYMBOL_DIR",
             "KICAD8_SYMBOL_DIR", "KICAD7_SYMBOL_DIR", "KICAD6_SYMBOL_DIR")

def _find_symbols():
    for _k in _ENV_KEYS:
        _d = os.environ.get(_k)
        if _d and glob.glob(os.path.join(_d, "*.kicad_sym")):
            return _d
    for _c in ("/usr/share/kicad/symbols", "/usr/local/share/kicad/symbols",
               "/app/share/kicad/symbols",                      # flatpak
               os.path.expanduser("~/.local/share/kicad/symbols"),
               "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols",
               r"C:\Program Files\KiCad\10.0\share\kicad\symbols",
               r"C:\Program Files\KiCad\9.0\share\kicad\symbols",
               r"C:\Program Files\KiCad\8.0\share\kicad\symbols"):
        if glob.glob(os.path.join(_c, "*.kicad_sym")):
            return _c
    return None

_SYM = _find_symbols()
if _SYM:
    for _k in _ENV_KEYS:
        os.environ.setdefault(_k, _SYM)
else:
    print("WARNING: KiCad stock symbols not found. Export KICAD_SYMBOL_DIR to "
          "your KiCad 'symbols' folder (e.g. /usr/share/kicad/symbols) and re-run.")

from skidl import *
import skidl as _skidl

# Belt-and-suspenders: ensure the stock dir and this project dir are searched.
for _paths in getattr(_skidl, "lib_search_paths", {}).values():
    for _p in (HERE, _SYM):
        if _p and _p not in _paths:
            _paths.append(_p)

# ---------------------------------------------------------------------------
# CFG: symbols NOT in KiCad stock libraries. Install each (SnapEDA / vendor)
# into a project symbol lib `ereader.kicad_sym`, or point lib_id at a stock lib
# your KiCad has. The symbol MUST expose the pin names listed in "needs pins".
# Footprints follow ereader-footprints.md (corrected packages).
# ---------------------------------------------------------------------------
CFG = {
    # ref : (symbol lib_id,                         footprint)
    # SnapEDA symbols the user imported: BQ25628ERYKR, MAX17048G+T10, LM3630ATME,
    # TPS62840DLCR, DM3AT-SF-PEJM5. Symbol wants are the BASE name so the
    # resolver prefix-matches whatever suffix SnapEDA used. Footprints prefer a
    # matching .kicad_mod in ereader.pretty/ (auto), falling back to the string
    # here. ref : (symbol lib_id, fallback footprint)
    "U2": ("ereader:BQ25628E",  "ereader:WQFN-HR18__RYK_TEX"),  # BQ25628E (Ultra Librarian). pins used: VBUS SYS BAT GND SDA SCL *INT(11) *CE(14) TS TS_BIAS REGN PMID SW BTST. RYK HotRod WQFN-HR18: footprint is pads 1-18, NO exposed pad -> nothing to tie.
    "U3": ("ereader:MAX17048",  "ereader:SON50P200X150X100-8N"),  # MAX17048. pins: CELL VDD GND SDA SCL ~ALERT(5) + CTG/QSTRT/EP->GND. VDD is a SEPARATE supply pin from CELL.
    "U4": ("ereader:LM3630A",   "ereader:BGA12N50P4X3_196X146X62"),  # LM3630A DSBGA-12. pins: IN GND SDA SCL HWEN SW ILED1 ILED2 OVP (SEL/PWM->GND).
    "U5": ("ereader:TPS62840",  "ereader:SON50P200X200X80-9N"),  # TPS62840 VSON-HR-8 + thermal pad. pins: VIN SW VOS(8=output) GND EN MODE STOP VSET(5=Rset) EP(9=thermal->GND, added to symbol). No FB pin. (9N footprint has pad 9; symbol's own 8N property is overridden by SKiDL.)
    "J2": ("ereader:EPD_GDEY0426T82_FPC24", "Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal"),  # 24 pins named by function AND numbered to the panel FPC datasheet
    "J4": ("ereader:DM3AT", "ereader:HRS_DM3AT-SF-PEJM5"),  # DM3AT-SF-PEJM5 microSD. needs: CLK CMD DAT0 DAT3 VDD VSS
    "SW4": ("ereader:ALPS_SLLB5", "ereader:ALPS_SLLB5_Lever"),        # needs: CW CCW PUSH COM
}

# --- Resolve CFG symbols: auto-use a stock symbol if your KiCad already ships
#     one; otherwise it must live in ereader.kicad_sym. Report ALL missing at
#     once (instead of crashing on the first) so you get the full list. --------
def _symbol_index():
    idx = {}
    for _d in [p for p in (_SYM, HERE) if p]:
        for _f in sorted(glob.glob(os.path.join(_d, "*.kicad_sym"))):
            _lib = os.path.splitext(os.path.basename(_f))[0]
            try:
                _txt = open(_f, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for _m in re.finditer(r'\(symbol\s+"([^"]+)"', _txt):
                _nm = _m.group(1)
                if re.search(r'_\d+_\d+$', _nm):   # skip unit sub-symbols
                    continue
                idx.setdefault(_nm.lower(), f"{_lib}:{_nm}")
    return idx

_INDEX = _symbol_index()

def _footprint_index():
    idx = {}   # name.lower() -> "ereader:Name"  (filename of each .kicad_mod)
    for _f in sorted(glob.glob(os.path.join(HERE, "ereader.pretty", "*.kicad_mod"))):
        _nm = os.path.splitext(os.path.basename(_f))[0]
        idx.setdefault(_nm.lower(), f"ereader:{_nm}")
    return idx

_FPX = _footprint_index()

def _resolve_fp(ref):
    """Prefer a footprint in ereader.pretty whose filename starts with the part
    base name (e.g. bq25628e -> BQ25628ERYKR.kicad_mod); else the CFG fallback."""
    want = CFG[ref][0].split(":")[1].lower()
    cands = sorted({v for k, v in _FPX.items() if k.startswith(want)})
    return cands[0] if len(cands) == 1 else CFG[ref][1]

def _resolve(ref):
    want = CFG[ref][0].split(":")[1].lower()
    exact = _INDEX.get(want)
    if exact:
        return exact, []
    # A candidate must START WITH the wanted part name (e.g. bq25628e ->
    # bq25628erykr). We deliberately do NOT match the reverse direction, so a
    # short stock symbol like Device:L can't hijack "LM3630A".
    cands = sorted({v for k, v in _INDEX.items() if k.startswith(want)})
    if len(cands) == 1:          # unique variant match -> safe to auto-use
        return cands[0], []
    return None, cands           # 0 or ambiguous -> report for the user to pick

_resolved, _missing = {}, {}
for _ref in CFG:
    _id, _hints = _resolve(_ref)
    (_resolved if _id else _missing).__setitem__(_ref, _id or _hints)

if _missing:
    print("\n=== SYMBOLS STILL NEEDED (add to ereader.kicad_sym, or install a stock lib) ===")
    for _ref, _hints in _missing.items():
        want = CFG[_ref][0].split(":")[1]
        line = f"  {_ref}: '{want}'  ->  footprint {CFG[_ref][1]}"
        if _hints:
            line += f"   [candidate(s) already in your libs: {', '.join(_hints)}]"
        print(line)
    print("\nHow: download each from SnapEDA (free) into ereader.kicad_sym next to the")
    print("board, or draw it in KiCad's Symbol Editor. J2 needs the GDEY0426T82 FPC pin")
    print("numbering; SW4 pins are CW/COM/PUSH/CCW. See docs/schematic-capture.md.")
    print("If a candidate above IS the right part, set its lib_id in CFG and re-run.")
    raise SystemExit(1)

FP = {  # stock footprint shorthands
    "R":   "Resistor_SMD:R_0402_1005Metric",
    "C04": "Capacitor_SMD:C_0402_1005Metric",
    "C06": "Capacitor_SMD:C_0603_1608Metric",
    "C08": "Capacitor_SMD:C_0805_2012Metric",
    "L08": "Inductor_SMD:L_0805_2012Metric",
    "L12": "Inductor_SMD:L_1210_3225Metric",
    "SOD": "Diode_SMD:D_SOD-123",
    "SOT23": "Package_TO_SOT_SMD:SOT-23",
}

# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------
def R(ref, val):  return Part("Device", "R", ref=ref, value=val, footprint=FP["R"])
def C(ref, val, fp): return Part("Device", "C", ref=ref, value=val, footprint=FP[fp])
def L(ref, val, fp): return Part("Device", "L", ref=ref, value=val, footprint=FP[fp])
def DS(ref, val): return Part("Device", "D_Schottky", ref=ref, value=val, footprint=FP["SOD"])
def cfg(ref, val):
    _lib, _name = _resolved[ref].split(":", 1)
    return Part(_lib, _name, ref=ref, value=val, footprint=_resolve_fp(ref))

U1 = Part("RF_Module", "ESP32-S3-WROOM-1", ref="U1",
          value="ESP32-S3-WROOM-1-N16R8", footprint="RF_Module:ESP32-S3-WROOM-1")
U6 = Part("Power_Protection", "USBLC6-2SC6", ref="U6",
          value="USBLC6-2SC6", footprint="Package_TO_SOT_SMD:SOT-23-6")
U2, U3, U4, U5 = cfg("U2", "BQ25628E"), cfg("U3", "MAX17048"), cfg("U4", "LM3630A"), cfg("U5", "TPS62840")

J1 = Part("Connector", "USB_C_Receptacle_USB2.0_16P", ref="J1", value="USB-C-16P",
          footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12")
J2 = cfg("J2", "EPD_FPC_24P")
J3 = Part("Connector_Generic", "Conn_01x06", ref="J3", value="FL_FPC_6P",
          footprint="Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal")
J4 = cfg("J4", "microSD")
J5 = Part("Connector_Generic", "Conn_01x02", ref="J5", value="Battery_1S",
          footprint="Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal")

SW1 = Part("Switch", "SW_Push", ref="SW1", value="BTN_A", footprint="ereader:WE_WS-TASU_436351045816")
SW2 = Part("Switch", "SW_Push", ref="SW2", value="BTN_B", footprint="ereader:WE_WS-TASU_436351045816")
SW3 = Part("Switch", "SW_Push", ref="SW3", value="BTN_C", footprint="ereader:WE_WS-TASU_436351045816")
SW4 = cfg("SW4", "SLLB510200")
JP5 = Part("Jumper", "SolderJumper_2_Open", ref="JP5", value="BOOT", footprint="ereader:JumperPad_2P_P2.0mm")
JP6 = Part("Jumper", "SolderJumper_2_Open", ref="JP6", value="RESET", footprint="ereader:JumperPad_2P_P2.0mm")

QE = Part("Transistor_FET", "Q_NMOS_GSD", ref="QE", value="Si1308EDL", footprint=FP["SOT23"])
D1 = DS("D1", "Schottky_30V")
DE1, DE2, DE3 = DS("DE1", "MBR0530"), DS("DE2", "MBR0530"), DS("DE3", "MBR0530")

L1, LC, L2, LE = L("L1", "2.2uH", "L08"), L("LC", "1uH", "L08"), L("L2", "22uH", "L12"), L("LE", "47uH", "L12")

R1, R2 = R("R1", "5.1k"), R("R2", "5.1k")
R3, R4, R5, R6, R7 = R("R3", "100k"), R("R4", "100k"), R("R5", "100k"), R("R6", "100k"), R("R7", "100k")
R8, R9, R10, R11 = R("R8", "4.7k"), R("R9", "4.7k"), R("R10", "4.7k"), R("R11", "4.7k")
R12, R13, R14, R15 = R("R12", "10k"), R("R13", "10k"), R("R14", "10k"), R("R15", "10k")
RE1, RE2 = R("RE1", "2.2R"), R("RE2", "1M")

CEN = C("CEN", "1uF", "C04");  CV = C("CV", "1uF", "C06")
CS = C("CS", "10uF", "C08");   CB = C("CB", "10uF", "C08");  CBT = C("CBT", "47nF", "C04")
CI = C("CI", "10uF", "C08");   CO = C("CO", "10uF", "C08");  CF = C("CF", "2.2uF/25V", "C08")
CU1 = C("CU1", "22uF", "C08")
CU2, CU3, CU4, CU5 = C("CU2", "0.1uF", "C04"), C("CU3", "0.1uF", "C04"), C("CU4", "0.1uF", "C04"), C("CU5", "0.1uF", "C04")
CGA, CGB, C4I = C("CGA", "0.1uF", "C04"), C("CGB", "1uF", "C04"), C("C4I", "1uF", "C04")
CE1 = C("CE1", "4.7uF/25V", "C08"); CE2 = C("CE2", "4.7uF/25V", "C08"); CE3 = C("CE3", "4.7uF/25V", "C08")
CE4 = C("CE4", "4.7uF/25V", "C08"); CE5 = C("CE5", "4.7uF/25V", "C08"); CE6 = C("CE6", "4.7uF/25V", "C08")
CE7 = C("CE7", "1uF/25V", "C06"); CE8 = C("CE8", "1uF/25V", "C06"); CE9 = C("CE9", "1uF/25V", "C06")

# --- Support parts the VENDOR symbols revealed as needed (were absent from the
#     function-name connection list). Values are datasheet-typical; VERIFY. ------
CRG = C("CRG", "4.7uF", "C06")    # BQ25628E REGN internal-LDO bypass -> GND (TI-typical 4.7uF)
CPM = C("CPM", "1uF", "C04")      # BQ25628E PMID rail bypass -> GND  (TI-typical 1uF)
R16 = R("R16", "267k")  # TPS62840 VSET -> GND. 267k (E96,1%) = 3.3V out for TPS62840DLC per
                        # datasheet Table 1 (SLVSEC6D), column TPS62840DLC. Window 256.32k-277.68k.

# ---------------------------------------------------------------------------
# Nets  (verbatim from ereader-connection-list.md; U1 by datasheet pin number)
# ---------------------------------------------------------------------------
Net("+VBUS").connect(J1["A4"], J1["B4"], J1["A9"], J1["B9"], U2["VBUS"], U6["VBUS"], CV[1])
Net("+SYS").connect(U2["SYS"], LC[2], U5["VIN"], U5["EN"], CS[1], CI[1])  # U5.EN=always-on from the INPUT rail (see +3V3 note)
Net("+VBAT").connect(U2["BAT"], U3["CELL"], U3["VDD"], U4["IN"], L2[1], J5[1], CB[1], CGA[1], CGB[1], C4I[1])  # U3.VDD = fuel-gauge supply (2.5-4.5V), a pin SEPARATE from CELL sense
Net("+3V3").connect(
    U1[2], U5[8], L1[2], J2["VCI"], J2["VDDIO"], J4["VDD"],  # U5[8]=VOS (TPS62840 output sense). J2 VCI+VDDIO=3V3 (J2.VDD is an internal LDO -> decap only); J4.VDD=microSD 3V3
    R3[1], R4[1], R5[1], R8[1], R9[1], R10[1], R11[1], R12[1], R13[1],       # (R14 top moved to TS_BIAS, not +3V3)
    CO[1], CU1[1], CU2[1], CU3[1], CU4[1], CU5[1], LE[1], CE6[1], CE7[1],
    # NOTE: U5.EN moved to +SYS (was here on +3V3). Tying the buck's EN to its OWN
    # output deadlocks startup (output=0 -> EN low -> never starts); EN sits on +SYS.
)
Net("GND").connect(
    U1[1], U1[40], U1[41], U2["GND"], U3["GND"], U4["GND"], U5["GND"], U6["GND"],
    J1["A1"], J1["B1"], J1["A12"], J1["B12"], J1["SH"], J2["VSS"], J4["VSS"], J5[2],  # J1["SH"] = USB-C shell/shield
    SW1[2], SW2[2], SW3[2], SW4["COM"], JP5[2], JP6[2],
    U4["SEL"], U4["PWM"],   # SEL->GND = I2C addr 0x36 (design); PWM unused (I2C dimming)
    U3["CTG"], U3["QSTRT"], U3["EP"],   # MAX17048: CTG (exposed-pad label), QSTRT (unused quick-start), EP thermal pad -> GND (datasheet)
    U5["MODE"], U5["STOP"], U5["EP"],   # TPS62840: MODE low=Power-Save (auto PFM/PWM); STOP low=normal switching (high halts); EP=pad 9 thermal pad -> GND

    J4["P1"], J4["P2"], J4["P3"], J4["P4"],   # microSD shell/shield tabs -> GND (ESD/EMC)
    R1[2], R2[2], R6[2], R7[2], R15[2],
    CEN[2], CV[2], CS[2], CB[2], CI[2], CO[2], CF[2],
    CU1[2], CU2[2], CU3[2], CU4[2], CU5[2], CGA[2], CGB[2], C4I[2],
    RE1[2], RE2[2], CE1[2], CE2[2], CE3[2], CE4[2], CE5[2], CE6[2], CE7[2], CE8[2], CE9[2],
    CRG[2], CPM[2], R16[2],   # BQ25628E REGN/PMID bypass returns + TPS62840 VSET resistor return
    J2["BS1"],
)
Net("I2C0_SDA").connect(U1[10], U2["SDA"], U3["SDA"], R8[2])
Net("I2C0_SCL").connect(U1[11], U2["SCL"], U3["SCL"], R9[2])
Net("I2C1_SDA").connect(U1[9], U4["SDA"], R10[2])
Net("I2C1_SCL").connect(U1[31], U4["SCL"], R11[2])
Net("EPD_SCLK").connect(U1[20], J2["SCLK"])
Net("EPD_MOSI").connect(U1[19], J2["SDA"])
Net("EPD_CS").connect(U1[18], J2["CS"], R4[2])
Net("EPD_DC").connect(U1[17], J2["DC"])
Net("EPD_RST").connect(U1[12], J2["RST"])
Net("EPD_BUSY").connect(U1[7], J2["BUSY"])
Net("SD_SCK").connect(U1[34], J4["CLK"])
Net("SD_MOSI").connect(U1[35], J4["CMD"])
Net("SD_MISO").connect(U1[33], J4["DAT0"])
Net("SD_CS").connect(U1[32], J4[2], R5[2])   # J4[2] = "CD/DAT3" (microSD CS in SPI mode); by number (name has a "/")
Net("BTN_A").connect(U1[4], SW1[1])
Net("BTN_B").connect(U1[5], SW2[1])
Net("BTN_C").connect(U1[6], SW3[1])
Net("LEV_CW").connect(U1[39], SW4["CW"])
Net("LEV_CCW").connect(U1[38], SW4["CCW"])
Net("LEV_PUSH").connect(U1[8], SW4["PUSH"])
Net("CHG_INT").connect(U1[24], U2[11], R12[2])   # U2[11] = "*INT" (open-drain, active-low charger IRQ); by number (name has a "*")
Net("GAUGE_ALRT").connect(U1[25], U3[5], R13[2])  # U3[5] = "~{ALERT}" (MAX17048 open-drain alert); by number (name has "~{}")
Net("FL_HWEN").connect(U1[23], U4["HWEN"], R6[1])
Net("CHG_CE").connect(U1[22], U2[14], R7[1])   # U2[14] = "*CE" (active-low charge-enable: R7 pulls low = charge-on); by number
Net("IO0_BOOT").connect(U1[27], JP5[1])
Net("EN").connect(U1[3], JP6[1], R3[2], CEN[1])
Net("USB_DP").connect(U1[14], U6[1], U6[6], J1["A6"], J1["B6"])   # USBLC6 I/O1 = pads 1 & 6 (same internal node; route-through)
Net("USB_DM").connect(U1[13], U6[3], U6[4], J1["A7"], J1["B7"])   # USBLC6 I/O2 = pads 3 & 4
Net("CC1").connect(J1["A5"], R1[1])
Net("CC2").connect(J1["B5"], R2[1])
Net("CHG_SW").connect(U2["SW"], LC[1], CBT[1])
Net("CHG_BTST").connect(U2["BTST"], CBT[2])
Net("TS").connect(U2["TS"], R14[2], R15[1])
Net("TS_BIAS").connect(U2["TS_BIAS"], R14[1])   # TS divider biased from the regulated TS_BIAS pin, NOT +3V3, so thresholds track the reference
Net("REGN").connect(U2["REGN"], CRG[1])         # BQ25628E internal-LDO output: bypass cap only
Net("PMID").connect(U2["PMID"], CPM[1])         # BQ25628E PMID rail: bypass cap only
Net("VSET").connect(U5["VSET"], R16[1])         # TPS62840 output-voltage select: R16=267k -> 3.3V (datasheet Table 1)
Net("BUCK_SW").connect(U5["SW"], L1[1])
Net("FL_SW").connect(U4["SW"], L2[2], D1["A"])
Net("FL_OUT").connect(D1["K"], CF[1], J3[1], J3[5], U4["OVP"])  # OVP senses the boost output (datasheet)
Net("FL_COOL_K").connect(J3[2], U4["ILED1"])  # datasheet ball D3 = ILED1 (was "LED1")
Net("FL_WARM_K").connect(J3[6], U4["ILED2"])  # datasheet ball D2 = ILED2 (was "LED2")
# EPD external DC-DC (topology per pcb-design SS6; VERIFY 1:1 vs Good Display ref)
Net("EPD_SW").connect(LE[2], QE["D"], DE1["A"], DE2["A"])
Net("EPD_GDR").connect(J2["GDR"], QE["G"], RE2[1])
Net("EPD_RESE").connect(J2["RESE"], QE["S"], RE1[1])
Net("EPD_VGH").connect(J2["VGH"], DE1["K"], CE5[1])
Net("EPD_PREVGL").connect(DE2["K"], DE3["A"])
Net("EPD_VGL").connect(J2["VGL"], DE3["K"], CE4[1])
Net("EPD_VSH1").connect(J2["VSH1"], CE1[1])
Net("EPD_VSH2").connect(J2["VSH2"], CE2[1])
Net("EPD_VSL").connect(J2["VSL"], CE3[1])
Net("EPD_VCOM").connect(J2["VCOM"], CE9[1])
Net("EPD_VDD").connect(J2["VDD"], CE8[1])   # SSD1677 core LDO output: decap to GND only, NOT driven from +3V3

# ---------------------------------------------------------------------------
# KNOWN ITEMS TO VERIFY before fabrication (do NOT skip):
#
#  *** RESOLVED (from the datasheet) ***
#  - R16 (TPS62840 VSET) = 267k, E96 1%. Sets 3.3V out for the TPS62840DLC per
#    datasheet Table 1 (SLVSEC6D), TPS62840DLC column (window 256.32k-277.68k).
#    VOS (pin 8) senses the output; this part has no FB pin. Populate exactly 267k.
#
#  *** CONFIRM POLARITY / VALUES (I wired the datasheet-typical default) ***
#  - U5.STOP -> GND (normal switching). STOP HIGH halts switching for a noise-free
#    measurement; confirm your build wants continuous operation (GND).
#  - U5.MODE -> GND (Power-Save, auto PFM/PWM). Tie HIGH for forced-PWM if desired.
#  - U5.EN -> +SYS (input rail), NOT +3V3. Corrected: EN on the buck's own output
#    can never start it. Confirm you don't instead want a GPIO to gate this rail.
#  - CRG 4.7uF (REGN) and CPM 1uF (PMID): TI-typical bypass values; confirm vs the
#    BQ25628E datasheet app circuit.
#  - U2.TS divider (R14/R15): now biased from TS_BIAS. If you fit a real NTC instead
#    of a fixed divider, wire NTC per the datasheet TS window.
#
#  *** STILL OPEN — decide before fab ***
#  - U2.ILIM (pin 4): input-current-limit set resistor to GND (+ ~1.2k/330nF RC per
#    datasheet) is NOT fitted. Left open the limit falls back to the I2C register
#    default. Add RILIM sized to your desired input current if you want a HW limit.
#  - U2.*PG (3), STAT (10), *QON (7): intentionally left NC (open-drain / internal
#    pull-up). Add a 10k pull-up + LED/GPIO only if you want charge status/IRQ.
#  - THERMAL PADS: resolved. U5 (TPS62840) now has an EP pin (pad 9) added to its
#    symbol and tied to GND here. U3 (MAX17048) EP is tied to GND. U2 (BQ25628E) is
#    the RYK *HotRod* WQFN-HR18 - its footprint has NO exposed pad (pads 1-18 only,
#    ground/thermal via the pin array), so there is nothing to tie. Confirm your
#    fab's copper/thermal relief on the multiple GND pins for the charger.
#  - Diodes use pin names A/K; confirm anode/cathode vs the SOD-123 pads.
#  - J2 (EPD FPC) pin numbers + EPD DC-DC diode/charge-pump topology copied 1:1 from
#    the Good Display GDEY0426T82-FL01C reference (rail caps >=25V).
# ---------------------------------------------------------------------------
ERC()
generate_netlist(file_="ereader-kicad.net")
