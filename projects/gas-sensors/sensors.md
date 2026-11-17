# Sensor parts

The parts chosen for the build, what each one measures and needs, and a wider
list of parts sold on a breakout board.

Figures marked with a source number were read on that datasheet or listing on
2026-11-17. The rest are **Unverified**. Prices are US dollars for one unit.

## The parts in the build (Settled)

| Sensor | Measures | Needs | Price |
|---|---|---|---:|
| BME688 | Broadband VOC, temperature, humidity, pressure | I²C | $19.95 [2] |
| CaliPile TPiS 1S 1385 | Average surface temperature in a 120° cone; presence | I²C | $12 |
| MP-7 | CO, 50–1,000 ppm | Analog in; heater switched between 5 V and 1.5 V | $4–7 |
| MP-4 | Methane and natural gas, 300–10,000 ppm | Analog in; switched 5 V heater | $3–6 |
| MQ-2 | LPG, flammable gas, smoke, 300–10,000 ppm | Analog in; switched 5 V heater | $1–3 |
| DS18B20 probe, two | Contact temperature | 1-Wire | $9.95 each [7] |
| MEMS microphone, ePTFE vent | Sound | I²S | $2 |
| PIR | Motion | Digital in | $1.50 |
| Photodiode | Ambient light | Analog in | $0.30 |
| Near-infrared phototransistor | Flame flicker | Analog in | $0.30 |

Roughly $70 of sensors for a fully fitted node, at these prices.

## BME688

One metal-oxide film on one tiny hotplate. It is not an array. It behaves like
several sensors because the heater steps through up to 10 temperatures
(typically 200–400 °C) in a scan, and one resistance is read at each step.

| Property | Value | Source |
|---|---|---|
| Scan time, 10 steps | 10.8 s | [1] |
| Current, standard gas scan | 3.9 mA | [1] |
| Current, low-power and ultra-low-power modes | 0.9 mA and 0.09 mA | [1] |
| Current, continuous | 12 mA | [1] |
| Unit-to-unit spread | ±15 %, on Bosch's library output after its calibration period | [1] |
| Running-in before the specifications apply | 5 days (Bosch); 48 h (Adafruit) | [1][2] |
| Independent dimensions in a scan | About 3–5, not 10 | Unverified |
| Recovery after a power cycle | Hours | Unverified |

What will bite:

- **Drift.** The baseline resistance wanders over hours with humidity and
  recent exposure, and over months as the film ages. This is the main one.
- **Humidity and temperature** often move the reading more than the gas does.
- **Unit spread.** A model fitted on one unit often fails on another.
- **Siloxanes** degrade the film for good. Bosch tests against typical indoor
  levels and claims tolerance of those, not immunity [1].
- **No quantities.** The output is a relative resistance change in an unknown
  mixture. The library's "CO₂-equivalent" is a VOC correlation, not CO₂ [1].
- **Speed.** Anything shorter than a scan, or faster than the film's own
  seconds-to-minutes response, is blurred.

It is good at one yes-or-no question in one fixed place: same box, same
airflow, same spot. It is poor at naming an unknown gas. Bosch does quote an
F1 score of 0.94 for picking out H₂S with the standard scan [1].

## Heated sensors: MQ-2, MP-4, MP-7

| Sensor | Tuned for | Heater | Drive | Source |
|---|---|---:|---|---|
| MQ-2 | LPG, flammable gas, smoke | up to 950 mW | On or off | [3] |
| MP-4 | Methane, natural gas | up to 350 mW | On or off | [4] |
| MP-7 | CO | 240 mW hot, about 110 mW averaged | Cycled | [5] |

- **MP-4 is tuned for methane, not propane.** The MQ-2 is the LPG sensor.
- **The MP-7 heater must cycle:** 60 s at 5 V to clean, when the reading is
  invalid, then 90 s at 1.5 V to measure [5]. Read only at the end of the low
  phase; the last 15 s is a first guess (Unverified). The PWM duty that gives
  an effective 1.5 V is a guess until measured on the board.
- **The MP-7 starts at 50 ppm** [5]. It will not show a low background.
- **Running-in.** Winsen asks for at least 48 h of heating on all three before
  a reading means anything [3][4][5]. Count heater-hours per element and
  report `conditioning` until then.
- **Power.** The MQ-2 is the largest load by far. Switching it off when it is
  not needed saves the most.
- All three need temperature and humidity from the BME688 to interpret.

The 110 mW average for the MP-7 is arithmetic from the heater's 105 Ω, not a
datasheet figure.

## Thermopile: CaliPile TPiS 1S 1385

One pixel with a 120° view [6]. It reads the average surface temperature of
everything in its cone, up to 120 °C. No aiming. It draws 15 µA.

- A small hot spot is diluted in the average. Expect a trend, not a location.
- Its filter passes 7.5–13.5 µm [6], and glass and acrylic block that band. A
  window has to be HDPE, silicon or germanium (Unverified). The PIR needs the
  same, so one window serves both.

## Flame flicker: near-infrared phototransistor

Sees the light a flame gives off, about 760–1,100 nm, and its flicker. It does
not see heat. With the thermopile: flicker says a flame exists; the thermopile
says something is getting hot. The ambient-light photodiode cannot stand in;
it is the wrong band.

## Microphone

Sealed behind an ePTFE acoustic vent, which passes sound and keeps out water
and salt spray.

## Power, sensors only

| Load | Draw |
|---|---:|
| MQ-2 heater | up to 950 mW at 5 V |
| MP-4 heater | up to 350 mW at 5 V |
| MP-7 heater, cycled | about 110 mW at 5 V |
| BME688, standard gas scan | about 13 mW at 3.3 V |
| BME688, low-power mode | about 3 mW at 3.3 V |

The BME688 figures are its datasheet currents [1] times 3.3 V.

## Looked at and not used

| Part | Why not |
|---|---|
| AMG8833 8×8 thermal array | About $45 on a breakout; the CaliPile does the job for $12 |
| MLX90640 32×24 thermal array | $74.95 on a breakout [8] |
| ST STHS34PF80 presence sensor | $14.95 on a breakout [9]; never tried against the CaliPile |
| Time-of-flight ranger for bilge level | Still water is a mirror, so returns are unreliable; needs aiming |
| Bilge leak pads | Exposed metal; a corrosion path into the board |
| Reed switch | Parked. Sealed, but needs a magnet on a moving part. |
| Electrochemical cells, pellistors, PID | They wear out; see the rules in the [README](README.md) |
| NDIR CO₂ or hydrocarbon modules | Fit the rules and were discussed early; not in the build so far |
| BME690 | Bosch's successor to the BME688. Not evaluated. |

## Other parts sold on a breakout

`verified` means the specifications and price in the row were read on the
numbered source. `verified (specs)` means the maker's page gives no price, so
the price is a guess.

| Part | Maker | Senses | Principle | Interface | Supply / power | Expected life | Approx price | Status |
|---|---|---|---|---|---|---|---|---|
| BME688 | Bosch | Broadband VOC, temperature, humidity, pressure | MEMS MOX, scanned heater | I²C / SPI | 1.71–3.6 V; 0.09–12 mA by mode | not stated | $19.95 Adafruit breakout | verified [1][2] |
| BME690 | Bosch | As BME688; successor part | MEMS MOX | I²C / SPI | similar | not stated | about $20 breakout | unverified |
| SGP40 | Sensirion | VOC index (0–500) | MEMS MOX | I²C | 3.3 V on chip; breakout 3–5 V | not stated on listing | $14.95 Adafruit breakout | verified [10] |
| SGP41 | Sensirion | VOC index and NOx index | MEMS MOX, two films | I²C | 3.3 V, about 3 mA | 10 years claimed | $8–25 | unverified |
| ENS160 | ScioSense | TVOC, eCO2, AQI; reducing and oxidising gases | MEMS MOX, multi-element | I²C (SPI on chip) | breakout 3–5 V | not stated on listing | $21.95 Adafruit breakout | verified [11] |
| ENS161 | ScioSense | As ENS160, lower-power modes | MEMS MOX | I²C / SPI | 1.8 V core | not stated | about $20 breakout | unverified |
| MiCS-5524 | SGX / Amphenol | CO 1–1000 ppm, NH3 1–500, ethanol 10–500, H2 1–1000, methane / propane / iso-butane 1000+ ppm; cannot say which | MEMS MOX, reducing film | Analog | 5 V; heater 25–35 mA | not stated | $14.95 Adafruit breakout | verified [12] |
| MiCS-4514 | SGX / Amphenol | Reducing (CO, VOC) and oxidising (NO2) channels | MEMS MOX, two films | Analog; I²C on some breakouts | 5 V, about 90 mW | not stated | $20–40 breakout | unverified |
| MiCS-6814 | SGX / Amphenol | Reducing, oxidising and NH3 channels | MEMS MOX, three films | Analog; I²C on some breakouts | 5 V, about 150 mW | not stated | $15–45 breakout | unverified |
| Grove Multichannel Gas Sensor v2 | Seeed (Winsen GM-102B / 302B / 502B / 702B elements) | NO2, ethanol, VOC, CO; qualitative only per the maker | Four MEMS MOX elements | I²C (0x08) | 3.3–5 V | not stated | $26.99 Seeed (list $29.99) | verified [13] |
| MQ-2 | Winsen, Hanwei and others | Flammable gas and smoke, 300–10 000 ppm | Heated MOS | Analog | 5 V; ≤ 950 mW (Winsen) | not stated; over 48 h preheat | $1–3 | verified (specs) [3] |
| MP-4 | Winsen | Methane, natural gas, 300–10 000 ppm | Heated MOS, flat element | Analog | 5 V; ≤ 350 mW | not stated; over 48 h preheat | $3–6 | verified (specs) [4] |
| MP-7 | Winsen | CO, 50–1000 ppm | Heated MOS, cycled heater | Analog plus switched heater (5 V 60 s / 1.5 V 90 s) | ≤ 240 mW in the high phase | not stated; 48 h or more preheat | $4–7 | verified (specs) [5] |
| MQ-8 | Winsen, Hanwei | Hydrogen, 100–10 000 ppm | Heated MOS | Analog | 5 V, under 900 mW | not stated | $2–5 | unverified |
| TGS2611 | Figaro | Methane, 500–10 000 ppm | Heated MOS | Analog | 5 V, about 280 mW | 10 years class | $15–25 | unverified |
| TGS6812 | Figaro | Hydrogen, methane, LPG to 100 % LEL | Catalytic bead | Bridge, analog | 3 V, about 525 mW | 5 years class | $50–70 | unverified |
| TGS5141 | Figaro | CO, 0–5000 ppm | Electrochemical, dry (no water reservoir) | nA current; needs an amplifier | none for the cell | 10 years claimed | $15–25 | unverified (maker page 404 at the URL tried) |
| 110-1xx / DGS series | SPEC Sensors | CO, H2S, NO2, O3, SO2, ethanol (one per cell) | Screen-printed electrochemical | Bare cell, or UART module | µW; module about 1 mW | 5 years typical, 10 claimed | $20 cell, about $75 module | unverified |
| A- and B-series cells | Alphasense | CO, H2S, NO2, SO2, O3, O2 and others | Electrochemical | nA current; needs their front-end board | none for the cell | 2–3 years | $60–150 | unverified |
| Gravity SEN0466 | DFRobot | CO, 0–1000 ppm, factory calibrated | Electrochemical | I²C, UART, analog | 3.3–5.5 V | more than 2 years in air | $66.90 DFRobot | verified [14] |
| Gravity calibrated line (H2S, O2, NH3, H2, NO2, SO2, O3 and others) | DFRobot | One gas per probe, same board as SEN0466 | Electrochemical | I²C, UART, analog | 3.3–5.5 V | about 2 years | $60–150 | unverified |
| ZE07-CO | Winsen | CO, 0–500 ppm | Electrochemical, module | UART, analog | 5 V | 2–3 years | $15–25 | unverified |
| SCD41 | Sensirion | CO2 400–5000 ppm, ±(40 ppm + 5 %); temperature, humidity | Photoacoustic NDIR | I²C (0x62) | 3.3–5 V breakout; 17 mA at a 5 s rate | 10 years claimed | $49.95 Adafruit breakout | verified [15] |
| SCD40 | Sensirion | CO2 400–2000 ppm; temperature, humidity | Photoacoustic NDIR | I²C | as SCD41, no single-shot low-power mode | 10 years claimed | about $45 breakout | unverified |
| SCD30 | Sensirion | CO2 400–10 000 ppm; temperature, humidity | Dual-channel NDIR | I²C, Modbus | 3.3–5.5 V, about 19 mA average | 15 years claimed | about $59 breakout | unverified |
| MH-Z19C | Winsen | CO2, 400–2000 / 5000 / 10 000 ppm variants | NDIR | UART, PWM | 5.0 V ± 0.1 V; under 40 mA average | more than 10 years | $15–30 | verified (specs) [16] |
| CM1106 / CM1107 | Cubic | CO2, 0–5000 ppm | NDIR (CM1107 dual-beam) | UART, I²C, PWM | 5 V, about 50 mA average | 10–15 years | $15–30 | unverified |
| STC31 | Sensirion | CO2 in air or nitrogen, 0–25 or 0–100 % by volume | Thermal conductivity | I²C | 3.3 V, under 1 mA | not stated | $25–40 breakout | unverified |
| Hydrocarbon / methane NDIR (Winsen MH-440D, Dynament, SGX INIR class) | various | Methane or propane, 0–100 % LEL or % by volume | NDIR, 3.3 µm | UART, analog | 3.3–5 V, 0.2–0.5 W | 5–10 years | $40–200 | unverified |
| SFA30 | Sensirion | Formaldehyde, 0–1000 ppb | Electrochemical, module | I²C, UART | 3.3–5 V, under 2 mA | 6 years claimed | $35–60 | unverified |
| SEN55 | Sensirion | PM1 / 2.5 / 4 / 10, VOC index, NOx index, temperature, humidity | Optical particle counter plus SGP41-class MOX | I²C | 5 V, about 70 mA | 10 years claimed | $30–45 | unverified |
| SEN66 | Sensirion | As SEN55, plus CO2 | Adds photoacoustic CO2 | I²C | 3.3 V | 10 years claimed | $50–65 | unverified |
| SPS30 | Sensirion | PM1 / 2.5 / 4 / 10 | Optical particle counter | I²C, UART | 5 V; 55 mA average, 80 mA max | 8–10 years (the listing gives both) | $60.50 SparkFun | verified [17] |
| PMSA003I | Plantower | PM1 / 2.5 / 10; particles from 0.3 µm | Optical particle counter | I²C (0x12) | 5 V; 100 mA max, 200 µA standby | MTTF 3 years or more | $44.95 Adafruit breakout | verified [18] |
| PMS5003 | Plantower | PM1 / 2.5 / 10 | Optical particle counter | UART | 5 V, about 100 mA | about 3 years | about $40 | unverified |
| CaliPile TPiS 1S 1385 | Excelitas | Object temperature to 120 °C, presence, motion, over-temperature; 120° view | Thermopile, single pixel | I²C | 2.6–3.6 V; 15 µA max | not stated | $12 | verified (specs) [6] |
| STHS34PF80 | ST | Presence and motion to about 4 m, 80° view; ambient temperature ±0.3 °C | Thermal MOS IR, no lens | I²C | breakout 3–5 V | not stated | $14.95 Adafruit breakout | verified [9] |
| MLX90640 (55°) | Melexis | 32×24 thermal image, −40 to 300 °C, ±2 °C over 0–100 °C | Thermopile array | I²C | 3.3–5 V breakout; under 23 mA | not stated | $74.95 Adafruit breakout (out of stock) | verified [8] |
| AMG8833 | Panasonic | 8×8 thermal image, 0–80 °C | Thermopile array | I²C | 3.3 V, about 4.5 mA | not stated | about $45 breakout; $26 bare | unverified |
| DS18B20, waterproof probe | Analog Devices (Maxim) | Contact temperature, −55 to 125 °C, ±0.5 °C from −10 to 85 °C | Silicon bandgap | 1-Wire | 3.0–5.5 V | not stated | $9.95 Adafruit (out of stock) | verified (listing) [7] |

Not looked up: a hydrogen part beyond the MQ-8 and DFRobot's probe (thermal
conductivity hydrogen modules exist), and current prices for the rows marked
unverified.

## Sources

Read on 2026-11-17.

1. https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme688-ds000.pdf
2. https://www.adafruit.com/product/5046
3. https://www.winsen-sensor.com/sensors/combustible-sensor/mq2.html
4. https://www.winsen-sensor.com/sensors/combustible-sensor/mp-4.html
5. https://www.winsen-sensor.com/sensors/co-sensor/mp-7.html
6. https://cdn.sparkfun.com/assets/8/b/7/7/7/TPiS_1S_1385_Datasheet.pdf
7. https://www.adafruit.com/product/381
8. https://www.adafruit.com/product/4407
9. https://www.adafruit.com/product/6426
10. https://www.adafruit.com/product/4829
11. https://www.adafruit.com/product/5606
12. https://www.adafruit.com/product/3199
13. https://www.seeedstudio.com/Grove-Multichannel-Gas-Sensor-v2-p-4569.html
14. https://www.dfrobot.com/product-2508.html
15. https://www.adafruit.com/product/5190
16. https://www.winsen-sensor.com/sensors/co2-sensor/mh-z19c.html
17. https://www.sparkfun.com/products/15103
18. https://www.adafruit.com/product/4632
