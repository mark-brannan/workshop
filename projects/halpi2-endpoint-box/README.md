# HALPI2 EndPoint box

Symphony: none yet

Purpose: hold the HALPI2-end QwiicBus EndPoint just outside the HALPI2, where plain I2C becomes cat5e.
A round 4-core lead (a USB offcut will do) leaves the HALPI2 through one of its PG7 glands and plugs into one Qwiic socket.
The other Qwiic socket feeds the BME688 box. The RJ45 goes to the far EndPoint (the IMU tray).
The board can be conformal-coated or potted; the box suits either, and that choice is still open.

![views](out/halpi2-endpoint-box_scad_pv_views.png)

| Part | File | Make |
|---|---|---|
| Box | `out/halpi2-endpoint-box_scad.3mf` | PETG, floor down, no supports |
| Fit gauge, prints first | `out/halpi2-endpoint-box_gauge.3mf` | try an M3 in a post pilot and the clip screws or wood screws in the ears |

60.7 x 45 x 26.1 high; 62 across the ears.

## How it mounts

Every mounting screw is outside the cavity; the floor has no holes.

| Where | How |
|---|---|
| DIN rail, behind the breaker panel | preferred clip (Printables 420009), two M3 pan heads through the ears into its inserts, 51 apart. The rail runs along the box's length, so the RJ45 faces along the rail |
| Upside down under a panel | two wood screws (#6 / 3.5) through the same ears |

The walls step 3 mm inward at each ear, so a head up to 12 across clears them.

## Coated or potted

| | Coated | Potted |
|---|---|---|
| Board | four M3 x 8 into the posts | same, then resin |
| Qwiic cables | up and out through the rim notches | plugged in first; resin to just under the notches (14 above the floor bottom, 6 over the board) |
| RJ45 | its mouth sits in the +x wall's window | same; tape the window's edge outside before pouring, the jack body closes the rest |
| Lid | optional 3 mm plate in the rebate (not drawn yet) | none |

## Numbers and where from

| Value | Source |
|---|---|
| Board 44.45 x 25.4; holes 2.54 / 22.86 from the -x end, 20.32 apart | SparkFun board file, parts.md |
| Qwiic sockets 12.7 from the -x end, one each long edge | same |
| Jack overhang 9.7, 16.5 wide | photo, as in lux-tube-cap |
| DIN clip screw pitch 51 | parts.md |

## Guessed

| Value | Now | Check |
|---|---|---|
| Jack height above the board | 13.5 | sets the window height and the rebate |
| Jack bottom flush with the board's top past the edge | yes | if it drops below, the window must go lower |
| M3 pilot | 2.6 | the gauge |
| Ear hole | 4.2 | the gauge; K2 holes print small |
| Qwiic plug and cable turn in 7.3 each side | enough | the plug in hand |

## Build

```
uv run shop build projects/halpi2-endpoint-box
uv run pytest -q projects/halpi2-endpoint-box
```
