"""Tests for the photocell flame pod: bounding box, volume window, feature counts."""

import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shapely.geometry import LinearRing, Point
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits, seated_overlap

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
LEAD_L = P["solder_out"]  # lead = "solder", the default; potted = true
EXIT_X = P["cell_end"] + P["board_l"] + LEAD_L + P["cable_d"] / 2
IN_L = EXIT_X + P["cable_d"] / 2 + P["end_clear"]
IN_W = P["board_w"] + 2 * P["fit"]
OUT_L, OUT_W = IN_L + 2 * P["wall"], IN_W + 2 * P["wall"]
BOARD_Z = P["floor_t"] + P["ledge"]
BOARD_TOP = BOARD_Z + P["board_t"]
POUR_Z = BOARD_TOP + P["pour_above"]
SHELL_H = BOARD_TOP + P["pot_h"] + P["pot_clear"]
CABLE_Z = BOARD_TOP + P["pin_z"]
HOLE_X = P["cell_end"] + P["board_l"] - P["hole_from_hdr"]


def build(tmp_path_factory, src, name, two_d=False):
    d = tmp_path_factory.mktemp(name)
    for f in ("model.scad", "part-lid.scad", "part-cover.scad"):
        (d / f).write_text((HERE / f).read_text())
    (d / "art").mkdir()
    (d / "art/fire-glyph.scad").write_text((HERE / "art/fire-glyph.scad").read_text())
    return trimesh.load(build_scad(d / src, d, name, two_d=two_d, render=False)["stl"])


@pytest.fixture(scope="module")
def shell(tmp_path_factory):
    return build(tmp_path_factory, "model.scad", "shell")


@pytest.fixture(scope="module")
def lid(tmp_path_factory):
    return build(tmp_path_factory, "part-lid.scad", "lid", two_d=True)


@pytest.fixture(scope="module")
def cover(tmp_path_factory):
    """The cover mesh as printed, turned back into its use pose on the shell (x, -y, Z - z)."""
    m = build(tmp_path_factory, "part-cover.scad", "cover")
    T = np.diag([1.0, -1.0, -1.0, 1.0])
    T[2, 3] = SHELL_H + P["cover_t"]
    return m.apply_transform(T)


def down(mesh, x, y):
    return ray_hits(mesh, (x, y, 60), (0, 0, -1))


def test_shell_bounds_volume(shell):
    assert shell.is_watertight
    x0, x1 = -P["wall"] - P["tab_l"], IN_L + P["wall"] + P["tab_l"]
    y0 = -OUT_W / 2
    assert np.allclose(shell.bounds, [[x0, y0, 0], [x1, OUT_W / 2, SHELL_H]], atol=0.05)
    assert 3_800 < shell.volume < 5_200


def test_potting_covers_cable_leaves_trimpot_and_cell_proud():
    assert POUR_Z > CABLE_Z + P["cable_d"] / 2 + 0.4  # the cable entry is sealed
    assert BOARD_TOP + P["pot_h"] > POUR_Z + 0.4  # the trimpot top stays out of the epoxy, adjustable
    assert SHELL_H - (BOARD_TOP + P["pot_h"]) >= 0.2  # the rim stands over the trimpot: the cover closes
    assert SHELL_H - POUR_Z >= 0.5  # a dam for the pour
    assert BOARD_TOP + P["cell_h"] - P["cell_t"] > SHELL_H + P["cover_t"] + 2  # the cell body clears the cover


def test_board_rests_on_ledges_and_boss(shell):
    y_ledge = IN_W / 2 - P["fit"] - P["ledge_lip"] / 2
    for y in (-y_ledge, y_ledge):
        assert np.isclose(down(shell, P["cell_end"] + P["board_l"] / 2, y)[0][2], BOARD_Z, atol=0.02)
    x_bare = P["cell_end"] + P["seat_l"] + 1
    assert np.isclose(down(shell, x_bare, y_ledge)[0][2], P["floor_t"], atol=0.02)  # bare past the corner seats
    assert np.isclose(down(shell, x_bare, 0)[0][2], P["floor_t"], atol=0.02)  # and mid-board under the cell leads


def test_photocell_end_seats_and_stops(shell):
    """Both photocell-end corners: a seat under the board, a stop past its end standing over the board top."""
    y_ledge = IN_W / 2 - P["fit"] - P["ledge_lip"] / 2
    for y in (-y_ledge, y_ledge):
        assert np.isclose(down(shell, P["cell_end"] + P["seat_l"] / 2, y)[0][2], BOARD_Z, atol=0.02)
        assert np.isclose(down(shell, P["cell_end"] - P["fit"] - 0.5, y)[0][2], BOARD_TOP + P["stop_h"], atol=0.02)
    assert np.isclose(down(shell, P["cell_end"] - 1, 0)[0][2], P["floor_t"], atol=0.02)  # clear under the cell body
    stop_face = ray_hits(shell, (P["cell_end"] + 1, y_ledge, BOARD_Z + P["board_t"] / 2), (-1, 0, 0))[0][0]
    assert np.isclose(stop_face, P["cell_end"] - P["fit"], atol=0.02)  # the board end stops 'fit' short of it
    assert np.isclose(down(shell, HOLE_X + P["boss_d"] / 2 - 0.3, 0)[0][2], BOARD_Z, atol=0.02)


def test_locating_pin_through_board_hole_no_floor_hole(shell):
    assert np.isclose(down(shell, HOLE_X, 0)[0][2], BOARD_TOP, atol=0.02)
    assert P["locate_d"] < 4 - 0.4  # board hole ~4
    assert len(down(shell, HOLE_X, 0)) == 2  # pin top and the underside: solid, no leak for the pour


def test_cable_exits_side_wall_clear_of_tabs(shell):
    hits = ray_hits(shell, (EXIT_X, -OUT_W, CABLE_Z), (0, 1, 0))
    assert hits[0][1] > 0  # nothing in the -Y wall at cable height: first hit is across the shell
    assert CABLE_Z - P["cable_d"] / 2 > BOARD_Z  # round bottom stays above the board underside
    assert EXIT_X + P["cable_d"] / 2 < IN_L  # inside the end wall, not over the end tab
    assert EXIT_X - P["cable_d"] / 2 > P["cell_end"] + P["board_l"] + LEAD_L - 0.01  # past the heatshrink


def test_two_mounting_tab_holes(shell):
    for x in (-P["wall"] - P["tab_l"] / 2, IN_L + P["wall"] + P["tab_l"] / 2):
        assert len(down(shell, x, 0)) == 0
        assert np.isclose(down(shell, x + P["tab_hole"] / 2 + 0.5, 0)[0][2], P["tab_t"], atol=0.02)


def test_lid_outline_and_two_holes(lid):
    assert lid.is_watertight
    assert np.allclose(lid.bounds, [[-P["wall"], -OUT_W / 2, 0], [IN_L + P["wall"], OUT_W / 2, P["lid_t"]]], atol=0.02)
    ci = P["col_in"]
    assert len(down(lid, ci, -(IN_W / 2 - ci))) == 0 and len(down(lid, IN_L - ci, IN_W / 2 - ci)) == 0
    assert len(down(lid, ci, IN_W / 2 - ci)) > 0  # the other diagonal is solid
    # hole edge at least 2 mm from the lid's edge
    assert ci + P["wall"] - P["lid_hole_d"] / 2 >= 2


def test_cover_printed_mesh_fits_shell(cover, shell):
    """On the printed mesh in its use pose: hole over the cell, notch over the cable, lip in the groove."""
    assert cover.is_watertight
    z_top = SHELL_H + P["cover_t"]
    assert np.isclose(cover.bounds[1][2], z_top, atol=0.02)
    assert np.isclose(cover.bounds[0][2], SHELL_H - P["skirt_h"], atol=0.02)
    cell_x = P["cell_end"] + P["cell_x_on"]
    for dx in (0, P["cell_d"] / 2 + 0.5):  # nothing over the cell, with room round it
        assert len(down(cover, cell_x + dx, 0)) == 0
    assert len(down(cover, P["cell_end"] + 20, 0)) == 2  # closed over the board and trimpot
    z = SHELL_H - 1
    assert ray_hits(cover, (EXIT_X, -OUT_W, z), (0, 1, 0))[0][1] > 0  # notch at the cable, -Y side
    assert ray_hits(cover, (EXIT_X, OUT_W, z), (0, -1, 0))[0][1] > 0  # the +Y skirt is whole: one way round only
    assert ray_hits(cover, (20, -OUT_W, z), (0, 1, 0))[0][1] < -OUT_W / 2  # skirt elsewhere
    lip_z = SHELL_H - P["skirt_h"] + 0.3 + P["cover_gap"] + P["catch"]
    for s in (-1, 1):
        lip_tip = min(abs(h[1]) for h in ray_hits(cover, (20, s * OUT_W, lip_z), (0, -s, 0)) if abs(h[1]) < OUT_W / 2 + 0.1)
        groove_tip = abs(ray_hits(shell, (20, s * OUT_W, lip_z), (0, -s, 0))[0][1])
        assert groove_tip < lip_tip < OUT_W / 2 - 0.3  # the lip reaches into the groove, short of its root
    for s, x_mid in ((-1, -P["wall"]), (1, IN_L + P["wall"])):  # both end walls, the header end beside the cable notch
        x_c = IN_L / 2
        out = abs(x_mid - x_c)
        lip_tip = min(abs(h[0] - x_c) for h in ray_hits(cover, (x_c + s * 2 * OUT_L, 0, lip_z), (-s, 0, 0)) if abs(h[0] - x_c) < out + 0.1)
        groove_tip = abs(ray_hits(shell, (x_c + s * 2 * OUT_L, 0, lip_z), (-s, 0, 0))[0][0] - x_c)
        assert groove_tip < lip_tip < out - 0.3
        assert abs(ray_hits(cover, (x_c + s * 2 * OUT_L, P["catch_y"] / 2 + 1, lip_z), (-s, 0, 0))[0][0] - x_c) > out  # lip ends mid-wall


def test_printed_cover_turned_over_fits_printed_shell(shell, cover, tmp_path):
    # the printed meshes in the pose they are used; the cover fixture has already turned the print over about X
    place = "translate([0, 0, 0])"
    assert seated_overlap(tmp_path, shell, cover, place) < 0.01
    assert seated_overlap(tmp_path, shell, cover, place, mirror="[1, 0, 0]") > 1  # the test sees a cover put on wrong


def test_cover_fire_glyph_groove_reads_from_above(cover):
    """On the printed cover in its use pose: a 90° V groove round the glyph, the right way round, not mirrored."""
    pts = re.findall(r"\[(-?[\d.]+), (-?[\d.]+)\]", (HERE / "art/fire-glyph.scad").read_text())
    pts = np.array(pts, float)
    z_top = SHELL_H + P["cover_t"]
    depth = P["groove_w"] / 2
    cell_x = P["cell_end"] + P["cell_x_on"]
    glyph_x = (cell_x + P["cell_hole_d"] / 2 + IN_L + P["wall"] + P["cover_gap"] + P["skirt_t"]) / 2 - P["glyph_bias"]
    to_use = lambda p: (glyph_x - P["glyph_h"] * p[1], P["glyph_h"] * p[0])  # rotate(90): tip toward -X, the cell
    ring = LinearRing(pts)
    far = sorted(pts, key=lambda p: -ring.distance(Point(-p[0], p[1])))[:3]  # outline points whose mirror is off it
    assert ring.distance(Point(-far[-1][0], far[-1][1])) * P["glyph_h"] > 2 * depth
    for p in far:
        x, y = to_use(p)
        assert np.isclose(down(cover, x, y)[0][2], z_top - depth, atol=0.08)  # at the V's apex
        assert np.isclose(down(cover, x, -y)[0][2], z_top, atol=0.02)  # the mirrored glyph would put it on plain face
    assert np.isclose(down(cover, glyph_x, 0)[0][2], z_top, atol=0.02)  # the glyph itself stands at the face
    assert P["cover_t"] - depth >= 0.8  # plate left under the groove
    half_w = OUT_W / 2 + P["cover_gap"] + P["skirt_t"]
    assert half_w - P["glyph_h"] * np.abs(pts[:, 0]).max() - depth >= 2.5  # margin to the plate's long edges
    tip_x = glyph_x - P["glyph_h"] * pts[:, 1].max()
    assert tip_x - depth - (cell_x + P["cell_hole_d"] / 2) >= 2.5  # and to the cell hole
