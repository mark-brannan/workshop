"""``shop gauge``: a thin fit-check print of a plate-like model, with no modelling.

    shop gauge projects/<slug> "mount()" <z_plate> [<z_wall>]

Writes ``part-gauge.scad`` beside ``model.scad`` and builds the project. The gauge is
two horizontal slices of the finished part, re-extruded thin: one through the plate
at ``z_plate`` (outline and through-holes), one through the walls at ``z_wall`` (what
the mating object sits against; leave it out for a bare plate). It follows the model,
so a moved hole moves in the gauge on the next build.

It keeps every feature the slices cross and misses any they do not (a countersink, a
blind hole). A gauge that should drop features or save plastic is written by hand
instead; this command never overwrites a ``part-gauge.scad`` it did not generate.
The generated file is self-contained, so it builds wherever ``model.scad`` does.
"""

from __future__ import annotations

import sys
from pathlib import Path

MARK = "// Fit-check gauge, generated:"

TEMPLATE = """{mark} shop gauge projects/{slug} "{call}" {args}
// Two horizontal slices of the finished part, re-extruded thin. Rerun the command to change it;
// a hand-written gauge replaces this file and drops this first line.
use <model.scad>

/* [Gauge] */
z_plate = {z_plate};   // slice height through the plate: its outline and through-holes
z_wall = {z_wall};    // slice height through the walls the object sits against; below 0 for none
gauge_t = {t};       // gauge plate thickness
gauge_rise = {rise};    // gauge wall height above the plate

module gauge_slice() {{
    linear_extrude(gauge_t) projection(cut = true) translate([0, 0, -z_plate]) children();
    if (z_wall >= 0) translate([0, 0, gauge_t - 0.01]) linear_extrude(gauge_rise + 0.01) projection(cut = true) translate([0, 0, -z_wall]) children();
}}

gauge_slice() {call};
"""


def _num(x: float) -> str:
    return f"{x:g}"


def write_gauge(proj: Path, call: str, z_plate: float, z_wall: float | None = None, t: float = 1, rise: float = 2) -> Path:
    """Write ``proj/part-gauge.scad`` slicing ``call`` (a module of ``model.scad``) and return its path."""
    if not (proj / "model.scad").exists():
        raise FileNotFoundError(f"{proj}: no model.scad to slice")
    call = call.strip().rstrip(";")
    if not call.endswith(")"):
        call += "()"
    out = proj / "part-gauge.scad"
    if out.exists() and not out.read_text().startswith(MARK):
        raise FileExistsError(f"{out} is hand-written; remove it first to generate one")
    args = _num(z_plate) + ("" if z_wall is None else f" {_num(z_wall)}")
    out.write_text(TEMPLATE.format(
        mark=MARK, slug=proj.name, call=call, args=args,
        z_plate=_num(z_plate), z_wall=_num(-1 if z_wall is None else z_wall), t=_num(t), rise=_num(rise),
    ))
    return out


def main(argv: list[str]) -> int:
    if len(argv) not in (3, 4):
        print(__doc__.strip())
        return 2
    from . import build

    proj = Path(argv[0]).resolve()
    try:
        out = write_gauge(proj, argv[1], float(argv[2]), float(argv[3]) if len(argv) == 4 else None)
    except (OSError, ValueError) as e:
        print(f"shop gauge: {e}", file=sys.stderr)
        return 1
    print(f"wrote {out}")
    return build.build_project(proj)
