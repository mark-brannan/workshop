"""The compact forms: counts, one piece per net, clearance, screws clear of copper and bodies, pin order, file in step."""

from itertools import combinations
from pathlib import Path

import pytest
from shapely.geometry import LineString, Point, box
from shop.testing import load_model

m = load_model(__file__, "layouts")
MIN_CLEAR = 0.3
SIZE = {"two-row": (42.0, 18.6, 4), "ring": (30.7, 30.7, 4), "pinwheel": (24.0, 24.0, 2)}   # mm, mm, screws


@pytest.fixture(params=list(m.LAYOUTS), scope="module")
def b(request):
    return m.LAYOUTS[request.param]()


def shapes(b, layer):
    out = [(s["net"], LineString([(s["x1"], s["y1"]), (s["x2"], s["y2"])]).buffer(s["w"] / 2))
           for s in b["tracks"] if s["layer"] == layer]
    return out + [(q["net"], Point(q["x"], q["y"]).buffer(q["d"] / 2)) for q in b["pads"]]


def test_counts_and_size(b):
    terms = [q for q in b["pads"] if q["ref"].startswith("J")]
    assert len(terms) == 21 and {n: sum(q["net"] == n for q in terms) for n in (1, 2, 3)} == {1: 7, 2: 7, 3: 7}
    assert {(q["ref"], q["net"]) for q in b["pads"] if q not in terms} == {("R1", 2), ("R1", 3)}
    x0, y0, x1, y1 = b["outline"]
    w, h, screws = SIZE[b["name"]]
    assert abs(x1 - x0 - w) < 0.25 and abs(y1 - y0 - h) < 0.25 and len(b["holes"]) == screws


def test_every_terminal_reads_g_d_v_left_to_right_facing_its_entry(b):
    for q in b["pads"]:
        if q["ref"].startswith("J"):
            first = next(o for o in b["pads"] if o["ref"] == q["ref"] and o["num"] == 1)
            along = (q["x"] - first["x"]) * q["ey"] - (q["y"] - first["y"]) * q["ex"]    # distance to the viewer's right
            assert abs(along - (q["num"] - 1) * 2.54) < 1e-6 and q["net"] == (q["num"] - 1) % 3 + 1


def test_no_two_nets_within_clearance(b):
    for layer in ("F.Cu", "B.Cu"):
        for (na, a), (nb, c) in combinations(shapes(b, layer), 2):
            assert na == nb or a.distance(c) >= MIN_CLEAR, (layer, na, nb, round(a.distance(c), 3))


def test_each_net_is_one_piece(b):
    for net in (1, 2, 3):
        parts = [g for layer in ("F.Cu", "B.Cu") for n, g in shapes(b, layer) if n == net]
        merged = parts[0]
        for g in parts[1:]:
            merged = merged.union(g)
        assert merged.geom_type == "Polygon", net


def test_copper_and_bodies_stay_on_the_board(b):
    x0, y0, x1, y1 = b["outline"]
    for layer in ("F.Cu", "B.Cu"):
        for _, g in shapes(b, layer):
            gx0, gy0, gx1, gy1 = g.bounds
            assert min(gx0 - x0, gy0 - y0, x1 - gx1, y1 - gy1) >= 0.5
    for bx0, by0, bx1, by1 in b["bodies"]:
        assert min(bx0 - x0, by0 - y0, x1 - bx1, y1 - by1) >= 0.45
    for (a, c) in combinations(b["bodies"], 2):
        assert box(*a).distance(box(*c)) >= 0.09, "two terminal bodies touch"


def test_screw_heads_clear_copper_bodies_and_the_edge(b):
    x0, y0, x1, y1 = b["outline"]
    r = b["head_d"] / 2
    for hx, hy in b["holes"]:
        head = Point(hx, hy).buffer(r)
        assert min(hx - r - x0, hy - r - y0, x1 - hx - r, y1 - hy - r) >= 0
        for body in b["bodies"]:
            assert head.distance(box(*body)) >= 0.1
        for layer in ("F.Cu", "B.Cu"):
            for _, g in shapes(b, layer):
                assert head.distance(g) >= 0.09, (layer, round(head.distance(g), 3))
    if b["resistor"]:
        (vx, vy), (dx, dy) = b["resistor"]
        body = LineString([(vx, vy), (dx, dy)]).buffer(1.25, cap_style="flat")
        for other in b["bodies"]:
            assert body.distance(box(*other)) >= 0.1, "R1 lies against a terminal body"
        for hx, hy in b["holes"]:
            assert body.distance(Point(hx, hy).buffer(r)) >= 0.1


def test_committed_output_matches_model(b):
    text = m.to_kicad(b)
    assert text.count("(") == text.count(")") and text.count("(segment") == len(b["tracks"])
    f = Path(__file__).parent / "out" / b["name"] / f"one-wire-bus-{b['name']}.kicad_pcb"
    assert f.read_text() == text
