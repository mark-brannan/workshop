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

At each end an arch (`arch_t` thick) ties the two skirts together under the deck's end strip, so the skirts can't
fold at their root and the 15 mm end strips become stiff beams (owner, 2026-11-22). It is a half-ellipse from the foot
of one skirt to the other, `arch_band` deep under the deck at its crown; printed deck down, each layer of it sits
inside the one below, so it needs no support. Each bonding face carries `fin_n` ridges running fore-aft, standing
`fin_h` into the epoxy (inside `bond_gap`): the face toward the skirt's foot is square to the skirt and bears the
sump's weight down the hull; the flank toward the deck faces down in print at about 80 degrees. Two staggered rows of Ø4 holes through each skirt
(`rivet_pitch`, between the ridges) let the epoxy set through as rivets, since it grips PETG poorly; a hole that
meets a boss stops at it; they are teardrops pointing at the skirt's foot, which is up in print. The skirts themselves
lean 24 degrees off vertical in print and hold themselves up.

The sump screws down through six Ø3 pilots into 12 mm bosses, at the Fusion deck's hole positions; only the
platform is bonded, so the sump comes out for cleaning.

Fasteners (owner, 2026-11-24): nylon M4 pan heads, no metal. The boat is ocean-going, and in a salt bilge
stainless pits in the crevice of a screw hole (304 badly, 316 too) and brass inserts dezincify. Drill each Ø3
pilot to 3.3 and tap M4 after printing; the Ø9 boss leaves about 2.8 mm of wall. A nylon penny washer, 12 mm
across or more, spans each 9 mm wing slot. Screw length: wing thickness + washer + about 8. The middle is cut through (`opening`, 176 x 59).
Fusion had a pocket there instead, its floor 8 deep at the centre and about 18 near its ends; what it
received is not recorded.

Cable-tie slits back up the screws against a wing sliding: two 6 x 2 slots per wing in the deck, just outboard of
the wing's straight edge at the aft end (`tie_slit_y`). A tie goes up a slot, over the wing, down the opening and
back under the deck: a loop round the deck strip and the wing. Sized for a 4.8 mm tie. The forward end has no room.

## Measured

Aboard, 2026-11-21 (owner's tape and speed square; source
[`research/shower-sump`](https://github.com/mark-brannan/symphony/tree/main/research/shower-sump)):

| Parameter | Taped | Used |
|---|---|---|
| `w_aft`, hull to hull at tab height, aft | 8 3/4 in = 222.25 mm ("best guess") | 234.25 (+6 a side) |
| `w_fwd`, same, forward | 7 1/2 in = 190.5 mm ("best guess") | 208 (+8.75 a side) |
| `len`, fore-aft between the two widths | 3 1/2 in = 88.9 mm, the tab length (a working number) | 88.9 |
| `hull_angle` | hull leans 23 stbd, 25 port from vertical, mean 24 (speed square, rough) | 66 deg (24 from vertical, the mean; owner's call: flexible ends conform, hull sanded, thickened epoxy) |

The sump's wings are D-shaped lobes, widest (215 mm tip to tip) at their middle, so the deck is widened over the taped
widths to cover them (owner, 2026-11-22); `wing_overlay.py` checks it. The hull is fixed, so that puts the deck about
12 mm higher on the hull than tab height; re-take the widths before printing. `opening` is 59 deep so the 89 mm
deck keeps 15 mm end strips. Bosses stop at the skirt's outer face. Known: `shop build` warns of a 3 mm flat
ceiling over the O3 pilots at x = +-100, where the skirt passes over the boss.

## Checking the wing fit

`ref/sump-wing-outline.csv` is the wing's plan outline traced from the box drawing (`ref/sump-drawing-wing.png`
shows the trace on the drawing). `uv run python projects/shower-sump-platform/wing_overlay.py` draws it over the
deck into `out/wing-overlay.png` and prints the least margin; `test_wing_fit.py` fails if the wing sticks out.
