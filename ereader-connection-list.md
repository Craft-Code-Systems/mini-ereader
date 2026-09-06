# Mini E-Reader — Net-by-Net Connection List (tool-agnostic)

Master connectivity. Source of truth for the netlist + schematic. Endpoints = `RefDes.PinName`.
Module U1 pin **numbers** are exact (ESP32-S3-WROOM-1 datasheet). IC pins by **function name** — remap to your symbol's pads.

⚠ Polarity note: BQ25628E **CE low = charge ENABLED**. Default charge-on = CE pulled **low** (R7→GND). GPIO14 drives high to hardware-disable.

---

## Components

| Ref | Part | Notes |
|-----|------|-------|
| U1 | ESP32-S3-WROOM-1-N16R8 | 41-pin module |
| U2 | BQ25628E | 1S buck charger, I2C 0x6B |
| U3 | MAX17048 | fuel gauge, I2C 0x36 |
| U4 | LM3630A | dual backlight boost, I2C 0x36 (I2C1) |
| U5 | TPS62840 | 3V3 buck |
| U6 | USBLC6-2SC6 | USB/CC ESD (SOT-23-6) |
| J1 | USB-C recept 16-pin | power + USB2 |
| J2 | FPC 24p 0.5mm | EPD (SSD1677) |
| J3 | FPC 6p 0.5mm | frontlight (FL0426-S01C) |
| J4 | microSD holder | |
| J5 | JST-PH/SH 2p | Li-Po battery |
| L1 | 2.2µH | TPS62840 buck |
| L2 | 22µH | LM3630A boost |
| L_C | ~1µH | BQ25628E buck (SW→SYS) |
| D1 | Schottky ~30V | LM3630A boost |
| SW1..3 | tactile | BTN_A/B/C |
| SW4 | SLLB510200 | lever CW/CCW/PUSH + COM |
| JP5 | jumper pad (2-pin, open) | BOOT |
| JP6 | jumper pad (2-pin, open) | RESET |
| R1,R2 | 5.1k | CC1,CC2 Rd |
| R3 | 100k | EN pull-up (+C_EN 1µF) |
| R4,R5 | 100k | EPD_CS, SD_CS pull-up |
| R6 | 100k | FL_HWEN pull-down |
| R7 | 100k | CHG_CE pull-down (charge-on default) |
| R8,R9 | 4.7k | I2C0 SDA/SCL pull-up |
| R10,R11 | 4.7k | I2C1 SDA/SCL pull-up |
| R12,R13 | 10k | CHG_INT, GAUGE_ALRT pull-up |
| R14,R15 | 10k+10k | BQ25628E TS divider (or NTC) |
| C_* | decoupling | see notes |

---

## Nets

### Power
```
+VBUS   : J1.VBUS(A4,B4,A9,B9), U2.VBUS, U6.VBUS, C_VBUS.1, TVS
+SYS    : U2.SYS, L_C.2, U5.VIN, C_SYS.1
+VBAT   : U2.BAT, U3.CELL, U4.IN, L2.1, J5.+, C_BAT.1
+3V3    : U5.VOUT(SW→L1→3V3), U1.2, J2.VDD, J4.VDD,
          R3.1, R4.1, R5.1, R8.1, R9.1, R10.1, R11.1, R12.1, R13.1,
          U2.(SCL/SDA pull rail), C_3V3(bulk 22µF + 4×0.1µF)
GND     : U1.1, U1.40, U1.41(EPAD), U2.PGND/GND/EP, U3.GND, U4.GND,
          U5.GND, U6.GND, J1.GND(A1,B1,A12,B12)+shield, J2.VSS,
          J4.VSS, J5.-, all C.2 / pull-down returns / SW returns
```

### I2C
```
I2C0_SDA : U1.10(IO17), U2.SDA, U3.SDA, R8.2
I2C0_SCL : U1.11(IO18), U2.SCL, U3.SCL, R9.2
I2C1_SDA : U1.9(IO16),  U4.SDA, R10.2
I2C1_SCL : U1.31(IO38), U4.SCL, R11.2
```

### EPD (SSD1677 @ J2) — match GDEY0426T82 datasheet pin numbers
```
EPD_SCLK : U1.20(IO12), J2.SCLK
EPD_MOSI : U1.19(IO11), J2.SDA(DIN)
EPD_CS   : U1.18(IO10), J2.CS,  R4.2
EPD_DC   : U1.17(IO9),  J2.DC
EPD_RST  : U1.12(IO8),  J2.RST
EPD_BUSY : U1.7(IO7),   J2.BUSY
J2.BS1   : tie for 4-wire SPI (per datasheet)
J2 support rails (VGH,VGL,VSH,VSL,VCOM,VPP,PREVGH,GDR,RESE):
          local reservoir caps + booster L/Schottky per Good Display ref. Not host nets.
```

### microSD (SPI mode @ J4)
```
SD_SCK  : U1.34(IO41), J4.CLK
SD_MOSI : U1.35(IO42), J4.CMD(DI)
SD_MISO : U1.33(IO40), J4.DAT0(DO)
SD_CS   : U1.32(IO39), J4.DAT3(CS), R5.2
(J4.DAT1,DAT2 → pull-up 10k to 3V3 or leave per holder)
```

### Buttons / lever (active-low, internal pull-up)
```
BTN_A    : U1.4(IO4),  SW1.1     (SW1.2→GND)
BTN_B    : U1.5(IO5),  SW2.1     (SW2.2→GND)
BTN_C    : U1.6(IO6),  SW3.1     (SW3.2→GND)
LEV_CW   : U1.39(IO1), SW4.CW
LEV_CCW  : U1.38(IO2), SW4.CCW
LEV_PUSH : U1.8(IO15), SW4.PUSH
SW4.COM  : GND
```

### Program / reset
```
IO0_BOOT : U1.27(IO0), JP5.1     (JP5.2→GND)
EN       : U1.3(EN),   JP6.1, R3.2, C_EN.1   (JP6.2→GND, C_EN.2→GND)
```
JP5/JP6 are bare exposed pads (no switch part) — short them momentarily with a
screwdriver tip or tweezers to trigger BOOT/RESET. See §4 of
`ereader-schematic.md` and `ereader-footprints.md`.

### USB-C
```
USB_DP : U1.14(IO20), U6.(dp I/O), J1.DP1(A6)+DP2(B6)
USB_DM : U1.13(IO19), U6.(dm I/O), J1.DM1(A7)+DM2(B7)
CC1    : J1.CC1(A5), R1.1   (R1.2→GND)
CC2    : J1.CC2(B5), R2.1   (R2.2→GND)
J1.SBU1(A8), J1.SBU2(B8) : NC
U6.VBUS : +VBUS (clamp ref)
```

### Charger switching (BQ25628E)
```
CHG_SW   : U2.SW, L_C.1, C_BTST.1
CHG_BTST : U2.BTST, C_BTST.2      (0.047µF SW→BTST)
TS       : U2.TS, R14.1(→REGN/3V3), R15.1(→GND)   (or NTC to GND)
CHG_INT  : U1.24(IO47), U2.INT, R12.2
CHG_CE   : U1.22(IO14), U2.CE, R7.1   (R7.2→GND = charge-on default)
U2.D+ , U2.D- : NC (BC1.2 unused) or tie to USB_DP/DM if you want DCP detect
```

### 3V3 buck (TPS62840)
```
BUCK_SW : U5.SW, L1.1        (L1.2→+3V3)
U5.EN   : +3V3 (always-on) or gate from CHG for load-shed
U5.FB   : +3V3 (fixed 3.3 variant) OR divider (adjustable variant) — pick part
U5.VIN  : +SYS
```

### Frontlight boost (LM3630A) — FL0426-S01C confirmed 4-wire
```
FL_SW     : U4.SW, L2.2, D1.A
FL_OUT    : D1.K, C_FL.1(≥25V), J3.1(C+), J3.5(W+)
FL_COOL_K : J3.2(C-), U4.LED1 (Bank A = COOL sink)
FL_WARM_K : J3.6(W-), U4.LED2 (Bank B = WARM sink)
J3.3, J3.4 : NC
U4.HWEN   : FL_HWEN = U1.23(IO21), R6.1   (R6.2→GND = FL off default)
U4.OVP    : set ≥18V per datasheet resistors (or internal)
L2.1      : +VBAT   (boost inductor VBAT→SW)
U4.IN     : +VBAT
```

---

## Decoupling / bulk (place close to pins)
```
U1 3V3  : 22µF + 4×0.1µF
U2 VBUS : 1µF ; SYS: 10µF ; BAT: 10µF ; BTST: 0.047µF
U5      : Cin 10µF (SYS), Cout 10µF (3V3)
U4      : Cin 1µF (VBAT), Cout ≥1µF/25V (FL_OUT)
U3 CELL : 0.1µF + 1µF
```

## Unused module pins (leave NC / test-point)
```
U1.15(IO3 strap), U1.16(IO46 strap), U1.21(IO13), U1.26(IO45 strap),
U1.28(IO35 PSRAM), U1.29(IO36 PSRAM), U1.30(IO37 PSRAM),
U1.36(RXD0/IO44), U1.37(TXD0/IO43), U1.13? no(used).
Tip: bring RXD0/TXD0 to test-points for a UART fallback console.
```
