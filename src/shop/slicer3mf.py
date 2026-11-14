"""Keep a slicer project's settings when a build rewrites its 3mf.

A 3mf the user has saved from OrcaSlicer/Bambu Studio (it carries ``Metadata/project_settings.config``)
holds their printer, filament and process settings. A plain rebuild would replace it with a bare mesh.
``carry`` is best effort:

* geometry unchanged: the user's file is put back byte for byte;
* geometry changed: the old file is archived under ``printed/`` beside it (``<name>.<sha8>.3mf``, kept
  for reference), and the new mesh is grafted into a copy of the user's project, so settings, plate and
  object placement survive. Stale thumbnails stay until the slicer next saves; reslice to be sure.
"""

from __future__ import annotations

import hashlib
import re
import zipfile
from io import BytesIO
from pathlib import Path

SETTINGS = "Metadata/project_settings.config"
MESH = re.compile(r"<mesh>.*?</mesh>", re.S)
VERTEX = re.compile(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"')
ITEM = re.compile(r'(<item\b[^>]*\btransform=")([^"]*)(")')
TOL = 1e-3


def read_prior(path: Path) -> bytes | None:
    """The existing file's bytes if it is a slicer project, else None."""
    path = Path(path)
    if not path.exists():
        return None
    data = path.read_bytes()
    try:
        with zipfile.ZipFile(BytesIO(data)) as z:
            return data if SETTINGS in z.namelist() else None
    except zipfile.BadZipFile:
        return None


def _verts(mesh: str) -> list[tuple[float, float, float]]:
    return [(float(x), float(y), float(z)) for x, y, z in VERTEX.findall(mesh)]


def _centre(mesh: str) -> tuple[str, float]:
    """The mesh recentred on its bounding box, and its height."""
    v = _verts(mesh)
    lo = [min(p[i] for p in v) for i in range(3)]
    hi = [max(p[i] for p in v) for i in range(3)]
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    mesh = VERTEX.sub(lambda m: f'<vertex x="{float(m[1]) - c[0]:.7g}" y="{float(m[2]) - c[1]:.7g}" z="{float(m[3]) - c[2]:.7g}"', mesh)
    return mesh, hi[2] - lo[2]


def _same(a: list, b: list) -> bool:
    return len(a) == len(b) and all(abs(p - q) <= TOL for u, w in zip(a, b) for p, q in zip(u, w))


def carry(prior: bytes | None, fresh_path: Path) -> str:
    """Fold ``prior`` (see ``read_prior``) into the freshly built ``fresh_path``; returns what it did."""
    if prior is None:
        return "no slicer settings to carry"
    fresh_path = Path(fresh_path)
    with zipfile.ZipFile(fresh_path) as z:
        fresh_model = z.read("3D/3dmodel.model").decode()
    new_mesh, height = _centre(MESH.search(fresh_model).group(0))

    zin = zipfile.ZipFile(BytesIO(prior))
    obj = next(n for n in zin.namelist() if n.startswith("3D/Objects/") and n.endswith(".model"))
    old_text = zin.read(obj).decode()
    if _same(_verts(MESH.search(old_text).group(0)), _verts(new_mesh)):
        fresh_path.write_bytes(prior)
        return "geometry unchanged: slicer project kept"

    sha = hashlib.sha256(prior).hexdigest()[:8]
    arch = fresh_path.parent / "printed" / f"{fresh_path.stem}.{sha}.3mf"
    arch.parent.mkdir(exist_ok=True)
    arch.write_bytes(prior)

    def fix_item(m):
        t = m[2].split()
        if len(t) == 12:
            t[11] = f"{height / 2:.7g}"
        return m[1] + " ".join(t) + m[3]

    out = BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == obj:
                data = MESH.sub(lambda _: new_mesh, old_text, count=1).encode()
            elif info.filename == "3D/3dmodel.model":
                data = ITEM.sub(fix_item, data.decode()).encode()
            zout.writestr(info, data)
    fresh_path.write_bytes(out.getvalue())
    return f"geometry changed: settings carried, previous project archived as {arch.name}"
