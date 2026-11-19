// Fit-check gauge, hand-written: the two unmeasured fits, for a fraction of the plastic.
//   left   a 10 mm ring of the lid's collar, slotted like it: drop it over the heater's bottom rim.
//   right  one and a half turns of the duct spigot: screw the duct on. Pitch is the owner's estimate.
// Both print ring face down. Change pitch or collar_fit in model.scad and reprint before the full parts.
include <model.scad>
part = "none";

/* [Gauge] */
rim_grip = 10;          // overrides the model's 22: enough to feel the fit, slots still 5 mm long
spigot_h = 1.5 * pitch; // one and a half turns of rib
flange = 3;             // ring beyond the collar or spigot, to hold it flat and give a grip

module rim_gauge() intersection() {
  lid();
  cylinder(d = rim_d + 2 * collar_fit + 2 * wall + 2 * flange, h = 100);
}
module duct_gauge() intersection() {
  spigot();
  cylinder(d = spigot_d + 2 * flange, h = 100);
}

translate([-(rim_d / 2 + wall + flange + 4), 0, 0]) rim_gauge();
translate([spigot_d / 2 + flange + 4, 0, 0]) duct_gauge();
