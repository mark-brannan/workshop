"""Tests for the DIN-rail bench stand end bracket: bounding box, volume window, rail slots, screw holes, module clearance.

The bracket prints flat: its profile is in XY (x toward the desk's front, y up in use), extruded bracket_t in Z.
"""

import json
import math
import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shapely import affinity
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
S = P["strut"]
FACE_LEN = P["s1"] + P["pitch"] + P["rail_top"]
FOOT0 = np.array([P["top_in"] - S / 2 * math.sin(A) + FACE_LEN * math.cos(A), W / 2])
TOP_Y = (FOOT0 + FACE_LEN * U)[1] + S / 2 * math.cos(A)
FOOT_LEN = P["flat_x"] + P["mod_h"] / 2 + 10


def edge(s):
    return FOOT0 + s * U + (S / 2 - 7.5 - P["cover"]) * N


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
OWN = [SEATS[0], SEATS[2], SEATS[3]]   # the top rail is held by the original's top, not our block
DEPTHS = [P["mod_d"]] * 3 + [P["back_mod_d"]]


@pytest.fixture(scope="module")
def bracket(tmp_path_factory):
    d = tmp_path_factory.mktemp("bracket")
    return trimesh.load(build_scad(HERE / "model.scad", d, "bracket", render=False)["stl"])


def test_one_watertight_piece(bracket):
    assert bracket.is_watertight
    assert len(bracket.split(only_watertight=False)) == 1


def test_bounds(bracket):
    assert np.allclose(bracket.bounds, [[min(0, P["back_x"] - 17.5 - P["block_wall"]), 0, 0], [FOOT_LEN + W / 2, TOP_Y, T]], atol=0.1)


def test_top_is_the_originals(bracket):
    # above the crossbar's bottom the profile is Szmalu's, point for point (szmalu_top.scad, cut from its mesh)
    src = (HERE / "szmalu_top.scad").read_text()
    cut = float(re.search(r"szmalu_top_cut = ([\d.]+);", src).group(1))
    pts = json.loads(re.search(r"points = (\[\[.*?\]\])", src).group(1))
    paths = json.loads(re.search(r"paths = (\[\[.*?\]\])", src).group(1))
    orig = Polygon([pts[i] for i in paths[0]], [[pts[i] for i in r] for r in paths[1:]])
    orig = affinity.translate(orig, 0, TOP_Y)
    grid = [(x, y) for x in np.arange(-0.5, 40, 1.0) for y in np.arange(TOP_Y - cut + 0.5, TOP_Y + 1, 1.0)]
    grid = [q for q in grid if orig.exterior.distance(Point(q)) > 0.2]   # away from the outline, where facets round
    wrong = [q for q in grid if solid(bracket, q) != orig.contains(Point(q))]
    assert not wrong, wrong[:5]


def test_diagonal_joins_the_tier_1_block_below_the_rail_centre(bracket):
    (c1, _), _, _, (cb, _) = SEATS
    j1 = local(c1, N, P["below"], -W / 2)
    k0 = np.array([P["back_x"] + 17.5 + P["block_wall"] - W / 2, W + 7.5 + P["cover"] - W / 2])
    for a_, b_ in ((j1, k0),):
        d = (b_ - a_) / np.linalg.norm(b_ - a_)
        side = np.array([-d[1], d[0]])
        mid = (a_ + b_) / 2
        assert solid(bracket, mid + (W / 2 - P["strip"] / 2) * side) and solid(bracket, mid - (W / 2 - P["strip"] / 2) * side)
    assert P["below"] > 0 and j1[1] < c1[1]


def test_gauge_is_one_rail_block(tmp_path):
    g = trimesh.load(build_scad(HERE / "part-gauge.scad", tmp_path, "gauge", render=False)["stl"])
    assert g.is_watertight
    assert np.allclose(g.extents, [35 + 2 * P["block_wall"], W + 7.5 + P["cover"], P["gauge_t"]], atol=0.1)


def test_volume_window(bracket):
    blocks = 4 * (35 + 2 * P["block_wall"]) * (W + 7.5 + P["cover"])   # rail slots come out of these
    lo = (FOOT_LEN * 2 * P["strip"] + (TOP_Y + FACE_LEN) * S + blocks / 2) * T   # foot ladder, solid post and face
    assert lo < bracket.volume < 1.8 * lo


def test_each_rail_passes_through_and_is_held_between_flat_faces(bracket):
    # the rail's own section is open plastic-free through the plate; a millimetre past the slot either side of the
    # base, and over the lips, is plastic: the rail sits between flat faces, closed round by the block
    rail = Polygon(RAIL).buffer(-0.1)
    for c, out in OWN:
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
    for c, out in OWN:
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
