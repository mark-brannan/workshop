# Desk presence sensor

Symphony: none yet

Purpose: a sitting timer for the desk. An LD2410C radar senses you in the chair, a D1 mini
(ESP8266) counts, the TM1637 shows the timer and the OLED shows troubleshooting and other stats.
The box is 45 wide to match the monitor arm stem. Its flat back tapes to the arm, facing the chair.
The D1 mini lies across the box behind the displays, so the box is short and deep.
The sides are smooth. The only openings are the two display windows and the USB plug in the +X side wall.
Not sealed against water or dust.

Outside: 45 x 85 x 49 mm (shell 46.5 deep + 2.5 cover); was 45 x 117 x 33 with the D1 mini beside the displays.

## Prints, PETG, no supports

| Part | File | Orientation | Overhangs |
|---|---|---|---|
| Fit gauge, **print first** | `part-gauge.scad` | flat | none: 1 mm slice of the face plus 2 mm of posts and ribs |
| Shell | `model.scad` | face down | front edge 45° chamfer; USB hole in the +X wall has a 45° gabled roof; everything else rises from the face |
| Cover | `part-cover.scad` | tape face down | countersinks open toward the bed at 45° |

## Layout (front view, top to bottom)

```
 front view                          side section (+X wall right)
 +-------------+                     face  boards   Dupont      D1 mini
 | D1 mini  |  |  behind everything  |=====|radar,OLED|housings |==[usb]== USB out the +X wall
 |  (behind)|  |  (dashed outline)   z 0   2-5       to ~19     24
 |  (radar)    |  no hole: looks through the 1.5 mm face
 |  +-------+  |
 |  | OLED  |  |  window 24 x 13; four M2 x 4-5 self-tappers into posts
 |  +-------+  |
 | [ 88:88 ]   |  TM1637 window; four M2.5 x 6 self-tappers into corner posts
 +-------------+
```
The D1 mini lies across the box at z = 24 from the face, resting on four pillars at its ends with
L-ribs to locate it, over the radar and the top of the OLED. Its Dupont jumpers go straight back.
To reach a display screw, unplug the D1 mini and lift it out.

## Assembly

1. TM1637: clip the bent header pins off flush with the black plastic and solder four jumper
   wires to the joints on the board's back (the bent pins can't fit at 45 wide). Display into its
   window, four M2.5 x 6 self-tappers from behind.
2. OLED: glass to the window, four M2 self-tappers from behind.
3. Radar: antenna side to the face in its rib pocket, a dab of hot glue at two corners.
4. D1 mini: drop it onto its four pillars, component side toward the face, USB end toward +X.
5. Jumpers per the table, USB in through the +X wall, cover on: four M3 countersunk into heat-set
   inserts in the side posts. Tape the cover to the arm.

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
