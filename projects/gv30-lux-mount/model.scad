// GV30 lux add-on: a split ring between the clamp's stub shoulder and the GV30.
// It slips over the stub; the split lets it go on around the coax without pulling it.
// A short arm runs straight out, the split continuing down its middle.
// Origin: antenna axis on Z, z = 0 on the stub's shoulder. Prints as shown.

/* [Ring] */
od = 32;            // the shoulder it sits on, off ref/clamp-upper.stl
id = 26;            // over the 1"-14 stub (OD 25.2)
h = 8;              // costs this much thread engagement (GV30 thread depth not measured)
split = 1.5;        // gap
arm_w = 16;         // across, split included
arm_l = 30;         // beyond the ring

$fn = 96;
e = 0.01;

difference() {
  union() {
    cylinder(d = od, h = h);
    translate([0, -arm_w / 2, 0]) cube([od / 2 + arm_l, arm_w, h]);
  }
  translate([0, 0, -e]) cylinder(d = id, h = h + 2 * e);
  translate([0, -split / 2, -e]) cube([od / 2 + arm_l + 1, split, h + 2 * e]);
}
