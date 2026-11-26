// Snap cover for the potted shell, PETG, in print orientation: plate face down, skirt up.
// parts: cover
// Use pose is cover() in model.scad; this turns it over about X (a rotation, not a mirror).
include <model.scad>
part = "none";

rotate([180, 0, 0]) translate([0, 0, -(shell_h + cover_t)]) cover();
