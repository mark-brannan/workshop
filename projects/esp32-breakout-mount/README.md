# DIN-rail mount for an ESP32 breakout board

Purpose: hold an ESP32 breakout board on a 35 mm TS35 rail. A flat 5 mm plate has
four 6 mm standoffs for the board's M2 holes, so the pins and solder on its back
clear the plate. The underside carries the same four blind peg holes as
`../din-rail-psu-mount`; press in the owner's DIN clips (thing:2415668). Rail runs
along X. Print as modelled: plate flat, standoffs up, no supports.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Board hole spacing | 80 x ~75.5 | owner, caliper |

## Guessed

| Value | Now | Why |
|---|---|---|
| `standoff_h` | 6 | clears typical header pins and solder; check the board's back |
| `insert_d` | 3.2 | M2 heat-set insert; set ~1.8 to tap M2 into the plastic. Calibration pending |
| `plate_l` x `plate_w` | 92 x 86 | 6 mm margin around the standoffs; the board's outline is unmeasured |
