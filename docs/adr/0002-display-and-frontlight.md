# Decision 0002: 4.26" 800×480 E-Paper with a laminated tunable frontlight

**Status:**      Accepted
**Date:**        2026-09-05
**Supersedes:**  (supersedes the earlier 2.13" assumption made before the
panel was known)

## Context

An e-reader needs a persistent, sunlight-readable display — E-Paper — and,
to be usable in the dark, a **frontlight** (light laminated *in front of*
the reflective panel, never a backlight). The physical size is set by the
frontlight datasheet the owner supplied: **Good Display FL0426-S01C**, a
frontlight built for a **4.26", 480×800-dot EPD**, LGP 61.40 × 104.10 mm.

The frontlight provides two independently driven LED channels for
colour-temperature control:

- **Cold:** 5 white LEDs in **series**, VF ≤ 15 V, IF ≤ 15 mA
- **Warm:** 5 white LEDs in **series**, VF ≤ 15 V, IF ≤ 15 mA
- 6-pin 0.5 mm FPC: 1 = LEDC+, 2 = LEDC−, 3 = NC, 4 = NC, 5 = LEDW+,
  6 = LEDW−

The matching display is a 4.26" 800×480 mono E-Paper (Good Display
GDEQ0426T82 class) on a 4-wire SPI, SSD-family controller. Storage: on-
module flash, removable microSD, or both.

## Decision

Target the **4.26" 800×480 mono E-Paper** over 4-wire SPI, with the **Good
Display FL0426-S01C frontlight** laminated in front, driven by a dual
constant-current boost driver ([Decision 0005](./0005-frontlight-driver.md)).
Include a **microSD (SPI)** socket as an *optional*, depopulatable part;
on-module flash is the default store.

## Considerations

**Pro:** 4.26"/800×480 is a genuinely readable page size while staying
"mini"; SPI panels are well-supported; the frontlight makes it usable in
the dark with adjustable warmth — a premium feature at low cost.

**Con:** The panel is larger (bigger board, more current, higher-voltage
frontlight rail than a bare EPD would need); the **EPD FPC pinout and exact
controller must be confirmed from the panel datasheet**, which the owner
has not yet supplied (only the frontlight datasheet is in hand); the
frontlight needs a ~15 V boost driver (see 0005).

Rejected: **2.13" SPI EPD** (original assumption — too small, and does not
match the supplied frontlight); **no frontlight** (unusable in the dark,
and the owner supplied a frontlight); **SD-only storage** (unnecessary
when on-module flash already holds a large text library).

## Consequences

- Board outline grows to accommodate a ~61 × 104 mm display area
  (`hardware/mini-ereader.kicad_pcb` outline is a placeholder to match the
  final enclosure).
- A frontlight subsystem is required (connector J5 + dual boost driver);
  see [Decision 0005](./0005-frontlight-driver.md).
- **Open input:** the EPD panel's own datasheet is needed to lock the
  display FPC connector pinout and controller (`hardware/DESIGN.md` §5
  marks this TBD). The SPI/logic signals are panel-agnostic; pin *numbers*
  are not.
- EPD and microSD share one SPI bus; EPD is write-only (no MISO), SD needs
  MISO + pull-ups.
- Firmware brings up the panel with a controller driver matched to the
  panel's waveform/LUT.
