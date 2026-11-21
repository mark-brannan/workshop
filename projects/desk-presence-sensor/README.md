# Desk presence sensor

Symphony: none yet

Purpose: a sitting timer for the desk. An LD2410C radar senses you in the chair, a D1 mini
(ESP8266) counts, the TM1637 shows the timer and the OLED shows troubleshooting and other stats.
The box is 45 wide to match the monitor arm stem. Its flat back tapes to the arm with double-sided
tape, facing the chair, so nothing goes through the back: the **front plate** carries every board and
the **back tray** clips over it. The D1 mini stands behind the displays, USB up, so the box is short
and deep. The only openings are the two display windows and the USB plug in the top. Not sealed.

Outside: 45 x 94 x 50 mm (was 45 x 117 x 33 with the D1 mini beside the displays).

## Requirements

Owner's, 2026-11-20. Numbered so a change can cite one.

| # | Requirement | Why |
|---|---|---|
| R1 | The segmented display (TM1637) is the lowest of the displays | easiest to see at the desk |
| R2 | The OLED sits just above the segmented display | next easiest to see |
| R3 | The radar sensor sits low, clear of the monitor | the monitor bezel blocks its view |
| R4 | The bottom-most position is the segmented display or the radar (R1 and R3 compete for it) | |
| R5 | The cable comes up and out the back | |
| R6 | The back is flat and taped to the monitor with double-sided tape: no screws or openings that the tape must cover | |
| R7 | 45 mm wide, to match the monitor arm stem | |
| R8 | PETG, no supports | print economy |

Status: the order is radar (bottom), TM1637, OLED, with the D1 mini behind the OLED, USB up through the
top wall (R1 to R5 met; the cable bends back over the top edge). Not yet checked against the real monitor.

## Prints, PETG, no supports

| Part | File | Orientation | Overhangs |
|---|---|---|---|
| Fit gauge, **print first** | `part-gauge.scad` | flat | none: 1 mm slice of the plate plus 2 mm of posts and ribs |
| Front plate | `model.scad` | front face down | everything rises from the face; no overhangs |
| Back tray | `part-tray.scad` | tape face down | stop ribs and snap barbs have 45° undersides; USB hole has a 45° gabled roof toward the rim |

## How it goes together

```
 side section, front at the left
 plate    boards            Dupont housings        D1 mini + its jumpers   tape face
 |=====|  radar/OLED/TM  |  up to z ~ 19  |      D1 at z = 24, USB up  |  (flat, taped)
 0    1.3                                         ^ four pillars carry its corners
```

The plate pushes into the tray's open front, past four snap leaves (a wall strip freed by two slits,
a 45° barb on its end), until its back face meets four stop ribs. The barbs hold it. To open,
pry a leaf out at the rim. The plate sits 1.3 mm behind the rim.

## Layout (front view, top to bottom)

```
 +----[usb]----+   USB plug through a gabled hole in the top wall
 |  D1 mini    |   behind the OLED at z = 24; four corner pillars (lower pair on 45 deg corbels), L-ribs
 | +---------+ |
 | |  OLED   | |   window 24 x 13; four M2 x 4-5 self-tappers into posts (under the D1: unplug it)
 | +---------+ |
 | [ 88:88 ]   |   TM1637 window, the lowest display; four M2.5 x 6 self-tappers into corner posts
 |  (radar)    |   bottom: no hole, looks through the 1.5 mm plate; rib pocket, dab of hot glue
 +-------------+
```

## Assembly

1. TM1637: clip the bent header pins off flush with the black plastic and solder four jumper
   wires to the joints on the board's back (the bent pins can't fit at 45 wide). Display into its
   window, four M2.5 x 6 self-tappers from behind.
2. OLED: glass to the window, four M2 self-tappers from behind.
3. Radar: antenna side to the plate in its rib pocket, a dab of hot glue at two corners.
4. D1 mini: drop it onto its four pillars, component side toward the plate, USB end up. It covers
   the radar and the top of the OLED, so the displays go on first; to reach a screw later, unplug it.
5. Jumpers per the table, then push the plate into the tray until the barbs click. Tape the back
   to the arm.

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
drives the TM1637. No firmware for this box yet.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| TM1637 board, holes, display | see [`parts.md`](../../parts.md) | owner, caliper |
| Pin directions: D1 mini male out the back, OLED out the back, radar out the back | | owner, by eye |

## Guessed (the gauge checks the face ones)

| Value | Now | Why |
|---|---|---|
| D1 mini, LD2410C outlines | 34.2 x 25.6, 22 x 16 | vendor drawings, not calipered; 0.5 slack per side |
| OLED holes, glass | 23.3 x 23.6; glass 26.7 x 19.3, 2.4 thick, centred | generic drawing |
| OLED active-area offset `ol_win_dy` | 1.5 toward the header | typical module; the gauge shows it |
| ESP can height and place | 3.2, centre 13 below the USB end | typical D1 mini; foam tape takes up ±0.5 |
| USB overmold | 12 x 8 | overmolds vary |
| Jumper stack `jumper_h` | 16.5 behind the D1 board | header 2.5 + Dupont housing 14 |
| Pilots `tm_pilot_d`, `ol_pilot_d`, `insert_d` | 2.2, 1.6, 4.2 | calibration pending |

## Open

- Perma-proto or a PCB later would cut the depth to ~20: `jumper_h` and `bend` set it.
- Firmware: sitting timer on the TM1637, stats on the OLED.
