// GV30 antenna clamp, top half, with a bolt-on arm for an upward-facing lux sensor.
// The clamp is the owner's own print (ref/clamp-upper.stl, from "antenna mount for oversized tubing.3mf"),
// changed three ways: the bore is filled and re-cut narrower, a pad with two M3 heat-set inserts sits
// on its +X shoulder, and a cable port runs from the pad's top down into the bore.
// The arm (part-arm.scad) screws to the pad; its lead lies in a press-in channel on the underside, so a
// broken arm comes off without touching the coax.
// Origin: tube axis on X, clamp split plane at z = 0, antenna axis on Z. Both parts print upright as shown,
// except the arm, which prints upside down (its top face on the bed).

part = "clamp";      // [clamp, arm, assembly]

/* [Clamp: from the owner's file, measured off the mesh] */
tube_r = 20;         // cradle radius (Ø40 tube)
old_bore_d = 19;     // bore in the owner's file
thread_top = 44;     // top of the 1"-14 stub
saddle_top = 27.1;   // top line of the saddle, along X

/* [Changes to the clamp] */
bore_d = 12;         // two coax at 2.7 + one thin patch lead, passed bare; FME fitted after
pad_x0 = 22;         // pad's inboard face: must clear the GV30's base skirt (radius not measured)
pad_x1 = 37;         // the clamp ends at 38.1
pad_w = 22;          // across Y
pad_top = 36;        // arm seats here
insert_d = 4.0;      // M3 heat-set insert hole
insert_h = 6;
screw_x = 33;        // the two M3 screws, at (screw_x, ±screw_dy)
screw_dy = 7;
port_d = 6;          // cable port, pad top to bore
port_x = 27;         // port axis at pad top
port_z_bore = 23;    // port axis where it meets the bore wall (cradle top is at z = 20)

/* [Arm] */
reach = 95;          // antenna axis to sensor centre
arm_t = 8;           // arm thickness
arm_w = 14;
head_d = 32;
board_l = 26;        // VEML7700 board, Adafruit 4162: 25.4 x 17.8 (vendor; not measured), plus clearance
board_w = 18.5;
skin = 0.6;          // white ASA over the sensor: the diffuser and the weather seal, 3 layers at 0.2
lead_w = 5.5;        // channel for the patch lead (not measured)
lead_throat = 4.5;   // the lead presses in past this

/* [Hardware] */
screw_d = 3.4;
cbore_d = 6.5;
cbore_h = 3;

$fn = 64;
e = 0.01;

module owner_clamp() translate([0, 0, 22]) import("ref/clamp-upper.stl", convexity = 6);

port_tilt = atan2(pad_top - port_z_bore, port_x - bore_d / 2);   // above horizontal

module port() {
  // from just above the pad top, down and inboard, ending inside the bore
  translate([port_x, 0, pad_top]) rotate([0, 270 - port_tilt, 0]) translate([0, 0, -3])
    cylinder(d = port_d, h = port_x / cos(port_tilt) + 3);
}

module clamp() {
  difference() {
    union() {
      owner_clamp();
      translate([0, 0, tube_r - 3]) cylinder(d = old_bore_d + 0.6, h = thread_top - tube_r + 3);
      translate([pad_x0, -pad_w / 2, tube_r]) cube([pad_x1 - pad_x0, pad_w, pad_top - tube_r]);
    }
    rotate([0, 90, 0]) cylinder(r = tube_r, h = 200, center = true);
    translate([0, 0, -1]) cylinder(d = bore_d, h = thread_top + 2);
    for (s = [-1, 1]) translate([screw_x, s * screw_dy, pad_top - insert_h]) cylinder(d = insert_d, h = insert_h + e);
    port();
  }
}

module lead_channel(x0, x1) {
  // open on the arm's underside (z = 0 here); lips narrow the mouth so the lead presses in
  translate([x0, -lead_w / 2, -e]) cube([x1 - x0, lead_w, arm_t - 2.5]);
}

module lips(x0, x1) {
  lip = (lead_w - lead_throat) / 2;
  for (s = [-1, 1]) translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(x1 - x0)
    polygon([[s * lead_w / 2, 0], [s * lead_throat / 2, 0], [s * lead_w / 2, lip]]);
}

module arm() {
  // z = 0 is the arm's underside, seated on the pad top
  difference() {
    union() {
      translate([pad_x0, -pad_w / 2, 0]) cube([pad_x1 - pad_x0, pad_w, arm_t]);
      translate([pad_x1 - e, -arm_w / 2, 0]) cube([reach - pad_x1, arm_w, arm_t]);
      translate([reach, 0, 0]) cylinder(d = head_d, h = arm_t);
    }
    for (s = [-1, 1]) translate([screw_x, s * screw_dy, -e]) {
      cylinder(d = screw_d, h = arm_t + 2 * e);
      translate([0, 0, arm_t - cbore_h]) cylinder(d = cbore_d, h = cbore_h + 1);
    }
    translate([reach - board_l / 2, -board_w / 2, -e]) cube([board_l, board_w, arm_t - skin + e]);
    lead_channel(port_x - port_d, reach - board_l / 2 + 1);
  }
  lips(port_x + port_d / 2 + 2, reach - board_l / 2 - 1);
}

module assembly() {
  color("white") clamp();
  color("lightgrey") translate([0, 0, pad_top]) arm();
}

if (part == "clamp") clamp();
else if (part == "arm") arm();
else assembly();
