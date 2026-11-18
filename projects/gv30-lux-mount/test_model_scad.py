"""Tests for the GV30 split ring and its cover: bounding box, volume window, the split, the sensor pocket and skin."""

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
def body():
    return run("body")


@pytest.fixture(scope="module")
def cover():
    return run("cover")


def test_body(body):
    lo, hi = body.bounds
    assert lo[0] == pytest.approx(-P["od"] / 2, abs=0.1) and hi[0] == pytest.approx(P["reach"] + P["head_d"] / 2, abs=0.1)
    assert hi[2] - lo[2] == pytest.approx(P["h"], abs=0.05)
    assert body.is_watertight and 7000 < body.volume < 14000
    assert not ray_hits(body, [0, 0, -5], UP), "bore clear over the stub"
    for x in (P["id"] / 2 + 1, P["reach"], P["reach"] + P["head_d"] / 2 - 1):
        assert not ray_hits(body, [x, 0, -5], UP), f"split open at x = {x}"


def test_pocket_and_recess(body):
    floor = P["h"] - P["cover_t"] - P["pocket"]
    assert ray_hits(body, [P["reach"], 5, P["h"] + 5], [0, 0, -1])[0][2] == pytest.approx(floor, abs=0.05)
    # recess over the arm, ring wall stays full height
    assert ray_hits(body, [P["od"] / 2 + 3, 5, P["h"] + 5], [0, 0, -1])[0][2] == pytest.approx(P["h"] - P["cover_t"], abs=0.05)
    assert ray_hits(body, [-P["od"] / 2 + 1, 0, P["h"] + 5], [0, 0, -1])[0][2] == pytest.approx(P["h"], abs=0.05)


def test_cover(cover):
    assert cover.extents[2] == pytest.approx(P["cover_t"], abs=0.05)
    assert cover.is_watertight and 1000 < cover.volume < 3500
    assert ray_hits(cover, [P["reach"], 0, -5], UP)[0][2] == pytest.approx(P["cover_t"] - P["skin"], abs=0.05), "skin"
