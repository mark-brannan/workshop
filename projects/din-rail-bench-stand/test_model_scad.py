"""Tests for the DIN-rail bench stand end bracket: bounding box, volume window, rail slots, screw holes, module clearance.

The bracket prints flat: its profile is in XY (x toward the desk's front, y up in use), extruded bracket_t in Z.
"""

import math
import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shapely.geometry import Point, Polygon
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
FOOT0 = np.array([W / 2 + P["face_shift"] + FACE_LEN * math.cos(A), W / 2])
TOP = FOOT0 + FACE_LEN * U
FOOT_LEN = P["flat_x"] + P["mod_h"] / 2 + 10


def edge(s):
    return FOOT0 + s * U + (W / 2) * N


UP = np.array([0.0, 1.0])
SEATS = [(edge(P["s1"]), N), (edge(P["s1"] + P["pitch"]), N), (np.array([P["flat_x"], W]), UP),
         (np.array([P["back_x"], W]), UP)]
RAIL = [(-17.5, 7.5), (-17.5, 6.5), (-12.5, 6.5), (-12.5, 0), (12.5, 0), (12.5, 6.5), (17.5, 6.5), (17.5, 7.5),
        (11.5, 7.5), (11.5, 1), (-11.5, 1), (-11.5, 7.5)]   # TS35, base on y = 0, lips out at y = 7.5


def local(c, out, x, y):
    """Seat-local (x across the rail's width, y out of the rail) to profile coordinates."""
    return c + x * np.array([out[1], -out[0]]) + y * out


def solid(bracket, pt):
    return len(ray_hits(bracket, (pt[0], pt[1], T + 5), (0, 0, -1))) > 0
DEPTHS = [P["mod_d"]] * 3 + [P["back_mod_d"]]


@pytest.fixture(scope="module")
def bracket(tmp_path_factory):
    d = tmp_path_factory.mktemp("bracket")
    return trimesh.load(build_scad(HERE / "model.scad", d, "bracket", render=False)["stl"])


def test_one_watertight_piece(bracket):
    assert bracket.is_watertight
    assert len(bracket.split(only_watertight=False)) == 1


def test_bounds(bracket):
    assert np.allclose(bracket.bounds, [[0, 0, 0], [FOOT_LEN + W / 2, TOP[1] + W / 2, T]], atol=0.1)


def test_gauge_is_one_rail_block(tmp_path):
    g = trimesh.load(build_scad(HERE / "part-gauge.scad", tmp_path, "gauge", render=False)["stl"])
    assert g.is_watertight
    assert np.allclose(g.extents, [35 + 2 * P["block_wall"], W + 7.5 + P["cover"], P["gauge_t"]], atol=0.1)


def test_volume_window(bracket):
    bars = FOOT_LEN + TOP[1] + FACE_LEN + TOP[0]  # foot, back post, face, top bar centrelines
    lo = bars * 2 * P["strip"] * T     # two strips per ladder bar; rungs, strut and rail blocks add to this
    assert lo < bracket.volume < 1.8 * lo


def test_each_rail_passes_through_and_is_held_between_flat_faces(bracket):
    # the rail's own section is open plastic-free through the plate; a millimetre past the slot either side of the
    # base, and over the lips, is plastic: the rail sits between flat faces, closed round by the block
    rail = Polygon(RAIL).buffer(-0.1)
    for c, out in SEATS:
        x0, y0, x1, y1 = rail.bounds
        pts = [(x, y) for x in np.arange(x0, x1, 0.5) for y in np.arange(y0, y1, 0.25) if rail.contains(Point(x, y))]
        hit = [p for p in pts if solid(bracket, local(c, out, *p))]
        assert not hit, f"plastic in the rail's way at seat {c}: {hit[:3]}"
        clr = P["rail_clr"] + 1
        for x in (-20, -6, 6, 20):    # under the base and lips, and the block's outer face over the lips
            assert solid(bracket, local(c, out, x * 0.5 if abs(x) < 10 else x, -clr))
        for x in (-6, 6):             # the tongue of plastic in the rail's channel, over the base
            assert solid(bracket, local(c, out, x, 1 + clr))
        for x in (-15, 15):
            assert solid(bracket, local(c, out, x, 7.5 + clr))


def test_screw_hole_runs_through_the_cover_and_rail_base_into_a_pilot(bracket):
    for c, out in SEATS:
        o = local(c, out, 0, 7.5 + P["cover"] + 5)
        h = ray_hits(bracket, (o[0], o[1], T / 2), (-out[0], -out[1], 0))
        assert len(h), "the screw hole has no bottom"
        assert np.linalg.norm(h[0][:2] - o) > 5 + 7.5 + P["cover"] + P["pilot_depth"] - 0.5
        q = local(c, out, 0, -P["pilot_depth"] / 2)    # pilot narrower than the clearance: plastic 2 mm off its axis
        assert solid(bracket, local(c, out, 2.1, -P["pilot_depth"] / 2))
        assert solid(bracket, q) and len(ray_hits(bracket, (q[0], q[1], T + 5), (0, 0, -1))) == 4


def envelope(c, out, d, d0=0.0):
    """A module's side outline, from d0 to d out from the rail's base."""
    along = np.array([out[1], -out[0]])
    h = P["mod_h"] / 2
    return Polygon([c + k * h * along + d0 * out for k in (-1, 1)] + [c + k * h * along + d * out for k in (1, -1)])


def test_module_envelopes_clear_each_other():
    # modules sit on the rails between the brackets, so only their spacing matters, not the frame
    t1, t2, fl, bk = (envelope(c, o, d) for (c, o), d in zip(SEATS, DEPTHS))
    assert t1.distance(fl) >= 10   # room for the flat module's back wiring and a finger
    assert t1.distance(t2) >= 10
    assert bk.distance(t1) >= 10
