"""Which shop tools this box has. Every box differs; missing is normal, not an error."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from .scad import find_openscad

WIN = Path("/mnt/c")  # WSL view of the Windows drive


@dataclass
class Tool:
    name: str
    role: str
    path: Path | None


def _first(*paths: Path | str | None) -> Path | None:
    for p in paths:
        if p and Path(p).exists():
            return Path(p)
    return None


def _win_appdata(sub: str) -> list[Path]:
    users = WIN / "Users"
    return sorted(users.glob(f"*/AppData/Local/{sub}")) if users.is_dir() else []


def detect() -> list[Tool]:
    which = shutil.which
    return [
        Tool("OpenSCAD", "default modeller", find_openscad()),
        Tool("OrcaSlicer", "print", _first(
            which("orca-slicer"),
            "/Applications/OrcaSlicer.app",
            WIN / "Program Files/OrcaSlicer/orca-slicer.exe",
            *sorted((WIN / "Users").glob("*/AppData/Local/Microsoft/WindowsApps/orca-slicer.exe")),
        )),
        Tool("LightBurn", "laser", _first(
            which("lightburn"),
            "/Applications/LightBurn.app",
            WIN / "Program Files/LightBurn/LightBurn.exe",
        )),
        Tool("Fusion 360", "STL merge script, CAM", _first(
            "/Applications/Autodesk Fusion.app",
            "/Applications/Autodesk Fusion 360.app",
            Path.home() / "Applications/Autodesk Fusion.app",  # Autodesk's Mac installer default
            *_win_appdata("Autodesk/webdeploy"),
        )),
    ]
