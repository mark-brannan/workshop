# HALMET piezo pod

Symphony: [`firmware/halmet`](https://github.com/mark-brannan/symphony/tree/main/firmware/halmet), [`reference/halmet_firmware.md`](https://github.com/mark-brannan/symphony/tree/main/reference/halmet_firmware.md), [`diagrams/electrical/chart-table-cabinet.drawio`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/chart-table-cabinet.drawio)

Purpose: hold the HALMET's alarm buzzer, stacked on its FET carrier, high on a vertical
engine-room bulkhead, open to the air. Out of the splash and the worst of the oil and dust, so no
seal; the shape keeps drips and dust off the parts that mind them.

![pod with carrier stand-in](out/assembly.png)

![views](out/halmet-piezo-pod_scad_pv_views.png)

## Status

- [x] Schematic (`piezo-alarm.drawio`)
- [x] `model.scad`, tests, render, 3MF
- [ ] Buy the buzzer and AO3400A; build the carrier
- [ ] Print in ASA; fit the carrier, tie the cable, screw it up

## Known, and from what

Nothing measured: the carrier and buzzer are not bought. The pod gives room instead.

| Parameter | Now | Source |
|---|---|---|
| `carrier_w` x `carrier_h` | 25 x 30 | room: the widest carrier the grooves take |
| `comp_h` | 11 | guess: a 5 mm screw terminal, the tallest part |
| `buzzer_d`, `buzzer_h` | 12, 9.5 | 12 mm active buzzer class, typical |
| `fit` | 0.3 a side | guess, uncalibrated |
| `screw_d` | 4.5 | #8 or M4 pan head |

## Design

- An open hood, 53 x 20 x 56, 10.7 cm3. Back plate against the bulkhead, two side walls, a 45-degree
  gable roof. Open front: the buzzer's port faces out, horizontal, so dust can't settle in it.
  Open bottom: drips drain, and the cable comes in from below so water doesn't run along it to the board.
- The carrier slides up from below in a groove in each side wall until its top edge meets the groove's
  end. Buzzer and terminal face out; the terminal sits at the carrier's bottom edge, screws reached from the front.
- One zip tie through the two low wall slots goes round the cable and under the carrier: it is both the strain
  relief and the keeper. Snip it and the carrier slides out.
- Two screws through ears either side, into the bulkhead.
- ASA, not PETG: high in an engine room may run 60-70 C (guess); PETG softens near 80 C.

## Print

As modelled: open bottom on the bed, roof up. Every overhang holds itself: the roof is 45 degrees inside and
out, each groove ends in a 45-degree slope, the screw holes are teardrops, the tie slots have pointed tops.
The footprint is narrow for its 56 mm height: use a brim.

## Wiring

![piezo alarm](out/piezo-alarm.png)

Source: [`piezo-alarm.drawio`](piezo-alarm.drawio). GPIO 32 HIGH turns on a low-side N-FET that sinks the buzzer's negative lead off V+, as symphony's firmware has it.
The gate resistor, the 100 k gate-to-source pull-down, the FET, the 1N4148 and the buzzer all sit in the pod in the engine room; with the pull-down there, a cut cable leaves the buzzer off.
The diode, cathode to V+, is harmless on a piezo-type buzzer and needed only if the buzzer turns out to be magnetic.
Intended parts, not yet bought: AO3400A FET (SOT-23, logic-level at 2.5 V), a 12 V active buzzer of the 12 mm class.
V+ reaches the inside of the HALMET box only at the power/N2K terminal, pin 2, ahead of the HALMET's own fuse (F301); no header or other terminal pin carries it, so X1's V+ lead shares that terminal with the supply wire.
HALMET pin numbers are from `HALMET.kicad_pcb` (hatlabs/HALMET-hardware) pad nets, read 2026-11-23.

| From | To | Net |
|---|---|---|
| HALMET power/N2K 4-pin, 2 (shared with the supply wire) | X1 pin 1 | V+ |
| HALMET GPIO 2x10, 8 | X1 pin 2 | GPIO 32 |
| HALMET GPIO 2x10, 12 | X1 pin 3 | GND |
| X1 pins 1, 2, 3 | field cable, 3 conductors, to engine room, length unknown | V+, GPIO 32, GND |
| Field cable | pod P1 pins 1, 2, 3 | V+, GPIO 32, GND |
| P1 pin 1 | buzzer +, D1 cathode | V+ |
| P1 pin 2 | R1 100 Ω, then Q1 gate; R2 100 k gate to source | GATE |
| P1 pin 3 | Q1 source, R2 | GND |
| Q1 drain | buzzer −, D1 anode | BZ_NEG |
