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


def test_standoff_clears_back_of_board_and_fits_m3(base):
    assert H >= 5 and P["insert_d"] >= 2.5 and P["standoff_d"] - P["insert_d"] >= 3.0


def test_hole_spacing_matches_calipers():
    # short side: outside edge to outside edge 72.3, inside edge to inside edge 65.4 -> holes 3.45, centres 68.85
    # long side: from the inside-edge diagonal 103 (+ one hole = centre diagonal)
    d = (72.3 - 65.4) / 2
    assert np.isclose(P["hole_dy"], (72.3 + 65.4) / 2, atol=0.01)
    assert np.isclose(np.hypot(P["hole_dx"], P["hole_dy"]) - d, 103.0, atol=0.15)
    # holes sit about 1 mm in from the 87 x 75 board's edges (owner, by eye)
    for span, edge in ((P["hole_dx"], 87), (P["hole_dy"], 75)):
        assert 0.7 < (edge - span - d) / 2 < 1.6


def test_four_countersunk_clip_holes_through_the_plate(base):
    xs = [float(v) for v in re.search(r"clip_xs\s*=\s*\[([^\]]*)\]", (HERE / "model.scad").read_text()).group(1).split(",")]
    ys = [float(v) for v in re.search(r"clip_ys\s*=\s*\[([^\]]*)\]", (HERE / "model.scad").read_text()).group(1).split(",")]
    assert len(xs) * len(ys) == 4
    assert abs(ys[0] - ys[1]) == pytest.approx(51, abs=0.01)  # clip span across the rail = the board's short side (Y)
    for x in xs:
        for y in ys:
            assert hits(base, x, y) == [] and len(hits(base, x + 2.5, y)) > 0  # open through the shank; solid just beside it


CLIP_STL = HERE.parent / "din-rail-psu-mount" / "ref_din_clip_heat_insert.stl"
# the clip turned, not mirrored: its x (hook 5, latch 56) along -Y, its flat face on the plate's back, body toward the rail
CLIP_PLACE = "multmatrix([[0,-1,0,{x}],[-1,0,0,27.05],[0,0,-1,0],[0,0,0,1]])"


def test_clips_seat_on_the_back_and_their_holes_line_up_with_the_plate(base, tmp_path):
    from shop.testing import seated_overlap

    clip = trimesh.load(CLIP_STL)
    xs = [float(v) for v in re.search(r"clip_xs\s*=\s*\[([^\]]*)\]", (HERE / "model.scad").read_text()).group(1).split(",")]
    for x in xs:
        assert seated_overlap(tmp_path, base, clip, CLIP_PLACE.format(x=x)) < 0.01
        # a clip seated one plate-thickness off the face, or the wrong way round, would not touch: it must touch the back
        placed = clip.copy()
        placed.apply_transform([[0, -1, 0, x], [-1, 0, 0, 27.05], [0, 0, -1, 0], [0, 0, 0, 1]])
        assert np.isclose(placed.bounds[1][2], 0, atol=0.02)
        for y in (22.05, -28.95):  # the plate's screw holes land on the clip's insert holes: open all the way down through both
            assert ray_hits(placed, (x, y, 20), (0, 0, -1)) == [] or ray_hits(placed, (x, y, 20), (0, 0, -1))[0][2] < 0.01
            assert len(ray_hits(placed, (x + 2.5, y, 20), (0, 0, -1))) > 0
