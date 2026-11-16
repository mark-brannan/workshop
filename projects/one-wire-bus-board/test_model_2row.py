"""Two-row form: counts, size window, and no copper of two nets closer than the clearance, per layer."""

from itertools import combinations

from shapely.geometry import LineString, Point
from shop.testing import load_model

m = load_model(__file__, "model_2row")
B = m.build()
MIN_CLEAR = 0.3


def shapes(layer):
    out = [(s["net"], LineString([(s["x1"], s["y1"]), (s["x2"], s["y2"])]).buffer(s["w"] / 2))
           for s in B["tracks"] if s["layer"] == layer]
    return out + [(q["net"], Point(q["x"], q["y"]).buffer(q["d"] / 2)) for q in B["pads"]]


def test_counts_and_size():
    terms = [q for q in B["pads"] if q["ref"].startswith("J")]
    assert len(terms) == 21 and {n: sum(q["net"] == n for q in terms) for n in (1, 2, 3)} == {1: 7, 2: 7, 3: 7}
    x0, y0, x1, y1 = B["outline"]
    assert 45 < x1 - x0 < 56 and 17 < y1 - y0 < 21


def test_no_two_nets_within_clearance():
    for layer in ("F.Cu", "B.Cu"):
        for (na, a), (nb, b) in combinations(shapes(layer), 2):
            assert na == nb or a.distance(b) >= MIN_CLEAR, (layer, na, nb, a.distance(b))


def test_each_net_is_one_piece():
    for layer_pair in (("F.Cu", "B.Cu"),):
        for net in (1, 2, 3):
            parts = [g for l in layer_pair for n, g in shapes(l) if n == net]
            merged = parts[0]
            for g in parts[1:]:
                merged = merged.union(g)
            assert merged.geom_type == "Polygon" or len(merged.geoms) == 1, net
