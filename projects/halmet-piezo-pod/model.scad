// HALMET piezo pod: a plain box and a screwed lid on an engine-room bulkhead.
// Holds the XY-MOS trigger module on the floor (foam tape). The flanged 12 V buzzer screws to the
// lid's outside by its two ears, stacked over the module, open to the air; its leads pass through the lid.
// Origin: back face (against the bulkhead), centred. X across, Y up the bulkhead, Z out from it.
// Print the box floor down and the lid (part-lid.scad) outer face down, as modelled: no overhangs.
// The two cables (HALMET signal, boat 12 V) enter through a notch in the bottom wall, run out
// to the rim; the lid closes it. The box screws to the bulkhead through its floor.

/* [Parts] */
mod_l = 33.8;         // XY-MOS module, owner caliper
mod_w = 16.7;         // owner caliper
mod_h = 12;           // seller listings; not calipered
tape_t = 1;           // foam tape under the module
buzzer_d = 29;        // flanged buzzer on hand, round body; owner, approximate
buzzer_h = 15;        // overall; owner, approximate
ear_span = 47.4;      // ear tip to ear tip; owner, caliper
ear_pitch = 40;       // ear hole to ear hole; owner, by eye

/* [Box] */
in_w = 30;            // across
in_l = 56;            // up the bulkhead: room past the module's ends for wires and a screwdriver
wall = 2;
floor_t = 2.4;
corner_r = 3;         // outside vertical corners
top_clear = 5;        // module top to the lid: wires into the terminals

/* [Lid screws: M2.5 self-tapping] */
boss_d = 6.5;
pilot_d = 2.2;        // calibration pending
lid_hole_d = 3.2;     // M2.5 clearance, generous: printed holes come out small
lid_t = 2.4;

/* [Buzzer on the lid: two M3 self-tapping screws through its ears] */
ear_pilot_d = 2.5;    // M3 self-tapping; calibration pending
ear_boss_d = 7;
ear_boss_h = 3.5;     // under the lid, into the box; ends above the module top
lead_d = 8;           // lead hole under the buzzer's centre

/* [Cable notch, bottom wall] */
notch_w = 12;         // two cables side by side
notch_d = 7;          // down from the rim

/* [Bulkhead screws] */
mount_d = 4.5;        // #8 or M4 pan head, from inside the box
mount_y = 22;         // from centre, up and down, past the module's ends

/* [Hidden] */
$fn = 64;
eps = 0.01;
out_w = in_w + 2*wall;
out_l = in_l + 2*wall;
depth = floor_t + tape_t + mod_h + top_clear;  // floor to the lid's underside
boss_x = in_w/2 - boss_d/2 + 0.5;
boss_y = in_l/2 - boss_d/2 + 0.5;

module rrect(w, l, r) { offset(r = r) square([w - 2*r, l - 2*r], center = true); }

module box() {
    difference() {
        union() {
            difference() {
                linear_extrude(depth) rrect(out_w, out_l, corner_r);
                translate([0, 0, floor_t]) linear_extrude(depth) square([in_w, in_l], center = true);
            }
            for (sx = [-1, 1], sy = [-1, 1]) translate([sx*boss_x, sy*boss_y, 0]) cylinder(d = boss_d, h = depth);
        }
        for (sx = [-1, 1], sy = [-1, 1]) translate([sx*boss_x, sy*boss_y, floor_t]) cylinder(d = pilot_d, h = depth);
        for (sy = [-1, 1]) translate([0, sy*mount_y, -1]) cylinder(d = mount_d, h = floor_t + 2);
        translate([-notch_w/2, -out_l/2 - 1, depth - notch_d]) cube([notch_w, wall + 2, notch_d + 1]);
    }
}

module lid() {
    difference() {
        union() {
            linear_extrude(lid_t) rrect(out_w, out_l, corner_r);
            for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, lid_t - eps]) cylinder(d = ear_boss_d, h = ear_boss_h);
        }
        translate([0, 0, -1]) cylinder(d = lead_d, h = lid_t + 2);
        for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, -1]) cylinder(d = ear_pilot_d, h = lid_t + ear_boss_h + 2);
        for (sx = [-1, 1], sy = [-1, 1]) translate([sx*boss_x, sy*boss_y, -1]) cylinder(d = lid_hole_d, h = lid_t + 2);
    }
}

// Lid in place, flipped onto the box, for the assembly drawing.
module lid_on() { translate([0, 0, depth + lid_t]) mirror([0, 0, 1]) lid(); }

module standins() {
    color("seagreen") translate([-mod_w/2, -mod_l/2, floor_t + tape_t]) cube([mod_w, mod_l, mod_h]);
    color("dimgray") translate([0, 0, depth + lid_t]) {
        cylinder(d = buzzer_d, h = buzzer_h);
        linear_extrude(1.5) hull() for (sy = [-1, 1]) translate([0, sy*(ear_span/2 - 3.5)]) circle(r = 3.5);
    }
}

show = "box";  // [box, assembly]
if (show == "assembly") { color("orange") box(); standins(); color("gold", 0.5) lid_on(); }
else box();
