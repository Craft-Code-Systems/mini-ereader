# Decision 0004: Program over native USB, no UART bridge or auto-reset circuit

**Status:**      Accepted
**Date:**        2026-09-05

## Context

ESP32 boards traditionally add a USB-UART bridge (CP2102/CH340) plus a
two-transistor auto-reset circuit driven by DTR/RTS, so a host can flash
and reset without touching buttons. The ESP32-S3, however, has a **native
USB peripheral (USB-Serial-JTAG)** that exposes a serial/JTAG interface
directly and supports host-initiated download — no bridge chip needed.

## Decision

Connect USB-C D+/D− straight to the ESP32-S3 (GPIO20/GPIO19). Provide plain
**BOOT (GPIO0)** and **RESET (EN)** buttons with pull-ups. **Omit** the
USB-UART bridge and the DTR/RTS auto-reset transistor pair.

## Considerations

**Pro:** Fewer parts (no bridge IC, no transistor pair), less board area,
lower cost; JTAG debugging over the same USB port; one connector for power,
data, and debug.

**Con:** No classic DTR/RTS auto-reset, so some toolchains may need a manual
bootloader entry (hold BOOT, tap RESET) if auto-download misbehaves; relies
on the native-USB stack being healthy in firmware.

Rejected: **CP2102 + auto-reset** — the familiar path, but redundant on the
S3 and pure added cost/area. Reconsider only if a variant must present a
legacy COM port with hardware auto-reset for a fixed toolchain.

## Consequences

- BOM drops the bridge IC and two transistors + resistors.
- USB D± must still be routed as a ~90 Ω differential pair and protected
  (USBLC6-2 ESD recommended).
- Bring-up docs note the manual bootloader gesture as a fallback.
- GPIO19/20 are reserved for USB and excluded from the peripheral pin map.
- The physical BOOT/RESET contacts started as tactile switches and were
  replaced with bare jumper pads in Rev C3 — see
  [Decision 0008](./0008-navigation-input.md) for the current implementation
  (`JP5`/`JP6`, screwdriver/tweezer-shortable). This ADR's "buttons" language
  describes the original implementation; the architectural call it documents
  (plain GPIO0/EN triggers, no UART bridge, no auto-reset circuit) is
  unaffected by that change.
