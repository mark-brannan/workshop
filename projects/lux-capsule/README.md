# Lux sensor capsule on top of a horizontal 1.5" tube

Symphony: [`diagrams/electrical/symphony-dc-overview.drawio`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/symphony-dc-overview.drawio)

Purpose: the smallest head that holds a VEML7700, a PTFE disc and the glass cabochon, sits on top of a horizontal 38.1 mm tube facing up, and is zip-tied on.
The cat5 pairs land directly on a small screw terminal; there is no extender board. Replaces the taller [lux-tube-cap](../lux-tube-cap/README.md), which assumed a vertical tube.

Cap 34 mm across and 18.7 mm tall (the dome stands 3.2 mm above it) on a 48 x 34 saddle, 13 mm of it below the tube's top.

| Part | What | Print |
|---|---|---|
| `cap` | Cup with the cabochon seat; two M2 screw holes | as modelled, supports for the dome seat |
| `riser` | Ring the VEML's corners rest on; the terminal lives inside it | as modelled |
| `base` | Saddle on the tube; a zip-tie groove each side of the cap, over the top and down both sides | saddle top on the bed, tube trench up |

Two versions (`exit`): `center` has a 7 mm hole through the base over a hole drilled in the tube's top wall, the cable going down inside the tube; `side` has no hole and a 6.5 mm notch
through the cap wall along the tube (+x), under the zip tie. Stack, bottom to top: base, riser, VEML7700 (chip up, terminal soldered on its back), PTFE disc, glass in the lip.
Two M2 self-tapping screws from below. Silicone in the glass lip, and PTFE to glass.

## Measured, and from what

| Item | Value | Source |
|---|---|---|
| Glass cabochon | 24.8 diameter, 6 high | owner, measured |
| Tube | 38.1 OD | owner |
| VEML7700 (Adafruit 4162) | 16.51 square, 1.6 | its Eagle .brd |

## Guesses (nothing measured yet)

The terminal (5-position, 2.54 mm pitch, 12.7 x 6 x 7.5), the PTFE disc (25 mm cut, not bought), tube inner diameter, cat5 outer diameter
(6.5 notch), the 7 mm hole to drill in the tube, and how the board is retained
(corners on the riser, loose; nothing clamps it).

## Open

- Terminal not chosen; if it is taller than 7.5 the riser grows.
- No gauge part.
