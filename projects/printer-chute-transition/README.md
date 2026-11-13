# K2 Plus chute cover to segmented-chute ball

Purpose: carry the K2 Plus exhaust chute (`ref/chute-cover.3mf`, the owner's file) straight down
into the ball of the segmented "poop chute" (`ref/catcherforRing.3mf`), so the owner's printed
segments attach below it. No bend is added; the jog you see is in the cover.

Two prints that plug together. The one-piece version (157 mm tall, 4 hours) failed an hour in.

```
 ear + screw holes ->  ==|  |      COVER: the owner's file, 12 mm trimmed off its open end
                         |  |
                         |  |
 spigot_h 15            ||  ||     spigot: goes up inside the cover's U; its 4th wall closes the open side
 lip_h 4               [||  ||]    lip: outside, three sides; the cover's cut end drops into the slot between
 flare_h 14              /  \      ADAPTER: square to round
 ball_h 30              (    )     ball: 0.8 mm wall, original outer profile
                         \__/      rim on the bed
```

`out/joint-section.png` is the joint in section, drawn from the built meshes.

## Files (out/)

| File | What | Print |
|---|---|---|
| `printer-chute-transition_adapter.3mf` / `.stl` | ball, flare, spigot, lip; 59 mm tall | as installed, ball rim on the bed, no supports. The rim is a 0.5 mm ring: use a brim (Orca's "inner brim only" keeps it off the mating edge) |
| `printer-chute-transition_cover.3mf` / `.stl` | the owner's cover, 112.65 mm long | lying as the owner's file lies, ear plate and U edges on the bed; orient as you printed the original |
| `printer-chute-transition_scad.*` | both, mated, as installed (156.65 mm) | not a print: the picture |

## The joint

The cover's cut end drops 4 mm into a slot and its walls slide 15 mm down the outside of the spigot.
Six crush ribs on the spigot (two per mating face) stand 0.15 mm past the gap; they push the U's legs
out against the lip, which stops them springing, so the slot at a rib is 0.05 mm narrower than the wall.
The lip stands 1.3 mm proud of the square on three sides for 4 mm; there is none at the printer's panel.

Fastening is open: the first print is to see the fit. PETG is the usual material and takes glue poorly;
heat (a soldering-iron tack through the lip) is the other candidate.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Cover open-end section | 48.48 x 48, walls 1.86, 4 mm chamfers on the top corners | `chute-cover.3mf` vertices |
| Cover length | 125 (ear at +74, open end at -50.6 in its own frame) | same |
| Ball outer profile | rim 27.8, widest 29.92 at 10.8, waist 25.53 at 30 (radii) | `catcherforRing.3mf` vertices |
| Ball wall | 0.77 to 0.83 | `catcherforRing.3mf`, sliced at six heights |

## Chosen, not measured

| Value | Now | Why |
|---|---|---|
| Ball centre | on the cover's section centre | chosen |
| `ball_wall` | 0.8 | the original segment's; the one-piece part had 1.86 |
| `trim`, `flare_h` | 12, 2 + trim = 14 | the cover's open end is cut back 12 mm so the installed height stays 156.65 mm; the flare's corners lean out at most 34 deg from vertical |
| `spigot_h`, `spigot_wall` | 15, 1.2 | engagement inside the cover |
| `spigot_clear`, `lip_clear` | 0.25, 0.1 | guesses: the fit table is uncalibrated |
| `rib_crush` | 0.15 | guess; raise for a tighter pinch |
| `lip_h`, `lip_wall` | 4, 1.2 | "a few mm" of outer sleeve |
| `rim_chamfer` | 0.3 | first-layer squish cannot flare the rim's mating edge; leaves 0.5 mm of the 0.8 wall on the bed |
| Ball cut | at the waist, z=30 | below the cone of the original segment, which is not included |

The flare thickens from 0.8 mm at the ball to 4.6 mm under the slot's floor (lip + cover wall + spigot).

Checks: `uv run pytest -q projects/printer-chute-transition`. Both parts watertight; cover identical to
the owner's above the cut; ball wall and outer profile; bore open; no overhang flatter than 45 deg on the
adapter; slot widths with and without a rib; lip on three sides only; spigot 0.25 mm clear of the cover
over its whole height. Nothing here is calibrated for fit.

## The clean prompt (use this to start over)

This describes the one-piece part that the two prints replaced.

> Build a printable part: extend `chute-cover.3mf` straight down into the ball of
> `catcherforRing.3mf`. No bend, no L shape. Files: `C:\Users\Solace\Downloads\chute-cover.3mf`
> and `C:\Users\Solace\Downloads\catcherforRing.3mf`.
>
> **Orientation (the part hangs on the printer):** the ear with the two screw holes is at the
> top and the screws go in horizontally, into the printer's rear enclosure. The U profile runs
> straight down from the ear. The 3MF's own Z axis is not "up"; along the chute, ear to open
> end, is vertical. The ball is the last thing at the bottom.
>
> 1. Keep `chute-cover.3mf` as is, ear end and screw holes included (its open end may be trimmed to lengthen the transition without making the part longer). Do not change its jog.
> 2. Add no extra square length: at the cover's open end, close the open side and flare
>    immediately into the ball of `catcherforRing.3mf`, on the same vertical axis. If needed you may also close
>    (enclose) an additional length of the original U's open side. Keep the whole part as short
>    as printing allows.
> 3. The ball (and the flare) may be wider than the square in any direction, but only below the
>    end of the square section.
> 4. Print stacked in the installed orientation, ball rim on the bed, no supports; or at 45 degrees
>    with breakaway fins built in. Say which you chose.
> 5. Ignore printer and material tolerances. Aim for easy to print and structurally sound.
> 6. Before the full model, show one profile view (side, vertical, ear up) and the numbers you read
>    from both files. Ask me anything unclear before building.
