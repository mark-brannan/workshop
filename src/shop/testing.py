"""Load a project's model.py next to its test file without sys.path games.

Each projects/<name>/ has a model.py and a test_model.py; the directories are
not packages, so tests load the sibling module by path under a unique name.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load_model(test_file: str | Path, name: str = "model") -> ModuleType:
    here = Path(test_file).resolve().parent
    modname = f"{here.name.replace('-', '_')}_{name}"
    spec = importlib.util.spec_from_file_location(modname, here / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod
