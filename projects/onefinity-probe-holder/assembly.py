"""The probe seated in the holder: how the lip's two legs meet the ledges. Writes out/assembly.png and out/assembly_sections.png.

    uv run python projects/onefinity-probe-holder/assembly.py   (shop build runs it after the model; reads the holder STL)

Lip (raised L on the machined face) orange, pocket floor blue, the holder's ledge faces green.
"""
import math
import re
import tempfile
from pathlib import Path

import matplotlib
import numpy as np
import pyvista as pv
import shapely
import shapely.ops
import trimesh

from shop.scad import OpenSCAD

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "out"
P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
T = math.radians(P["tilt"])
SLOT = P["probe_t"] + 2 * P["fit_t"]
Z_CUT = P["open_v"] * math.cos(T) - SLOT / 2 * math.sin(T)
HOLDER, PROBE, LIP, POCKET, LEDGE = "#b9a8e0", "#9aa3ad", "#ff9a3c", "#4f8fd6", "#3fbf6f"


def world(u, v, w):
    """Probe frame (u across, v up the face, w through it, +w the support wall) to world, as placed() in model.scad."""
    y, z = -w, v
    return np.array((u, y * math.cos(T) - z * math.sin(T), y * math.sin(T) + z * math.cos(T) - Z_CUT))


def wdir(u, v, w):
    return world(u, v, w) - world(0, 0, 0)


def pe(s, n):
    """(s along the seated probe's lower-right edge from its point, n inward) to (u, v), as pe() in model.scad."""
    return (s - n) / math.sqrt(2), (s + n) / math.sqrt(2) - P["fit_v"] * math.sqrt(2)


W_LIP = -P["probe_t"] / 2 + P["fit_t"]  # the lip's face, wall side
W_POCKET = W_LIP + P["pocket_d"]
W_LEDGE = -P["probe_t"] / 2
TO_WALL = wdir(0, 0, -1)  # the normal of the lip, pocket floor; the ledges face the other way


def probe_mesh() -> trimesh.Trimesh:
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "probe.stl"
        OpenSCAD().run(HERE / "model.scad", stl, '-D', 'part="probe"')
        return trimesh.load(stl)


def face_colours(m: trimesh.Trimesh, base, faces):
    """Per-face colours: faces whose normal is `normal` and whose w is `w` take `colour`."""
    c = np.tile(np.array(matplotlib.colors.to_rgb(base)), (len(m.faces), 1))
    w = -(m.triangles_center - world(0, 0, 0)) @ TO_WALL
    for normal, wv, colour in faces:
        hit = (m.face_normals @ normal > 0.99) & (np.abs(w - wv) < 0.05)
        c[hit] = matplotlib.colors.to_rgb(colour)
    return (c * 255).astype(np.uint8)


def pv_parts(m, colours):
    """(pyvista mesh, colour) per colour: one add_mesh each, lit and shaded as usual."""
    out = []
    for c in np.unique(colours, axis=0):
        sub = m.submesh([np.where((colours == c).all(axis=1))[0]], append=True)
        out.append((pv.wrap(sub), "#%02x%02x%02x" % tuple(c)))
    return out


def three_d(holder, probe, path):
    hc = face_colours(holder, HOLDER, [(-TO_WALL, W_LEDGE, LEDGE)])
    pc = face_colours(probe, PROBE, [(TO_WALL, W_LIP, LIP), (TO_WALL, W_POCKET, POCKET)])
    # the wall plate and the sweep behind the ledges hidden, so the machined face shows from the wall side
    y_cut = world(0, 0, W_LEDGE - 4)[1]
    keep = holder.triangles_center[:, 1] < y_cut
    open_h = holder.submesh([np.where(keep)[0]], append=True)
    open_c = hc[keep]
    # everything on the user's side of the ledge faces hidden, so the ledges show through the probe
    wall_side = -(holder.triangles_center - world(0, 0, 0)) @ TO_WALL < W_LEDGE + 0.05
    back_h = holder.submesh([np.where(wall_side)[0]], append=True)
    back_c = hc[wall_side]
    panels = [
        ("seated, from the user's side", (0, -1, 0.35), (0, 0, 1), holder, hc, 1.0),
        ("from the wall, square to the machined face (holder behind the ledges cut away, see-through):\n"
         "green ledges over the orange lip's two legs", TO_WALL, (0, 0, 1), open_h, open_c, 0.55),
        ("from the user's side, square to the probe (see-through), support wall cut away:\n"
         "green ledge faces behind the orange lip legs", -TO_WALL, (0, 0, 1), back_h, back_c, 1.0),
        ("the probe alone, machined face: lip L orange, pocket blue", TO_WALL, (0, 0, 1), None, None, 1.0),
    ]
    pv.OFF_SCREEN = True
    p = pv.Plotter(off_screen=True, shape=(2, 2), window_size=(1800, 1800), border=True)
    for i, (label, vec, up, hm, hcol, op) in enumerate(panels):
        p.subplot(i // 2, i % 2)
        p.set_background("#202326")
        for part, col in pv_parts(probe, pc):
            p.add_mesh(part, color=col, opacity=0.4 if i == 2 else 1.0)
        if hm is not None:
            for part, col in pv_parts(hm, hcol):
                p.add_mesh(part, color=col, opacity=op if col != LEDGE else 1.0)
            p.add_mesh(pv.wrap(hm).extract_feature_edges(30), color="#111111", line_width=1.5)
        p.add_text(label, font_size=10, color="white")
        p.view_vector(tuple(vec), viewup=up)
        p.reset_camera()
        if i in (1, 2, 3):
            p.enable_parallel_projection()
    p.screenshot(str(path))
    p.close()


def section(m, s, origin_n=0.0):
    """Cut square to the probe's lower-right edge at s: 2D polygons in (x toward the wall, y into the probe)."""
    u, v = pe(s, origin_n)
    o = world(u, v, 0)
    e = wdir(1, 1, 0) / math.sqrt(2)
    x = TO_WALL
    y = wdir(-1, 1, 0) / math.sqrt(2)
    segs = trimesh.intersections.mesh_plane(m, plane_normal=e, plane_origin=o)
    if len(segs) == 0:
        return []
    xy = np.stack([(segs - o) @ x, (segs - o) @ y], axis=-1).round(4)
    lines = shapely.ops.linemerge([shapely.LineString(seg) for seg in xy if np.linalg.norm(seg[1] - seg[0]) > 1e-6])
    polys = list(shapely.ops.polygonize(lines))
    # nested rings come back as separate polygons: an odd nesting depth is a hole
    return [pp for pp in polys if sum(q.contains(pp.representative_point()) for q in polys if q is not pp) % 2 == 0]


def sections(holder, probe, path):
    lap = P["pocket_s"] + 2
    cuts = [
        (lap, f"across a lip leg, {lap:.0f} mm up the edge: the ledge laps the lip"),
        (P["pocket_s"] - 10, f"across the pocket, {P['pocket_s'] - 10:.0f} mm up: the ledge tapering in, the pocket floor well clear"),
    ]
    fig, axs = plt.subplots(1, 2, figsize=(16, 8), facecolor="#202326")
    for ax, (s, title) in zip(axs, cuts):
        ax.set_facecolor("#202326")
        for poly in section(holder, s):
            ax.fill(*poly.exterior.xy, color=HOLDER, ec="white", lw=0.6)
        for poly in section(probe, s):
            ax.fill(*poly.exterior.xy, color=PROBE, ec="white", lw=0.6, alpha=0.9)
        lip = -W_LIP
        ax.axvline(lip, color=LIP, lw=1, ls=":")
        ax.axvline(-W_LEDGE, color=LEDGE, lw=1, ls=":")
        ax.axvline(-W_POCKET, color=POCKET, lw=1, ls=":")
        ax.text(lip, 21, " lip face", color=LIP, fontsize=9, ha="right")
        ax.text(-W_LEDGE, 23, " ledge face", color=LEDGE, fontsize=9)
        ax.text(-W_POCKET, 19, "pocket floor ", color=POCKET, fontsize=9, ha="right")
        ax.text(-16, -8, "support wall side\n(toward the user)", color="white", fontsize=9)
        ax.text(14, -8, "wall plate side", color="white", fontsize=9)
        ax.set_title(title, color="white", fontsize=11)
        ax.set_xlim(-22, 26)
        ax.set_ylim(-12, 26)
        ax.set_aspect("equal")
        ax.tick_params(colors="#aaaaaa")
        ax.grid(color="#444444", lw=0.5)
        ax.set_xlabel("mm through the probe (toward the wall)", color="#aaaaaa")
        ax.set_ylabel("mm in from the probe's lower edge", color="#aaaaaa")
    fig.suptitle("Probe (grey) in the holder (purple), cut square to its lower-right edge", color="white")
    fig.tight_layout()
    fig.savefig(path, dpi=110, facecolor=fig.get_facecolor())
    plt.close(fig)


def lip_closeups(holder, probe, path):
    """Iso close-ups on the right side corner, where the lip leg meets its ledge, from each face's side (they face each other)."""
    hc = face_colours(holder, HOLDER, [(-TO_WALL, W_LEDGE, LEDGE)])
    pc = face_colours(probe, PROBE, [(TO_WALL, W_LIP, LIP), (TO_WALL, W_POCKET, POCKET)])
    wall_side = -(holder.triangles_center - world(0, 0, 0)) @ TO_WALL < W_LEDGE + 0.05
    no_support = holder.submesh([np.where(wall_side)[0]], append=True)
    up_edge = wdir(1, 1, 0) / math.sqrt(2)  # up the probe's lower-right edge
    across = wdir(-1, 1, 0) / math.sqrt(2)  # in from that edge, across the face
    f = world(*pe(P["pocket_s"] + 2, 2), (W_LIP + W_LEDGE) / 2)  # between lip and ledge, on the lap
    panels = [
        ("lip side: from the wall, above and outside the corner; holder see-through\n"
         "orange lip leg and blue pocket under the green ledge", TO_WALL + 0.7 * up_edge - 0.6 * across, holder, hc, 0.35, probe, 1.0, 0),
        ("ledge side: from the user, above and outside the corner; probe see-through, support wall cut away\n"
         "green ledge face, the orange lip leg behind it", -TO_WALL + 0.5 * up_edge + 0.5 * across + 0.4 * np.array((0, 0, 1)), no_support, hc[wall_side], 1.0, probe, 0.35, 0),
    ]
    pv.OFF_SCREEN = True
    p = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(2000, 1000), border=True)
    for i, (label, vec, hm, hcol, hop, pm, pop, g) in enumerate(panels):
        p.subplot(0, i)
        p.set_background("#202326")
        shift = -g * TO_WALL
        for part, col in pv_parts(pm, pc):
            p.add_mesh(part.translate(shift, inplace=False), color=col, opacity=pop)
        for part, col in pv_parts(hm, hcol):
            p.add_mesh(part, color=col, opacity=1.0 if col == LEDGE else hop)
        p.add_mesh(pv.wrap(hm).extract_feature_edges(30), color="#111111", line_width=1.5, opacity=max(hop, 0.4))
        p.add_text(label, font_size=9, color="white")
        foc = f + shift / 2
        p.camera.focal_point = tuple(foc)
        p.camera.position = tuple(foc + (110 if i == 0 else 150) * vec / np.linalg.norm(vec))
        p.camera.up = (0, 0, 1)
    p.screenshot(str(path))
    p.close()


def main():
    holder = trimesh.load(OUT / "onefinity-probe-holder_scad.stl")
    probe = probe_mesh()
    three_d(holder, probe, OUT / "assembly.png")
    lip_closeups(holder, probe, OUT / "assembly_lip.png")
    sections(holder, probe, OUT / "assembly_sections.png")
    for f in ("assembly.png", "assembly_lip.png", "assembly_sections.png"):
        print(OUT / f)


if __name__ == "__main__":
    main()
