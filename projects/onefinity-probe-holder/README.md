# Onefinity touch-probe holder

Purpose: park the Onefinity touch probe on a vertical surface in front of you (bench or enclosure side), cords still
attached, angled so you can reach in and lift it out. The probe drops in point first, as a diamond, its pocket corner
down. Its two lower edges sit in a 90° V, and its top leans out toward you 30°, so gravity holds it. The large flat
face rests on a support wall on your side, facing down; the machined face (the 54 mm pocket) points up, toward the wall, open between the fins: no lip, since the lean keeps the probe on the support wall and the open side makes a wider target for the point. The V
sides reach 40 mm up, about half the probe, and the support wall, a quarter circle about the V point, reaches 52 mm: just past the probe's centre of mass, 46 mm up. The top stays open. The cords leave
the two upper edges and nothing gets in their way. The V flares out 4 mm a side toward its top so the probe finds its seat by sliding. The V's side walls carry on toward the wall as fins until they meet the 5 mm plate, so they hold the cradle up. Fins meet the plate through an R6 concave fillet. The point is open: the V arms stop 10 mm up the probe's edges, cut by a 90° notch square to the arms, so the tip hangs free and only the arms and the support wall hold the probe. A 3 mm tab inside each fin, near its top, laps 3 mm over the raised lip on the machined face, 1 mm clear of it; the pocket passes under freely and the lip slides the last 4.5 mm under the tab, past a 45° lead-in. Outside edges are rounded, the V arms' top edges R2.

![probe in place](out/concept_with_probe.png)

## Files (out/)

`onefinity-probe-holder_scad.3mf` / `.stl`: the holder, printed as installed: the plate's lower edge on the bed. `concept_with_probe.png`, `concept_side.png`: the probe resting in it (preview, `-D show_probe=true`).

Hardware: 2 × #8 (4 mm) countersunk wood screws, about 25 mm long, through a 5 mm plate. Both sit at the plate's top (z 82), above the cradle, where the probe's weight pulls the plate off the wall. A driver reaches them straight on over the support wall.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Probe block | 63.5 × 63.5 × 18.8 | owner, caliper |
| Pocket | 54 × 54, square to the block, in one corner, open on two edges; leaves 15 thick | owner, caliper; photos |
| Lip | 9.5 wide along the two upper edges (63.5 − 54) | derived |
| Cord exits | roughly centred on the two lipped edges | owner |

## Guessed

| Value | Now | Why |
|---|---|---|
| `tilt` | 30° from vertical, top out toward the user | owner: 15 to 20, top out, bottom near the wall |
| `fit_t`, `fit_v` | 1.0, 0.8 a side, plus a 4 mm flare at the V's top | loose drop-in that guides itself. It's a holder, not a fixture, so no gauge print |
| `v_depth`, `back_h` | 40, 52 | owner: cover about half the square, a little more on the flat face, top open; the flat face needs cover only past the centre of mass (46 up, the pocket shifts it 1 mm up) |
| `plate_pt` | 14 | the plate stops just under the fins |
| `open_v`, tabs | 10; 3 in, 4.5 long, 3 thick | owner: about 10 mm of the point open; tabs a few mm over the lip |
| Screws | 2 at ±25, z 82, above the cradle; holes 5, countersink 10 | #8 wood screws, loose; printed holes run small. High, because the load pulls the top of the plate off the wall |

## How overhangs are held (print orientation = as installed)

- V arm undersides and the fins: 52° from horizontal, because the 45° V is tilted back 30°.
- The open point's notch faces are square to the V arms, so they lean 52°.
- Each tab's underside, facing the support wall, leans 60°; its sides are square to the arms.
- The R6 fillet where the fins meet the plate runs from vertical at the plate to the face it joins, so it is never flatter than that face.
- The support wall's outer face leans out at 60°.
- Screw holes run horizontally with teardrop tops. Countersinks are 90° cones.
- The test allows under 40 mm² of flat overhang: the 3 mm corner rounds of the quarter circle pass through flat (44–46°) for a few mm.

Volume 60.5 cm³ (about 75 g PETG), down from 93.3 with the nose cut out and the plate shortened.
