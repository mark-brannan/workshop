"""Tool caddy long layout: massing study bounds (mm)."""
from pathlib import Path

import pytest
import pyvista as pv

STL = Path(__file__).parent / "out" / "tool-caddy_scad.stl"


def test_bounds_and_volume():
    m = pv.read(STL)
    x0, x1, y0, y1, z0, z1 = m.bounds
    assert (x1 - x0, y1 - y0) == (pytest.approx(411.1, abs=0.1), pytest.approx(191.6, abs=0.2))
    assert 115 < z1 < 130
    assert 700_000 < m.volume < 850_000
