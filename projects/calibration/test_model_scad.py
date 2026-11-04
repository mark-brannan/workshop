"""Tests for the K2 Plus tolerance print (model.scad).

Bounding box, a volume window, body count (plate + gauge bar + one tab per
size), every hole open and every peg standing, probed by rays at the
positions the parameters predict.
"""

import math
import re
from pathlib import Path

import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad.exe not found")


def scad_params(path: Path) -> dict:
    head = path.read_text().split("/* [Hidden] */", 1)[0]
    out = {}
    for k, v in re.findall(r"^(\w+)\s*=\s*([^;]+);", head, re.M):
        out[k] = [float(x) for x in v.strip("[] ").split(",")] if "[" in v else float(v)
    return out


P = scad_params(HERE / "model.scad")
N = round((P["d_max"] - P["d_min"]) / P["d_step"]) + 1
DIAS = [(round(P["d_min"] * 10) + i) / 10 for i in range(N)]
COLS = int(P["cols"])
ROWS = math.ceil(N / COLS)
PX = COLS * P["pitch_x"] + 2 * P["edge"]
PY = ROWS * P["pitch_y"] + P["slot_band"] + 2 * P["edge"]
TAB = P["tab"]
GAP = 5


def hole_xy(i):
    return (P["edge"] + (i % COLS + 0.5) * P["pitch_x"], PY - P["edge"] - (i // COLS + 0.4) * P["pitch_y"])


def peg_xy(i):
    x0 = PX + GAP + (i % COLS) * (TAB[0] + P["tab_gap"])
    y0 = PY - TAB[1] - (i // COLS) * (TAB[1] + P["tab_gap"])
    return x0 + TAB[0] / 2, y0 + TAB[1] - P["d_max"] / 2 - 1


@pytest.fixture(scope="module")
def mesh(tmp_path_factory) -> trimesh.Trimesh:
    built = build_scad(HERE / "model.scad", tmp_path_factory.mktemp("scad"), "cal", render=False)
    return trimesh.load(built["stl"])


def test_range():
    assert N == 31 and DIAS[0] == 3.0 and DIAS[-1] == 6.0


def test_bounding_box(mesh):
    lo, hi = mesh.bounds
    width = PX + GAP + COLS * TAB[0] + (COLS - 1) * P["tab_gap"]
    assert lo.tolist() == pytest.approx([0, -GAP - P["slot_w"], 0], abs=0.01)
    assert hi.tolist() == pytest.approx([width, PY, TAB[2] + P["peg_h"]], abs=0.01)


def test_watertight_and_bodies(mesh):
    assert mesh.is_watertight
    assert len(mesh.split(only_watertight=False)) == 2 + N


def test_volume(mesh):
    t = P["plate_t"]
    plate = (PX * PY - sum(math.pi * d * d / 4 for d in DIAS) - P["slot_l"] * P["slot_w"]) * t
    gauge = P["slot_l"] * P["slot_w"] * t
    pegs = sum(TAB[0] * TAB[1] * TAB[2] + math.pi * d * d / 4 * P["peg_h"] for d in DIAS)
    nominal = plate + gauge + pegs
    # Labels are debossed: 64 labels of about 3 glyphs take a few hundred mm^3 off.
    assert nominal - 600 < mesh.volume < nominal, (mesh.volume, nominal)


def test_holes_open_pegs_standing(mesh):
    for i, d in enumerate(DIAS):
        x, y = hole_xy(i)
        assert ray_hits(mesh, (x, y, 20), (0, 0, -1)) == [], f"hole {d}"
        # Just inside the bore wall: solid plate, so 2 hits (top, bottom).
        assert len(ray_hits(mesh, (x + d / 2 + 0.3, y, 20), (0, 0, -1))) == 2, f"wall {d}"
        px, py = peg_xy(i)
        hits = ray_hits(mesh, (px, py, 20), (0, 0, -1))
        assert len(hits) == 2 and hits[0][2] == pytest.approx(TAB[2] + P["peg_h"], abs=1e-6), f"peg {d}"
        # Just outside the peg: tab only.
        assert ray_hits(mesh, (px + d / 2 + 0.2, py, 20), (0, 0, -1))[0][2] == pytest.approx(TAB[2], abs=1e-6)


def test_slot_open(mesh):
    y = P["edge"] + P["slot_band"] / 2 + 2
    for x in (PX / 2 - P["slot_l"] / 2 + 0.5, PX / 2, PX / 2 + P["slot_l"] / 2 - 0.5):
        assert ray_hits(mesh, (x, y, 20), (0, 0, -1)) == []
