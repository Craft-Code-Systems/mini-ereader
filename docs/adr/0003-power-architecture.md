# Decision 0003: USB-C + 1S LiPo, discrete load-share, 3.3 V LDO

**Status:**      Superseded by [Decision 0006](./0006-i2c-managed-power-path.md)
**Date:**        2026-09-05

> Superseded 2026-09-06: the canonical board (`ereader.*`, Rev C) uses an
> I2C-managed power path (BQ25628E charger, TPS62840 buck, MAX17048 gauge).
> See [Decision 0006](./0006-i2c-managed-power-path.md). The Context and
> reasoning below are preserved as the trail.

## Context

The reader must run from a rechargeable battery, charge over USB-C, and
provide a clean 3.3 V rail to an MCU whose Wi-Fi TX peaks near 500 mA. A
single-cell LiPo (3.0–4.2 V) is the obvious chemistry for a pocket device.
Three sub-decisions: charger, source selection (USB vs battery), and
regulation. (The frontlight's ~15 V rail is a separate boost stage — see
[Decision 0005](./0005-frontlight-driver.md).)

The tension is regulation: an LDO is tiny and quiet but cannot boost, so
the 3.3 V rail sags once the cell falls below ~3.4 V, wasting the battery
tail; a buck-boost uses the whole range but adds cost, area, and switching
noise near the RF module and ADC.

## Decision

Charge with **MCP73831** (PROG-set, 500 mA). Select the source with a
**discrete load-share** — a DMG2305UX P-FET (battery→VSYS, off when USB
present) plus a Schottky (USB→VSYS) — so USB powers the system and only
charges the cell when plugged. Regulate VSYS→3.3 V with an **AP2112K-3.3**
LDO (600 mA), generously bulk-decoupled for TX bursts.

## Considerations

**Pro:** Minimal BOM and board area; every part is cheap, common, and
hand-solderable; the load-share avoids charging and discharging the cell
at once; the LDO is silent (no switching noise near the RF module or ADC).

**Con:** LDO dropout wastes the 3.0–3.4 V battery tail; the discrete
load-share has a Schottky drop (~0.3 V) on the USB path and no proper DPPM.

Rejected for v0.1, kept as upgrade paths:
- **MCP73871** power-path charger — seamless switching + DPPM, but larger
  and more complex. Adopt if "run while charging a dead battery" matters.
- **TPS63020 buck-boost** on 3.3 V — uses the full 3.0–4.2 V range, at the
  cost of area, EMI, and BOM. Adopt if runtime per charge is the priority.

## Consequences

- Bulk capacitance near the module 3V3 pins must cover 500 mA TX bursts
  (≥ 22 µF local + 10 µF rail); see `ereader-pcb-design.md`.
- Usable battery floor is ~3.4 V; firmware low-battery warning triggers
  above that.
- Charge current (R_PROG) is re-chosen for the actual cell capacity
  (≤ 1C). 2.0 kΩ = 500 mA is the placeholder.
- A battery-sense divider to an ADC and the charger STAT line to a GPIO
  give firmware state-of-charge and charge state.
- The frontlight boost stage draws from VSYS, not +3V3.
