"""Electrical checks on the generated board: connectivity per net, clearance, counts, parseable file."""

from itertools import combinations
from pathlib import Path

from shapely.geometry import LineString, Point
from shop.testing import load_model

m = load_model(__file__)
B = m.build()
P = B["p"]
MIN_CLEAR = 0.3


def shapes(layer):
    out = []  # (net, geometry)
    for s in B["tracks"]:
        if s["layer"] == layer:
            out.append((s["net"], LineString([(s["x1"], s["y1"]), (s["x2"], s["y2"])]).buffer(s["w"] / 2)))
    for q in B["pads"]:  # plated: a pad is on both layers
        out.append((q["net"], Point(q["x"], q["y"]).buffer(P.pad_d / 2)))
    return out


def test_counts():
    assert len(B["pads"]) == P.terminals * 3 == 21
    for net in (1, 2, 3):
        assert sum(q["net"] == net for q in B["pads"]) == P.terminals
    x0, y0, x1, y1 = B["outline"]
    assert 62 < x1 - x0 < 67 and 10 < y1 - y0 < 12


def test_every_pin_is_on_one_2_54_grid():
    xs = sorted(q["x"] for q in B["pads"])
    assert all(abs(b - a - 2.54) < 1e-9 for a, b in zip(xs, xs[1:]))
    x0, y0, x1, y1 = B["outline"]
    for bx0, by0, bx1, by1 in B["bodies"]:
        assert 0 <= y1 - by1 <= 1.0, "body front must sit at the board's front edge"
        assert by0 - y0 >= 3.0 and (by1 - by0) == 6.5


def test_copper_stays_off_the_edge():
    x0, y0, x1, y1 = B["outline"]
    for layer in ("F.Cu", "B.Cu"):
        for _, g in shapes(layer):
            bx0, by0, bx1, by1 = g.bounds
            assert bx0 - x0 >= 0.5 and x1 - bx1 >= 0.5 and by0 - y0 >= 0.5 and y1 - by1 >= 0.5


def test_no_vias_no_jumpers_one_layer_each():
    layers = {n: {s["layer"] for s in B["tracks"] if s["net"] == n} for n in (1, 2, 3)}
    assert layers == {1: {"F.Cu"}, 2: {"B.Cu"}, 3: {"F.Cu"}}


def test_each_net_is_one_connected_piece_touching_all_its_pads():
    for net in (1, 2, 3):
        segs = [s for s in B["tracks"] if s["net"] == net]
        geoms = [LineString([(s["x1"], s["y1"]), (s["x2"], s["y2"])]).buffer(s["w"] / 2) for s in segs]
        merged = geoms[0]
        for g in geoms[1:]:
            merged = merged.union(g)
        assert merged.geom_type == "Polygon", f"net {net} track is in pieces"
        for q in (q for q in B["pads"] if q["net"] == net):
            assert merged.intersects(Point(q["x"], q["y"]).buffer(P.pad_d / 2)), f"net {net} misses a pad"


def test_clearance_between_nets_on_each_layer():
    for layer in ("F.Cu", "B.Cu"):
        for (n1, g1), (n2, g2) in combinations(shapes(layer), 2):
            if n1 != n2:
                assert g1.distance(g2) >= MIN_CLEAR, f"{layer}: nets {n1}/{n2} {g1.distance(g2):.2f} mm apart"


def test_kicad_file_balanced_and_complete():
    text = m.to_kicad(B)
    assert text.count("(") == text.count(")")
    assert text.count("(footprint") == P.terminals + len(B["holes"])
    assert text.count("(segment") == len(B["tracks"])
    assert text.count("(gr_line") == 4
    assert text.count('"DATA"') >= P.terminals + 1


def test_committed_output_matches_model():
    f = Path(__file__).parent / "out" / "one-wire-bus.kicad_pcb"
    assert f.read_text() == m.to_kicad(B)
