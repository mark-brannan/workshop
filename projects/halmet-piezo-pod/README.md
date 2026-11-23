# HALMET piezo pod

Symphony: [`firmware/halmet`](https://github.com/mark-brannan/symphony/tree/main/firmware/halmet), [`reference/halmet_firmware.md`](https://github.com/mark-brannan/symphony/tree/main/reference/halmet_firmware.md), [`diagrams/electrical/chart-table-cabinet.drawio`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/chart-table-cabinet.drawio)

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
