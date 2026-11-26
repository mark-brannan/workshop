# DIN-rail mount for the MRD066A ESP32 terminal adapter

Purpose: hold the "MRD066A for esp32 terminal adapter" breakout (unknown brand, 63 x 77) on a 35 mm TS35 rail.
It is [esp32-freenove-mount](../esp32-freenove-mount/) with this board's M2 hole pattern; everything else
(5 mm plate, four 6 mm standoffs, two Printables 420009 clips printed as
`../din-rail-psu-mount/out/din-rail-psu-mount_din-clip.3mf`, countersunk M3 x 6 under the board) is the same.
The rail runs along X, the board's long side (77), so both terminal strips lie along the rail and their wire entries
face up and down, toward the wire ducts (vendor photo: strips run the 77 side, entries face the long edges).
The short side (63) runs across the rail (Y), as does each clip (51 mm between its screws), hook up (+Y).
Board screws are M2, into M2 heat-set inserts in the standoffs.
Print as modelled: plate flat, standoffs up, no supports. The gauge (`out/esp32-mrd066a-mount_gauge.3mf`) prints first.
Assembly render: `out/assembly.png`, `out/assembly_exploded.png` (`uv run python assembly.py`; the board is a stand-in slab).

Symphony: none yet

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Board outline | 63 x 77 | owner, caliper |
| Hole size | 2.2, M2 | owner, caliper |
| Hole centres, short side (Y) | 58.6 | owner, caliper: 56.4 inside to inside, plus one hole |
| Hole centres, long side (X) | 72.9 | owner, caliper: 70.7 inside to inside, plus one hole |
| Diagonal check | 91.33 modelled vs 91.4 | owner, caliper: inside to inside diagonal |
| Hole edge to board edge | ~0.5 by eye | owner; the centres and outline give 1.1 (short side) and 0.95 (long side) |

## Guessed

| Value | Now | Why |
|---|---|---|
| `standoff_h` | 6 | as on the Freenove mounts; clears pins and solder on the back |
| `insert_d` | 3.2 | M2 heat-set insert (3.5 OD); ~1.7 to tap M2 into the plastic. Calibration pending |
