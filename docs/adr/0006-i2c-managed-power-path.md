# Decision 0006: I2C-managed power path — BQ25628E charger, TPS62840 buck, MAX17048 gauge

**Status:**      Accepted
**Date:**        2026-09-06
**Supersedes:**  [Decision 0003](./0003-power-architecture.md)

## Context

[Decision 0003](./0003-power-architecture.md) chose the minimal discrete
power path — MCP73831 linear charger (PROG-set 500 mA), a discrete P-FET +
Schottky load-share, an AP2112K-3.3 LDO, and a resistor divider to an ADC
for battery sense — to get an openable board quickly. The actual board
(`ereader.*`, Rev C) that is now the canonical KiCad project took a
different route across the whole power/telemetry chain, and it is the real,
placed design. The ADRs must reconcile to it.

Three forces drove the change. The LDO wastes the 3.0–3.4 V battery tail and
the divider gives only coarse state-of-charge; the design instead wants to
use the full cell and read accurate SoC. Charge behaviour should be
firmware-managed (charge-cap hysteresis for cell longevity), not fixed by a
PROG resistor. And the deep-sleep µA budget (README non-functional baseline)
favours a nanoamp-Iq buck over an LDO's quiescent draw plus an always-on
sense divider.

## Decision

Charge with **TI BQ25628E** (1S I2C buck charger, up to 2 A; addr 0x6B on
I2C0), firmware-managed via `EN_CHG` (stop at 80 % SoC, resume at 50 %), with
a hardware **`CE` pin on GPIO14** (100 kΩ strap = charge-on default) as the
fail-safe and dead-battery power-up path. Regulate SYS→3.3 V with **TI
TPS62840** buck (750 mA, 60 nA Iq). Read state-of-charge with **Maxim
MAX17048** ModelGauge (addr 0x36, no sense resistor; `/ALRT`→GPIO48). Run
two I2C buses to break the MAX17048-vs-LM3630A 0x36 address clash: **I2C0** =
charger + gauge, **I2C1** = the frontlight driver (see
[Decision 0007](./0007-lm3630a-frontlight-driver.md)).

## Considerations

**Pro:** The buck uses the whole 3.0–4.2 V cell instead of stranding the
tail; ModelGauge gives accurate SoC with no sense resistor; firmware-set
charge caps extend pack life; ~60 nA Iq slashes deep-sleep drain; BQ25628E
integrates a power path (run-while-charging), JEITA/thermal regulation, and
headroom to 2 A for a larger cell.

**Con:** Two more I2C devices plus a second bus (firmware, four pull-ups,
extra pins); a switching charger and buck add EMI to manage near the RF
module and the gauge; the parts cost more and are finer-pitch than the
discrete path; the shared 0x36 address forces the second bus.

Rejected:
- **Keep the 0003 path** (MCP73831 / AP2112 / divider) — simpler and
  cheaper, but strands the battery tail, gives coarse SoC, and cannot do
  SoC-managed charge caps.
- **Single I2C bus** with a BQ27441-G1A gauge (@0x55) — avoids the second
  bus but needs a sense resistor; kept only as a forced fallback.

## Consequences

- **I2C0** (SDA GPIO17 / SCL GPIO18): BQ25628E 0x6B + MAX17048 0x36.
  **I2C1** (SDA GPIO16 / SCL GPIO38): LM3630A. 4.7 kΩ pull-ups per bus.
- GPIO14 = `CHG_CE` (100 kΩ strap, charge-on default); GPIO47 = `CHG_INT`;
  GPIO48 = `GAUGE_ALRT` (low-SoC wake → graceful shutdown).
- Firmware implements the 50↔80 % charge state machine (hysteresis stops
  chatter); default is charge-on before firmware runs, for dead-battery
  recovery. Ichg set conservative (~0.3–0.5C) by register; optional VREG
  4.10–4.15 V for longevity.
- The 3.3 V rail must survive the S3 TX burst (~0.5 A): TPS62840 (750 mA) +
  22 µF bulk at the module 3V3 pins.
- Layout: keep the charger buck loop tight with the input cap at VBUS, and
  hold both switch nodes away from the antenna and BAT_SENSE. Detail in
  `ereader-pcb-design.md` §4 (power tree) and §8 (charging + SoC).
- The frontlight boost draws from VBAT/SYS, not +3V3 (unchanged from 0003).
- MCU note: Rev C uses the **-N16R8** variant of the module chosen in
  [Decision 0001](./0001-mcu-esp32-s3.md) (16 MB flash / 8 MB PSRAM, for
  OTA A/B + the 800×480 framebuffer + fonts). That is a variant selection
  under 0001, not a new decision.
