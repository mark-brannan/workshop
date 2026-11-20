# Lux sensor capsule on top of a horizontal 1.5" tube

Symphony: [`diagrams/electrical/symphony-dc-overview.drawio`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/symphony-dc-overview.drawio)

Purpose: the smallest head that holds a VEML7700, a PTFE disc and the glass cabochon, sits on top of a horizontal 38.1 mm tube facing up, and is zip-tied on.
The cat5 pairs land directly on a small screw terminal; there is no extender board. Replaces the taller [lux-tube-cap](../lux-tube-cap/README.md), which assumed a vertical tube.

Cap 33 mm across, 15.5 mm tall with the dome 3.2 mm above that, on a 46 x 33 saddle with a small ear each side for the zip ties.
Top edge rounding is 4 mm (`edge_r`).

| Part | What | Print |
|---|---|---|
| `cap` | Cup with the cabochon seat; two M2 screw holes | as modelled, supports for the dome seat |
| `riser` | 2.5 mm ring the VEML's corners rest on | as modelled |
| `base` | Saddle on the tube; a zip-tie groove across each ear | saddle top on the bed, tube trench up |

Wiring: the VEML7700's own Qwiic socket takes a short pigtail; the cat5 pairs are joined to it outside the head, or inside the tube in the center
version. No terminal in the head. `center` has a 7 mm hole through the saddle over a hole drilled in the tube's top wall; `side` has no hole and a
5 mm notch through the cap wall along the tube (+x), under the zip tie.
Stack, bottom to top: base, riser, VEML7700 (chip up), PTFE disc, glass in the lip. Two M2 self-tapping screws from below.
Silicone in the glass lip, and PTFE to glass.

## Measured, and from what

| Item | Value | Source |
|---|---|---|
| Glass cabochon | 24.8 diameter, 6 high | owner, measured |
| Tube | 38.1 OD | owner |
| VEML7700 (Adafruit 4162) | 16.51 square, 1.6 | its Eagle .brd |

## Guesses (nothing measured yet)

The Qwiic socket's height (4.3) and position on the VEML7700 (it sets the PTFE height), the PTFE disc (25 mm cut, not bought), tube inner diameter,
the 7 mm hole to drill in the tube, 1 mm of wall beside each M2 screw, and how the board is retained (corners on the riser, loose; nothing clamps it).

## Open

- Whether the pigtail-and-splice wiring is wanted over a screw terminal; a terminal under the board adds about 7 mm of height and 1.1 mm of wall.
- No gauge part.
