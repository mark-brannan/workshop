// Pedestal for the home-made rudder angle sensor (../rudder-angle-sensor), low in the lazarette on starboard.
// Prototype: every size is a guess (README). Prints as modelled, base down.
// The seat's footprint, holes and turn are read from the sensor's model, their one home.
use <../rudder-angle-sensor/model.scad>

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
lead_hole_d = 10;
rim = 4;
plate_t = 5;        // plastic over each nut
lip_h = 2;
seat_fit = 0.6;     // lip over the sensor's foot, on the width (guess)

/* [Nut traps: M4 hex nut, slid in from the plate's two ends] */
nut_af = 7.0;       // across flats, ISO 4032 nominal (guess for the nuts on hand)
nut_t = 3.2;
nut_fit = 0.4;      // slot over the nut, on width and on height (guess)
screw_below = 8;    // screw hole's depth under the plate: takes an M4 x 30 with 2 to spare
layer_h = 0.2;      // the two bridge layers over each slot

/* [View] */
view = "print";     // print | assembly
rudder = 0;         // assembly only: rudder angle, degrees
rod_len = 340;      // assembly only: equals stock-to-sensor distance (guess, 300 to 420)
arm_len = 100;      // assembly only: both arms; one of the sensor's stud radii

/* [Hidden] */
$fn = 72;
eps = 0.01;
sensor_w = sensor_foot()[0];            // along the sensor's two flange holes
sensor_d = sensor_foot()[1];
sensor_hole_pitch = sensor_flange()[0];
sensor_hole_d = sensor_flange()[1];
sensor_cup_h = sensor_heights()[0];
sensor_arm_top = sensor_heights()[1];
seat_turn = -sensor_arm_zero();         // sensor frame to this one: its arm's centre lands on +X
plate_w = sensor_w + 2 * rim;
plate_d = sensor_d + 2 * rim;
plate_r = 4;
flare = norm([plate_w / 2 - plate_r, plate_d / 2 - plate_r]) + plate_r - col_od / 2;   // 45 degrees out to the plate's corners
under_z = base_t + col_h;               // plate's underside: the nuts bear here
top_z = under_z + plate_t;
trap_w = nut_af + nut_fit;
trap_h = nut_t + nut_fit;
assert(len([for (r = sensor_arm_radii()) if (r == arm_len) r]) == 1, "arm_len is not one of the sensor's stud radii");
assert(sensor_hole_pitch / 2 - trap_w / 2 / cos(30) > lead_hole_d / 2 + 2, "a nut slot reaches the lead hole");

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
        translate([0, 0, under_z]) rotate([0, 0, seat_turn]) rrect(plate_w, plate_d, plate_t, plate_r);
    }
}

// One flange screw, in the sensor's frame (holes on x): a hole through the plate, a slot for the nut run out to the
// plate's end, and the screw's run-out below. The slot's ceiling is the nut's seat: a 7.4 bridge from wall to wall,
// then two layers that close the opening down to the hole, laid at 90 degrees to each other.
module nut_trap(s) {
    x = s * sensor_hole_pitch / 2;
    translate([x, 0, under_z + 2 * layer_h - eps]) cylinder(d = sensor_hole_d, h = plate_t + lip_h + 1);
    translate([x, 0, under_z + layer_h - eps]) linear_extrude(layer_h + 2 * eps) square(sensor_hole_d, center = true);
    translate([x, 0, under_z - eps]) linear_extrude(layer_h + 2 * eps) square([sensor_hole_d, trap_w], center = true);
    translate([0, 0, under_z - trap_h]) linear_extrude(trap_h) hull() for (k = [0, 1])
        translate([x + s * k * plate_w, 0]) circle(d = trap_w / cos(30), $fn = 6);
    translate([x, 0, under_z - screw_below]) cylinder(d = sensor_hole_d, h = screw_below - trap_h + eps);
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
            translate([0, 0, top_z - eps]) rotate([0, 0, seat_turn]) difference() {
                rrect(plate_w, plate_d, lip_h + eps, plate_r);
                translate([0, 0, -eps]) rrect(sensor_w + seat_fit, sensor_d + seat_fit, lip_h + 3 * eps, 2);
            }
        }
        bore();
        lead_slot();
        translate([0, 0, base_t]) cylinder(d = lead_hole_d, h = col_h + plate_t + lip_h + 1);
        rotate([0, 0, seat_turn]) for (s = [-1, 1]) nut_trap(s);
    }
}

// Not printed: the sensor (its own model's parts), the rod and the quadrant's stud, to show the parallelogram.
// Stock lies along -Y at rod_len; both arms point +X (aft) with the rudder centred.
module assembly() {
    pedestal();
    flange_z = top_z + sensor_cup_h;        // the sensor model's z = 0
    arm_z = flange_z + sensor_arm_top;      // arm's top face
    ball_z = arm_z + 6;
    dir = [cos(rudder), sin(rudder), 0];
    stock = [0, -rod_len, 0];
    translate([0, 0, flange_z]) rotate([0, 0, seat_turn]) {
        color("orange", 0.8) body();
        color("steelblue", 0.8) cup();
        color("dimgray") for (s = [-1, 1]) translate([s * sensor_hole_pitch / 2, 0, 6]) cylinder(d = sensor_m4_head(), h = 4);
    }
    color("tomato") translate([0, 0, arm_z]) rotate([0, 0, rudder]) rotate([180, 0, 0]) arm();
    color("dimgray") translate(dir * arm_len + [0, 0, ball_z]) sphere(d = 7);
    color("silver") hull() {
        translate(dir * arm_len + [0, 0, ball_z]) sphere(d = 3);
        translate(stock + dir * arm_len + [0, 0, ball_z]) sphere(d = 3);
    }
    translate(stock) rotate([0, 0, rudder]) {
        color("firebrick", 0.6) translate([0, -10, ball_z - 32]) cube([arm_len + 30, 20, 12]);
        color("orange", 0.8) translate([arm_len - 12, -12, ball_z - 36]) cube([24, 24, 34]);
        color("dimgray") translate([arm_len, 0, ball_z]) sphere(d = 7);
    }
    color("gray") translate(stock) cylinder(d = 60, h = ball_z + 80);
}

if (view == "assembly") assembly(); else pedestal();
