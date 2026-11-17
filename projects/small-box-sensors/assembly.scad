// Assembly view, not a print: the carrier, two boards, connector and vent in the box. assembly.py renders and checks it.
// Stand-in sizes marked "guess" are not from a drawing; README lists every source.
include <model.scad>
part = "assembly";
variant = "env";     // env: BME688 with a vent | imu: ICM-20948, no vent
show = "carrier";    // one component per run, or "clash"

/* [Boards: Adafruit board files] */
board_l = 25.4;
board_w = 17.78;
pcb_t = 1.6;         // guess
part_h = 3.0;        // tallest part above the board, from the 4.6 overall on the product page
jst = [4.3, 6, 3];   // JST-SH socket on the board, at each short edge (guess)
plug_out = 4;        // Qwiic plug past the board edge (guess)
loop_out = 10;       // Qwiic cable's bend past the board edge (guess)

/* [SP13 panel socket: Weipu SP1312 drawing unless marked] */
sp_x = -7;           // along the connector wall from its centre
sp_z = 9.5;          // above the inside floor: mid-way up the plain wall
sp_hole = 13;
sp_flange_d = 19.5;
sp_flange_t = 3;     // guess
sp_nut_af = 17;      // guess
sp_nut_t = 3;        // guess
sp_rear = 13;        // body and solder cups inside the wall face (guess from the 19.2 overall)
sp_rear_d = 11;      // guess

/* [Vent: Gore XS M6 x 0.75 drawing unless marked] */
vent_x = 12;
vent_z = 11;
vent_hole = 6.2;
vent_head_d = 11.2;
vent_head_h = 4.5;
vent_thread = 7;
vent_nut_af = 10;
vent_nut_t = 2.5;    // guess

/* [Screws] */
stack_screw_l = 20;  // M2.5 x 20
m25_nut_af = 5;
m25_nut_t = 2;
boss_head_d = 5.6;   // M3 pan head self-tapper (guess)
boss_head_h = 2.2;

wall_y = in_w/2;                         // inside face of the connector wall
z_plate = boss_h;                        // carrier underside, on the bosses
z_lo = z_plate + plate_t + post_h;       // lower board underside
z_hi = z_lo + pcb_t + spacer_h;          // upper board underside
holes = concat([["y+", sp_x, sp_z, sp_hole]], variant == "env" ? [["y+", vent_x, vent_z, vent_hole]] : []);

module hexnut(af, t) { cylinder(d = af / cos(30), h = t, $fn = 6); }

module board(z) {
    translate([0, plate_y, z]) {
        difference() {
            translate([-board_l/2, -board_w/2, 0]) cube([board_l, board_w, pcb_t]);
            for (sx = [-1, 1], sy = [-1, 1]) translate([sx*hole_dx/2, sy*hole_dy/2, -1]) cylinder(d = 2.5, h = pcb_t + 2);
        }
        for (sx = [-1, 1]) translate([sx*(board_l/2 - jst[0]/2) - jst[0]/2, -jst[1]/2, pcb_t]) cube(jst);
        translate([-2, -2, pcb_t]) cube([4, 4, 1.2]);     // the chip
    }
}

module qwiic() {     // plugs at the +x end of both boards and the cable's bend between them
    for (z = [z_lo, z_hi]) translate([board_l/2, plate_y - 2.5, z + pcb_t]) cube([plug_out, 5, 3]);
    translate([board_l/2 + plug_out, plate_y - 2, z_lo + pcb_t + 0.5]) cube([loop_out - plug_out, 4, z_hi - z_lo + 2]);
}

module screws_stack() {
    for (p = posts) translate([p[0], p[1], z_plate]) {
        translate([0, 0, head_h - 2]) cylinder(d = 4.5, h = 2);                    // pan head, mostly below the plate
        translate([0, 0, head_h]) cylinder(d = 2.4, h = stack_screw_l);
        translate([0, 0, z_hi - z_plate + pcb_t]) difference() { hexnut(m25_nut_af, m25_nut_t); translate([0, 0, -1]) cylinder(d = 2.45, h = 4); }
    }
}

module screws_boss() {
    for (sx = [-1, 1]) translate([sx*boss_pitch/2, 0, 0]) {
        translate([0, 0, z_plate + plate_t]) cylinder(d = boss_head_d, h = boss_head_h);
        translate([0, 0, boss_h + 0.01]) cylinder(d = 2.4, h = plate_t);
    }
}

module sp13() {
    translate([sp_x, wall_y, sp_z]) rotate([-90, 0, 0]) {
        translate([0, 0, 0.01]) cylinder(d = sp_hole - 0.1, h = box_wall - 0.02);
        translate([0, 0, box_wall]) cylinder(d = sp_flange_d, h = sp_flange_t);            // outside
        translate([0, 0, box_wall + sp_flange_t]) cylinder(d = 13, h = 8);
        translate([0, 0, -sp_nut_t]) hexnut(sp_nut_af, sp_nut_t - 0.01);         // inside, flats toward the floor and the gasket band
        translate([0, 0, -sp_rear]) cylinder(d = sp_rear_d, h = sp_rear);
    }
}

module vent() {
    translate([vent_x, wall_y, vent_z]) rotate([-90, 0, 0]) {
        translate([0, 0, box_wall]) cylinder(d = vent_head_d, h = vent_head_h);
        translate([0, 0, box_wall - vent_thread]) cylinder(d = vent_hole - 0.2, h = vent_thread - 0.01);
        translate([0, 0, -vent_nut_t]) rotate(30) difference() { hexnut(vent_nut_af, vent_nut_t - 0.01); translate([0, 0, -1]) cylinder(d = 6.1, h = 5); }
    }
}

names = concat(["box", "lid", "carrier", "spacer", "board_lo", "board_hi", "screws_stack", "screws_boss", "sp13", "qwiic"],
               variant == "env" ? ["vent"] : []);

module comp(n) {
    if (n == "box") box_body(holes);
    if (n == "lid") box_lid();
    if (n == "carrier") translate([0, 0, z_plate]) carrier();
    if (n == "spacer") translate([0, plate_y, z_lo + pcb_t]) spacer();
    if (n == "board_lo") board(z_lo);
    if (n == "board_hi") board(z_hi);
    if (n == "screws_stack") screws_stack();
    if (n == "screws_boss") screws_boss();
    if (n == "sp13") sp13();
    if (n == "qwiic") qwiic();
    if (n == "vent") vent();
}

// Every pair's overlap, in one solid. The 1 mm marker cube keeps the export from being empty.
module clash() {
    translate([200, 0, 0]) cube(1);
    for (i = [0 : len(names) - 2], j = [i + 1 : len(names) - 1]) intersection() { comp(names[i]); comp(names[j]); }
}

if (show == "clash") clash(); else comp(show);
