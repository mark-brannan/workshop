# Lux sensor capsule on the top of a 1.5" tube

Symphony: [`diagrams/electrical/symphony-dc-overview.drawio`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/symphony-dc-overview.drawio)

Purpose: the smallest head that holds a VEML7700, a PTFE disc and the glass cabochon, sits on the end of a 38.1 mm tube, and is zip-tied on.
The cat5 pairs land directly on a small screw terminal; there is no extender board. Replaces the taller [lux-tube-cap](../lux-tube-cap/README.md).

34 mm across, 18.7 mm tall (the dome stands 3.2 mm above the cap), narrower than the tube it sits on.

| Part | What | Print |
|---|---|---|
| `cap` | Cup with the cabochon seat; two M2 screw holes | as modelled, supports for the dome seat |
| `riser` | Ring the VEML's corners rest on; the terminal lives inside it | as modelled |
| `base` | Plate with three fingers that run down the tube, a zip-tie groove across them | plate top on the bed, fingers up |

Two versions (`exit`): `center` has a 7 mm hole through the base for the cable down the hollow tube; `side` has no hole and a 6.5 mm notch
through the cap wall at +x. Stack, bottom to top: base, riser, VEML7700 (chip up, terminal soldered on its back), PTFE disc, glass in the lip.
Two M2 self-tapping screws from below. Silicone in the glass lip, and PTFE to glass.

## Measured, and from what

| Item | Value | Source |
|---|---|---|
| Glass cabochon | 24.8 diameter, 6 high | owner, measured |
| Tube | 38.1 OD | owner |
| VEML7700 (Adafruit 4162) | 16.51 square, 1.6 | its Eagle .brd |

## Guesses (nothing measured yet)

The terminal (5-position, 2.54 mm pitch, 12.7 x 6 x 7.5), the PTFE disc (25 mm cut, not bought), tube inner diameter, cat5 outer diameter
(6.5 notch), whether three 3 mm PETG fingers hold under tie tension (layer lines run across their root), and how the board is retained
(corners on the riser, loose; nothing clamps it).

## Open

- Terminal not chosen; if it is taller than 7.5 the riser grows.
- No gauge part.
