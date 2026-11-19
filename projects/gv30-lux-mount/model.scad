// GV30 lux add-on: a split ring between the clamp's stub shoulder and the GV30, with an arm carrying a
// lux sensor. The split runs down the arm's middle, so it opens around the coax and the cord can lie in it.
// A cover drops into a recess over the arm, flush with the ring's top, and is thinned to a skin over the
// sensor: the diffuser.
// Origin: antenna axis on Z, z = 0 on the stub's shoulder.
// Print: body as shown; cover upside down (skin on the bed).

part = "assembly";   // [body, cover, assembly]

/* [Ring] */
od = 32;            // the shoulder it sits on, off ref/clamp-upper.stl
id = 26;            // over the 1"-14 stub (OD 25.2)
h = 8;              // costs this much thread engagement (GV30 thread depth not measured)
split = 1.5;        // gap

/* [Arm and head] */
reach = 50;         // antenna axis to sensor centre
head_d = 36;

/* [Sensor: VEML7700, Adafruit 4162, 25.4 x 17.8 (vendor; not measured)] */
board_l = 26;
board_w = 18.5;
pocket = 3;         // below the cover: board 1.6 and its parts

/* [Cover] */
cover_t = 2;
skin = 0.6;         // white ASA over the sensor, 3 layers at 0.2
fit = 0.2;          // cover to recess, each side

$fn = 96;
e = 0.01;

module outline() hull() { circle(d = od); translate([reach, 0]) circle(d = head_d); }

// the arm's part of the outline: everything outside the ring
module arm_outline(grow = 0, spill = 0) intersection() {
  difference() { offset(delta = grow + spill) outline(); circle(d = od - 2 * grow); }
  translate([1, -head_d]) square([reach + head_d, 2 * head_d]);   // keeps off the ring's tangent points
}

module body() {
  difference() {
    linear_extrude(h) outline();
    translate([0, 0, -e]) cylinder(d = id, h = h + 2 * e);
    translate([0, -split / 2, -e]) cube([reach + head_d, split, h + 2 * e]);
    translate([0, 0, h - cover_t]) linear_extrude(cover_t + e) arm_outline(spill = 1);
    translate([reach - board_l / 2, -board_w / 2, h - cover_t - pocket]) cube([board_l, board_w, pocket + e]);
  }
}

module cover() {
  // z = 0 is the underside
  difference() {
    linear_extrude(cover_t) arm_outline(-fit);
    translate([reach - board_l / 2, -board_w / 2, -e]) cube([board_l, board_w, cover_t - skin + e]);
  }
}

module assembly() {
  color("lightgrey") body();
  color("white") translate([0, 0, h - cover_t]) cover();
}

if (part == "body") body();
else if (part == "cover") cover();
else assembly();
