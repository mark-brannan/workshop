# BME688 cabin screen

Purpose: an open, printed case for one Adafruit BME688 on the cabin's wood panelling, near the
companionway but not at it. It keeps out dust, drips and the odd splash, and lets cabin air reach
the chip quickly. No membrane, no gasket, no IP rating. The sealed box is [bme688-halpi2](../bme688-halpi2/).

![cut-away](out/section_views.png)

## How it breathes

Air enters a slot that faces down, rises between the cover and a baffle, turns over the baffle's
top and falls onto the chip. The test fires rays from the chip in fourteen directions; all are blocked.

## Overhead variant

For the underside of the panel above the berth by the nav station: plate up, two screws into the panel,
chip facing down. The panel is the roof. The cover is a floor with one 10 mm hole under a shallow arch that meets the floor at both
sides; four fins hold the arch up (arch 0.6 mm, three layers at its crown; fins 0.8 mm, two lines; floor 1.2 mm), each with a 3 mm gap either side of the hole so air can cross between them.
Air comes in the hole, runs out under the arch to its open ends, up and in. It prints floor-down with no
supports; no span is more than 5 mm (2.5 mm from its support). The cable leaves through an arched hole in the +x long wall near the Qwiic end, so it can run rearward along the panel. Just inside the hole it rides over a small block on the plate, against that wall; a cable tie (up to 3.6 wide) goes through a tunnel under the block and round the cable for strain relief. Nothing cuts through the plate, and the only hole in the walls is the cable exit.
32 x 62 x 15.6. Prints: `out/bme688-cabin-screen_overhead-body.3mf` and `_overhead-cover.3mf`; the cover takes
two M2 screws on a diagonal, into heat-set inserts in the body.

The board sits in a seat: a 1.2 mm ledge under its edges, walls round it flush with its face, and an
8 mm gap in each short wall for the Qwiic plug. Two M2 screws on one diagonal go into heat-set inserts in
pads under the board; the walls stop it turning, so the other two holes stay empty.

| Overhead hardware | Count | Size |
|---|---|---|
| M2 heat-set inserts | 4 | 3.2 hole, 4 deep (+0.5); the insert size is a guess until the bag or calipers say |
| Board screws | 2 | M2 x 5 pan head (x 6 bottoms out at 0.1 mm to spare) |
| Cover screws | 2 | M2 x 6 pan head |
| Panel screws | 2 | M3 countersunk wood screws |

![overhead cut-away](out/overhead_section_views.png)

## Constraints (wall variant)

| | |
|---|---|
| Keeps out | dust, drips, a small chance of splash |
| Mount | two holes 51 mm apart: wood screws into the panelling, or the DIN clip (Printables 420009) |
| Cable | fixed, out the bottom through a notch in the chamber floor; Qwiic pigtail inside |
| Size | 32 x 62 x 17 |

## Parts

| Part | Which |
|---|---|
| Printed | body `out/bme688-cabin-screen_scad.3mf`, cover `out/bme688-cabin-screen_cover.3mf` |
| Board | Adafruit BME688, PID 5046, on four M2.5 self-tapping screws (overhead: see its hardware table) |
| Cover | hooks under the roof's lip; two M2.5 self-tapping screws at the bottom |

## Measured, and from what

Nothing is calipered. The board's size and holes are from Adafruit's board file, the mount pitch from
the DIN clip's model; both are in [`parts.md`](../../../parts.md). The pilot holes (2.1) and the baffle's
fit (0.3 a side) are guesses until the calibration table has numbers.

## Not confirmed

- How fast the reading follows the cabin air through the baffle.
- Whether the Qwiic plug and its wires fold into the 4 mm under the board.

## Build

```
uv run shop build projects/gas-sensors/bme688-cabin-screen
```
