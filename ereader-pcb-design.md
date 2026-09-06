# Mini E-Reader — PCB Design Spec (Rev C)

Schematic-level ref. Not gerbers. Follow in KiCad. All part numbers byte-exact — verify against latest datasheets before order.

Rev C: frontlight FULLY RESOLVED from FL0426-S01C (2 independent 4-wire strings), CHG_CE hardware fallback locked in, magnet alignment silk markers, battery band set.

---

## 1. Decisions / assumptions

- MCU = **ESP32-S3-WROOM-1-N16R8** (kept). 8 MB octal PSRAM holds 800×480×2-plane framebuffer (96 KB) + EPUB render + fonts. 16 MB flash = OTA A/B + fonts + cache.
- Panel = **GDEY0426T82-FL01C** (frontlight cool/warm, 800×480, SSD1677, SPI, 3V3 logic). Panel FPC = 24-pin 0.5 mm. Frontlight FPC = 6-pin 0.5 mm (**FL0426-S01C**, confirmed §7).
- Battery = single-cell Li-Po, **~1000–2000 mAh, thin large-area**. Fast charge not needed → conservative Ichg (§8).
- USB-C = charge + native USB-OTG data + program (one connector; native USB-Serial/JTAG on S3).
- SoC charge cap (stop 80 / resume 50) = ESP32 over I2C, + hardware CE fallback (§8).
- Program/recovery = native USB + BOOT + RESET buttons.

---

## 2. Block diagram

```
              USB-C (16p)
          VBUS │ CC1/CC2(5.1k) │ D+ D-  │ SBU(nc)
               │               │        │
        ┌──────┴──────┐   ┌────┴────┐   │
   ESD  │ USBLC6-2SC6 │   │(to S3   │   ESD (same array)
        └──────┬──────┘   │ USB19/20)│
               │VBUS               │
        ┌──────┴───────┐           │
        │ BQ25628E     │ I2C0(0x6B)│
        │ 2A buck chg  ├───────────┼──┐
        │ CE ◄─GPIO14  │           │  │
        └──┬────────┬──┘           │  │I2C0
        BAT│      SYS│             │  │
     ┌─────┴───┐  ┌──┴─────────┐   │  │
     │ Li-Po 1S│  │ TPS62840   │   │  │
     └────┬────┘  │ buck 3V3   │   │  │
      VBAT│       └──┬─────────┘   │  │
     ┌────┴─────┐ 3V3│             │  │
     │MAX17048  │    ├─────────────┼──┼──► ESP32-S3-WROOM-1-N16R8
     │gauge 0x36│────┘ I2C0        │  │      │  │  │
     └──────────┘                  │  │      │  │  └─I2C1(0x36)─► LM3630A ─► FL 6p FPC
                                   USB │      │  └─SPI──────────► EPD 24p FPC
                                       └─USB  └─SPI──────────► microSD
   Inputs: 3× side btn + SLLB510200 (CW/CCW/push) → GPIO pull-up, wake
   Prog:   BOOT(GPIO0) + RESET(EN) tactiles
```

---

## 3. BOM (core)

| Ref | Part | Fn | Notes |
|-----|------|-----|------|
| U1 | ESP32-S3-WROOM-1-N16R8 | MCU+radio | pre-certified module (FCC/IC/CE). Follow integration guide |
| U2 | TI **BQ25628E** | 1S I2C buck charger 2A | addr 0x6B. EN_CHG reg + CE pin (§8) |
| U3 | Maxim **MAX17048G+T10** | fuel gauge (ModelGauge, no sense R) | addr 0x36, I2C0 |
| U4 | TI **LM3630A** | dual-string I2C backlight boost | addr 0x36 → I2C1 (§7) |
| U5 | TI **TPS62840** | 3V3 buck 750 mA, Iq 60 nA | LDO alt if area-tight |
| U6 | ST **USBLC6-2SC6** | USB ESD array | D+/D-/CC/VBUS |
| J1 | USB-C recept 16-pin (e.g. GCT USB4085) | power+data | |
| J2 | 24-pin 0.5 mm FPC, bottom-contact | EPD | flip-lock |
| J3 | 6-pin 0.5 mm FPC | frontlight | 1=C+ 2=C− 3=NC 4=NC 5=W+ 6=W− |
| J4 | microSD push-pull holder | storage | |
| SW1–3 | tactile SMD (side) | page/menu | |
| SW4 | ALPS **SLLB510200** | lever+push (CW/CCW/press) | 10 mA/5 V max, 9.5×8.8×2.2 mm |
| SW5 | tactile SMD | BOOT | GPIO0→GND momentary |
| SW6 | tactile SMD | RESET | EN→GND momentary |
| — | 5.1 kΩ ×2 | CC1/CC2 Rd (sink) | |
| — | 100 kΩ | EN pull-up + 1 µF | module EN weak ~2 MΩ |
| — | 100 kΩ pull-up ×2 | EPD_CS, SD_CS idle-high thru boot | §5 |
| — | 100 kΩ pull-down ×1 | FL_HWEN (FL off at boot) | §5 |
| — | 100 kΩ strap ×1 | CHG_CE boot-default = charge-on | §8 |
| — | 4.7 kΩ ×4 | I2C0 + I2C1 pull-ups | |
| — | SSD1677 booster caps + L | per Good Display ref schematic | §6 |

---

## 4. Power tree

```
USB VBUS 5V ──► BQ25628E ──► SYS ──► TPS62840 ──► 3V3 rail
                    └──────► BAT (Li-Po 1S)
3V3  → U1 (≥500 mA headroom; RF bursts >avg), microSD, EPD VDD, gauge, logic
VBAT → LM3630A boost → ~15–18 V (2×5-series strings), Iset ≤15 mA/ch
VBAT → MAX17048 sense
```

- 3V3 survives S3 TX burst (~0.5 A): TPS62840 (750 mA) + 22 µF bulk at module 3V3.
- **I2C clash fix = 2 buses (locked).** Keeps sense-less MAX17048 + dual-ch LM3630A. 1-bus alt only if forced: gauge → BQ27441-G1A @0x55 (needs sense R).

---

## 5. ESP32-S3 pin map

Safe pins: 1–18, 21, 38–42, 47, 48. **Never 26–37** (26–32 flash, 33–37 octal PSRAM). USB 19/20 native. GPIO21 = static enable only.

| Signal | GPIO | Dir | Note |
|--------|------|-----|------|
| EPD_SCLK | 12 | O | SPI ≤10–20 MHz |
| EPD_MOSI | 11 | O | DIN |
| EPD_CS | 10 | O | 100k pull-up (idle-high thru boot) |
| EPD_DC | 9 | O | |
| EPD_RST | 8 | O | boot-low harmless (re-reset in init) |
| EPD_BUSY | 7 | I | |
| SD_SCK | 41 | O | own SPI bus |
| SD_MOSI | 42 | O | |
| SD_MISO | 40 | I | |
| SD_CS | 39 | O | 100k pull-up (idle-high) |
| I2C0_SDA | 17 | IO | charger 0x6B + gauge 0x36 |
| I2C0_SCL | 18 | IO | |
| I2C1_SDA | 16 | IO | LM3630A 0x36 |
| I2C1_SCL | 38 | IO | |
| BTN_A | 4 | I | pull-up, RTC-wake |
| BTN_B | 5 | I | pull-up, RTC-wake |
| BTN_C | 6 | I | pull-up, RTC-wake |
| LEV_CW | 1 | I | pull-up, RTC-wake |
| LEV_CCW | 2 | I | pull-up, RTC-wake |
| LEV_PUSH | 15 | I | pull-up, RTC-wake |
| CHG_INT | 47 | I | BQ25628E /INT |
| GAUGE_ALRT | 48 | I | MAX17048 /ALRT (low-SoC wake) |
| FL_HWEN | 21 | O | LM3630A HWEN; 100k pull-down (FL off at boot) |
| CHG_CE | 14 | O | BQ25628E CE; 100k strap = charge-on default (§8) |
| BOOT | 0 | I | strap; SW5→GND; module 10k pull-up |
| RESET | EN | I | SW6→GND; 100k pull-up + 1 µF |
| USB_D- | 19 | — | native → J1 |
| USB_D+ | 20 | — | native → J1 |

Free/unused after this map: 3(strap), 13. All 6 btn/lever inputs RTC-capable → wake sources; assign BTN_A + LEV_PUSH, ext1-mask rest.

### Glitch-safe by design
- ⚠ GPIO1–18 ~60 µs low pulse at power-up; 18/19/20 glitch high. Audited:
- EPD_CS(10) + SD_CS(39): 100k pull-up → idle high thru boot → no spurious select. ✓
- FL_HWEN(21): 100k pull-down → frontlight OFF until firmware. ✓
- CHG_CE(14): 100k strap to charge-on level → boot-low pulse benign (charger debounces; default is charge-on anyway). ✓
- EPD_RST(8): boot-low benign (re-reset in init). ✓
- I2C0/1 + all btn/lever: pull-ups present → absorbed. ✓
- No glitch-sensitive load (gate/latch/relay) hangs unpulled off a glitchy pin. Glitch-safe. ✓

---

## 6. EPD subsystem (SSD1677)

4-line SPI (SDA-in only; write-mostly). Tie **BS1** for 4-wire SPI.

Match the **panel datasheet pin numbers exactly** (24-pin EPD FPC, 0.5 mm):
- Logic: SCLK, SDA(MOSI), CS, DC, RST, BUSY, VDD=3V3, VSS=GND, BS (tie low = 4-wire SPI).
- Booster/analog: GDR, RESE, VSH1/VSH2, VSL, VGL, VGH, VCOM, VCI, VDD, VPP — external DC-DC + reservoir caps per the **Good Display reference circuit** ("ESP32 Sample Code" zip). Copy 1:1; rail values non-negotiable. Short FPC stubs; guard-ground under booster caps.

**External DC-DC — exact values** (ported from `hardware/DESIGN.md` §5; verify against the panel datasheet reference circuit before order. Designators are from that source — renumber to match the `ereader` schematic):
- **L** 47 µH, ≥500 mA (NR3015 class): +3V3 → switch node (boost FET drain).
- **Q** Si1308EDL N-MOSFET (SOT-23): gate = GDR, drain = switch node, source = RESE. **R** 1 MΩ GDR→GND (gate pulldown) + **R** 2.2 Ω RESE→GND (current sense).
- **D×3** MBR0530 Schottky (≥30 V, ≥500 mA): one builds PREVGH (→ VGH); two build the PREVGL (→ VGL) charge-pump path.
- **Caps (all ≥25 V, X5R/X7R):** 4.7 µF on VSH1, VSH2, VSL, VGL/PREVGL, VGH/PREVGH, and the +3V3 boost input; 1 µF on VCI, VDD, VCOM.
- Internal rails: **VGH ≈ +20 V, VGL ≈ −20 V, VSH ≈ +15 V, VSL ≈ −15 V, VCOM ≈ −2 V** — hence the ≥25 V cap rating. Panel VCI draw is small (~7.5 mA), so the +3V3 boost input is light.

- Mechanical: EPD 24p FPC + FL 6p FPC both exit the bottom edge → place J2 + J3 adjacent on bottom edge.

---

## 7. Frontlight (LM3630A) — CONFIRMED

Source: **FL0426-S01C** drawing. Two **independent 4-wire** series strings (NOT common-anode):

| FL pin | Net | String |
|---|---|---|
| 1 | LED C+ | Cold anode |
| 2 | LED C− | Cold cathode |
| 3 | NC | — |
| 4 | NC | — |
| 5 | LED W+ | Warm anode |
| 6 | LED W− | Warm cathode |

- Cold = 5 series LED, Warm = 5 series LED. Per-LED Vf 2.8–3.6 V → string VF ≤15 V; IF ≤15 mA each. (10 LEDs total; "7 LED" web spec = wrong rev.)

**Final wiring (LM3630A single boost, dual sink):**
```
LM3630A OUT (boost) ──┬── FL pin1 (C+)
                      └── FL pin5 (W+)      ← both anodes tie to OUT
FL pin2 (C−) ── LM3630A LED1 sink (Bank A = COOL)
FL pin6 (W−) ── LM3630A LED2 sink (Bank B = WARM)
FL pin3,4 = NC
```
- Equal string length → shared boost OUT is efficient; boost regulates to the active sink. Set OVP ≥18 V (5×3.6). Program each bank Iset ≤15 mA; PWM per bank.
- Independent on/off + brightness per bank → full cool/warm blend + global dim. Firmware over I2C1 (0x36). FL_HWEN(21) = hard off in standby.
- No common-anode strap option needed (topology confirmed 4-wire). Drop that DNP.
- EMI: boost L + Cout loop <5 mm, local ceramics, far from antenna + FPC.

---

## 8. Charging + SoC optimization (ESP32-managed + HW fallback)

Chain: BQ25628E (charge control) + MAX17048 (SoC truth), both I2C0.

Primary control = **ESP32 over I2C** (BQ25628E EN_CHG) — the 80/50 mechanism, no fixed hardware threshold:
```c
soc = max17048_read_soc();            // %
if (soc >= 80) bq25628_charge_dis();  // clear EN_CHG
if (soc <= 50) bq25628_charge_en();   // set EN_CHG
```
- Hysteresis 50↔80 stops chatter.
- Default charge-on at power-up (before firmware) → dead-battery recovery; firmware then applies 80/50.
- **HW fallback (locked): CHG_CE → GPIO14**, 100k strap to charge-on level. Firmware can hard-cut even if I2C hangs; still ESP32-commanded (not a fixed threshold).
- **Ichg conservative** (fast charge not needed): set ~0.3–0.5C via reg → e.g. 500 mA for a 1.5 Ah cell. Gentler on a thin large-area pack; less heat. BQ25628E caps at 2 A regardless.
- Optional longevity: VREG 4.10–4.15 V (vs 4.20).
- Gauge /ALRT → GPIO48: low-SoC → wake + graceful shutdown.
- Enable BQ25628E thermal reg / JEITA; add NTC if pack has one.

---

## 9. USB-C

- Sink only: CC1,CC2 each 5.1 kΩ → GND (Rd). No source/DRP.
- VBUS → BQ25628E VBUS (+ input cap, + TVS via U6).
- D+/D- → S3 GPIO19/20 native + through U6 ESD. 90 Ω diff, length-match, short.
- SBU1/2 = NC. Shield → chassis via R+C (or direct per EMC).
- Full-speed (12 Mbps) fine for book sync/MSC + JTAG/programming.

---

## 10. Compliance (FCC / CE)

**Intentional radiator** handled by module. ESP32-S3-WROOM-1 = **FCC ID 2AC7Z-ESPS3WROOM1** + IC + CE/RED (modular). Inherit by:
- Module at board edge, antenna over edge, honor keep-out (no copper any layer, no traces, no fill, no parts).

**Magnets (phone-attach) — #1 RF risk:**
- Magnets live in the **3D-printed shell** (avoid NdFeB near reflow). PCB carries **silk alignment markers only** (see §11) so you register the shell's magnet pockets to the board — magnets are NOT on the PCB.
- Keep magnet zone ≥10–15 mm from antenna keep-out; opposite end from module.
- ⚠ Bigger issue = the **phone's own MagSafe ring + metal chassis** (always behind device). Orient antenna edge to overhang / clear the phone magnet array + metal. Antenna over free space, not over phone metal.

**Unintentional radiator / product testing still required:**
- FCC Part 15B (verification) — USB, switchers, digital.
- CE: EN 55032 + EN 55035; RED via module + product EMC; LVD N/A (<50 V). RoHS + REACH.
- Switchers (charger buck + FL boost) = main 15B risk: minimal switch-node loops, ceramics close, solid GND, spread-spectrum if available, optional shield can over FL boost.
- USB: ESD array (U6) + DNP common-mode choke footprint on D+/D-.
- Solid uninterrupted GND on layer 2; stitch vias around edge + keep-out.
- Use WROOM-1 (PCB antenna), not WROOM-1U, unless you certify an external antenna.

---

## 11. Layout rules (priority order)

1. Module antenna at edge, keep-out clear; magnet zone far (+ mind phone magnet ring, §10).
2. Continuous GND plane under everything except antenna keep-out.
3. FL boost: L + Schottky + Cout in <5 mm loop, far from antenna + FPC.
4. Charger buck loop tight; input cap at VBUS pin.
5. EPD booster caps hugging FPC pins; short stubs. J2 + J3 adjacent on bottom edge.
6. USB D+/D- 90 Ω diff, ESD at connector then module.
7. Decouple module 3V3: 22 µF + 4×0.1 µF at power pins; bulk at buck.
8. EN: 100 kΩ pull-up + 1 µF + RESET(SW6). BOOT(SW5)→GPIO0→GND.
9. Boot-default pulls: EPD_CS/SD_CS 100k↑, FL_HWEN 100k↓, CHG_CE 100k strap = charge-on.
10. I2C0 + I2C1: 4.7 kΩ pull-ups each to 3V3.
11. **Magnet alignment silk markers**: on the face nearest the shell magnets, print crosshair/circle fiducials at each magnet pocket center so the printed shell registers to the PCB. Copper-free zones there (mechanical only). Mirror position on far end from antenna.
12. Test points: 3V3, VBAT, SYS, I2C0, I2C1, BOOT, EN.

---

## 12. Stack / process

- 4-layer (SIG / GND / PWR / SIG). Controlled-Z for USB pair. ENIG finish (FPC + fine pitch).

---

## 13. Status

- Frontlight: **RESOLVED** — 2 independent strings (5 cool + 5 warm), 4-wire, LM3630A dual-bank (§7).
- Battery: ~1000–2000 mAh thin cell; only sets Ichg reg + case (non-schematic-blocking). Watch mechanical: recess the thin cell, no flex over components.
- Nothing outstanding blocks schematic capture.
