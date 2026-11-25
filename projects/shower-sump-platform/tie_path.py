"""The tie's path over the wing, down the fairlead and through the end-arch slit, drawn on the installed platform.

Usage: uv run python projects/shower-sump-platform/tie_path.py   (writes out/tie-wrap.png)
"""
import csv
import math
import re
import tempfile
from pathlib import Path

import numpy as np
import pyvista as pv

from shop.scad import OpenSCAD

HERE = Path(__file__).parent
P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
BG = "#14181f"


def tie_points(s=1):
    """Starboard (s=1) or port tie, centreline: along the wing top hugging the box wall, off both tips, down each fairlead, through the slits."""
    L, x0, z0, xs, zs = P["len"] / 2, P["tie_top_x"], P["tie_top_z"], P["tie_x"], P["tie_zc"]
    tip = 45.35  # wing tip, ref/sump-wing-outline.csv
    y_mouth, y_in = L - P["tie_lead"], L - P["arch_t"]
    half = [(x0, 0, z0 + 0.7), (x0, tip, z0 + 0.7), (xs, y_mouth + 0.7, zs + P["tie_slit_w"] / 2), (xs, y_in, zs)]
    pts = half + [(x, -y, z) for x, y, z in reversed(half)]
    return np.array([(s * x, y, z) for x, y, z in pts])


def wing(s=1):
    rows = [r for r in csv.reader(open(HERE / "ref/sump-wing-outline.csv")) if r and r[0][0] in "-0123456789"]
    pts = np.array([(s * float(x), float(y), 0.0) for x, y in rows])
    poly = pv.PolyData(pts, faces=[len(pts), *range(len(pts))]).triangulate()
    return poly.extrude((0, 0, P["tie_top_z"]), capping=True)


def main():
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl, "-D", 'part="installed"')
        plat = pv.read(str(stl))
    osc.cleanup()
    lean = math.degrees(math.atan2(P["tie_top_x"] - P["tie_x"], P["tie_top_z"] - P["tie_zc"]))

    p = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1800, 820), border=False)
    for col, (vec, zoom, title) in enumerate([
        ((0.9, 1, 0.55), 2.6, "Starboard forward end: over the wing, off its tip, down the fairlead, through the slit"),
        ((-0.45, 1, 0.3), 4.2, f"End face from forward and inboard: tie centreline slants {lean:.0f} deg; 12 mm slit tilted {P['tie_tilt']:.0f} deg"),
    ]):
        p.subplot(0, col)
        p.set_background(BG)
        p.add_mesh(plat, color="#7a869a", smooth_shading=False)
        p.add_mesh(plat.extract_feature_edges(feature_angle=30), color="#1d222b", line_width=1.5)
        p.add_mesh(wing(), color="#d8a830", opacity=0.45)
        p.add_mesh(pv.MultipleLines(tie_points()).tube(radius=0.65), color="#e04040")
        p.add_text(title, font_size=9, color="#e8e8e8")
        p.camera.focal_point = (P["tie_x"] + 4, P["len"] / 2, -3)
        p.camera.position = np.array(p.camera.focal_point) + 200 * np.array(vec)
        p.camera.up = (0, 0, 1)
        if col == 1:
            p.enable_parallel_projection()
        p.camera.zoom(zoom)
    out = HERE / "out/tie-wrap.png"
    p.screenshot(str(out))
    print(out, f"lean {lean:.1f} deg")


if __name__ == "__main__":
    main()
