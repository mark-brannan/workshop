"""1-wire bus board, two-row form: terminals back to back, wire entry facing opposite edges, MASTER at one end.

Row F (pin line y = 0, entry toward +y): one 9-position block (terminals 1-3), a one-hole gap, MASTER (3-position).
Row B (pin line y = -row_sep, entry toward -y): one 9-position block (terminals 4-6), mirrored.
The same three nets as the one-row board, no vias:
  G  top    trunk in the channel between the rows, stubs from both rows
  D  bottom trunk in the channel, stubs from both rows (crosses G only on the other layer)
  V  top    a trunk in front of each row (under its body), joined by a link past the left end
Optional 4k7 pull-up (R1, DATA to VCC) stands in the one-hole gap beside MASTER.
Writes out/two-row/. Shares Params, render and the fab step with model.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from shop.testing import load_model

_m = load_model(__file__)
NET_NAMES, NETS, PITCH, Params, render = _m.NET_NAMES, _m.NETS, _m.PITCH, _m.Params, _m.render


@dataclass
class Params2(Params):
    row_sep: float = 7.62       # pin line to pin line: 3 pitches, bodies back to back
    g_off: float = 5.08         # G trunk behind row F's pin line; MASTER's G pin sits on it
    lip: float = 3.0            # board past the wire-entry face: room for the G D V and terminal labels
    v_link_x: float = -2.0      # V link, left of the first pin
    field_block: int = 9        # pins in each field block
    master_hole: int = 11       # MASTER's pin column, in holes from the first pin (R1 stands in the gap before it)


def build(p: Params2 = Params2()) -> dict:
    S, nf = p.row_sep, p.field_block
    pads, bodies, groups = [], [], []
    xm = p.master_hole * PITCH
    for ref, row, labels in (("J1", "F", ["1", "2", "3"]), ("J2", "B", ["4", "5", "6"])):
        y = 0.0 if row == "F" else -S
        for i in range(nf):
            x = i * PITCH if row == "F" else (nf - 1 - i) * PITCH      # B is rotated 180: pad 1 on the right
            pads.append({"ref": ref, "num": i + 1, "net": NETS["GDV"[i % 3]], "x": x, "y": y, "d": p.pad_d,
                         "drill": p.drill, "row": row, "n": nf})
        x0, x1 = -p.end_gap, (nf - 1) * PITCH + p.end_gap
        bodies.append((x0, -p.back_to_pin, x1, p.front_to_pin) if row == "F"
                      else (x0, y - p.front_to_pin, x1, y + p.back_to_pin))
        groups += [(row, (3 * g + 1) * PITCH, lab) for g, lab in enumerate(labels)]
    ym = -S / 2
    for i in range(3):                                                 # MASTER: pin column, entry toward +x
        pads.append({"ref": "J3", "num": i + 1, "net": NETS["GDV"[i]], "x": xm, "y": -p.g_off + i * PITCH,
                     "d": p.pad_d, "drill": p.drill, "row": "M", "n": 3})
    bodies.append((xm - p.back_to_pin, -p.g_off + PITCH - 3 * PITCH / 2, xm + p.front_to_pin, -p.g_off + PITCH + 3 * PITCH / 2))
    tracks = []

    def seg(a, b, layer, net):
        if a != b:
            tracks.append({"x1": a[0], "y1": a[1], "x2": b[0], "y2": b[1], "layer": layer, "net": net,
                           "w": p.track_w if net == NETS["D"] else p.power_w})

    yg, yd = -p.g_off, -p.d_off
    yv = {"F": p.v_off, "B": -S - p.v_off, "M": p.v_off}
    for net, y, layer in ((NETS["G"], yg, "F.Cu"), (NETS["D"], yd, "B.Cu")):
        pp = sorted((q for q in pads if q["net"] == net), key=lambda q: q["x"])
        for q in pp:
            seg((q["x"], q["y"]), (q["x"], y), layer, net)
        seg((pp[0]["x"], y), (pp[-1]["x"], y), layer, net)
    for rows in ("FM", "B"):
        pp = sorted((q for q in pads if q["net"] == NETS["V"] and q["row"] in rows), key=lambda q: q["x"])
        y = yv[rows[0]]
        for q in pp:
            seg((q["x"], q["y"]), (q["x"], y), "F.Cu", NETS["V"])
        seg((p.v_link_x, y), (pp[-1]["x"], y), "F.Cu", NETS["V"])
    seg((p.v_link_x, yv["F"]), (p.v_link_x, yv["B"]), "F.Cu", NETS["V"])

    resistor = None
    if p.pullup:
        xr = (xm - p.back_to_pin + (nf - 1) * PITCH + p.end_gap) / 2    # middle of the gap before MASTER
        rv, rd = (xr, ym + p.r_pitch / 2), (xr, ym - p.r_pitch / 2)
        pads.append({"ref": "R1", "num": 1, "net": NETS["V"], "x": rv[0], "y": rv[1], "d": p.r_pad_d, "drill": p.r_drill})
        pads.append({"ref": "R1", "num": 2, "net": NETS["D"], "x": rd[0], "y": rd[1], "d": p.r_pad_d, "drill": p.r_drill})
        seg(rv, (xr, yv["F"]), "F.Cu", NETS["V"])
        seg(rd, (xr, yd), "B.Cu", NETS["D"])
        resistor = (xr, rv[1], rd[1])
    hl = p.v_link_x - p.power_w / 2 - 3.5 - 0.3
    hr = xm + p.front_to_pin + p.mount_keepout
    outline = (hl - p.mount_inset, -S - p.front_to_pin - p.lip, hr + p.mount_inset, p.front_to_pin + p.lip)
    x0, y0, x1, y1 = outline
    holes = [(hx, hy) for hx in (hl, hr) for hy in (y0 + p.mount_inset, y1 - p.mount_inset)]
    silk = []
    for row, x, lab in groups:
        sgn = 1 if row == "F" else -1
        silk.append((x, (0 if row == "F" else -S) + sgn * (p.front_to_pin + 2.2), lab, "F.SilkS", 1.0, 0 if sgn == 1 else 180))
    for q in pads:
        if q["ref"] in ("J1", "J2"):
            sgn = 1 if q["row"] == "F" else -1
            silk.append((q["x"], q["y"] + sgn * (p.front_to_pin + 0.8), "GDV"[(q["num"] - 1) % 3], "F.SilkS", 1.0,
                         0 if sgn == 1 else 180))
        elif q["ref"] == "J3":
            silk.append((xm + p.front_to_pin + 0.8, q["y"], "GDV"[q["num"] - 1], "F.SilkS", 1.0, 0))
    silk.append((xm + p.front_to_pin + 2.2, ym, "MASTER", "F.SilkS", 1.0, 90))
    if resistor:
        silk.append((resistor[0], ym + 1.2, "4k7", "F.SilkS", 0.9, 90))
    silk.append(((x0 + x1) / 2, y0 + 1.4, f"1-WIRE BUS  G=GND  D=DATA  V=+V   rev {p.rev}", "B.SilkS", 1.0, 0))
    return {"pads": pads, "tracks": tracks, "outline": outline, "holes": holes, "bodies": bodies,
            "resistor": resistor, "p": p, "silk": silk, "fig": (12, 8),
            "titles": ("Top copper: G down the channel, V in front of each row, linked at the left; entry faces the top, bottom and right edges",
                       "Bottom copper: D, one trace down the channel")}


def to_kicad(b: dict) -> str:
    p = b["p"]
    o = ['(kicad_pcb (version 20221018) (generator "workshop")', ' (general (thickness 1.6))', ' (paper "A4")',
         ' (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "B.Silkscreen") '
         '(37 "F.SilkS" user "F.Silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (44 "Edge.Cuts" user) (49 "F.Fab" user))',
         f' (setup (pad_to_mask_clearance {p.mask_expansion}))', ' (net 0 "")']
    o += [f' (net {n} "{NET_NAMES[n]}")' for n in (1, 2, 3)]
    ox, oy = 100.0, 100.0
    for ref, grp in _by_ref(b["pads"]).items():
        if ref == "R1":
            xr, yv_, yd_ = b["resistor"]
            o.append(f' (footprint "workshop:R_Axial_P7.62mm" (layer "F.Cu") (at {ox + xr:.3f} {oy + yv_:.3f})')
            o.append('  (fp_text reference "R1" (at 0 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')
            for q, yy in zip(grp, (0.0, yd_ - yv_)):
                o.append(f'  (pad "{q["num"]}" thru_hole circle (at 0 {yy:.3f}) (size {p.r_pad_d} {p.r_pad_d}) '
                         f'(drill {p.r_drill}) (layers "*.Cu" "*.Mask") (net {q["net"]} "{NET_NAMES[q["net"]]}"))')
            o.append(' )')
            continue
        q0 = grp[0]
        back = q0["row"] == "B"
        if q0["row"] == "M":
            at = f'{ox + q0["x"]:.3f} {oy + min(q["y"] for q in grp):.3f} 270'
        else:
            anchor = max(q["x"] for q in grp) if back else min(q["x"] for q in grp)
            at = f'{ox + anchor:.3f} {oy + q0["y"]:.3f}{" 180" if back else ""}'
        o.append(f' (footprint "workshop:ScrewBlock_1x{q0["n"]}_P2.54mm" (layer "F.Cu") (at {at})')
        o.append(f'  (fp_text reference "{ref}" (at 0 -1.9) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')
        for q in sorted(grp, key=lambda q: q["num"]):
            o.append(f'  (pad "{q["num"]}" thru_hole {"rect" if q["num"] == 1 else "circle"} (at {(q["num"] - 1) * PITCH:.3f} 0) '
                     f'(size {p.pad_d} {p.pad_d}) (drill {p.drill}) (layers "*.Cu" "*.Mask") (net {q["net"]} "{NET_NAMES[q["net"]]}"))')
        o.append(' )')
    for k, (hx, hy) in enumerate(b["holes"]):
        o.append(f' (footprint "workshop:MountingHole_M3" (layer "F.Cu") (at {ox + hx:.3f} {oy + hy:.3f})')
        o.append(f'  (fp_text reference "H{k + 1}" (at 0 0) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))')
        o.append(f'  (pad "" np_thru_hole circle (at 0 0) (size {p.mount_d} {p.mount_d}) (drill {p.mount_d}) (layers "*.Cu" "*.Mask"))')
        o.append(' )')
    for s in b["tracks"]:
        o.append(f' (segment (start {ox + s["x1"]:.3f} {oy + s["y1"]:.3f}) (end {ox + s["x2"]:.3f} {oy + s["y2"]:.3f}) '
                 f'(width {s["w"]}) (layer "{s["layer"]}") (net {s["net"]}))')
    for bx0, by0, bx1, by1 in b["bodies"]:
        o.append(f' (gr_rect (start {ox + bx0:.3f} {oy + by0:.3f}) (end {ox + bx1:.3f} {oy + by1:.3f}) (layer "F.SilkS") (width 0.12) (fill none))')
    for x, y, text, layer, size, rot in b["silk"]:
        mirror = " (justify mirror)" if layer == "B.SilkS" else ""
        o.append(f' (gr_text "{text}" (at {ox + x:.3f} {oy + y:.3f} {rot}) (layer "{layer}") '
                 f'(effects (font (size {size} {size}) (thickness 0.15)){mirror}))')
    x0, y0, x1, y1 = b["outline"]
    for (a, c, d, e) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        o.append(f' (gr_line (start {ox + a:.3f} {oy + c:.3f}) (end {ox + d:.3f} {oy + e:.3f}) (layer "Edge.Cuts") (width 0.1))')
    o.append(')')
    return "\n".join(o) + "\n"


def _by_ref(pads: list) -> dict:
    out: dict = {}
    for q in pads:
        out.setdefault(q["ref"], []).append(q)
    return out


def main() -> None:
    out = Path(__file__).parent / "out" / "two-row"
    out.mkdir(parents=True, exist_ok=True)
    b = build()
    (out / "one-wire-bus-2row.kicad_pcb").write_text(to_kicad(b))
    render(b, out / "one-wire-bus-2row.png")
    from shop import pcbfab
    print(pcbfab.fab(out / "one-wire-bus-2row.kicad_pcb", out / "fab"))
    x0, y0, x1, y1 = b["outline"]
    w, h = x1 - x0, y1 - y0
    print(f"board {w:.1f} x {h:.1f} mm, {len(b['pads'])} pads; ${w * h / 645.16 * 5:.2f} per lot of 3")


if __name__ == "__main__":
    main()
