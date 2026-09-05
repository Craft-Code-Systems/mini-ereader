# Decision 0005: Dual constant-current boost driver for the frontlight

**Status:**      Accepted
**Date:**        2026-09-05

## Context

The chosen frontlight (Good Display FL0426-S01C,
[Decision 0002](./0002-display-and-frontlight.md)) has two independent LED
channels, each **5 white LEDs in series**: **VF ≤ 15 V, IF ≤ 15 mA**. To
control both brightness and colour temperature, each channel must be driven
at a regulated constant current, dimmable independently, from a battery/USB
rail of only 3.0–5.0 V — well below the ~15 V the string needs. So the
driver must **boost** and **regulate current**, per channel.

Options: (a) two single-channel WLED boost drivers; (b) one boost to ~16 V
plus two low-side constant-current sinks; (c) an integrated dual/multi-
channel LED driver.

## Decision

Use **two TPS61165 WLED boost drivers** (one per channel), input from VSYS,
output a regulated LED current set by a sense resistor, dimmed by **PWM on
each driver's control pin from two MCU LEDC pins** (FL_COLD_PWM = GPIO15,
FL_WARM_PWM = GPIO16). Set LED current with R_SET = 0.2 V / I_LED
(≈ 13 Ω for 15 mA; start lower, e.g. 10 mA, and tune).

## Considerations

**Pro:** Each channel is fully independent (true colour-temperature mixing
by ratioing the two PWM duties); TPS61165 integrates the switch and current
regulation, needing only L + Schottky + Cout + Cin + R_SET; PWM dimming maps
directly onto the ESP32-S3 LEDC peripheral; components are cheap.

**Con:** Two boost inductors (board area) and two switching nodes (EMI) that
must be kept away from the RF module and the battery-sense ADC; boost
efficiency and inrush to manage; the small SOT-23/WSON driver is fiddly to
hand-solder.

Rejected:
- **One boost + two linear current sinks** — saves an inductor but burns the
  headroom difference as heat in the sinks and still needs two control loops;
  revisit if area beats efficiency.
- **Integrated dual-channel LED driver** — cleanest in principle, but common
  parts target higher-current backlights or RGB; kept as a future
  consolidation if a suitable ≤15 mA, ~16 V dual driver is sourced.
- **Direct/parallel drive from 3.3 V** — impossible; the series string needs
  ~15 V.

## Consequences

- Add connector **J5** (6-pin 0.5 mm FPC) wired to the FL0426-S01C pinout;
  route LEDC+/− and LEDW+/− to their respective drivers, NC pins left open.
- Reserve two ESP32-S3 LEDC pins (GPIO15, GPIO16) for PWM dimming.
- Frontlight draws from **VSYS** (not +3V3); budget ~0.15 A input at full
  brightness (both channels).
- Layout: keep both boost stages and their inductors in one corner, away
  from the antenna and BAT_SENSE; local ground pour and short switch loops.
- **Confirm the LED electrical spec** (VF, IF, series count) against the
  full FL0426-S01C datasheet before finalising R_SET and the boost Cout
  voltage rating (≥ 20 V).
