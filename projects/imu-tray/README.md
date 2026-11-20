# IMU tray: ICM-20948 and QwiicBus EndPoint, mid-boat

Symphony: [`reference/pypilot_containerization.md`](https://github.com/mark-brannan/symphony/tree/main/reference/pypilot_containerization.md), [`runbooks/pypilot.md`](https://github.com/mark-brannan/symphony/tree/main/runbooks/pypilot.md)

Purpose: hold pypilot's IMU and its cat5e I2C extender on a horizontal shelf in the middle of the boat, in a dry spot.
Not sealed: a vented cover keeps off dust, fingers and dropped tools, and lets the boards breathe so damp doesn't collect inside.
Every joint plugs in (RJ45, Qwiic); no solder.

![assembly](out/assembly.png)

| Part | File | Print |
|---|---|---|
| Tray | `out/imu-tray_scad.3mf` | floor down, no supports |
| Cover | `out/imu-tray_cover.3mf` | roof down, no supports |
| Fit gauge, prints first | `out/imu-tray_gauge.3mf` | 1 mm outline with 5 mm post rings: try an M2.5 self-tapper in a pilot hole and a shelf screw in each shelf hole |

PETG. Outside about 144 x 43 x 28.5 high, saddle and ear included.

## What goes in

| | |
|---|---|
| Boards | ICM-20948 (Adafruit 4554) and QwiicBus EndPoint (SparkFun 16988), eight M2.5 x 8 self-tapping screws into 2.1 pilot holes, no inserts. Brass or stainless near the IMU (steel near the magnetometer is a hard-iron offset) |
| Between them | Qwiic cable, 100 mm: EndPoint's +y port, round to the IMU's -x socket |
| Shelf | two #8 or M4 pan-head wood screws on the centre line: the ear past the IMU and the hole by the saddle, both reachable with the boards in |
| Cover | drops over a 3 mm lip, 0.4 loose each side; nothing holds it down |
| Cat5e | one zip tie through the saddle, so a tug pulls on the tray, not the jack |

## Assembly

1. Boards on, eight screws in.
2. Qwiic cable between them.
3. Tray on the shelf, arrow (+x, the IMU's x axis) toward the bow, or set pypilot's heading offset to match. Plug the cat5e in, tie it to the saddle.
4. Cover on.

## Coating (optional)

One thin coat of acrylic conformal coating (MG Chemicals 422C or similar) on both boards, Qwiic sockets, RJ45 jack and the IMU chip's top masked or not: acrylic is fine over the ICM-20948. About 15 min of hands-on time.
It guards against salt-air corrosion; the cover does the rest. Skip it if the spot stays dry.

## Numbers and where from

| Value | mm | Source |
|---|---|---|
| EndPoint 44.45 x 25.4, holes 20.32 square from the far end | | SparkFun board file, parts.md |
| ICM-20948 25.4 x 17.78, holes 20.32 x 12.7 | | Adafruit board file, parts.md |
| Jack overhang 9.7, 16.5 wide | | photo, as in lux-tube-cap |

## Guessed

| Value | Now | Check |
|---|---|---|
| Jack height above the board | 13.5 | cover has 2.9 above it |
| Plug axis above the board | 6.5 | plug opening 19 wide, 23 high from the floor |
| M2.5 self-tapper pilot | 2.1 | the gauge |
| Shelf hole | 4.8 | the gauge; printed holes run small on the K2 |
| Qwiic plug and cable room on the EndPoint's +y side | 11 | look at the assembly; the cable route isn't modelled |
