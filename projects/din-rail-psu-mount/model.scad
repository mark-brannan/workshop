// DIN-rail (TS35) mount for an 58 x 85 mm enclosed AC-DC supply, one piece, low profile.
// A 2.5 mm lightened frame, the PSU's own footprint, screws (M3) to its two diagonal holes.
// Two DIN clips are part of the frame: Maxstupo's "DIN Rail Clip (Heat Insert Version)", Printables
// model 420009 (CC BY 4.0), imported from ref_din_clip_heat_insert.stl. Its two heat-insert screw holes
// are filled, since the clip is no longer a separate part. A fixed hook on one side and a spring latch on
// the other hold the rail flange 4.1 mm off the PSU face. The rail runs along X, the 58 mm axis; the
// 85 mm side stands up and down. The plate runs 15 mm past the PSU's lower end, with chamfered zip-tie
// slot pairs there for strain relief (the tie loops under the plate, where no PSU sits).
// Print with the lip down (z = 0): the PSU sits in the pocket the lip makes, 8 mm deep, on the plate underside.

/* [Plate] */
plate_l = 58;        // X, along the rail: the PSU's footprint (box, caliper), no overhang
plate_w = 85;        // Y, across the rail (the vertical, long side): the PSU's footprint
ext = 15;            // the plate continues this far past the PSU's lower end (-Y), for the zip ties
plate_t = 2.5;       // the frame
corner_r = 3;
rim_w = 6;           // perimeter band of the lightened frame
boss_d = 10;         // solid round around each screw hole

/* [Lip] the PSU sits in a pocket, the lip stands on the PSU side of the plate */
lip_h = 8;           // lip height above the PSU-side face of the plate
lip_t = 2;           // lip wall thickness, outside the PSU's own footprint

/* [PSU mounting features] (caliper ~; x right, y toward the back, centred on the footprint, left = left in normal view) */
hole_d = 3.5;        // M3, easy slip fit; the head bears on the rail side
slot_w = 3.4;        // the PSU's U slot and pill width (~)
holes = [[-24.2, -37.7], [-24.2, 30.8]];   // blind holes in the PSU underside, 68.5 apart
uslot_x = -23.5;     // U slot open to the back edge, inner tip 5.5 mm from it
uslot_depth = 5.5;
pill = [23.5, -37.5];  // closed pill, 5.5 long tip to tip, long axis along Y (guess)
pill_len = 5.5;

/* [Zip-tie strain relief: slot pairs in the extension, the tie loops under the plate] */
tie_w = 5.5;         // slot length across the tie: takes ties up to 5 mm wide (standard), small ones too
tie_t = 2.2;         // slot width
tie_gap = 5;         // slot centre to slot centre, along Y
tie_c = 1.2;         // underside chamfer on each slot's outer edge, where the tie turns under
tie_xs = [-18, 0, 18];  // pair positions along X

/* [Clips] */
clip_x = 13.5;         // clip centre distance from the plate centre, along the rail
clip_len = 18;       // each clip's length along the rail: the model's own 18 mm
strip_pad = 2;       // solid frame band beyond each clip's length, each side

/* [Hidden] */
$fn = 48;
// The clip in its own frame: x across the rail (0..60), y along it (-9..9), z up from the PSU face (0..7.5).
// The rail centre line is x = 27.05 (hook lips at 9.8 and 44.3); the flange seat is z = 4.1.
rail_cx = 27.05;
strip_w = clip_len + 2*strip_pad;

// The two heat-insert holes, filled: the one at x = 5 runs through the fixed hook (7.5), the one at
// x = 56 through the shelf (4.6).
module clip() {
    translate([0, 0, 0.01]) rotate([0, 0, 90]) translate([-rail_cx, 0, 0]) union() {  // 0.01 into the frame, not coplanar
        import("ref_din_clip_heat_insert.stl");
        translate([5, 0, 0]) cylinder(d = 4.3, h = 7.5);
        translate([56, 0, 0]) cylinder(d = 4.3, h = 4.6);
    }
}

tie_y = -plate_w/2 - ext/2;   // the slot pairs' centre line, mid-extension
module pocket() translate([0, -ext/2]) offset(r = corner_r) square([plate_l - 2*corner_r, plate_w + ext - 2*corner_r], center = true);
module outline() offset(delta = lip_t) pocket();
// the PSU's own slots as plate cut-outs: the U opens to the back edge of the pocket, the pill is closed
module slots2d() {
    hull() { translate([uslot_x, plate_w/2 - uslot_depth + slot_w/2]) circle(d = slot_w); translate([uslot_x - slot_w/2, plate_w/2 - 0.01]) square([slot_w, 0.01]); }
    hull() for (s = [-1, 1]) translate([pill[0], pill[1] + s*(pill_len - slot_w)/2]) circle(d = slot_w);
}

// Perimeter rim, a solid band under each clip out to the side rim, a boss round each screw hole; the rest is open.
module frame2d() intersection() { outline(); union() {
    difference() { outline(); offset(delta = -rim_w) outline(); }
    for (sx = [-1, 1]) translate([sx*clip_x - strip_w/2, -plate_w/2 - lip_t]) square([strip_w, plate_w + 2*lip_t]);
    translate([-plate_l/2 - lip_t, -plate_w/2 - ext - lip_t]) square([plate_l + 2*lip_t, ext + rim_w + lip_t]);   // the extension is solid
    for (h = holes) translate(h) circle(d = boss_d);
    translate([uslot_x, plate_w/2 - uslot_depth/2]) square([boss_d, boss_d + 4], center = true);
    translate(pill) square([boss_d, pill_len + 4], center = true);
} }

// Each slot: local X along global X (the slot's length), local Y along global Y; s = -1 / +1 is the lower / upper
// slot of its pair, its chamfer opening away from the web between them.
module tie_slots() { for (x = tie_xs, s = [-1, 1]) translate([x, tie_y + s*tie_gap/2, -1]) linear_extrude(plate_t + 2) square([tie_w, tie_t], center = true); }
module tie_chamfers() {
    for (x = tie_xs, s = [-1, 1]) translate([x, tie_y + s*tie_gap/2]) hull() {
        translate([0, s*tie_c/2, -0.5]) linear_extrude(0.5) square([tie_w, tie_t + tie_c], center = true);
        translate([0, 0, tie_c]) linear_extrude(0.01) square([tie_w, tie_t], center = true);
    }
}

module base() {
    difference() {
        linear_extrude(plate_t) frame2d();
        for (h = holes) translate([h[0], h[1], -1]) cylinder(d = hole_d, h = plate_t + 2);
        translate([0, 0, -1]) linear_extrude(plate_t + 2) slots2d();
        tie_slots();
        tie_chamfers();
    }
}

module lip() linear_extrude(lip_h + 0.01) difference() { outline(); pocket(); }

module mount() {
    lip();
    translate([0, 0, lip_h]) {
        base();
        for (sx = [-1, 1]) translate([sx*clip_x, 0, 0]) clip();
    }
}

mount();
