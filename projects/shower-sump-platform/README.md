# Shower-sump platform

Symphony: [`diagrams/electrical/circuit-inventory.md`](https://github.com/mark-brannan/symphony/tree/main/diagrams/electrical/circuit-inventory.md)

Purpose: a level seat for the shower sump box down in the bilge, forward of amidships, so the sump sits
low, at bilge level. The underside follows the hull's V.

## Owner's brief, 2026-11-19

- Very simple. About as wide as the sump's base: where it goes, the sump's wings just about touch hull to
  hull at the right height. It does not go all the way down.
- The hull is a V two ways: the bilge V across the boat, and the narrowing toward the bow.
- Bonded in with thickened epoxy or 3M 5200.
- The Fusion design ("shower sump platform", v6, 2026-05-03; `ref/fusion-v6.step`) had the angle and
  shape not quite right. It was a 280 x 110 deck on two legs; the legs' faces lean 55 degrees above
  horizontal and pull in 18 mm per 100 mm toward its narrow end, and those are the defaults here.

## Shape

A flat deck, `w_aft` to `w_fwd` across and `len` fore-aft, at the height of the sump's wings. Its two long
edges are skirts that lean in at `hull_angle` (the bilge V); `w_aft` against `w_fwd` is the V toward the
bow. Each skirt is one flat face, the bonding face, held `bond_gap` inside the hull for the adhesive.
Underneath is open; nothing reaches the keel. Prints deck down.

## Measured

Nothing yet. The widths, length and angle are the Fusion v6 numbers, which were close but not right.
