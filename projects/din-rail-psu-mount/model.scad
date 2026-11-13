// DIN-rail (TS35) mount for an 80 x 110 mm enclosed AC-DC supply, one piece, low profile.
// A 2.5 mm lightened frame, the PSU's own footprint, screws (M3) to its two diagonal holes.
// Two DIN clips are part of the frame: Maxstupo's "DIN Rail Clip (Heat Insert Version)", Printables
// model 420009 (CC BY 4.0), imported from ref_din_clip_heat_insert.stl. Its two heat-insert screw holes
// are filled, since the clip is no longer a separate part. A fixed hook on one side and a spring latch on
// the other hold the rail flange 4.1 mm off the PSU face. The rail runs along X, the 80 mm axis; the
// 110 mm side stands up and down.
// Print with the PSU face down (z = 0).

/* [Plate] */
plate_l = 80;        // X, along the rail: the PSU's footprint, no overhang
plate_w = 110;       // Y, across the rail (the vertical, long side)
plate_t = 2.5;       // the frame
corner_r = 3;
rim_w = 6;           // perimeter band of the lightened frame
boss_d = 11;         // solid round around each screw hole

/* [PSU mounting holes] (caliper ~, diagonal pair) */
hole_dx = 47;        // centre to centre along X (the 80 mm side)
hole_dy = 75;        // centre to centre along Y (the 110 mm side)
hole_d = 3.5;        // M3, easy slip fit; the head bears on the rail side

/* [Clips] */
clip_x = 25;         // clip centre distance from the plate centre, along the rail
clip_len = 18;       // each clip's length along the rail: the model's own 18 mm
strip_pad = 3;       // solid frame band beyond each clip's length, each side

/* [Hidden] */
$fn = 48;
// The clip in its own frame: x across the rail (0..60), y along it (-9..9), z up from the PSU face (0..7.5).
// The rail centre line is x = 27.05 (hook lips at 9.8 and 44.3); the flange seat is z = 4.1.
rail_cx = 27.05;
strip_w = clip_len + 2*strip_pad;
holes = [[-hole_dx/2, -hole_dy/2], [hole_dx/2, hole_dy/2]];

// The two heat-insert holes, filled: the one at x = 5 runs through the fixed hook (7.5), the one at
// x = 56 through the shelf (4.6).
module clip() {
    translate([0, 0, 0.01]) rotate([0, 0, 90]) translate([-rail_cx, 0, 0]) union() {  // 0.01 into the frame, not coplanar
        import("ref_din_clip_heat_insert.stl");
        translate([5, 0, 0]) cylinder(d = 4.3, h = 7.5);
        translate([56, 0, 0]) cylinder(d = 4.3, h = 4.6);
    }
}

module outline() offset(r = corner_r) square([plate_l - 2*corner_r, plate_w - 2*corner_r], center = true);

// Perimeter rim, a solid band under each clip out to the side rim, a boss round each screw hole; the rest is open.
module frame2d() intersection() { outline(); union() {
    difference() { outline(); offset(delta = -rim_w) outline(); }
    for (sx = [-1, 1]) translate([sx*clip_x - strip_w/2, -plate_w/2]) square([strip_w, plate_w]);
    for (h = holes) translate(h) circle(d = boss_d);
} }

module base() {
    difference() {
        linear_extrude(plate_t) frame2d();
        for (h = holes) translate([h[0], h[1], -1]) cylinder(d = hole_d, h = plate_t + 2);
    }
}

module mount() {
    base();
    for (sx = [-1, 1]) translate([sx*clip_x, 0, 0]) clip();
}

mount();
