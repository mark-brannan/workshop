# DIN-rail mount for the Freenove ESP32/ESP32-S3 breakout board

Purpose: hold the Freenove "Breakout Board for ESP32/ESP32-S3" (the non-universal one, 87 x 75) on a 35 mm TS35 rail.
It is [esp32-freenove-universal-mount](../esp32-freenove-universal-mount/) with the board's hole pattern and a narrower plate; everything else
(5 mm plate, four 6 mm standoffs for M3 heat inserts, two Printables 420009 clips printed as
`../din-rail-psu-mount/out/din-rail-psu-mount_din-clip.3mf`, countersunk M3 x 6 under the board) is the same.
The rail runs along X, the board's long side; each clip spans the short side (Y, 51 mm between its screws), hook up (+Y).
Print as modelled: plate flat, standoffs up, no supports. The gauge (`out/esp32-freenove-mount_gauge.3mf`) prints first.
Assembly render: `out/assembly.png`, `out/assembly_exploded.png` (`uv run python assembly.py`; the board is a stand-in slab).

Symphony: none yet

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Board outline | 87 x 75 | vendor drawing |
| Hole size | 3.45, M3 | owner, caliper: short side 72.3 outside edge to outside edge, 65.4 inside to inside |
| Hole centres, short side (Y) | 68.85 | same two readings, averaged |
| Hole centres, long side (X) | 81.2 | owner, caliper: inside-edge diagonal 103, plus one hole = 106.45 centre diagonal |
| Hole edge to board edge | ~1 | owner, by eye; the model gives 1.2 (long) and 1.35 (short) |

## Guessed

| Value | Now | Why |
|---|---|---|
| `standoff_h` | 6 | as on the universal mount; clears pins and solder on the back |
| `insert_d` | 4.0 | M3 heat-set insert; ~2.6 to tap M3 into the plastic. Calibration pending |
