// Assembly view, not a print: the pod, the board, the SP13 socket and the lid vent in the box. assembly.py renders and checks it.
// Stand-in sizes marked "guess" are not from a drawing; README lists every source.
include <model.scad>
part = "assembly";
show = "pod";        // one component per run, or "clash"

/* [Board: Adafruit board file unless marked] */
pcb_t = 1.6;         // guess
chip_h = 0.93;       // BME688 package height, Bosch datasheet
chip_dx = 0;         // chip centre off the board centre (guess: centred)
chip_dy = 0;
jst = [4.3, 6, 3];   // JST-SH socket on the board, at each short edge (guess)
plug_out = 4;        // Qwiic plug past the board edge (guess)
lead_out = 6;        // the pigtail's wires before they turn toward the socket (guess)

/* [SP13 panel socket: Weipu SP1312 drawing unless marked] */
sp_x = 0;            // along the connector wall from its centre
sp_z = 9.5;          // above the inside floor: mid-way up the plain wall
sp_hole = 13;
sp_flange_d = 19.5;
sp_flange_t = 3;     // guess
sp_nut_af = 17;      // guess
sp_nut_t = 3;        // guess
sp_rear = 13;        // body and solder cups inside the wall face (guess from the 19.2 overall)
sp_rear_d = 11;      // guess

/* [Vent in the lid: Gore XS M6 x 0.75 drawing unless marked] */
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
z_pod = boss_h;                          // pod underside, on the bosses
z_b = z_pod + seat_h;                    // board underside
z_chip = z_b + pcb_t + chip_h;           // chip top
lid_top_z = rim_z + lid_h;               // lid's outer face
vent_x = chip_dx;                        // the vent sits over the chip
vent_y = plate_y + chip_dy;
vent_tip_z = lid_top_z - vent_thread;    // inner end of the vent's thread
holes = [["y+", sp_x, sp_z, sp_hole]];

module hexnut(af, t) { cylinder(d = af / cos(30), h = t, $fn = 6); }

module board() {
    translate([0, plate_y, z_b]) {
        difference() {
            translate([-board_l/2, -board_w/2, 0]) cube([board_l, board_w, pcb_t]);
            for (sx = [-1, 1], sy = [-1, 1]) translate([sx*hole_dx/2, sy*hole_dy/2, -1]) cylinder(d = 2.5, h = pcb_t + 2);
        }
        for (sx = [-1, 1]) translate([sx*(board_l/2 - jst[0]/2) - jst[0]/2, -jst[1]/2, pcb_t]) cube(jst);
        translate([chip_dx - 1.5, chip_dy - 1.5, pcb_t]) cube([3, 3, chip_h]);
    }
}

module pigtail() {   // Qwiic plug at the +x end, through the rim's notch, and the start of its four wires
    translate([board_l/2, plate_y - 2.5, z_b + pcb_t]) cube([plug_out, 5, 3]);
    translate([board_l/2 + plug_out, plate_y - 2, z_b + pcb_t + 0.5]) cube([lead_out, 4, 2]);
}

module screws_stack() {
    for (p = posts) translate([p[0], p[1], z_pod]) {
        translate([0, 0, head_h - 2]) cylinder(d = 4.5, h = 2);                    // pan head, mostly below the pod
        translate([0, 0, head_h]) cylinder(d = 2.4, h = stack_screw_l);
        translate([0, 0, seat_h + pcb_t]) difference() { hexnut(m25_nut_af, m25_nut_t); translate([0, 0, -1]) cylinder(d = 2.45, h = 4); }
    }
}

module screws_boss() {
    for (sx = [-1, 1]) translate([sx*boss_pitch/2, 0, 0]) {
        translate([0, 0, z_pod + plate_t]) cylinder(d = boss_head_d, h = boss_head_h);
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

module lid() {
    difference() {
        box_lid();
        translate([vent_x, vent_y, ceil_z - 1]) cylinder(d = vent_hole, h = lid_top + 2);
    }
}

module vent() {      // head outside on the lid, thread and nut inside, over the chip
    translate([vent_x, vent_y, 0]) {
        translate([0, 0, lid_top_z]) cylinder(d = vent_head_d, h = vent_head_h);
        translate([0, 0, vent_tip_z]) cylinder(d = vent_hole - 0.2, h = vent_thread - 0.01);
        translate([0, 0, ceil_z - vent_nut_t]) rotate(30) difference() { hexnut(vent_nut_af, vent_nut_t - 0.01); translate([0, 0, -1]) cylinder(d = 6.1, h = 5); }
    }
}

names = ["box", "lid", "pod", "board", "screws_stack", "screws_boss", "sp13", "pigtail", "vent"];

module comp(n) {
    if (n == "box") box_body(holes);
    if (n == "lid") lid();
    if (n == "pod") translate([0, 0, z_pod]) pod();
    if (n == "board") board();
    if (n == "screws_stack") screws_stack();
    if (n == "screws_boss") screws_boss();
    if (n == "sp13") sp13();
    if (n == "pigtail") pigtail();
    if (n == "vent") vent();
}

// Every pair's overlap, in one solid. The 1 mm marker cube keeps the export from being empty.
module clash() {
    translate([200, 0, 0]) cube(1);
    for (i = [0 : len(names) - 2], j = [i + 1 : len(names) - 1]) intersection() { comp(names[i]); comp(names[j]); }
}

if (show == "clash") clash(); else comp(show);
