"""One build plate from many parts: ``shop plate plates/<name>.plate``.

A ``.plate`` file lists STL paths (repo-relative, one per line, ``#`` comments). Each part keeps its
print orientation, may turn 90° about Z, and is shelf-packed onto the K2 Plus bed. Writes
``plates/out/<name>.3mf`` (one named object per part, so the slicer can print by object), a merged
``.stl`` and PNGs. Rebuild after any part's ``shop build``; the plate reads the current STLs.
"""

from __future__ import annotations

import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh

from .build import ROOT

BED = (350.0, 350.0, 350.0)  # K2 Plus
MARGIN = 5.0  # bed edge to part
GAP = 8.0  # part to part


@dataclass
class Placed:
    name: str
    mesh: trimesh.Trimesh  # moved into bed coordinates


def read_plate(path: Path) -> list[Path]:
    lines = (ln.split("#", 1)[0].strip() for ln in path.read_text().splitlines())
    return [ROOT / ln for ln in lines if ln]


def pack(parts: list[tuple[str, trimesh.Trimesh]], bed=BED, margin=MARGIN, gap=GAP) -> list[Placed]:
    """Shelf-pack footprints, deepest first. Raises ValueError if a part won't fit."""
    prepped = []
    for name, m in parts:
        m = m.copy()
        ex = m.extents
        if ex[1] > ex[0]:  # long side along X
            m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (0, 0, 1)))
        m.apply_translation(-m.bounds[0])
        if m.extents[2] > bed[2]:
            raise ValueError(f"{name}: {m.extents[2]:.0f} mm tall, bed height {bed[2]:.0f}")
        prepped.append((name, m))
    prepped.sort(key=lambda nm: -nm[1].extents[1])

    placed, x, y, shelf = [], margin, margin, 0.0
    for name, m in prepped:
        w, d = m.extents[:2]
        if w > bed[0] - 2 * margin:
            raise ValueError(f"{name}: {w:.0f} mm wide, bed {bed[0]:.0f}")
        if x + w > bed[0] - margin:  # next shelf
            x, y, shelf = margin, y + shelf + gap, 0.0
        if y + d > bed[1] - margin:
            raise ValueError(f"{name}: plate full at y {y:.0f} mm; split the plate")
        m.apply_translation((x, y, 0))
        placed.append(Placed(name, m))
        x, shelf = x + w + gap, max(shelf, d)
    return placed


def write_3mf(placed: list[Placed], path: Path) -> None:
    objs, items = [], []
    for i, p in enumerate(placed, start=1):
        v = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in p.mesh.vertices)
        t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in p.mesh.faces)
        objs.append(f'<object id="{i}" name="{p.name}" type="model"><mesh><vertices>{v}</vertices>'
                    f"<triangles>{t}</triangles></mesh></object>")
        items.append(f'<item objectid="{i}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources>{"".join(objs)}</resources><build>{"".join(items)}</build></model>')
    types = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
             'content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
            'relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def build(plate: Path) -> Path:
    from .render import render_png

    parts = [(p.stem, trimesh.load(p, force="mesh")) for p in read_plate(plate)]
    placed = pack(parts)
    out = plate.parent / "out"
    out.mkdir(exist_ok=True)
    tmf = out / f"{plate.stem}.3mf"
    write_3mf(placed, tmf)
    stl = out / f"{plate.stem}.stl"
    trimesh.util.concatenate([p.mesh for p in placed]).export(stl)
    render_png(stl, out / f"{plate.stem}.png")
    vol = sum(p.mesh.volume for p in placed) / 1000
    for p in placed:
        (x0, y0, _), (x1, y1, z1) = p.mesh.bounds
        print(f"{p.name:36s} x {x0:5.0f}-{x1:5.0f}  y {y0:5.0f}-{y1:5.0f}  h {z1:4.0f}")
    print(f"{len(placed)} parts, {vol:.0f} cm³ -> {tmf.relative_to(ROOT)}")
    return tmf


def main(args: list[str]) -> int:
    if not args:
        print("shop plate plates/<name>.plate ...")
        return 2
    for a in args:
        build(Path(a).resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
