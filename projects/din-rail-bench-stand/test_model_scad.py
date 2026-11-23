"""Tests for the DIN-rail bench stand end bracket: bounding box, volume window, pilot holes, module clearance.

The bracket prints flat: its profile is in XY (x toward the desk's front, y up in use), extruded bracket_t in Z.
"""

import math
import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shapely.geometry import Polygon
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
A = math.radians(P["a"])
W, T = P["bar_w"], P["bracket_t"]
U = np.array([-math.cos(A), math.sin(A)])
N = np.array([math.sin(A), math.cos(A)])
FACE_LEN = P["s1"] + P["pitch"] + P["mod_h"] / 2 + P["face_over"]
FOOT0 = np.array([W / 2 + FACE_LEN * math.cos(A), W / 2])
TOP = FOOT0 + FACE_LEN * U
FOOT_LEN = P["flat_x"] + P["mod_h"] / 2 + 10


def edge(s):
    return FOOT0 + s * U + (W / 2) * N


SEATS = [(edge(P["s1"]), N), (edge(P["s1"] + P["pitch"]), N), (np.array([P["flat_x"], P["flat_pad"]]), np.array([0.0, 1.0]))]


@pytest.fixture(scope="module")
def bracket(tmp_path_factory):
    d = tmp_path_factory.mktemp("bracket")
    return trimesh.load(build_scad(HERE / "model.scad", d, "bracket", render=False)["stl"])


def test_one_watertight_piece(bracket):
    assert bracket.is_watertight
    assert len(bracket.split(only_watertight=False)) == 1


def test_bounds(bracket):
    assert np.allclose(bracket.bounds, [[0, 0, 0], [FOOT_LEN + W / 2, TOP[1] + W / 2, T]], atol=0.1)


def test_volume_window(bracket):
    bars = FOOT_LEN + TOP[1] + FACE_LEN  # foot, back post, face centrelines
    lo = bars * W * T                    # struts and pads only add to this
    assert lo < bracket.volume < 1.6 * lo


def test_three_pilot_holes_open_on_the_rail_edge(bracket):
    # a print-vertical ray 8 mm into each hole crosses plastic, hole, plastic: 4 hits; 2 mm beside the hole: 2
    for c, out in SEATS:
        p = c - 8 * out
        assert len(ray_hits(bracket, (p[0], p[1], T + 5), (0, 0, -1))) == 4
        side = p + 4 * np.array([out[1], -out[0]])
        assert len(ray_hits(bracket, (side[0], side[1], T + 5), (0, 0, -1))) == 2
    # the hole opens on the edge: a ray in along the hole axis from outside meets nothing for the hole's depth
    for c, out in SEATS:
        o = c + 5 * out
        h = ray_hits(bracket, (o[0], o[1], T / 2), (-out[0], -out[1], 0))
        assert not len(h) or np.linalg.norm(h[0][:2] - o) > 5 + P["pilot_depth"] - 0.5


def envelope(c, out):
    along = np.array([out[1], -out[0]])
    h, d = P["mod_h"] / 2, P["mod_d"]
    return Polygon([c + k * h * along for k in (-1, 1)] + [c + k * h * along + d * out for k in (1, -1)])


def test_module_envelopes_clear_each_other_and_the_frame():
    t1, t2, fl = (envelope(c, o) for c, o in SEATS)
    assert t1.distance(fl) >= 10   # room for the flat module's back wiring and a finger
    assert t1.distance(t2) >= 10
