"""Headless PNG rendering of a mesh file (STL) with pyvista/VTK off-screen.

On this machine pyvista renders off-screen without an X server; if the
backend is missing it raises, and export_all records the failure rather
than aborting the geometry exports.
"""

from __future__ import annotations

import os
from pathlib import Path

VIEWS = {
    "iso": "iso",
    "top": "xy",
    "front": "xz",
    "right": "yz",
}


def _plotter(shape, window_size):
    import pyvista as pv

    pv.OFF_SCREEN = True
    return pv.Plotter(off_screen=True, shape=shape, window_size=window_size, border=True)


def render_png(mesh_path: Path, png_path: Path, *, views: bool = True, size: int = 600) -> list[Path]:
    """Render ``mesh_path`` (STL/3MF/OBJ) to ``png_path`` (isometric view).

    With ``views=True`` also writes ``<stem>_views.png``: a 2x2 of iso/top/front/right.
    Returns the list of PNG paths written.
    """
    os.environ.setdefault("PYVISTA_OFF_SCREEN", "true")
    import pyvista as pv

    mesh = pv.read(str(mesh_path))
    written: list[Path] = []

    p = _plotter(shape=(1, 1), window_size=(size, size))
    p.add_mesh(mesh, color="#c8a24a", smooth_shading=False, show_edges=False)
    p.add_axes()
    p.view_isometric()
    p.screenshot(str(png_path))
    p.close()
    written.append(png_path)

    if views:
        views_path = png_path.with_name(png_path.stem + "_views.png")
        p = _plotter(shape=(2, 2), window_size=(size * 2, size * 2))
        for i, (label, cam) in enumerate(VIEWS.items()):
            p.subplot(i // 2, i % 2)
            p.add_mesh(mesh, color="#c8a24a", show_edges=False)
            p.add_text(label, font_size=12)
            if cam == "iso":
                p.view_isometric()
            else:
                p.camera_position = cam
                p.enable_parallel_projection()
        p.screenshot(str(views_path))
        p.close()
        written.append(views_path)
    return written
