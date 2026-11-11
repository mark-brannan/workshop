# K2 Plus chute cover to segmented-chute ball

Purpose: carry the K2 Plus exhaust chute (`ref/chute-cover.3mf`, the owner's file, unchanged)
straight down into the ball of the segmented "poop chute" (`catcherforRing.3mf`), so the
owner's printed segments attach below it. No bend is added; the jog you see is in the cover.

```
 ear + screw holes ->  ==|  |     screws go in horizontally (along Y), unchanged
                         |  |     cover, jog included, unchanged (125 mm)
                         |  |
 cone_h 11              |  |     inside the cover's last run: U closed, bore funnels square to round
 flare_h 2               /  \     outer square to round in 2 mm
 ball_h  30             (    )    ball: widest 59.8 mm, only below the square
                         \__/     rim on the bed
```

## Files (out/)

`printer-chute-transition_scad.3mf` / `.stl`: one part, 157 mm tall, in print orientation
(printed upside down: the 45 x 11 mm ear face on the bed, ball rim on top, no supports; `ear_down = false` gives the ear-up version, 14 mm flare needed). `.png` / `_views.png`: renders.
The cover is embedded in `model.scad` as `cover_mesh()` (1212 vertices, 2428 triangles);
`ref/` keeps the owner's 3MF and an STL of it.

## Measured, and from what

| Value | mm | Source |
|---|---|---|
| Cover open-end section | 48.48 x 48, walls 1.86, 4 mm chamfers on the top corners | `chute-cover.3mf` vertices |
| Cover length | 125 (ear at +74, open end at -50.6 in its own frame) | same |
| Ball outer profile | rim 27.8, widest 29.92 at 10.8, waist 25.53 at 30 (radii) | `catcherforRing.3mf` vertices |

## Chosen, not measured

| Value | Now | Why |
|---|---|---|
| Ball centre | on the cover's section centre | chosen |
| Ball wall | 1.86 inward from the measured outer surface | the original shell is ~1.0; matched to the cover for strength. Outer shape, which mates with the next segment, is the original |
| `tube_h` | 0 | no extra square run: the flare starts at the cover's open end (raise it to add one) |
| `flare_h` | 2 | outer step to the neck; upside down the corners lean inward, no overhang |
| `cone_h` | 11 | inner funnel inside the cover's last run, ceiling lean ~41 deg; a brim is advisable for the 45 x 11 mm footprint |
| `bore_r` | 22 | round bore, inside the cover's 44.8 x 46.1 passage |
| Ball cut | at the waist, z=30 | below the cone of the original segment, which is not included |

Checks: `uv run pytest -q projects/printer-chute-transition`. Cover unchanged (same wall crossings
along six vertical rays, same top), watertight, bore open from top to rim. Nothing wider than the
square sits at or above the cover's open end (z=32, installed frame); the ball overhangs only below.
Nothing here is calibrated for fit.

## The clean prompt (use this to start over)

> Build a printable part: extend `chute-cover.3mf` straight down into the ball of
> `catcherforRing.3mf`. No bend, no L shape. Files: `C:\Users\Solace\Downloads\chute-cover.3mf`
> and `C:\Users\Solace\Downloads\catcherforRing.3mf`.
>
> **Orientation (the part hangs on the printer):** the ear with the two screw holes is at the
> top and the screws go in horizontally, into the printer's rear enclosure. The U profile runs
> straight down from the ear. The 3MF's own Z axis is not "up"; along the chute, ear to open
> end, is vertical. The ball is the last thing at the bottom.
>
> 1. Keep `chute-cover.3mf` exactly as is, ear end and screw holes included. Do not change its jog.
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
