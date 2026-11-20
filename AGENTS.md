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
| OpenSCAD + BOSL2 | Default modeller, the happy path | Whatever install the box has, found by `src/shop/scad.py` (`shop build`). On Linux and WSL, a native `openscad` on PATH with BOSL2, installed once per box by `scripts/install-openscad-linux`, outside any worktree; never install a private copy in a scratch dir or worktree. The Windows install is the fallback only. On a Mac: `brew install uv` and `brew install --cask openscad@snapshot` (Manifold), BOSL2 cloned into `~/Documents/OpenSCAD/libraries/BOSL2`. A/B against build123d: `projects/README-ab.md` |
| build123d | True fillets on arbitrary edges, STEP export | `uv` project, headless |
| Render helper | PNG of every build (`src/shop/render.py`) | pyvista off-screen |
| OrcaSlicer | Front-end for print | user's machine |
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

## Sibling repo: symphony (the boat)

The boat's system docs live in symphony (public; local checkout `~/symphony`): what is installed, how it is wired, firmware, Signal K.
This repo holds the object: geometry, caliper numbers, print and cut files, and the wiring inside one box.
The seam is the box's connectors: inside is here, outside is there.

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
