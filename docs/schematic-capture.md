# Schematic Capture Worksheet (Eeschema)

Follow this once to draw a native `ereader.kicad_sch`. It turns the netlist-first
design into a proper schematic-driven project so that **Update PCB from Schematic**
works cleanly and the "pad *X* not found in footprint" errors disappear.

## Why this is needed (read once)

`ereader-kicad.net` names IC pins by **function** (`IN`, `SDA`, `SW`, `LED1`…).
KiCad's netlist import binds those names to footprint **pads**, but real footprints
number their pads (QFN `1..n`, BGA `A1/B1…`). With no symbol in between, the names
never match — that is the 56 `pad ... not found` errors seen on netlist import.

A **symbol** solves it: the symbol pairs each pin *name* with the datasheet pad
*number*. So in schematic capture you only attach nets to named pins; KiCad maps
name → pad number for you. **You never hand-map pads.**

> `ereader-connection-list.md` stays the human source of truth (net-by-net).
> The schematic *implements* it. Once the schematic drives the board, the
> hand-authored `ereader-kicad.net` is retired (Eeschema generates its own).

## One-time setup

1. Open `ereader.kicad_pro` in the KiCad project manager.
2. Open the **Schematic Editor**. It will be empty (there is no `.kicad_sch`
   yet — that is expected, and is why *Update PCB from Schematic* / F8 errored).
   Save immediately as `ereader.kicad_sch` in the project folder.
3. Capture per the tables below, then annotate → ERC → assign footprints →
   **Update PCB from Schematic**.

## Capture method: label-based wiring (do this, it's fast)

You do **not** need to draw wires across the sheet. Use **global labels**
(`Place → Add Global Label`, hotkey **Ctrl+H**) whose text is the **net name**
from `ereader-connection-list.md`. Two pins carrying the same-named global label
are connected. So the loop for every pin is:

1. Place the symbol.
2. On each pin, drop a short wire stub + a **global label** named after its net.
3. Move on. Same net name anywhere = one net.

Power nets (`+3V3`, `+VBAT`, `+SYS`, `+VBUS`, `GND`) are cleanest with **power
symbols** (`Place → Add Power`, **P**) instead of labels — `GND`, `+3V3`, etc.

## Symbol + footprint picklist

The symbol carries the pin→pad map, so **use a matched symbol+footprint pair**.
KiCad-stock ones are safe as-is; for the `SnapEDA` rows, download the symbol AND
its footprint together (they are internally consistent) and confirm the package
against the MPN. Footprints reflect the corrections in `ereader-footprints.md`.

| Ref | MPN | Symbol (lib_id or source) | Footprint |
|-----|-----|---------------------------|-----------|
| U1 | ESP32-S3-WROOM-1-N16R8 | `RF_Module:ESP32-S3-WROOM-1` (stock) | `RF_Module:ESP32-S3-WROOM-1` |
| U2 | BQ25628ERYKR | SnapEDA / TI | **18-pin WQFN 2.5×3.0mm (RYK)** — vendor land |
| U3 | MAX17048G+T10 | KiCad `Battery_Management` if present, else SnapEDA/ADI | µDFN-8 2×2mm |
| U4 | LM3630AYFQR | SnapEDA / TI | DSBGA-12, 0.4mm |
| U5 | TPS62840DLCR | KiCad `Regulator_Switching` if present, else SnapEDA/TI | **VSON-HR 8-pin 2.0×2.0mm (DLC)** |
| U6 | USBLC6-2SC6 | `Power_Protection:USBLC6-2SC6` (stock) | `Package_TO_SOT_SMD:SOT-23-6` |
| J1 | USB-C 16P | `Connector:USB_C_Receptacle_USB2.0` | `...:USB_C_Receptacle_HRO_TYPE-C-31-M-12` |
| J2 | EPD 24p FPC | `Connector:Conn_01x24` (numbered) | `...:Hirose_FH12-24S-0.5SH...` |
| J3 | FL 6p FPC | `Connector:Conn_01x06` | `...:Hirose_FH12-6S-0.5SH...` |
| J4 | microSD | `Connector:microSD_HC` (or holder symbol) | `...:microSD_HC_Hirose_DM3AT-SF-PEJM5` |
| J5 | Li-Po 1S | `Connector:Conn_01x02` | `Connector_JST:JST_PH_S2B-PH-K...` |
| SW1-3 | WE WS-TASU | `Switch:SW_Push` | `ereader:WE_WS-TASU_436351045816` |
| SW4 | ALPS SLLB510200 | `Switch:SW_...` w/ pins CW/CCW/PUSH/COM | `ereader:ALPS_SLLB5_Lever` |
| JP5/JP6 | jumper pads | `Jumper:SolderJumper_2_Open` | `ereader:JumperPad_2P_P2.0mm` |
| QE | Si1308EDL | `Transistor_FET:Si1308EDL` or `Device:Q_NMOS_GSD` | `Package_TO_SOT_SMD:SOT-23` |
| DE1-3 | MBR0530 | `Device:D_Schottky` | `Diode_SMD:D_SOD-123` |
| D1 | Schottky 30V | `Device:D_Schottky` | `Diode_SMD:D_SOD-123` |
| L1/LC | 2.2µH / 1µH | `Device:L` | `Inductor_SMD:L_0805_2012Metric` |
| L2/LE | 22µH / 47µH | `Device:L` | `L_1210_3225Metric` |
| R* | see BOM | `Device:R` | `Resistor_SMD:R_0402_1005Metric` |
| C* | see BOM | `Device:C` | per `ereader-footprints.md` |

## Wiring — go subsystem by subsystem

`ereader-connection-list.md` is the authoritative pin→net list; the Mermaid
diagrams in `ereader-schematic.md` show each subsystem. Capture in this order,
labeling each pin with its net name from the connection list:

1. **U1 (MCU).** Its pins are **numbered** in the connection list (exact
   WROOM-1 datasheet pins) and the stock symbol uses those same numbers —
   attach each net (`+3V3`, `GND`, `EPD_SCLK`, `I2C0_SDA`, `USB_DP`, …) to the
   matching pin. Tie unused strap/PSRAM pins per §"Unused module pins".
2. **Power** (§ Power): USB-C `J1` → `U6` ESD → `U2` charger → `U5` buck →
   `+3V3`; `U3` gauge; `J5` battery. Use power symbols for the rails.
3. **I²C** (§ I2C): `R8/R9` on `I2C0`, `R10/R11` on `I2C1`.
4. **EPD `J2`** (§ EPD): logic pins + the support rails.
5. **EPD external DC-DC** (§ EPD external DC-DC): `LE/QE/DE1-3/RE1/RE2/CE1-9`.
6. **microSD `J4`**, **USB-C `J1`** (§ microSD / USB-C).
7. **Buttons/lever** (§ Buttons/lever), **BOOT/RESET** (§ Program/reset).
8. **Charger switching**, **buck**, **frontlight boost** (their § sections).
9. **Decoupling** (§ Decoupling): place each cap on its rail per the table.

## Three things that need care

- **J2 (EPD FPC) pin numbers.** The connection list gives J2 pins by function
  (`SCLK`, `GDR`, `VGH`, …). The `Conn_01x24` symbol has numbered pins 1-24. Map
  each function to its **FPC pin number from the GDEY0426T82-FL01C datasheet**
  before wiring — this is the one mapping the datasheet must supply. (J4 microSD
  uses named pads that already line up.)
- **EPD DC-DC interconnect is a placeholder.** Capture `LE/QE/DE1-3/RE1-2/CE1-9`
  per § EPD external DC-DC, but **transcribe the diode/charge-pump topology and
  orientation 1:1 from the Good Display GDEY0426T82-FL01C reference schematic**
  before trusting it. Rail cap values are non-negotiable (≥25V).
- **Footprint swaps will re-do routing.** When you assign the correct U2/U5
  lands (and any others), *Update PCB from Schematic* replaces the placeholder
  footprints on the board — the traces routed to those old lands are dropped and
  must be re-routed. Expect this; it is why the wrong placeholders should be
  fixed before investing in routing them.

## Finish

1. **Annotate** (`Tools → Annotate`) — keep the existing refdes (U1, U2, …).
2. **ERC** (`Inspect → Electrical Rules Checker`) — resolve every error.
3. **Assign footprints** (the table above) — every symbol gets one.
4. **Update PCB from Schematic** (F8) — the parts bind by pad number; the
   "pad not found" errors are gone.
5. Place + route the new/changed parts; stitch the 3 `GND_F.Cu` islands.
6. `python3 preflight.py` (still valid: board must contain every part) → DRC → 0/0.

Once the schematic drives the board, delete or stop maintaining
`ereader-kicad.net` (Eeschema now generates the netlist), and update the
milestone checklist in `README.md`.
