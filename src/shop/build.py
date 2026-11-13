"""Build every model in a project dir, Python or OpenSCAD, the same way.

    uv run python -m shop.build                      # all projects/*
    uv run python -m shop.build projects/demo-bracket  # one project

``model.py`` runs as a script (it exports itself). ``model.scad`` builds via
``shop.scad.build_scad`` into ``out/<slug>_scad.*`` (STL, 3MF, PNGs); a model with
``mode = "2d"`` at top level is a 2D model and also gets a DXF. Each
``part-<name>.scad`` beside it is a further printed part, built to ``out/<slug>_<name>.*``. Without
OpenSCAD the .scad models are skipped, not failed (CI has none).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .scad import build_scad, find_openscad, has_mode_variable

ROOT = Path(__file__).resolve().parents[2]


def build_project(proj: Path) -> int:
    rc = 0
    name = proj.name.removeprefix("demo-")
    py = proj / "model.py"
    if py.exists():
        print(f"== {py}")
        rc |= subprocess.run([sys.executable, str(py)], cwd=proj).returncode
    for scad in [proj / "model.scad", *sorted(proj.glob("part-*.scad"))]:
        if not scad.exists():
            continue
        print(f"== {scad}")
        if find_openscad() is None:
            print("   skipped: openscad not found on this box")
        else:
            stem = "scad" if scad.name == "model.scad" else scad.stem.removeprefix("part-")
            paths = build_scad(scad, proj / "out", f"{name}_{stem}", two_d=has_mode_variable(scad), threemf=True)
            times = paths.pop("times")
            print(f"   {paths.pop('version')}; " + ", ".join(f"{k} {v:.2f}s" for k, v in times.items()))
            for k, v in paths.items():
                print(f"   {k:12s} {v}")
            rc |= 1 if "render_error" in paths else 0
    return rc


def main(argv: list[str]) -> int:
    projs = [Path(a).resolve() for a in argv[1:]] or sorted(p for p in (ROOT / "projects").iterdir() if p.is_dir())
    rc = 0
    for p in projs:
        if (p / "model.py").exists() or (p / "model.scad").exists():
            rc |= build_project(p)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
