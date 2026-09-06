# Decision 0008: Navigation input — 3 side buttons + a lever switch

**Status:**      Accepted
**Date:**        2026-09-06

## Context

The reader needs navigation input — page forward/back, menu, scroll, select —
and it must work from deep sleep: the device sleeps with the page retained in
the µA range (README non-functional baseline), so every input has to be able
to wake the ESP32-S3. No prior ADR covered input; the earlier reference spec
(the since-removed `hardware/` lineage) assumed three buttons, while the
canonical board (`ereader.*`, Rev C) settled on a richer scheme. This
decision documents that
scheme.

The tension is affordance vs. cost/pins. Plain buttons are cheap, obvious,
and trivially wake-capable, but paging through a long library or menu with
two or three buttons is clunky. A scroll-and-select control fixes that, but a
true quadrature rotary encoder adds A/B decode, rotational travel/mechanics,
and more firmware. A middle option — a multi-directional lever switch — gives
CW/CCW/press as three ordinary momentary contacts, no quadrature decode.

## Decision

Use **three side tactile buttons** (SW1–SW3: page/menu) plus **one ALPS
SLLB510200 multi-directional lever switch** (SW4: CW / CCW / press). All are
active-low momentary contacts to GND with pull-ups, each on an **RTC-capable
GPIO** so any can wake the S3 from deep sleep. Firmware debounces and decodes
them (no hardware quadrature). BOOT (JP5→GPIO0) and RESET (JP6→EN) remain for
native-USB programming/recovery (see
[Decision 0004](./0004-native-usb-programming.md)) — as of Rev C3 they're bare
exposed jumper pads rather than tactiles, momentarily shorted with a
screwdriver tip or tweezers, since that recovery path is used rarely enough
that a dedicated switch part isn't worth the BOM cost or the accidental-press
risk of a labelled button sitting on the case.

## Considerations

**Pro:** The lever gives one-handed scroll (CW/CCW) + select (press) in a
single part while the three side buttons cover page-forward/back/menu; every
input is a simple momentary contact (debounce in firmware, no encoder decode);
all sit on RTC GPIOs, so any is a deep-sleep wake source — matching the µA
sleep budget; low BOM cost and only six GPIOs for the whole navigation set.

**Con:** The SLLB510200 is a specific ALPS part (sourcing + footprint risk;
small 9.5 × 8.8 × 2.2 mm SMD; contacts rated 10 mA / 5 V — signal-level only);
six inputs consume six GPIOs; waking on several pins needs `ext1`-mask setup;
a lever is less self-evident than labelled buttons.

Rejected:
- **Three buttons only** (the reference spec) — simplest, but no scroll/select
  affordance; long menus and the library list are tedious.
- **A true quadrature rotary encoder** — finer scroll resolution, but needs
  A/B decode, more mechanics/travel, and more firmware; the lever covers
  CW/CCW/press with three plain contacts for less.
- **Capacitive touch / touchscreen** — out of scope (README non-scope) and
  adds cost and standby power.

## Consequences

- Add **SW1–SW3** (side tactiles) and **SW4** (ALPS SLLB510200). Pin map:
  `BTN_A`=GPIO4, `BTN_B`=GPIO5, `BTN_C`=GPIO6; `LEV_CW`=GPIO1,
  `LEV_CCW`=GPIO2, `LEV_PUSH`=GPIO15 — all pull-up, RTC-wake
  (`ereader-pcb-design.md` §5).
- All six are RTC-capable wake sources: assign `BTN_A` + `LEV_PUSH` as the
  primary wakes and `ext1`-mask the rest.
- `LEV_PUSH` takes GPIO15 — one reason the frontlight moved to I2C control,
  freeing the LEDC pins 0005 had reserved; see
  [Decision 0007](./0007-lm3630a-frontlight-driver.md).
- The 10 mA / 5 V contact rating is signal-level only (GPIO + pull-up) — do
  not switch any power rail through the lever.
- Firmware provides debounce and CW/CCW/press decode; no hardware quadrature
  or encoder peripheral is used.
- Sourcing: verify SLLB510200 stock before order. **SLLB510100** is a
  pin-compatible alternative in the same SLLB5 series (same 9.5×8.8×2.2 mm
  envelope and CW/CCW/PUSH/COM terminals) — swap the value if it sources better.
- **Footprints (Rev C2):** the three nav tactiles use a genuinely
  **side-actuated** land, `ereader:WE_WS-TASU_436351045816` (Würth WS-TASU
  436351045816, 4.7×3.5 mm side push), drawn from the WE datasheet — 4 pads
  1.2×0.7 mm + two Ø0.75 boss holes — with the actuator facing the board edge. The
  earlier `SW_SPST_TL3342` stand-in was **top-actuated**, unusable here because the
  screen covers the whole front and magnets hold the back to the phone. SW4 uses
  `ereader:ALPS_SLLB5_Lever`, drawn from the ALPS SLLB5 datasheet (4 signal pads on
  2 mm pitch in CW/COM/PUSH/CCW order + two Ø1.1 locator holes + solder lugs), so
  `LEV_CW/CCW/PUSH` and `COM→GND` connect on netlist import instead of sitting
  unconnected. Both lands are drawn from the datasheets but still to be DRC'd against
  the ordered part before route/fab; tune SW4's placement/orientation to the
  enclosure edge.
- **BOOT/RESET → bare jumper pads (Rev C3).** SW5/SW6 (the Würth tactiles on
  BOOT/RESET) are replaced by `ereader:JumperPad_2P_P2.0mm` under refs `JP5`/`JP6`:
  two 1.2×1.2 mm exposed pads on 2 mm pitch, no switch part, at the same board
  location the tactiles occupied. Short the pair momentarily with a screwdriver tip
  or tweezers to pull `IO0_BOOT`/`EN` low; open circuit otherwise. Hand-drawn
  geometry (no datasheet to check against, since there's no part to order) — DRC
  the pad spacing against fab minimum clearance and confirm the case cutout still
  reaches them before fab.
