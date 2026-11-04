"""Parametric L-bracket (mm). Run: uv run python projects/demo-bracket/model.py"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Cylinder,
    GridLocations,
    Locations,
    Mode,
    Part,
    Plane,
    chamfer,
    fillet,
)

HERE = Path(__file__).parent


@dataclass(frozen=True)
class BracketParams:
    thickness: float = 3.0
    width: float = 40.0        # shared X extent of both plates
    base_depth: float = 30.0   # horizontal plate, along Y
    wall_height: float = 25.0  # vertical plate, along Z
    hole_d: float = 4.2
    holes_per_leg: int = 2
    hole_pitch: float = 24.0   # between the two holes, along X
    outer_fillet: float = 2.0
    hole_chamfer: float = 1.0


def build(p: BracketParams = BracketParams()) -> Part:
    t = p.thickness
    with BuildPart() as bp:
        # Horizontal plate: X in [0,w], Y in [0,base_depth], Z in [0,t]
        with Locations((p.width / 2, p.base_depth / 2, t / 2)):
            Box(p.width, p.base_depth, t)
        # Vertical plate: Y in [0,t], Z in [0,wall_height]; overlaps base at the corner
        with Locations((p.width / 2, t / 2, p.wall_height / 2)):
            Box(p.width, t, p.wall_height)
        # Outside corner edge: along X at y=0, z=0
        outer = bp.edges().filter_by(Axis.X).group_by(Axis.Y)[0].group_by(Axis.Z)[0]
        fillet(outer, radius=p.outer_fillet)

        # Base holes, drilled from the top face (+Z)
        base_y = (p.base_depth + t) / 2  # centred on the clear part of the base
        with Locations(Plane.XY.offset(t)):
            with Locations((p.width / 2, base_y)):
                with GridLocations(p.hole_pitch, 1, p.holes_per_leg, 1):
                    Cylinder(p.hole_d / 2, t, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
        # Wall holes, drilled from the outside face (-Y), through +Y
        wall_z = (p.wall_height + t) / 2
        # Plane.XZ normal is -Y with origin at y=0, so Align.MAX puts the cut in y in [0, t].
        with Locations(Plane.XZ):
            with Locations((p.width / 2, wall_z)):
                with GridLocations(p.hole_pitch, 1, p.holes_per_leg, 1):
                    Cylinder(p.hole_d / 2, t, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)

        # 1 mm chamfer on the hole edges at the base top face (z=t) and wall outer face (y=0)
        hole_edges = bp.edges().filter_by(lambda e: e.geom_type.name == "CIRCLE")
        top_hole_edges = hole_edges.filter_by(lambda e: abs(e.center().Z - t) < 1e-6)
        outer_hole_edges = hole_edges.filter_by(lambda e: abs(e.center().Y - 0) < 1e-6)
        chamfer(top_hole_edges + outer_hole_edges, length=p.hole_chamfer)

    part = bp.part
    part.label = "demo-bracket"
    return part


def main(argv: list[str]) -> int:
    from shop.export import export_all

    t0 = time.perf_counter()
    part = build()
    t1 = time.perf_counter()
    paths = export_all(part, "bracket", HERE / "out")
    t2 = time.perf_counter()
    print(f"build {t1 - t0:.2f}s, export {t2 - t1:.2f}s, volume {part.volume:.1f} mm^3")
    for k, v in paths.items():
        print(f"  {k:10s} {v}")
    return 1 if "render_error" in paths else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
