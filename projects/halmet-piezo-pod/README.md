# HALMET piezo pod

Symphony: [`firmware/halmet`](https://github.com/mark-brannan/symphony/tree/main/firmware/halmet), [`reference/halmet_firmware.md`](https://github.com/mark-brannan/symphony/tree/main/reference/halmet_firmware.md), [`diagrams/electrical/chart-table-cabinet.drawio`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/chart-table-cabinet.drawio)

Purpose: hold the HALMET's alarm buzzer and the XY-MOS trigger module that switches it, high on a
vertical engine-room bulkhead, out of the splash and the worst of the oil and dust. A plain box and a
screwed lid; no seal. The flanged buzzer sits under the lid, stacked over the module; only its round body comes out through the lid, so its leads stay inside.

![box with lid, module and buzzer stand-ins](out/assembly.png)

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
| XY-MOS module | 33.8 x 16.7 x 12 | owner, caliper; height from seller listings |
| Buzzer, on hand | body 29.0 dia, ~15 high; ear flange 4.5 thick at the back; ears 47.4 tip to tip, holes ~40 apart; leads leave the side at the back | owner, caliper; height and hole pitch by eye |
| `body_hole_d`, `ear_hole_d` | 29.8, 3.6 | clearance; printed holes come out small |
| `pilot_d`, `lid_hole_d` | 2.2, 3.2 | M2.5 self-tapping; printed holes come out small |
| `mount_d` | 4.5 | #8 or M4 pan head |

## Design

- Box 40 x 60 x 22.9, 15.4 cm3; lid 40 x 60 x 2.4, 3.9 cm3. PETG.
- The module lies on the floor on foam tape, 3 mm under the buzzer's back.
- The buzzer's round body goes up through a 29.8 mm hole in the lid; its ear flange bears on the lid's
  underside, ears along the box's length. Two M3 bolts go down through the lid and the ears, nuts under the
  ears. Its leads leave its side inside the box; the box is 36 wide inside so they have room toward a long wall.
  If the ear holes are not 40 apart, `ear_pitch` moves them.
- Four M2.5 self-tapping screws into corner bosses hold the lid.
- Two screws through the floor, from inside, hold the box to the bulkhead, clear of the module's ends.
- Two cables (HALMET signal, boat 12 V) enter through a 12 x 7 notch in the bottom wall, run out to the
  rim; the lid closes it. Tie them to the bulkhead below the box for strain relief.
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
