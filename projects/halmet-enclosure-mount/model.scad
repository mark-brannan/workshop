// Frame that holds a Hat Labs HALMET board in the 158x90x60 pre-drilled box.
// Screws to the box's six holed floor bosses and rests on its four no-hole posts;
// two standoffs take the board's M3 slots. Zip-tie slots give the wiring strain relief.
// Four raised posts at the right end carry an SSD1306 display module above the board's level.
// Origin: centre of the box floor. X along the box length. Print flat, standoffs up.

mode = "2d";         // [2d:laser profile, 3d:print]
part = "frame";      // [frame, gauge:thin fit check of the same outline]

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
post_h = 2;          // lower than the bosses, so the frame underside steps down to meet them
frame_w = 75;        // gland side: pads stop at -frame_w/2, short of the gland nuts
pad_r = 4.5;         // semicircle tab over each rest post (post ~5 diameter)
gland_chamfer = 2;   // 45-degree chamfer on the top edge under the gland nuts

/* [Zip-tie strain relief: slot pairs, the tie loops under the frame] */
tie_w = 4;           // slot length; takes ties up to 3.6 mm wide
tie_t = 2;           // slot width
tie_gap = 5;         // slot centre to slot centre
tie_bar_y = -29;     // slot pairs along the gland-side edge
tie_bar_xs = [-24, 24];
tie_end_ys = [-10.5, 10.5];  // slot pairs on the left end, between bosses

/* [Board position on the floor] */
board_dx = -18.25;   // puts the board's top-left slot standoff over the back-left rest post:
board_dy = 12.5;     // -post_dx/2 + 21.75, post_dy/2 - 22.5

/* [Display: 0.96" SSD1306 module on four raised posts at the right end] */
oled = 1;            // 0 leaves the display posts off
oled_x = 50.5;       // module centre; inner posts clear the ESP32 antenna overhang by 2.3
oled_y = 17;         // posts miss the boss screws, the lid-screw column and the USB plug's path
oled_hole_dx = 23.3; // hole centres, generic module; caliper the one in hand
oled_hole_dy = 23.6;
oled_rise = 18;      // post height above the frame top: module ~10 mm above the HALMET's top face
oled_post_d = 6;
oled_insert_d = 3.2; // M2 heat-set insert
oled_insert_depth = 4.5;

/* [Plate: hex-lightened] */
plate_t = 3;
plate_y_lo = -33;    // gland-side edge between the lid-screw columns
plate_y_hi = 35;     // back edge between the lid-screw columns, on the rest-post centres
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
drop = max(0, boss_h - post_h);   // underside pockets this deep over the holed bosses
body_t = plate_t + drop;
rests = [[36, 18], [-38.5, -19.5]];
bar_x0 = boss_span/2 - slot_reach - screw_d/2 - 3;   // inner edge of an end bar
bar_x1 = boss_span/2 + slot_reach;                   // outer edge
oled_posts = [for (sx = [-1, 1], sy = [-1, 1]) [oled_x + sx*oled_hole_dx/2, oled_y + sy*oled_hole_dy/2]];
y_hi = boss_pitch + 6;    // end bars
y_lo = -boss_pitch - 6;

module at_board(pts) { for (p = pts) translate([p[0] + board_dx, p[1] + board_dy]) children(); }

// Outline: one plate over the bosses, the four rest posts, the board and the display.
module outline2d() {
    intersection() {
        union() {
            offset(r = 2) offset(delta = -2) for (r = plate_rects) translate([r[0], r[1]]) square([r[2] - r[0], r[3] - r[1]]);
            for (sx = [-1, 1], sy = [-1, 1]) translate([sx*post_dx/2, sy*post_dy/2]) circle(r = pad_r);
            at_board(slots) circle(r = standoff_d/2 + rim_w);
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
    [for (sx = [-1, 1]) [sx*post_dx/2 - pad_r, -post_dy/2, sx*post_dx/2 + pad_r, plate_y_lo + 1]],  // front tabs reach the posts
    oled ? [[oled_x - oled_hole_dx/2 - oled_post_d, y_hi - 1, lid_col_x - 1, oled_y + oled_hole_dy/2 + oled_post_d/2 + 2]] : []);
keep_rects = concat(
    [[-100, -100, -(boss_span/2 - slot_reach - screw_d/2 - 1.5), 100], [boss_span/2 - slot_reach - screw_d/2 - 1.5, -100, 100, 100]],
    [for (x = tie_bar_xs) [x - tie_gap/2 - tie_t/2 - 2, tie_bar_y - tie_w/2 - 2, x + tie_gap/2 + tie_t/2 + 2, tie_bar_y + tie_w/2 + 2]],
    [for (y = tie_end_ys) [-bar_x1, y - tie_gap/2 - tie_t/2 - 2, -(bar_x0 + bar_x1)/2 + tie_w/2 + 2, y + tie_gap/2 + tie_t/2 + 2]]);
keep_discs = concat(   // [x, y, r]
    [for (sx = [-1, 1], sy = [-1, 1]) [sx*post_dx/2, sy*post_dy/2, pad_r]],
    [for (s = slots) [s[0] + board_dx, s[1] + board_dy, standoff_d/2 + 2]],
    [for (s = rests) [s[0] + board_dx, s[1] + board_dy, rest_d/2 + 2]],
    oled ? [for (p = oled_posts) [p[0], p[1], oled_post_d/2 + 1.5]] : []);


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

module tie_pair(along_x) {
    for (s = [-1, 1]) translate(along_x ? [s*tie_gap/2, 0] : [0, s*tie_gap/2])
        square(along_x ? [tie_t, tie_w] : [tie_w, tie_t], center = true);
}

module tie_slots() {
    for (x = tie_bar_xs) translate([x, tie_bar_y]) tie_pair(true);
    for (y = tie_end_ys) translate([-(bar_x0 + bar_x1)/2, y]) tie_pair(false);
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
            if (oled) linear_extrude(body_t + oled_rise) for (p = oled_posts) translate(p) circle(d = oled_post_d);
        }
        if (oled) translate([0, 0, body_t + oled_rise - oled_insert_depth]) linear_extrude(oled_insert_depth + 1)
            for (p = oled_posts) translate(p) circle(d = oled_insert_d);
        translate([0, 0, body_t + standoff_h - insert_depth])
            linear_extrude(insert_depth + 1) at_board(slots) circle(d = insert_d);
        translate([0, -frame_w/2, body_t]) rotate([45, 0, 0])
            cube([200, gland_chamfer*sqrt(2), gland_chamfer*sqrt(2)], center = true);
        if (drop > 0) translate([0, 0, -1]) linear_extrude(drop + 1)
            for (sx = [-1, 1], k = [-1, 0, 1]) scale([sx, 1]) translate([0, k*boss_pitch]) hull() {
                translate([boss_span/2 - slot_reach, 0]) circle(d = boss_d + 2);
                translate([bar_x1 + 2, 0]) circle(d = boss_d + 2);
            }
    }
}

if (mode == "2d") profile(true);
else if (part == "gauge") linear_extrude(gauge_t) profile(true);
else frame();
