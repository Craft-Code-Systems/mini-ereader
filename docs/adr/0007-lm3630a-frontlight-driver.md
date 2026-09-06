# Decision 0007: LM3630A single-boost dual-sink frontlight driver

**Status:**      Accepted
**Date:**        2026-09-06
**Supersedes:**  [Decision 0005](./0005-frontlight-driver.md)

## Context

[Decision 0005](./0005-frontlight-driver.md) chose two TPS61165 WLED boost
drivers (one per channel), PWM-dimmed from two ESP32-S3 LEDC pins. It was
sound but assumed each channel needed its own boost. The canonical board
(`ereader.*`, Rev C) took a different route, and the ADRs must reconcile to
it.

The frontlight topology is now confirmed from the FL0426-S01C drawing
([Decision 0002](./0002-display-and-frontlight.md), Rev C §7): two
**independent 4-wire** series strings — cool and warm, **5 LEDs each**,
VF ≤ 15 V, IF ≤ 15 mA, equal length, sharing nothing (not common-anode).
Equal-length strings mean a *single* boost can feed both anodes while two
current sinks regulate each string independently — exactly what an
integrated dual-string LED driver provides, which 0005 had rejected only
because no suitable ≤15 mA / ~16 V dual part was sourced at the time.

## Decision

Drive the frontlight with **TI LM3630A** (I2C dual-string backlight boost,
addr 0x36 on **I2C1**): one boost `OUT` feeds both string anodes (FL pin 1
C+, pin 5 W+), and the two integrated current sinks — Bank A = cool at FL
pin 2 C−, Bank B = warm at pin 6 W− — regulate each string. Per-bank Iset
≤ 15 mA and per-bank brightness are set over I2C1; **`FL_HWEN` on GPIO21**
(100 kΩ pull-down = off at boot) is the hard standby cut. OVP ≥ 18 V.

## Considerations

**Pro:** One inductor and one switch node instead of two — less board area
and one fewer EMI aggressor near the antenna and FPCs; the integrated dual
sink gives true per-channel current regulation and independent cool/warm
brightness for colour-temperature blend; I2C control frees the two LEDC pins
0005 reserved; equal string lengths make the shared boost efficient (it
regulates to the active sink).

**Con:** Adds a device to I2C — and because the LM3630A is 0x36 it clashes
with the MAX17048, forcing the second I2C bus (see
[Decision 0006](./0006-i2c-managed-power-path.md)); dimming is firmware over
I2C, not a raw LEDC pin; boost OVP and inrush must be managed; a single boost
is a shared point of failure for both channels (two independent boosts were
not).

Rejected:
- **Two TPS61165 boosts** (0005) — more area and two switch nodes for no
  functional gain now that the strings are confirmed equal-length.
- **One boost + two discrete linear sinks** — the LM3630A integrates exactly
  this in one part.
- **Direct/parallel drive from 3.3 V** — impossible; the series string needs
  ~15 V.

## Consequences

- Connector **J3** (6-pin 0.5 mm FPC): 1 C+ / 2 C− / 3 NC / 4 NC / 5 W+ /
  6 W−; both anodes to boost `OUT`, cathodes to the LED1/LED2 sinks. (This is
  J3 in `ereader-pcb-design.md` §3/§7; it was labelled J5 in 0005.)
- **I2C1** (SDA GPIO16 / SCL GPIO38) carries the LM3630A at 0x36; GPIO21 =
  `FL_HWEN` (100 kΩ pull-down). This frees GPIO15/16 that 0005 reserved for
  PWM — on Rev C, GPIO16 is now I2C1_SDA and GPIO15 is the encoder push.
- Frontlight draws from VBAT/SYS, not +3V3; set OVP ≥ 18 V (5 × 3.6 V) and
  per-bank Iset conservative, then tune.
- Layout: boost L + Cout loop < 5 mm with local ceramics, far from the
  antenna and the FPCs. Detail in `ereader-pcb-design.md` §7 and §11.
- ADR 0005 marked Superseded by this decision.
