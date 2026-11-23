# Heater fan mount

Symphony: [`diagrams/electrical/circuit-inventory.md`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/circuit-inventory.md)

Combustion-air booster for the diesel heater. A 3" flex duct from a deck vent screws onto the bottom,
an 80 mm fan pushes the air up, and a slotted collar is hose-clamped over the heater's bottom rim.
A PWM board in a pocket beside the fan sets the speed from a knob on the cabin face.

![box, as printed](out/heater-fan-mount_box_pv_views.png)

## Parts, all PETG

| Part | File | Prints | Volume |
|---|---|---|---|
| Box: fan socket and controller pocket | `part-box.scad` | floor down, open top up, 0.8 mm 45° chamfer round the bed edge; the round knob hole (7.5) bridges its own crown; a one-line 45° web holds up the gland hole's crown, cut it out after printing | 38.7 cm³ |
| Lid with the 76 mm collar | `part-lid.scad` | plate down | 32.2 cm³ |
| Spigot: flange and duct thread | `part-spigot.scad` | flange down | 20.2 cm³ |
| **Gauge, prints first** | `part-gauge.scad` | ring faces down | 23.5 cm³ |

Every part prints in its model orientation. The knob face prints as a vertical wall, so it shows layer lines, not the plate's texture.
Four M4 screws through lid, fan, box floor and spigot flange; nuts sit in pockets in the flange.
12 V enters through a PG9 gland (16 mm hole) on the back wall, against the bulkhead.

## The gauge

![gauge](out/heater-fan-mount_gauge_pv_views.png)

| Ring | Try | If wrong |
|---|---|---|
| Left: 10 mm of the collar, slotted | drop over the heater's bottom rim | change `rim_d` (loose) or `collar_fit` |
| Right: 1.5 turns of the duct rib | screw the duct on | count 10 wire turns over a length; `pitch` = length / 10 |

## Numbers and where they came from

| Number | Value | Source |
|---|---|---|
| Heater rim, outside | ~75.4 (collar bore 76.0) | owner: a 76 bore was near a friction fit on the old part. **Unmeasured**: gauge |
| Duct wire pitch | 15, right-hand | owner estimate, 15-19. **Unmeasured**: gauge |
| Duct ID | 76.2 | 3" nominal |
| Fan | 80 x 80 x 25, holes 71.5 square, bore 76 | GDA8025 IP68 vendor drawing; thickness ~24.5 owner; holes match an earlier test print |
| Controller | 1803BK PWM board, 32 x 32 (35 with break-off edge), holes ~26 square | listing; not calipered |
| Pot shaft above the board | 7 | **estimate** |
| Pot shaft across the board | centred | owner: the knob is centred on the module, so knob, standoffs and pocket share one centre line; pocket 40 wide |
| PG9 gland | thread 15.2, hole 16 | catalogue typical, **unmeasured** |
| Walls | 2 shell, 3 knob face, 1.6 divider, 2.5 lid and flange | set by each wall's job; no structural load beyond the unit's own weight |
