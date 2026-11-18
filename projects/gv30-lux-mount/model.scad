// GV30 lux add-on: a ring under the antenna, a tongue through the GV30's slot, a bolt-on arm.
// The ring drops over the clamp's 1"-14 stub and is trapped between the stub's shoulder and the GV30's base.
// The tongue fills the GV30's slot: it keys the ring to the antenna and carries the sensor lead through the
// skirt into the antenna's cavity, where it runs down the clamp's bore with the coax.
// The arm screws to the tab outside the skirt (two M3 heat-set inserts), so a broken arm comes off without
// touching the coax. The VEML7700 sits face up under a thin skin of white ASA: the diffuser.
// Origin: antenna axis on Z, z = 0 on the stub's shoulder, arm along +X.
// Print: the ring as shown (flat on the bed); the arm upside down (skin on the bed).

part = "ring";       // [ring, arm, assembly]

/* [GV30: owner's figures and guesses] */
slot_w = 7;          // owner's figure
slot_l = 25;         // owner's figure; assumed open at the skirt's rim
skirt_ir = 34;       // skirt inside radius: a guess (vendor Ø75 overall)
skirt_t = 2.5;       // skirt wall: a guess

/* [Clamp: off ref/clamp-upper.stl] */
stub_d = 25.2;       // 1"-14 thread OD
boss_d = 32;         // the shoulder the ring sits on
shoulder_z = 9;      // shoulder height in the mesh's own coordinates

/* [Ring and tongue] */
ring_t = 3;          // costs this much thread engagement (GV30 thread depth not measured)
ring_id = 26;        // over the stub
ring_od = 66;        // inside the skirt
tongue_w = 6.4;      // slot_w less clearance
tongue_h = 18;       // above the ring, into the slot
tongue_in = 3;       // reaches this far inside the skirt
lead_d = 4.5;        // patch lead (not measured)

/* [Tab: arm seat, outside the skirt] */
tab_l = 16;          // radially, from just outside the skirt
tab_w = 22;
tab_h = 10;          // arm seats on top
insert_d = 4.0;      // M3 heat-set insert
insert_h = 6;
screw_dx = 9;        // from the tab's inboard face
screw_dy = 7;        // ± across

/* [Arm] */
reach = 95;          // antenna axis to sensor centre
arm_t = 8;
arm_w = 14;
head_d = 32;
board_l = 26;        // VEML7700, Adafruit 4162: 25.4 x 17.8 (vendor; not measured), plus clearance
board_w = 18.5;
skin = 0.6;          // white ASA over the sensor, 3 layers at 0.2
lead_w = 5.5;        // press-in channel on the arm's underside
lead_throat = 4.5;

/* [Hardware] */
screw_d = 3.4;
cbore_d = 6.5;
cbore_h = 3;

$fn = 96;
e = 0.01;

skirt_or = skirt_ir + skirt_t;
tab_x0 = skirt_or + 0.5;
tab_x1 = tab_x0 + tab_l;
port_x = tab_x0 + 3.5;   // lead drops through the tab here

module ring() {
  difference() {
    union() {
      cylinder(d = ring_od, h = ring_t);
      // tongue: from inside the skirt, through the slot, out to the tab
      translate([skirt_ir - tongue_in, -tongue_w / 2, 0]) cube([tab_x0 - skirt_ir + tongue_in + e, tongue_w, ring_t + tongue_h]);
      translate([tab_x0, -tab_w / 2, 0]) cube([tab_l, tab_w, tab_h]);
    }
    translate([0, 0, -e]) cylinder(d = ring_id, h = ring_t + 2 * e);
    // GV30 skirt: the ring's tab and tongue straddle it
    translate([0, 0, ring_t]) difference() {
      cylinder(r = skirt_or + 0.3, h = slot_l + 5);
      translate([0, 0, -e]) cylinder(r = skirt_ir - 0.3, h = slot_l + 6);
      translate([0, -slot_w / 2, -e]) cube([skirt_or + 1, slot_w, slot_l + 6]);
    }
    // lead: down through the tab from the arm, then inboard through the tongue into the cavity
    translate([port_x, 0, ring_t + lead_d / 2 + 1]) cylinder(d = lead_d, h = tab_h);
    translate([skirt_ir - tongue_in - 1, 0, ring_t + lead_d / 2 + 1]) rotate([0, 90, 0]) cylinder(d = lead_d, h = port_x - skirt_ir + tongue_in + 1);
    for (s = [-1, 1]) translate([tab_x0 + screw_dx, s * screw_dy, tab_h - insert_h]) cylinder(d = insert_d, h = insert_h + e);
  }
}

module lips(x0, x1) {
  lip = (lead_w - lead_throat) / 2;
  for (s = [-1, 1]) translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(x1 - x0)
    polygon([[s * lead_w / 2, 0], [s * lead_throat / 2, 0], [s * lead_w / 2, lip]]);
}

module arm() {
  // z = 0 is the underside, seated on the tab
  difference() {
    union() {
      translate([tab_x0, -tab_w / 2, 0]) cube([tab_l, tab_w, arm_t]);
      translate([tab_x1 - e, -arm_w / 2, 0]) cube([reach - tab_x1, arm_w, arm_t]);
      translate([reach, 0, 0]) cylinder(d = head_d, h = arm_t);
    }
    for (s = [-1, 1]) translate([tab_x0 + screw_dx, s * screw_dy, -e]) {
      cylinder(d = screw_d, h = arm_t + 2 * e);
      translate([0, 0, arm_t - cbore_h]) cylinder(d = cbore_d, h = cbore_h + 1);
    }
    translate([reach - board_l / 2, -board_w / 2, -e]) cube([board_l, board_w, arm_t - skin + e]);
    translate([port_x - lead_w / 2, -lead_w / 2, -e]) cube([reach - board_l / 2 - port_x + lead_w / 2 + 1, lead_w, arm_t - 2.5]);
  }
  lips(tab_x1 + 1, reach - board_l / 2 - 1);
}

module gv30_standin() {
  // skirt with its slot, and the base face on the ring; the dome above is not drawn
  translate([0, 0, ring_t]) difference() {
    union() {
      cylinder(r = skirt_or, h = slot_l + 8);
      translate([0, 0, slot_l + 8]) cylinder(r1 = skirt_or, r2 = skirt_or - 4, h = 12);
    }
    translate([0, 0, -e]) cylinder(r = skirt_ir, h = slot_l + 4);
    translate([0, -slot_w / 2, -e]) cube([skirt_or + 1, slot_w, slot_l]);
  }
}

module assembly() {
  color("gainsboro") translate([0, 0, -shoulder_z]) import("ref/clamp-upper.stl", convexity = 6);
  color("white") ring();
  color("lightgrey") translate([0, 0, tab_h]) arm();
  %gv30_standin();
}

if (part == "ring") ring();
else if (part == "arm") arm();
else assembly();
