"""The sump box's traced wing outline lies inside the platform deck (plan view). Failing means widen the deck."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from wing_overlay import P, margins, wing


def test_wing_inside_deck():
    assert min(margins()) >= 0, f"wing sticks out of the deck by {-min(margins()):.1f} mm"


def test_wing_tip_is_the_drawings_215():
    assert max(x for x, _ in wing()) * 2 == pytest.approx(215, abs=0.1)


def test_wing_length_within_deck_overhang():
    ys = [y for _, y in wing()]
    assert (max(ys) - min(ys)) - P["len"] < 5   # the wing may run a little past the deck's fore-aft ends
