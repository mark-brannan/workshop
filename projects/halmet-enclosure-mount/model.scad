// Frame that holds a Hat Labs HALMET board in the 158x90x60 pre-drilled box.
// Screws to the box's six holed floor bosses and rests on its four no-hole posts;
// two standoffs take the board's M3 slots. Zip-tie slots give the wiring strain relief.
// Four raised posts at the right end carry an SSD1306 display module above the board's level.
// Origin: centre of the box floor. X along the box length. Print flat, standoffs up.

mode = "2d";         // [2d:laser profile, 3d:print]
part = "frame";      // [frame, gauge:thin fit check of the same outline]

/* [Box: owner's estimates, tune after a gauge print] */
boss_span = 136;     // holed bosses, centre to centre along the box length
boss_pitch = 21;     // neighbouring bosses on one end
screw_d = 3.4;       // clearance for the screw into a boss
slot_reach = 4;      // each fork slot accepts the boss this far in or out of boss_span
boss_h = 3.5;        // holed boss height above the floor
boss_d = 6;          // holed boss outside diameter (photo)
lid_col_x = 64.8;    // lid-screw column in each corner, full height: inner edge along X (photo)
lid_col_y = 32.4;    // and across Y; keep the display clear of both

/* [Rest posts: four no-hole posts on the long sides] */
post_dx = 80;        // centre to centre along the length (photo 77 to 80)
post_dy = 70;        // centre to centre across the width (photo 67 to 69)
post_h = 2;          // lower than the bosses, so the frame underside steps down to meet them
frame_w = 75;        // overall width across the post pads
pad_l = 12;          // pad length along X; covers a post 4 mm either side of post_dx
gland_chamfer = 2;   // 45-degree chamfer on the top edge under the gland nuts

/* [Zip-tie strain relief: slot pairs, the tie loops under the frame] */
tie_w = 4;           // slot length; takes ties up to 3.6 mm wide
tie_t = 2;           // slot width
tie_gap = 5;         // slot centre to slot centre
tie_bar_y = -31;     // gland-side bar joining the two near-wall pads
tie_bar_w = 8;
tie_bar_xs = [-24, 0, 24];   // slot pairs on the gland-side bar
tie_end_ys = [-10.5, 10.5];  // slot pairs on the left end bar, between bosses

/* [Board position on the floor] */
board_dx = -8;       // toward the left end, to make room for the display
board_dy = 3;        // away from the gland-nut wall (-Y)

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

/* [Frame] */
plate_t = 3;
rail_w = 8;
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
rail_ys = [for (s = slots) s[1] + board_dy];
bar_x0 = boss_span/2 - slot_reach - screw_d/2 - 3;   // inner edge of an end bar
bar_x1 = boss_span/2 + slot_reach;                   // outer edge
oled_posts = [for (sx = [-1, 1], sy = [-1, 1]) [oled_x + sx*oled_hole_dx/2, oled_y + sy*oled_hole_dy/2]];
y_hi = max(boss_pitch + 6, max(rail_ys) + rail_w/2);
y_lo = min(-boss_pitch - 6, min(rail_ys) - rail_w/2);

module at_board(pts) { for (p = pts) translate([p[0] + board_dx, p[1] + board_dy]) children(); }

module solid2d() {
    offset(r = 1.5) offset(delta = -1.5) {
        for (sx = [-1, 1]) scale([sx, 1]) translate([bar_x0, y_lo]) square([bar_x1 - bar_x0, y_hi - y_lo]);
        for (y = rail_ys) translate([-bar_x0 - 1, y - rail_w/2]) square([2*bar_x0 + 2, rail_w]);
        translate([board_dx - rail_w/2, min(rail_ys)]) square([rail_w, max(rail_ys) - min(rail_ys)]);
        at_board(slots) circle(d = standoff_d + 2);
        at_board(rests) circle(d = rest_d + 4);
        for (sx = [-1, 1], sy = [-1, 1]) {
            rail = sy > 0 ? max(rail_ys) : min(rail_ys);
            translate([sx*post_dx/2 - pad_l/2, min(rail, sy*frame_w/2)])
                square([pad_l, abs(sy*frame_w/2 - rail)]);
        }
        translate([-post_dx/2, tie_bar_y - tie_bar_w/2]) square([post_dx, tie_bar_w]);
        if (oled) for (sy = [-1, 1])   // a bar under each pair of display posts
            translate([oled_x - oled_hole_dx/2 - 4, oled_y + sy*oled_hole_dy/2 - 4])
                square([min(oled_hole_dx + 8, bar_x1 - oled_x + oled_hole_dx/2 + 4), 8]);
    }
}

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
