"""Tests for the one-piece DIN-rail PSU mount: bounding box, volume window, feature counts.

Features are counted by vertical ray probes through the STL.
"""

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
L, W, T, EXT = P["plate_l"], P["plate_w"], P["plate_t"], P["ext"]
TIE_Y = -W / 2 - EXT / 2
SH_LEN = P["shelf_len"]
SH_X0 = -L / 2 + 8.5  # shelf starts 8.5 mm in from the left edge
TIE_XS = [SH_X0 + SH_LEN / 2 - P["tie_off"], SH_X0 + SH_LEN / 2 + P["tie_off"]]



@pytest.fixture(scope="module")
def mount(tmp_path_factory):
    d = tmp_path_factory.mktemp("mount")
    return trimesh.load(build_scad(HERE / "model.scad", d, "mount", render=False)["stl"])


def first_z(mesh, x, y):
    h = ray_hits(mesh, (x, y, 50), (0, 0, -1))
    return h[0][2] if len(h) else None


LIP_H, LIP_T = P["lip_h"], P["lip_t"]
TOP = LIP_H + T  # plate z 0..T, lip T..TOP


def test_one_watertight_piece(mount):
    assert mount.is_watertight
    assert len(mount.split(only_watertight=False)) == 1


def test_bounds(mount):
    # the PSU's 58 x 85 footprint, a 2 mm lip on three sides, a 15 mm shelf on the lower side; 8 mm lip + 2.5 mm plate
    assert (L, W, EXT) == (58, 85, 15)
    assert np.allclose(mount.bounds, [[-L / 2 - LIP_T, -W / 2 - EXT, 0], [L / 2 + LIP_T, W / 2 + LIP_T, TOP]], atol=0.05)


def test_volume_window(mount):
    plate = (L + 2 * LIP_T) * (W + 2 * LIP_T) * T + SH_LEN * (EXT - LIP_T) * T
    walls = 2 * (W + L) * LIP_T * LIP_H
    shelf = SH_LEN * (EXT - LIP_T) * LIP_H
    assert 0.9 * (plate + walls + shelf) < mount.volume < 1.05 * (plate + walls + shelf)


def test_back_is_flat_and_solid(mount):
    assert np.isclose(first_z(mount, 0, 0), T)  # solid plate, no lip in the pocket, clips are separate parts
    assert np.isclose(mount.bounds[1][2], TOP)


def test_pocket_is_the_psu_footprint_8mm_deep(mount):
    # the pocket floor is the plate top, T; the lip walls stand to TOP on the three thin sides
    assert np.isclose(first_z(mount, 0, 0), T)
    for x, y in [(L / 2 + LIP_T / 2, 0), (-L / 2 - LIP_T / 2, 0), (0, W / 2 + LIP_T / 2)]:
        assert np.isclose(first_z(mount, x, y), TOP)


def test_lower_lip_is_a_15mm_shelf_over_33_5mm(mount):
    mid = SH_X0 + SH_LEN / 2
    # raised to TOP across the 15 mm below the PSU edge, mid-shelf (between the slot pairs); pocket floor at the PSU edge
    for y in (-W / 2 - 1, -W / 2 - EXT + 1):
        assert np.isclose(first_z(mount, mid, y), TOP)
    assert np.isclose(first_z(mount, mid, -W / 2 + 1), T)
    # outside the shelf the lower lip is the thin 2 mm wall: nothing 5 mm beyond it, wall itself raised
    for x in (SH_X0 - 3, SH_X0 + SH_LEN + 3):
        assert first_z(mount, x, -W / 2 - 5) is None
        assert np.isclose(first_z(mount, x, -W / 2 - LIP_T / 2), TOP)
    # the shelf's two ends
    assert first_z(mount, SH_X0 - 0.5, -W / 2 - 8) is None and first_z(mount, SH_X0 + 0.5, -W / 2 - 8) is not None
    assert first_z(mount, SH_X0 + SH_LEN + 0.5, -W / 2 - 8) is None and first_z(mount, SH_X0 + SH_LEN - 0.5, -W / 2 - 8) is not None


def test_pocket_corners_are_square(mount):
    # the PSU's own square corners fit: pocket floor right into every corner, outside it the lip is raised
    for sx in (-1, 1):
        for sy in (-1, 1):
            assert np.isclose(first_z(mount, sx * (L / 2 - 0.2), sy * (W / 2 - 0.2)), T)
            assert np.isclose(first_z(mount, sx * (L / 2 + 0.2), sy * (W / 2 + 0.2)), TOP) or sy < 0


def test_pill_cutout_is_closed_slot_long_along_Y(mount):
    px, py = 25, -39
    assert first_z(mount, px, py) is None
    assert first_z(mount, px, py + 2.5) is None and first_z(mount, px, py + 3.2) is not None
    assert first_z(mount, px + 1.5, py) is None and first_z(mount, px + 2.0, py) is not None


def test_two_diagonal_screw_holes(mount):
    for hx, hy in [(-23.2, -36.7), (-23.2, 29.8), (-22.75, 38.7)]:
        assert first_z(mount, hx, hy) is None
    assert 3.3 <= P["hole_d"] <= 3.6  # M3, easy slip fit


def test_cord_tie_slot_pairs_straddle_a_cord_running_down_Y(mount):
    gap, tw, tt, c = P["tie_gap"], P["tie_w"], P["tie_t"], P["tie_c"]
    assert tw >= 5.2 and len(TIE_XS) == 2  # a standard 4.8 mm tie; one point for the AC cord, one for the DC
    for x in TIE_XS:
        for s in (-1, 1):
            sx = x + s * gap / 2
            assert first_z(mount, sx, TIE_Y) is None  # slot through shelf and plate
            assert first_z(mount, sx, TIE_Y + tw / 2 - 0.3) is None and first_z(mount, sx, TIE_Y + tw / 2 + 0.3) is not None  # long along Y
            # the web between the pair stands full height: the cord lies on it
            assert np.isclose(first_z(mount, x, TIE_Y), TOP)
            # outer-edge chamfer: just outside the slot the back is cut away, still solid above
            xo = sx + s * (tt / 2 + c * 0.25)
            assert first_z(mount, xo, TIE_Y) is not None
            h = ray_hits(mount, (xo, TIE_Y, -5), (0, 0, 1))
            assert h[0][2] > 0.3  # not the flat z = 0 face


def test_outline_is_rounded_and_filleted(mount):
    # the shelf's outer corners are rounded, not square
    assert first_z(mount, SH_X0 + 0.3, -W / 2 - EXT + 0.3) is None
    # the step between shelf and thin lip is filleted: material in the inside corner that a square step would leave empty
    assert first_z(mount, SH_X0 - 1, -W / 2 - LIP_T - 0.5) is not None


def test_slot_inner_bottom_edges_are_rounded(mount):
    r, tt, gap = P["tie_ri"], P["tie_t"], P["tie_gap"]
    for x in TIE_XS:
        for s in (-1, 1):
            inner = x + s * gap / 2 - s * tt / 2  # the slot's web-side edge
            h = ray_hits(mount, (inner - s * 0.2, TIE_Y, -5), (0, 0, 1))
            assert h[0][2] > 1.0  # back cut away right by the edge
            h = ray_hits(mount, (x, TIE_Y, -5), (0, 0, 1))
            assert np.isclose(h[0][2], 0)  # web centre still flat on the back


@pytest.fixture(scope="module")
def gauge(tmp_path_factory):
    d = tmp_path_factory.mktemp("psu_gauge")
    for f in ("model.scad", "part-gauge.scad"):
        (d / f).write_text((HERE / f).read_text())
    return trimesh.load(build_scad(d / "part-gauge.scad", d, "gauge", render=False)["stl"])


def test_gauge_is_the_mount_sliced_thin_with_the_same_holes(gauge):
    G = params(HERE / "part-gauge.scad")
    GT, GR = G["gauge_t"], G["gauge_rise"]
    assert 0 < G["z_plate"] < T < G["z_wall"] < TOP  # one slice through the plate, one through the lip
    assert gauge.is_watertight and gauge.body_count == 1
    assert np.allclose(gauge.bounds, [[-L / 2 - LIP_T, -W / 2 - EXT, 0], [L / 2 + LIP_T, W / 2 + LIP_T, GT + GR]], atol=0.05)
    assert first_z(gauge, 0, 0) == pytest.approx(GT, abs=0.02)  # plate top
    assert first_z(gauge, 0, W / 2 + LIP_T / 2) == pytest.approx(GT + GR, abs=0.02)  # lip top
    assert first_z(gauge, TIE_XS[0], TIE_Y) == pytest.approx(GT + GR, abs=0.02)  # the shelf, between a slot pair
    assert first_z(gauge, TIE_XS[0] + P["tie_gap"] / 2, TIE_Y) is None  # a tie slot
    for h in [(-23.2, -36.7), (-23.2, 29.8), (-22.75, 38.7), (25, -39)]:
        assert first_z(gauge, *h) is None


CLIP_YS = [-22.05, 28.95]  # the clip's insert holes, across the rail (its model: x = 5 and 56, rail centre 27.05)


def test_clip_screw_holes_are_countersunk_from_the_psu_side(mount):
    cx, d, cd, ch = P["clip_x"], P["hole_d"], P["csk_d"], P["csk_h"]
    for x in (-cx, cx):
        for y in CLIP_YS:
            assert first_z(mount, x, y) is None  # through for an M3
            assert first_z(mount, x + d / 2 + 0.2, y) == pytest.approx(T - ch, abs=0.1) or first_z(mount, x + d / 2 + 0.2, y) < T
            assert first_z(mount, x + cd / 2 - 0.3, y) < T  # countersink cuts the pocket floor
            assert np.isclose(first_z(mount, x + cd / 2 + 0.3, y), T)  # floor flat beyond it
            assert first_z(mount, x, y) is None and ray_hits(mount, (x + d / 2 + 0.2, y, -5), (0, 0, 1))[0][2] == pytest.approx(0, abs=0.01)  # back flat


def test_clip_bosses_clear_the_psu_screw_heads():
    # clip boss: 17 mm wide (its model, y -8.5..8.5) round each insert; an M3 pan head 5.5 across, 0.5 mm air
    for hx, hy in [(-23.2, -36.7), (-23.2, 29.8)]:
        for y in CLIP_YS:
            if abs(hy - y) < 8.5 + 2.75:
                assert abs(hx) - 2.75 - (P["clip_x"] + 8.5) >= 0.5


@pytest.fixture(scope="module")
def clip(tmp_path_factory):
    d = tmp_path_factory.mktemp("clip")
    for f in ("part-din-clip.scad", "ref_din_clip_heat_insert.stl"):
        (d / f).write_bytes((HERE / f).read_bytes())
    return trimesh.load(build_scad(d / "part-din-clip.scad", d, "clip", render=False)["stl"])


def test_clip_is_the_printables_420009_model(clip):
    assert np.allclose(clip.extents, [60, 18, 7.5], atol=0.05)
    assert clip.volume == pytest.approx(4488, rel=0.01)
    for x in (5, 56):  # its two heat-insert holes, 51 mm apart, as clip_ys
        assert len(ray_hits(clip, (x, 0, 20), (0, 0, -1))) == 0 or ray_hits(clip, (x, 0, 20), (0, 0, -1))[0][2] < 0.01
    assert CLIP_YS[1] - CLIP_YS[0] == pytest.approx(51)
