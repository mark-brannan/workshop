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
| OpenSCAD + BOSL2 | Default modeller, the happy path | Whatever install the box has, found by `src/shop/scad.py` (`shop build`). On the WSL box, the Windows install: the Nightly (2026.11.01, Manifold) when present, else 2021.01. BOSL2 not in the system `libraries/` folder yet; install to confirm. On a Mac: `brew install uv` and `brew install --cask openscad@snapshot` (Manifold), BOSL2 cloned into `~/Documents/OpenSCAD/libraries/BOSL2`. A/B against build123d: `projects/README-ab.md` |
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
- Outputs under `out/` are committed. Git LFS only once a file passes 5 MB, not before.
- A project is `projects/<slug>/` with `README.md` (purpose, constraints, what was measured and from what), `model.scad` or `model.py`, a test file, `out/`.

## Verification loop

Build, `uv run pytest -q`, read the PNG, then report with the picture.
