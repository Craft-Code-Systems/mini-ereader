# Mini E-Reader — Footprint / Land-Pattern Picklist

✓ = in KiCad 8 official libs (use as-is). ⚑ = pull from SnapEDA / Ultra-Librarian / mfr, verify pad map.
Always DRC land vs the ordered part's datasheet before route.

## Actives

| Ref | MPN | Package | Footprint | Source | Notes |
|-----|-----|---------|-----------|--------|-------|
| U1 | ESP32-S3-WROOM-1-N16R8 | 41-pin SMD module | `RF_Module:ESP32-S3-WROOM-1` | ✓ KiCad | symbol `RF_Module:ESP32-S3-WROOM-1`. Honor antenna keep-out in courtyard |
| U2 | BQ25628E**RYK**R (confirm suffix) | QFN 4×4? / small QFN | ⚑ TI Ultra-Librarian | new part — no KiCad official. Confirm exact package/pad from TI datasheet Sec.11 |
| U3 | MAX17048G+T10 | µDFN-8 (2×2, 0.5mm) | ⚑ SnapEDA / ADI | verify vs G+ package |
| U4 | LM3630A**YFQ**R | DSBGA-12 (0.4mm pitch) | ⚑ TI Ultra-Librarian | 0.4mm BGA → tight; check fab min. WSON variant if available = easier |
| U5 | TPS62840**DLC**R | SOT-563 6-pin (verify) | ⚑ TI Ultra-Librarian | confirm DLC vs other suffix + fixed-vs-adj |
| U6 | USBLC6-2SC6 | SOT-23-6 | `Package_TO_SOT_SMD:SOT-23-6` | ✓ KiCad | symbol `Power_Protection:USBLC6-2SC6` ✓ |

## Connectors

| Ref | MPN | Footprint | Source | Notes |
|-----|-----|-----------|--------|-------|
| J1 | USB-C 16-pin recept (USB2, e.g. HRO TYPE-C-31-M-12 / GCT USB4085) | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | ✓ KiCad | 16-pin = power+USB2 only. Add 2 mount posts to GND |
| J2 | EPD FPC 24p 0.5mm | `Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal` ✓ KiCad | ⚑ verify | ⚠ match **contact side** (GDEY0426T82 FPC = bottom-contact) + flip-lock. Pick a flip-lock ZIF |
| J3 | FL FPC 6p 0.5mm | `Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal` ✓ KiCad | ⚑ verify | same contact-side rule as J2 |
| J4 | microSD push-pull | `Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5` | ✓ KiCad | or Molex 5031821852 |
| J5 | Li-Po 1S | `Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal` | ✓ KiCad | or SH 1.0mm if slim |

## Switches

| Ref | MPN | Footprint | Source | Notes |
|-----|-----|-----------|--------|-------|
| SW1-3,5,6 | SMD tactile (e.g. TL3342, PTS810) | `Button_Switch_SMD:SW_SPST_TL3342` | ✓ KiCad | swap to your exact tactile |
| SW4 | ALPS **SLLB510200** | ⚑ custom / SnapEDA | 2-dir lever + push, 9.5×8.8×2.2mm. Build land from ALPS drawing (CW/CCW/PUSH/COM). No KiCad official |

## Passives / discrete

| Ref | Value | Footprint | Notes |
|-----|-------|-----------|-------|
| R1-15 | see BOM | `Resistor_SMD:R_0402_1005Metric` | 0603 if hand-solder |
| C* (0.1/1µF) | — | `Capacitor_SMD:C_0402_1005Metric` | |
| CS,CB,CI,CO,CF,CU1 (10-22µF) | — | `Capacitor_SMD:C_0805_2012Metric` | CF ≥25V (FL_OUT) |
| L1 | 2.2µH | `Inductor_SMD:L_0805_2012Metric` | buck; ≥1A Isat |
| LC | ~1µH | `Inductor_SMD:L_0805_2012Metric` | charger buck; per BQ25628E |
| L2 | 22µH | `Inductor_SMD:L_1210_3225Metric` | FL boost; ≥0.3A, per LM3630A |
| D1 | Schottky 30V | `Diode_SMD:D_SOD-123` | FL boost rectifier |

## EPD support (SSD1677, local to J2)
Not separate line items — copy the **Good Display GDEY0426T82 reference** block verbatim: reservoir caps (0402/0603, 1µF/4.7µF X7R 25V+) on VGH/VGL/VSH/VSL/VCOM/VPP/PREVGH + booster components (GDR/RESE). Place hugging J2.

## Library setup
1. KiCad official libs cover ✓ rows out of the box.
2. For ⚑ rows: SnapEDA (free login) or TI/ADI Ultra-Librarian → export KiCad symbol+footprint → add as project-local lib.
3. Confirm every ⚑ package suffix against the exact orderable MPN (JLCPCB/LCSC/Mouser stock) before committing land patterns.

## Netlist / .cmp footprint status (Rev C2)
Fixed the import errors. In `ereader-kicad.net` + `ereader.cmp`:
- **Assigned (import clean):** U1, U6, J1, J2 (full FH12-24S name), J3 (full FH12-6S name), J4, J5, L1/L2/LC, D1, SW1-3/5/6, all R/C.
- **Left BLANK on purpose → assign in KiCad *Footprint Assignment* (CvPcb):** U2 BQ25628E, U3 MAX17048, U4 LM3630A, U5 TPS62840, SW4 SLLB510200. No official KiCad footprint exists → pull from SnapEDA/Ultra-Librarian per confirmed MPN, or draw the land from the datasheet. Blank = no "not found" error; component just awaits a footprint.
- ⚠ J1 USB-C string assumes `USB_C_Receptacle_HRO_TYPE-C-31-M-12` exists in your install (it imported fine for you). If a future error hits it, blank it and assign your exact 16-pin part.
- SW4 land: build from ALPS SLLB5 drawing — pads CW / CCW / PUSH / COM. Once drawn, set its footprint in Footprint Assignment.
