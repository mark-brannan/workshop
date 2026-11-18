# D1 mini sensor node: LD2410C presence radar plus air quality and an OLED

Purpose: one ESP8266 (Wemos D1 mini) node that senses presence and air, shows it on a small OLED,
and can take an optional MOX gas experiment (MQ-2, MQ-135) for the boat builds. Nothing here is built
or measured yet: parts are ordered or on the bench, no enclosure exists, no firmware is chosen.
Parts are a menu; the baseline below is the default, everything else is optional.

## Baseline and options

| Part | Role | Bus / pins | Address | Power | Status |
|---|---|---|---|---|---|
| Wemos D1 mini (ESP8266) | controller | | | USB 5 V | on hand |
| HLK LD2410C | mmWave presence | UART0 swapped: radar TX to D7 (GPIO13), radar RX from D8 (GPIO15); optional OUT to D5 (GPIO14) | | 5 V, ~80 mA (datasheet, unmeasured) | on hand |
| Sensirion SCD41 | CO2, T, RH | I2C, D1 SCL (GPIO5), D2 SDA (GPIO4) | 0x62 | 3.3 V | ordered |
| Adafruit BME688 (5046) | VOC / T / RH / pressure, MOX reference | I2C | 0x77 | 3.3 V | ordered |
| SSD1306 / SH1106 OLED | display | I2C | 0x3C | 3.3 V | spares on hand |
| VEML7700 | lux (baseline) | I2C | 0x10 | 3.3 V | ordered |
| BH1750 | lux (spare, same job) | I2C | 0x23 | 3.3 V | ordered |
| ADS1115 | optional: analog front end for MQ sensors | I2C | 0x48 | 3.3 V | to buy if the MOX experiment runs |
| MQ-2 (1), MQ-135 (2) | optional: MOX experiment, A0 to A2 on the ADS1115 | via divider to the ADS1115 | | 5 V heater, ~150 mA each (recollection, measure it) | on hand |

All I2C addresses are distinct. The logger moves off UART0 (GPIO2 / D4, or off) because the radar
runs at 256000 baud, too fast for ESP8266 software serial.

## Notes that shape the box

- SCD41 and BME688 read warm near the ESP8266, the radar and any MQ heater: separate them and vent.
- Feed the BME688 pressure to the SCD41 for CO2 compensation.
- Three MQ heaters add ~450 mA at 5 V: give the box a supply of 1 A or more and feed heaters and radar from it, not through the D1 mini.
- MQ outputs reach 5 V: a divider to the ADS1115 (3.3 V supply) on each channel.
- The LD2410C looks through plastic; keep metal out of its field of view.

## To measure on arrival

Board outlines and hole patterns (LD2410C, SCD41, VEML7700, BH1750, ADS1115, OLED, D1 mini) go into
[`parts.md`](../../parts.md) the day they are measured. MQ heater resistance (H to H) with a meter:
about 30 ohm expected, 5 V / R is the real current.

## Open

- Firmware: [`esphome/node.yaml`](esphome/node.yaml) passes `esphome config`; not compiled, not flashed. Copy `secrets.example.yaml` to `secrets.yaml` first. The MQ / ADS1115 add-on is not in it yet.
- Enclosure and layout: not started; waits on the measurements above.
