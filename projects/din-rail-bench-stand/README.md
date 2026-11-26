# DIN-rail bench stand

Symphony: none yet

Purpose: a desk "mini rack" for the bench: PSUs, buck/boost, a Pi or ESP32 on breakouts, a V/A meter, within reach.
Several stands sit side by side. Each stand is two of these end brackets and four TS35 rails cut to length:
two across the sloped face, one flat on the foot in front, and one flat at the back under the face for AC gear
(a small PSU, mains terminals, relays), out of reach from the front.

The construction is Szmalu's [DIN Rail Stand KIT](https://www.thingiverse.com/thing:3609072) (CC BY-NC), which holds one rail:
an A-frame end bracket, a thick plate of thin ladder bars, the rail passing through a slot of its own section.
Its top, above the crossbar, is the original's profile cut from its mesh and used as is (`szmalu_top.scad`, CC BY-NC, attribution above); below that, this one is scaled up to hold four rails.

Prototype, not printed. Nothing here is measured.

![profile beside the original](out/din-rail-bench-stand_vs_original.png)
![assembly](out/din-rail-bench-stand_assembly.png)

`view="assembly"` stands two brackets up with 300 mm rails and orange module envelopes (60 tall, 45 deep); the back rail's are red (55 deep).
Front of the desk is +X (right in the side view).

## Sizes

| Size | Value | Source |
|---|---|---|
| Rail | TS35, 35 × 7.5 | standard |
| Face slope | 60° above the desk | guess |
| Tier pitch, along the face | 70 | 60 module + 10 wiring room; guess |
| Module envelope | 60 tall, 45 deep from the rail base; 55 on the back rail | guesses: the small boards planned, not 90 standard DIN gear |
| Face angle and top | 60°, the top and its rail as the original's, unchanged | the original |
| Tier 1 | 106.5 along the face from its foot, high enough that the back (AC) rail's modules clear it by 10 | the model; the test holds 10 |
| Back (AC) rail | flat, its block flush with the back post, never behind it | Solace |
| Flat rail | 108.5 from the back; the face runs into its holder, as the original's face runs through its holders | the model |
| Gap, tier 1 envelope to flat-rail envelope | ≥ 10 (test) | guess |
| Plate, across the rail | 20 | the original's, unscaled |
| Bars | post, face, crossbar and diagonal solid 3 mm; the foot a 10 mm ladder, two 3 mm strips and a 4 mm slot | the original's (Light), measured off its mesh |
| Rail holder | the original's, lifted from its top rail at every seat: two hooks round the lips, the channel open between, no screw | the original |
| Bracing | the original's top and crossbar; a 3 mm diagonal from below tier 1's centre to the back rail's holder, a triangle with face and foot, as the Pro's diagonal | the original; the diagonal's ends are ours |
| Footprint, side | 154 deep × 180 tall (the original: 130 × 90) | the model |
| Bracket volume | 80 cm³ each | the model |

## How a rail is held

As the original holds its rails: the rail slides through a slot of its own section in the original's holder,
two hooks round its lips with the channel open between. Nothing pins it lengthwise but the slot's grip, as in the original.

Modules clip onto the rail between the brackets, so they only need room from each other, not from the frame.

## How it prints

Flat, as modelled, 20 mm tall; every wall is vertical, so no overhangs. The rail slots and ladder slot run straight through.

Print the gauge first (`out/din-rail-bench-stand_gauge.3mf`, 5.5 cm³): one rail holder, 10 tall, a strut under it.
Slide a rail offcut through and feel the grip before the brackets.

## Open

- The holder's grip on a rail in PETG: unmeasured; the gauge settles it.
