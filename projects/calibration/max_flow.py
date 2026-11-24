"""Melt-rate (maximum volumetric flow) test for the K2 Plus: one single-wall loop, pushed harder as it climbs.

Same idea as OrcaSlicer's max volumetric speed calibration, written as g-code directly so it can be started
over Moonraker without the slicer GUI. The loop is a stadium, one fat line wide. Every `band_layers` layers
the speed steps up so the plastic melted per second rises by `q_step`. Where the wall turns matt, thin or
gappy, the hot end has stopped keeping up; the last clean band, less a margin, is the filament profile's
max volumetric speed.

The front wall carries a row of columns, one per band, each stopping at the top of its own band, so the
row reads as a bar chart: shortest on the left is the first band, tallest on the right is the last. Read
the plain back wall for the surface and the front for which band it is.

    uv run python projects/calibration/max_flow.py [PETG]   # writes out/max_flow_<material>.gcode and .png
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from flow_ratio import G, area, start_gcode


@dataclass
class P:
    material: str = "PETG"
    tool: int | None = None  # None: external spool, no tool change. n: CFS via T<n>
    nozzle: int = 250  # Generic PETG @K2 Plus, as last printed
    bed: int = 70
    fan: int = 80  # percent; the profile's maximum, since a layer here lasts only a few seconds
    flow: float = 0.95  # the profile's flow ratio
    q_start: float = 8.0  # mm3/s in the first band
    q_step: float = 2.0
    q_end: float = 40.0  # the hot end's rated figure (ABS, 280 C)
    band_layers: int = 5
    h: float = 0.3
    w: float = 0.8  # a fat line keeps the head speed modest: 40 mm3/s is about 190 mm/s
    length: float = 200.0  # stadium outside, X
    depth: float = 60.0  # stadium outside, Y
    centre: tuple[float, float] = (175.0, 175.0)
    brim_loops: int = 3  # extra first-layer loops each side of the wall
    v1: float = 30.0  # first layer, mm/s
    accel: int = 10000  # enough to reach the top band's speed within 2 mm
    col_first: float = 9.0  # first column's distance along the front straight
    col_pitch: float = 7.5
    col_w: float = 3.0
    col_out: float = 2.0
    v_travel: float = 300.0
    retract: float = 0.8
    zhop: float = 0.4
    fil_d: float = 1.75

    @property
    def bands(self) -> list[float]:
        n = round((self.q_end - self.q_start) / self.q_step) + 1
        return [self.q_start + i * self.q_step for i in range(n)]

    def speed(self, q: float) -> float:
        """Head speed, mm/s, that melts q mm3/s of filament."""
        return q / (self.flow * area(self.w, self.h))

    def band_top(self, i: int) -> float:
        """Height of the top of band i above the bed; layer 1 is the brim layer under band 0."""
        return self.h * (1 + (i + 1) * self.band_layers)


def loop(p: P, off: float = 0.0, cols_from: int | None = None) -> list[tuple[float, float]]:
    """Centreline of the wall, counter-clockwise from the left end of the front straight, closed.
    `off` moves it outward. `cols_from` adds the front columns for bands cols_from and later."""
    cx, cy = p.centre
    r = p.depth / 2 - p.w / 2
    xl, xr = cx - p.length / 2 + p.depth / 2, cx + p.length / 2 - p.depth / 2
    ro = r + off
    pts = [(xl, cy - ro)]
    if cols_from is not None:
        for i in range(cols_from, len(p.bands)):
            x = xl + p.col_first + i * p.col_pitch
            pts += [(x, cy - ro), (x + p.col_w / 2, cy - ro - p.col_out), (x + p.col_w, cy - ro)]
    pts.append((xr, cy - ro))
    n = 36
    pts += [(xr + ro * math.sin(math.pi * k / n), cy - ro * math.cos(math.pi * k / n)) for k in range(1, n + 1)]
    pts.append((xl, cy + ro))
    pts += [(xl - ro * math.sin(math.pi * k / n), cy + ro * math.cos(math.pi * k / n)) for k in range(1, n + 1)]
    return pts


def build(p: P) -> str:
    g = G(p)
    bands = p.bands
    layers = 1 + len(bands) * p.band_layers
    seconds = 0.0

    def run(pts, v):
        nonlocal seconds
        for a, b in zip(pts, pts[1:]):
            seconds += math.dist(a, b) / v
        for q in pts[1:]:
            g.extrude(*q, p.w, p.flow, v)

    g.z = p.h
    g.emit(";LAYER_CHANGE")
    g.emit(f";Z:{g.z:.2f}")
    for k in range(-p.brim_loops, p.brim_loops + 1):
        pts = loop(p, off=k * p.w * 0.9, cols_from=0 if k == 0 else None)
        g.travel(*pts[0])
        run(pts, p.v1)
    g.emit(f"M106 S{round(255 * p.fan / 100)}")
    g.emit(f"M204 S{p.accel}")
    for i, q in enumerate(bands):
        pts = loop(p, cols_from=i)
        v = p.speed(q)
        g.emit(f"; band {i}: {q:.0f} mm3/s at {v:.0f} mm/s, top at {p.band_top(i):.1f} mm")
        for _ in range(p.band_layers):
            g.z += p.h
            g.emit(";LAYER_CHANGE")
            g.emit(f";Z:{g.z:.2f}")
            g.emit(f"G1 Z{g.z:.3f} F3000")
            run(pts, v)
    g.emit(f"G1 E{-p.retract:.3f} F2400")
    grams = g.e_total * g.fil * 1.27 / 1000
    xs = [x for x, _ in loop(p, off=p.brim_loops * p.w * 0.9)]
    ys = [y for _, y in loop(p, off=p.brim_loops * p.w * 0.9, cols_from=0)]
    head = [
        "; HEADER_BLOCK_START",
        "; generated by OrcaSlicer 2.5.0 on 2026-11-24 at 00:00:00",
        "; (actually workshop projects/calibration/max_flow.py; header kept Orca-shaped for Moonraker metadata)",
        f"; total layer number: {layers}",
        f"; max_z_height: {p.h * layers:.2f}",
        "; HEADER_BLOCK_END",
        f"; melt rate per band, mm3/s, bottom to top: {', '.join(f'{q:.0f}' for q in bands)}",
        f"; band height {p.h * p.band_layers:.1f} mm; first band starts {p.h:.1f} mm above the bed",
        f"; estimated printing time (normal mode) = {round(seconds / 60)}m (moves only, heating not counted)",
        f"; MINX = {min(xs) - p.w:.1f}", f"; MINY = {min(ys) - p.w:.1f}",
        f"; MAXX = {max(xs) + p.w:.1f}", f"; MAXY = {max(ys) + p.w:.1f}",
        *start_gcode(p),
    ]
    tail = [
        "M106 S0",
        "END_PRINT",
        f"; filament used [g] = {grams:.2f}",
        f"; filament_type = {p.material}",
        f"; first_layer_bed_temperature = {p.bed}",
        f"; first_layer_temperature = {p.nozzle}",
        f"; nozzle_temperature = {p.nozzle}",
        f"; layer_height = {p.h}",
        "; nozzle_diameter = 0.4",
        "; filament_diameter = 1.75",
    ]
    return "\n".join(head + g.lines + tail) + "\n"


def picture(p: P, path: Path) -> None:
    """Front view of the printed wall as the user will hold it: a band per melt rate, columns as a bar chart."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    bands = p.bands
    bh = p.h * p.band_layers
    fig, ax = plt.subplots(figsize=(12, 5.2), facecolor="#111418")
    ax.set_facecolor("#111418")
    x0, x1 = -p.length / 2, p.length / 2
    for i, q in enumerate(bands):
        y = p.band_top(i) - bh
        ax.add_patch(plt.Rectangle((x0, y), p.length, bh, fc=plt.cm.viridis(0.15 + 0.8 * i / (len(bands) - 1)),
                                   ec="#111418", lw=0.6))
        ax.text(x1 + 3, y + bh / 2, f"{q:.0f} mm³/s · {p.speed(q):.0f} mm/s", va="center", color="#d8dee9",
                fontsize=7.5)
        cx = x0 + p.depth / 2 + p.col_first + i * p.col_pitch
        ax.add_patch(plt.Rectangle((cx, p.h), p.col_w, p.band_top(i) - p.h, fc="#e5e9f0", ec="#111418", lw=0.5))
        ax.text(cx + p.col_w / 2, p.band_top(i) + 0.4, f"{q:.0f}", ha="center", va="bottom", color="#e5e9f0",
                fontsize=7)
    ax.add_patch(plt.Rectangle((x0 - 3, 0), p.length + 6, p.h, fc="#7b8494", ec="none"))
    ax.set_xlim(x0 - 8, x1 + 48)
    ax.set_ylim(-1.5, p.band_top(len(bands) - 1) + 3)
    ax.set_aspect(3)  # bands are 1.5 mm tall; true scale leaves no room for their labels
    ax.set_ylabel("height above bed, mm", color="#d8dee9")
    ax.set_xlabel("front wall, mm · each column stops at the top of the band whose melt rate is written above it",
                  color="#d8dee9")
    ax.tick_params(colors="#d8dee9")
    for s in ax.spines.values():
        s.set_color("#4c566a")
    ax.set_title(f"Melt-rate test, {p.material} at {p.nozzle} °C: last clean band is the limit", color="#eceff4")
    fig.tight_layout()
    fig.savefig(path, dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


PRESETS = {"PETG": P()}

if __name__ == "__main__":
    import sys

    p = PRESETS[sys.argv[1] if len(sys.argv) > 1 else "PETG"]
    out = Path(__file__).parent / "out" / f"max_flow_{p.material}.gcode"
    out.write_text(build(p))
    picture(p, out.with_suffix(".png"))
    print(out, f"{len(out.read_text().splitlines())} lines")
