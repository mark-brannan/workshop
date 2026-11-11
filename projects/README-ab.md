# OpenSCAD vs build123d: happy-path A/B

Date 2026-11-03. Plain OpenSCAD, no libraries. Two parts already in the repo
as build123d (`model.py`) were rewritten as `model.scad` to the same spec;
both build through `uv run python -m shop.build` and both have tests.

OpenSCAD used: `OpenSCAD version 2026.11.01` (the Nightly, `--backend=manifold`),
`/mnt/c/Program Files/OpenSCAD (Nightly)/openscad.exe`. The 2021.01 release
(`/mnt/c/Program Files/OpenSCAD/openscad.exe`, CGAL) was measured too and its
numbers are in brackets. Timings are warm, repeated three times, same machine
(WSL2 driving the Windows exe); build123d numbers are in-process and exclude
the interpreter start (`import build123d` 5.3 s via `uv run`, measured once);
each OpenSCAD call includes its 0.13 s exe start.

| | bracket: build123d | bracket: OpenSCAD | plate: build123d | plate: OpenSCAD |
|---|---|---|---|---|
| Non-blank lines | 78 | 45 | 66 | 25 |
| `wc -w` (token proxy) | 405 | 292 | 233 | 144 |
| Build + export, s | 0.11 (STL+3MF+STEP) | 0.20 STL [3.44] | 0.08 (DXF+SVG+STL+3MF+STEP) | 0.34 DXF+STL [0.87] |
| Render, s | 0.43 pyvista | 0.50 OpenSCAD PNG [2.99]; pyvista on the STL 0.43 | 0.43 pyvista | 0.48 [0.50]; pyvista 0.41 |
| Edit-run iterations on the model | n/a | 1 (first run correct) | n/a | 1 (first run correct) |
| Outside round 2 mm | right (fillet face + PNG) | right (ray probe z=0.946 at y=0.3; pyvista `right` view) | - | - |
| Hole chamfers 1 mm | right (4 cone faces + PNG) | right (ray probes at 45 deg; visible in PNG) | - | - |
| Holes | 4, by cylinder faces + axes | 4, by ray through each centre | 4 + slot, by sketch area | 4 + slot, by rays |
| DXF entities | 6 LINE, 4 CIRCLE, 2 ARC | - | layer `cut`, `$INSUNITS` 4 (mm) | [326 LINE] / 6 closed LWPOLYLINE, layer `0`, no `$INSUNITS` |
| `$fn` | n/a (true arcs) | 64 | n/a | 64 |

Iterations around the models, counted honestly: `src/shop/scad.py` took 3
edit-run rounds (project path resolution, Nightly path staging, temp cleanup)
and the two test files 3 (trimesh's ray engine needs `rtree` and its section
polygons `networkx`, neither in the venv, so `shop.testing.ray_hits` is a
20-line numpy ray caster; a shape bug in it; the Nightly's DXF style).

## PNGs looked at

| | build123d (pyvista) | OpenSCAD (`--render`, Tomorrow) | pyvista on the OpenSCAD STL |
|---|---|---|---|
| bracket | `demo-bracket/out/bracket.png` | `demo-bracket/out/bracket_scad.png` | `demo-bracket/out/bracket_scad_pv.png`, `_pv_views.png` |

The OpenSCAD PNG (camera `rot 55,0,25`, viewed from -Y) shows the wall-hole
chamfers plainly and hides the base holes and the round; the pyvista iso
(from +X+Y) shows the round and the base-hole chamfers and hides the wall
chamfers. Neither is poor; the pyvista 2x2 `_views.png` is what confirms the
round (`right` view). Both renderers are written for every `.scad` build.

## Assertions with no mesh equivalent

- Counting bores, the fillet and the chamfer cones by B-rep face type
  (`CYLINDER`/`CONE` with a radius): replaced by ray probes that land on the
  cone at the depth a 45 deg chamfer predicts and on the round at the height a
  2 mm arc predicts (`abs_tol` 0.05).
- Hole axes from cylinder faces: implied by the ray direction that passes.
- STEP round trip: no STEP from OpenSCAD.
- Sketch area from the B-rep: volume window on the extrude instead.
- `CIRCLE == 4` in the DXF and layer name `cut`: curves are polylines, layer is `0`.

## OpenSCAD DXF notes

- Unitless as OpenSCAD writes it (fixed by `finish_dxf`, below). 2021.01 writes no HEADER section; the Nightly writes a HEADER
  with extents but no `$INSUNITS`. Numbers are the model's millimetres.
  ezdxf read the header-less file back with a default `$INSUNITS` of 6
  (metres) in one run; a consumer must not trust that field.
- Layer names: not possible from plain OpenSCAD; everything lands on layer
  `0`. Since this write-up, `shop.scad.finish_dxf` post-processes every
  OpenSCAD DXF: R2010, `$INSUNITS` 4 (mm), geometry on layer `cut` coloured
  for its LightBurn layer. Several layers means one OpenSCAD DXF per layer,
  merged by the same function.
- Curves: 2021.01 emits one LINE per `$fn` segment (326 entities here);
  the Nightly emits one closed LWPOLYLINE per loop (6 entities). Neither
  writes CIRCLE or ARC.
- `$fn = 64`: a 0.16 mm chord on a 3.2 mm hole, fine for the laser.

## Where a library would have helped

`profile()` and `hole()` in the bracket (the quarter-round built from a
`difference` plus an `intersection` of a circle and a square, the chamfer as
an explicit cone with an epsilon) are the 14 lines BOSL2 would replace with
`cuboid(rounding=, edges=)` and `cyl(chamfer1=)` plus attachments for the
hole placement. The plate needed nothing a library offers beyond `hull()`
for the slot.

## Driving openscad.exe from WSL

- 2021.01 reads and writes `\\wsl.localhost` UNC paths directly.
- The 2026.11.01 Nightly aborts on a UNC input (`std::filesystem_error:
  cannot set current path`) and silently writes nothing to a UNC output
  (exit 0, no file). `shop.scad` stages the project's `*.scad` in
  `/mnt/c/Users/Solace/AppData/Local/Temp/shop_<pid>/`, writes there and
  moves the result back; the first failed UNC attempt costs about 1 s per
  build, after which the instance stays on the staged path.
- `--backend=manifold` is passed only when `--help` lists it; it must not
  be given twice.
- Values with quotes pass through WSL interop intact: `-D mode="3d"` as one
  argv element works.
