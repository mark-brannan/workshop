"""Fab outputs for a KiCad board: rule check, Gerbers, drill file, upload zip, top and bottom pictures.

Runs kicad-cli from the box's own install, else from the kicad/kicad container; a box with neither skips.
The rule check uses OSH Park's 2-layer limits (docs.oshpark.com/design-tools/kicad/kicad-design-rules).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

IMAGE = "kicad/kicad:9.0"
LAYERS = "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"

OSHPARK_RULES = """(version 1)
(rule "oshpark clearance" (constraint clearance (min 0.1524mm)))
(rule "oshpark track width" (constraint track_width (min 0.1524mm)))
(rule "oshpark annular ring" (constraint annular_width (min 0.127mm)))
(rule "oshpark drill" (constraint hole_size (min 0.254mm)))
(rule "oshpark copper to hole" (constraint hole_clearance (min 0.127mm)))
(rule "oshpark hole to hole" (constraint hole_to_hole (min 0.127mm)))
(rule "oshpark edge keepout" (constraint edge_clearance (min 0.381mm)))
"""


def _runner(workdir: Path) -> list[str] | None:
    if shutil.which("kicad-cli"):
        return ["kicad-cli"]
    if shutil.which("docker") and subprocess.run(
            ["docker", "image", "inspect", IMAGE], capture_output=True).returncode == 0:
        return ["docker", "run", "--rm", "-u", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/tmp",
                "-v", f"{workdir}:{workdir}", "-w", str(workdir), IMAGE, "kicad-cli"]
    return None


def fab(pcb: Path, out: Path, picture: tuple = (2000, 420, 3.2)) -> str:
    """Check `pcb` and write its fab set under `out`. Returns a one-line summary; raises on a rule violation.
    `picture` is the top and bottom pictures' width, height and zoom: the default frames a long narrow board."""
    pcb, out = pcb.resolve(), out.resolve()
    root = pcb.parent
    assert out.is_relative_to(root), "fab output must sit under the board's folder"
    cli = _runner(root)
    if cli is None:
        return "pcbfab: no kicad-cli on this box, skipped"
    if out.exists():
        shutil.rmtree(out)
    gerbers = out / "gerbers"
    gerbers.mkdir(parents=True)

    def run(*args: str) -> None:
        r = subprocess.run([*cli, *args], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(f"kicad-cli {' '.join(args)}\n{r.stdout}{r.stderr}")

    rules = pcb.with_suffix(".kicad_dru")
    rules.write_text(OSHPARK_RULES)
    report = out / "drc.json"
    run("pcb", "drc", "--severity-all", "--format", "json", "-o", str(report), str(pcb))
    drc = json.loads(report.read_text())
    found = [v for v in drc.get("violations", []) + drc.get("unconnected_items", [])
             if v["type"] != "lib_footprint_issues"]   # generated boards carry their footprints inline
    if found:
        raise RuntimeError("rule check: " + "; ".join(f"{v['type']}: {v['description']}" for v in found))
    report.unlink()

    run("pcb", "export", "gerbers", "-o", str(gerbers) + "/", "--layers", LAYERS, "--subtract-soldermask", str(pcb))
    run("pcb", "export", "drill", "-o", str(gerbers) + "/", "--format", "excellon", "--drill-origin", "absolute",
        "--excellon-units", "mm", "--excellon-zeros-format", "decimal", "--excellon-oval-format", "alternate", str(pcb))
    for job in gerbers.glob("*.gbrjob"):
        job.unlink()
    files = sorted(gerbers.iterdir())
    bundle = out / f"{pcb.stem}-gerbers.zip"
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.writestr(zipfile.ZipInfo(f.name, (2020, 1, 1, 0, 0, 0)), f.read_bytes())  # fixed date: stable zip
    for side in ("top", "bottom"):
        run("pcb", "render", "--side", side, "--quality", "basic", "--background", "opaque",
            "-w", str(picture[0]), "-h", str(picture[1]), "--zoom", str(picture[2]), "-o", str(out / f"{side}.png"), str(pcb))
    return f"pcbfab: rule check clean, {len(files)} files in {bundle.relative_to(root)}"


def render3d(pcb: Path, png: Path, rotate: str = "-50,0,-25", zoom: float = 1.5) -> bool:
    """Perspective picture of `pcb` with whatever 3D models its footprints name. False when the box lacks KiCad."""
    pcb, png = pcb.resolve(), png.resolve()
    root = pcb.parent
    assert png.is_relative_to(root), "the picture must sit under the board's folder"
    cli = _runner(root)
    if cli is None:
        return False
    r = subprocess.run([*cli, "pcb", "render", "--quality", "high", "--background", "opaque", "--perspective", "--floor",
                        "--rotate", rotate, "--zoom", str(zoom), "-w", "2000", "-h", "1000", "-o", str(png), str(pcb)],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stdout + r.stderr)
    return True
