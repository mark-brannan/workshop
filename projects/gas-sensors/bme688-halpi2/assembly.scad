// Assembly view, not a print: the screen's body and cover, the board, the pigtail, the cable and the screws.
// assembly.py renders and checks it. Stand-in sizes marked "guess" are not from a drawing; README lists every source.
include <model.scad>
part = "assembly";
show = "body";       // one component per run, or "clash"

/* [Board: Adafruit board file unless marked] */
chip_h = 0.93;       // BME688 package height, Bosch datasheet
jst = [4.3, 6, 3];   // JST-SH socket on the board, at each short edge (guess)
plug_out = 4;        // Qwiic plug past the board edge (guess)
lead_out = 6;        // the pigtail's wires before they turn toward the cable (guess)

/* [Cable] */
cable_d = 4.5;       // 4-core (guess)

/* [Screws] */
cover_screw_l = 12;  // M3 x 12 self-tapper
cover_head_d = 5.6;  // pan head (guess)
cover_head_h = 2.2;
mount_head_d = 8;    // 4 mm wood screw, pan head (guess)
mount_head_h = 3;

z_b = plate_t + pad_h;                   // board underside

module hexnut(af, t) { cylinder(d = af / cos(30), h = t, $fn = 6); }

module board() {     // drawn long side along x, then stood up with its +x end down
    translate([0, board_y, z_b]) rotate(-90) {
        difference() {
            translate([-board_l/2, -board_w/2, 0]) cube([board_l, board_w, pcb_t]);
            for (sx = [-1, 1], sy = [-1, 1]) translate([sx*hole_dx/2, sy*hole_dy/2, -1]) cylinder(d = 2.5, h = pcb_t + 2);
        }
        for (sx = [-1, 1]) translate([sx*(board_l/2 - jst[0]/2) - jst[0]/2, -jst[1]/2, pcb_t]) cube(jst);
        translate([-1.5, -1.5, pcb_t]) cube([3, 3, chip_h]);
    }
}

module pigtail() {   // Qwiic plug in the lower socket and the start of its four wires
    translate([0, board_y, z_b]) rotate(-90) {
        translate([board_l/2, -2.5, pcb_t]) cube([plug_out, 5, 3]);
        translate([board_l/2 + plug_out, -2, pcb_t + 0.5]) cube([lead_out, 4, 2]);
    }
}

module cable() {     // in the floor notch, ending just inside
    translate([0, 2, notch_z - notch_w/2 + cable_d/2]) rotate([90, 0, 0]) cylinder(d = cable_d, h = 2 + floor_t + 12);
}

module screws_cover() {
    for (p = pilots) translate([p[0], p[1], body_h + cover_t]) {
        cylinder(d = cover_head_d, h = cover_head_h);
        translate([0, 0, -cover_screw_l]) cylinder(d = 2.4, h = cover_screw_l);
    }
}

module screws_mount() {
    for (y = [mount_lo_y, mount_hi_y]) translate([0, y, plate_t]) {
        cylinder(d = mount_head_d, h = mount_head_h);
        translate([0, 0, -plate_t - 10]) cylinder(d = 3.9, h = plate_t + 10);
    }
}

names = ["body", "cover", "board", "pigtail", "cable", "screws_cover", "screws_mount"];

module comp(n) {
    if (n == "body") body();
    if (n == "cover") translate([0, 0, body_h + cover_t]) mirror([0, 0, 1]) cover();
    if (n == "board") board();
    if (n == "pigtail") pigtail();
    if (n == "cable") cable();
    if (n == "screws_cover") screws_cover();
    if (n == "screws_mount") screws_mount();
}

// Every pair's overlap, in one solid. The 1 mm marker cube keeps the export from being empty.
module clash() {
    translate([200, 0, 0]) cube(1);
    for (i = [0 : len(names) - 2], j = [i + 1 : len(names) - 1]) intersection() { comp(names[i]); comp(names[j]); }
}

if (show == "clash") clash(); else comp(show);
