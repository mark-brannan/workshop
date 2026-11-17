// Pod for one Adafruit BME688 board (25.4 x 17.78, holes 20.32 x 12.7) in the 63 x 58 x 35 box.
// It lifts the board to just under a membrane vent in the lid and walls it in, so the sensor
// shares a few cm3 of air with the vent instead of the whole box.
// Screws to the box's two floor bosses; four M2.5 x 20 come up through the block and the board, nuts on top.
// Print as shown: tab on the bed, rim up, no supports. The block is solid in the model; sparse infill does the lightening.
include <../../small-box-sensors/box.scad>
part = "pod";

/* [Tab on the floor bosses] */
plate_l = 55;        // x; inside the 58 floor, clear of the short walls
tab_w = 10;          // y, on the box centre line
plate_t = 2;
corner_r = 2;
slot_w = 3.4;        // M3 self-tapper clearance
slot_play = 4;       // each way along x; covers the 39 to 47 guess for the boss pitch

/* [Board] */
board_l = 25.4;      // Adafruit board file
board_w = 17.78;
hole_dx = 20.32;
hole_dy = 12.7;
plate_y = -5;        // board centre, off the box centre, away from the connector wall

/* [Block and rim] */
seat_h = 17;         // board's underside above the pod's underside; puts the chip about 1.5 under the vent's thread
pad_h = 1;           // seat pads stand this far above the block top, clear of the board's underside
pad_d = 5;
rim_fit = 0.6;       // board edge to rim, each side
rim_t = 1.2;
lid_gap = 1.5;       // rim top to the lid's underside; the lid numbers are photo estimates
notch_w = 7;         // gap in the rim at one short end, for the Qwiic plug
screw_d = 2.9;       // M2.5 clearance, printed
head_d = 5;          // M2.5 pan head, in a pocket under the block
head_h = 1.2;

/* [Hidden] */
$fn = 48;
blk_l = board_l + 2*(rim_fit + rim_t);
blk_w = board_w + 2*(rim_fit + rim_t);
pod_h = ceil_z - lid_gap - boss_h;       // 24: the pod's underside sits on the bosses
posts = [for (sx = [-1, 1], sy = [-1, 1]) [sx*hole_dx/2, plate_y + sy*hole_dy/2]];

module rrect(l, w, r) { hull() for (sx = [-1, 1], sy = [-1, 1]) translate([sx*(l/2 - r), sy*(w/2 - r)]) circle(r = r); }

module pod() {
    difference() {
        union() {
            linear_extrude(plate_t) rrect(plate_l, tab_w, corner_r);
            translate([0, plate_y]) linear_extrude(pod_h) rrect(blk_l, blk_w, corner_r);
        }
        translate([0, plate_y, seat_h - pad_h]) linear_extrude(pod_h) rrect(blk_l - 2*rim_t, blk_w - 2*rim_t, corner_r - rim_t/2);   // the chamber
        translate([blk_l/2 - rim_t - 1, plate_y - notch_w/2, seat_h]) cube([rim_t + 2, notch_w, pod_h]);                          // plug notch
        for (sx = [-1, 1]) translate([sx*boss_pitch/2, 0, -1]) linear_extrude(plate_t + 2)
            hull() for (d = [-slot_play, slot_play]) translate([d, 0]) circle(d = slot_w);
        for (p = posts) translate([p[0], p[1], -1]) {
            cylinder(d = screw_d, h = pod_h);
            cylinder(d = head_d, h = head_h + 1);
        }
    }
    for (p = posts) translate([p[0], p[1], seat_h - pad_h - 0.01]) difference() {      // seat pads
        cylinder(d = pad_d, h = pad_h + 0.01);
        translate([0, 0, -1]) cylinder(d = screw_d, h = pad_h + 2);
    }
}

if (part == "pod") pod();
