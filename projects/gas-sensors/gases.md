# Gases aboard, and what can sense them

What might be in the air on a boat, where it comes from, and which kinds of
sensor respond to it at all.

Everything here is general knowledge and **Unverified**, except the few
footnotes that cite a source. Use it to choose what to look up, not to set an
alarm point.

## The gases

Density is relative to air. Heavier gases pool low (bilge, under the sole,
locker bottoms). Lighter ones collect high (deckhead, top of a battery box).
Near 1 they mix, and the sensor goes where the people or the source are.

| Gas | Comes from | Density | Sensor goes |
|---|---|---:|---|
| Carbon monoxide (CO) | Engine, generator and heater exhaust, own or a neighbour's; stoves | 0.97 | Head height in cabins and berths |
| LPG (propane, butane) | Stove, heater, locker, hose and regulator leaks | 1.5, 2.0 | Low: below the appliance, bilge |
| Gasoline vapour | Petrol engine space, outboard fuel, dinghy tank, jerry cans | 3–4 | Low in the engine space and bilge |
| Diesel vapour | Fuel leaks, tank vents, injector spray, heater | heavier | Low in the engine space |
| Methane | CNG stoves; sewage and holding-tank gas | 0.55 | High |
| Hydrogen | Lead-acid charging, most on overcharge; lithium cell venting | 0.07 | Highest point of the battery space |
| Carbon dioxide (CO₂) | People in a closed cabin, combustion, CO₂ fire systems | 1.5 | Breathing height |
| VOCs, broadly | Fuel, solvents, paint, resin, cleaners, cooking, mould | mostly heavier | Near the source |
| Lithium electrolyte vapours | A lithium cell venting, typically minutes before thermal runaway | about 3 | In the battery box, plus a reference outside |
| Hydrogen sulphide (H₂S) | Holding tanks, stagnant seawater in hoses, badly overcharged lead-acid | 1.19 | Low, near heads and tank |
| Ammonia (NH₃) | Absorption fridges, holding systems, cleaners | 0.59 | High, near the fridge |
| NO₂ and NOx | Diesel exhaust, gas stoves | 1.58 | Breathing height |
| Sulphur dioxide (SO₂) | Exhaust from high-sulphur fuel | 2.2 | Breathing height |
| Low oxygen | Sealed lockers and tanks (rusting steel, chain), CO₂ flooding | n/a | Where a person would enter |
| Refrigerants | Fridge, freezer, air-conditioning leaks | 2–3.5 | Low, near the compressor |
| Smoke, soot, particles | Electrical faults, cooking, exhaust, heaters | rises hot | High for fire; anywhere for air quality |
| Ozone | Ozone "odour" generators, some purifiers, arcing | 1.66 | Breathing height |

## Levels that matter

| Gas | Levels of interest |
|---|---|
| CO | 35 ppm is a common 8 h limit; alarms act at about 70 ppm over hours, 400 ppm over minutes |
| LPG | Explosive from about 2 % (the lower explosive limit, LEL); alarms usually at 10–25 % of LEL |
| Gasoline vapour | LEL about 1.4 %; marine fume detectors alarm near 20 % of LEL |
| Diesel vapour | Barely evaporates below about 52 °C: a smell and a VOC trace, not an explosive mix |
| Methane | LEL about 5 % |
| Hydrogen | LEL 4 %; battery-room practice alarms at 1 % and 2 % |
| CO₂ | 420 ppm outdoors, 1,000 stuffy, 5,000 the 8 h limit, 40,000 immediately dangerous |
| VOCs | No single limit; a trend signal |
| Lithium electrolyte vapours | Any at all; runaway itself adds H₂, CO, CO₂, hydrocarbons, HF and smoke |
| H₂S | Smelt at ppb; limits 1–10 ppm; 100 ppm immediately dangerous, and by then odourless |
| NH₃ | 25 ppm 8 h limit; 300 ppm immediately dangerous |
| NO₂ | About 0.1–5 ppm |
| SO₂ | About 2–5 ppm |
| Oxygen | 20.9 % normal; under 19.5 % counts as deficient |
| Refrigerants | Leak finding; R290 and R600a in small fridges are flammable (they are propane and isobutane) |
| Ozone | About 0.1 ppm |

## Which kind of sensor responds

| Word | Meaning |
|---|---|
| `good` | The normal choice; works at the levels of interest |
| `possible` | Responds, with caveats |
| `problematic` | Responds poorly, unselectively, or only with expensive hardware |
| `no` | No useful response |

| Column | Sensor kind | Example parts |
|---|---|---|
| hMOS | Heated metal-oxide | MQ-2, MP-4, MP-7, Figaro TGS |
| mMOX | MEMS metal-oxide | BME688, SGP41, ENS160 |
| EC | Electrochemical cell | Alphasense, SPEC, DFRobot Gravity |
| NDIR | Infrared absorption | MH-Z19, SCD30 |
| PA | Photoacoustic infrared | SCD41 |
| Pell | Catalytic bead (pellistor) | TGS6812 |
| PID | Photoionisation, 10.6 eV lamp | handheld VOC meters |
| TC | Thermal conductivity | STC31 |
| OPC | Optical particle counter | SPS30, PMSA003I |

| Gas | hMOS | mMOX | EC | NDIR | PA | Pell | PID | TC | OPC |
|---|---|---|---|---|---|---|---|---|---|
| CO | possible [1] | possible [2] | good | problematic [3] | problematic [3] | no [4] | no [5] | no | no |
| LPG | good [6] | possible [7] | no | good | possible [8] | good | problematic [9] | possible [10] | no |
| Gasoline vapour | good [6] | good | no | good [11] | possible [8] | good [12] | good | problematic [10] | no |
| Diesel vapour | possible [13] | possible [13] | no | problematic [13] | problematic | problematic [12] | good | no | problematic [14] |
| Methane | good [6] | problematic [7] | no | good | possible [8] | good | no [5] | possible [10] | no |
| Hydrogen | good [15] | possible [15] | good [16] | no [17] | no [17] | good | no [5] | good [18] | no |
| CO2 | no [19] | no [19] | problematic [20] | good | good | no | no | possible [21] | no |
| VOCs, broadly | possible | good [22] | problematic [23] | problematic | problematic | problematic [4] | good | no | no |
| Li electrolyte vapours | possible | good [24] | problematic [25] | problematic [26] | problematic [26] | problematic [4] | possible [27] | no | possible [28] |
| H2S | possible | possible [29] | good | no | no | no [30] | possible | no | no |
| NH3 | possible | possible | good | problematic | problematic | no | possible | no | no |
| NO2 / NOx | problematic [31] | possible [31] | good [32] | problematic | no | no | problematic | no | no |
| SO2 | problematic | problematic | good | problematic | problematic | no | no [5] | no | no |
| O2 depletion | no | no | good [33] | no | no | no [34] | no | no | no |
| Refrigerants | good [35] | possible | no | good | possible [8] | problematic [36] | no [5] | possible [10] | no |
| Smoke / particulates | possible [37] | possible [37] | possible [38] | no | no | no | problematic | no | good [39] |
| Ozone | good [40] | possible [31] | good [32] | no [41] | no | no | no | no | no |

1. CO-tuned heated MOS (MQ-7, MP-7) needs a high/low heater cycle and still responds to hydrogen and alcohol; humidity moves the baseline.
2. Responds as a "reducing gas" with no way to tell CO from ethanol or hydrogen.
3. CO absorbs at 4.6 µm, but ppm-level CO needs a long optical path; no commodity module at hobby prices.
4. Pellistors read in % LEL; ppm-level toxic or VOC concentrations are far below their floor.
5. Ionisation energy above a 10.6 eV lamp (CO 14.0, methane 12.6, hydrogen 15.4, SO2 12.3, most HFC refrigerants).
6. Works well as a tripwire. Not quantitative: drifts, and reads humidity and temperature.
7. Light alkanes need a hotter film than the low-power MEMS parts usually run; response starts around 1000 ppm (the MiCS-5524 listing gives "1,000+ ppm" for methane, propane and iso-butane).
8. Photoacoustic hydrocarbon and refrigerant sensors exist, but few are sold on hobby breakouts; the commodity photoacoustic part is CO2-only.
9. Propane (10.95 eV) is above a 10.6 eV lamp; butane (10.53 eV) responds weakly.
10. Thermal conductivity works at percent levels in a known two-gas mix; it cannot tell which gas changed the reading. Heavy vapours differ little from air.
11. Hydrocarbon NDIR is calibrated on methane or propane; gasoline needs a correction factor.
12. Heavy hydrocarbons diffuse slowly into the bead and under-read; leaded fuel, sulphur and silicones poison it.
13. Diesel's vapour pressure is very low at cabin temperature, so there is little to sense until it is hot or sprayed.
14. Sees diesel mist or smoke as particles, not the vapour.
15. Very sensitive to hydrogen, and to everything else reducing. A hydrogen reading from a MOX part is "hydrogen or alcohol or solvent".
16. Hydrogen cells cross-respond to CO, and CO cells to hydrogen, unless filtered.
17. Hydrogen has no infrared absorption.
18. Hydrogen conducts heat about seven times better than air, so thermal conductivity is selective enough in a battery box. Resolution is typically around 0.1 % or coarser, adequate against a 4 % LEL.
19. "eCO2" from a MOX part is a VOC correlation, not a CO2 measurement.
20. Electrochemical CO2 cells exist but are short-lived and uncommon.
21. Percent-level CO2 only (Sensirion STC31 class); not for cabin ppm.
22. The use these parts are designed for; output is a relative index, not ppm.
23. Cells exist for specific compounds (formaldehyde, ethanol), not for VOCs as a class.
24. Commercial lithium off-gas detectors are described by their maker as responding to electrolyte solvent VOCs; the maker's page does not name the sensing principle. See [products.md](products.md).
25. No cell for carbonates; CO and H2 cells catch the later runaway gases.
26. Carbonates absorb in the infrared, but there is no commodity module tuned for them.
27. DMC's ionisation energy is near the 10.6 eV lamp limit, so response is weak; an 11.7 eV lamp is short-lived.
28. Sees the vent aerosol and smoke once a cell opens.
29. Bosch quotes an F1 score of 0.94 for H2S scanning with the BME688's standard gas-scan mode (datasheet; source 1 in [sensors.md](sensors.md)).
30. H2S is also a pellistor poison.
31. Oxidising gases need a different film or heater setpoint (MiCS-2714 / 4514 / 6814 oxidising channel, SGP41 NOx index, ENS161). The common tin-oxide MQ parts are not built for it.
32. NO2 and ozone cells cross-respond to each other.
33. Galvanic lead cells last about 2–3 years; lead-free cells about 5. Optical (fluorescence quenching) and zirconia sensors are the non-consumable alternatives, outside this matrix.
34. A pellistor needs oxygen to work and under-reads in depleted air, but it does not measure oxygen.
35. Refrigerant-tuned heated MOS (Figaro TGS832 / TGS2630 class) is what handheld leak detectors used for decades.
36. Halogenated refrigerants inhibit or poison the bead. Fine for R290 / R600a, which are just LPG.
37. Responds to combustion gases, not particles; MQ-2 is sold as a "smoke" sensor on that basis.
38. CO from a smouldering fire.
39. Cannot distinguish smoke from fog, spray or cooking aerosol; salt and humidity inflate counts.
40. Ozone-tuned heated MOS (tungsten-oxide film, MQ-131 class).
41. The reference method for ozone is UV absorption, not infrared.

## What each kind costs to live with

| Kind | Life | Wears out? | Power | Module price |
|---|---|---|---|---|
| Heated MOS | 5–10 years claimed | No, but drifts | 240–950 mW heater | $2–25 |
| MEMS MOX | 5–10 years claimed | No, but drifts | 0.3–50 mW by duty | $10–30 |
| Electrochemical | 2–3 years; some CO cells 5–10 | Yes; replace on a calendar | microwatts | $20–150 |
| NDIR | 10–15 years | No | 100–400 mW lamp types | CO₂ $20–60; hydrocarbon $40–200 |
| Photoacoustic | 10 years claimed | No | 2–60 mW by rate | $45–55 for CO₂ |
| Catalytic bead | 3–5 years | In effect, yes | 200–500 mW | $20–100 |
| PID | Sensor 5 years; lamp 1–2 | Yes: the lamp | 50–150 mW | $300–600 |
| Thermal conductivity | 10 years or more | No | 1–50 mW | $25–60 |
| Particle counter | 3–10 years | Fan and optics | 0.3–0.5 W running | $40–60 |

| Kind | What hurts it |
|---|---|
| Heated MOS | Siloxanes (permanent), sulphur, heavy solvent exposure; humidity and temperature |
| MEMS MOX | Siloxanes; output is relative only; one unit reads differently from the next |
| Electrochemical | Dries out hot and dry, floods hot and wet; cross-gases; over-range |
| NDIR | Condensation and dust on the optics; auto-baseline assumes regular fresh air |
| Photoacoustic | Vibration and loud low-frequency noise; the same baseline assumption |
| Catalytic bead | Silicones, lead, sulphur, halogens; needs oxygen; over-range cracks the bead |
| PID | Humidity quenches the signal; the lamp window fouls |
| Thermal conductivity | Not selective; needs humidity and temperature compensation |
| Particle counter | Salt, fog and condensation read as particles; fan bearings in salt air |

The heater, current and price figures behind these ranges, where checked, are
in [sensors.md](sensors.md).
