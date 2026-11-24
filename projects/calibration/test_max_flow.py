"""The melt-rate job asks the hot end for what its header says, band by band, and stays on the bed."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import max_flow  # noqa: E402

BED = 350.0
FIL = math.pi * (1.75 / 2) ** 2
MOVE = re.compile(r"^G1 X([-\d.]+) Y([-\d.]+) E([-\d.]+) F(\d+)$")


def bands_in(gcode: str) -> list[list[float]]:
    """Melt rate, mm3/s, of every extruding move, grouped by the band comment above it."""
    out: list[list[float]] = []
    x = y = None
    for line in gcode.splitlines():
        if re.match(r"; band \d", line):
            out.append([])
        m = MOVE.match(line)
        t = re.match(r"^G1 X([-\d.]+) Y([-\d.]+) F", line)
        if m:
            nx, ny, e, f = (float(v) for v in m.groups())
            d = math.hypot(nx - x, ny - y)
            if out and d > 1:
                out[-1].append(e * FIL / (d / (f / 60)))
            x, y = nx, ny
        elif t:
            x, y = float(t.group(1)), float(t.group(2))
    return out


def test_each_band_melts_its_rate():
    p = max_flow.P()
    got = bands_in(max_flow.build(p))
    assert len(got) == len(p.bands) == 17
    for want, rates in zip(p.bands, got):
        assert rates and all(abs(r - want) < 0.02 * want for r in rates), want


def test_speed_and_size():
    p = max_flow.P()
    assert 180 < p.speed(p.q_end) < 200
    assert abs(p.band_top(len(p.bands) - 1) - 25.8) < 1e-6
    g = max_flow.build(p)
    xy = [(float(a), float(b)) for a, b in re.findall(r"^G1 X([-\d.]+) Y([-\d.]+)", g, re.M)]
    body = [q for q in xy if q[0] > 20 and q[1] > 20]  # the purge line runs along the bed's front-left edges
    assert 60 < min(x for x, _ in body) and max(x for x, _ in body) < BED - 60
    assert 130 < min(y for _, y in body) and max(y for _, y in body) < 220


def test_columns_never_start_in_air():
    """A band's loop carries its own column and every later one, so each column grows from the bed."""
    p = max_flow.P()
    for i in range(len(p.bands)):
        assert len(max_flow.loop(p, cols_from=i)) - len(max_flow.loop(p)) == 3 * (len(p.bands) - i)
