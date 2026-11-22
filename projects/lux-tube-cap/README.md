# Lux sensor head on top of a 1.5" tube

Symphony: [`diagrams/electrical/symphony-dc-overview.drawio`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/symphony-dc-overview.drawio)

Purpose: the simplest head that caps a 38.1 mm tube, zip-tied on, carrying the VEML7700 under a glass cabochon and PTFE diffuser,
with a cat5 run to a QwiicBus EndPoint. Same electronics as [lux-sensor-mount](../lux-sensor-mount/README.md), no arm.

Two versions of one head (`exit` in `model.scad`):

| | Cable | Body part | Height above tube |
|---|---|---|---|
| center | down the hollow tube; the plug rises through a 20 mm floor hole into the jack | `part-body-center` | 73 + 15 skirt |
| side | out of a 8 mm hole in the wall; the plug sits in a bay above the tube's top face | `part-body-side` | 94 + 15 skirt |

Shared: `part-lid` (window, drip skirt), `part-ring` (clamps the PTFE), `part-deck` (VEML plate). M3 heat-set inserts, PETG.
Assembly: EndPoint slides down the two card guides (hot-glue or pot it) with the cable plugged in; Qwiic cable to the VEML on the deck;
deck onto the posts; lid with two M3x16 from the top; ring with two M3 from below; silicone in the glass lip and round the lid seam.
Zip ties go in the two grooves on the skirt; four slits let them close it on the tube.

The EndPoint stands on edge, jack down, so the plug goes in straight and the head stays 46 mm across. The cost is height.

## Measured, and from what

| Item | Value | Source |
|---|---|---|
| Glass cabochon | 24.8 diameter, 6 high | owner, measured |
| Tube | 38.1 OD | owner |
| EndPoint, VEML7700 | as in lux-sensor-mount | their Eagle .brd files |

## Guesses (nothing measured yet)

Tube inner diameter (the center version needs a bore over about 20 for the plug), RJ45 jack and plug heights, plug axis 6.5 above the board,
the Qwiic port position on the VEML and the deck notch that serves it, skirt fit (0.4 loose), whether four slits and two ties clamp it,
and the cable bend in the side exit. Print the skirt and floor first against the real tube.

## Open

- Qwiic cable not modelled. No gauge part yet.
- Cat5 shield termination is outside this part.
