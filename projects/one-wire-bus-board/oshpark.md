# Ordering the one-wire bus board from OSH Park

What this is for: a handful of small boards that tie six 1-wire sensor cables and one master cable
(HALMET or an ESP32) into GND, DATA and VCC, inside an IP-rated enclosure on the boat. Read 2026-11-16.

## What to upload

| File | What it is |
|---|---|
| [out/fab/one-wire-bus-gerbers.zip](out/fab/one-wire-bus-gerbers.zip) | the upload: 7 Gerbers and 1 drill file |
| [out/fab/gerbers/](out/fab/gerbers/) | the same files, unzipped, for a Gerber viewer |
| [out/fab/top.png](out/fab/top.png), [bottom.png](out/fab/bottom.png) | KiCad's pictures, to compare with OSH Park's previews |
| [out/assembled-front.png](out/assembled-front.png), [-back.png](out/assembled-back.png) | the board with stand-in terminals and M3 screws |
| [out/one-wire-bus.kicad_pcb](out/one-wire-bus.kicad_pcb) | the board; OSH Park also takes this file directly |
| [out/one-wire-bus.kicad_dru](out/one-wire-bus.kicad_dru) | OSH Park's limits as KiCad rules; the check runs against these |

`uv run python projects/one-wire-bus-board/model.py` rebuilds all of it and stops on a rule violation.

## The order

https://oshpark.com/

| Their page | Enter or check |
|---|---|
| Upload | the zip; reported size 2.80 x 0.43 in (71.0 x 10.8 mm) |
| Previews | top: 7 x G D V, 1-6, MASTER, 4k7; bottom: one DATA trace, the name line; drills: 25 holes on the pads |
| Service | 2 Layer Prototype (purple, 1.6 mm, 1 oz copper, ENIG) |
| Quantity | 3 |
| Shipping | USPS First Class, $0 |

The pages after upload were not seen; field names there may differ.

## Price

$5 per square inch of one board buys three boards; lots of three only. Area is the outline's bounding
rectangle, so anything stray on the outline layer raises the price. Arithmetic from that rate, not a site quote.

| Field terminals (plus MASTER) | Board, mm | Total for 3 | Per board |
|---|---|---|---|
| 4 | 56 x 10.8 | $4.69 | $1.56 |
| 5 | 66 x 10.8 | $5.52 | $1.84 |
| 6 (as built) | 71 x 10.8 | $5.94 | $1.98 |
| 8 | 86 x 10.8 | $7.20 | $2.40 |
| 10 | 101 x 10.8 | $8.45 | $2.82 |
| 12 | 121 x 10.8 | $10.13 | $3.38 |
| 16 | 151 x 10.8 | $12.64 | $4.21 |

About $0.64 per extra terminal on the lot. `terminals` in `model.py` sets the count.

| Other 2-layer services | Price | Ships in |
|---|---|---|
| Prototype | $5 / sq in for 3 | 9-12 days |
| Super Swift | $10 / sq in for 3 | 5 business days |
| After Dark (black, clear mask) | $5 / sq in for 3 | 12-21 days |
| Medium Run | $1 / sq in, 100 sq in minimum | 12-21 days |

## Their limits against this board

| Rule | OSH Park | This board |
|---|---|---|
| Trace width / spacing | 0.15 / 0.15 mm | 0.5 and 1.0 / 0.3 or more |
| Drill | 0.25 mm minimum | 0.8, 1.3, 3.2 |
| Annular ring | 0.13 mm | 0.3 and 0.4 |
| Copper to board edge | 0.38 mm | 0.5 or more |
| Mask expansion | 0.05 mm | 0.05 |
| Silkscreen line | 0.13 mm | 0.12 lines, 0.15 text |
| Hole size tolerance | +/-0.06 mm | terminal holes 1.3 for ~0.9 pins |
| Edge tolerance | +/-0.13 mm, plus panel-tab stubs to file | nothing fits against the edge |

OSH Park does not promise a rule check or a call about problems: the board is made as the previews show.

## Sources

docs.oshpark.com: `services/`, `services/two-layer/`, `design-tools/kicad/`, `design-tools/kicad/generating-kicad-gerbers/`,
`design-tools/kicad/kicad-design-rules/`, `submitting-orders/board-outline/`, `submitting-orders/drill-specs/`,
`submitting-orders/shipping-information/`.

Not confirmed there: sales tax, silkscreen colour, the size and place of the tab stubs.
