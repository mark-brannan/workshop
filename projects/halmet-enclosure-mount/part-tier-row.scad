// Flat tier carrying an OLED and two TM1637 modules end to end, with the LM393 light sensor hung under it.
// Sketch stage: the plate's supports are not drawn, and the modules are not part of the print. Millimetres, installed orientation:
// plate top at z = 0, module bosses up, the sensor mount down. Origin as model.scad (box floor centre).
/* [Plate] */
plate_t = 2.5;
x0 = 26;  x1 = 72;       // plate edges; the back part stops at x_back for the lid-screw column
x_back = 63.8;
y_front = -38;  y_back = 39.5;  y_col = 31.4;   // the full-width part spans -y_col..y_col
round_r = 1.5;
/* [Modules, one centre line, end to end: 24 + 24 + 28] */
cx = 47.5;
tm_y = [-25, -1];        // TM1637 centres, 23 x 41 boards
oled_y = 25.4;           // 27.3 x 27.8 board
tm_dx = 37.5;  tm_dy = 19;   // module screw spacing
oled_dx = 23.3;  oled_dy = 23.6;
tm_boss_h = 3;  tm_boss_d = 6;  tm_hole = 2.8;       // M2.5
oled_boss_h = 5.5;  oled_boss_d = 4.5;  oled_hole = 0.9;   // self-tapping M1 pilot
/* [Light sensor under the plate] */
ldr_x0 = 25.5;  ldr_y = -25;  ldr_l = 31;  ldr_w = 14;
ldr_hole_in = 7;         // screw hole from the header end
ldr_pad_h = 5;           // trimpot 4.6 + 0.4
ldr_pad_d = 7;  ldr_insert_d = 4;  ldr_insert_depth = 4;   // M3 heat-set insert, screw comes up from below
ldr_wall = 1.2;  ldr_fit = 0.3;  pcb_t = 1.6;
$fn = 48;

tm_posts = [for (y = tm_y, sx = [-1, 1], sy = [-1, 1]) [cx + sx*tm_dx/2, y + sy*tm_dy/2]];
oled_posts = [for (sx = [-1, 1], sy = [-1, 1]) [cx + sx*oled_dx/2, oled_y + sy*oled_dy/2]];

module rr(a, b, c, d) { offset(r = round_r) offset(delta = -round_r) translate([a, b]) square([c - a, d - b]); }

module plate() {
    translate([0, 0, -plate_t]) linear_extrude(plate_t) difference() {
        union() { rr(x0, y_front, x_back, y_back); rr(x0, -y_col, x1, y_col); }
    }
}
module bosses() translate([0, 0, -0.01]) {
    linear_extrude(tm_boss_h + 0.01) for (p = tm_posts) translate(p) circle(d = tm_boss_d);
    linear_extrude(oled_boss_h + 0.01) for (p = oled_posts) translate(p) circle(d = oled_boss_d);
}
module ldr_mount() {
    hx = ldr_x0 + ldr_l - ldr_hole_in;
    translate([hx, ldr_y, -plate_t - ldr_pad_h]) cylinder(d = ldr_pad_d, h = ldr_pad_h + 0.01);
    for (s = [-1, 1])   // side walls beside the board, from the pad toward the cell end, stopping it turning
        translate([ldr_x0 + 6, ldr_y + (s > 0 ? ldr_w/2 + ldr_fit : -ldr_w/2 - ldr_fit - ldr_wall), -plate_t - ldr_pad_h - pcb_t])
            cube([ldr_l - 8, ldr_wall, ldr_pad_h + pcb_t + 0.01]);
}
difference() {
    union() { plate(); bosses(); ldr_mount(); }
    for (p = tm_posts) translate([p[0], p[1], -plate_t - 1]) cylinder(d = tm_hole, h = plate_t + tm_boss_h + 2);
    for (p = oled_posts) translate([p[0], p[1], -plate_t - 1]) cylinder(d = oled_hole, h = plate_t + oled_boss_h + 2, $fn = 16);
    // M3 heat-set insert, blind, open at the pad's bottom face where the board sits
    translate([ldr_x0 + ldr_l - ldr_hole_in, ldr_y, -plate_t - ldr_pad_h - 0.01]) cylinder(d = ldr_insert_d, h = ldr_insert_depth);
}
