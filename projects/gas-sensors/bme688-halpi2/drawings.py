"""The wiring picture. Usage: uv run python drawings.py"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

HERE = Path(__file__).parent


def wiring(ax):
    def box(x, y, w, h, label, c):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", fc=c, ec="#333"))
        ax.text(x + w / 2, y + h - 2.5, label, ha="center", va="top", fontsize=9, weight="bold")
    ax.add_patch(Rectangle((-4, -8), 50, 62, fill=False, ls="--", ec="#888")); ax.text(21, 55.5, "inside the HALPI2", ha="center", fontsize=9, color="#666")
    ax.add_patch(Rectangle((100, -8), 96, 62, fill=False, ls="--", ec="#888")); ax.text(148, 55.5, "inside the screen", ha="center", fontsize=9, color="#666")
    box(0, 0, 26, 48, "40-pin header\n(I2C bus 1)", "#d5f5e3")
    box(40, 8, 12, 30, "PG7\ngland", "#eeeeee")
    box(104, 4, 18, 40, "splice,\nheat-\nshrunk", "#d6eaf8")
    box(140, 14, 14, 24, "Qwiic\nplug", "#f5b7b1")
    box(160, 6, 32, 36, "BME688\n0x77", "#e8daef")
    rows = [("3V3", "pin 1", "1", "red", "#c0392b"), ("SDA", "pin 3", "2", "blue", "#2471a3"),
            ("SCL", "pin 5", "3", "yellow", "#d4ac0d"), ("GND", "pin 9", "4", "black", "#222")]
    for i, (sig, pin, n, colour, c) in enumerate(rows):
        y = 27 - i * 6
        ax.plot([26.5, 103.5], [y, y], c, lw=2, zorder=0); ax.plot([122.5, 139.5], [y, y], c, lw=2)
        ax.plot([27.5], [y], "s", color=c, ms=5)
        ax.text(25, y, f"{sig} {pin}", ha="right", va="center", fontsize=8)
        ax.text(131, y + 1, colour, ha="center", va="bottom", fontsize=7, color=c)
    ax.text(14, -5, "four single Dupont\nsockets on the pins", ha="center", fontsize=8)
    ax.text(70, 32, "4-core cable, under 300 mm,\nin through the floor notch", ha="center", fontsize=8)
    ax.text(131, -3, "Qwiic pigtail, cut and\nspliced to the cable", ha="center", fontsize=8)
    ax.set_xlim(-6, 198); ax.set_ylim(-10, 60); ax.set_aspect("equal"); ax.axis("off")


fig, ax = plt.subplots(figsize=(12, 4.6))
wiring(ax)
fig.tight_layout(); fig.savefig(HERE / "out/wiring.png", dpi=120)
