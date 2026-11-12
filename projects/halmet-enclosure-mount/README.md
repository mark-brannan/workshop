# HALMET adapter plate for the 158x90x60 waterproof box

Purpose: hold a Hat Labs HALMET board in Hat Labs' pre-drilled 158x90x60 mm
enclosure (SKU ECK-PW158-H). The board's two M3 slots match nothing in the box,
so a flat printed plate screws to the box's floor bosses and carries two
standoffs for the board.

![overlay](out/overlay.png)

## Status

- [x] Board geometry, from the KiCad file
- [x] 2D overlay (`overlay.py`, `out/overlay.png`)
- [ ] Enclosure measured with calipers (table below)
- [ ] `model.scad`, test, render
- [ ] Printed and fitted

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

## Guessed

Scaled from the vendor's one top-down photo; perspective makes these +/-5 mm.
The vendor publishes no drawing and no manufacturer part number.

| Value | Now | To measure |
|---|---|---|
| Holed bosses, end to end | 140 | centre to centre along the box length |
| Holed bosses, pitch on one end | 22 | centre to centre, three per end |
| Boss height and hole diameter | 5, 2.6 | depth gauge and a drill shank |
| Solid posts | 79 x 68.5, same height as the bosses | spacing, and height against the bosses |
| Inner floor | 150 x 82 | length and width at the floor |
| Floor to lowest wall fitting | 12 | floor to the underside of the lowest gland nut |

## Design

- Plate 146 x 56 x 3, flat on the six holed bosses, slotted along the box
  length so a boss estimate that is a few mm out still fits.
- Two standoffs, 6 mm, at the board's slot centres, each with an M3 heat-set
  insert. Two plain rests under the opposite corners so pushing a plug into a
  terminal block does not rock the board.
- The plate is narrower than the gap between the solid posts, so it passes
  between them whatever their height.
- A plate, not a grid: a grid earns its keep when the hole positions are not
  known. Here both ends are known, and a solid plate is stiffer for less print.
