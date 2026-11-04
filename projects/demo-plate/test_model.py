import math
import subprocess
import sys
from pathlib import Path

import ezdxf
import pytest

from shop.testing import load_model

_m = load_model(__file__)
PlateParams = _m.PlateParams
sketch = _m.sketch

HERE = Path(__file__).parent
P = PlateParams()


def test_sketch_area():
    sk = sketch(P)
    holes = 4 * math.pi * (P.hole_d / 2) ** 2
    slot = P.slot_length * P.slot_width + math.pi * (P.slot_width / 2) ** 2
    assert math.isclose(sk.area, P.length * P.width - holes - slot, rel_tol=1e-6)


@pytest.fixture(scope="module")
def dxf_path():
    subprocess.run([sys.executable, str(HERE / "model.py")], check=True, cwd=HERE)
    return HERE / "out" / "plate.dxf"


def test_dxf_entities(dxf_path):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    types = {}
    for e in msp:
        types[e.dxftype()] = types.get(e.dxftype(), 0) + 1
    # 4 outline lines + 4 circles + slot (2 lines + 2 arcs); tolerate polyline variants
    n = sum(types.values())
    assert 10 <= n <= 20, types
    assert types.get("CIRCLE", 0) == 4, types
    assert all(e.dxf.layer == "cut" for e in msp)
    xs, ys = [], []
    for e in msp.query("LINE"):
        for pt in (e.dxf.start, e.dxf.end):
            xs.append(pt.x)
            ys.append(pt.y)
    assert math.isclose(max(xs) - min(xs), P.length, abs_tol=0.01)
    assert math.isclose(max(ys) - min(ys), P.width, abs_tol=0.01)
