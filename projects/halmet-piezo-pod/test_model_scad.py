"""Tests for the HALMET piezo pod: bounding box, volume window, feature counts."""

import math
import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
IN_W = P["carrier_w"] + 2 * P["fit"] - 2 * P["groove_d"]
OUT_W = IN_W + 2 * P["wall"]
DEPTH = P["plate_t"] + P["back_gap"] + P["carrier_t"] + P["comp_h"] + P["front_clear"]
CARRIER_Y = P["plate_t"] + P["back_gap"]
GROOVE_TOP = P["bottom_gap"] + P["carrier_h"] + P["fit"]
EAVE = GROOVE_TOP + P["groove_d"] + P["top_clear"]
HEIGHT = EAVE + IN_W / 2 + P["roof_t"] * math.sqrt(2)
EAR_X = OUT_W / 2 + P["ear_w"] / 2


@pytest.fixture(scope="module")
def pod(tmp_path_factory):
    d = tmp_path_factory.mktemp("pod")
    (d / "model.scad").write_text((HERE / "model.scad").read_text())
    return trimesh.load(build_scad(d / "model.scad", d, "pod", render=False)["stl"])


def test_bounds_volume(pod):
    assert pod.is_watertight
    half = OUT_W / 2 + P["ear_w"]
    assert np.allclose(pod.bounds, [[-half, 0, 0], [half, DEPTH, HEIGHT]], atol=0.05)
    assert 8_000 < pod.volume < 14_000


def test_carrier_slides_in_grooves_up_to_a_stop(pod):
    y = CARRIER_Y + P["carrier_t"] / 2
    for s in (-1, 1):
        x = s * (IN_W / 2 + P["groove_d"] - 0.2)  # inside the groove, near its deep face
        up = ray_hits(pod, (x, y, -1), (0, 0, 1))
        assert np.isclose(up[0][2], GROOVE_TOP + 0.2, atol=0.05)  # open from below to the 45-degree stop
    # The carrier edge, carrier_w wide, reaches into both grooves but not past them.
    assert IN_W < P["carrier_w"] < IN_W + 2 * P["groove_d"]


def test_buzzer_and_terminal_clear_inside_the_walls():
    assert CARRIER_Y + P["carrier_t"] + max(P["buzzer_h"], P["comp_h"]) <= DEPTH
    assert P["buzzer_d"] < IN_W


def test_open_bottom_and_front(pod):
    assert len(ray_hits(pod, (0, DEPTH / 2, -1), (0, 0, 1))) == 2  # only the roof, from below
    assert len(ray_hits(pod, (0, DEPTH + 1, GROOVE_TOP / 2), (0, -1, 0))) == 2  # front open to the plate


def test_tie_slot_through_both_walls(pod):
    z = P["tie_z"] + P["tie_w"] / 2
    y = P["plate_t"] + 0.5 + P["tie_t"] / 2
    assert len(ray_hits(pod, (-OUT_W, y, z), (1, 0, 0))) == 0
    assert P["tie_z"] + P["tie_w"] + P["tie_t"] / 2 < P["bottom_gap"]  # tie sits under the carrier


def test_two_screw_holes_through_the_ears(pod):
    for s in (-1, 1):
        assert len(ray_hits(pod, (s * EAR_X, -1, P["ear_h"] / 2), (0, 1, 0))) == 0
