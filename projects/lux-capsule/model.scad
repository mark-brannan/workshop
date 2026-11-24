// Lux sensor capsule sitting on top of a horizontal 38.1 mm tube (tube axis along x), facing up. z up, z = 0 is the top of the tube, tube axis at z = -19.05.
// Three printed parts: base (a saddle with two zip-tie grooves that go round the tube), riser (ring the board sits on), cap (glass seat over the board).
// The VEML7700 lies under a PTFE disc and the cabochon; its own Qwiic socket takes a short pigtail that is joined to the cat5 pairs outside the head (inside the tube, center version). No terminal, no extender board.
view = "closed";    // closed | section | cap_print | riser_print | base_print
exit = "center";    // center: cable through a hole drilled in the top of the hollow tube | side: cable out through a notch in the cap wall, along the tube (+x)
tube_od = 38.1; R_t = tube_od/2;
head_d = 33; bore_d = 25.2;          // head = glass + 3.9 mm wall
plate_t = 3; edge_r = 4;             // saddle thickness at the tube's top; rounding of the cap's top edge
// Window: same stack as lux-sensor-mount
cab_d = 24.8; cab_h = 6;             // owner's cabochon, measured
ptfe_t = 1;  capture = 1.5; seat_gap = 0.15; bevel = 30;
lux = [16.51, 16.51, 1.6];           // Adafruit VEML7700 4162, Eagle .brd
conn_h = 4.3;                        // Qwiic (JST-SH) socket height above the board: a guess
riser_h = 2.5;                       // pigtail runs under the board
riser_od = 25; riser_id = 21;        // board corners (diag 23.3) rest on the ring
gap = 0.3;                           // connector top to PTFE
screw_r = 14.3; screw_d = 1.7;       // two M2 self-tapping at +-y
side_z = -9.6; ear_w = 8; tie_x = 19.6;   // saddle: the cap's circle plus an ear each side; its sides stop where the tube surface reaches them
tie_w = 3.4; tie_d = 1.2;                  // zip-tie grooves across the ears
slot_w = 5; slot_z = 2;
cap_z = plate_t;                     // cap and riser start on the plate
z_board = cap_z + riser_h; z_ptfe = z_board + lux[2] + conn_h + gap; z_g = z_ptfe + ptfe_t;
cab_R = (pow(cab_d/2, 2) + cab_h*cab_h)/(2*cab_h); lip_r = cab_d/2 - capture;
lip_h = sqrt(cab_R*cab_R - lip_r*lip_r) - (cab_R - cab_h);
cap_top = z_g + lip_h + 1.2;
echo(overall = cap_top, dome_above_cap = z_g + cab_h - cap_top);
$fn = 120;
module glass(o = 0) translate([0, 0, z_g - (cab_R - cab_h)]) intersection() { sphere(r = cab_R + o); translate([-50, -50, cab_R - cab_h]) cube(100); }
module tube_cut() translate([-100, 0, -R_t]) rotate([0, 90, 0]) cylinder(r = R_t + 0.2, h = 200);
module base() difference() {
  union() {
    translate([0, 0, side_z]) cylinder(d = head_d, h = plate_t - side_z);
    hull() for (sx = [-1, 1]) translate([sx*(tie_x - 0.6), 0, 0]) rotate_extrude() hull() { translate([0, side_z]) square([ear_w/2, 1]); translate([ear_w/2 - 2, plate_t - 2]) circle(2); translate([0, plate_t - 2]) square([1, 2]); }
  }
  tube_cut();
  for (sx = [-1, 1]) translate([sx*tie_x - tie_w/2, -30, plate_t - tie_d]) cube([tie_w, 60, 10]);
  if (exit == "center") translate([0, 0, -30]) cylinder(d = 7, h = 40);
  for (s = [-1, 1]) translate([0, s*screw_r, -30]) { cylinder(d = 2.4, h = 40); cylinder(d = 4.0, h = 30 - 5 + 2); }
}
module riser() translate([0, 0, cap_z]) difference() {
  cylinder(d = riser_od, h = riser_h);
  translate([0, 0, -1]) cylinder(d = riser_id, h = riser_h + 2);
  if (exit == "side") translate([riser_od/2 - 3, -slot_w/2, -1]) cube([6, slot_w, slot_z + 1 + 0.01]);
}
module cap() difference() {
  translate([0, 0, cap_z]) rotate_extrude() hull() { square([head_d/2, 1]); translate([head_d/2 - edge_r, cap_top - cap_z - edge_r]) circle(edge_r); square([1, cap_top - cap_z]); }
  translate([0, 0, cap_z - 1]) cylinder(d = bore_d, h = z_g - cap_z + 1);
  glass(seat_gap);
  translate([0, 0, z_g + lip_h + 0.4]) cylinder(h = 20, r1 = lip_r, r2 = lip_r + 20/tan(bevel));
  for (s = [-1, 1]) translate([0, s*screw_r, cap_z - 1]) cylinder(d = screw_d, h = 9);
  if (exit == "side") hull() { translate([0, 0, cap_z + slot_z]) rotate([0, 90, 0]) cylinder(d = slot_w, h = 30); translate([0, -slot_w/2, cap_z - 1]) cube([30, slot_w, 1]); }
}
module parts() {
  color("SteelBlue") base(); color("LightSteelBlue") riser(); color("CadetBlue") cap();
  color("LightCyan", 0.6) glass(); color("white") translate([0, 0, z_ptfe]) cylinder(d = bore_d - 0.6, h = ptfe_t);
  color("green") translate([-lux[0]/2, -lux[1]/2, z_board]) cube(lux);
  color("Crimson") translate([-lux[0]/2 - 1, -3, z_board + lux[2]]) cube([4, 6, conn_h]);   // Qwiic socket, position a guess
}
module tube() color("silver", 0.3) translate([-40, 0, -R_t]) rotate([0, 90, 0]) difference() { cylinder(r = R_t, h = 80); translate([0, 0, -1]) cylinder(r = R_t - 3, h = 82); }
if (view == "cap_print") translate([0, 0, -cap_z]) cap();
if (view == "riser_print") translate([0, 0, -cap_z]) riser();
if (view == "base_print") translate([0, 0, plate_t]) rotate([180, 0, 0]) base();   // saddle top on the bed, the tube trench up
if (view == "closed") { parts(); tube(); }
if (view == "section") intersection() { union() { parts(); tube(); } translate([-100, -100, -100]) cube([100, 200, 300]); }
