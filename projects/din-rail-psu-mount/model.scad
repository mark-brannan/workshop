// DIN-rail (TS35, 35 x 7.5 mm) mount for an 80 x 110 mm enclosed AC-DC supply.
// Plate bolts to the PSU's two diagonal base holes; the rail side carries two
// fixed hooks (-Y) and two flexure latches (+Y). Print with the PSU face down
// (z=0), no supports. The rail runs along X (the 110 mm axis).

/* [Plate] */
plate_l = 110;       // X
plate_w = 80;        // Y
plate_t = 4;
corner_r = 3;

/* [PSU mounting holes] (caliper ~, diagonal pair) */
hole_dx = 75;        // centre to centre along X
hole_dy = 47;        // centre to centre along Y
hole_d = 4.5;        // clearance for M4: a guess until the thread is known

/* [Rail] */
rail_w = 35;         // flange tip to flange tip
flange_t = 1.0;      // rail sheet thickness
clr = 0.4;           // lip-to-flange clearance in z, FIT NUMBER UNMEASURED
side_clr = 0.5;      // hook wall to flange edge

/* [Hooks] */
wall_t = 2;          // hook wall / latch beam thickness
lip_len = 2.5;       // lip engagement over the flange (flange tip at 17.5, crown wall at 13.5)
lip_t = 2.2;         // lip thickness at the wall
tip_t = 0.8;         // lip thickness at the tip (ramp)
slot_in = 2.5;       // gap inside the beam (pry-release)
slot_out = 2.5;      // gap outside the beam (flex room)
beam_len = 22;
hook_len = 10;       // X length of the latch hook on the beam
fixed_len = 18;      // X length of each fixed hook
clip_x0 = 2;         // inner end of beams / hooks, from X = 0

/* [Hidden] */
$fn = 48;
r = rail_w / 2;                    // 17.5, flange edge from centreline
wall_in = r + side_clr;            // 18
lip_tip = wall_in - lip_len;       // 16.5

// Hook cross-section in (outward distance from rail centreline, z).
module hook_profile() {
    z0 = plate_t + flange_t + clr;
    polygon([
        [wall_in, plate_t - 0.5], [wall_in + wall_t, plate_t - 0.5],
        [wall_in + wall_t, z0 + lip_t], [wall_in, z0 + lip_t],
        [lip_tip, z0 + tip_t], [lip_tip, z0], [wall_in, z0]
    ]);
}

// Extrude the profile along X from x0 to x1, outward toward side s (+1 = +Y).
module hook(x0, x1, s) {
    translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(x1 - x0)
        scale([s, 1]) hook_profile();
}

module plate_body() {
    linear_extrude(plate_t) difference() {
        offset(r = corner_r) square([plate_l - 2 * corner_r, plate_w - 2 * corner_r], center = true);
        for (p = [[-1, -1], [1, 1]]) translate([p[0] * hole_dx / 2, p[1] * hole_dy / 2]) circle(d = hole_d);
        for (sx = [0, 1]) mirror([sx, 0]) beam_slot();
    }
}

// U-shaped slot freeing one latch beam (+X form; mirrored for the other).
// The beam runs from its free end at X = clip_x0 out to the anchor at
// X = clip_x0 + beam_len, where the slot stops and the plate resumes.
module beam_slot() {
    x0 = clip_x0 - 2;                          // gap past the free end
    x1 = clip_x0 + beam_len;                   // anchor
    y0 = wall_in - slot_in;                    // inside edge
    y1 = wall_in + wall_t + slot_out;          // outside edge
    difference() {
        translate([x0, y0]) square([x1 - x0, y1 - y0]);
        translate([clip_x0, wall_in]) square([beam_len + 1, wall_t]);
    }
}

module mount() {
    plate_body();
    // fixed hooks, -Y
    for (sx = [-1, 1]) hook(sx > 0 ? clip_x0 + 2 : -(clip_x0 + 2 + fixed_len), sx > 0 ? clip_x0 + 2 + fixed_len : -(clip_x0 + 2), -1);
    // latch hooks, +Y, on the free end of each beam
    for (sx = [-1, 1]) hook(sx > 0 ? clip_x0 : -(clip_x0 + hook_len), sx > 0 ? clip_x0 + hook_len : -clip_x0, 1);
}

mount();
