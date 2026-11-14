"""Export one build123d Part to every fab format at once."""

from __future__ import annotations

from pathlib import Path

from build123d import Mesher, Part, export_step, export_stl

from . import slicer3mf
from .render import render_png


def export_all(part: Part, name: str, outdir: Path | str, *, render: bool = True) -> dict[str, Path]:
    """Write ``name``.stl/.3mf/.step and PNG renders into ``outdir``.

    Returns a dict of format -> path. If rendering fails the error string is
    stored under ``render_error`` and the geometry exports still succeed.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    stl = outdir / f"{name}.stl"
    export_stl(part, stl, tolerance=0.01, angular_tolerance=0.1)
    paths["stl"] = stl

    threemf = outdir / f"{name}.3mf"
    prior = slicer3mf.read_prior(threemf)
    m = Mesher()
    m.add_shape(part, linear_deflection=0.01, angular_deflection=0.1)
    m.add_meta_data("shop", "name", name, "str", must_preserve=False)
    m.write(threemf)
    paths["3mf"] = threemf
    if prior is not None:
        slicer3mf.carry(prior, threemf)

    step = outdir / f"{name}.step"
    export_step(part, step)
    paths["step"] = step

    if render:
        try:
            pngs = render_png(stl, outdir / f"{name}.png")
            paths["png"] = pngs[0]
            if len(pngs) > 1:
                paths["png_views"] = pngs[1]
        except Exception as e:  # noqa: BLE001 - report, don't abort exports
            paths["render_error"] = f"{type(e).__name__}: {e}"  # type: ignore[assignment]
    return paths
