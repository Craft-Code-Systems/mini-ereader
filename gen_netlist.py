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
    "U2": ("ereader:BQ25628E",  "ereader:BQ25628E_WQFN18_2.5x3.0"),  # 18-pin WQFN (RYK). needs pins: VBUS SYS BAT GND SDA SCL INT CE TS SW BTST (+ EP->GND)
    "U3": ("ereader:MAX17048",  "Package_DFN_QFN:DFN-8-1EP_2x2mm_P0.5mm_EP0.9x1.5mm"),  # needs: CELL GND SDA SCL ALRT
    "U4": ("ereader:LM3630A",   "ereader:LM3630A_DSBGA12"),          # needs: IN GND SDA SCL HWEN SW LED1 LED2 (OVP per datasheet)
    "U5": ("ereader:TPS62840",  "ereader:TPS62840_VSON8_2x2"),       # VSON-HR (DLC). needs: VIN SW VOUT GND EN FB (MODE per variant)
    "J2": ("ereader:EPD_GDEY0426T82_FPC24", "Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal"),  # 24 pins named by function AND numbered to the panel FPC datasheet
    "J4": ("Connector:microSD_HC", "Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5"),  # if not stock, use ereader: symbol. needs: CLK CMD DAT0 DAT3 VDD VSS
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

def _resolve(ref):
    want = CFG[ref][0].split(":")[1]
    exact = _INDEX.get(want.lower())
    if exact:
        return exact, []
    hints = sorted({v for k, v in _INDEX.items()
                    if k.startswith(want.lower()) or want.lower().startswith(k)})
    return None, hints

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
    return Part(_lib, _name, ref=ref, value=val, footprint=CFG[ref][1])

U1 = Part("RF_Module", "ESP32-S3-WROOM-1", ref="U1",
          value="ESP32-S3-WROOM-1-N16R8", footprint="RF_Module:ESP32-S3-WROOM-1")
U6 = Part("Power_Protection", "USBLC6-2SC6", ref="U6",
          value="USBLC6-2SC6", footprint="Package_TO_SOT_SMD:SOT-23-6")
U2, U3, U4, U5 = cfg("U2", "BQ25628E"), cfg("U3", "MAX17048"), cfg("U4", "LM3630A"), cfg("U5", "TPS62840")

J1 = Part("Connector", "USB_C_Receptacle_USB2.0", ref="J1", value="USB-C-16P",
          footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12")
J2 = cfg("J2", "EPD_FPC_24P")
J3 = Part("Connector", "Conn_01x06", ref="J3", value="FL_FPC_6P",
          footprint="Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal")
J4 = cfg("J4", "microSD")
J5 = Part("Connector", "Conn_01x02", ref="J5", value="Battery_1S",
          footprint="Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal")

SW1 = Part("Switch", "SW_Push", ref="SW1", value="BTN_A", footprint="ereader:WE_WS-TASU_436351045816")
SW2 = Part("Switch", "SW_Push", ref="SW2", value="BTN_B", footprint="ereader:WE_WS-TASU_436351045816")
SW3 = Part("Switch", "SW_Push", ref="SW3", value="BTN_C", footprint="ereader:WE_WS-TASU_436351045816")
SW4 = cfg("SW4", "SLLB510200")
JP5 = Part("Jumper", "SolderJumper_2_Open", ref="JP5", value="BOOT", footprint="ereader:JumperPad_2P_P2.0mm")
JP6 = Part("Jumper", "SolderJumper_2_Open", ref="JP6", value="RESET", footprint="ereader:JumperPad_2P_P2.0mm")

QE = Part("Device", "Q_NMOS_GSD", ref="QE", value="Si1308EDL", footprint=FP["SOT23"])
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

# ---------------------------------------------------------------------------
# Nets  (verbatim from ereader-connection-list.md; U1 by datasheet pin number)
# ---------------------------------------------------------------------------
Net("+VBUS").connect(J1["A4"], J1["B4"], J1["A9"], J1["B9"], U2["VBUS"], U6["VBUS"], CV[1])
Net("+SYS").connect(U2["SYS"], LC[2], U5["VIN"], CS[1], CI[1])
Net("+VBAT").connect(U2["BAT"], U3["CELL"], U4["IN"], L2[1], J5[1], CB[1], CGA[1], CGB[1], C4I[1])
Net("+3V3").connect(
    U1[2], U5["VOUT"], L1[2], J2["VDD"], J2["VCI"], J4["VDD"],
    R3[1], R4[1], R5[1], R8[1], R9[1], R10[1], R11[1], R12[1], R13[1], R14[1],
    CO[1], CU1[1], CU2[1], CU3[1], CU4[1], CU5[1], LE[1], CE6[1], CE7[1], CE8[1],
    U5["EN"],  # buck enable = always-on (connection-list SS "3V3 buck"); floating EN = disabled
)
Net("GND").connect(
    U1[1], U1[40], U1[41], U2["GND"], U3["GND"], U4["GND"], U5["GND"], U6["GND"],
    J1["A1"], J1["B1"], J1["A12"], J1["B12"], J1["S1"], J2["VSS"], J4["VSS"], J5[2],
    SW1[2], SW2[2], SW3[2], SW4["COM"], JP5[2], JP6[2],
    R1[2], R2[2], R6[2], R7[2], R15[2],
    CEN[2], CV[2], CS[2], CB[2], CI[2], CO[2], CF[2],
    CU1[2], CU2[2], CU3[2], CU4[2], CU5[2], CGA[2], CGB[2], C4I[2],
    RE1[2], RE2[2], CE1[2], CE2[2], CE3[2], CE4[2], CE5[2], CE6[2], CE7[2], CE8[2], CE9[2],
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
Net("SD_CS").connect(U1[32], J4["DAT3"], R5[2])
Net("BTN_A").connect(U1[4], SW1[1])
Net("BTN_B").connect(U1[5], SW2[1])
Net("BTN_C").connect(U1[6], SW3[1])
Net("LEV_CW").connect(U1[39], SW4["CW"])
Net("LEV_CCW").connect(U1[38], SW4["CCW"])
Net("LEV_PUSH").connect(U1[8], SW4["PUSH"])
Net("CHG_INT").connect(U1[24], U2["INT"], R12[2])
Net("GAUGE_ALRT").connect(U1[25], U3["ALRT"], R13[2])
Net("FL_HWEN").connect(U1[23], U4["HWEN"], R6[1])
Net("CHG_CE").connect(U1[22], U2["CE"], R7[1])
Net("IO0_BOOT").connect(U1[27], JP5[1])
Net("EN").connect(U1[3], JP6[1], R3[2], CEN[1])
Net("USB_DP").connect(U1[14], U6["DP"], J1["A6"], J1["B6"])
Net("USB_DM").connect(U1[13], U6["DM"], J1["A7"], J1["B7"])
Net("CC1").connect(J1["A5"], R1[1])
Net("CC2").connect(J1["B5"], R2[1])
Net("CHG_SW").connect(U2["SW"], LC[1], CBT[1])
Net("CHG_BTST").connect(U2["BTST"], CBT[2])
Net("TS").connect(U2["TS"], R14[2], R15[1])
Net("BUCK_SW").connect(U5["SW"], L1[1])
Net("FL_SW").connect(U4["SW"], L2[2], D1["A"])
Net("FL_OUT").connect(D1["K"], CF[1], J3[1], J3[5])
Net("FL_COOL_K").connect(J3[2], U4["LED1"])
Net("FL_WARM_K").connect(J3[6], U4["LED2"])
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

# ---------------------------------------------------------------------------
# KNOWN ITEMS TO VERIFY before fabrication (do NOT skip):
#  - U5.FB: NOT wired here. Tie to +3V3/VOUT for a fixed-3.3V TPS62840 variant,
#    or to a feedback divider for an adjustable variant. Set per your MPN.
#  - U5.EN wired to +3V3 (always-on) per the connection list; confirm polarity.
#  - Diodes use pin names A/K; confirm anode/cathode vs the SOD-123 pads.
#  - J2 (EPD FPC) symbol pins must be numbered to the GDEY0426T82-FL01C FPC
#    datasheet, and the EPD DC-DC diode/charge-pump topology copied 1:1 from
#    the Good Display reference (rail caps >=25V).
#  - Confirm each IC's exposed thermal pad / unused pins per its datasheet.
# ---------------------------------------------------------------------------
ERC()
generate_netlist(file_="ereader-kicad.net")
