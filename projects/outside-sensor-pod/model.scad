// Outside sensor pod: a louvred shield around bare, coated I2C sensor boards (Adafruit 25.4 x 17.78 outline).
// Three printed parts on three M4 rods: louvre (x5), cap, base. Louvre and cap print upside down as shown here
// (in-use top face on the bed, skirt and spacer tubes rising); the base prints as used. No supports.
part = "louvre";     // louvre | cap | base

/* [Louvre] */
cav_r = 21;          // open centre: the sensor cavity
flat_r = 38;         // flat ring ends, 45 degree skirt starts
out_r = 50;
plate_t = 2;
drop = 14;           // skirt tip below the plate's top face, in use
pitch = 13;          // plate to plate; drop - pitch is the rain overlap
n_louvres = 5;

/* [Rods] */
post_r = 30;
post_d = 9;
rod_d = 4.5;         // M4 clearance, printed
post_a = [90, 210, 330];

/* [Cap] */
cap_t = 3;
win_ap = 12;         // light aperture for the lux sensor
win_flare = 18;      // aperture's mouth on the top face
win_d = 20.4;        // seat for a 20 mm disc of 3 mm clear acrylic, bedded from inside
collar_h = 3.5;
collar_wall = 2;

/* [Base] */
base_t = 5;
boss_h = 3;          // lifts the bottom louvre so its skirt clears the tongue
bridge_w = 14;
fin_t = 4;
fin_w = 22;
fin_h = 60;
tongue_l = 82;       // from the pod's axis to the tongue's end
tongue_w = 40;
slot_x = 66;         // two M5 slots: placeholder mount until the site is chosen
slot_dy = 20;
slot_w = 5.5;
slot_l = 10;
tie = [5, 2.5];      // zip-tie slots for the lead's strain relief

/* [Board bay: Adafruit LPS3X board file] */
hole_pitch = 20.32;  // the board's two holes, along its long edge
hole_inset = 2.54;   // hole line in from that edge
board_w = 17.78;
board_z = 40;        // board centre above the base's underside
standoff = 3;        // board's back off the fin: clears the address jumper and solder joints
screw_d = 2.9;       // M2.5 clearance, printed

/* [Hidden] */
$fn = 96;
hole_y = -(board_w/2 - hole_inset);

module rods(h) { for (a = post_a) rotate(a) translate([post_r, 0, -1]) cylinder(d = rod_d, h = h + 2, $fn = 32); }

module skirt_plate(r_in) {
    rotate_extrude() polygon([[r_in, 0], [flat_r, 0], [out_r, drop - plate_t], [out_r, drop], [flat_r, plate_t], [r_in, plate_t]]);
    for (a = post_a) rotate(a) translate([post_r, 0, 0]) cylinder(d = post_d, h = pitch, $fn = 48);
}

module louvre() { difference() { skirt_plate(cav_r); rods(drop); } }

module cap() {
    difference() {
        union() {
            skirt_plate(0);
            cylinder(r = flat_r, h = cap_t);
            cylinder(d = win_d + 2*collar_wall, h = cap_t + collar_h);
        }
        rods(drop);
        translate([0, 0, cap_t]) cylinder(d = win_d, h = collar_h + 1);
        translate([0, 0, -0.01]) cylinder(d1 = win_flare, d2 = win_ap, h = cap_t + 0.02);
    }
}

module base() {
    difference() {
        union() {
            linear_extrude(base_t) {
                difference() { circle(r = flat_r); circle(r = cav_r); }
                square([bridge_w, 2*cav_r + 2], center = true);
                hull() { translate([post_r, -tongue_w/2]) square([1, tongue_w]); for (sy = [-1, 1]) translate([tongue_l - 6, sy*(tongue_w/2 - 6)]) circle(r = 6); }
            }
            for (a = post_a) rotate(a) translate([post_r, 0, 0]) cylinder(d = post_d, h = base_t + boss_h, $fn = 48);
            translate([-fin_t/2, -fin_w/2, 0]) cube([fin_t, fin_w, base_t + fin_h]);
            for (sy = [-1, 1]) translate([0, sy*(fin_w/2 - 1) + 1, 0]) rotate([90, 0, 0])         // gussets
                linear_extrude(2) polygon([[-bridge_w/2, base_t], [bridge_w/2, base_t], [fin_t/2, base_t + 20], [-fin_t/2, base_t + 20]]);
            for (sz = [-1, 1]) translate([0, hole_y, board_z + sz*hole_pitch/2]) rotate([45, 0, 0])  // diamond standoffs
                cube([fin_t + 2*standoff, 5.5, 5.5], center = true);
        }
        rods(base_t + boss_h);
        for (sz = [-1, 1]) translate([0, hole_y, board_z + sz*hole_pitch/2]) rotate([0, 90, 0]) cylinder(d = screw_d, h = 30, center = true, $fn = 24);
        for (sy = [-1, 1]) translate([slot_x, sy*slot_dy/2, -1]) linear_extrude(base_t + 2)
            hull() for (sx = [-1, 1]) translate([sx*(slot_l - slot_w)/2, 0]) circle(d = slot_w, $fn = 32);
        for (sx = [-1, 1], sy = [-1, 1]) translate([sx*4.5, sy*16, base_t/2]) cube([tie[1], tie[0], base_t + 2], center = true);
    }
}

if (part == "louvre") louvre();
if (part == "cap") cap();
if (part == "base") base();
