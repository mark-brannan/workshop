"""Tests for the tube-top lux capsule: each printed part's bounding box, volume window and watertightness."""

import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

# (view, exit) -> (extents x, y, z in mm, volume window in mm^3), measured from the 2026-11-20 build
PARTS = {
    ("cap_print", "center"): ((34.0, 34.0, 15.7), (6000, 7200)),
    ("cap_print", "side"): ((34.0, 34.0, 15.7), (5800, 7000)),
    ("riser_print", "center"): ((25.0, 25.0, 9.5), (1250, 1500)),
    ("riser_print", "side"): ((25.0, 25.0, 9.5), (1200, 1450)),
    ("base_print", "center"): ((39.3, 43.1, 17.0), (3900, 4700)),
    ("base_print", "side"): ((39.3, 43.1, 17.0), (4000, 4800)),
}


@pytest.mark.parametrize("view,exit_", PARTS)
def test_part(view, exit_):
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl, "-D", f'view="{view}"', "-D", f'exit="{exit_}"')
        mesh = trimesh.load(stl)
    osc.cleanup()
    extents, (vmin, vmax) = PARTS[(view, exit_)]
    assert mesh.extents == pytest.approx(extents, abs=0.5)
    assert mesh.is_watertight and vmin < mesh.volume < vmax
