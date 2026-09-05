# Decision 0003: USB-C + 1S LiPo, discrete load-share, 3.3 V LDO

**Status:**      Accepted
**Date:**        2026-09-05

## Context

The reader must run from a rechargeable battery and charge over USB-C, and
provide a clean 3.3 V rail to an MCU whose Wi-Fi TX peaks near 500 mA. Three
sub-decisions: charger, source selection (USB vs battery), and regulation.

A single-cell LiPo (3.0–4.2 V) is the obvious chemistry for a pocket device.
The tension is regulation: an LDO is tiny and quiet but cannot boost, so the
3.3 V rail sags once the cell falls below ~3.4 V, wasting the battery tail;
a buck-boost uses the whole range but adds cost, area, and switching noise.

## Decision

Charge with **MCP73831** (PROG-set, 500 mA). Select the source with a
**discrete load-share** — a DMG2305UX P-FET (battery→VSYS, off when USB
present) plus a Schottky (USB→VSYS) — so USB powers the system and only
charges the cell when plugged. Regulate VSYS→3.3 V with an **AP2112K-3.3**
LDO (600 mA), generously bulk-decoupled for TX bursts.

## Considerations

**Pro:** Minimal BOM and board area; every part is cheap, common, and hand-
solderable; the load-share avoids simultaneously charging and discharging
the cell; the LDO is silent (no switching noise near the RF module or ADC).

**Con:** LDO dropout wastes the 3.0–3.4 V battery tail; the discrete
load-share has a Schottky drop (~0.3 V) on the USB path and no proper DPPM
(dynamic power-path management).

Rejected for v0.1, kept as upgrade paths:
- **MCP73871** power-path charger — seamless source switching + DPPM, but
  larger and more complex. Adopt if "run while charging a dead battery"
  behaviour matters.
- **TPS63020 buck-boost** on the 3.3 V rail — uses the full 3.0–4.2 V
  range, at the cost of area, EMI, and BOM. Adopt if runtime per charge is
  the priority.

## Consequences

- Bulk capacitance near the module 3V3 pins must be sized for 500 mA TX
  bursts (≥ 22 µF local + 10 µF rail); see `DESIGN.md` §3.5.
- Effective usable battery floor is ~3.4 V; firmware low-battery warning
  should trigger above that.
- Charge current (R_PROG) must be re-chosen for the actual cell capacity
  (≤ 1C). 2.0 kΩ = 500 mA is the placeholder.
- A battery-sense divider to an ADC and the charger STAT line to a GPIO give
  firmware state-of-charge and charge state.
