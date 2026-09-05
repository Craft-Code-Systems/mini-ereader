# Decision 0002: SPI E-Paper (SSD1680) display, microSD optional

**Status:**      Accepted
**Date:**        2026-09-05

## Context

An e-reader needs a persistent, low-power, sunlight-readable display —
which means E-Paper. For a *mini* reader the panel should be small, cheap,
and driveable over SPI from the MCU without exotic supplies. It also needs
somewhere to keep books: on-module flash, removable microSD, or both.

Small E-Paper panels commonly use the **SSD1680** controller with a 24-pin
0.5 mm FPC and an on-chip charge pump, so no separate high-voltage boost IC
or inductor is required — just decoupling capacitors. The main hazard is
that **FPC pinouts differ between otherwise-similar panels.**

## Decision

Target a **2.13", 250×122 monochrome SSD1680 panel** (reference part
GDEY0213B74) on a 24-pin 0.5 mm FPC over 4-wire SPI (SCK/MOSI + CS/DC/RST/
BUSY). Include a **microSD (SPI)** socket as an *optional*, depopulatable
part; on-module flash is the default store.

## Considerations

**Pro:** SPI SSD1680 panels are cheap, well-supported (GxEPD2), and need
only capacitors around the controller. microSD gives effectively unlimited
book storage for those who want it, on the same SPI bus.

**Con:** The exact 24-pin FPC pinout is panel-specific and must be verified
against the chosen panel's datasheet before ordering — a wrong pinout
bricks the display bring-up. microSD adds board area and four+ nets.

Rejected: **parallel/8080 E-Paper** (more pins, bigger panels than needed);
**I²C OLED** (not sunlight-readable, not persistent); **SD-only storage**
(unnecessary when 8–16 MB on-module flash already holds a large text
library).

## Consequences

- `DESIGN.md` §5 lists a reference 24-pin pinout **flagged for datasheet
  verification**; changing panel size (2.9"/4.2") revisits this Decision.
- EPD and microSD share one SPI bus; EPD is write-only (no MISO), SD needs
  MISO + pull-ups.
- microSD is the first candidate for depopulation if board area is tight.
- Firmware brings up the panel with an SSD1680 driver profile matched to
  the panel's waveform/LUT.
