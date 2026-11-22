# Masthead sky sensor

Symphony: [`diagrams/electrical/nav-light-controller.md`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/nav-light-controller.md)

Purpose: one small head at the masthead that logs daylight, its colour, UV and cloud cover (sky infrared temperature)
to Signal K. One custom board, assembled by JLCPCB, under one PTFE disc; the cat5 run down the mast plugs into it.
Supersedes the lower placements in [lux-capsule](../lux-capsule/README.md) and its siblings: the masthead is the only spot
with nothing above it (placement worked through 2026-11-20 against the Hans Christian 38T sail plan).

Nothing drawn yet. Next: the schematic.

## Owner's calls, 2026-11-20

- Masthead.
- Four sensors on one board: lux, colour, UV, sky IR.
- The long-cable I2C extender is on the board, not a separate box.
- The mast cable is its own run with a P82B96 at each end, not a leg of the existing QwiicBus (PCA9615) bus.

## Constraints

- The masthead already carries the combination nav-light fixture. An anchor light ~0.2 m away puts roughly 5 lux on an
  upward diffuser (estimate) against ~0.001 lux of night sky: the head sits above the fixture or behind a shade ring.
- Window: lux, colour and UV under one PTFE disc (PTFE passes UV; glass does not). Sky IR looks through its own hole,
  open or under thin polyethylene film; glass, acrylic and PTFE block long-wave IR.
- Head printed in ASA. No coating or potting over the sensor faces (it yellows and biases colour and lux).
- Heel tilts the cosine response; imu-tray's tilt can correct it in software.
- Field cable meets the board by connector, never soldered.

## Chip check, 2026-11-19 (LCSC and JLCPCB stock lookups, datasheets)

| Role | Part | LCSC | Stock | $ @10 | Supply; I2C | Addr |
|---|---|---|---|---|---|---|
| Lux | VEML7700-TT | C1850416 | 5900 | 0.99 | 2.5–3.6 V; bus 1.7–3.6 V | 0x10 |
| Colour | AS7341-DLGM (OLGA-8) | C2649486 | 5237 | 6.45 | **1.7–2.0 V**; pins abs max 3.6 V | 0x39 |
| 1.8 V rail for AS7341 | XC6206P182MR | C21659 | 31374 | 0.16 | — | — |
| Level shift for AS7341 | PCA9306DCUR | C33196 | 10667 | 0.46 | — | — |
| Sky IR | MLX90632SLD-DCB-000-RE | C7541116 | 2425 | 6.18 | 3.0–3.6 V, 3.3 V I2C; 50° FOV | 0x3A / 0x3B |
| UV | AS7331-AQFM (OLGA-16), UVA/UVB/UVC | C20482877 | **0 at JLC** | 13.09 | 2.7–3.6 V; needs a 3.3 MΩ ±1 % REXT | 0x74–0x77 by A0/A1 |
| Long cable | P82B96DGKR (MSOP-8), one at each end | C2652360 | 982 | 2.67 | 2–15 V; cable side at 12 V; 400 kHz over at least 20 m | — |

All JLC "extended" parts. No address clashes.

Replaced, 2026-11-20 (JLC stock lookup, TI and ams datasheets):

| Part | Why it went |
|---|---|
| LTR-390UV-01 | JLC: "no longer manufactured", 0 in stock |
| PCA9615 | 0 at JLC in both packages |

UV has no in-stock replacement at JLC: AS7331, LTR-390, VEML6075, SI1133, SI1145 and the GUVA photodiodes all show 0.
AS7331 is not marked end of life; it is picked on merit (true UVA, UVB, UVC channels, 3.3 V native).

## Open

- AS7331 sourcing: JLC global sourcing or a consigned part; distributor stock not yet read.
- The cabin-end P82B96 board, where the mast run meets the Pi's I2C: not drawn, no project yet.
- MLX90632 calibration starts at −20 °C object; a clear night sky often reads colder.
- Whether JLC assembles the AS7341's OLGA package: unverified.
- Masthead geometry (fixture, antenna, wind instrument positions): not known; give the head room, no caliper trip.
