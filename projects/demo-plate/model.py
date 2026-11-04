"""2D plate for laser (DXF/SVG) and the same sketch extruded for print (STL).
Run: uv run python projects/demo-plate/model.py"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

from build123d import (
    BuildPart,
    BuildSketch,
    ExportDXF,
    ExportSVG,
    GridLocations,
    LineType,
    Mode,
    Rectangle,
    Circle,
    SlotCenterToCenter,
    Sketch,
    extrude,
)

HERE = Path(__file__).parent


@dataclass(frozen=True)
class PlateParams:
    length: float = 100.0
    width: float = 60.0
    thickness: float = 3.0
    hole_d: float = 3.2
    hole_inset: float = 5.0       # hole centre from each edge
    slot_length: float = 20.0     # centre-to-centre
    slot_width: float = 6.0


def sketch(p: PlateParams = PlateParams()) -> Sketch:
    with BuildSketch() as sk:
        Rectangle(p.length, p.width)
        with GridLocations(p.length - 2 * p.hole_inset, p.width - 2 * p.hole_inset, 2, 2):
            Circle(p.hole_d / 2, mode=Mode.SUBTRACT)
        SlotCenterToCenter(p.slot_length, p.slot_width, mode=Mode.SUBTRACT)
    return sk.sketch


def main(argv: list[str]) -> int:
    from shop.export import export_all

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    p = PlateParams()
    t0 = time.perf_counter()
    sk = sketch(p)

    dxf = ExportDXF(unit=__import__("build123d").Unit.MM)
    dxf.add_layer("cut", color=__import__("build123d").ColorIndex.RED, line_type=LineType.CONTINUOUS)
    dxf.add_shape(sk, layer="cut")
    dxf.write(out / "plate.dxf")

    svg = ExportSVG(unit=__import__("build123d").Unit.MM, line_weight=0.1)
    svg.add_layer("cut", line_color="red")
    svg.add_shape(sk, layer="cut")
    svg.write(out / "plate.svg")

    with BuildPart() as bp:
        extrude(sk, amount=p.thickness)
    part = bp.part
    paths = export_all(part, "plate", out)
    t1 = time.perf_counter()
    print(f"plate build+export {t1 - t0:.2f}s, area {sk.area:.1f} mm^2, volume {part.volume:.1f} mm^3")
    print(f"  dxf        {out / 'plate.dxf'}")
    print(f"  svg        {out / 'plate.svg'}")
    for k, v in paths.items():
        print(f"  {k:10s} {v}")
    return 1 if "render_error" in paths else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
