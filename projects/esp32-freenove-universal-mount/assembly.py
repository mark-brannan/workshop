"""Assembled mount: board on the standoffs, two DIN clips screwed to the back. Writes out/assembly.png and out/assembly_exploded.png.

Usage: uv run python assembly.py   (reads out/esp32-freenove-universal-mount_scad.stl, so build first)
The board is a stand-in slab (87 x 83 x 1.6, vendor drawing; thickness assumed), not a model of the module.
"""
import re
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).parent
OUT = HERE / "out"
CLIP_STL = HERE.parent / "din-rail-psu-mount" / "ref_din_clip_heat_insert.stl"
CLIP_RAIL_Y = 27.05  # the clip's rail centre in its own model, x; it lands on y = 0 across the rail

P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
CLIP_XS = [-20.0, 20.0]
# The clip is turned, not mirrored: its x (hook end 5, latch end 56) runs along -Y, its flat z = 0 face
# against the plate's back, its body toward the rail (-Z). Hook ends up at +Y.
CLIP_TURN = np.array([[0, -1, 0, 0], [-1, 0, 0, CLIP_RAIL_Y], [0, 0, -1, 0], [0, 0, 0, 1]], float)
assert np.isclose(np.linalg.det(CLIP_TURN[:3, :3]), 1)


def clips():
    out = []
    for x in CLIP_XS:
        m = pv.read(str(CLIP_STL))
        m.transform(CLIP_TURN, inplace=True)
        out.append(m.translate((x, 0, 0), inplace=False))
    return out


def board(z0):
    b = pv.Box(bounds=(-43.5, 43.5, -41.5, 41.5, z0, z0 + 1.6)).triangulate()
    return b


def scene(p, explode):
    dz = 28 if explode else 0
    mount = pv.read(str(OUT / "esp32-freenove-universal-mount_scad.stl"))
    p.add_mesh(mount, color="#c8a24a")
    for c in clips():
        p.add_mesh(c.translate((0, 0, -dz), inplace=False), color="#4a8fd6")
    z0 = P["plate_t"] + P["standoff_h"]
    p.add_mesh(board(z0 + dz), color="#1f6f3f")
    for sx in (-1, 1):
        for sy in (-1, 1):
            h = pv.Cylinder(center=(sx * P["hole_dx"] / 2, sy * P["hole_dy"] / 2, z0 + dz + 2.4), direction=(0, 0, 1), radius=3.0, height=1.6)
            p.add_mesh(h, color="#333333")


def shot(path, panels, size=800, explode=False):
    p = pv.Plotter(off_screen=True, shape=(2, 2) if len(panels) == 4 else (1, len(panels)),
                   window_size=(size * (2 if len(panels) == 4 else len(panels)), size * (2 if len(panels) == 4 else 1)), border=True)
    for i, (label, vec, up, ortho) in enumerate(panels):
        p.subplot(i // 2 if len(panels) == 4 else 0, i % 2 if len(panels) == 4 else i)
        scene(p, explode)
        p.add_text(label, font_size=11)
        p.view_vector(vec, viewup=up)
        p.reset_camera()
        if ortho:
            p.enable_parallel_projection()
    p.screenshot(str(path))
    p.close()
    print(path)


if __name__ == "__main__":
    pv.OFF_SCREEN = True
    shot(OUT / "assembly.png", [
        ("board side up, from front-left: front = -Y (viewer), rail runs left-right (X)", (-1, -1, 0.9), (0, 0, 1), False),
        ("from below: clips screwed to the back (rail side), hook end at +Y", (1, 1, -0.9), (0, 0, 1), False),
        ("plan from above: board long side along the rail (X); clips span the short side (Y)", (0, 0, 1), (0, 1, 0), True),
        ("end view from +X: clip hooks at top (+Y), spring latch at bottom (-Y)", (1, 0, 0), (0, 0, 1), True),
    ])
    shot(OUT / "assembly_exploded.png", [("exploded: clips screwed to the back, board on the four standoffs", (-1, -1, 0.5), (0, 0, 1), False)],
         size=1100, explode=True)
