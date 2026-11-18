// Assembly view, not a print: the frame, tier, boards, modules, standoffs and screws in the box.
// Stand-in boards are boxes; heights marked "guess" are not measured. assembly.py renders it in colour.
include <model.scad>
part = "assembly";
show = "frame";      // one component per run; assembly.py loops over them

/* [Stand-ins: guesses unless marked] */
floor_t = 2.5;       // guess
wall_t = 2.5;        // guess
hex_af = 5.5;        // M3 F/F standoff across flats (assumed)
board_z = body_t + standoff_h;      // HALMET underside
ldr_z = tier_z1 + ldr_ledge;        // LM393 underside, on its cradle
mod_z = tier_z1 + mod_standoff;     // OLED and TM1637 underside
floor_z = -boss_h;

// HALMET parts from the KiCad footprints (overlay.py): [x, y, w, d, h], board lower-left origin; heights guessed.
halmet_parts = [
    [1.0, 33.5, 41.0, 8.0, 10], [1.0, 23.2, 37.5, 8.0, 10], [1.5, 9.3, 15.5, 8.0, 10],   // terminal blocks
    [60.5, 30.0, 25.5, 18.0, 3.3],   // ESP32 module
    [82.0, 12.5, 6.0, 8.0, 3.3],     // USB
    [55.0, 48.5, 24.5, 5.2, 8.5], [7.6, 46.0, 10.5, 5.2, 8.5]];   // headers

module hexpost(h) { cylinder(d = hex_af / cos(30), h = h, $fn = 6); }
module head(d = head_d, h = head_h) { cylinder(d = d, h = h); }

module box() {
    L = 151; W = 83;
    translate([-L/2 - wall_t, -W/2 - wall_t, floor_z - floor_t]) difference() {
        cube([L + 2*wall_t, W + 2*wall_t, floor_t + rim_z]);
        translate([wall_t, wall_t, floor_t]) cube([L, W, rim_z]);
        for (i = [0:5]) translate([L/2 + wall_t - 62.5 + i*25, -1, floor_t + 20]) rotate([-90, 0, 0]) cylinder(d = 13, h = wall_t + 2);
    }
    for (sx = [-1, 1], k = [-1, 0, 1]) translate([sx*boss_span/2, k*boss_pitch, floor_z]) cylinder(d = boss_d, h = boss_h);
    for (sx = [-1, 1], sy = [-1, 1]) translate([sx*post_dx/2, sy*post_dy/2, floor_z]) cylinder(d = 5, h = post_h);
    for (sx = [-1, 1], sy = [-1, 1]) scale([sx, sy, 1]) translate([lid_col_x, lid_col_y, floor_z]) cube([75.5 - lid_col_x, 41.5 - lid_col_y, rim_z]);
}

module lid() { translate([-79, -45, rim_z - boss_h + lid_depth]) cube([158, 90, wall_t]); }

module halmet() {
    translate([board_dx - 44.5, board_dy - 29, board_z]) {
        linear_extrude(pcb_t) difference() {
            union() { square([83, 58]); square([89, 24.7]); }
            for (c = [[0, 0], [89, 0], [0, 58]]) translate(c) circle(r = 8.5);
            for (s = slots) translate([s[0] + 44.5, s[1] + 29]) rotate(45) hull() for (d = [-0.8, 0.8]) translate([d, 0]) circle(d = 3.2);
        }
        for (p = halmet_parts) translate([p[0], p[1], pcb_t]) cube([p[2], p[3], p[4]]);
    }
}

module oled() {
    translate([oled_x - oled_w/2, oled_y - oled_h/2, mod_z]) cube([oled_w, oled_h, pcb_t]);
}
module oled_header() {   // pins out the front edge, toward the glands, a Dupont plug on them through the tier
    translate([oled_x, oled_y - oled_h/2 + oled_pin_in, mod_z]) {
        translate([-5.08, -1.27, -2.5]) cube([10.16, 2.54, 2.5]);
        translate([-5.08, -1.27, -2.5 - 14]) cube([10.16, 2.54, 14 - 6]);
        for (i = [0:3]) translate([-3.81 + i*2.54 - 0.32, -0.32, -8.5]) cube([0.64, 0.64, 8.5]);
    }
}
module oled_glass() { translate([oled_x - 13, oled_y - 9.5 + 2, mod_z + pcb_t]) cube([26, 19, 1.5]); }
module seg() { translate([seg_x - seg_w/2, seg_y - seg_h/2, mod_z]) cube([seg_w, seg_h, pcb_t]); }
module seg_body() { translate([seg_x - 15, seg_y - 7, mod_z + pcb_t]) cube([30, 14, 7 - pcb_t]); }

module ldr() {
    translate([ldr_x0, ldr_y - ldr_w/2, ldr_z]) {
        cube([ldr_l, ldr_w, pcb_t]);
        translate([12, 2, pcb_t]) cube([7, 7, ldr_part_h]);                       // trimpot (guess)
        translate([ldr_l - 2.5, ldr_w/2 - 3.8, pcb_t]) cube([2.5, 7.6, 2.5]);      // header
        for (dy = [-2.54, 0, 2.54]) translate([ldr_l, ldr_w/2 + dy - 0.32, pcb_t + 0.94]) cube([ldr_pin_l, 0.64, 0.64]);   // pins, straight out
    }
    translate([ldr_x0 - 1, ldr_y, ldr_z + pcb_t]) {                               // photocell on leads bent up
        cylinder(d = 0.6, h = 3, $fn = 8);
        translate([0, 0, 3]) cylinder(d = 5, h = 2);
    }
}

module tier_standoffs() { for (c = tier_cols) translate([c[0], c[1], tier_z0]) hexpost(tier_standoff); }
module module_standoffs() { for (p = concat(oled_posts, seg_posts)) translate([p[0], p[1], tier_z1]) cylinder(d = 5 / cos(30), h = mod_standoff, $fn = 6); }

module screws_floor() { for (sx = [-1, 1], k = [-1, 0, 1]) translate([sx*boss_span/2, k*boss_pitch, body_t - relief_h]) head(); }
module screws_board() { at_board(slots) translate([0, 0, board_z + pcb_t]) head(); }
module screws_tier() { for (c = tier_cols) translate([c[0], c[1], tier_z1]) head(); }
module screws_ldr() {   // M3 up from under the tier, nut on the board top
    translate([ldr_post[0], ldr_post[1], tier_z1 - tier_t - 2.5]) head(5.7, 2.5);
    translate([ldr_post[0], ldr_post[1], ldr_z + pcb_t]) head(5.5, 2.4);
}
module screws_m25() {
    for (p = concat(oled_posts, seg_posts)) {
        translate([p[0], p[1], tier_z1 - tier_t - 2]) head(4.5, 2);
        translate([p[0], p[1], mod_z + pcb_t]) head(4.5, 2);
    }
}

if (show == "box") box();
else if (show == "lid") lid();
else if (show == "frame") frame();
else if (show == "tier") tier();
else if (show == "halmet") halmet();
else if (show == "oled") oled();
else if (show == "oled_header") oled_header();
else if (show == "oled_glass") oled_glass();
else if (show == "seg") seg();
else if (show == "seg_body") seg_body();
else if (show == "ldr") ldr();
else if (show == "tier_standoffs") tier_standoffs();
else if (show == "module_standoffs") module_standoffs();
else if (show == "screws_floor") screws_floor();
else if (show == "screws_board") screws_board();
else if (show == "screws_tier") screws_tier();
else if (show == "screws_ldr") screws_ldr();
else if (show == "screws_m25") screws_m25();
