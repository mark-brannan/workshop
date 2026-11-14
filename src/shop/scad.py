"""Build an OpenSCAD model the same way export_all builds a build123d one.

Whichever OpenSCAD this box has: ``$OPENSCAD``, a native ``openscad`` on
PATH, the macOS app, or the Windows install driven from WSL. For the Windows
exe, file arguments are converted with ``wslpath -w``; the repo is reachable
from Windows as a ``\\\\wsl.localhost`` UNC path. If the exe cannot write to a
UNC path the output is written to the Windows temp dir and moved back.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import ezdxf

from . import slicer3mf
from .render import render_png

# Searched after $OPENSCAD and a native ``openscad`` on PATH, in this order.
CANDIDATES = (
    Path("/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"),  # macOS
    Path("/mnt/c/Program Files/OpenSCAD (Nightly)/openscad.exe"),  # WSL: dev snapshot, preferred
    Path("/mnt/c/Program Files/OpenSCAD/openscad.exe"),  # WSL: 2021.01
)
WIN_TEMP = Path("/mnt/c/Users/Solace/AppData/Local/Temp")
ISO_CAMERA = "0,0,0,55,0,25,200"  # gimbal: tx,ty,tz,rx,ry,rz,dist; dist/translate overridden by --viewall/--autocenter


def find_openscad() -> Path | None:
    env = os.environ.get("OPENSCAD")
    if env and Path(env).exists():
        return Path(env)
    native = shutil.which("openscad")
    if native:
        return Path(native)
    for c in CANDIDATES:
        if c.exists():
            return c
    return None


def _winpath(p: Path) -> str:
    return subprocess.run(["wslpath", "-w", str(p)], check=True, capture_output=True, text=True).stdout.strip()


class OpenSCAD:
    def __init__(self, exe: Path | None = None):
        self.exe = exe or find_openscad()
        if self.exe is None:
            raise FileNotFoundError("openscad not found; set OPENSCAD=/path/to/openscad")
        self.windows = self.exe.suffix.lower() == ".exe"  # Windows exe driven from WSL
        self._help: str | None = None
        self.staged = False  # route files through the Windows temp dir (see run)

    def version(self) -> str:
        r = subprocess.run([str(self.exe), "--version"], capture_output=True, text=True)
        return (r.stdout + r.stderr).strip()

    def help(self) -> str:
        if self._help is None:
            r = subprocess.run([str(self.exe), "--help"], capture_output=True, text=True)
            self._help = r.stdout + r.stderr
        return self._help

    def backend_args(self) -> list[str]:
        return ["--backend=manifold"] if "--backend" in self.help() else []

    def run(self, scad: Path, out: Path, *args: str) -> subprocess.CompletedProcess:
        """Run ``openscad -o out args scad``.

        UNC paths first (2021.01 reads and writes them). The 2026 nightly cannot
        chdir to a ``\\\\wsl.localhost`` input dir and does not land output on one
        either, so on failure the project's ``*.scad`` files are staged in the
        Windows temp dir and the output moved back; once that works it is used
        for the rest of this instance's calls.
        """
        out.parent.mkdir(parents=True, exist_ok=True)
        base = [str(self.exe), *self.backend_args(), *args]
        if not self.windows:
            cmd = [base[0], "-o", str(out), *base[1:], str(scad)]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0 and out.exists():
                return r
            raise RuntimeError(f"openscad failed ({r.returncode}): {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
        r = None
        if not self.staged:
            cmd = [base[0], "-o", _winpath(out), *base[1:], _winpath(scad)]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0 and out.exists():
                return r
        if WIN_TEMP.is_dir():
            stage = WIN_TEMP / f"shop_{os.getpid()}"
            stage.mkdir(exist_ok=True)
            for f in (*scad.parent.glob("*.scad"), *scad.parent.glob("*.stl")):  # .stl: import() inputs
                shutil.copy(f, stage / f.name)
            s_out = stage / out.name
            cmd = [base[0], "-o", _winpath(s_out), *base[1:], _winpath(stage / scad.name)]
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=stage)
            if r.returncode == 0 and s_out.exists():
                shutil.move(str(s_out), str(out))
                self.staged = True
                return r
        raise RuntimeError(f"openscad failed ({r.returncode}): {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")

    def cleanup(self) -> None:
        shutil.rmtree(WIN_TEMP / f"shop_{os.getpid()}", ignore_errors=True)


# Layer name -> RGB. LightBurn assigns imported DXF geometry to its layers by
# colour, not by layer name, so each name carries a LightBurn palette colour
# (00 black, 01 blue, 02 red). Names match the build123d exports ("cut").
LIGHTBURN_LAYERS = {
    "cut": (255, 0, 0),  # LightBurn 02
    "score": (0, 0, 255),  # LightBurn 01
    "engrave": (0, 0, 0),  # LightBurn 00
}


def finish_dxf(parts: dict[str, Path], out: Path) -> Path:
    """Merge raw OpenSCAD DXFs into one R2010 DXF in millimetres, one layer each.

    ``parts`` maps a LightBurn layer name to the raw DXF whose geometry goes on
    it. OpenSCAD writes no units and puts everything on layer ``0``; the output
    has ``$INSUNITS`` 4 (mm), each layer named and coloured, and every entity
    on its layer with colour BYLAYER. Lines and polylines are copied as is.
    """
    doc = ezdxf.new("R2010", units=ezdxf.units.MM)
    doc.header["$MEASUREMENT"] = 1  # metric
    msp = doc.modelspace()
    for name, src in parts.items():
        layer = doc.layers.add(name)
        layer.rgb = LIGHTBURN_LAYERS[name]
        attribs = {"layer": name}
        for e in ezdxf.readfile(src).modelspace():
            kind = e.dxftype()
            if kind == "LINE":
                msp.add_line(e.dxf.start, e.dxf.end, dxfattribs=attribs)
            elif kind == "LWPOLYLINE":
                msp.add_lwpolyline(e.get_points(), format="xyseb", close=e.closed, dxfattribs=attribs)
            else:
                raise ValueError(f"{src}: unexpected {kind} from OpenSCAD")
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(out)
    return out


def has_mode_variable(scad_path: Path) -> bool:
    return re.search(r'^\s*mode\s*=\s*"', scad_path.read_text(), re.M) is not None


def build_scad(scad_path: Path | str, outdir: Path | str, name: str, two_d: bool = False, *, render: bool = True, threemf: bool = False) -> dict:
    """Write ``name``.stl (and .dxf when ``two_d``, .3mf when asked) plus PNGs into ``outdir``.

    The DXF is in millimetres with its geometry on the LightBurn layer ``cut``
    (see ``finish_dxf``).

    For a 2D model that exposes ``mode = "2d"`` the STL is the extruded form
    (``-D mode="3d"``). Returns format -> path, plus ``times`` (seconds) and
    ``version``; render failures are recorded under ``render_error``.
    """
    scad_path, outdir = Path(scad_path), Path(outdir)
    osc = OpenSCAD()
    paths: dict = {"version": osc.version(), "times": {}}
    t0 = time.perf_counter()
    three_d: list[str] = ["-D", 'mode="3d"'] if two_d and has_mode_variable(scad_path) else []
    if two_d:
        dxf = outdir / f"{name}.dxf"
        raw = outdir / f"{name}.raw.dxf"
        osc.run(scad_path, raw)
        finish_dxf({"cut": raw}, dxf)
        raw.unlink()
        paths["dxf"] = dxf
    if not two_d or three_d:
        stl = outdir / f"{name}.stl"
        osc.run(scad_path, stl, *three_d)
        paths["stl"] = stl
    if threemf:
        tmf = outdir / f"{name}.3mf"
        prior = slicer3mf.read_prior(tmf)
        osc.run(scad_path, tmf, *three_d)
        paths["3mf"] = tmf
        if prior is not None:
            paths["3mf_note"] = slicer3mf.carry(prior, tmf)
    paths["times"]["export"] = time.perf_counter() - t0

    if render:
        t1 = time.perf_counter()
        png = outdir / f"{name}.png"
        try:
            osc.run(
                scad_path, png, *three_d,
                "--render", "--autocenter", "--viewall", "--imgsize=1200,900",
                "--colorscheme=Tomorrow", f"--camera={ISO_CAMERA}",
            )
            paths["png"] = png
        except RuntimeError as e:
            paths["render_error"] = str(e)
        paths["times"]["render_openscad"] = time.perf_counter() - t1
        if "stl" in paths:
            t2 = time.perf_counter()
            try:
                pngs = render_png(paths["stl"], outdir / f"{name}_pv.png")
                paths["png_pv"] = pngs[0]
                if len(pngs) > 1:
                    paths["png_views"] = pngs[1]
            except Exception as e:  # noqa: BLE001
                paths["render_error"] = f"{type(e).__name__}: {e}"
            paths["times"]["render_pyvista"] = time.perf_counter() - t2
    osc.cleanup()
    return paths
