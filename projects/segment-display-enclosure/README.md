# Segment display enclosure

Purpose: a small stand-alone box for the segment display module (the one the
halmet tier also carries). Two prints, no supports:

- **Shell** (`model.scad`), printed face down. The display looks out through a
  window, its face 0.5 mm behind the outer face. The board rests on four posts
  fused into the walls.
- **Back cover** (`part-back.scad`), printed outer face down. A locating lip fits
  inside the shell; four tubes press on the board's back; a slot at the -X end
  lets the wires out.

Four M2.5 x 20 self-tapping screws go cover -> tube -> board -> post, about 5 mm
into each post. Outside: 46.5 x 28.5 x 22.6 mm.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Board | 41.5 x 23.5 | owner, caliper |
| Hole spacing | 37.5 x 19, ~2.8 dia, edge 0.5 from board edge | owner, caliper |
| Display body | 30 x 14, face 7 above the board | owner, caliper |

## Guessed

| Value | Now | Why |
|---|---|---|
| `disp_dx`, `disp_dy` | 0, 0 | display assumed centred on the board |
| `board_t` | 1.6 | standard PCB |
| `rear_clear` | 11 | board back to cover: room for header pins and wire bends; sized so M2.5 x 20 screws reach |
| `cable_x` | -13 | wire slot at the -X end, where the header is assumed |
| `pilot_d` | 2.2 | M2.5 self-tapping; calibration pending |
| `lip_clear` | 0.25 | per side; fit calibration pending |
