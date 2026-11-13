// Assembly view: frame, tier and sensor standoffs, with stand-in boards. A picture, not a print.
// Board and module bodies are blocks at approximate positions and heights; only their outlines,
// holes and mounting heights come from model.scad.
include <model.scad>
part = "assembly";
show = "boards";      // [tiers, boards]
mod_standoff = 6;     // M2.5 F/F under each display module: guess

hex_d = 5.5 / cos(30);
module hexpost(p, z0, z1, c = "goldenrod") color(c) translate([p[0], p[1], z0]) cylinder(d = hex_d, h = z1 - z0, $fn = 6);
module block(x0, y0, x1, y1, z0, h, c) color(c) translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, h]);

// HALMET, board-local: origin lower-left, 89 x 58; R8.5 concave at three corners, USB tab step on the right.
module halmet() {
    z = body_t + standoff_h;
    translate([board_dx - 44.5, board_dy - 29, 0]) {
        color("#1f6f3a") translate([0, 0, z]) linear_extrude(1.6) difference() {
            square([89, 58]);
            for (c = [[0, 0], [0, 58], [89, 0]]) translate(c) circle(r = 8.5);
            translate([83, 24.7]) square([7, 40]);
            for (s = slots) translate([s[0] + 44.5, s[1] + 29]) circle(d = 3.2);
        }
        t = z + 1.6;
        block(1, 33.5, 42, 41.5, t, 10, "#2e9e4f");      // terminal blocks (positions from the overlay)
        block(1, 23.2, 38.5, 31.2, t, 10, "#2e9e4f");
        block(1.6, 9.3, 17, 17.3, t, 10, "#2e9e4f");     // N2K / power
        block(60.5, 30, 82, 48, t, 3.2, "silver");       // ESP32 module
        block(55, 48.5, 79.6, 53.7, t, 8.5, "#222");     // 2x10 header
        block(7.6, 46, 18.2, 51.2, t, 8.5, "#222");      // 2x4 header
        block(82, 12.5, 89, 20.5, t, 3.3, "silver");     // USB-C
    }
}

module oled() {
    z = tier_z1 + mod_standoff;
    for (p = oled_posts) hexpost(p, tier_z1, z, "silver");
    translate([oled_x, oled_y, z]) {
        color("#1b3b8f") translate([-oled_w/2, -oled_h/2, 0]) cube([oled_w, oled_h, 1.2]);
        color("#111") translate([-oled_w/2 + 0.5, -oled_h/2 + 4.5, 1.2]) cube([oled_w - 1, 19, 1.5]);
        color("#222") translate([-5, oled_h/2 - 3.5, 1.2]) cube([10, 2.5, 8.5]);
    }
}

module seg() {
    z = tier_z1 + mod_standoff;
    for (p = seg_posts) hexpost(p, tier_z1, z, "silver");
    translate([seg_x, seg_y, z]) {
        color("#1b3b8f") translate([-seg_w/2, -seg_h/2, 0]) cube([seg_w, seg_h, 1.6]);
        color("#222") translate([-15 - 1.5, -7 - 0.25, 1.6]) cube([30, 14, 7 - 1.6]);   // display body, face 7 above the board
        color("#222") translate([seg_w/2 - 2.5, -5, -5]) cube([2.5, 10, 5]);            // pins bent down at the back
    }
}

module sensor() {
    z = body_t + ldr_standoff;
    for (p = ldr_posts) hexpost(p, body_t, z);
    translate([ldr_x0, ldr_y, z]) {
        color("#1b5fbf") translate([0, -ldr_w/2, 0]) cube([ldr_l, ldr_w, pcb_t]);
        color("#2b6fe0") translate([12, -1, pcb_t]) cube([7, 6.6, ldr_part_h]);      // trimpot
        color("#111") translate([19, -5, pcb_t]) cube([5, 4, 1.5]);                  // LM393
        color("#c0392b") translate([-1.5, 0, pcb_t + 3]) cylinder(d = 5, h = 2);     // photocell, leads bent up
        color("silver") for (dy = [-1.3, 1.3]) translate([-1.5, dy, pcb_t]) cylinder(d = 0.5, h = 3);
        color("#222") translate([ldr_l, -3.75, -2.5 - 12]) cube([2.5, 7.5, 12]);     // header bent down, Dupont plug
    }
}

color("#c9cdd3") frame();
for (c = tier_cols) hexpost(c, tier_z0, tier_z1 - tier_t);
color("#b49be0", 0.9) tier();
if (show == "boards") { halmet(); oled(); seg(); }
sensor();
