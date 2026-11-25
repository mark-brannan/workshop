"""Head mirror outline: edges match the tape, angles sum, inset shrinks evenly."""

import importlib.util
import sys
from pathlib import Path

import ezdxf
import numpy as np

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("mirror_model", HERE / "model.py")
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m  # dataclass needs its module registered
spec.loader.exec_module(m)


def edges(pts):
    P = list(pts.values())
    return [np.linalg.norm(P[(i + 1) % 4] - P[i]) / m.IN for i in range(4)]


def test_edges_match_tape_readings():
    p = m.Params()
    assert np.allclose(edges(m.corners(p)), [p.top, p.wide, p.bottom, p.narrow], atol=1e-6)


def test_no_square_corner_and_angles_close():
    a = m.angles(m.corners())
    assert abs(sum(a.values()) - 360) < 1e-6
    assert all(abs(v - 90) > 2 for v in a.values())
    assert abs(a["narrow-top"] - 85) < 1e-6


def test_middle_width_matches_tape():
    c = m.corners()
    mid_top = (c["narrow-top"] + c["wide-top"]) / 2
    mid_bot = (c["narrow-bottom"] + c["wide-bottom"]) / 2
    assert abs(np.linalg.norm(mid_top - mid_bot) / m.IN - 10.25) < 1 / 16


def test_bounding_box_and_clearance():
    c = m.corners()
    span = np.ptp(np.array(list(c.values())), axis=0)
    assert 525 < span[0] < 540 and 265 < span[1] < 275
    small = m.corners(m.Params(clearance_mm=1.0))
    assert all(e1 < e0 for e0, e1 in zip(edges(c), edges(small)))


def test_dxf_is_one_closed_outline(tmp_path):
    out = tmp_path / "x.dxf"
    m.write_dxf(m.corners(), out)
    polys = list(ezdxf.readfile(out).modelspace().query("LWPOLYLINE"))
    assert len(polys) == 1 and polys[0].closed and polys[0].dxf.layer == "cut"
