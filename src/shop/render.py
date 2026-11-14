"""Headless PNG rendering of a mesh file (STL) with pyvista/VTK off-screen.

On this machine pyvista renders off-screen without an X server; if the
backend is missing it raises, and export_all records the failure rather
than aborting the geometry exports.
"""

from __future__ import annotations

import os
from pathlib import Path

COLOR = "#b9a6d9"

# label -> (direction the camera sits in, view-up, orthographic). X is right in top/front/bottom;
# the isos sit on the -Y side (front) unless named otherwise, so -Y is nearest the viewer, as in the top view.
VIEWS = {
    "top": ((0, 0, 1), (0, 1, 0), True),
    "bottom": ((0, 0, -1), (0, -1, 0), True),
    "front (-Y)": ((0, -1, 0), (0, 0, 1), True),
    "back (+Y)": ((0, 1, 0), (0, 0, 1), True),
    "left (-X)": ((-1, 0, 0), (0, 0, 1), True),
    "right (+X)": ((1, 0, 0), (0, 0, 1), True),
    "iso front-right": ((1, -1, 0.9), (0, 0, 1), False),
    "iso front-left": ((-1, -1, 0.9), (0, 0, 1), False),
    "iso underside": ((1, -1, -0.9), (0, 0, 1), False),
}


def _add(p, mesh):
    """The part, plus dark crease lines so same-facing faces at different heights stay readable."""
    p.add_mesh(mesh, color=COLOR, smooth_shading=False, show_edges=False)
    p.add_mesh(mesh.extract_feature_edges(feature_angle=30), color="#2a2a2a", line_width=2)


def _look(p, vec, up, ortho):
    p.view_vector(vec, viewup=up)
    p.reset_camera()
    if ortho:
        p.enable_parallel_projection()


def _plotter(shape, window_size):
    import pyvista as pv

    pv.OFF_SCREEN = True
    return pv.Plotter(off_screen=True, shape=shape, window_size=window_size, border=True)


def render_png(mesh_path: Path, png_path: Path, *, views: bool = True, size: int = 600) -> list[Path]:
    """Render ``mesh_path`` (STL/3MF/OBJ) to ``png_path`` (front-right isometric).

    With ``views=True`` also writes ``<stem>_views.png``: a labelled 3x3 contact sheet of top, bottom,
    front, back, left, right and three isos. Returns the list of PNG paths written.
    """
    os.environ.setdefault("PYVISTA_OFF_SCREEN", "true")
    import pyvista as pv

    mesh = pv.read(str(mesh_path))
    written: list[Path] = []

    p = _plotter(shape=(1, 1), window_size=(size, size))
    _add(p, mesh)
    p.add_axes()
    _look(p, *VIEWS["iso front-right"])
    p.screenshot(str(png_path))
    p.close()
    written.append(png_path)

    if views:
        views_path = png_path.with_name(png_path.stem + "_views.png")
        p = _plotter(shape=(3, 3), window_size=(size * 3, size * 3))
        for i, (label, (vec, up, ortho)) in enumerate(VIEWS.items()):
            p.subplot(i // 3, i % 3)
            _add(p, mesh)
            p.add_text(label, font_size=12)
            _look(p, vec, up, ortho)
        p.screenshot(str(views_path))
        p.close()
        written.append(views_path)
    return written
