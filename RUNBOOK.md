# Runbook

What you can run yourself, by task. Every command works from any directory
once `~/workshop/setup.sh` has put `shop` on PATH. `shop` with no arguments
prints the list; `shop watch <cmd> --help` prints each one's flags.

## At a glance

| I want to… | Run |
|---|---|
| see which tools this box has | `shop doctor` |
| rebuild every part | `shop build` |
| rebuild one part (STL, 3MF, PNG) | `shop build projects/<slug>` |
| check a part from six sides | `shop views projects/<slug>/model.scad <view>` |
| print a thin fit-check before the real part | `shop gauge projects/<slug> "mount()" <z_plate> [<z_wall>]` |
| slice a 3MF to g-code, no GUI | `orca-slicer --slice 0 --outputdir <dir> <file.3mf>` |
| run every test | `uv run pytest -q` (from `~/workshop`) |
| see what the printer is doing | `shop printer` |
| check a job before starting it | `shop watch preflight <file.gcode> --plate frosted --vents closed` |
| heat-soak for an ASA or ABS job | `shop watch soak <file.gcode> --plate frosted` |
| start a job safely | `shop watch start <file.gcode> --plate frosted --vents closed` |
| start a job and watch it to the end; a cheap model checks each frame | `shop watch <file.gcode>` |
| watch whatever is printing now | `shop watch` |
| watch a running job, frame by frame | `shop watch next` |
| grab the camera frame after a layer | `shop watch frame <layer> out.jpg` |
| find the Fusion scripts folder | `shop fusion` |
| see which parts plug into the boat | `shop symphony` |

`<file.gcode>` is the name as the printer lists it (what OrcaSlicer uploaded),
not a path on this box.

## Make a part

```
shop build projects/<slug>
```

Writes `projects/<slug>/out/`: the 3MF to print, the STL, and a PNG to look at.
Warnings, never failures: a flat overhang and its unsupported span, a mesh that
is not a closed solid, geometry that changed when no `.scad` did. A 3MF you
saved from OrcaSlicer keeps its settings across a rebuild; when the mesh
changed, the old one is kept under `out/printed/`.

A project with a KiCad board (`one-wire-bus-board`) also writes its Gerbers,
drill file and upload zip on build.

## Slice headless

`orca-slicer` is a native OrcaSlicer, the same version as the user's
Windows install, from `scripts/install-orcaslicer-linux` or, on a Mac,
`scripts/install-orcaslicer-mac` (once per box; it is not in the repo). On a
Mac the user's presets are in `~/Library/Application Support/OrcaSlicer/user/`
(system presets are packed in `system/*.opc`); copy that folder as `--datadir`.

The CLI cannot resolve a preset's `inherits` from those packed bundles, so a
user preset file passed to `--load-settings` fails ("Preset was not found in
the loaded bundle"). With no saved project for the model, borrow the settings
of one that is: `scripts/orca-slice <saved.3mf> <model.3mf> <outdir> [--bed
"Textured PEI Plate"]` grafts its resolved settings onto the model and slices.
K2 Plus PETG at 0.20 Strength: `projects/shower-sump-platform/out/shower-sump-platform_scad.3mf`. It slices with the settings carried in a 3MF saved from
OrcaSlicer, so slice the user's saved project, not a bare mesh:

```
orca-slicer --datadir <scratch>/orca --slice 0 --outputdir <scratch> --export-3mf sliced.3mf <file.3mf>
```

Writes `plate_<n>.gcode` and the sliced 3MF to `--outputdir`, and `result.json`
(`"return_code": 0` on success) to the current directory, so run it from the
scratch dir. `--datadir` keeps the run from touching any GUI config. Check the
g-code header (`; printer_model`, `; filament_type`, `; total layers count`)
before uploading it.

## Print a high-temperature job (ASA, ABS)

The order the printer notes earned the hard way
([printer-notes.md](projects/k2-plus-mods/printer-notes.md)):

1. **Preflight.** Read-only; add `--fix` to send the fixes it names (Z lift, feed setting).
   Example output, trimmed:
   ```
   shop watch preflight box.gcode --plate frosted --vents closed
   ```
   ```
     ok    printer ready, job complete
     ok    file ASA-CF, bed 90, height 102.4 mm
     FAIL  Z 2.00 below 10: homing XY here drags the nozzle   fix: G90...
     ok    plate frosted rated 120 C, bed 90
     ok    rear vents closed
     ok    spool job, CFS printing off
     ok    macro HEAT_HOLD
     ok    macro BED_VIEW
     ok    patch: chamber check re-arms (verify_heater.py)
   preflight FAIL (1)
   ```
2. **Soak.** About 45 min from hot, an hour from cold. Passes once the bed has
   held target 45 min and the chamber reads 33 °C or more. Refuses a bed over
   the plate's rating unless `--over-rating`.
   ```
   shop watch soak box.gcode --plate frosted
   ```
3. **Start.** Runs preflight with fixes, re-sends the CFS setting the screen
   undoes when idle, starts the job, and checks it is printing within 60 s.
   Add `--cfs` to feed from the CFS; the default is the spool.
   ```
   shop watch start box.gcode --plate frosted --vents closed
   ```
4. **Watch.** Run it again after each frame until it says `DONE`:
   ```
   shop watch next [--plate frosted --vents closed [--cfs]]
   ```
   | It prints | Exit | Means |
   |---|---|---|
   | `watch CHECKPOINT layer 10 of 529: ~/.local/state/print-watch/box/layer-0010.jpg` | 0 | look at the frame, then run it again |
   | `watch RECOVER 1/2: key22 before layer 1; restarting Klipper and the job` | — | a known fault before layer 1; it carries on by itself |
   | `watch FAULT at layer 212: key836; …` | 1 | your call: the printer is left as it is |
   | `watch DONE: job complete at layer 529` | 3 | finished |

   Without `--plate` and `--vents`, a fault before layer 1 is reported, not restarted.
   Frames come after layers 2, 10, 50, then every 100. A part taller than
   60 mm slows linearly to 70% speed at its top (`M220`); `--no-taper` turns
   that off, `--taper-from` and `--taper-to` move it. The taper only runs while
   `next` is running. Nothing here ever cancels a print.

An agent can run the same steps: the `print-watch` skill
(`.claude/skills/print-watch/SKILL.md`) is the agent's version of this section.

## On the printer's own console

Macros from [`k2-plus-mods`](projects/k2-plus-mods/), typed in the web console
or sent over Moonraker:

| Macro | Does |
|---|---|
| `HEAT_HOLD BED=90 CHAMBER=50` | hold bed and chamber (120 min timer); a morning preheat |
| `HEAT_HOLD_OFF` | end the hold |
| `BED_VIEW` | bring the bed up to the camera (never closer than 10 mm) |

When Klipper is stuck (shutdown, a job stuck "printing" at layer 0):
`ssh root@192.168.0.190 /etc/init.d/klipper restart`, wait a minute, then
`shop printer` to check it stayed ready.
