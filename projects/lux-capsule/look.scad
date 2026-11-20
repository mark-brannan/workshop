// Look only: outside shape, no internals, no attachment. C = round button, D = stadium along the tube. z = 0 is the tube's top, tube along x.
R_t = 19.05; $fn = 120;
module tube() translate([-45, 0, -R_t]) rotate([0, 90, 0]) cylinder(r = R_t, h = 90);
module blob(len, w, h, er, depth = 14) hull() for (sx = [-1, 1]) translate([sx*(len - w)/2, 0, 0]) rotate_extrude() hull() {   // stadium of width w, length len; len = w gives a round button
  translate([0, -depth]) square([w/2, 1]);
  translate([w/2 - er, h - er]) circle(er);
  translate([0, h - er]) square([1, er]);
}
module eye(h) color("LightCyan", 0.7) translate([0, 0, h - 3]) intersection() { translate([0, 0, -(((12.4*12.4 + 36)/12) - 6)]) sphere(r = (12.4*12.4 + 36)/12); translate([-50, -50, 0]) cube(100); }
module head(len, w, h, er) { difference() { color("SteelBlue") blob(len, w, h, er); translate([-100, 0, -R_t]) rotate([0, 90, 0]) cylinder(r = R_t, h = 200); } eye(h); }
tube();
translate([-30, 0, 0]) head(32, 32, 18.7, 8);     // C
translate([22, 0, 0]) head(46, 32, 18.7, 8);      // D
