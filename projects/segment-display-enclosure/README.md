# Segment display enclosure

Purpose: a small stand-alone box for the TM1637 4-digit segment display module
(the one the halmet tier also carries). Two prints, no supports:

- **Shell** (`model.scad`), printed face down. The display looks out through a
  window, its face 0.5 mm behind the outer face. The board's front rests on four
  corner posts, clipped clear of the display body.
- **Back cover** (`part-back.scad`), printed outer face down. A lip locates it
  inside the shell, four tubes press on the board's flat back, and a tongue
  fills the end-wall notch above the plug.

The right-angle header is on the board's front at one short end, pins pointing
out past the board edge. A Dupont plug pushes onto them from outside through a
window in that end wall. Four M2.5 x 12 self-tapping screws go cover -> tube ->
board -> post, about 5 mm into each post. Outside: 46.5 x 28.5 x 14.6 mm.

`out/segment-display-enclosure_review.png`: shell, cover and an exploded
assembly with stand-ins, from above, below and the face.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Board | 41.5 x 23.5 | owner, caliper |
| Hole spacing | 37.5 x 19, ~2.8 dia, edge 0.5 from board edge | owner, caliper |
| Display body | 30 x 14, face 7 above the board | owner, caliper |
| Display to pin end | 5, exact; the window is anchored here | owner |
| Display to clean end | 7.1 measured, 6.5 by difference; the display may be ~29.8 at its base | owner, caliper |
| Display to long edges | 4.5 (-Y, bottom with pins on the right, seen from the front) and 5 | owner, caliper |

## Guessed

| Value | Now | Why |
|---|---|---|
| header pin height | plug window 3.3 tall from the board's front down | right-angle header pins ~1.3 above the board, from the photo |
| `board_t` | 1.6 | standard PCB |
| `rear_clear` | 3 | board back to cover: solder joints only |
| `pilot_d` | 2.2 | M2.5 self-tapping; calibration pending |
| `lip_clear` | 0.25 | per side; fit calibration pending |
