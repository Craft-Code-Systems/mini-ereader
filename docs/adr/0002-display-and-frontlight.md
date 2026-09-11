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

The matching display is confirmed by the owner's second datasheet as the
**Good Display GDEY0426T82-FL01C** — 4.26" 800×480 mono E-Paper, controller
**SSD1677**, 4-wire SPI, 24-pin 0.5 mm FPC, with the frontlight laminated
on (integrated module). Storage: on-module flash, removable microSD, or
both.

## Decision

Target the **Good Display GDEY0426T82-FL01C** (4.26" 800×480, SSD1677,
4-wire SPI) with its integrated dual-channel frontlight, driven by a dual
constant-current boost driver ([Decision 0005](./0005-frontlight-driver.md)).
The SSD1677 needs an external DC-DC (inductor + N-FET + Schottkys + sense
resistor) per the datasheet reference circuit. Include a **microSD (SPI)**
socket as an *optional*, depopulatable part; on-module flash is the default
store.

## Considerations

**Pro:** 4.26"/800×480 is a genuinely readable page size while staying
"mini"; SPI panels are well-supported; the frontlight makes it usable in
the dark with adjustable warmth — a premium feature at low cost.

**Con:** The panel is larger (bigger board, more current) and the SSD1677
needs its own external DC-DC (inductor + N-FET + Schottkys + sense R) for
the ±20 V gate / ±15 V source rails; the frontlight needs a separate ~15 V
boost driver (see 0005). Two switching subsystems to keep quiet near the
antenna and ADC.

Rejected: **2.13" SPI EPD** (original assumption — too small, and does not
match the supplied frontlight); **no frontlight** (unusable in the dark,
and the owner supplied a frontlight); **SD-only storage** (unnecessary
when on-module flash already holds a large text library).

## Consequences

- Board outline grows to fit the 105.33 × 62.37 mm display module
  (`ereader.kicad_pcb` outline ~66 × 115 mm; match
  to the final enclosure).
- A frontlight subsystem is required (connector J5 + dual boost driver);
  see [Decision 0005](./0005-frontlight-driver.md).
- An SSD1677 external DC-DC is required (J4 pins GDR/RESE + L2/Q2/D4-D6 +
  ≥25 V caps), fed from +3V3, per the datasheet reference circuit
  (`ereader-pcb-design.md` §6).
- **Resolved:** the full 24-pin EPD FPC pinout and controller are locked
  from the GDEY0426T82-FL01C datasheet (`ereader-pcb-design.md` §6).
- EPD and microSD share one SPI bus; EPD is write-only (no MISO), SD needs
  MISO + pull-ups.
- Firmware brings up the panel with a controller driver matched to the
  panel's waveform/LUT.

## Reconciliation note (Rev C — non-normative erratum, 2026-09-11)

The decision above stands, but its **designators predate the Rev C board** and
must not be read literally — the canonical designators live in
`ereader-connection-list.md` / `ereader-kicad.net`:

- EPD panel FPC = **J2** (this ADR's prose says "J4"); frontlight FPC = **J3**
  (prose says "J5"); the 1S Li-Po = **J5**; microSD = **J4**.
- The SSD1677 external DC-DC parts are now captured as **LE / QE / DE1–DE3 /
  RE1 / RE2 / CE1–CE9** (this ADR's "L2/Q2/D4-D6" was placeholder naming; note
  `L2` in Rev C is the *frontlight* boost inductor, not the EPD one).

No decision is changed here — only the part references are mapped to the built
design so the ADR can't be misread during the remaining EPD-booster work.
