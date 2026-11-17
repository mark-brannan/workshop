# Finished detectors and monitors

What can be bought ready-made, on and off boats, and what each one detects.

`verified [n]` means the row was read on that source on 2026-11-17. `snippet`
means it was seen only in a search result, because the shop's page refused the
fetch. The rest are **Unverified**. Prices are US dollars. "Listing" is what
the page said, not a claim that the product has no other.

## For boats

| Product | Detects | Output | Listing | Price | Status |
|---|---|---|---|---|---|
| Fireboy-Xintex G-1B-R | Gasoline vapour, at 20 % LEL | Local alarm, LED display | not stated | $301.53 | verified [1] |
| Fireboy-Xintex MB-1-R | Gasoline vapour | Local alarm | not seen | $162.88 | snippet |
| Fireboy-Xintex P-1B-R | Propane | Local alarm | not seen | $330–490 | snippet |
| Fireboy-Xintex systems with solenoid or blower control | Propane or gasoline | Alarm and relay | not checked | $450–800 | Unverified |
| Fireboy-Xintex CMD6-MB | CO | 85 dB horn, two LEDs | not stated | $142–222 | verified [2] |
| Safe-T-Alert 62-541 and 62-542 Marine | CO | Local alarm; relay variants | UL 2034 Marine | $62–100 | snippet |
| Trident 1300-7760 LP gas control | Propane or CNG, at 10 % LEL | 95 dB alarm; closes a solenoid | UL Listed | $383.28 | verified [4] |
| BEP 600-GDL | LPG and petrol vapour | Alarm, solenoid control | not seen | $276–364 | snippet |
| Digital Yacht CO Alert | CO | Alarm; NMEA 2000 Alert messages | "UL approved sensor" | $294–390 | features verified [3] |
| Maretron CO-CO1224T with SIM100 | CO | Relay; NMEA 2000 through the SIM100 | not seen | not found | snippet |
| Maretron LP-200012UL with SIM100 | LPG | NMEA 2000 through the SIM100 | not confirmed | not found | snippet |

Two ways onto NMEA 2000 turned up, both for CO first. The Digital Yacht unit
speaks it directly and reports a sensor fault as well as CO. Maretron's wired
detectors go through a switch indicator module, which carries on or off, not a
level. One search found no ready-made Signal K gas device.

## For houses and RVs

| Product | Detects | Output | Listing | Price | Status |
|---|---|---|---|---|---|
| Safe-T-Alert 30-442-P | Propane | Local alarm | UL 1484 (RV) | $52–100 | snippet |
| Safe-T-Alert 35-742 | CO and propane | Local alarm | UL 2034, UL 1484 | $74.99 | snippet |
| Kidde or First Alert CO alarm | CO | Local alarm | UL 2034 | $20–50 | Unverified |
| Kidde or First Alert explosive gas and CO alarm | Methane or propane, and CO | Local alarm | UL 1484, UL 2034 | $45–65 | Unverified |

## Air-quality monitors

| Product | Detects | Output | Price | Status |
|---|---|---|---|---|
| Aranet4 Home | CO₂ ±(30 ppm + 3 %), temperature, humidity, pressure | E-ink display, Bluetooth app | $189.00 | verified [5] |
| Airthings View Plus | Radon, PM2.5, CO₂, VOC, temperature, humidity, pressure | Display, Wi-Fi and Bluetooth app | about $299 | features verified [6] |

The Aranet4 uses an NDIR sensor and runs up to four years on its batteries.

## Portable and industrial

| Product | Detects | Output | Price | Status |
|---|---|---|---|---|
| Honeywell BW Clip4 | H₂S, CO, oxygen, combustibles to 100 % LEL | Sound, light, vibration | $755–1,129 | snippet |
| Eagle Eye HGD-2000 | Hydrogen: warning at 1 %, alarm at 2 % | Two relays, 80 dB alarm | $1,134–1,980 | snippet |
| Storage Battery Systems SBS-H2 | Hydrogen: relays at 0.5 % and 1 % | Two relays | not found | snippet |
| Honeywell Li-ion Tamer | Electrolyte vapour at a cell's first vent; also CO and H₂ | CAN bus, relays, Modbus | not published | verified [7] |
| ANSUL lithium-ion off-gas detection | Battery off-gas, against a reference sensor outside the rack | Controller | not published | Unverified |

The BW Clip4 is a sealed unit with a two-year life. Honeywell does not publish
how the Li-ion Tamer senses, only that it responds to VOCs [7].

## Sources

1. https://www.aztekcomputers.com/g-1b-r-xintex-gasoline-fume-detector-alarm-plastic-fireboy-xintex/p
2. https://www.wholesalemarine.com/fireboy-xintex-battery-operated-carbon-monoxide-detector
3. https://panbo.com/digital-yacht-co-alert-carbon-monoxide-alarm-with-nmea-2000-integration/
4. https://www.fisheriessupply.com/trident-marine-marine-lp-gas-control-and-detection-system/1300-7760
5. https://aranet.com/en/home/products/aranet4-home
6. https://www.airthings.com/view-plus
7. https://buildings.honeywell.com/us/en/brands/our-brands/li-ion-tamer
