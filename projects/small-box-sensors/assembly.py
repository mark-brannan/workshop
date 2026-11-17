"""Colour renders of both builds in the box, and the clash check.

Usage: uv run python assembly.py   (writes out/assembly-<variant>*.png; one openscad run per component)
"""
import sys
import tempfile
from pathlib import Path

import pyvista as pv

from shop.render import VIEWS, _look
from shop.scad import OpenSCAD

HERE = Path(__file__).parent
OUT = HERE / "out"

# component: (colour, opacity, exploded dz). Order is assembly order.
PARTS = {
    "box": ("#6b7680", 0.22, -30),
    "screws_stack": ("#222222", 1, -8),
    "carrier": ("#e0a030", 1, 0),
    "screws_boss": ("#222222", 1, 30),
    "board_lo": ("#7a1fa2", 1, 10),
    "spacer": ("#e8c070", 1, 20),
    "board_hi": ("#1f5fbf", 1, 30),
    "qwiic": ("#d03030", 1, 30),
    "sp13": ("#c0c0c8", 1, 0),
    "vent": ("#f0f0f0", 1, 0),
    "lid": ("#9aa4ad", 0.12, 55),
}


def build(tmp: Path, variant: str) -> dict[str, pv.PolyData]:
    osc = OpenSCAD()
    meshes = {}
    for name in [*PARTS, "clash"]:
        if name == "vent" and variant != "env":
            continue
        stl = tmp / f"{variant}-{name}.stl"
        osc.run(HERE / "assembly.scad", stl, "-D", f'show="{name}"', "-D", f'variant="{variant}"')
        meshes[name] = pv.read(str(stl))
    osc.cleanup()
    return meshes


def clash_volume(meshes) -> tuple[float, tuple]:
    """Overlap volume in mm3 over every pair of components (the 1 mm3 marker removed) and where it is."""
    pts = meshes["clash"].points
    pts = pts[pts[:, 0] < 150]
    vol = meshes["clash"].volume - 1.0
    where = tuple(round(float(v), 1) for v in (*pts.min(0), *pts.max(0))) if len(pts) else ()
    return (0.0 if abs(vol) < 1e-3 else vol), where


def scene(p, meshes, names, explode=False):
    for n in names:
        if n not in meshes:
            continue
        colour, alpha, dz = PARTS[n]
        m = meshes[n].translate((0, 0, dz), inplace=False) if explode else meshes[n]
        p.add_mesh(m, color=colour, opacity=alpha, smooth_shading=False)


def shot(path, meshes, panels, size=700):
    p = pv.Plotter(off_screen=True, shape=(1, len(panels)), window_size=(size * len(panels), size), border=True)
    for i, (label, names, explode, cam) in enumerate(panels):
        p.subplot(0, i)
        scene(p, meshes, names, explode)
        p.add_text(label, font_size=11)
        if cam == "iso":
            p.view_isometric()
            p.camera.azimuth = 200
        else:
            p.camera_position = cam
            p.enable_parallel_projection()
        p.reset_camera()
    p.screenshot(str(path))
    p.close()
    print(path)


def sheet(path, meshes, names, size=500):
    p = pv.Plotter(off_screen=True, shape=(3, 3), window_size=(size * 3, size * 3), border=True)
    for i, (label, (vec, up, ortho)) in enumerate(VIEWS.items()):
        p.subplot(i // 3, i % 3)
        scene(p, meshes, names)
        p.add_text(label, font_size=12)
        _look(p, vec, up, ortho)
    p.screenshot(str(path))
    p.close()
    print(path)


def main() -> int:
    pv.OFF_SCREEN = True
    rc = 0
    for variant in ("env", "imu"):
        with tempfile.TemporaryDirectory() as d:
            meshes = build(Path(d), variant)
        vol, where = clash_volume(meshes)
        print(f"{variant}: overlap between components {vol:.2f} mm3 {where}")
        rc |= vol > 0
        inside = [n for n in PARTS if n != "lid"]
        shot(OUT / f"assembly-{variant}.png", meshes, [
            ("lid off, from the connector side", inside, False, "iso"),
            ("top, lid off", inside, False, "xy"),
            ("through the connector wall", list(PARTS), False, "xz"),
            ("exploded", list(PARTS), True, "iso"),
        ])
        sheet(OUT / f"assembly-{variant}_views.png", meshes, list(PARTS))
    return rc


if __name__ == "__main__":
    sys.exit(main())
