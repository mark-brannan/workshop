# BME688 cabin screen

Purpose: an open, printed case for one Adafruit BME688 on the cabin's wood panelling, near the
companionway but not at it. It keeps out dust, drips and the odd splash, and lets cabin air reach
the chip quickly. No membrane, no gasket, no IP rating. The sealed box is [bme688-halpi2](../bme688-halpi2/).

## Mounting

For the underside of the panel above the berth by the nav station: plate up, two screws into the panel,
chip facing down. The panel is the roof. The cover is a floor with one 10 mm hole under a shallow arch that meets the floor at both
sides; four fins hold the arch up (arch 0.6 mm, three layers at its crown; fins 0.8 mm, two lines; floor 1.2 mm), each with a 3 mm gap either side of the hole so air can cross between them.
Air comes in the hole, runs out under the arch to its open ends, up and in. It prints floor-down with no
supports; no span is more than 5 mm (2.5 mm from its support). The cable leaves through an arched hole in the +x long wall near the Qwiic end, so it can run rearward along the panel. Just inside the hole it rides over a small block on the plate, against that wall; a cable tie (up to 3.6 wide) goes through a tunnel under the block and round the cable for strain relief. Nothing cuts through the plate, and the only hole in the walls is the cable exit.
32 x 62 x 15.6. Prints: `out/bme688-cabin-screen_overhead-body.3mf` and `_overhead-cover.3mf`; the cover takes
two M2.5 self-tapping screws on a diagonal, into pilot holes in the body.

The board sits in a seat: a 1.2 mm ledge under its edges, walls round it flush with its face, and an
10 mm gap in each short wall for the Qwiic plug. Four M2.5 self-tapping screws, one per corner of the
board, go into pilot holes in pads under it.

| Hardware | Count | Size |
|---|---|---|
| Pilot holes | 6 | 2.2 mm, 4.5 deep, blind; printed holes run small, so the first print is the test |
| Board screws | 4 | M2.5 x 6 self-tapping, pan head (bottoms out at 0.1 mm to spare) |
| Cover screws | 2 | M2.5 x 5 self-tapping, pan head, through 2.9 holes in the floor |
| Panel screws | 2 | M3 countersunk wood screws |

![overhead cut-away](out/overhead_section_views.png)

## Constraints

| | |
|---|---|
| Keeps out | dust, drips, a small chance of splash |
| Mount | two holes 51 mm apart: M3 countersunk wood screws into the panel, or the DIN clip (Printables 420009) |
| Cable | fixed, out the +x long wall through an arched hole; Qwiic pigtail inside |

## Measured, and from what

Nothing is calipered. The board's size and holes are from Adafruit's board file, the mount pitch from
the DIN clip's model; both are in [`parts.md`](../../../parts.md). The pilot holes (2.2) and the baffle's
fit (0.3 a side) are guesses until the calibration table has numbers.

## Not confirmed

- How fast the reading follows the cabin air through the arch.
- Whether the Qwiic plug and its wires fold into the 4 mm under the board.

## Build

```
uv run shop build projects/gas-sensors/bme688-cabin-screen
```
