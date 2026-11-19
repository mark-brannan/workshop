# Lux sensor head on the instrument tube

Symphony: [`diagrams/electrical/symphony-dc-overview.drawio`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/symphony-dc-overview.drawio)

Purpose: an upward-facing VEML7700 lux sensor on an arm clamped to the 38.1 mm tube, sealed behind a glass cabochon
and a PTFE diffuser, plugged in by cat5 with no soldering.

Moved here 2026-11-19 from symphony `hardware/lux_sensor/` (symphony#167, #168); this is the only copy.

## Parts (one `part-*.scad` each)

| Part | What | Print |
|---|---|---|
| `tray` | One bolt-in tray for both boards: potting wall round the edge and the EndPoint, a bridge carrying the VEML over the EndPoint, a 2.4 mm lip round the bridge | plate down |
| `ring` | Clamps the PTFE square against the glass; two M3 | flat |
| `lid` | Top plate with the glass lip, square PTFE pocket, two M3 inserts | top face down, supports for the dome seat |
| `arm` | Arm half with the collar half, four M3 insert posts for the tray | as modelled |
| `back` | Collar back half | as modelled |

M3 heat-set inserts throughout. PETG. The EndPoint is held by two M3x5 self-tapping screws (2.7 mm blind holes) through its jack-side mounting holes; the far pair is under the VEML bridge.

## Measured, and from what

| Item | Value | Source |
|---|---|---|
| Glass cabochon | 24.8 diameter, 6 high | owner, measured |
| Tube | 38.1 OD | owner |
| EndPoint (SparkFun 16988) | 44.45 x 25.4; Qwiic ports on both long edges, 12.7 from the far end; RJ45 at the near end | its Eagle .brd |
| VEML7700 (Adafruit 4162) | 16.51 square | its Eagle .brd |
| Pin rows | EndPoint J8 GND/VCC/SDA/SCL, VEML VIN/3V3/GND/SCL/SDA: cannot stack-solder | both .brd files |

## Guesses (nothing measured yet)

RJ45 jack height 13.5 and plug height 14, plug axis 6.5 above the board, VEML Qwiic port position, the 3 mm bridge clearance
over the EndPoint's ports, the 2.4 mm lip over the sensor chip, the 6 mm width of the Qwiic notches. The first test print is
the tray plus ring against real boards; a `part-gauge.scad` has not been made.

## Open

- Qwiic cable between the boards is not modelled.
- Potting compound and fill level not chosen.
- PTFE sheet not bought; the pocket is square 25.4.
