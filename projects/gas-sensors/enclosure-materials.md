# Enclosure materials: silicone, seals, vents, plastics

What was read on 2026-11-17 about what may sit near a MOX sensor and what keeps
water out. Each line is from the numbered source, opened and read unless marked
`snippet`. Nothing here was tested on the bench.

## Silicone and MOX sensors

| Claim | Source |
|---|---|
| Siloxane vapour breaks down on the hot sensing layer and leaves "non-volatile reaction products like polymers or silica" | [1] |
| The silica blocks the sites where oxygen adsorbs; response to acetone and CO falls "nearly to zero", response to hydrogen "remains fairly stable" | [1] |
| VOC sensitivity falls and response time rises strongly | [2] |
| Cured silicone rubber holds residual volatile siloxanes, "generally in the range 0.05–3 per cent by weight" | [3] |
| They leave with time and heat: D4 below detection after a week's storage; two hours at 200 °C cuts it significantly | [3] |
| Food-grade silicone is not siloxane-free: nipples 0.5 to 269 µg/g, bakeware up to 7030 µg/g | [4] |
| The food-contact limit is 0.5 % volatiles after 4 h at 200 °C, usually met by post-curing | [5] |
| Relay makers list silicone rubber, not only sealant, as a source of contact-fouling silicone gas | [6] |
| Bosch, BME680: avoid "adhesive, PCB and housing materials that are emitting siloxanes and/or volatile organic compounds"; avoid "outgassing rubbers"; use "thermoplastic elastomers or highly filled rubbers" | [7] |
| Figaro names "silicone or silicone rubber/putty" | [8] |
| Sensirion, SGP4x: recommends "a silicone or rubber sealing" between housing and board, and elsewhere forbids silicone conformal coatings and lists Viton seals "after thermal outgassing" | [9] [10] |

Doses that degrade a sensor: detectable from 85 to 340 ppm·min of HMDSO [11, via a summary];
the standard test is 400 ppm·min [1]; 40 ppb of D5 for ten years is the lifetime case in [2].

**Not found:** the emission rate of a cured silicone O-ring or gasket at room
temperature, or any test of a MOX sensor beside one. Whether one O-ring delivers
a damaging dose cannot be settled from published data.

## Lid seals that are not silicone

Enclosure makers use foamed polyurethane, EPDM, neoprene and TPE [12]. Butyl
passes about 20 times less water vapour than EPDM and about 950 times less than
silicone [13]; nothing was found on its outgassing or on butyl beside a MOX sensor.

## Vents

| Vent | Rating | Airflow at 70 mbar | Seal | Source |
|---|---|---|---|---|
| Gore PolyVent XS, M6 x 0.75 | IP65/66/67/68 | 300 ml/min | silicone, 60 Shore A | [14] |
| Gore PolyVent Standard, M12 | IP65–68, 69K | 450 ml/min | silicone, 60 Shore A | [14] |
| Amphenol LTW VENT-PS1, M12 | IPX8 | over 1000 ml/min | silicone (snippet) | [15] |
| Bopla DAE, M12 | IP68 | 400 ml/min | not stated | [16] |
| Stego DA 284, M12 | IP66/68/X9K | 120 l/h | NBR | [17] |

## Printed cases and water

No printed (FDM) case with a documented pass of the IP tests was found. In one
maker's uncontrolled dive tests, untreated PETG leaked at the seams,
acetone-smoothed ASA leaked slowly, epoxy-coated PETG sealed, and printed
flexible gaskets all failed [18]. The owner's own PETG fitting leaked at low
pressure.

## Styrene from ABS

Printed ABS keeps giving off styrene after the print; no decay curve [19].
Moulded ABS holds residual styrene, one figure 2000 µg/g (snippet) [20]. Its
emission at room temperature was not found. Sensirion recommends ABS and PC
housings, and lists PA, POM and PMMA as not recommended [9].

## Sources

1. https://jsss.copernicus.org/articles/9/283/2020/jsss-9-283-2020.pdf
2. https://pmc.ncbi.nlm.nih.gov/articles/PMC5948493
3. https://assets.publishing.service.gov.uk/media/5a7c4a3ded915d3d0e87b611/scho0309bpqz-e-e.pdf
4. https://pubmed.ncbi.nlm.nih.gov/22575024/
5. https://www.bfr.bund.de/cm/349/XV-Silicones.pdf
6. https://ap.industry.panasonic.com/en/products/control/relay/cautions_use
7. https://www.bosch-sensortec.com/media/boschsensortec/downloads/handling_soldering_mounting_instructions/bst-bme680-hs000.pdf
8. https://www.figarosensor.com/attention/mos-type.html
9. https://cdn.sparkfun.com/assets/6/c/d/d/7/GAS_SGP4x_Design-In_Guide_D1.pdf
10. https://sensirion.com/en/media/documents/C16AA7D5/6440F28E/GAS_AN_SGPxx_HandlingAndAssemblyInstructions_D1.pdf
11. https://jsss.copernicus.org/articles/4/305/2015/
12. https://www.rhopointcomponents.com/download/fibox-gasket-materials
13. https://www.osti.gov/servlets/purl/6884480
14. https://kr.gore.com/system/files/2025-04/gore-ptv-screwin-datasheet-en.pdf
15. https://www.farnell.com/datasheets/2328173.pdf
16. https://www.bopla.de/fileadmin/product_data/_Product_Information/52042000_DAE-M12-Technical-Information-EN.pdf
17. https://www.stego-group.com/en-us/products/da-284-p
18. https://blog.prusa3d.com/watertight-3d-printing-part-2_53638/
19. https://stacks.cdc.gov/view/cdc/55079
20. https://pmc.ncbi.nlm.nih.gov/articles/PMC4048609
