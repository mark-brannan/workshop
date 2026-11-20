# Shower-sump platform

Symphony: [`diagrams/electrical/circuit-inventory.md`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/circuit-inventory.md)

Purpose: a level seat for the shower sump box down in the bilge, forward of amidships, so the sump sits
low, at bilge level. The underside follows the hull's V.

## Owner's brief, 2026-11-19

- Very simple. About as wide as the sump, angled to match the hull's V toward the bow.
- The Fusion design ("shower sump platform", v6, 2026-05-03; `ref/fusion-v6.step`) had the wrong angle
  and shape. It was a 280 x 110 deck on two angled legs.

## Shape

A flat deck carried by `frames` V-shaped frames. Each frame's underside is the hull's V at that station:
`deadrise_aft` and `deadrise_fwd` set it at the two ends, so a V that steepens toward the bow fits, and
`keel_rise` tilts the keel line. Water runs under the deck and through a notch at the keel in each frame.
Prints deck down. A strap goes round the sump and the deck between the frames.

## Measured

Nothing yet. Each `(unmeasured)` value in `model.scad` is a guess: the sump's footprint, the deadrise and
the keel flat.
