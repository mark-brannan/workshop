# Parts

Bought parts we have measured or looked up, so the next project that uses one starts from numbers.
Each row says where its numbers came from. A caliper reading beats a vendor drawing, and a vendor
drawing beats a photo. The project link shows the part fitted.

## Boards and modules

| Part | Where from | Dimensions, mm | Source | Used in |
|---|---|---|---|---|
| Hat Labs HALMET | Hat Labs | 89 x 58; two 4.8 x 3.2 slots at 45°, centres (22.75, 51.5) and (67.25, 6.5) from the lower-left corner; R8.5 concave cut at three corners | `HALMET.kicad_pcb`, hatlabs/HALMET-hardware | [halmet-enclosure-mount](projects/halmet-enclosure-mount/) |
| SSD1306 0.96" OLED | generic | 27.3 x 27.8; holes 23.3 x 23.6, M2 (owner) | generic drawing, not calipered | halmet-enclosure-mount |
| TM1637 4-digit module | generic | board 41.5 x 23.5; holes 37.5 x 19, ~2.8 dia, 0.5 from the edge; display body 30 x 14, face 7 above the board; header 5 above the board's back, 6.8 past its edge | owner, caliper | [segment-display-enclosure](projects/segment-display-enclosure/) |
| LM393 photoresistor module | Amazon B0FS6866W3 | 32 x 14; one M3 hole between the trimpot and the header, centred across, ~7 from the header end; photocell at the far end; right-angle 3-pin header | vendor drawing; hole position from the photo | halmet-enclosure-mount |
| LM393 photoresistor module, on hand | | 31 x 14; one M3 hole, ~4 across, centred, its rim 5 from one end and both long edges; header pins 6 past the edge; photocell bent up, its top ~11.5 above the board top | owner, caliper | [halmet-enclosure-mount](projects/halmet-enclosure-mount/), [photocell-flame-pod](projects/photocell-flame-pod/) |
| ESP32 breakout board | | holes 80 x ~75.5, M2 | owner, caliper | [esp32-breakout-mount](projects/esp32-breakout-mount/) |
| AC-DC supply, 58 x 85 | Amazon B0DK3SPYNZ | 85 x 58; two base holes on a diagonal, ~75 x ~47, M3 screws | owner, caliper (approx) | [din-rail-psu-mount](projects/din-rail-psu-mount/) |
| Adafruit STEMMA QT boards: BME688 (5046), ICM-20948 (4554), LTC4311 (4756) | Adafruit | 25.4 x 17.78; four 2.5 holes at 20.32 x 12.7; JST-SH socket at each short edge; ~4.6 overall height | Adafruit board files (BME688 inferred from the BME680 file); product pages | [small-box-sensors](projects/small-box-sensors/), [bme688-halpi2](projects/gas-sensors/bme688-halpi2/) |
| Adafruit BME688 (5046), chip and sockets | Adafruit | chip at the board's exact centre (12.7, 8.89); both JST-SH sockets on the chip's face, on the centre line at each short edge; 10 k pull-ups; 0x77, or 0x76 with SDO to GND | Adafruit-BME680-PCB board file (shared with the BME688); Adafruit guide | [bme688-halpi2](projects/gas-sensors/bme688-halpi2/) |
| Adafruit LPS35HW (4258), STEMMA QT revision | Adafruit | 25.4 x 17.78; only two 2.5 holes, 20.32 apart, 2.54 in from one long edge (the header takes the other edge); sensor at the board's exact centre (12.7, 8.89); JST-SH socket at each short edge on the centre line; AP2112K-3.3 regulator, BSS138 level shifter, 10 k pull-ups, green LED; 0x5D, address jumper on the back; VIN 3-5 V; the breakout itself is not water resistant | `Adafruit LPS3X.brd`, adafruit/Adafruit-LPS3X-PCB; product page | [outside-sensor-pod](projects/outside-sensor-pod/) |
| Qwiic / STEMMA QT pigtail, 150 mm (4397 sockets, 4209 pins) | Adafruit | JST-SH 4-pin, 1.0 pitch; pin 1 GND black, 2 V+ red, 3 SDA blue, 4 SCL yellow | Adafruit STEMMA QT technical specs; product pages | [bme688-halpi2](projects/gas-sensors/bme688-halpi2/) |
| HALPI2, I2C and cable entry | Hat Labs | 40-pin header, 2.54 pitch: pin 1 3V3, 3 SDA, 5 SCL, 6 and 9 GND; bus `/dev/i2c-1`, own controller at 0x6d; no Qwiic socket; front panel has 3 blanked positions for PG7 glands (3 included) or SP13, "6mm or 13mm holes"; 45 above the board | docs.hatlabs.fi/halpi2 (hardware, interfaces, troubleshooting); hole sizes not on a drawing | [bme688-halpi2](projects/gas-sensors/bme688-halpi2/) |
| DSN-MINI-360 buck converter, on hand | | 17.5 x 16.5; the 16.5 side has unused board and can be trimmed to as little as 12; terminal pads ~8.8 apart across the width | owner, caliper (terminal spacing approx) | [outside-sensor-pod](projects/outside-sensor-pod/) (candidate) |
| SparkFun QwiicBus EndPoint, PCA9615 (16988) | SparkFun | 44.45 x 25.4; four 3.2 mm mounting holes on a 20.32 x 20.32 grid, 2.54 in from the sides, 2.54 and 22.86 from the far end; RJ45 jack; differential pairs on the jack's pads only | SparkFun board file | [imu-tray](projects/imu-tray/); too long for small-box-sensors |
| 1803BK PWM fan controller | generic | 32 x 32 (35 with the break-off edge); holes ~26 square; pot with M7 bushing, shaft height unmeasured | listing, not calipered | [heater-fan-mount](projects/heater-fan-mount/) |

The halmet-enclosure-mount model uses 41 x 23 with holes 37.5 x 19 for the TM1637 (owner, caliper; 36 from rough calipers was 1.5 narrow). The calipered numbers above come from segment-display-enclosure. Measure the one in hand.

## Enclosures

| Part | Where from | Dimensions, mm | Source | Used in |
|---|---|---|---|---|
| Waterproof box 158 x 90 x 60 | Hat Labs ECK-PW158-H | inside floor ~151 x 83; floor to rim 39; six holed bosses ~3.5 tall, span 143 x pitch 21.7 (owner's estimates, tuned by fit check; model.scad); four no-hole posts ~80 x 70; lid-screw column in each corner; lid 17 deep, rim to ceiling (owner, caliper, may read 0.5 over at the gasket); six 13 mm holes on one long wall | vendor page; owner; first print | [halmet-enclosure-mount](projects/halmet-enclosure-mount/enclosure/) |
| Waterproof box 63 x 58 x 35 | Amazon ABS, black or clear lid, brass inserts | outer 63 x 58 x 35 (older listing 64 x 57); 53 inside across the 58 side; 39 straight wall between corner columns, both walls; lid ~8.5, wall ~2.5, floor ~3; two floor bosses ~6 dia x ~4, ~5.5 in from each short wall (photo estimates) | vendor listings; photos | [one-wire-enclosure](projects/one-wire-enclosure/), [small-box-sensors](projects/small-box-sensors/) |
| Shower sump box, 750 GPH pump (unbranded) | | box 186 wide x 275 long (length "measure it!"); 334 overall; 112 tall; wings 215 tip to tip, tabs ~90 long (approx); per side two 9 slots 59 apart at 186 across, and one 5 hole at 200 across, 25 from a slot | owner, Fusion parameters (2026-02), some flagged unmeasured | [shower-sump-platform](projects/shower-sump-platform/) |

## Hardware

| Part | Dimensions, mm | Source | Used in |
|---|---|---|---|
| M3 F/F hex standoff, the owner's stock | 19.7 long, 5.5 across flats (assumed) | owner, caliper (length) | halmet-enclosure-mount |
| 2.54 mm screw terminal block, 3-pos (commodity, KF2.54-3P class) | pins on 2.54 mm, body 3 x 2.54 wide; typical depth 6.5, pins ~3.3 from the wire-entry face, drill ~1.3 | commodity; any in-stock 3P part | [one-wire-bus-board](projects/one-wire-bus-board/) |
| SP13 panel socket, rear nut (Weipu SP1312) | cut-out 13 with a flat at 12.1; thread M13 x 1; flange 19.5; overall 19.2; panel up to 3.5; nut size not found | Weipu drawing | small-box-sensors |
| Membrane vent M6 x 0.75 (Gore PolyVent XS) | hole 6.2; head 11.2; thread 7; overall 11.5; wrench 10; IP65/66/67/68; 300 ml/min at 70 mbar; ePTFE membrane; O-ring silicone 60 Shore A | Gore drawing; Gore screw-in vent datasheet | small-box-sensors |
| Membrane vent M12 (Stego DA 284) | IP66/IP68/IPX9K; 120 l/h; seal NBR, not silicone; dimensions not read | Stego product page | |
| PG7 nylon gland | thread 12.5 x 8 long; body hex 15; locknut 19 across flats x 5 (Essentra), which differs from the 15 in one-wire-enclosure | Altech table; Essentra listing | |
| DS18B20 waterproof probe, the owner's | cable 3.5 OD; probe with its heat shrink 6.3 at the widest; the cable takes an M8 gland (2-5 clamp), fed bare-end first since the probe won't pass the gland | owner, caliper (approx) | [one-wire-enclosure](projects/one-wire-enclosure/) |
| DIN rail TS35 | 34.5 measured, 35 nominal | owner, caliper | din-rail-psu-mount |
| DIN clip (preferred, low profile) | Printables 420009, `din_clip_heat_insert.stl`, printed apart, two M3 heat-insert holes 51 mm apart across the rail (model x = 5 and 56, rail centre 27.05), on the clip's centre line; the mount screws on with M3 countersunk | owner's choice of design |
| Fan GDA8025 IP68, 12 V | 80 x 80 x 25 (~24.5 owner); holes 71.5 square, M4; air bore 76 | vendor drawing; owner (thickness) | [heater-fan-mount](projects/heater-fan-mount/) |
| Diesel heater bottom rim | ~75.4 outside: a 76 bore was near a friction fit; unmeasured | owner | [heater-fan-mount](projects/heater-fan-mount/) |
| 3" flex duct, wire helix | 76.2 ID nominal; right-hand wire, pitch 15-19 (estimate) | owner | [heater-fan-mount](projects/heater-fan-mount/) |
