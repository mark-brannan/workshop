# HALMET piezo pod

Symphony: [`firmware/halmet`](https://github.com/mark-brannan/symphony/tree/main/firmware/halmet), [`reference/halmet_firmware.md`](https://github.com/mark-brannan/symphony/tree/main/reference/halmet_firmware.md), [`diagrams/electrical/chart-table-cabinet.drawio`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/chart-table-cabinet.drawio)

Purpose: hold the HALMET's alarm buzzer and the XY-MOS trigger module that switches it, high on a
vertical engine-room bulkhead, out of the splash and the worst of the oil and dust. A plain box and a
snap-on lid; no seal. The flanged buzzer sits inside, stacked over the module; only its round body comes out through the lid, so its leads stay inside.

![box with lid, module and buzzer stand-ins](out/assembly.png)

![half section on the centreline: inserts in the columns, M3 screws, buzzer ears, module](out/cutaway.png)

`show = "cutaway"` in `model.scad` renders the section; `"exploded"` the exploded view.

![box](out/halmet-piezo-pod_scad_pv_views.png)

![lid](out/halmet-piezo-pod_lid_pv_views.png)

## Status

- [x] Schematic (`piezo-alarm.drawio`)
- [x] Box and lid: `model.scad`, `part-lid.scad`, tests, renders, 3MFs
- [x] XY-MOS board calipered and photographed
- [ ] Solder a 2-pin header to the module's J1 trigger pads, on the bench
- [ ] Print box and lid; fit, wire, screw up

## Known, and from what

Module calipered; buzzer measured by the owner, partly by eye.

| Parameter | Now | Source |
|---|---|---|
| XY-MOS module | 33.8 x 16.7 x 12; board ~1.1 thick | owner, caliper; height from seller listings |
| `pocket_gap`, `hole_gap` | 3, 0.1 | owner, caliper: board's terminal end to the pin block's near edge; board's far end to a screw hole's near edge |
| `hole_d` | 2.6 | owner, caliper; sets where the screw-hole centre sits |
| Buzzer, on hand | body 29.0 dia, ~15 high; ear flange 4.5 thick at the back; ears 47.4 tip to tip, holes ~40 apart; leads leave the side at the back | owner, caliper; height and hole pitch by eye |
| `body_hole_d`, `ear_hole_d` | 29.8, 3.6 | clearance; printed holes come out small |
| `m2_pilot` | 1.7 | M2 self-tapping into the plinth; calibration pending |
| `insert_hole_d` | 4.0 | M3 x 4 heat-set insert, maker's hole; inserts not bought |
| `mount_d` | 4.5 | #8 or M4 pan head |

## Design

- Box 40 x 85 x 30.5 over the tabs, 19.4 cm3; lid 40 x 60 x 6.4 with its skirts, 4.5 cm3. PETG.
- The module sits in a rimmed seat on a 3 mm plinth, its terminal pins down in a blind pocket, held by two M2
  self-tapping screws at the far end.
- The buzzer's round body goes up through a 29.8 mm hole in the lid. Its leads leave its side inside the box;
  the box is 36 wide inside so they have room toward a long wall. If the ear holes are not 40 apart, `ear_pitch` moves them.
- The lid snaps on: a skirt down each long wall carries a 45° ridge that clicks into a groove in the wall.
- Two rounded tabs at the ends screw to the bulkhead (#8 or M4).
- Two cables (HALMET signal, boat 12 V) enter through a 9 mm mousehole with a round roof at the foot of
  the end wall at the module's terminal end. Tie them to the bulkhead below the box for strain relief.
- Walls 2.0, floor 2.4, lid 2.4. Outside edges square, box and lid flush at the seam; only the lid's top edge rounded;
  2 mm fillet floor to wall inside, inside corners rounded, lead-in at the rim.
- Buzzer as low as the module allows: its back 1 mm over the module's top, its top 0.5 mm proud of the lid
  (`proud`; 0 is flush). Turned 39° in plan so its ears land on two columns standing on the floor beside
  the module. Two M3 screws hold the ears into M3 x 4 heat-set inserts in the column tops, inside the box,
  under the lid (inserts not bought; `insert_hole_d` follows the maker's hole).
- Print box floor down and lid outer face down. Nothing overhangs.

## Wiring

![piezo alarm](out/piezo-alarm.png)

Source: [`piezo-alarm.drawio`](piezo-alarm.drawio). GPIO 32 HIGH triggers the XY-MOS dual-MOSFET trigger module (on hand), which switches the buzzer low-side off boat 12 V, as symphony's firmware has it.
Only GPIO 32 leaves the HALMET, one conductor through a 1-pin pluggable at the gland; nothing is added inside the HALMET box.
The pod's 12 V comes from a boat 12 V tap near the pod, fused at the tap. The trigger's ground is the module's VIN−, so the trigger current returns through the boat: HALMET GND → power/N2K pin 1 (NET-C) → the N2K backbone power tap, where NET-C is tied to the 12 V bus negative → boat negative bus → the pod tap's negative → VIN−.
The HALMET's J201 GND and power/N2K pin 1 are one net, `GND`, in `HALMET.kicad_pcb`.
The module's input is J1, unpopulated pads at the end opposite the screw terminals (owner photo); a 2-pin header gets soldered there on the bench. R1 to R3 and an LED are on the board, values unread, and J1's pin order is unread. The FETs are D4184: AOS AOD4184A, V<sub>GS(th)</sub> 1.7 / 2.1 / 2.6 V min / typ / max (aosmd.com datasheet).
D1, a 1N4148 across the buzzer, cathode to OUT+, sits in the OUT screw terminals with the buzzer leads, no solder. It is harmless on a piezo-type buzzer and needed only if the buzzer turns out to be magnetic.
Intended buzzer, not yet bought: 12 V active buzzer, 12 mm class.
HALMET pin numbers are from `HALMET.kicad_pcb` (hatlabs/HALMET-hardware) pad nets, read 2026-11-23.

| From | To | Net |
|---|---|---|
| HALMET GPIO 2x10, 8 | X1, 1-pin at the gland | GPIO 32 |
| X1 | cable A, 1 conductor, to engine room | GPIO 32 |
| Cable A | module J1 signal pin | GPIO 32 |
| HALMET power/N2K 4-pin, 2, 1 | N2K drop to the backbone power tap | NET-S, NET-C (GND) |
| Boat 12 V tap +, fused at the tap | module VIN+ | 12 V |
| Boat 12 V tap − | module VIN−; J1 GND joins it on the board | boat negative, trigger ground |
| Module OUT+ | buzzer +, D1 cathode | 12 V |
| Module OUT− | buzzer −, D1 anode | switched negative |

### Margin

3.3 V drive, minus the drop across the module's input divider, minus the ground offset between HALMET GND and VIN−, must clear the FET threshold at buzzer current.

- Bench, before install: drive J1 from a bench supply at 2.5 V, standing in for 0.8 V of offset, with the buzzer on 12 V. Full tone passes.
- Boat, once wired: meter HALMET GND to the pod's VIN− with the engine cranking and running. The 0.8 V budget comes from the bench check.

If the bench check fails, the fallback is an NPN stage in the pod (for example a 2N3904, 0.6 V base turn-on). It still uses one wire and adds nothing to the HALMET box.
