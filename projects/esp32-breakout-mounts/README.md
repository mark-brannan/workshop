# DIN-rail mount for an ESP32 breakout board

Purpose: hold an ESP32 breakout board on a 35 mm TS35 rail. A flat 5 mm plate has
four 6 mm standoffs for the board's M3 holes, so the pins and solder on its back
clear the plate. The back is flat: two of the preferred DIN clips (Printables 420009, printed
as `../din-rail-psu-mount/out/din-rail-psu-mount_din-clip.3mf`, two M3 heat inserts each) screw on from the board side,
countersunk M3 x 6 under the board. The rail runs along X, the board's long side; each clip
spans the short side (Y, 51 mm between its screws), hook up (+Y). Print as modelled: plate flat,
standoffs up, no supports. Assembly render: `out/assembly.png`, `out/assembly_exploded.png` (`uv run python assembly.py`; the board is a stand-in slab).

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Board hole centres | 81.2 x 77.0 | owner, caliper: outside edge to outside edge 84.4 (long) x 80.2 (short), less a 3.2 hole; diagonal 115.2 agrees within 0.1 (any hole 3.0-3.25 fits it) |
| Hole size | 3.1-3.3, M3 | owner, plastic caliper, touch-dependent |

## Guessed

| Value | Now | Why |
|---|---|---|
| `standoff_h` | 6 | clears typical header pins and solder; check the board's back |
| `insert_d` | 4.0 | M3 heat-set insert; set ~2.6 to tap M3 into the plastic. Calibration pending |
| `plate_l` x `plate_w` | 93.2 x 89 | 6 mm margin around the standoffs; the board's outline is unmeasured |

## History

- 2026-11-24: the first gauge put the board's far holes ~1–1.5 mm off (owner, photos); spacing was 80 x ~75.5, now 81.2 x 77.0 from three caliper readings. Holes are M3, not M2.
- 2026-11-24: clip holes turned 90 degrees (owner): clips now span the board's short side, rail along its long side. Blind peg holes for thing:2415668 replaced by four countersunk M3 holes for the 420009 clip.
