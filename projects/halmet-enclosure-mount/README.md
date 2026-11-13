# HALMET adapter plate for the 158x90x60 waterproof box

Purpose: hold a Hat Labs HALMET board in Hat Labs' pre-drilled 158x90x60 mm
enclosure (SKU ECK-PW158-H). The board's two M3 slots match nothing in the box,
so a printed frame screws to the box's six holed floor bosses, rests on its
four no-hole posts, and carries two standoffs for the board. Box photos and
inside measurements: [`enclosure/`](enclosure/README.md).

![frame](out/halmet-enclosure-mount_scad.png)

![overlay](out/overlay.png)

## Status

- [x] Board geometry, from the KiCad file
- [x] Board geometry drawn against the box (`overlay.py`)
- [x] `model.scad`, tests, render, 3MF and laser DXF
- [x] Rest pads on the four no-hole posts, zip-tie slots, underside pockets over the bosses (`model.scad`, tests)
- [x] Build and test the post/tie revision; `overlay.py` draws the built DXF (`out/overlay.png`)
- [x] Raised SSD1306 display posts (`model.scad`, tests, overlay)
- [x] Hex-lightened plate replaces the open frame; every display post on solid plate
- [ ] Fit check in the box, then tune the box parameters
- [ ] Final print or cut, fitted

## Known, and from what


Board coordinates: origin at the board's lower-left bounding corner, terminal
blocks on the left, USB tab on the right, component side up.

| Value | mm | Source |
|---|---|---|
| Board bounding size | 89 x 58 | `HALMET.kicad_pcb`, hatlabs/HALMET-hardware |
| Corner cut-outs | concave, radius 8.5, at three corners | same |
| USB tab | right edge steps in 6 mm above y = 24.7 | same |
| Mounting slot 1 centre | (22.75, 51.5) | same |
| Mounting slot 2 centre | (67.25, 6.5) | same |
| Slot size | 4.8 x 3.2 oval, long axis at 45 degrees, unplated | same |
| Slot to slot | 44.5 across, 45.0 up, 63.3 direct | same |
| Underside | solder jumpers and through-hole pin stubs only | same |
| Box outside | 158 x 90 x 60 | vendor page |
| Box wall holes | six 13 mm, four with PG7 plugs, all on one long wall | vendor page and photos |

## Estimated

The box is too deep for calipers to reach the bosses squarely, so these are the
owner's eyeball numbers. The frame is built to be tuned from a fit check.

| Parameter | Now | Source |
|---|---|---|
| `boss_span` | 140 | first print, scaled by its own 144 mm length; 136 put the screws at the fork mouths |
| `boss_pitch` | 22.5 | 21 printed with the outer screws inside their slots; scaled from the photo of that print against its own 21 mm slot pitch |
| Boss height | 3.5 | owner; read as height, not hole diameter (agent's reading) |
| Solid post height | 2 | owner; lower than the bosses, so the frame passes over them |
| Inner floor | 151 x 83 | owner |
| Floor to lowest gland nut | 2 to 3 | owner; the frame stays 14 mm clear of that wall in plan |
| `screw_d` | 3.4 | guess; the boss hole diameter is unmeasured |

## Design

- One plate, 145 x 77, lightened by a hex lattice: 9 mm cells, 2 mm walls, a
  2 mm rim. Cells are clipped where they meet a solid island (screw ends, rest
  pads, standoffs, rests, tier bosses, tie slots). 25.8 cm3 measured from the
  STL, against 11 for the earlier open frame; the plate is the stiffer of the two.
  `hex_flat`, `hex_web`, `rim_w` tune it.
- Each end bar has three fork slots, open toward the box wall, so a boss
  anywhere within `slot_reach` (2.5 mm) of `boss_span` still takes its screw.
- Two standoffs, 6 mm, at the board's slot centres, each with an M3 heat-set
  insert. Two plain rests on the other diagonal so pushing a plug into a
  terminal block does not rock the board.
- Flat underneath, resting on the six bosses. Four pads reach over the no-hole posts, which sit
  about 1 mm lower; a 1 mm stick-on pad on each closes the gap if the plate rocks.
- Zip-tie strain relief: slot pairs, the tie looping under the frame. Six
  along the gland-side edge, chamfered underneath where the tie turns, two on the left end beside the terminal blocks. Positions are lists at the top of the model.
- `board_dy` moves the board, rails and standoffs together, away from the
  gland-nut wall.
- Display tier, a separate flat print (`part-tier.scad`): a plate at the rim carrying the 0.96" SSD1306
  and, below it, a TM1637 4-digit module, each on M2.5 F/F standoffs screwed up from under the tier.
  It sits on four 19.7 mm M3 F/F standoffs, screwed up through counterbored pads on the plate
  before the plate goes in the box; four M3 from above hold the tier down.
- Light sensor, under the tier: the LM393 module ([`parts.md`](../../parts.md)) on two more 19.7 mm
  F/F standoffs, seated on the plate and screwed up from below. One takes the module's M3 hole; the other
  is a plain rest under the photocell end. The photocell end sits just past the tier's left edge, so the
  cell sees the lid with its leads bent up. Bend the header pins down past the board's end; the plug hangs
  toward the plate. Hole position and trimpot height are guesses: caliper them.

## Fit check

`out/halmet-enclosure-mount_gauge.3mf` is the same outline as a 1 mm plate with big windows;
2 mm stubs, holed through, mark the standoffs, rests and tier bosses. Lay it on the bosses, read where
each boss sits in its fork, and change `boss_span` and `boss_pitch` to centre
them.

## Laser

`out/halmet-enclosure-mount_scad.dxf` is the same outline with M3 through
holes where the standoffs go; use two loose 6 mm M3 spacers. 3 mm acrylic
cuts cleanly but cracks at a fork tine if a screw is overtightened; a printed
frame is the better part for a boat.
