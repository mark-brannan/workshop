"""Tests for the ESP32 breakout mount: bounding box, volume window, feature counts."""

import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")


def params(path: Path) -> dict[str, float]:
    return {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", path.read_text(), re.M)}


P = params(HERE / "model.scad")
L, W, T, H = P["plate_l"], P["plate_w"], P["plate_t"], P["standoff_h"]


@pytest.fixture(scope="module")
def base(tmp_path_factory):
    d = tmp_path_factory.mktemp("esp")
    src = d / "model.scad"
    src.write_text((HERE / "model.scad").read_text())
    return trimesh.load(build_scad(src, d, "base", render=False)["stl"])


def hits(mesh, x, y, down=True):
    z, dz = (50, -1) if down else (-50, 1)
    return ray_hits(mesh, (x, y, z), (0, 0, dz))


def test_bounds_and_watertight(base):
    assert base.is_watertight
    assert np.allclose(base.bounds, [[-L / 2, -W / 2, 0], [L / 2, W / 2, T + H]], atol=0.02)


def test_four_standoffs_with_blind_insert_holes(base):
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * P["hole_dx"] / 2, sy * P["hole_dy"] / 2
            h = hits(base, x, y)
            # rim-less first hit is the bottom of the insert hole, inside the plate
            assert np.isclose(h[0][2], T + H - P["insert_depth"], atol=0.02)
            assert T + H - P["insert_depth"] > 0.5  # never breaks through the underside
            # the standoff body is there, off-axis
            assert np.isclose(hits(base, x + P["insert_d"] / 2 + 0.5, y)[0][2], T + H, atol=0.02)


def test_standoff_clears_back_of_board_and_fits_m2(base):
    assert H >= 5 and P["insert_d"] >= 1.6 and P["standoff_d"] - P["insert_d"] >= 2.5


def test_four_blind_peg_holes_from_underside(base):
    for sx in (-1, 1):
        for py in (5.9 - 20.745, 35.9 - 20.745):
            h = hits(base, sx * P["clip_x"], py, down=False)
            assert np.isclose(h[0][2], P["peg_hole_depth"], atol=0.02)
