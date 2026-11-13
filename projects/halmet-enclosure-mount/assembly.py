"""Colour renders of the assembled mount in its box: assembled, exploded, and the tier on its own.

Usage: uv run python assembly.py   (writes out/assembly*.png; one openscad run per component)
"""
import sys
import tempfile
from pathlib import Path

import pyvista as pv

from shop.scad import OpenSCAD

HERE = Path(__file__).parent
OUT = HERE / "out"

# component: (colour, opacity, exploded dz). Order is assembly order. The LM393 light sensor is left out for now.
PARTS = {
    "box": ("#9aa4ad", 0.18, -45),
    "frame": ("#c8a24a", 1, 0),
    "screws_floor": ("#333333", 1, 12),
    "tier_standoffs": ("#d4af37", 1, 22),
    "halmet": ("#1f6f3f", 1, 32),
    "screws_board": ("#333333", 1, 44),
    "tier": ("#e0c07a", 1, 72),
    "screws_m25": ("#333333", 1, 72),
    "module_standoffs": ("#d4af37", 1, 72),
    "oled": ("#2456a6", 1, 72),
    "oled_glass": ("#111111", 1, 72),
    "oled_header": ("#222222", 1, 72),
    "seg": ("#2456a6", 1, 72),
    "seg_body": ("#f2f2f2", 1, 72),
    "ldr": ("#1b5fbf", 1, 72),
    "screws_ldr": ("#333333", 1, 72),
    "screws_tier": ("#333333", 1, 92),
    "lid": ("#9aa4ad", 0.12, 110),
}
TIER = ["tier", "screws_m25", "module_standoffs", "oled", "oled_glass", "oled_header", "seg", "seg_body", "ldr", "screws_ldr"]


def build(tmp: Path) -> dict[str, pv.PolyData]:
    osc = OpenSCAD()
    meshes = {}
    for name in PARTS:
        stl = tmp / f"{name}.stl"
        osc.run(HERE / "assembly.scad", stl, "-D", f'show="{name}"')
        meshes[name] = pv.read(str(stl))
    osc.cleanup()
    return meshes


def scene(p, meshes, names, explode=False):
    for n in names:
        colour, alpha, dz = PARTS[n]
        m = meshes[n].translate((0, 0, dz), inplace=False) if explode else meshes[n]
        p.add_mesh(m, color=colour, opacity=alpha, smooth_shading=False)


def shot(path, panels, size=700):
    rows, cols = (1, len(panels)) if len(panels) < 4 else (2, 2)
    p = pv.Plotter(off_screen=True, shape=(rows, cols), window_size=(size * cols, size * rows), border=True)
    for i, (label, names, explode, cam) in enumerate(panels):
        p.subplot(i // cols, i % cols)
        scene(p, MESHES, names, explode)
        p.add_text(label, font_size=11)
        if cam == "iso":
            p.view_isometric()
        elif cam == "under":
            p.view_isometric()
            p.camera.elevation = -60
        else:
            p.camera_position = cam
            p.enable_parallel_projection()
        p.reset_camera()
    p.screenshot(str(path))
    p.close()
    print(path)


if __name__ == "__main__":
    pv.OFF_SCREEN = True
    with tempfile.TemporaryDirectory() as d:
        MESHES = build(Path(d))
    inside = [n for n in PARTS if n != "lid"]
    shot(OUT / "assembly_tier.png", [("tier, modules on", TIER, False, "iso"), ("tier from below", TIER, False, "under")])
    shot(OUT / "assembly.png", [
        ("assembled (box ghosted)", inside, False, "iso"),
        ("top", inside, False, "xy"),
        ("from the gland side, lid ghosted", list(PARTS), False, "xz"),
        ("from the right end", list(PARTS), False, "yz"),
    ])
    shot(OUT / "assembly_exploded.png", [("exploded, bottom to top in assembly order", list(PARTS), True, "iso")], size=1100)
    sys.exit(0)
