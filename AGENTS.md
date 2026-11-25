# workshop

Code-first CAD so an agent can design, test and render physical parts with
minimal human toil. The user designs by sending a photo of a real object, caliper
measurements and a brief. **Calipers are truth; the photo is topology.**
A measured object that will be mounted, clamped or fitted again goes in the
library (`src/shop/`) so the second mount costs nothing.
Its dimensions, part number and their source go in [`parts.md`](parts.md) the day they are measured.

## Tools and roles

| Tool | Role | Here |
|---|---|---|
| OpenSCAD + BOSL2 | Default modeller, the happy path | Whatever install the box has, found by `src/shop/scad.py` (`shop build`). On Linux and WSL, a native `openscad` on PATH with BOSL2, installed once per box by `scripts/install-openscad-linux`, outside any worktree; never install a private copy in a scratch dir or worktree. The Windows install is the fallback only. On a Mac: `brew install uv`, then `scripts/install-openscad-mac` once per box (cask `openscad@snapshot`, Manifold; BOSL2 in `~/Documents/OpenSCAD/libraries/BOSL2`); without it the scad tests skip. A/B against build123d: `projects/README-ab.md` |
| build123d | True fillets on arbitrary edges, STEP export | `uv` project, headless |
| Render helper | PNG of every build (`src/shop/render.py`) | pyvista off-screen |
| OrcaSlicer | Front-end for print; headless slicing | The user's GUI is the Windows install. Agents slice with a native `orca-slicer` on PATH, installed once per box by `scripts/install-orcaslicer-linux` at the Windows install's version (RUNBOOK: Slice headless) |
| LightBurn | Front-end for laser | workshop Mac |
| VS Code | Reads hand-written g-code for the router | |
| Fusion 360 | Not used unless a 3D-contour CAM job appears | |
| Fusion scripts | STL merge to STEP (`fusion/merge_stl/`), run inside Fusion | `shop fusion` prints the folder to add |

## Deliverables by destination

| Destination | Deliverable |
|---|---|
| Cut (laser) | DXF, layer names mapping to LightBurn layers |
| Print | 3MF or STL |
| Tweak | A parameter: OpenSCAD Customizer or chat |
| Read | PNG render or dimensioned PDF |

SVG is an intermediate only; never the deliverable handed to the user.

## Conventions

- Millimetres. Z up.
- Print orientation is the model orientation unless the project README says otherwise.
- Supports are designed, not left to the slicer. Every overhang and ceiling in print orientation holds itself up by shape, for example:
  - a wall or slope at 45° or steeper, or the part reoriented so the overhang becomes a wall
  - a point-up (teardrop) or small hexagonal hole
  - a 45° roof or arch over a wider opening, or the opening run out to the rim
  - a gusset under a ledge, shelf or boss; a stepped 45° corbel where a gusset won't fit
  - a 45° chamfer on a downward-facing edge, since a fillet goes flat at its foot; fillets on vertical and upward edges
  - a downward-facing counterbore printed over two sacrificial bridge layers laid at 90°
  - a split into flat prints

  Where shape can't do it, model a breakaway support into the part. Flat overhangs and bridges tend to print badly even when short; avoid them where a shape will do, and raise any that remain with the user. The README says how each overhang is held. `shop build` warns on a flat overhang with its unsupported span; it never fails.
- Prefer a method that builds the same mesh every time over one that doesn't, where either will do. `minkowski()` of non-convex shapes is one that doesn't: on Manifold its mesh changes from run to run and is often not a closed solid. `shop build` warns on a mesh that is not a closed solid, and on geometry that changed when no `.scad` did.
- Parameters at the top of every model: a dataclass (Python) or Customizer-commented variables (OpenSCAD).
- Every model has a test file asserting bounding box, a volume window and feature counts.
- Every build writes a PNG; the agent looks at it before reporting.
- A plate-like part whose hole spacing or fit against a measured object is unproven gets a `part-gauge.scad`, and the gauge prints first. By default it is sliced from the model: `shop gauge projects/<slug> "mount()" <z_plate> [<z_wall>]`. It is hand-written where the gauge should drop features or save plastic.

## Fit numbers (calibration)

All unmeasured. `projects/calibration/` fills this table. **Nothing ships on a guess.**

| Row | Value | Source |
|---|---|---|
| K2 Plus hole clearance (ASA) | unmeasured | |
| K2 Plus press fit | unmeasured | |
| K2 Plus horizontal expansion | unmeasured | |
| K40 kerf, 3 mm ply | unmeasured | |
| K40 kerf, 3 mm acrylic | unmeasured | |
| Router end-mill runout | unmeasured | |

## Repo rules

- Tools differ from box to box. `shop doctor` lists this one's; a build skips what the box lacks, never fails on it.

- Push to `main`. No PRs, no drafts, no "shall I commit" turns.
- A checkpoint whose next step is a print or a physical test is pushed the same turn: to `main`, or to the PR when the work is on one. No turn spent asking.
- Outputs under `out/` are committed. Git LFS only once a file passes 5 MB, not before.
- The 3MF is what the user prints and looks at. A change to a printable part is not done, and a print is never named as the next step, until `shop build projects/<slug>` has regenerated its 3MF and the commit is on `main`. A PNG render alone is not a deliverable. Check `origin/main` holds the new 3MF before saying so.
- A project is `projects/<slug>/` with `README.md` (purpose, constraints, what was measured and from what), `model.scad` or `model.py`, a test file, `out/`.

## Verification loop

Build, `uv run pytest -q`, read the PNG, then report with the picture.

### Asymmetric mating features

A set of mating features is asymmetric here when its mirror image is a different set: a diagonal pair of holes, an offset corner, three corners of four, a snap finger or key toward one end, a pocket on one side. Holes, fingers, ridges, keys and pockets all count. Test: flip it left to right; if a feature lands somewhere new, this section applies.

Two faces that mate see the same features from opposite sides, so one is the mirror of the other. A symmetric set forgives a model that forgets this; an asymmetric one mates one way round only. This burned several troubleshooting sessions on `din-rail-psu-mount`, `bme688-cabin-screen` and `halmet-piezo-pod`.

A hand can turn a part over; it cannot mirror it. A part's print pose and the pose it is used in differ by `rotate()` and `translate()` only, never `mirror()`, in either direction: the assembly places the printed part by a turn, and a print pose is the designed part turned. `mirror()` builds symmetric shape inside a part; it never places one. A test fails on `mirror()` applied to a printed part (`tests/test_turned_not_mirrored.py`).

Where parts mate through such features, printed to printed or printed to a measured object, the report carries both of these before any print:

- **A 3D render of the assembly**, in the pose the user will assemble it, the mating features visibly in line. It labels front and back, and which way up each part goes. The agent looks at it before sending it. Where the user's word on orientation and the model disagree, the user's word stands.
- **A fit test** on the meshes that get printed, in the pose they are used, never on the hole or feature lists in `model.scad`. It fails on the mirrored layout. `shop.testing.seated_overlap` seats one printed mesh on another and, asked, seats the mirror image too; where the mirror image seats as cleanly, the test also checks what engages. A project that prints more than one part has one; the same test file lists the older projects that get theirs when next changed.

## Sibling repo: symphony (the boat)

The boat's system docs live in symphony (public; local checkout `~/symphony`): what is installed, how it is wired, firmware, Signal K.
This repo holds the object: geometry, caliper numbers, print and cut files, and the wiring inside one box.
The seam is the box's connectors: inside is here, outside is there.
Undecided is not a home. Work goes where its purpose is: choosing something for Symphony starts in symphony, in its `research/`. A project starts here when there is a thing to make.

| Diagram | Home | Format |
|---|---|---|
| Boat wiring: DC overview, circuits, cabinet layouts | symphony `diagrams/electrical/` | `.drawio` |
| Flows, software, signal paths | symphony | `.mmd` |
| Inside one box: sensor-to-MCU hookup | here, `projects/<slug>/` | `.drawio` |
| PCB | here, `projects/<slug>/` | KiCad |
| One-off mockup nobody will edit | not committed | SVG |

- A boat-bound project's README has a `Symphony:` line linking the symphony paths it plugs into (full GitHub URLs to symphony's `main`), or `Symphony: none yet`.
  `shop symphony` prints the index; a test fails on a link whose path left symphony's main.
- Before designing a part that will be installed on the boat, read the symphony paths on its `Symphony:` line; firmware, pin choices and circuits there constrain the part.
- A fact has one home. Don't copy a symphony table here; link it.
