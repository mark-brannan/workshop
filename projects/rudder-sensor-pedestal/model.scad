// Pedestal for pypilot's rudder sensor, low in the lazarette on starboard.
// Prototype: every size is a guess (README). Prints as modelled, base down.

/* [Mount] */
base_w = 90;        // footprint, screwed to whatever is fixed down there
base_d = 70;
base_t = 5;
screw_d = 5.0;      // #10 / M4.5 wood screw, loose
screw_inset = 10;

/* [Column] */
col_od = 40;
col_wall = 3;
col_h = 80;         // mount surface to the plate's underside: sets the sensor at quadrant height (guess)
slot_w = 10;        // lead exit at the column's foot

/* [Sensor seat] */
sensor_w = 50;      // sensor body footprint (guess; not on the store page)
sensor_d = 35;
sensor_h = 22;
sensor_hole_d = 4.8;    // M4, with the K2's undersize allowance
sensor_hole_pitch = 40;
lead_hole_d = 10;
rim = 4;
plate_t = 5;
lip_h = 2;

/* [View] */
view = "print";     // print | assembly
rudder = 0;         // assembly only: rudder angle, degrees
rod_len = 340;      // assembly only: equals stock-to-sensor distance (guess, 300 to 420)
arm_len = 100;      // assembly only: both arms

/* [Hidden] */
$fn = 72;
eps = 0.01;
plate_w = sensor_w + 2 * rim;
plate_d = sensor_d + 2 * rim;
flare = (plate_w - col_od) / 2;   // 45 degree flare, self-supporting
top_z = base_t + col_h + plate_t;

module rrect(w, d, h, r = 4) {
    linear_extrude(h) offset(r) square([w - 2 * r, d - 2 * r], center = true);
}

module base() {
    difference() {
        rrect(base_w, base_d, base_t, 6);
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * (base_w / 2 - screw_inset), sy * (base_d / 2 - screw_inset), -eps]) {
                cylinder(d = screw_d, h = base_t + 2 * eps);
                translate([0, 0, base_t - 2.5]) cylinder(d1 = screw_d, d2 = screw_d + 5, h = 2.5 + 2 * eps);
            }
    }
}

module column_solid() {
    translate([0, 0, base_t - eps]) cylinder(d = col_od, h = col_h - flare + eps);
    hull() {
        translate([0, 0, base_t + col_h - flare]) cylinder(d = col_od, h = eps);
        translate([0, 0, base_t + col_h]) rrect(plate_w, plate_d, plate_t);
    }
}

module bore() {
    id = col_od - 2 * col_wall;
    translate([0, 0, base_t]) cylinder(d = id, h = col_h - flare - id / 2);
    // closes at 45 degrees, so the plate prints without support
    translate([0, 0, base_t + col_h - flare - id / 2 - eps]) cylinder(d1 = id, d2 = 0, h = id / 2);
}

module lead_slot() {
    // pointed top: no bridge over the exit
    translate([col_od / 2 - col_wall - 1, 0, base_t])
        rotate([0, 90, 0]) linear_extrude(col_wall + 2)
            polygon([[0, -slot_w / 2], [-14, -slot_w / 2], [-14 - slot_w / 2, 0], [-14, slot_w / 2], [0, slot_w / 2]]);
}

module pedestal() {
    difference() {
        union() {
            base();
            column_solid();
            // lip that locates the sensor body
            translate([0, 0, top_z - eps]) difference() {
                rrect(plate_w, plate_d, lip_h + eps);
                translate([0, 0, -eps]) rrect(sensor_w + 0.6, sensor_d + 0.6, lip_h + 3 * eps, 2);
            }
        }
        bore();
        lead_slot();
        translate([0, 0, base_t]) cylinder(d = lead_hole_d, h = col_h + plate_t + lip_h + 1);
        for (sx = [-1, 1])
            translate([sx * sensor_hole_pitch / 2, 0, base_t + col_h - 8])
                cylinder(d = sensor_hole_d, h = plate_t + lip_h + 9);
    }
}

// Not printed: the sensor, its arm, the rod and the quadrant's stud, to show the parallelogram.
// Stock lies along -Y at rod_len; both arms point +X (aft) with the rudder centred.
module assembly() {
    pedestal();
    shaft_z = top_z + sensor_h;
    arm_z = shaft_z + 6;
    dir = [cos(rudder), sin(rudder), 0];
    stock = [0, -rod_len, 0];
    color("orange", 0.8) translate([0, 0, top_z]) rrect(sensor_w, sensor_d, sensor_h, 3);
    color("dimgray") {
        translate([0, 0, shaft_z]) cylinder(d = 6, h = 9);
        rotate([0, 0, rudder]) translate([0, -3, arm_z]) cube([arm_len, 6, 3]);
        translate(dir * arm_len + [0, 0, arm_z + 1.5]) sphere(d = 7);
    }
    color("silver") hull() {
        translate(dir * arm_len + [0, 0, arm_z + 1.5]) sphere(d = 3);
        translate(stock + dir * arm_len + [0, 0, arm_z + 1.5]) sphere(d = 3);
    }
    translate(stock) rotate([0, 0, rudder]) {
        color("firebrick", 0.6) translate([0, -10, arm_z - 30]) cube([arm_len + 30, 20, 12]);
        color("orange", 0.8) translate([arm_len - 12, -12, arm_z - 34]) cube([24, 24, 34]);
        color("dimgray") translate([arm_len, 0, arm_z - 1]) sphere(d = 7);
    }
    color("gray") translate(stock) cylinder(d = 60, h = arm_z + 80);
}

if (view == "assembly") assembly(); else pedestal();
