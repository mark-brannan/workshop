# symphony-head-mirror

Outline of the head's mirror over the sink, for a shatterproof replacement
(acrylic mirror, polycarbonate mirror or laminated glass). No corner is square.

Symphony: none yet

## Deliverables

- `out/symphony-head-mirror.dxf`: outline in mm on layer `cut`, front view (reflective face up).
- `out/symphony-head-mirror.png`: dimensioned drawing, front view.

The shape is not symmetric: a piece cut mirror-imaged will not fit. Cut it
reflective face up, in the front view.

## Measured (2026-11-22, out of the boat, from the back)

Tape and speed square. Photos are in the owner's Downloads, `Symphony Mirror Photos`.

| Edge / corner | Reading | Photo |
|---|---|---|
| Long edge with "AGM 2 21-03" on the back (`top`) | 20 3/16 in | `..._083552` |
| Other long edge (`bottom`) | 20 1/16 in | `..._083518` |
| End with the two touching pads (`wide`) | 10 5/8 in | `..._083615`, `..._083626` |
| Other end (`narrow`) | 9 13/16 to 9 15/16, taken as 9 7/8 in | `..._083653`, `..._083809` |
| Across the middle | 10 1/4 in (check: the solved shape gives 10.25) | `..._083445` |
| Corner angles | speed square reads 85° | `..._083948`, `..._084015`, `..._084046` |

Four sides plus one angle fix a four-sided shape. The 85° is put at the
narrow-top corner. That choice was checked against the angles read off the
top-down photo `..._083445`:

| Corner | Photo estimate | Solved |
|---|---|---|
| narrow-top | 82.8° | 85.0° |
| wide-top | 94.5° | 93.9° |
| wide-bottom | 84.2° | 83.9° |
| narrow-bottom | 98.5° | 97.2° |

Not measured: the thickness and the diagonals. A diagonal (`narrow-top` to
`wide-bottom`, 595 mm solved) would confirm the shape to about a millimetre.

`Params.clearance_mm` takes an equal amount off every edge if the replacement
should be cut undersize.
