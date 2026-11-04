"""finish_dxf: OpenSCAD-style raw DXF in, millimetres and LightBurn layers out.

Raw inputs are written with ezdxf in the two shapes OpenSCAD produces (R12
LINE segments from 2021.01, closed LWPOLYLINEs from the Nightly), so this
runs without openscad.exe.
"""

import ezdxf
from shop.scad import LIGHTBURN_LAYERS, finish_dxf


def raw_lines(path):
    doc = ezdxf.new("R12")
    msp = doc.modelspace()
    sq = [(0, 0), (10, 0), (10, 10), (0, 10)]
    for a, b in zip(sq, sq[1:] + sq[:1]):
        msp.add_line(a, b)
    doc.saveas(path)
    return path


def raw_poly(path):
    doc = ezdxf.new("R2000")
    doc.modelspace().add_lwpolyline([(2, 2), (4, 2), (4, 4)], close=True)
    doc.saveas(path)
    return path


def test_units_layers_geometry(tmp_path):
    out = finish_dxf({"cut": raw_lines(tmp_path / "a.dxf"), "score": raw_poly(tmp_path / "b.dxf")}, tmp_path / "o.dxf")
    doc = ezdxf.readfile(out)
    assert doc.header["$INSUNITS"] == 4
    assert doc.header["$MEASUREMENT"] == 1
    for name in ("cut", "score"):
        assert doc.layers.get(name).rgb == LIGHTBURN_LAYERS[name]
    ents = list(doc.modelspace())
    assert sorted((e.dxftype(), e.dxf.layer) for e in ents) == [("LINE", "cut")] * 4 + [("LWPOLYLINE", "score")]
    assert all(e.dxf.color == 256 for e in ents)  # BYLAYER, so the layer colour decides
    (poly,) = [e for e in ents if e.dxftype() == "LWPOLYLINE"]
    assert poly.closed and [p[:2] for p in poly.get_points()] == [(2, 2), (4, 2), (4, 4)]
