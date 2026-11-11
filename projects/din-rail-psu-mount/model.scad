// DIN-rail (TS35, 35 x 7.5 mm) mount for an 80 x 110 mm enclosed AC-DC supply.
// A flat base plate screws to the PSU's two diagonal holes. Four separate clips
// press into rectangular windows in the plate: two fixed hooks (-Y) and two
// flexure latches (+Y). The rail runs along X, the 80 mm axis: the 110 mm side stands up and down.
// Print the base with the PSU face down (z=0); clips print upright as shown.

/* [Show] */
part = "print";      // [print:All parts laid out for printing, assembled:Assembled, base:Base plate only, fixed:Fixed clip only, latch:Latch clip only]

/* [Plate] */
plate_l = 80;        // X, along the rail
plate_w = 110;       // Y, across the rail (the vertical, long side)
plate_t = 4;
corner_r = 3;

/* [PSU mounting holes] (caliper ~, diagonal pair) */
hole_dx = 47;        // centre to centre along X (the 80 mm side)
hole_dy = 75;        // centre to centre along Y (the 110 mm side)
hole_d = 2.8;        // M2.5 clearance. The PSU holes take 2.5 mm, 3.3 mm at the very most
cbore_d = 5.2;       // screw-head pocket on the rail side
cbore_depth = 2;

/* [Rail] */
rail_w = 35;         // flange tip to flange tip
flange_t = 1.0;      // rail sheet thickness
clr = 0.4;           // lip-to-flange clearance in z
side_clr = 0.5;      // hook wall to flange edge

/* [Hooks] */
wall_t = 2;          // hook wall / latch beam thickness
lip_len = 2.5;       // lip engagement over the flange
lip_t = 2.2;         // lip thickness at the wall
tip_t = 0.8;         // lip thickness at the tip (ramp)
slot_in = 2.5;       // gap inside the beam (pry-release)
slot_out = 2.5;      // gap outside the beam (flex room)
beam_len = 22;
hook_len = 10;       // X length of the latch hook on the beam
fixed_len = 18;      // X length of each fixed hook

/* [Press fit] */
press = 0.1;         // clip block oversize per side against its window

/* [Hidden] */
$fn = 48;
r = rail_w / 2;                    // 17.5, flange edge from centreline
wall_in = r + side_clr;            // 18
lip_tip = wall_in - lip_len;       // 16.5
z0 = plate_t + flange_t + clr;     // underside of the lips

// Clip blocks: footprints that the plate windows copy. Local origin = block corner.
fix_x = 24;  fix_y = wall_t + 4;        // fixed clip block
lat_gap = 2; lat_anchor = 4;
lat_x = lat_gap + beam_len + lat_anchor; // latch clip block, X
lat_y = slot_in + wall_t + slot_out + 4; // latch clip block, Y
// Absolute positions of the window corners (+X side; the -X side mirrors).
fix_x0 = 2;
fix_y0 = wall_in - 1.5;                  // fixed window starts here (on the -Y side, mirrored)
lat_x0 = 2;
lat_y0 = wall_in - slot_in - 2;

// Hook cross-section (u = outward from rail centreline, v = z).
module hook_profile() {
    polygon([
        [wall_in, plate_t - 0.5], [wall_in + wall_t, plate_t - 0.5],
        [wall_in + wall_t, z0 + lip_t], [wall_in, z0 + lip_t],
        [lip_tip, z0 + tip_t], [lip_tip, z0], [wall_in, z0]
    ]);
}
module hook_x(x0, x1) {   // +Y side, extruded x0..x1
    translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(x1 - x0) hook_profile();
}

// ---- clips, each in its own local frame: block corner at the origin ----------
// Fixed clip: block + hook wall with lip. Local Y runs outward from y = fix_y0.
module fixed_clip() {
    translate([-press, -press, 0]) cube([fix_x + 2*press, fix_y + 2*press, plate_t]);
    translate([2, -fix_y0, 0]) hook_x(0, fixed_len);
}
// Latch clip: block with a U slot freeing a beam; hook on the beam's free end.
module latch_clip() {
    ay = slot_in + 2;               // beam inner face, local Y (= wall_in - lat_y0)
    difference() {
        translate([-press, -press, 0]) cube([lat_x + 2*press, lat_y + 2*press, plate_t]);
        // U slot: free end gap + inside + outside, stopping at the anchor
        difference() {
            translate([-1, 2, -1]) cube([lat_gap + 1 + beam_len, slot_in + wall_t + slot_out, plate_t + 2]);
            translate([lat_gap, ay, -2]) cube([beam_len + 1, wall_t, plate_t + 4]);
        }
    }
    translate([lat_gap, -lat_y0, 0]) hook_x(0, hook_len);
}

// ---- base plate ---------------------------------------------------------------
module window(w, d) { translate([0, 0, -1]) cube([w, d, plate_t + 2]); }

module base() {
    difference() {
        linear_extrude(plate_t)
            offset(r = corner_r) square([plate_l - 2*corner_r, plate_w - 2*corner_r], center = true);
        for (p = [[-1, -1], [1, 1]]) translate([p[0]*hole_dx/2, p[1]*hole_dy/2, 0]) {
            translate([0, 0, -1]) cylinder(d = hole_d, h = plate_t + 2);
            translate([0, 0, plate_t - cbore_depth]) cylinder(d = cbore_d, h = cbore_depth + 1);
        }
        for (sx = [-1, 1]) {
            // fixed windows, -Y side
            scale([sx, -1, 1]) translate([fix_x0, fix_y0, 0]) window(fix_x, fix_y);
            // latch windows, +Y side
            scale([sx, 1, 1]) translate([lat_x0, lat_y0, 0]) window(lat_x, lat_y);
        }
    }
}

// ---- placement ----------------------------------------------------------------
module placed_fixed(sx)  { scale([sx, -1, 1]) translate([fix_x0, fix_y0, 0]) fixed_clip(); }
module placed_latch(sx)  { scale([sx, 1, 1])  translate([lat_x0, lat_y0, 0]) latch_clip(); }

module assembled() {
    base();
    for (sx = [-1, 1]) { placed_fixed(sx); placed_latch(sx); }
}

module print_layout() {
    base();
    // clips beside the plate, upright (same orientation as installed)
    for (i = [0, 1]) {
        translate([-58 + i*32, plate_w/2 + 8, 0]) fixed_clip();
        translate([6 + i*34, plate_w/2 + 8, 0]) latch_clip();
    }
}

if (part == "base") base();
else if (part == "fixed") fixed_clip();
else if (part == "latch") latch_clip();
else if (part == "assembled") assembled();
else print_layout();
