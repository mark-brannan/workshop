"""Flow-ratio test for the K2 Plus: a grid of solid tiles, one flow ratio each.

Same idea as OrcaSlicer's flow-rate calibration (YOLO mode), written as g-code directly so it can be
started over Moonraker without the slicer GUI. Layer 1 prints at the profile's flow so every tile sticks
the same; layers 2..N print at the tile's own ratio. Pick the tile whose top is smoothest with no gaps
between lines and no ridges; that ratio goes into the filament profile.

    uv run python projects/calibration/flow_ratio.py [ASA-CF|PETG]   # writes out/flow_ratio_<material>.gcode
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class P:
    material: str = "ASA-CF"
    tool: int | None = None  # None: external spool, no tool change, prints what is in the toolhead. n: CFS via T<n>
    nozzle: int = 270
    bed: int = 90
    fan: int = 20  # percent
    base_flow: float = 0.92  # layer 1, the profile's current value
    ratios: list[float] = field(default_factory=lambda: [round(0.88 + 0.01 * i, 2) for i in range(13)])
    tile: float = 22.0
    gap: float = 5.0
    tab: float = 10.0  # label tab on each tile's front edge, flow x100 raised on it
    tab_layers: int = 3
    digit_layers: int = 4  # raised 0.8 mm above the tab
    cols: int = 7
    origin: tuple[float, float] = (80.0, 150.0)  # front-left of the first tile
    h: float = 0.2
    layers: int = 7  # 1.4 mm tiles; the digits need the height
    w: float = 0.42
    w1: float = 0.5  # first layer line width
    v_wall: float = 60.0  # mm/s
    v_fill: float = 100.0  # 0.42 x 0.2 at 100 mm/s = 7.5 mm3/s, well under the 12 cap
    v1: float = 40.0  # first layer
    v_travel: float = 300.0
    retract: float = 0.8
    zhop: float = 0.4
    fil_d: float = 1.75


def area(w: float, h: float) -> float:
    """Orca's extrusion cross-section: a rectangle with semicircular sides."""
    return (w - h) * h + math.pi * h * h / 4


def spacing(w: float, h: float) -> float:
    return w - h * (1 - math.pi / 4)


def tile_origins(p: P) -> list[tuple[float, float]]:
    out = []
    for i, _ in enumerate(p.ratios):
        r, c = divmod(i, p.cols)
        out.append((p.origin[0] + c * (p.tile + p.gap), p.origin[1] + p.tab + r * (p.tile + p.tab + p.gap)))
    return out


class G:
    def __init__(self, p: P):
        self.p, self.lines, self.x, self.y, self.z, self.e_total = p, [], 0.0, 0.0, 0.0, 0.0
        self.fil = math.pi * (p.fil_d / 2) ** 2

    def emit(self, s: str):
        self.lines.append(s)

    def travel(self, x: float, y: float):
        p = self.p
        self.emit(f"G1 E{-p.retract:.3f} F2400")
        self.emit(f"G1 Z{self.z + p.zhop:.3f} F3000")
        self.emit(f"G1 X{x:.3f} Y{y:.3f} F{p.v_travel * 60:.0f}")
        self.emit(f"G1 Z{self.z:.3f} F3000")
        self.emit(f"G1 E{p.retract:.3f} F2400")
        self.x, self.y = x, y

    def extrude(self, x: float, y: float, w: float, flow: float, v: float):
        d = math.hypot(x - self.x, y - self.y)
        e = flow * area(w, self.p.h) * d / self.fil
        self.e_total += e
        self.emit(f"G1 X{x:.3f} Y{y:.3f} E{e:.5f} F{v * 60:.0f}")
        self.x, self.y = x, y


def tile(g: G, x0: float, y0: float, layer: int, flow: float, w: float, v_wall: float, v_fill: float,
         sx: float | None = None, sy: float | None = None):
    p = g.p
    sx = sx or p.tile
    sy = sy or p.tile
    s = spacing(w, p.h)
    # two perimeters, outer first inward
    for k in range(2):
        a = w / 2 + k * s
        pts = [(x0 + a, y0 + a), (x0 + sx - a, y0 + a), (x0 + sx - a, y0 + sy - a), (x0 + a, y0 + sy - a)]
        g.travel(*pts[0])
        for q in pts[1:] + pts[:1]:
            g.extrude(*q, w, flow, v_wall)
    # solid fill inside, lines alternating X / Y per layer
    lo = w / 2 + 1.5 * s  # fill line centres start half a spacing inside perimeter 2
    span_c = sy if layer % 2 == 0 else sx  # across the lines
    span_l = sx if layer % 2 == 0 else sy  # along the lines
    n = int((span_c - 2 * lo) / s) + 1
    along_x = layer % 2 == 0
    for i in range(n):
        c = lo + i * s
        a, b = (lo, span_l - lo) if i % 2 == 0 else (span_l - lo, lo)
        if along_x:
            start, end = (x0 + a, y0 + c), (x0 + b, y0 + c)
        else:
            start, end = (x0 + c, y0 + a), (x0 + c, y0 + b)
        if i == 0:
            g.travel(*start)
        else:
            g.extrude(*start, w, flow, v_fill)  # short connector
        g.extrude(*end, w, flow, v_fill)


SEG = {  # 7-segment strokes per digit, unit box 0..1 wide, 0..2 tall
    "a": ((0, 2), (1, 2)), "b": ((1, 2), (1, 1)), "c": ((1, 1), (1, 0)), "d": ((1, 0), (0, 0)),
    "e": ((0, 0), (0, 1)), "f": ((0, 1), (0, 2)), "g": ((0, 1), (1, 1)),
}
DIGITS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
          "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def label(g: G, x0: float, y0: float, text: str, flow: float):
    """Raised 7-segment digits centred on the tab under tile (x0, y0)."""
    p = g.p
    u, pitch = 3.5, 5.6  # digit width (height 2u = 7 mm) and advance
    xs = x0 + (p.tile - (len(text) - 1) * pitch - u) / 2
    ys = y0 - p.tab + (p.tab - 2 * u) / 2
    for k, ch in enumerate(text):
        ox = xs + k * pitch
        for sname in DIGITS[ch]:
            (ax, ay), (bx, by) = SEG[sname]
            g.travel(ox + ax * u, ys + ay * u)
            g.extrude(ox + bx * u, ys + by * u, 0.6, flow, 20.0)  # one wide line per stroke


def build(p: P) -> str:
    g = G(p)
    orgs = tile_origins(p)
    xs = [o[0] for o in orgs]
    ys = [o[1] for o in orgs]
    minx, miny, maxx, maxy = min(xs), min(ys) - p.tab, max(xs) + p.tile, max(ys) + p.tile
    for li in range(p.layers):
        g.z = p.h * (li + 1)
        g.emit(";LAYER_CHANGE")
        g.emit(f";Z:{g.z:.2f}")
        g.emit("G92 E0")
        if li == 1:
            g.emit(f"M106 S{round(255 * p.fan / 100)}")
        first = li == 0
        for (x0, y0), r in zip(orgs, p.ratios):
            g.emit(f"; tile flow {r:.2f}")
            tile(g, x0, y0, li, p.base_flow if first else r, p.w1 if first else p.w,
                 p.v1 if first else p.v_wall, p.v1 if first else p.v_fill)
        for (x0, y0), r in zip(orgs, p.ratios):
            if li < p.tab_layers:
                g.emit(f"; label tab {r:.2f}")
                tile(g, x0, y0 - p.tab, li, p.base_flow, p.w1 if first else p.w,
                     p.v1 if first else p.v_wall, p.v1 if first else p.v_fill, sx=p.tile, sy=p.tab)
            elif li < p.tab_layers + p.digit_layers:
                g.emit(f"; label digits {r:.2f}")
                label(g, x0, y0, str(round(r * 100)), p.base_flow)
    grams = g.e_total * g.fil * 1.1 / 1000
    head = [
        "; HEADER_BLOCK_START",
        "; generated by OrcaSlicer 2.5.0 on 2026-11-18 at 00:00:00",
        "; (actually workshop projects/calibration/flow_ratio.py; header kept Orca-shaped for Moonraker metadata)",
        f"; total layer number: {p.layers}",
        f"; max_z_height: {p.h * p.layers:.2f}",
        "; HEADER_BLOCK_END",
        f"; flow ratios (x100 raised on each tile's front tab): {', '.join(f'{r:.2f}' for r in p.ratios)}",
        f"; MINX = {minx:.1f}", f"; MINY = {miny:.1f}", f"; MAXX = {maxx:.1f}", f"; MAXY = {maxy:.1f}",
        "M140 S0",
        "M104 S0",
        *(["BOX_ENABLE_CFS_PRINT ENABLE=0"] if p.tool is None else []),  # spool holder: CFS out of the print
        f"START_PRINT EXTRUDER_TEMP={p.nozzle} BED_TEMP={p.bed}",
        *([f"T{p.tool}"] if p.tool is not None else []),
        f"M109 S{p.nozzle}",
        "M204 S2000",
        "G1 Z3 F600",
        "M83",
        "G1 Y150 F12000",
        "G1 X0 F12000",
        "G1 Z0.2 F600",
        "G1 X0 Y150 F6000",
        "G1 X0 Y0 E15 F6000",
        "G1 X150 Y0 E15 F6000",
        "G92 E0",
        "G1 Z1 F600",
        "M106 S0",
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


PRESETS = {
    "ASA-CF": P(),
    # SUNLU PETG @System as last printed: flow 0.95, 245 C, bed 60, fan 10-30
    "PETG": P(material="PETG", nozzle=245, bed=60, fan=30, base_flow=0.95,
              ratios=[round(0.90 + 0.01 * i, 2) for i in range(13)]),
}

if __name__ == "__main__":
    import sys

    p = PRESETS[sys.argv[1] if len(sys.argv) > 1 else "ASA-CF"]
    out = Path(__file__).parent / "out" / f"flow_ratio_{p.material}.gcode"
    out.write_text(build(p))
    print(out, f"{len(out.read_text().splitlines())} lines")
