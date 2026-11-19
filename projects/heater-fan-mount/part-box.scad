// The box in its print orientation: knob face (-Y as installed) down on the bed, smooth cabin face.
include <model.scad>
part = "none";
translate([0, 0, W / 2 + front - wall]) rotate([90, 0, 0]) box();
