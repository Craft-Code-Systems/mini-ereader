# Mini E-Reader — Schematic (subsystem view)

> **Why this file exists / why there is no `.kicad_sch`.** This board was captured
> **netlist-first**: the electrical design lives in
> [`ereader-connection-list.md`](./ereader-connection-list.md) (source of truth) →
> [`ereader-kicad.net`](./ereader-kicad.net) (netlist) → [`ereader.kicad_pcb`](./ereader.kicad_pcb)
> (placement). No schematic sheet was ever drawn, so KiCad's **Schematic Editor
> (Eeschema) has nothing to open** — that is the answer to "why is there no schematic".
>
> KiCad **cannot** auto-generate a schematic from a netlist or from the PCB (there is
> no netlist→schematic or PCB→schematic importer). A native `.kicad_sch` has to be
> *drawn* in Eeschema. The diagrams below are that schematic in reviewable form —
> they render directly on GitHub (Mermaid) and mirror the connection list net-for-net.
>
> **To get a native Eeschema schematic:** create a new schematic in the `ereader`
> project, drop the symbols for U1–U6 / J1–J5 / SW1–SW4 / JP5–JP6 / passives, and
> wire them to match these diagrams (label-based wiring is fine — same-named net
> labels connect). Run **ERC**, then it drives the same `ereader-kicad.net`.

All pin **numbers** on U1 are the exact ESP32‑S3‑WROOM‑1 datasheet pins; IC pins on
U2–U6 are by **function name** (remap to your chosen symbol's pads). Nets are taken
verbatim from the connection list.

---

## 1. System block diagram

```mermaid
flowchart LR
  USBC["USB-C J1<br/>(VBUS + USB2 + CC)"]
  ESD["U6 USBLC6-2SC6<br/>ESD"]
  CHG["U2 BQ25628E<br/>1S buck charger (I2C 0x6B)"]
  BATT["J5 Li-Po 1S"]
  GAUGE["U3 MAX17048<br/>fuel gauge (I2C 0x36)"]
  BUCK["U5 TPS62840<br/>3V3 buck"]
  MCU["U1 ESP32-S3-WROOM-1<br/>N16R8"]
  FL["U4 LM3630A<br/>dual FL boost (I2C1)"]
  EPD["J2 EPD FPC 24p<br/>SSD1677 / GDEY0426T82"]
  FLC["J3 Frontlight FPC 6p<br/>FL0426-S01C"]
  SD["J4 microSD"]
  NAV["SW1-3 side buttons<br/>SW4 SLLB5 lever"]

  USBC -->|"+VBUS"| CHG
  USBC --- ESD
  ESD ---|"USB_DP/DM"| MCU
  CHG -->|"+SYS"| BUCK
  CHG <-->|"+VBAT"| BATT
  CHG -->|"+VBAT"| GAUGE
  CHG -->|"+VBAT"| FL
  BUCK -->|"+3V3"| MCU
  MCU -->|"SPI 4-wire"| EPD
  MCU -->|"SPI"| SD
  MCU <-->|"I2C0"| CHG
  MCU <-->|"I2C0"| GAUGE
  MCU <-->|"I2C1"| FL
  FL -->|"FL_OUT + sinks"| FLC
  NAV -->|"GPIO active-low"| MCU
```

---

## 2. Power tree

```mermaid
flowchart TB
  J1["USB-C J1<br/>VBUS A4/B4/A9/B9"]
  CVBUS["C_VBUS"]
  U2["U2 BQ25628E"]
  LC["L_C ~1uH"]
  J5["J5 Li-Po +"]
  U3["U3 MAX17048"]
  U4["U4 LM3630A IN"]
  L2["L2 22uH"]
  U5["U5 TPS62840"]
  L1["L1 2.2uH"]
  RAIL3V3["+3V3 rail<br/>U1.2, J2.VDD, J4.VDD, pull-up rails, C_3V3 22uF+4x0.1uF"]

  J1 -->|"+VBUS"| U2
  J1 --- CVBUS
  U2 -->|"SW"| LC -->|"+SYS"| U5
  U2 <-->|"BAT = +VBAT"| J5
  U2 -->|"+VBAT"| U3
  U2 -->|"+VBAT"| U4
  U2 -->|"+VBAT"| L2
  U5 -->|"SW"| L1 -->|"+3V3"| RAIL3V3
  U5 -.->|"VIN = +SYS"| U2
```

`GND`: U1.1/40/41(EPAD), U2 PGND/GND/EP, U3/U4/U5/U6 GND, J1 GND+shield, J2.VSS,
J4.VSS, J5.−, all cap returns, all pull-down / switch returns.

---

## 3. MCU GPIO map (U1 = ESP32‑S3‑WROOM‑1)

| Pin | GPIO | Net | Goes to |
|-----|------|-----|---------|
| 2 | 3V3 | +3V3 | supply |
| 1 / 40 / 41 | GND/EPAD | GND | ground |
| 3 | EN | EN | JP6 (RESET), R3 pull-up, C_EN |
| 27 | IO0 | IO0_BOOT | JP5 (BOOT) |
| 4 | IO4 | BTN_A | SW1.1 |
| 5 | IO5 | BTN_B | SW2.1 |
| 6 | IO6 | BTN_C | SW3.1 |
| 39 | IO1 | LEV_CW | SW4.CW |
| 38 | IO2 | LEV_CCW | SW4.CCW |
| 8 | IO15 | LEV_PUSH | SW4.PUSH |
| 10 | IO17 | I2C0_SDA | U2, U3, R8 |
| 11 | IO18 | I2C0_SCL | U2, U3, R9 |
| 9 | IO16 | I2C1_SDA | U4, R10 |
| 31 | IO38 | I2C1_SCL | U4, R11 |
| 20 | IO12 | EPD_SCLK | J2 |
| 19 | IO11 | EPD_MOSI | J2 |
| 18 | IO10 | EPD_CS | J2, R4 |
| 17 | IO9 | EPD_DC | J2 |
| 12 | IO8 | EPD_RST | J2 |
| 7 | IO7 | EPD_BUSY | J2 |
| 34 | IO41 | SD_SCK | J4 |
| 35 | IO42 | SD_MOSI | J4 |
| 33 | IO40 | SD_MISO | J4 |
| 32 | IO39 | SD_CS | J4, R5 |
| 14 | IO20 | USB_DP | U6, J1 |
| 13 | IO19 | USB_DM | U6, J1 |
| 24 | IO47 | CHG_INT | U2.INT, R12 |
| 22 | IO14 | CHG_CE | U2.CE, R7 |
| 23 | IO21 | FL_HWEN | U4.HWEN, R6 |

Strap/PSRAM/unused pins (IO3/13/45/46/35/36/37, RXD0/TXD0) → NC or test-point.

---

## 4. Navigation input (this is the input scheme from ADR 0008)

Nav contacts are **active-low momentary to GND** with the ESP32‑S3 **internal
pull-ups**; every one sits on an RTC‑capable GPIO so it can wake the MCU from deep
sleep. **SW1–SW3 are side-actuated (right-angle) tactiles** and **SW4 is the ALPS
SLLB5 two-way lever + push** — the actuators face the **board edge** because the
screen covers the whole front and magnets hold the back to the phone, so nothing
can be pressed from the top or bottom faces. **JP5/JP6 (BOOT/RESET) are not
switches** — they're bare exposed 2-pad jumpers, momentarily shorted with a
screwdriver tip or tweezers when you actually need to flash/recover the board;
they read open (floating high through the pull-up) in normal use, so there's no
switch part, cap, or accidental-press risk sitting on a rarely-used recovery path.

```mermaid
flowchart LR
  subgraph MCU["U1 ESP32-S3 (internal pull-ups, RTC-wake)"]
    IO4["IO4"]; IO5["IO5"]; IO6["IO6"]
    IO1["IO1"]; IO2["IO2"]; IO15["IO15"]
    IO0["IO0"]; EN["EN"]
  end
  SW1["SW1 side tact<br/>BTN_A"]; SW2["SW2 side tact<br/>BTN_B"]; SW3["SW3 side tact<br/>BTN_C"]
  SW4["SW4 ALPS SLLB5 lever<br/>CW / CCW / PUSH / COM"]
  JP5["JP5 jumper pad<br/>BOOT (screwdriver-shortable)"]; JP6["JP6 jumper pad<br/>RESET (screwdriver-shortable)"]
  GND(["GND"])

  IO4 -- "BTN_A" --> SW1 --> GND
  IO5 -- "BTN_B" --> SW2 --> GND
  IO6 -- "BTN_C" --> SW3 --> GND
  IO1 -- "LEV_CW" --> SW4
  IO2 -- "LEV_CCW" --> SW4
  IO15 -- "LEV_PUSH" --> SW4
  SW4 -- "COM" --> GND
  IO0 -- "IO0_BOOT" --> JP5 --> GND
  EN -- "EN" --> JP6 --> GND
```

`R3` (100k) pulls **EN** up with `C_EN` (1µF) for a clean reset; BOOT uses the
module's internal strap pull-up.

---

## 5. I2C buses

```mermaid
flowchart LR
  U1["U1 ESP32-S3"]
  R8["R8 4.7k"]; R9["R9 4.7k"]; R10["R10 4.7k"]; R11["R11 4.7k"]
  U2["U2 BQ25628E 0x6B"]; U3["U3 MAX17048 0x36"]; U4["U4 LM3630A"]
  V3["+3V3"]

  U1 -- "I2C0_SDA (IO17)" --> U2 & U3
  U1 -- "I2C0_SCL (IO18)" --> U2 & U3
  U1 -- "I2C1_SDA (IO16)" --> U4
  U1 -- "I2C1_SCL (IO38)" --> U4
  V3 --- R8 & R9 & R10 & R11
  R8 --- U2
  R9 --- U2
  R10 --- U4
  R11 --- U4
```

U3 (fuel gauge) and U4 (frontlight) both answer at 0x36 — that clash is exactly why
U4 is on a **separate bus (I2C1)**.

---

## 6. E‑paper (SSD1677 @ J2, 4‑wire SPI)

```mermaid
flowchart LR
  U1["U1 ESP32-S3"]
  R4["R4 100k"]; V3["+3V3"]
  J2["J2 EPD FPC 24p<br/>SSD1677 / GDEY0426T82"]

  U1 -- "EPD_SCLK (IO12)" --> J2
  U1 -- "EPD_MOSI (IO11)" --> J2
  U1 -- "EPD_CS (IO10)" --> J2
  U1 -- "EPD_DC (IO9)" --> J2
  U1 -- "EPD_RST (IO8)" --> J2
  J2 -- "EPD_BUSY (IO7)" --> U1
  V3 --- R4 --- J2
```

`J2.BS1` tied **low** (→GND) for 4‑wire SPI.

### 6a. EPD external DC‑DC (SSD1677 boost + charge pumps)

The SSD1677 needs an external boost + charge‑pump for its ±20 V gate / ±15 V source
rails. Now captured as real parts (LE/QE/DE1‑3/RE1‑2/CE1‑9) feeding J2's support pins:

```mermaid
flowchart LR
  V3["+3V3"]; LE["LE 47µH"]; QE["QE Si1308EDL<br/>N-FET"]
  SW["EPD_SW"]; DE1["DE1 MBR0530"]; DE2["DE2"]; DE3["DE3"]
  J2["J2 SSD1677<br/>GDR/RESE/VGH/VGL<br/>VSH1/VSH2/VSL/VCOM/VCI"]
  RE1["RE1 2.2Ω"]; RE2["RE2 1MΩ"]; GND(["GND"])

  V3 --> LE --> SW
  SW --> QE
  J2 -- "GDR" --> QE
  QE -- "RESE" --> RE1 --> GND
  J2 -- "GDR" --> RE2 --> GND
  SW --> DE1 -- "VGH" --> J2
  SW --> DE2 --> DE3 -- "VGL" --> J2
  J2 -. "VSH1/VSH2/VSL/VCOM reservoir caps CE1-3,CE9→GND" .- GND
  V3 -. "VCI/VDD caps CE6-8→GND" .- GND
```

> ⚠ **VERIFY & COPY 1:1.** The diode/charge‑pump interconnect, diode **orientation**, and
> the J2 (GDEY0426T82) **FPC pin numbers** are a functional PLACEHOLDER — transcribe them
> exactly from the Good Display GDEY0426T82‑FL01C reference schematic ("ESP32 Sample Code"
> zip) and the panel datasheet before capture + route. Rail cap **values are
> non‑negotiable** (≥25 V). See `ereader-connection-list.md` → *EPD external DC‑DC*.

---

## 7. microSD (SPI @ J4) and USB‑C data

```mermaid
flowchart LR
  U1["U1 ESP32-S3"]
  R5["R5 100k"]; V3["+3V3"]
  J4["J4 microSD"]
  U6["U6 USBLC6-2SC6"]
  J1["J1 USB-C"]
  R1["R1 5.1k"]; R2["R2 5.1k"]; GND(["GND"])

  U1 -- "SD_SCK (IO41)" --> J4
  U1 -- "SD_MOSI (IO42)" --> J4
  J4 -- "SD_MISO (IO40)" --> U1
  U1 -- "SD_CS (IO39)" --> J4
  V3 --- R5 --- J4
  U1 -- "USB_DP (IO20)" --- U6 --- J1
  U1 -- "USB_DM (IO19)" --- U6 --- J1
  J1 -- "CC1" --- R1 --> GND
  J1 -- "CC2" --- R2 --> GND
```

---

## 8. Charger (BQ25628E) + 3V3 buck (TPS62840)

```mermaid
flowchart LR
  VBUS["+VBUS"]; SYS["+SYS"]; VBAT["+VBAT"]; V3["+3V3"]
  U2["U2 BQ25628E"]; LC["L_C ~1uH"]; CBTST["C_BTST 0.047uF"]
  R7["R7 100k"]; R12["R12 10k"]; R14["R14 10k"]; R15["R15 10k"]; GND(["GND"])
  U5["U5 TPS62840"]; L1["L1 2.2uH"]
  U1["U1 ESP32-S3"]

  VBUS --> U2
  U2 -- "SW" --> LC --> SYS
  U2 -- "BTST" --- CBTST
  U2 --- VBAT
  U1 -- "CHG_CE (IO14)" --> U2
  U2 -- "CHG_INT" --> U1
  U2 -- "INT" --- R12 --> V3
  U2 -- "CE" --- R7 --> GND
  U2 -- "TS" --- R14 --> V3
  U2 -- "TS" --- R15 --> GND
  SYS --> U5
  U5 -- "SW" --> L1 --> V3
```

`CE low = charge enabled`; R7→GND makes charge-on the power-up default, GPIO14 drives
high to hard-disable.

---

## 9. Frontlight boost (LM3630A → FL0426‑S01C, 4‑wire)

```mermaid
flowchart LR
  VBAT["+VBAT"]; U4["U4 LM3630A"]; L2["L2 22uH"]; D1["D1 Schottky 30V"]
  CFL["C_FL >=25V"]; J3["J3 FL FPC 6p"]
  U1["U1 ESP32-S3"]; R6["R6 100k"]; GND(["GND"])

  VBAT --> U4
  VBAT --> L2 -- "FL_SW" --> U4
  U4 -- "FL_SW" --> D1 -- "FL_OUT" --> CFL
  D1 -- "FL_OUT" --> J3
  J3 -- "FL_COOL_K (C-)" --> U4
  J3 -- "FL_WARM_K (W-)" --> U4
  U1 -- "FL_HWEN (IO21)" --> U4
  U4 --- R6 --> GND
```

`FL_OUT` feeds both J3.1 (C+) and J3.5 (W+); LED1/LED2 sink the cool/warm banks;
`R6→GND` keeps the frontlight off by default until GPIO21 enables it.
