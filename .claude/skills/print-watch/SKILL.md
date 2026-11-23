---
name: print-watch
description: Heat-soak, start and watch a K2 Plus print with the `shop watch` commands, sending the user each checkpoint frame. Use on "watch this print", "soak and start <file>", "start the ASA job", or any high-temperature (ASA, ABS) job. Not for slicing or modelling.
---

# Print watch

The steps and their output are in the repo's `RUNBOOK.md`, "Print a
high-temperature job"; why each check exists is in
`projects/k2-plus-mods/printer-notes.md`. This file is only what an agent
may and may not do on its own.

## Ask the user first

Plate (`frosted`, `smooth`, `pattern`, `epoxy`), rear vents (`closed`,
`open`) and feed (spool, or `--cfs`), unless the user's message says. These
are read off the printer, not guessed; one question, all three.

## Yours to do

1. `shop watch preflight <file> --plate … --vents … --fix`. A FAIL with no fix
   goes to the user with its line.
2. `shop watch soak <file> --plate …` for ASA or ABS, in the background. It may
   run unattended: one `HEAT_HOLD`, bed at most 100, chamber at most 50, ended
   by the macro's own timer. Never extend it or send a second one, and never
   pass `--over-rating` without the user's word.
3. `shop watch start <file> --plate … --vents …` once the soak passes.
4. `shop watch next <file> --plate … --vents …`, in the background. On each
   `CHECKPOINT`, look at the frame and send it to the user with one line on
   what it shows (brim down or lifting, part on the bed or moved). Then run
   `next` again. `DONE` ends the watch.

## Never yours

- **Cancel a print.** Only on the user's word, however bad the frame looks.
  Send the frame and say what you see.
- **Restart mid-print.** `next` restarts Klipper and the job itself, only before
  layer 1 and only on `key22`, `key798`, `key559` or `key852`, at most twice.
  Any `FAULT` line goes to the user verbatim; touch nothing.
- **Heat the bed past the plate's rating**, or the chamber past 50.
- **Jog Z by hand.** A jog drove the bed into the nozzle on 2026-11-22; use
  `BED_VIEW` to see the bed.
