# K2 Plus mods

Rollout plan for firmware and macro mods on the Creality K2 Plus (firmware 1.1.7.0).
Already done: root over SSH with key login (`ssh root@192.168.0.190`), fork of
[Rcpilot33/k2-improvements](https://github.com/Rcpilot33/k2-improvements) cloned to
`~/k2-improvements` with `upstream` pointing at Rcpilot33.

Every step: snapshot first, show the diff with a plain-English line per change,
apply on the user's yes, check, record the result here.

Machine facts (fan map, tach channels, addresses): [printer-notes.md](printer-notes.md).

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
- 2026-11-12 18:58: step 1 done over Moonraker's file API, no SSH: `~/k2-backups/2026-11-12-1858-config.tar.gz`, 12 files.
- 2026-11-12 19:05: key login works. SSH snapshot `~/k2-backups/2026-11-12-1905-ssh-printer_data.tar.gz` (config, database, /etc/dropbear, /etc/config).
- 2026-11-12 19:06: step 2 found password SSH on for root, adbd listening on 0.0.0.0:5037.
- 2026-11-12 19:10: printer accepts 2 keys (this Mac, WSL box), not all machines; password SSH stays on until it does.
- 2026-11-12 19:35: step 3 applied (`chamber_soak.cfg`, include in printer.cfg, 2 calls in START_PRINT); Klipper ready; PLA no-op ok.
- 2026-11-12 19:56: ASA test stopped (e-stop, restart) for a PETG print. In 24 min the bed went 63→~89 °C at full power and never reached 100; chamber heater target 55, power 0%. Cause unknown: firmware gating or a heater fault. Test the chamber heater alone next.
- 2026-11-14 23:00: heaters tested one at a time, room ~15 °C, 100% power throughout (`out/2026-11-14-heater-alone.csv`). Chamber heater alone, target 55: 15.2→31.0 °C in 20 min, ~0.6 °C/min at the end. Bed alone, target 100: 17→88.8 °C in 30 min, ~1.2 °C/min at the end; extrapolated plateau near 109 °C (guess). With the bed at 88 °C and the chamber heater off, the chamber fell 35→29 °C. Both heaters draw power when alone; the 12 Nov 0% was with the bed also at full power. Door and lid closed (user, after the run); rear vents and the external fume fan unknown. Workshop unheated. Klipper logs on the printer (25 Sep, 10–14 Nov) show no heater fault; only 3 shutdowns, 12 Nov e-stop likely. Soak at 55 °C / 15 min is unreachable as set.
- 2026-11-15 12:13: rerun with both rear vents closed (user), door and lid assumed closed, room ~16 °C (`out/2026-11-15-vents-closed.csv`, graph `out/2026-11-15-vents-closed.png`, script `plot_heat.py`). Chamber heater alone, 20 min: 16.1→31.4 °C (14 Nov: 15.2→31.0). Bed alone, 30 min: 18.1→91.7 °C (14 Nov: 17→88.8). Closing the vents is worth ~3 °C on the bed at 30 min and almost nothing on the chamber. ABS (bed 100 + chamber 55 together, bed starting at 92 °C): both targets reached and held in 35 min. The chamber heater stayed at 0% for the first 8 min until bed power fell below ~97%, which explains the 12 Nov 0%. Then chamber 30→55 °C in 27 min, with the rear exhaust fan at 100% from 35 °C up. Cool-down with heaters off, 45 min: bed 100→42 °C, chamber 55→30 °C. Time to ABS temps from a cold printer: not measured (guess ~65 min: 30 min bed, then 35).
- 2026-11-12 19:35: camera not readable by the agent: no snapshot URL, Fluidd camera tile black.
