// GV30 lux add-on: a split ring between the clamp's stub shoulder and the GV30.
// It slips over the stub; the split lets it go on around the coax without pulling it.
// A side hole lets the sensor's cord in towards the mast's centre.
// Origin: antenna axis on Z, z = 0 on the stub's shoulder. Prints as shown.

/* [Ring] */
od = 32;            // the shoulder it sits on, off ref/clamp-upper.stl
id = 26;            // over the 1"-14 stub (OD 25.2)
h = 8;              // costs this much thread engagement (GV30 thread depth not measured)
split = 1.5;        // gap
cord_d = 4.5;       // cord (not measured)

$fn = 96;
e = 0.01;

difference() {
  cylinder(d = od, h = h);
  translate([0, 0, -e]) cylinder(d = id, h = h + 2 * e);
  translate([0, -split / 2, -e]) cube([od, split, h + 2 * e]);
  translate([0, 0, h / 2]) rotate([0, 90, 180]) cylinder(d = cord_d, h = od);
}
