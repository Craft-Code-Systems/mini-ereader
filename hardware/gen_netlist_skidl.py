#!/usr/bin/env python3
"""
Mini E-Reader — netlist generator (SKiDL).

Encodes the net graph from DESIGN.md so a KiCad netlist can be produced
programmatically, then imported into pcbnew to place footprints. Treat this
as a *starting point*, not a verified schematic: SKiDL resolves parts from
your installed KiCad symbol libraries, and a few lib_ids / pin names below
are marked TODO because they depend on the exact part/panel you fit.

Prereqs (on a machine with KiCad installed):
    pip install skidl
    # KiCad's symbol libs must be discoverable (KICAD8_SYMBOL_DIR etc.)

Run:
    python gen_netlist_skidl.py          # writes mini-ereader.net
    # In KiCad PCB editor: File > Import > Netlist... -> mini-ereader.net

Then draw the actual schematic in Eeschema for review (ERC), using this
netlist and DESIGN.md as the reference. This script does not draw a
schematic; it only expresses connectivity.
"""

import sys

try:
    from skidl import Part, Net, generate_netlist, ERC, TEMPLATE
except Exception as exc:  # pragma: no cover - env without skidl
    sys.stderr.write(
        "SKiDL not available (%s).\n"
        "Install with `pip install skidl` on a machine that has KiCad's\n"
        "symbol libraries, then re-run. See the module docstring.\n" % exc
    )
    sys.exit(1)


def R(value):
    """0603 resistor template helper."""
    return Part("Device", "R", value=value, footprint="Resistor_SMD:R_0603_1608Metric")


def C(value):
    """0603 capacitor template helper."""
    return Part("Device", "C", value=value, footprint="Capacitor_SMD:C_0603_1608Metric")


def build():
    # ---- Power / global nets -------------------------------------------
    gnd = Net("GND")
    vbus = Net("VBUS")
    vbat = Net("VBAT")
    vsys = Net("VSYS")
    v3v3 = Net("+3V3")

    # ---- Signal nets ---------------------------------------------------
    spi_sck = Net("SPI_SCK")
    spi_mosi = Net("SPI_MOSI")
    spi_miso = Net("SPI_MISO")
    epd_cs = Net("EPD_CS")
    epd_dc = Net("EPD_DC")
    epd_rst = Net("EPD_RST")
    epd_busy = Net("EPD_BUSY")
    sd_cs = Net("SD_CS")
    sd_cd = Net("SD_CD")
    btn_prev = Net("BTN_PREV")
    btn_next = Net("BTN_NEXT")
    btn_sel = Net("BTN_SEL")
    boot = Net("BOOT")
    en = Net("EN")
    usb_dp = Net("USB_DP")
    usb_dm = Net("USB_DM")
    bat_sense = Net("BAT_SENSE")
    chg_stat = Net("CHG_STAT")
    fl_cold_pwm = Net("FL_COLD_PWM")
    fl_warm_pwm = Net("FL_WARM_PWM")

    # ---- MCU: ESP32-S3-WROOM-1 ----------------------------------------
    # lib_id RF_Module:ESP32-S3-WROOM-1 ships with KiCad 8. Pin *names*
    # below match that symbol; adjust if your library revision differs.
    u1 = Part("RF_Module", "ESP32-S3-WROOM-1", footprint="RF_Module:ESP32-S2-WROOM")
    u1["3V3"] += v3v3
    u1["GND"] += gnd
    u1["EN"] += en
    u1["IO0"] += boot
    u1["IO19"] += usb_dm
    u1["IO20"] += usb_dp
    u1["IO12"] += spi_sck
    u1["IO11"] += spi_mosi
    u1["IO14"] += spi_miso
    u1["IO10"] += epd_cs
    u1["IO9"] += epd_dc
    u1["IO8"] += epd_rst
    u1["IO7"] += epd_busy
    u1["IO13"] += sd_cs
    u1["IO21"] += sd_cd
    u1["IO4"] += btn_prev
    u1["IO5"] += btn_next
    u1["IO6"] += btn_sel
    u1["IO1"] += bat_sense
    u1["IO2"] += chg_stat
    u1["IO15"] += fl_cold_pwm
    u1["IO16"] += fl_warm_pwm

    # Module decoupling
    C("22uF")[1, 2] += v3v3, gnd
    C("10uF")[1, 2] += v3v3, gnd
    for _ in range(4):
        C("100nF")[1, 2] += v3v3, gnd

    # EN / BOOT
    R("10k")[1, 2] += v3v3, en
    C("100nF")[1, 2] += en, gnd
    R("10k")[1, 2] += v3v3, boot

    # ---- USB-C receptacle ---------------------------------------------
    # TODO: set lib_id/footprint to your exact connector; pin names vary.
    j1 = Part("Connector", "USB_C_Receptacle_USB2.0_16P",
              footprint="Connector_USB:USB_C_Receptacle_XKB_U262-16XN-4BVC11")
    j1["VBUS"] += vbus
    j1["GND"] += gnd
    j1["CC1"] += Net("CC1")
    j1["CC2"] += Net("CC2")
    j1["DP1", "DP2"] += usb_dp
    j1["DM1", "DM2"] += usb_dm
    R("5.1k")[1, 2] += j1["CC1"], gnd
    R("5.1k")[1, 2] += j1["CC2"], gnd
    C("4.7uF")[1, 2] += vbus, gnd
    C("100nF")[1, 2] += vbus, gnd

    # ---- Charger: MCP73831 (SOT-23-5) ---------------------------------
    u2 = Part("Battery_Management", "MCP73831-2-OT",
              footprint="Package_TO_SOT_SMD:SOT-23-5")
    u2["VDD"] += vbus
    u2["VSS"] += gnd
    u2["VBAT"] += vbat
    u2["STAT"] += chg_stat
    u2["PROG"] += Net("PROG")
    R("2.0k")[1, 2] += u2["PROG"], gnd            # 500 mA
    C("4.7uF")[1, 2] += vbat, gnd
    # Charge status LED to VBUS
    d2 = Part("Device", "LED", footprint="LED_SMD:LED_0603_1608Metric")
    r6 = R("1k")
    vbus += r6[1]
    r6[2] += d2["A"]
    d2["K"] += chg_stat

    # ---- Load-share: DMG2305UX P-FET + Schottky -----------------------
    q1 = Part("Transistor_FET", "DMG2305UX",
              footprint="Package_TO_SOT_SMD:SOT-23")
    q1["S"] += vbat
    q1["D"] += vsys
    q1["G"] += Net("Q1_G")
    R("100k")[1, 2] += q1["G"], vbus              # off when USB present
    R("100k")[1, 2] += q1["G"], gnd               # on when USB absent
    d1 = Part("Device", "D_Schottky", footprint="Diode_SMD:D_SMA")
    d1["A"] += vbus
    d1["K"] += vsys

    # ---- LDO: AP2112K-3.3 (SOT-23-5) ----------------------------------
    u3 = Part("Regulator_Linear", "AP2112K-3.3",
              footprint="Package_TO_SOT_SMD:SOT-23-5")
    u3["VIN"] += vsys
    u3["EN"] += vsys
    u3["GND"] += gnd
    u3["VOUT"] += v3v3
    C("1uF")[1, 2] += vsys, gnd
    C("1uF")[1, 2] += v3v3, gnd

    # ---- Battery sense divider ----------------------------------------
    r5a = R("100k")
    r5b = R("100k")
    vbat += r5a[1]
    r5a[2] += bat_sense
    r5b[1] += bat_sense
    r5b[2] += gnd
    C("100nF")[1, 2] += bat_sense, gnd

    # ---- E-Paper 4.26" 800x480 (panel datasheet REQUIRED) -------------
    # The EPD FPC pin count/pinout/controller depend on the specific 4.26"
    # panel (GDEQ0426T82 class). The MCU-side nets (EPD_*) exist above; map
    # the connector ONLY from the panel datasheet, then uncomment and wire:
    #   j4 = Part("Connector", "Conn_01xNN", footprint="Connector_FFC-FPC:...")
    #   j4[<SCLK>] += spi_sck ;  j4[<SDA>]  += spi_mosi
    #   j4[<CS#>]  += epd_cs  ;  j4[<D/C#>] += epd_dc
    #   j4[<RST#>] += epd_rst ;  j4[<BUSY>] += epd_busy
    #   j4[<VDD/VDDIO/VCI>] += v3v3 ;  j4[<VSS>] += gnd
    #   # + controller charge-pump / VCOM caps per the datasheet
    # (Left unwired here on purpose; ERC will flag EPD_* as single-pin nets.)

    # ---- Frontlight: Good Display FL0426-S01C -------------------------
    # 6-pin FPC: 1 LEDC+  2 LEDC-  3 NC  4 NC  5 LEDW+  6 LEDW-
    j5 = Part("Connector", "Conn_01x06",
              footprint="Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal")

    def fl_driver(pwm_net, out_net, fb_net, tag):
        # TODO: TPS61165 may not be in your KiCad symbol libs; set lib_id and
        #       verify pin names (VIN, GND, SW, FB, CTRL).
        u = Part("Regulator_Switching", "TPS61165",
                 footprint="Package_TO_SOT_SMD:SOT-23-6")
        sw = Net("FL_SW_%s" % tag)
        u["VIN"] += vsys
        u["GND"] += gnd
        u["CTRL"] += pwm_net
        u["SW"] += sw
        u["FB"] += fb_net           # LED string cathode returns into FB
        # Boost: L (VSYS->SW), Schottky (SW->OUT), Cout (OUT->GND), Cin, R_SET
        L = Part("Device", "L", value="10uH",
                 footprint="Inductor_SMD:L_1210_3225Metric")
        L[1, 2] += vsys, sw
        D = Part("Device", "D_Schottky", value=">=20V",
                 footprint="Diode_SMD:D_SOD-123")
        D["A"] += sw
        D["K"] += out_net
        C("1uF")[1, 2] += out_net, gnd      # Cout (>=25V, see BOM)
        C("1uF")[1, 2] += vsys, gnd         # Cin
        R("13R")[1, 2] += fb_net, gnd       # R_SET: ILED = 0.2V / R_SET

    fl_c_out, fl_c_fb = Net("FL_C_OUT"), Net("FL_C_FB")
    fl_w_out, fl_w_fb = Net("FL_W_OUT"), Net("FL_W_FB")
    fl_driver(fl_cold_pwm, fl_c_out, fl_c_fb, "C")
    fl_driver(fl_warm_pwm, fl_w_out, fl_w_fb, "W")
    j5[1] += fl_c_out    # LEDC+
    j5[2] += fl_c_fb     # LEDC-
    j5[5] += fl_w_out    # LEDW+
    j5[6] += fl_w_fb     # LEDW-
    # j5[3], j5[4] = NC

    # ---- microSD (SPI) ------------------------------------------------
    j3 = Part("Connector", "microSD_Card_Det",
              footprint="Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5")
    j3["VDD"] += v3v3
    j3["VSS"] += gnd
    j3["CLK"] += spi_sck
    j3["DI"] += spi_mosi
    j3["DO"] += spi_miso
    j3["CS"] += sd_cs
    j3["DAT1"] += Net("SD_DAT1")   # unused in SPI mode
    j3["DAT2"] += Net("SD_DAT2")
    j3["CD"] += sd_cd
    R("10k")[1, 2] += v3v3, sd_cs
    R("10k")[1, 2] += v3v3, spi_miso
    C("10uF")[1, 2] += v3v3, gnd

    # ---- Buttons ------------------------------------------------------
    j2 = Part("Connector", "Conn_01x02", footprint="Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical")
    j2[1] += vbat
    j2[2] += gnd

    def button(net):
        sw = Part("Switch", "SW_Push", footprint="Button_Switch_SMD:SW_SPST_TL3342")
        sw[1] += net
        sw[2] += gnd
        R("10k")[1, 2] += v3v3, net
        C("100nF")[1, 2] += net, gnd

    button(btn_prev)
    button(btn_next)
    button(btn_sel)

    # BOOT / RESET buttons (no pull-up cap on boot beyond the 10k above)
    sw_boot = Part("Switch", "SW_Push", footprint="Button_Switch_SMD:SW_SPST_TL3342")
    sw_boot[1] += boot
    sw_boot[2] += gnd
    sw_rst = Part("Switch", "SW_Push", footprint="Button_Switch_SMD:SW_SPST_TL3342")
    sw_rst[1] += en
    sw_rst[2] += gnd


if __name__ == "__main__":
    build()
    ERC()
    generate_netlist(file_="mini-ereader.net")
    print("Wrote mini-ereader.net — import into pcbnew, then draw/verify in Eeschema.")
