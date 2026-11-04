#!/bin/sh
# Put `shop` on PATH from this checkout. Safe to re-run; any box, any tools.
#   ~/workshop/setup.sh
# yadm bootstrap clones ~/workshop and runs this. Missing CAD apps are fine:
# `shop doctor` says what this box has, and builds skip what it lacks.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
command -v uv >/dev/null || { echo "setup.sh: uv not on PATH; install it first: https://docs.astral.sh/uv/" >&2; exit 1; }
uv tool install --quiet --force --editable "$here"
shop doctor
