# Parts

Bought parts we have measured or looked up, so the next project that uses one starts from numbers.
Each row says where its numbers came from. A caliper reading beats a vendor drawing, and a vendor
drawing beats a photo. The project link shows the part fitted.

## Boards and modules

| Part | Where from | Dimensions, mm | Source | Used in |
|---|---|---|---|---|
| Hat Labs HALMET | Hat Labs | 89 x 58; two 4.8 x 3.2 slots at 45°, centres (22.75, 51.5) and (67.25, 6.5) from the lower-left corner; R8.5 concave cut at three corners | `HALMET.kicad_pcb`, hatlabs/HALMET-hardware | [halmet-enclosure-mount](projects/halmet-enclosure-mount/) |
| SSD1306 0.96" OLED | generic | 27.3 x 27.8; holes 23.3 x 23.6, M2.5 or M2 | generic drawing, not calipered | halmet-enclosure-mount |
| TM1637 4-digit module | generic | board 41.5 x 23.5; holes 37.5 x 19, ~2.8 dia, 0.5 from the edge; display body 30 x 14, face 7 above the board; header 5 above the board's back, 6.8 past its edge | owner, caliper | [segment-display-enclosure](projects/segment-display-enclosure/) |
| LM393 photoresistor module | Amazon B0FS6866W3 | 32 x 14; one M3 hole between the trimpot and the header, centred across, ~7 from the header end; photocell at the far end; right-angle 3-pin header | vendor drawing; hole position from the photo | halmet-enclosure-mount |
| LM393 photoresistor module, on hand | | 31 x 14; one M3 hole, ~4 across, centred, its rim 5 from one end and both long edges; header pins 6 past the edge | owner, caliper | [halmet-enclosure-mount](projects/halmet-enclosure-mount/) |
| ESP32 breakout board | | holes 80 x ~75.5, M2 | owner, caliper | [esp32-breakout-mount](projects/esp32-breakout-mount/) |
| AC-DC supply, 58 x 85 | Amazon B0DK3SPYNZ | 85 x 58; two base holes on a diagonal, ~75 x ~47, M3 screws | owner, caliper (approx) | [din-rail-psu-mount](projects/din-rail-psu-mount/) |

The halmet-enclosure-mount model uses 41 x 23 with holes 36 x 19 for the TM1637, from the owner's
rough calipers. The calipered numbers above come from segment-display-enclosure. Measure the one in hand.

## Enclosures

| Part | Where from | Dimensions, mm | Source | Used in |
|---|---|---|---|---|
| Waterproof box 158 x 90 x 60 | Hat Labs ECK-PW158-H | inside floor ~151 x 83; floor to rim 39; six holed bosses ~3.5 tall at 140 x 22.5 pitch; four no-hole posts ~80 x 70; lid-screw column in each corner; lid 17 deep, rim to ceiling (owner, caliper, may read 0.5 over at the gasket); six 13 mm holes on one long wall | vendor page; owner; first print | [halmet-enclosure-mount](projects/halmet-enclosure-mount/enclosure/) |

## Hardware

| Part | Dimensions, mm | Source | Used in |
|---|---|---|---|
| M3 F/F hex standoff, the owner's stock | 19.7 long, 5.5 across flats (assumed) | owner, caliper (length) | halmet-enclosure-mount |
| 2.54 mm screw terminal, 3-pos (OST OSTVN 2.54) | 3-pos body 8.02 x 6.5 x 8.5 (L x deep x tall); pitch 2.54; pins 3.3 from the wire-entry face, 3.5 long, 0.9 x 0.4; drill 1.30 | vendor drawing, owner-supplied, not calipered | [one-wire-bus-board](projects/one-wire-bus-board/) |
| DIN rail TS35 | 34.5 measured, 35 nominal | owner, caliper | din-rail-psu-mount |
| DIN clip (preferred, low profile) | Printables 420009, `din_clip_heat_insert.stl`, printed apart, two M3 heat-insert holes 51 mm apart across the rail (model x = 5 and 56, rail centre 27.05), on the clip's centre line; the mount screws on with M3 countersunk | owner's choice of design |
