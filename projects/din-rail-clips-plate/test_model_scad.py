"""Tests for the DIN clip plate: bounding box, volume window, feature counts."""

from pathlib import Path

import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")
CLIP_VOL = 4488  # one clip, Printables 420009


@pytest.fixture(scope="module")
def plate(tmp_path_factory):
    d = tmp_path_factory.mktemp("plate")
    for f in ("model.scad", "ref_din_clip_heat_insert.stl"):
        (d / f).write_bytes((HERE / f).read_bytes())
    return trimesh.load(build_scad(d / "model.scad", d, "plate", render=False)["stl"])


def test_ten_clips_in_five_pairs_inside_the_bed(plate):
    parts = plate.split(only_watertight=False)
    assert len(parts) == 10
    assert plate.volume == pytest.approx(10 * CLIP_VOL, rel=0.01)
    assert np.allclose(plate.extents, [126, 106, 7.5], atol=0.1)  # K2 Plus bed is 350
    assert plate.bounds[0][2] == pytest.approx(0, abs=1e-6)
    ys = sorted(round(p.bounds.mean(axis=0)[1], 1) for p in parts)
    assert all(ys[2 * i] == ys[2 * i + 1] for i in range(5))  # five rows of two


def test_each_pair_is_one_clip_turned_not_mirrored(plate):
    for row in range(5):
        y = (row - 2) * 22
        l, r = (
            p for p in plate.split(only_watertight=False) if abs(p.bounds.mean(axis=0)[1] - y) < 1
        )
        l, r = sorted((l, r), key=lambda p: p.bounds.mean(axis=0)[0])
        T = r.copy()
        T.apply_transform(np.diag([-1.0, -1.0, 1.0, 1.0]))  # turn 180 about Z
        c = T.bounds.mean(axis=0) - l.bounds.mean(axis=0)
        T.apply_translation(-c)
        assert T.volume == pytest.approx(l.volume, rel=1e-3)
        assert np.allclose(T.bounds, l.bounds, atol=0.1)
