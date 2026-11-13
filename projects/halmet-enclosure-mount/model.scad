// Frame that holds a Hat Labs HALMET board in the 158x90x60 pre-drilled box.
// Screws to the box's six holed floor bosses and rests on its four no-hole posts;
// two standoffs take the board's M3 slots. Zip-tie slots give the wiring strain relief.
// A separate tier (part-tier.scad) screws onto it and carries the displays at rim height.
// Origin: centre of the box floor. X along the box length. Print flat, standoffs up; the tier prints upside down.

mode = "2d";         // [2d:laser profile, 3d:print]
part = "frame";      // [frame, gauge:thin fit check of the same outline, tier:display tier, 3D only]

/* [Box: owner's estimates, tune after a gauge print] */
boss_span = 140;     // holed bosses, centre to centre: first print, scaled by its own 144 mm length (136 put the screws at the fork mouths)
boss_pitch = 21;     // neighbouring bosses on one end
screw_d = 3.4;       // clearance for the screw into a boss
slot_reach = 2.5;    // each fork slot accepts the boss this far in or out of boss_span
boss_h = 3.5;        // holed boss height above the floor
boss_d = 6;          // holed boss outside diameter (photo)
lid_col_x = 64.8;    // lid-screw column in each corner, full height: inner edge along X (photo)
lid_col_y = 32.4;    // and across Y; keep the display clear of both

/* [Rest posts: four no-hole posts on the long sides] */
post_dx = 80;        // centre to centre along the length (photo 77 to 80)
post_dy = 70;        // centre to centre across the width (photo 67 to 69)
post_h = 2.5;        // ~1 below the bosses (owner); the flat frame clears them by that, a stick-on pad closes it
frame_w = 75;        // gland side: pads stop at -frame_w/2, short of the gland nuts
pad_r = 4.5;         // semicircle tab over each rest post (post ~5 diameter)
gland_chamfer = 2;   // 45-degree chamfer on the top edge under the gland nuts

/* [Zip-tie strain relief: slot pairs, the tie loops under the frame] */
tie_w = 4;           // slot length; takes ties up to 3.6 mm wide
tie_t = 2;           // slot width
tie_gap = 5;         // slot centre to slot centre
tie_c = 1;           // underside chamfer on each slot's outer edge, where the tie turns under
tie_bar_y = -29;     // slot pairs along the gland-side edge
tie_bar_xs = [-55, -33, -11, 11, 33, 55];  // evenly along the gland-side edge
tie_end_ys = [-10.5, 10.5];  // slot pairs on the left end, between bosses

/* [Board position on the floor] */
board_dx = -20.75;   // left edge just clear of the left fork slots
board_dy = 12.5;     // back edge about at the box's back wall (owner checked the fit)

/* [Display tier: separate part, screwed to four M3-insert bosses on the plate] */
rim_z = 39;          // box floor to rim (owner)
tier_t = 2.5;        // top plate; its top sits at the rim
tier_x0 = 26;        // left edge; the left side stays open for the USB plug and wiring
tier_x1 = 72;        // right edge, a cantilever past the right wall
tier_y0 = -16;       // front edge
wall_t = 2;
wall_x = 60;         // right wall, inside the plate's end bar
tier_cols = [[31, 34.5], [54, 34.5], [37, -11.25], [58, -11.25]];  // screw columns
col_d = 9.5;
col_bore = 6.2;      // M3 pan head and driver, from above through the top plate
tier_boss_h = 3;     // M3-insert bosses on the plate under the columns
tier_boss_d = 8;
module_rise = 3;     // module standoffs above the tier top; clears parts on the module's back
mod_post_d = 5;
pilot_d = 2.2;       // M2.5 self-tapping, through standoff and plate
oled_w = 27.3;       // 0.96" SSD1306, generic
oled_h = 27.8;
oled_hole_dx = 23.3; // caliper the one in hand
oled_hole_dy = 23.6;
oled_x = 49.65;      // back posts inside the plate's back edge, right edge 0.5 clear of the lid-screw column
oled_y = 25.2;
seg_w = 41;          // TM1637 4-digit module (owner)
seg_h = 23;
seg_hole_dx = 36;    // owner, rough calipers
seg_hole_dy = 19;    // owner
seg_gap = 1.5;       // below the OLED, toward the glands

/* [Plate: hex-lightened] */
plate_t = 4.5;
plate_y_lo = -33;    // gland-side edge between the lid-screw columns
plate_y_hi = 39.5;   // back edge between the lid-screw columns, tangent to the rear post tabs
rim_w = 2;           // solid rim round the outline
hex_flat = 9;         // hex cell across flats
hex_web = 2.0;       // wall between cells
hex_x0 = 1.5;        // grid offset
hex_y0 = 3;
gauge_t = 0.8;

/* [Standoffs] */
standoff_h = 6;      // board underside above the frame; clears pin stubs
standoff_d = 8;
insert_d = 4.0;      // M3 heat-set insert
insert_depth = 6.5;  // blind, from the standoff top
rest_d = 4;          // plain rests on the other diagonal
spacer_hole_d = 3.2; // laser and gauge: M3 through a loose spacer

/* [Hidden] */
$fn = 48;
// From HALMET.kicad_pcb, relative to the centre of the 89 x 58 board.
slots = [[-21.75, 22.5], [22.75, -22.5]];
drop = 0;            // flat underside on the bosses: pockets over them printed badly
body_t = plate_t + drop;
rests = [[36, 18], [-38.5, -19.5]];
bar_x0 = boss_span/2 - slot_reach - screw_d/2 - 3;   // inner edge of an end bar
bar_x1 = boss_span/2 + slot_reach;                   // outer edge
seg_x = oled_x;
seg_y = oled_y - oled_h/2 - seg_gap - seg_h/2;
oled_posts = [for (sx = [-1, 1], sy = [-1, 1]) [oled_x + sx*oled_hole_dx/2, oled_y + sy*oled_hole_dy/2]];
seg_posts = [for (sx = [-1, 1], sy = [-1, 1]) [seg_x + sx*seg_hole_dx/2, seg_y + sy*seg_hole_dy/2]];
tier_z0 = body_t + tier_boss_h;        // column feet
tier_z1 = rim_z - boss_h;              // top of the tier plate
y_hi = boss_pitch + 6;    // end bars
y_lo = -boss_pitch - 6;

module at_board(pts) { for (p = pts) translate([p[0] + board_dx, p[1] + board_dy]) children(); }

// Outline: one plate over the bosses, the four rest posts, the board and the display.
module outline2d() {
    intersection() {
        union() {
            offset(r = 2) offset(delta = -2) for (r = plate_rects) translate([r[0], r[1]]) square([r[2] - r[0], r[3] - r[1]]);
            for (sx = [-1, 1], sy = [-1, 1]) translate([sx*post_dx/2, sy*post_dy/2]) circle(r = pad_r);
            at_board(slots) circle(r = standoff_d/2 + 0.5);   // the back one stays inside the straight back edge
        }
        translate([-100, -frame_w/2]) square([200, 100 + frame_w/2]);
    }
}

// Lattice: hex cells inside the rim, a web clear of every solid island
// (screw ends, post pads, standoffs, rests, display posts, tie slots).
hex_r = hex_flat/sqrt(3);                     // cell circumradius
hex_pitch = hex_flat + hex_web;
plate_rects = concat(                         // outline as [x0, y0, x1, y1] boxes
    [[-bar_x1, y_lo, bar_x1, y_hi], [-lid_col_x + 1, plate_y_lo, lid_col_x - 1, plate_y_hi]],
    [for (sx = [-1, 1]) [sx*post_dx/2 - pad_r, -post_dy/2, sx*post_dx/2 + pad_r, plate_y_lo + 1]]);  // front tabs reach the posts
keep_rects = concat(
    [[-100, -100, -(boss_span/2 - slot_reach - screw_d/2 - 1.5), 100], [boss_span/2 - slot_reach - screw_d/2 - 1.5, -100, 100, 100]],
    [[-lid_col_x + 1, -100, lid_col_x - 1, tie_bar_y + tie_w/2 + 2]],   // solid band along the gland side
    [for (x = tie_bar_xs) [x - tie_gap/2 - tie_t/2 - 2, tie_bar_y - tie_w/2 - 2, x + tie_gap/2 + tie_t/2 + 2, tie_bar_y + tie_w/2 + 2]],
    [for (y = tie_end_ys) [-bar_x1, y - tie_gap/2 - tie_t/2 - 2, -(bar_x0 + bar_x1)/2 + tie_w/2 + 2, y + tie_gap/2 + tie_t/2 + 2]]);
keep_discs = concat(   // [x, y, r]
    [for (sx = [-1, 1], sy = [-1, 1]) [sx*post_dx/2, sy*post_dy/2, pad_r]],
    [for (s = slots) [s[0] + board_dx, s[1] + board_dy, standoff_d/2 + 2]],
    [for (s = rests) [s[0] + board_dx, s[1] + board_dy, rest_d/2 + 2]],
    [for (c = tier_cols) [c[0], c[1], tier_boss_d/2]]);


module keep2d() {
    for (r = keep_rects) translate([r[0], r[1]]) square([r[2] - r[0], r[3] - r[1]]);
    for (d = keep_discs) translate([d[0], d[1]]) circle(r = d[2]);
}

// Full hex grid clipped to the rim and a web clear of the islands; cells cut there stay,
// slivers narrower than 2.5 mm drop out.
module lattice2d() {
    offset(r = 1.25) offset(r = -1.25) intersection() {
        difference() { offset(delta = -rim_w) outline2d(); offset(delta = hex_web) keep2d(); }
        for (i = [-12:12], j = [-8:8])
            translate([hex_x0 + i*hex_pitch + (j % 2 == 0 ? 0 : hex_pitch/2), hex_y0 + j*hex_pitch*sqrt(3)/2])
                offset(r = 0.8) offset(delta = -0.8) rotate(30) circle(r = hex_r, $fn = 6);
    }
}

module solid2d() { difference() { outline2d(); lattice2d(); } }

// Children at each tie slot's centre: slot length along local Y, local +X away from its pair's web.
module tie_each() {
    for (x = tie_bar_xs, s = [-1, 1]) translate([x + s*tie_gap/2, tie_bar_y]) mirror([s < 0 ? 1 : 0, 0]) children();
    for (y = tie_end_ys, s = [-1, 1]) translate([-(bar_x0 + bar_x1)/2, y + s*tie_gap/2]) rotate(90) mirror([s < 0 ? 1 : 0, 0]) children();
}

module tie_slots() { tie_each() square([tie_t, tie_w], center = true); }

module tie_chamfers() {
    tie_each() hull() {
        translate([0, 0, -1]) linear_extrude(1) translate([tie_c/2, 0]) square([tie_t + tie_c, tie_w + 0.02], center = true);
        translate([0, 0, tie_c]) linear_extrude(0.01) square([tie_t - 0.02, tie_w + 0.02], center = true);
    }
}

module fork_slots() {
    for (sx = [-1, 1], k = [-1, 0, 1]) scale([sx, 1]) translate([0, k*boss_pitch]) hull() {
        translate([boss_span/2 - slot_reach, 0]) circle(d = screw_d);
        translate([bar_x1 + 2, 0]) circle(d = screw_d);
    }
}

module profile(spacer_holes) {
    difference() {
        solid2d();
        fork_slots();
        tie_slots();
        if (spacer_holes) at_board(slots) circle(d = spacer_hole_d);
    }
}

// Z = 0 is the top of the rest posts; the holed bosses reach up into the pockets.
module frame() {
    difference() {
        union() {
            linear_extrude(body_t) profile(false);
            linear_extrude(body_t + standoff_h) at_board(slots) circle(d = standoff_d);
            linear_extrude(body_t + standoff_h) at_board(rests) circle(d = rest_d);
            linear_extrude(tier_z0) for (c = tier_cols) translate(c) circle(d = tier_boss_d);
        }
        translate([0, 0, tier_z0 - insert_depth]) linear_extrude(insert_depth + 1)
            for (c = tier_cols) translate(c) circle(d = insert_d);
        translate([0, 0, body_t + standoff_h - insert_depth])
            linear_extrude(insert_depth + 1) at_board(slots) circle(d = insert_d);
        tie_chamfers();
        translate([0, -frame_w/2, body_t]) rotate([45, 0, 0])
            cube([200, gland_chamfer*sqrt(2), gland_chamfer*sqrt(2)], center = true);
        if (drop > 0) translate([0, 0, -1]) linear_extrude(drop + 1)
            for (sx = [-1, 1], k = [-1, 0, 1]) scale([sx, 1]) translate([0, k*boss_pitch]) hull() {
                translate([boss_span/2 - slot_reach, 0]) circle(d = boss_d + 2);
                translate([bar_x1 + 2, 0]) circle(d = boss_d + 2);
            }
    }
}

// Tier, in box coordinates (Z = 0 on the rest posts). Top plate at the rim, three walls
// (left side open), four hollow screw columns onto the plate's bosses, modules on short posts.
module tier_plate2d() {
    translate([tier_x0, tier_y0]) square([tier_x1 - tier_x0, lid_col_y - 1 - tier_y0]);
    translate([tier_x0, tier_y0]) square([lid_col_x - 1 - tier_x0, plate_y_hi - tier_y0]);
}

module wall_hex2d(l, h) {   // hex windows, a vertex toward the plate so the tier prints upside down unsupported
    offset(r = 1) offset(r = -1) intersection() {
        translate([3, 3]) square([l - 6, h - 6]);
        for (i = [-1:12], j = [0:4])
            translate([i*hex_pitch + (j % 2 == 0 ? 0 : hex_pitch/2), 3 + hex_r + j*hex_pitch*sqrt(3)/2])
                rotate(30) circle(r = hex_r, $fn = 6);
    }
}

module tier_wall(p0, p1) {   // a wall from p0 to p1 (plan), wall_t thick on its left
    l = norm(p1 - p0); h = tier_z1 - tier_t - tier_z0;
    translate([p0[0], p0[1], tier_z0]) rotate([0, 0, atan2(p1[1] - p0[1], p1[0] - p0[0])]) rotate([90, 0, 0])
        translate([0, 0, -wall_t]) linear_extrude(wall_t) difference() { square([l, h + 0.01]); wall_hex2d(l, h); }
}

module tier() {
    yb = plate_y_hi - wall_t;
    difference() {
        union() {
            translate([0, 0, tier_z1 - tier_t]) linear_extrude(tier_t) tier_plate2d();
            tier_wall([tier_x0, tier_y0], [wall_x, tier_y0]);
            tier_wall([wall_x, tier_y0], [wall_x, plate_y_hi]);
            tier_wall([wall_x, plate_y_hi], [tier_x0, plate_y_hi]);
            translate([0, 0, tier_z0]) linear_extrude(tier_z1 - tier_z0) for (c = tier_cols) translate(c) circle(d = col_d);
            translate([0, 0, tier_z1]) linear_extrude(module_rise) for (p = concat(oled_posts, seg_posts)) translate(p) circle(d = mod_post_d);
        }
        translate([0, 0, tier_z0 - 1]) linear_extrude(tier_z1 + module_rise + 2) {
            for (c = tier_cols) translate(c) circle(d = screw_d);
            for (p = concat(oled_posts, seg_posts)) translate(p) circle(d = pilot_d);
        }
        translate([0, 0, tier_z0 + tier_boss_h]) linear_extrude(tier_z1) for (c = tier_cols) translate(c) circle(d = col_bore);
        translate([0, 0, tier_z1 - tier_t - 0.01]) linear_extrude(tier_t + 1.01) offset(r = 1.5) offset(delta = -1.5) {
            // wire windows inside each module's hole pattern; the OLED's reaches toward its header edge
            translate([oled_x - oled_hole_dx/2 + 4, oled_y - oled_hole_dy/2 + 4]) square([oled_hole_dx - 8, oled_hole_dy/2 - 4 + oled_h/2 - 2]);
            translate([seg_x - seg_hole_dx/2 + 4, seg_y - seg_hole_dy/2 + 4]) square([seg_hole_dx - 8, seg_hole_dy - 8]);
        }
    }
}

if (part == "tier") tier();
else if (mode == "2d") profile(true);
else if (part == "gauge") linear_extrude(gauge_t) profile(true);
else frame();
