# workshop

Local, disposable proof that a code-first CAD toolchain runs headless on WSL2:
build123d (OCCT via cadquery-ocp) for geometry, pyvista/VTK off-screen for PNG
renders, ezdxf for checking laser output. Python 3.12 via `uv`.

Layout

- `src/shop/export.py` — `export_all(part, name, outdir)` writes STL, 3MF, STEP, PNG.
- `src/shop/render.py` — off-screen PNG (iso + 2x2 iso/top/front/right).
- `projects/demo-bracket/` — parametric L-bracket (3D print / STEP).
- `projects/demo-plate/` — 100x60 plate sketch, DXF + SVG for the laser and the same
  sketch extruded to STL. Outputs land in each project's `out/` (gitignored).

Commands

    uv sync
    uv run python projects/demo-bracket/model.py
    uv run python projects/demo-plate/model.py
    uv run pytest

Remove with `rm -rf ~/workshop`.
