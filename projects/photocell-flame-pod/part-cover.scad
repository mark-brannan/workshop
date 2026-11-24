// Snap cover for the potted tray, PETG, in print orientation: plate face down, skirt up.
// Use pose is cover() in model.scad; this turns it over about X (a rotation, not a mirror).
include <model.scad>
part = "none";

rotate([180, 0, 0]) translate([0, 0, -(tray_h + cover_t)]) cover();
