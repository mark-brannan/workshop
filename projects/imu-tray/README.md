# IMU tray: ICM-20948 and QwiicBus EndPoint, mid-boat

Symphony: [`reference/pypilot_containerization.md`](https://github.com/mark-brannan/symphony/tree/main/reference/pypilot_containerization.md), [`runbooks/pypilot.md`](https://github.com/mark-brannan/symphony/tree/main/runbooks/pypilot.md)

Purpose: hold pypilot's IMU and its cat5e I2C extender on a horizontal shelf in the middle of the boat, in a dry spot.
A walled box with four mounting feet outside it, so it screws down with or without the boards in; the wall tops are rebated for an optional 3 mm lid, clear acrylic or printed. Not sealed.
Every joint plugs in (RJ45, Qwiic); no solder. Securing the cat5e is done separately, off the tray.

![assembly](out/assembly.png)

| Part | File | Make |
|---|---|---|
| Tray | `out/imu-tray_scad.3mf` | print floor down, no supports |
| Lid, optional | `out/imu-tray_lid.dxf` / `out/imu-tray_lid.3mf` | cut from 3 mm clear acrylic, or print flat |
| Fit gauge, prints first | `out/imu-tray_gauge.3mf` | thin slices of the tray: try an M2.5 self-tapper in a pilot hole and a shelf screw in a foot hole |

PETG. Box 103.6 x 44 x 27.5 high; 125.6 long over the feet.

## What goes in

| | |
|---|---|
| Boards | ICM-20948 (Adafruit 4554) and QwiicBus EndPoint (SparkFun 16988), eight M2.5 x 8 self-tapping screws into 2.1 pilot holes. Brass or stainless near the IMU (steel near the magnetometer is a hard-iron offset) |
| Between them | Qwiic cable, 100 mm: EndPoint's +y port, round to the IMU's -x socket |
| Shelf | four #8 or M4 pan-head wood screws, one through each corner foot |
| Lid | drops into the rebate, flush with the wall tops, 0.3 loose each side |

## Assembly

1. Box on the shelf, four screws through the feet, any time. Arrow on the floor (+x, the IMU's x axis) toward the bow, or set pypilot's heading offset to match.
2. Boards on, eight screws. Qwiic cable between them. Plug the cat5e in through the opening in the -x wall.
3. Lid on, if wanted.

## Coating (optional)

One thin coat of acrylic conformal coating (MG Chemicals 422C or similar) on both boards, Qwiic sockets and RJ45 jack masked. About 15 min hands-on.
It guards against salt-air corrosion. Skip it if the spot stays dry.

## Numbers and where from

| Value | Source |
|---|---|
| EndPoint 44.45 x 25.4, holes 20.32 square from the far end | SparkFun board file, parts.md |
| ICM-20948 25.4 x 17.78, holes 20.32 x 12.7 | Adafruit board file, parts.md |
| Jack overhang 9.7, 16.5 wide | photo, as in lux-tube-cap |

## Guessed

| Value | Now | Check |
|---|---|---|
| Jack height above the board | 13.5 | lid underside 1.9 above it |
| Plug axis above the board | 6.5 | opening 19 wide, from 1 mm under the plug to the top |
| M2.5 self-tapper pilot | 2.1 | the gauge |
| Foot hole | 4.8 | the gauge; printed holes run small on the K2 |
| Lid fit in the rebate | 0.3 each side | first cut; K40 kerf unmeasured |
| Qwiic plug and cable room on the EndPoint's +y side | 11 | the cable route isn't modelled |
