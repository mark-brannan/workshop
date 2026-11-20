# Rudder angle sensor

Symphony: none yet

Autopilot work is symphony#171; no symphony path covers the lazarette yet.

Purpose: a home-made stand-in for [pypilot's rudder sensor](https://pypilot.org/opencart/index.php?route=product/product&language=en-gb&product_id=54):
a Hall chip reads a magnet on the end of a shaft, with no contact and no seal, and gives a 3-wire analog angle. It bolts to the seat of
[`rudder-sensor-pedestal`](../rudder-sensor-pedestal/); its arm takes an M3 ball link and a 3 mm rod to the quadrant.

Rev 1, not printed. Nothing here is measured.

![section](out/rudder-angle-sensor_section.png)

The magnet (red and blue) turns in a chamber closed underneath by a 1 mm wall; the chip (black) is under that wall, in a cup potted to
the rim. Magnet face to chip top is **1.9 mm**: 0.5 air, 1.0 wall, 0.4 to the chip. Other views: `out/rudder-angle-sensor_{assembly,exploded}_views.png`.

## The board's output is 0 to 3.3 V, not 0 to 5 V

Read from Adafruit's schematic for the 6357: the chip's `VDD5` and `VDD3` pins are both on net `3.3V`, the output of the AP2127K-3.3
regulator `U2`, whose input is net `VCC` (header pin 1, VIN). The chip's output pin is net `PWMOUT`, header pin 6. So fed 5 V, this
board's output swings 0 to 3.3 V and follows the regulator, not the 5 V supply. pypilot's own sensor is ratiometric to 5 V. Ways out,
not chosen here:

- a bare AS5600 module wired the datasheet's 5 V way (5 V on VDD5V, only a capacitor on VDD3V3);
- keep this board and accept 3.3 V full scale, if the controller's input can be scaled or calibrated to it.

From the AS5600 datasheet, not checked on a part: the analog output spans a full turn by default, so ±35° of rudder uses about a fifth
of the swing until the range is narrowed over I2C, and the wrap point has to sit outside the rudder's travel.

## Sizes

| Size | Value | Source |
|---|---|---|
| Board outline, corner radius | 25.4 × 17.78, r 2.54 | [Adafruit's Eagle `.brd`](https://github.com/adafruit/Adafruit-AS5600-Magnetic-Angle-Sensor-PCB), layer 20 |
| Board mounting holes | four, 2.5 drill, 20.32 × 12.7 | same file |
| Chip position | board centre (12.7, 8.89), on the top side | same file, part `X1` |
| JST SH sockets | top side, 10.12 either side of the chip, 4.25 × 6.1 | same file, parts `CONN3`, `CONN4` |
| Header | six holes at 2.54 along one long edge, 6.35 from the chip | same file, part `JP1` |
| Board thickness | 1.6 | guess |
| Chip height | 1.6 | guess |
| JST SH socket height | 2.95 | guess |
| Bearing | 686: 6 × 13 × 5 | guess; the owner's pick, none on hand checked |
| Bearing inner race outer diameter | 8 | guess |
| Shaft | 6 | guess |
| Magnet | 6 × 2.5, diametric | guess |
| Flange | two M4 at 40 | guess, the pedestal's own guess |
| Arm stud radii | 40, 50, 60 | guess; the one used must equal the quadrant stud's radius |
| Every fit clearance | see `/* [Fits] */` in `model.scad` | guess; the repo's calibration table is unmeasured |
| Room under the board for header and plug | 8 | guess |
| Cable | 5 | guess |

Every bought part is a parameter at the top of `model.scad`. The tests build a 625 bearing on a 5 mm shaft, and a 608 on an 8 mm shaft
with a bare 23 mm module. The model stops with a message where a combination can't work: the Adafruit board's JST sockets stand up
beside the magnet chamber, which limits that board to bearings of about 16 mm outside diameter.

## Parts and how each prints

All five print flat with no slicer supports; `out/rudder-angle-sensor_scad.3mf` is the plate, one 3MF per part beside it.

| Part | Prints | Overhangs |
|---|---|---|
| Bearing body | floor down | Chamber and bearing bore only widen upward. The two JST reliefs in the underside have gable roofs. The cone sockets are 45°. The weep hole is a teardrop. |
| Electronics cup | open top up | Cable exit is a teardrop. Posts, pins and cone studs grow from the floor and rim. |
| Magnet cap | bearing side down | 45° chamfer on the bed side, so it touches the inner race only. Magnet pocket opens upward. |
| Arm | top face down | Hub, skirt and the step onto the inner race grow upward. Pinch screw hole and head pocket are teardrops, the nut trap a point-up hexagon. |
| Spacer sleeve | on end | none |

## Changed from the concept

- The JST sockets on the 6357 are taller than the chip, so a flat floor would put the magnet 3.2 mm from the chip. The body has two
  reliefs in its underside for them; the chip comes up to 0.4 under the wall.
- Body and cup are located by two cone studs on the cup's rim in cone sockets in the body, because the body's underside is its print
  bed and can't carry a spigot.
- The flange is the pedestal's M4, not M3.
- The arm's hub is as wide as its skirt and prints upside down, so nothing overhangs; the pinch slit runs through the skirt.

Suggestions the owner hasn't asked for, both in the model: the **skirt** on the arm's hub, lapping 3 mm down the body's top to shed
spray (`skirt_lap`), and the **weep hole** from the magnet chamber out the body's side (`weep_d = 0` removes it).

## Not printed

- AS5600 breakout (Adafruit 6357 by default; see the 3.3 V note)
- 6 × 2.5 diametric disc magnet
- 6 mm stainless shaft, about 32 long (`shaft_len` is echoed by the build); non-magnetic, 304 or 316
- two 686 bearings
- M3 × 16 screw and nut for the pinch clamp
- two M4 × 30 screws for the flange, through body and cup into the pedestal
- two M3 ball links, a 3 mm rod, and an M3 nut for the stud on the arm
- 3-conductor cable, a crimped 3-way plug, and a right-angle pin header soldered to the board's underside, pins running back under
  the board. No flexible wire is soldered to the board.
- potting epoxy, and putty to close the cable exit while it cures

## Assembly

1. Glue the magnet in the cap's pocket, face flush. Press and glue the cap on the shaft's end.
2. Drop shaft and cap into the body. Lower bearing, sleeve, upper bearing over the shaft; a drop of retaining compound on the outer races.
3. Arm on the shaft, pressed down lightly to take up bearing play, then the pinch screw.
4. Solder the header to the board, trim its stubs on the chip side, plug the cable in, seat the board on the cup's pins, cable out the side.
5. **Bench test before potting:** body on the cup, 5 V on, turn the arm, read the output across the whole travel.
6. Close the cable exit with putty, fill the cup to the rim, cure.
7. Body on the cup's studs, both onto the pedestal with the two M4; swing the arm off the screw it covers.

## To fill in before printing

- Bearing actually on hand: inside, outside, width, and the inner race's outer diameter
- Board actually bought, and the 3.3 V or 5 V choice above
- Magnet diameter and thickness; shaft diameter and whether a magnet sticks to it
- Quadrant stud radius, which fixes the arm hole
- Mount pattern and screw size of the pedestal's seat
- Header and plug: the height they need under the board
- What holds the M4 screws in the pedestal (its holes are plain)
- Fit clearances, once `projects/calibration/` has numbers

Open: axis offset. The datasheet wants the magnet within 0.25 mm of the chip's centre; here that rides on printed pins, studs and a
printed bore, none of it measured. The bench test is the check.
