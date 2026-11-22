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

The sump screws down through six Ø3 pilots into 12 mm bosses, at the Fusion deck's hole positions; only the
platform is bonded, so the sump comes out for cleaning. The middle is cut through (`opening`, 176 x 59).
Fusion had a pocket there instead, its floor 8 deep at the centre and about 18 near its ends; what it
received is not recorded.

## Measured

Aboard, 2026-11-21 (owner's tape and speed square; source
[`research/shower-sump`](https://github.com/mark-brannan/symphony/tree/main/research/shower-sump)):

| Parameter | Taped | Used |
|---|---|---|
| `w_aft`, hull to hull at tab height, aft | 8 3/4 in = 222.25 mm ("best guess") | 234.25 (+6 a side) |
| `w_fwd`, same, forward | 7 1/2 in = 190.5 mm ("best guess") | 208 (+8.75 a side) |
| `len`, fore-aft between the two widths | 3 1/2 in = 88.9 mm, the tab length (a working number) | 88.9 |
| `hull_angle` | hull leans 23 stbd, 25 port from vertical, mean 24 (speed square, rough) | 66 deg |

The sump's wings are D-shaped lobes, widest (215 mm tip to tip) at their middle, so the deck is widened over the taped
widths to cover them (owner, 2026-11-22); `wing_overlay.py` checks it. The hull is fixed, so that puts the deck about
12 mm higher on the hull than tab height; re-take the widths before printing. `opening` is 59 deep so the 89 mm
deck keeps 15 mm end strips. Bosses stop at the skirt's outer face. Known: `shop build` warns of a 3 mm flat
ceiling over the O3 pilots at x = +-100, where the skirt passes over the boss.

## Checking the wing fit

`ref/sump-wing-outline.csv` is the wing's plan outline traced from the box drawing (`ref/sump-drawing-wing.png`
shows the trace on the drawing). `uv run python projects/shower-sump-platform/wing_overlay.py` draws it over the
deck into `out/wing-overlay.png` and prints the least margin; `test_wing_fit.py` fails if the wing sticks out.
