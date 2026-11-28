---
name: print-watch
description: Start and watch a K2 Plus print, any material, with the agent driving and the `shop watch` commands as its parts. Preflight, soak when needed, start, then watch frame by frame and send the user each checkpoint. Use on "print this", "start <file>", "watch this print", "soak and start <file>", or when a `shop watch` command has failed. Not for slicing or modelling.
---

# Print watch

You drive; `shop watch` is a box of parts. Each subcommand does one job
and returns, and you read what it printed before picking the next. Don't
hand the whole job to `shop watch run` / `shop watch <file>`: that loop
hides a failure behind one line and gets a frame judged by a model of its
own, when you can look at the frame yourself.

Steps and output: `RUNBOOK.md`, "Print a high-temperature job". Why each
check exists: `projects/k2-plus-mods/printer-notes.md`.

## The parts

| Part | Does | Returns |
|---|---|---|
| `shop watch preflight <file> [--plate … --vents …] [--fix]` | Checks the job against the printer. `--fix` sends the fixes and strips tool changes from a spool job, on the printer over SSH | `ok`/`FAIL` lines, then PASS or FAIL |
| `shop watch soak <file> --plate …` | One `HEAT_HOLD` for ASA/ABS; ends by the macro's own timer | PASS, or FAIL with the reason |
| `shop watch start <file> [--plate … --vents …]` | preflight `--fix`, CFS switch, start, confirms it is printing | `start … printing` or FAIL |
| `shop watch next` | Blocks until the next checkpoint layer, then grabs the frame | `CHECKPOINT` + frame path, `DONE`, or `FAULT` |
| `shop watch frame <layer> <out.jpg>` | One camera frame now | the file |
| `shop watch upload <file.gcode>` | Upload from this box, tool changes stripped unless `--cfs` | bytes sent |

`<file>` may be the 3MF name; it resolves to the newest matching gcode on
the printer, and says which.

## The loop

1. **Ask once, all three, unless the message says:** plate (`frosted`,
   `smooth`, `pattern`, `epoxy`), rear vents (`closed`, `open`), feed (spool,
   or `--cfs`). A PETG job on the pattern plate with vents open and the spool is
   the default and needs no question.
2. `preflight … --fix`. A FAIL with no fix goes to the user with its line. A `STALE GCODE` warning goes to the user with its line before `start`: the file on the printer was sliced before the model last changed shape.
3. ASA or ABS: `soak` in the background; on PASS, go on.
4. `start`.
5. `next` in the background. On `CHECKPOINT`, Read the frame, send it with one
   line on what it shows (brim down or lifting, part on the bed or moved,
   spaghetti). Run `next` again. `DONE` ends it.

## When a part fails

Its message is a lead, not a verdict. Look at the printer yourself before
you tell the user anything, in one call:

```bash
curl -s -m 5 -o /dev/null -w '%{http_code} %{time_total}s\n' http://192.168.0.190:4408/printer/info
```

- Answers fast: the printer is up. A timeout or 504 was the web front end
  choking, often seconds after an upload. Wait 10 s and rerun the same part;
  each part is safe to rerun.
- No answer: then say it is off the network.
- A part that fails the same way twice is a bug in the part: fix it in
  `src/shop/printwatch.py` with a test, push, then go on with the print.

## Never yours

- **Cancel a print.** Only on the user's word, however bad the frame looks.
  Send the frame and say what you see.
- **Restart mid-print.** `next` restarts Klipper and the job itself, only before
  layer 1 and only on `key22`, `key798`, `key559` or `key852`, at most twice.
  Any `FAULT` line goes to the user verbatim; touch nothing.
- **Heat the bed past the plate's rating**, or the chamber past 50. Never
  extend a soak, send a second `HEAT_HOLD`, or pass `--over-rating` without
  the user's word.
- **Jog Z by hand.** A jog drove the bed into the nozzle on 2026-11-22; use
  `BED_VIEW` to see the bed.
