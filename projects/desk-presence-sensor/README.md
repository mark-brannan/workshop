# Desk presence sensor

Symphony: none yet

Purpose: a sitting timer for the desk. An LD2410C radar senses you in the chair, a D1 mini
(ESP8266) counts, the TM1637 shows the timer and the OLED shows troubleshooting and other stats.
The box is 45 wide to match the monitor arm stem. Its flat back tapes to the arm with double-sided
tape, facing the chair, so nothing goes through the back: the **shell** (face and walls in one print)
carries every board and the shallow **back plate** snaps gently into it. The D1 mini stands on edge
low in the box, USB up, in two slots, held by its own **retainer**. The only openings are the two
display windows and the cable slot in the top. Not sealed.

Outside: 45 x 81 x 52 mm (was 45 x 91 x 50 with the D1 mini behind the OLED).

## Requirements

Owner's, 2026-11-20. Numbered so a change can cite one.

| # | Requirement | Why |
|---|---|---|
| R1 | The segmented display (TM1637) is the lowest of the displays | easiest to see at the desk |
| R2 | The OLED sits just above the segmented display | next easiest to see |
| R3 | The radar sensor sits low, clear of the monitor | the monitor bezel blocks its view |
| R4 | The bottom-most position is the segmented display or the radar (R1 and R3 compete for it) | |
| R5 | The USB cable exits up and back through the top wall, never through the back | the back is taped flat |
| R6 | The back is flat and taped to the monitor with double-sided tape: no screws or openings that the tape must cover | |
| R7 | 45 mm wide, to match the monitor arm stem | |
| R8 | PETG, no supports | print economy |
| R9 | Stacking order, bottom to top: radar, TM1637, OLED. Held, 2026-11-21 | settles R4 |
| R10 | Back flat and shallow; it closes with a gentle snap. Held, 2026-11-21 | |
| R11 | The D1 mini may be bare: no male header pins assumed | one on hand is bare |

Status: the order is radar (bottom), TM1637, OLED; the D1 mini stands behind the radar and TM1637
wiring, USB up, and the cable leaves through the top wall near the back (R1 to R5 met). Not yet checked against the real monitor.

## Prints, PETG, no supports

| Part | File | Orientation | Overhangs |
|---|---|---|---|
| Fit gauge, **print first** | `part-gauge.scad` | flat | none: 1 mm slice of the plate plus 2 mm of posts and ribs |
| Shell | `model.scad` | front face down | D1 slots run straight up; the wall ledge starts on 45° slopes; cable slot open to the rim |
| Back plate | `part-back.scad` | tape face down | tab bumps are 45° both faces |
| D1 retainer | `part-retainer.scad` | on its flat side | none |

## How it goes together

```
 side section, front at the left (z from the outer face)
 face  radar + Dupont   D1 on edge, slots          retainer  back plate (taped)
 |==|  0 .. 19.5    |   z 20.5 .. 46.1, USB up  |  46.3..49.3 | 49.6 .. 52.1
```

The D1 mini stands on its long edge at right angles to the face, ESP can toward the +X wall, pins
toward the middle. It slides in from the open back: its lower edge in a floor slot that stops it,
its upper edge in a ledge slot on the wall (cut away around the USB plug). The retainer strip
presses into the same slots behind it. The back plate's four tabs click 0.5 mm bumps into V grooves
in the side walls; pry at a corner to open.

## Layout (front view, top to bottom)

```
 +------[cable]+   cable slot in the top wall, open to the back rim
 | +---------+ |
 | |  OLED   | |   window 24 x 13; four M2 x 4-5 self-tappers into posts
 | +---------+ |
 | [ 88:88 ]  :|   TM1637 window, the lowest display; four M2.5 x 6 self-tappers into corner posts
 |  (radar)   :|   no hole, looks through the 1.5 mm face; rib pocket, dab of hot glue
 +-------------+   ':' = D1 mini on edge behind, at the +X wall (left as seen from the desk)
```

## Assembly

1. TM1637: clip the bent header pins off flush with the black plastic and solder four jumper
   wires to the joints on the board's back (the bent pins can't fit at 45 wide). Display into its
   window, four M2.5 x 6 self-tappers from behind.
2. OLED: glass to the window, four M2 self-tappers from behind.
3. Radar: antenna side to the face in its rib pocket, a dab of hot glue at two corners.
4. D1 mini: jumpers on, then slide it into its slots from the back, USB end up, until it stops.
   Press the retainer into the slots behind it. Plug in the USB cable and lay it in the top slot.
5. Jumpers per the table, then press the back plate in until the tabs click. Tape the back to the arm.

## Wiring (Dupont, D1 mini side)

| From | D1 mini |
|---|---|
| Radar 5V, GND | 5V, G |
| Radar TX | D7 (GPIO13), UART0 swapped |
| Radar RX | D8 (GPIO15) |
| OLED VCC, GND, SCL, SDA | 3V3, G, D1 (GPIO5), D2 (GPIO4) |
| TM1637 VCC, GND, CLK, DIO | 3V3, G, D5 (GPIO14), D6 (GPIO12) |

The radar takes the hardware UART at 256000 baud, so the logger moves to D4 (GPIO2), as in
[d1-mini-sensor-node](../d1-mini-sensor-node/esphome/node.yaml). Radar OUT is not wired; D5 now
drives the TM1637. Firmware: [`esphome/desk.yaml`](esphome/desk.yaml).

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| TM1637 board, holes, display | see [`parts.md`](../../parts.md) | owner, caliper |
| Pin directions: D1 mini male out the back, OLED out the back, radar out the back | | owner, by eye |

## Guessed (the gauge checks the face ones)

| Value | Now | Why |
|---|---|---|
| D1 mini, LD2410C outlines | 34.2 x 25.6, 22 x 16 | vendor drawings, not calipered |
| Radar stack `rd_stack` | 19.5 from the face | board + header + Dupont housing |
| Slot clearance `slot_clr`, snap `bump` | 0.25 per side, 0.5 | calibration pending |
| OLED holes, glass | 23.3 x 23.6; glass 26.7 x 19.3, 2.4 thick, centred | generic drawing |
| OLED active-area offset `ol_win_dy` | 1.5 toward the header | typical module; the gauge shows it |
| ESP can height | 3.2 | typical D1 mini |
| USB plug | fits between the ledge segments (`usb_gap` 13) | overmolds vary |
| Jumper stack `jumper_h` | 16.5 beside the D1 board | header 2.5 + Dupont housing 14 |
| Pilots `tm_pilot_d`, `ol_pilot_d`, `insert_d` | 2.2, 1.6, 4.2 | calibration pending |

## Open

- Perma-proto or a PCB later would cut the depth: `rd_stack` and the D1 width set it.
- Firmware: sitting timer on the TM1637, stats on the OLED.
- Other D1 placements weighed 2026-11-21: flat on the floor (USB out a side wall), upright parallel
  to the face (its Dupont stack adds to the displays' depth, and it covers screws).
