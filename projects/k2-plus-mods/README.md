# K2 Plus mods

Rollout plan for firmware and macro mods on the Creality K2 Plus (firmware 1.1.7.0).
Already done: root over SSH with key login (`ssh root@192.168.0.190`), fork of
[Rcpilot33/k2-improvements](https://github.com/Rcpilot33/k2-improvements) cloned to
`~/k2-improvements` with `upstream` pointing at Rcpilot33.

Every step: snapshot first, show the diff with a plain-English line per change,
apply on the user's yes, check, record the result here.

## Steps

| # | Step | Check it worked | Undo | Door |
|---|---|---|---|---|
| 0 | Wait for the print to finish | `shop printer` shows idle | — | — |
| 1 | Snapshot `/mnt/UDISK/printer_data/config` to `~/k2-backups/<date>.tar.gz` on the Mac | tarball lists `printer.cfg` | — | — |
| 2 | Lock down access: user changes the root password (`passwd` on the printer); decide on adbd (port 5037) | password login refused with the old default; `nc -z 192.168.0.190 5037` | `passwd` again; re-enable adbd | two-way |
| 3 | Own START_PRINT for ASA/ABS: OrcaSlicer passes material and chamber target, printer heat-soaks the chamber before printing | dry start with ASA profile waits for chamber target, then prints | restore `gcode_macro` files from step 1 tarball, `FIRMWARE_RESTART` | two-way |
| 4 | KAMP: adaptive mesh and purge where the part sits | mesh covers only the part area in Fluidd | restore from snapshot | two-way |
| 5 | Pressure advance and input shaper per material, fills the calibration table in `AGENTS.md` | values written to the table with source | — (measure only) | two-way |
| 6 | Moonraker into Home Assistant | printer entities show in HA | remove the integration | two-way |
| 7 | Full Rcpilot33 install, then the Cartographer probe | — | factory reset | **one-way: needs a factory reset, 1.1.7.0 untested upstream. Stop and confer.** |

## Step 3 settings (proposed, unmeasured)

| Material | Chamber target | Soak cap | Source |
|---|---|---|---|
| ASA | 55 °C | 15 min | guess |
| ABS | 55 °C | 15 min | guess |
| PETG, PLA | no soak | — | stock behaviour |

Reference only: `macros/start_print` in Rcpilot33/k2-improvements. No full install before step 7.

## Log

- 2026-11-12: plan written; step 0 pending.
- 2026-11-12 18:55: step 0 done (printer idle). Step 1 blocked: key login refused, `ssh-copy-id` unfinished.
