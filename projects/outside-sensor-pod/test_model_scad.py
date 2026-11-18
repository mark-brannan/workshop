"""Tests for the outside sensor pod: bounding box, volume window and feature counts for the louvre, cap and base."""

import re
import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")
P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
POSTS = [(P["post_r"] * c, P["post_r"] * s) for c, s in ((0, 1), (-0.8660254, -0.5), (0.8660254, -0.5))]
UP = [0, 0, 1]


def run(part: str) -> trimesh.Trimesh:
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl, "-D", f'part="{part}"')
        mesh = trimesh.load(stl)
    osc.cleanup()
    return mesh


@pytest.fixture(scope="module")
def louvre():
    return run("louvre")


@pytest.fixture(scope="module")
def cap():
    return run("cap")


@pytest.fixture(scope="module")
def base():
    return run("base")


def test_louvre(louvre):
    x, y, z = louvre.extents
    assert x == pytest.approx(2 * P["out_r"], abs=0.1) and y == pytest.approx(2 * P["out_r"], abs=0.1)
    assert z == pytest.approx(P["drop"], abs=0.05)
    assert louvre.is_watertight and 12000 < louvre.volume < 17000
    assert not ray_hits(louvre, [0, 0, -5], UP), "cavity is open"
    for px, py in POSTS:
        assert not ray_hits(louvre, [px, py, -5], UP), "rod hole"
    assert ray_hits(louvre, [-P["post_r"], 0, -5], UP), "flat ring between the posts"


def test_louvres_overlap_and_breathe():
    assert 0 < P["drop"] - P["pitch"] <= 2, "skirt tip sits below the next plate's top: no level line of sight"
    run_out = P["out_r"] - P["flat_r"]
    assert (run_out - (P["drop"] - P["pitch"])) / 2**0.5 > 6, "air channel between skirts, mm"
    assert (P["drop"] - P["plate_t"]) / run_out <= 1.0, "skirt no steeper than 45 degrees off the bed"


def test_cap(cap):
    x, _, z = cap.extents
    assert x == pytest.approx(2 * P["out_r"], abs=0.1) and z == pytest.approx(P["drop"], abs=0.05)
    assert cap.is_watertight and 20000 < cap.volume < 30000
    assert not ray_hits(cap, [0, 0, -5], UP), "light aperture"
    assert len(ray_hits(cap, [P["win_ap"] / 2 + 2, 0, -5], UP)) == 2, "window seat floor, cap_t thick"
    assert ray_hits(cap, [P["cav_r"] - 3, 0, -5], UP), "closed over the cavity"
    for px, py in POSTS:
        assert not ray_hits(cap, [px, py, -5], UP), "rod hole"


def test_base(base):
    (x0, y0, z0), (x1, y1, z1) = base.bounds
    assert (x0, x1) == pytest.approx((-P["flat_r"], P["tongue_l"]), abs=0.1)
    assert y1 - y0 == pytest.approx(2 * P["flat_r"], abs=0.1)
    assert (z0, z1) == pytest.approx((0, P["base_t"] + P["fin_h"]), abs=0.05)
    assert base.is_watertight and 30000 < base.volume < 45000
    for px, py in POSTS:
        assert not ray_hits(base, [px, py, -5], UP), "rod hole"
    for sy in (-1, 1):
        assert not ray_hits(base, [P["slot_x"], sy * P["slot_dy"] / 2, -5], UP), "mount slot"
    hole_y = -(P["board_w"] / 2 - P["hole_inset"])
    for sz in (-1, 1):
        zc = P["board_z"] + sz * P["hole_pitch"] / 2
        assert not ray_hits(base, [-20, hole_y, zc], [1, 0, 0]), "board screw hole through the fin"
        assert len(ray_hits(base, [-20, hole_y + 2.2, zc], [1, 0, 0])) == 2, "standoff around it"


def test_stack_fits_the_boards():
    cap_inner = P["base_t"] + P["boss_h"] + P["pitch"] * (P["n_louvres"] + 1) - P["cap_t"] - P["collar_h"]
    assert P["base_t"] + P["fin_h"] < cap_inner - 5, "fin top clear of the window collar"
    assert P["board_z"] - 12.7 > P["base_t"] + 20, "board's lower end above the gussets"
    reach = ((P["fin_t"] / 2 + P["standoff"] + 5) ** 2 + (P["board_w"] / 2) ** 2) ** 0.5
    assert reach < P["cav_r"] - 5, "board corners clear of the cavity wall"
