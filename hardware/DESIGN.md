# Mini E-Reader — Hardware Design (reference spec)

> ⚠️ **Not the canonical board.** The actual, further-along KiCad design is
> `../ereader.kicad_pcb` (`../ereader-pcb-design.md`, Rev C). This document
> is an earlier, simpler *reference spec*; where they differ (power:
> MCP73831+LDO here vs BQ25628E+TPS62840 buck there; frontlight: 2×TPS61165
> here vs LM3630A there; input: 3 buttons here vs +rotary encoder there),
> the `ereader.*` board wins. The one part worth porting *up* from here is
> the **exact SSD1677 boost circuit** (§5), which the Rev C spec references
> but does not enumerate.

> Reference design v0.1. This is the electrical "source of truth": block
> diagram, power architecture, net-by-net connectivity, MCU pin map, and
> component notes. The KiCad schematic/PCB in this folder are captured
> **from** this document — if they ever disagree, this document wins until
> the KiCad ERC/netlist is confirmed clean and this note is removed.

**Status:** design captured, not yet drawn/routed in KiCad. See
[Verification status](#11-verification-status).

---

## 1. Overview

A pocket e-reader built around an **ESP32-S3** driving a **4.26" monochrome
SPI E-Paper** panel (800×480) with a **laminated tunable-white frontlight**,
powered by a **single-cell LiPo** with **USB-C** charging and native-USB
programming. Optional **microSD** for book storage. Three tactile buttons.

| Attribute        | Value                                                        |
|------------------|-------------------------------------------------------------|
| MCU              | ESP32-S3-WROOM-1 (N8R2 or N16R8 module)                     |
| Display          | GDEY0426T82-FL01C, 4.26" 800×480, SSD1677, 4-wire SPI, 24-pin FPC |
| Frontlight       | integrated dual (cold+warm), 2× 5-series LEDs, VF≤15V, IF≤15mA |
| Wireless         | Wi-Fi b/g/n + BLE 5 (on-module)                            |
| Storage          | On-module flash (8/16 MB) + optional microSD (SPI)         |
| Power in         | USB-C (5 V) and/or 1S LiPo (3.0–4.2 V)                     |
| Charger          | MCP73831, 500 mA (PROG-set)                                 |
| System rail      | 3.3 V via AP2112K-3.3 LDO (600 mA)                         |
| Frontlight rail  | ~15 V per channel via 2× TPS61165 boost (CC, PWM-dimmed)   |
| Programming      | Native USB (USB-Serial-JTAG), no external UART bridge      |
| Board            | 2-layer, ~1.6 mm FR-4, hand/JLCPCB-assemblable            |

> **Correction history:** an early draft assumed a 2.13" SSD1680 panel. The
> owner supplied the **FL0426-S01C** frontlight (→ 4.26"/800×480 + frontlight
> subsystem, §5b) and then the **GDEY0426T82-FL01C** panel datasheet, which
> locks the controller (**SSD1677**), the 24-pin EPD FPC pinout, and the
> external DC-DC reference circuit (§5). See ADR 0002.

---

## 2. Block diagram

```
            ┌──────────┐         VBUS (5V)
  USB-C  ───┤ USB-C RCP ├───┬───────────────┐
  (power+   │  CC 5.1k  │   │               │
   data)    └────┬─────┘    │           ┌───▼────────┐   VBAT
             D+/D-│         │           │  MCP73831  ├───────┐
                  │         │           │  Li charger│  STAT │
                  │         │           └───▲────────┘   │   │
                  │         │  ┌── JST-PH ──┘            LED  │
                  │         │  │  1S LiPo                     │
                  │         ▼  ▼                              │
                  │   ┌───────────────┐  VSYS ┌───────────┐  │
                  │   │ load-share    ├───┬────┤ AP2112-3.3│  │
                  │   │ P-FET + diode │   │    │   LDO     │  │
                  │   └───────────────┘   │    └─────┬─────┘  │
                  │                       │        +3V3       │
                  │              ┌────────▼────────┐ │        │
                  │              │ 2× TPS61165     │ │        │
                  │              │ boost CC ~15V   │ │        │
                  │              │ (cold / warm)   │ │        │
                  │              └───────┬─────────┘ │        │
                  │                  FL FPC (J5)     │        │
             ┌────▼───────────────────────────────────▼──────▼───┐
             │                 ESP32-S3-WROOM-1                    │
             │  USB  SPI(SCK/MOSI/MISO)  GPIO  ADC  2×PWM  EN/BOOT │
             └───┬───────┬───────────────┬─────┬──────┬───────────┘
                 │       │               │     │   FL_COLD/WARM_PWM
             (native)  ┌─▼──────┐    ┌───▼──┐  │
                       │ E-Paper│    │microSD│ VBAT sense (÷2)
                       │ 4.26"  │    │  (SPI)│  + 3 buttons
                       │ 800×480│    └───────┘
                       └────────┘
```

---

## 3. Power architecture

Sources: VBUS (USB 5 V), VBAT (1S LiPo). Rails: VSYS (OR of the two), +3V3
(LDO), and two ~15 V frontlight channels (boosted from VSYS).

### 3.1 Charging — MCP73831 (SOT-23-5)

| Pin | Net    | Notes                                                    |
|-----|--------|----------------------------------------------------------|
| 1 STAT | CHG_STAT | Open-drain. LED to VBUS via 1 kΩ; also to GPIO (sense). |
| 2 VSS  | GND    |                                                          |
| 3 VBAT | VBAT   | 4.7 µF to GND.                                           |
| 4 VDD  | VBUS   | 4.7 µF to GND.                                           |
| 5 PROG | R_PROG to GND | 2.0 kΩ → **500 mA** (`I_chg ≈ 1000 V / R_PROG`). |

### 3.2 Load-share (USB priority) — DMG2305UX P-FET + Schottky

- **Q1 P-FET:** source = VBAT, drain = VSYS, gate to GND via 100 kΩ and to
  VBUS via 100 kΩ. No USB → gate low → on (battery feeds VSYS). USB present
  → gate high → off (battery isolated).
- **D1 Schottky (VBUS→VSYS):** supplies VSYS from USB, ~0.3 V drop.
- ADR 0003 alternative: MCP73871 power-path charger.

### 3.3 Regulation — AP2112K-3.3 (SOT-23-5)

VIN = VSYS (1 µF), EN = VSYS, VOUT = +3V3 (1 µF min + 10 µF bulk). LDO
can't boost → +3V3 sags below VBAT ≈ 3.4 V; size bulk caps for 500 mA
Wi-Fi-TX bursts (≥ 22 µF near the module). Buck-boost (TPS63020) is the
ADR-0003 alternative for full battery-tail use.

### 3.4 Battery telemetry

VBAT → 100 kΩ/100 kΩ divider → **BAT_SENSE** → ADC (GPIO1, ADC1_CH0), 100 nF
to GND. CHG_STAT → GPIO2 for charge state.

### 3.5 Frontlight rails — 2× TPS61165 boost (see §5b)

Two independent WLED boost drivers step VSYS up to ~15 V and regulate each
LED string's current; PWM-dimmed from the MCU. Details in §5b / ADR 0005.

### 3.6 Power budget (rough)

| Rail | Load                         | Typ    | Peak   |
|------|------------------------------|--------|--------|
| +3V3 | ESP32-S3 active + Wi-Fi RX   | 80 mA  | —      |
| +3V3 | ESP32-S3 Wi-Fi TX burst      | —      | 500 mA |
| +3V3 | E-paper refresh burst        | 10 mA  | 40 mA  |
| +3V3 | microSD active               | 40 mA  | 100 mA |
| VSYS | Frontlight (both ch, boost in)| —     | ~150 mA|
| +3V3 | deep sleep (page held)       | ~20 µA | —      |

---

## 4. MCU pin map — ESP32-S3-WROOM-1

Avoided: strapping pins (0, 3, 45, 46 — 0 used for BOOT only), on-module
SPI flash/PSRAM pins (26–37). Display/SD share one SPI bus.

| Function        | GPIO   | Net          | Notes                            |
|-----------------|--------|--------------|----------------------------------|
| USB D−          | GPIO19 | USB_DM       | Native USB.                      |
| USB D+          | GPIO20 | USB_DP       | Native USB.                      |
| BOOT            | GPIO0  | BOOT         | Button to GND + 10 kΩ pull-up.   |
| EN / RESET      | EN     | EN           | 10 kΩ pull-up, 100 nF, button.   |
| SPI SCK         | GPIO12 | SPI_SCK      | Shared: EPD + SD.                |
| SPI MOSI        | GPIO11 | SPI_MOSI     | Shared: EPD + SD.                |
| SPI MISO        | GPIO14 | SPI_MISO     | SD only (EPD write-only).        |
| EPD CS          | GPIO10 | EPD_CS       |                                  |
| EPD DC          | GPIO9  | EPD_DC       | Data/command.                    |
| EPD RST         | GPIO8  | EPD_RST      | Active-low reset.                |
| EPD BUSY        | GPIO7  | EPD_BUSY     | Input.                           |
| SD CS           | GPIO13 | SD_CS        |                                  |
| SD card-detect  | GPIO21 | SD_CD        | Optional.                        |
| Button PREV     | GPIO4  | BTN_PREV     | To GND + 10 kΩ + 100 nF.         |
| Button NEXT     | GPIO5  | BTN_NEXT     |                                  |
| Button SELECT   | GPIO6  | BTN_SEL      |                                  |
| Battery sense   | GPIO1  | BAT_SENSE    | ADC1_CH0, ÷2.                    |
| Charge status   | GPIO2  | CHG_STAT     | MCP73831 STAT.                   |
| **Frontlight cold PWM** | GPIO15 | FL_COLD_PWM | LEDC PWM → TPS61165 #1 CTRL. |
| **Frontlight warm PWM** | GPIO16 | FL_WARM_PWM | LEDC PWM → TPS61165 #2 CTRL. |

Module power: all **3V3** pins → +3V3; all **GND** pins + **EPAD** → GND.
Decoupling: 100 nF per 3V3 pin + 10 µF and 22 µF bulk near the module.

---

## 5. E-Paper display — GDEY0426T82-FL01C (4.26", 800×480, SSD1677)

**Panel:** Good Display **GDEY0426T82-FL01C** — 4.26" reflective mono
E-Paper, **800×480**, 1-bit B/W, **controller SSD1677**, 4-wire SPI, with
the frontlight (§5b) laminated on (this is the integrated panel+frontlight
module). Active area 92.8 × 55.68 mm; module outline **105.33 × 62.37 ×
1.8 mm**. VCI/VDDIO = 3.3 V. Two FPC tails exit the bottom edge: a 24-pin
(EPD) and a 6-pin (frontlight).

**J4 — EPD FPC, 24-pin 0.5 mm** (from datasheet §5 + reference circuit §8.2):

| Pin | Name  | Connect to                    | Pin | Name  | Connect to                |
|-----|-------|-------------------------------|-----|-------|---------------------------|
| 1   | NC    | —                             | 13  | SCLK  | SPI_SCK (GPIO12)          |
| 2   | GDR   | Q2 gate (boost N-FET)         | 14  | SDI   | SPI_MOSI (GPIO11)         |
| 3   | RESE  | Q2 source / R_SENSE 2.2 Ω     | 15  | VDDIO | +3V3                      |
| 4   | NC    | —                             | 16  | VCI   | +3V3 (+ 1 µF)             |
| 5   | VSH2  | 4.7 µF → GND                  | 17  | VSS   | GND                       |
| 6   | TSCL  | NC (internal temp sensor)     | 18  | VDD   | 1 µF → GND                |
| 7   | TSDA  | NC                            | 19  | VPP   | NC (OTP program only)     |
| 8   | BS    | **GND** (selects 4-wire SPI)  | 20  | VSH1  | 4.7 µF → GND              |
| 9   | BUSY  | EPD_BUSY (GPIO7)              | 21  | VGH   | PREVGH (D6 cathode) + 4.7 µF |
| 10  | RES#  | EPD_RST (GPIO8)              | 22  | VSL   | 4.7 µF → GND              |
| 11  | D/C#  | EPD_DC (GPIO9)               | 23  | VGL   | PREVGL (D4) + 4.7 µF      |
| 12  | CS#   | EPD_CS (GPIO10)              | 24  | VCOM  | 1 µF → GND                |

**SSD1677 external DC-DC (reference circuit §8.2), fed from +3V3:**

- **L2** 47 µH, ≥500 mA (NR3015 class): +3V3 → switch node (Q2 drain).
- **Q2** Si1308EDL N-MOSFET (SOT-23): gate = GDR (pin 2), drain = switch
  node, source = RESE (pin 3). **R11** 1 M GDR→GND (gate pulldown);
  **R12** 2.2 Ω RESE→GND (current sense).
- **D4/D5/D6** MBR0530 Schottky (≥30 V, ≥500 mA): D6 builds PREVGH (→ VGH);
  D4/D5 build PREVGL (→ VGL) charge-pump path.
- **Caps (all ≥25 V, X5R/X7R):** 4.7 µF on VSH2, VSH1, VSL, VGL(PREVGL),
  VGH(PREVGH), and the +3V3 boost input; 1 µF on VCI, VDD, VCOM.
- Internal regulators produce VGH ≈ +20 V, VGL ≈ −20 V, VSH ≈ +15 V,
  VSL ≈ −15 V, VCOM ≈ −2 V — hence the ≥25 V cap rating.

EPD is write-only (no SDO/MISO). BS tied low = 4-wire SPI. Panel typical
current is small (~7.5 mA on VCI), so the boost input on +3V3 is light.

---

## 5b. Frontlight (part of GDEY0426T82-FL01C; drawing FL0426-S01C)

A light guide + LEDs laminated in front of the E-Paper for reading in the
dark, with **adjustable colour temperature** (cold + warm channels). Both
the frontlight drawing (FL0426-S01C) and the panel module mechanical
drawing show the same dual-channel 6-pin FPC.

**Electrical (from the datasheet drawing):**

- **Cold channel:** 5 white LEDs in **series** — VF ≤ 15 V, IF ≤ 15 mA.
- **Warm channel:** 5 white LEDs in **series** — VF ≤ 15 V, IF ≤ 15 mA.
- Operating 0–50 °C; LGP 61.40 × 104.10 mm; total thickness 0.685 mm.

**Connector J5 — 6-pin 0.5 mm FPC:**

| Pin | Signal | Connect to                                  |
|-----|--------|---------------------------------------------|
| 1   | LEDC+  | TPS61165 #1 boost output (cold string anode)|
| 2   | LEDC−  | TPS61165 #1 FB node → R_SET → GND (cathode) |
| 3   | NC     | —                                           |
| 4   | NC     | —                                           |
| 5   | LEDW+  | TPS61165 #2 boost output (warm string anode)|
| 6   | LEDW−  | TPS61165 #2 FB node → R_SET → GND (cathode) |

**Driver (per channel) — TPS61165 (see ADR 0005):**

- VIN = VSYS; L = 10 µH; boost Schottky D (≥ 20 V, e.g. PMEG4010); Cout =
  1 µF / ≥ 25 V; Cin = 1 µF; R_SET = 0.2 V / I_LED (≈ 13 Ω for 15 mA —
  start at ~10 mA and tune).
- LED string anode = boost output; string cathode returns into the FB pin
  (driver regulates 200 mV across R_SET → constant current).
- **CTRL** driven by MCU LEDC PWM: FL_COLD_PWM (GPIO15) / FL_WARM_PWM
  (GPIO16). Brightness = combined duty; colour temperature = cold:warm duty
  ratio.

> Confirmed by both datasheets: 5 LEDs **in series** per channel, VF ≤ 15 V,
> IF ≤ 15 mA. Size Cout ≥ 20 V and set R_SET for your target brightness
> (start ~10 mA and tune up to the 15 mA max).

---

## 6. microSD (optional, SPI mode)

CS = SD_CS, CLK = SPI_SCK, DI = SPI_MOSI, DO = SPI_MISO; 10 kΩ pull-ups on
CS/DI/DO/CLK. VDD = +3V3 (10 µF + 100 nF). Optional card-detect → SD_CD.
First candidate to depopulate if area is tight (on-module flash suffices).

---

## 7. USB-C

USB 2.0 receptacle. VBUS→VBUS (4.7 µF + 100 nF). Both **CC1/CC2** get
**5.1 kΩ to GND** (Rd, sink). D+/D− → USB_DP/USB_DM (GPIO20/19), each side's
two data pins joined. Shield → GND via bead or 1 MΩ ∥ 4.7 nF. Recommended:
USBLC6-2 ESD on VBUS + D±.

---

## 8. Reset / boot

- **EN:** 10 kΩ pull-up to +3V3, 100 nF to GND, RESET button to GND.
- **BOOT (GPIO0):** 10 kΩ pull-up, BOOT button to GND.
- Native USB supports auto-download → no DTR/RTS transistor circuit (ADR
  0004). Manual entry: hold BOOT, tap RESET, release BOOT.

---

## 9. Net list (schematic-as-text)

- **GND**: USB shield/GND, USB-C GND, MCP73831.VSS, AP2112.GND, module GND +
  EPAD, all decoupling returns, EPD VSS, SD GND, button returns, divider low
  side, LED cathode return, Q1 gate pulldown, both TPS61165 GND + R_SET low
  side, FL boost input cap returns.
- **VBUS**: USB-C VBUS, MCP73831.VDD, D1 anode, Q1 gate resistor, CHG_STAT
  LED anode resistor, 4.7 µF.
- **VBAT**: MCP73831.VBAT, Q1 source, JST-PH +, 4.7 µF, divider top.
- **VSYS**: Q1 drain, D1 cathode, AP2112.VIN + EN, both TPS61165 VIN + Cin,
  1 µF.
- **+3V3**: AP2112.VOUT, module 3V3 pins, EPD VDD/VDDIO/VCI, SD VDD, all
  pull-ups, decoupling, 10/22 µF bulk.
- **SPI_SCK / SPI_MOSI**: GPIO12/11 → EPD SCLK/SDA + SD CLK/DI.
- **SPI_MISO**: GPIO14 → SD DO (pull-up).
- **EPD_CS/DC/RST/BUSY**: GPIO10/9/8/7 ↔ EPD (J4) CS#/D-C#/RES#/BUSY.
- **EPD J4 supplies**: VDDIO/VCI = +3V3; VSS = GND; BS (pin8) = GND.
- **EPD boost**: +3V3 → L2 → EPD_SW (Q2 drain, D6 anode, D4 anode).
  GDR → Q2 gate + R11(1M)→GND. RESE → Q2 source + R12(2.2Ω)→GND.
  PREVGH = D6.K → VGH(21) + 4.7µF. PREVGL = D4/D5 network → VGL(23) + 4.7µF.
  4.7µF each on VSH1(20)/VSH2(5)/VSL(22); 1µF each on VCI(16)/VDD(18)/VCOM(24).
  VPP(19), TSCL(6), TSDA(7), pins 1/4 = NC.
- **SD_CS / SD_CD**: GPIO13 / GPIO21.
- **BTN_PREV/NEXT/SEL**: GPIO4/5/6 → button→GND + pull-up + 100 nF.
- **BOOT / EN**: GPIO0 / EN with pull-ups + buttons; EN has 100 nF.
- **USB_DP/USB_DM**: GPIO20/19 ↔ USB-C D+/D−.
- **BAT_SENSE**: divider mid → GPIO1 + 100 nF. **CHG_STAT**: MCP73831.STAT →
  LED + GPIO2.
- **FL_COLD_PWM / FL_WARM_PWM**: GPIO15/16 → TPS61165 #1/#2 CTRL.
- **FL_C_OUT / FL_W_OUT** (~15 V): TPS61165 #x boost out → J5 pin1 / pin5.
- **FL_C_FB / FL_W_FB**: J5 pin2 / pin6 → TPS61165 #x FB → R_SET → GND.

---

## 10. PCB guidance

- **Stack-up:** 2-layer, 1.6 mm FR-4, 1 oz. Top = signals + parts, bottom =
  ground pour.
- **Board outline placeholder:** ~66 × 115 mm to sit behind the ~61 × 104 mm
  display; finalise to the enclosure. (`.kicad_pcb` has a rectangle to edit.)
- **Ground:** continuous bottom pour; stitch to top. Honour the module
  antenna keep-out (module at a board edge, no copper under antenna).
- **Power:** wide VBUS/VBAT/VSYS/+3V3 traces (≥ 0.4 mm). Bulk caps at the LDO
  out and module 3V3 pins.
- **Frontlight boost:** put both TPS61165 stages + inductors in one corner,
  **away from the antenna and BAT_SENSE**; short switch loops, local ground,
  Cout close to the IC. Keep the ~15 V FL nets clear of sensitive analog.
- **USB:** D+/D− as a ~90 Ω differential pair, short, over solid ground.
- **EPD/FL FPC:** keep SPI short; FPC connectors on the display-facing edge.
- **Test points:** 3V3, GND, VBAT, VSYS, EN, BOOT, SPI, FL outputs.

---

## 11. Verification status

| Item                          | State                                             |
|-------------------------------|---------------------------------------------------|
| Architecture / power design   | ✅ captured here + ADRs                            |
| Frontlight subsystem          | ✅ specified (§5b, ADR 0005)                       |
| Net connectivity              | ✅ specified (§9) + `gen_netlist_skidl.py`         |
| BOM                           | ✅ `BOM.csv` (verify stock/footprints before order)|
| KiCad project/config          | ✅ scaffold opens in KiCad 8                       |
| KiCad schematic capture       | ⛔ **to do in KiCad** (also runs via CI ERC)       |
| KiCad PCB layout + routing    | ⛔ **to do in KiCad** (CI DRC)                     |
| ERC / DRC clean               | ⛔ **to do** — locally + CI                        |
| EPD panel FPC pinout/controller | ✅ locked from GDEY0426T82-FL01C datasheet (§5)  |
| Frontlight LED VF/IF          | ✅ confirmed dual, 5-series, VF≤15V IF≤15mA        |

CI (`.github/workflows/kicad.yml`) runs `kicad-cli` ERC/DRC + export once
the design is captured. See `/docs/runbook.md`.

---

## 12. Open questions for the owner

1. **Frontlight current** — target brightness / IF per channel (≤ 15 mA)?
2. **microSD** — keep, or on-module flash only?
3. **Enclosure & battery** — outline, connector/button placement, cell
   capacity (sets charge current). Display module is 105.33 × 62.37 mm.
4. **Buck-boost vs LDO** — how much 3.0–3.4 V battery tail must be usable?
5. **Power switch** — hard slide switch on VBAT, or firmware deep-sleep?
