# Mini E-Reader — Hardware Design

> Reference design v0.1. This is the electrical "source of truth": block
> diagram, power architecture, net-by-net connectivity, MCU pin map, and
> component notes. The KiCad schematic/PCB in this folder are captured
> **from** this document — if they ever disagree, this document wins until
> the KiCad ERC/netlist is confirmed clean and this note is removed.

**Status:** design captured, not yet drawn/routed in KiCad. See
[Verification status](#verification-status).

---

## 1. Overview

A pocket e-reader built around an **ESP32-S3** module driving a small
**monochrome SPI E-Paper** panel, powered by a **single-cell LiPo** with
**USB-C** charging and native-USB programming. Optional **microSD** for
book storage. Three tactile buttons for navigation.

| Attribute        | Value                                                        |
|------------------|-------------------------------------------------------------|
| MCU              | ESP32-S3-WROOM-1 (N8R2 or N16R8 module)                      |
| Display          | 2.13" mono E-Paper, SSD1680 controller, 24-pin 0.5 mm FPC   |
| Wireless         | Wi-Fi b/g/n + BLE 5 (on-module)                             |
| Storage          | On-module flash (8/16 MB) + optional microSD (SPI)          |
| Power in         | USB-C (5 V) and/or 1S LiPo (3.0–4.2 V)                      |
| Charger          | MCP73831, 500 mA (PROG-set)                                  |
| System rail      | 3.3 V via AP2112K-3.3 LDO (600 mA)                          |
| Programming      | Native USB (USB-Serial-JTAG), no external UART bridge       |
| Board            | 2-layer, ~1.6 mm FR-4, hand/JLCPCB-assemblable              |

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
                  │   ┌───────────────┐  VSYS  ┌───────────┐ │
                  │   │ load-share    ├────────┤ AP2112-3.3│ │
                  │   │ P-FET + diode │        │   LDO     │ │
                  │   └───────────────┘        └─────┬─────┘ │
                  │                                 +3V3     │
                  │                                   │      │
             ┌────▼───────────────────────────────────▼──────▼───┐
             │                 ESP32-S3-WROOM-1                    │
             │  USB  SPI(SCK/MOSI/MISO)  GPIO  ADC  BOOT/EN        │
             └───┬───────┬───────────────┬─────┬──────┬───────────┘
                 │       │               │     │      │
             (native)  ┌─▼──────┐    ┌───▼──┐  │   ┌──▼───┐
                       │ E-Paper│    │microSD│ VBAT│ 3x   │
                       │ SSD1680│    │  (SPI)│ sense│ btns │
                       │ 24p FPC│    └───────┘ (÷2) └──────┘
                       └────────┘
```

---

## 3. Power architecture

Three sources, one system rail, one regulated rail.

- **VBUS** — 5 V from USB-C. Feeds the charger and (via the load-share
  path) the system when USB is plugged in.
- **VBAT** — 1S LiPo, 3.0–4.2 V, on a JST-PH 2-pin. Charged from VBUS.
- **VSYS** — the OR of VBUS and VBAT. Powers the LDO.
- **+3V3** — regulated 3.3 V for the MCU, display logic, SD, and pull-ups.

### 3.1 Charging — MCP73831 (SOT-23-5)

| Pin | Net    | Notes                                                    |
|-----|--------|----------------------------------------------------------|
| 1 STAT | CHG_STAT | Open-drain. LED to VBUS via 1 kΩ; also to GPIO (sense). |
| 2 VSS  | GND    |                                                          |
| 3 VBAT | VBAT   | 4.7 µF to GND.                                           |
| 4 VDD  | VBUS   | 4.7 µF to GND.                                           |
| 5 PROG | via R_PROG to GND | 2.0 kΩ → **500 mA** charge current.          |

`I_chg ≈ 1000 V / R_PROG`. 2.0 kΩ → 500 mA. Use 5 kΩ (200 mA) for small
cells. Keep charge current ≤ 1C of the pack.

### 3.2 Load-share (USB priority) — DMG2305UX P-FET + Schottky

Goal: when USB is present the system runs from USB (and the battery only
charges); when USB is absent the system runs from the battery. This avoids
charging *and* discharging the cell at the same time.

- **Q1 (P-FET), body-diode from VBAT→VSYS:** source = VBAT, drain = VSYS,
  gate pulled to GND through 100 kΩ, and tied to VBUS through 100 kΩ.
  - No USB: gate ≈ 0 V, Vgs ≈ −VBAT → **on**, battery feeds VSYS.
  - USB present: gate ≈ 5 V > source → Vgs ≈ 0/positive → **off**, battery
    isolated from VSYS.
- **D1 Schottky (VBUS→VSYS):** SS14/PMEG type. Supplies VSYS from USB when
  plugged, ~0.3 V drop.

> **ADR-0003 alternative:** for a "proper" power-path (seamless, no diode
> drop, DPPM) swap the MCP73831 + P-FET for an **MCP73871** power-path
> charger. Chosen the simpler discrete load-share for v0.1 to keep BOM and
> layout small; revisit if battery-while-charging behaviour matters.

### 3.3 Regulation — AP2112K-3.3 (SOT-23-5)

| Pin | Net  | Notes                                    |
|-----|------|------------------------------------------|
| 1 VIN | VSYS | 1 µF to GND.                            |
| 2 GND | GND  |                                          |
| 3 EN  | VSYS | Enabled whenever VSYS present. (Optional: gate with a soft-power switch.) |
| 4 NC  | —    |                                          |
| 5 VOUT| +3V3 | 1 µF (min) to GND; add 10 µF bulk.      |

**Dropout note:** an LDO cannot boost. At VBAT ≈ 3.3–3.4 V the 3.3 V rail
begins to sag (AP2112 dropout ≈ 250 mV @ 300 mA). E-paper draws current
only in bursts, and ESP32-S3 Wi-Fi TX peaks ~500 mA — size bulk caps
generously (≥ 22 µF near the module). For full battery utilisation down to
3.0 V, ADR-0003 notes a buck-boost (TPS63020) as the alternative.

### 3.4 Battery telemetry

VBAT → 100 kΩ / 100 kΩ divider → **BAT_SENSE** → ESP32-S3 ADC (GPIO1,
ADC1_CH0), with 100 nF to GND. Divider halves 4.2 V → 2.1 V, inside the
ADC range. Firmware reads state-of-charge; CHG_STAT reads charge state.

### 3.5 Power budget (rough)

| Rail | Load                         | Typ    | Peak   |
|------|------------------------------|--------|--------|
| +3V3 | ESP32-S3 active + Wi-Fi RX   | 80 mA  | —      |
| +3V3 | ESP32-S3 Wi-Fi TX burst      | —      | 500 mA |
| +3V3 | E-paper refresh burst        | 10 mA  | 30 mA  |
| +3V3 | microSD active               | 40 mA  | 100 mA |
| +3V3 | deep sleep (page held)       | ~20 µA | —      |

---

## 4. MCU pin map — ESP32-S3-WROOM-1

Avoided: strapping pins (0, 3, 45, 46 — 0 used for BOOT only), on-module
SPI flash/PSRAM pins (26–37), and USB pins reserved below. All display/SD
share one SPI bus.

| Function        | GPIO   | Net        | Notes                              |
|-----------------|--------|------------|------------------------------------|
| USB D−          | GPIO19 | USB_DM     | Native USB (USB-Serial-JTAG).      |
| USB D+          | GPIO20 | USB_DP     | Native USB.                        |
| BOOT            | GPIO0  | BOOT       | Button to GND + 10 kΩ pull-up.     |
| EN / RESET      | EN     | EN         | 10 kΩ pull-up, 100 nF to GND, btn. |
| SPI SCK         | GPIO12 | SPI_SCK    | Shared: EPD + SD.                  |
| SPI MOSI        | GPIO11 | SPI_MOSI   | Shared: EPD + SD.                  |
| SPI MISO        | GPIO14 | SPI_MISO   | SD only (EPD is write-only).       |
| EPD CS          | GPIO10 | EPD_CS     |                                    |
| EPD DC          | GPIO9  | EPD_DC     | Data/command.                      |
| EPD RST         | GPIO8  | EPD_RST    | Active-low reset.                  |
| EPD BUSY        | GPIO7  | EPD_BUSY   | Input, panel busy.                 |
| SD CS           | GPIO13 | SD_CS      |                                    |
| SD card-detect  | GPIO21 | SD_CD      | Optional, to GND when inserted.    |
| Button PREV     | GPIO4  | BTN_PREV   | To GND + 10 kΩ pull-up + 100 nF.   |
| Button NEXT     | GPIO5  | BTN_NEXT   | "                                  |
| Button SELECT   | GPIO6  | BTN_SEL    | "                                  |
| Battery sense   | GPIO1  | BAT_SENSE  | ADC1_CH0, ÷2 divider.              |
| Charge status   | GPIO2  | CHG_STAT   | Read MCP73831 STAT (open-drain).   |

Module power: all **3V3** pins → +3V3; all **GND** pins → GND; **EPAD** →
GND. Decoupling: 100 nF at each 3V3 pin + 10 µF and 22 µF bulk near module.

---

## 5. E-Paper display

**Reference panel:** GDEY0213B74 (2.13", 250×122, SSD1680, 24-pin 0.5 mm
FPC, "B74"/DES-compatible pinout). **The FPC pinout differs between panels
— confirm against your exact panel's datasheet before ordering.**

Interface is 4-wire SPI plus DC/RST/BUSY (see pin map). The SSD1680 has an
integrated charge pump; external parts are decoupling capacitors on the
pump/VCOM pins — no separate high-voltage boost IC or inductor is needed.

### 5.1 24-pin FPC connector (GDEY0213B74 / SSD1680 typical)

| Pin | Signal | Connect to           | Pin | Signal | Connect to             |
|-----|--------|----------------------|-----|--------|------------------------|
| 1   | NC     | —                    | 13  | BS1    | GND (selects 4-wire SPI)|
| 2   | GDR    | 1 µF → GND / FET*    | 14  | BUSY   | EPD_BUSY               |
| 3   | RESE   | 0.47 Ω sense*        | 15  | RST#   | EPD_RST                |
| 4   | NC     | —                    | 16  | D/C#   | EPD_DC                 |
| 5   | VSH2   | 1 µF → GND           | 17  | CS#    | EPD_CS                 |
| 6   | VGL    | 1 µF → GND           | 18  | SCLK   | SPI_SCK                |
| 7   | VGH    | 1 µF → GND           | 19  | SDA    | SPI_MOSI               |
| 8   | VSH1   | 1 µF → GND           | 20  | VDDIO  | +3V3                   |
| 9   | VSL    | 1 µF → GND           | 21  | VCI    | +3V3 (+ 1 µF)          |
| 10  | VCOM   | 1 µF → GND           | 22  | VSS    | GND                    |
| 11  | VDDH?  | 1 µF → GND           | 23  | VSS    | GND                    |
| 12  | VPP?   | (prog, leave/NC)     | 24  | VDD    | +3V3 (+ 1 µF)          |

\* GDR/RESE/VSH2 relate to the on-chip source-driver boost; some panels
integrate these and the pin function/order changes. **Match the datasheet
of the specific panel.** The safe, panel-agnostic signals are the SPI/logic
group (SCLK, SDA, CS#, D/C#, RST#, BUSY, BS1) and the supplies (VCI, VDDIO,
VDD, VSS).

---

## 6. microSD (optional, SPI mode)

Push-pull or hinge socket, SPI mode: CS=SD_CS, CLK=SPI_SCK, DI=SPI_MOSI,
DO=SPI_MISO. 10 kΩ pull-ups on CS, DI, DO, CLK. VDD = +3V3 with 10 µF +
100 nF. Optional card-detect switch → SD_CD to GND.

> If board area is tight, microSD is the first thing to drop — the on-module
> 8/16 MB flash holds a meaningful library of compressed text. Tracked in
> ADR-0002.

---

## 7. USB-C

USB 2.0 receptacle (16-pin). VBUS→VBUS (+4.7 µF bulk, 100 nF). GND→GND.
Both **CC1 and CC2** each get a **5.1 kΩ to GND** (Rd — declares a
UFP/sink so a source supplies 5 V). D+/D− tie to USB_DP/USB_DM (GPIO20/19)
with the two data pins of each side joined. Shield → GND through a bead or
1 MΩ ∥ 4.7 nF. Optional: 5 V TVS on VBUS and D±.

---

## 8. Reset / boot

- **EN**: 10 kΩ pull-up to +3V3, 100 nF to GND, RESET button to GND.
- **BOOT (GPIO0)**: 10 kΩ pull-up to +3V3, BOOT button to GND.
- Native USB supports auto-download, so the two-transistor DTR/RTS
  auto-reset circuit is **not** required (ADR-0004). To force the ROM
  bootloader manually: hold BOOT, tap RESET, release BOOT.

---

## 9. Net list (schematic-as-text)

Every net and its members. This is what the KiCad schematic must realise;
`gen_netlist_skidl.py` encodes the same graph programmatically.

- **GND**: USB shield/GND, USB-C GND, MCP73831.VSS, AP2112.GND, all module
  GND + EPAD, all decoupling cap returns, EPD VSS/BS1, SD GND, button
  returns, divider low side, LED cathode return, Q1 gate pulldown.
- **VBUS**: USB-C VBUS, MCP73831.VDD, D1 anode, Q1 gate resistor (to VBUS),
  CHG_STAT LED anode resistor, bulk 4.7 µF.
- **VBAT**: MCP73831.VBAT, Q1 source, JST-PH +, 4.7 µF, divider top.
- **VSYS**: Q1 drain, D1 cathode, AP2112.VIN, AP2112.EN, 1 µF.
- **+3V3**: AP2112.VOUT, module 3V3 pins, EPD VDD/VDDIO/VCI, SD VDD, all
  pull-ups, decoupling caps, bulk 10/22 µF.
- **SPI_SCK**: GPIO12, EPD SCLK, SD CLK.
- **SPI_MOSI**: GPIO11, EPD SDA, SD DI.
- **SPI_MISO**: GPIO14, SD DO (pull-up).
- **EPD_CS/EPD_DC/EPD_RST/EPD_BUSY**: GPIO10/9/8/7 ↔ EPD CS#/D-C#/RST#/BUSY.
- **SD_CS**: GPIO13 ↔ SD CS (pull-up). **SD_CD**: GPIO21 ↔ card-detect.
- **BTN_PREV/NEXT/SEL**: GPIO4/5/6, each to a button→GND, pull-up, 100 nF.
- **BOOT**: GPIO0, BOOT button→GND, 10 kΩ pull-up.
- **EN**: module EN, 10 kΩ pull-up, 100 nF, RESET button→GND.
- **USB_DP/USB_DM**: GPIO20/19 ↔ USB-C D+/D−.
- **BAT_SENSE**: divider mid, GPIO1, 100 nF.
- **CHG_STAT**: MCP73831.STAT, LED (via R to VBUS), GPIO2.

---

## 10. PCB guidance

- **Stack-up:** 2-layer, 1.6 mm FR-4, 1 oz copper. Top = signals + parts,
  bottom = ground pour + a few signals.
- **Ground:** continuous bottom pour; stitch top pour to it. Keep the RF
  section of the module (antenna keep-out) clear of copper — follow the
  ESP32-S3-WROOM-1 module keep-out: **no copper under the antenna**, module
  at a board edge, antenna pointing off-board.
- **Power:** wide traces VBUS/VBAT/VSYS/+3V3 (≥ 0.4 mm). Bulk caps close to
  the LDO out and module 3V3 pins. Charger caps close to the IC.
- **USB:** route D+/D− as a ~90 Ω differential pair, short, matched, over
  solid ground; series 0 Ω placeholders optional.
- **EPD FPC:** keep the SPI group short; the pump caps hug the connector.
- **Buttons:** on an accessible edge; pull-ups near the MCU.
- **Test points:** 3V3, GND, VBAT, EN, BOOT, TX/RX-equivalent (USB), SPI.
- **Fiducials:** 2–3 if you want machine assembly.

---

## 11. Verification status

| Item                          | State                                             |
|-------------------------------|---------------------------------------------------|
| Architecture / power design   | ✅ captured in this doc + ADRs                     |
| Net connectivity              | ✅ specified (§9) + `gen_netlist_skidl.py`         |
| BOM                           | ✅ `BOM.csv` (verify stock/footprints before order)|
| KiCad project/config          | ✅ scaffold present, opens in KiCad 8              |
| KiCad schematic capture       | ⛔ **to do in KiCad** (no EDA tooling in CI env)   |
| KiCad PCB layout + routing    | ⛔ **to do in KiCad**                              |
| ERC / DRC clean               | ⛔ **to do — run in KiCad**                        |
| EPD FPC pinout vs real panel  | ⚠️ **confirm against your panel datasheet**       |

See `docs/runbook.md` for how to open the project, run ERC/DRC, and export
fabrication files.

---

## 12. Open questions for the owner

1. **Display size/panel** — 2.13" assumed. 2.9" (296×128) or 4.2" also
   common; changes FPC pinout and board size.
2. **microSD** — keep, or rely on on-module flash only?
3. **Enclosure & battery** — sets board outline, connector placement,
   button layout, and cell capacity (charge-current choice).
4. **Buck-boost vs LDO** — how much of the 3.0–3.4 V battery tail must be
   usable? (ADR-0003.)
5. **Power switch** — hard slide switch on VBAT, or firmware deep-sleep only?
