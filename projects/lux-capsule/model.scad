// Lux sensor capsule on the top of a 38.1 mm tube. Axis = tube axis, z up, z = 0 is the tube's top face.
// Three printed parts: base (plate + three zip-tie fingers down the tube), riser (ring the board sits on), cap (glass seat over the board).
// The VEML7700 lies under a PTFE disc and the cabochon; cat5 pairs go on a 2.54 mm screw terminal under the board. No extender board.
view = "closed";    // closed | section | cap_print | riser_print | base_print
exit = "center";    // center: cable down the hollow tube | side: cable out through a notch in the cap wall, +x
tube_od = 38.1; R_t = tube_od/2;
head_d = 34; bore_d = 25.2;          // head = glass + 4.4 mm wall
plate_t = 3;
// Window: same stack as lux-sensor-mount
cab_d = 24.8; cab_h = 6;             // owner's cabochon, measured
ptfe_t = 1;  capture = 1.5; seat_gap = 0.15; bevel = 30;
lux = [16.51, 16.51, 1.6];           // Adafruit VEML7700 4162, Eagle .brd
term = [12.7, 6, 7.5];               // 5-position 2.54 mm screw terminal under the board: a guess, not bought
riser_h = 9.5;                       // terminal 7.5 + 2 for wire ends
riser_od = 25; riser_id = 21;        // board corners (diag 23.3) rest on the ring
gap = 0.8;                           // board top to PTFE
screw_r = 14.8; screw_d = 1.8;       // two M2 self-tapping at +-y
tabs = [0, 120, 240]; tab_t = 3; tab_arc = 30; fh = 14; tie_z = -6.5;
slot_w = 6.5; slot_z = 4;
cap_z = plate_t;                     // cap and riser start on the plate
z_board = cap_z + riser_h; z_ptfe = z_board + lux[2] + gap; z_g = z_ptfe + ptfe_t;
cab_R = (pow(cab_d/2, 2) + cab_h*cab_h)/(2*cab_h); lip_r = cab_d/2 - capture;
lip_h = sqrt(cab_R*cab_R - lip_r*lip_r) - (cab_R - cab_h);
cap_top = z_g + lip_h + 1.2;
echo(overall = cap_top, dome_above_cap = z_g + cab_h - cap_top);
$fn = 120;
module glass(o = 0) translate([0, 0, z_g - (cab_R - cab_h)]) intersection() { sphere(r = cab_R + o); translate([-50, -50, cab_R - cab_h]) cube(100); }
module base() difference() {
  union() {
    cylinder(d = head_d, h = plate_t);
    for (a = tabs) rotate(a - tab_arc/2) rotate_extrude(angle = tab_arc) {
      square([R_t + 0.25 + tab_t, plate_t]);
      translate([R_t + 0.25, -fh]) square([tab_t, fh + plate_t]);
    }
  }
  translate([0, 0, tie_z - 1.7]) difference() { cylinder(d = 2*(R_t + 0.25 + tab_t) + 2, h = 3.4); translate([0, 0, -1]) cylinder(d = 2*(R_t + 0.25 + tab_t - 1.2), h = 6); }
  if (exit == "center") translate([0, 0, -1]) cylinder(d = 7, h = plate_t + 2);
  for (s = [-1, 1]) translate([0, s*screw_r, -1]) { cylinder(d = 2.4, h = plate_t + 2); cylinder(d = 4.2, h = 1 + 1.6); }
}
module riser() translate([0, 0, cap_z]) difference() {
  cylinder(d = riser_od, h = riser_h);
  translate([0, 0, -1]) cylinder(d = riser_id, h = riser_h + 2);
  if (exit == "side") translate([riser_od/2 - 3, -slot_w/2, -1]) cube([6, slot_w, slot_z + 1 + 0.01]);
}
module cap() difference() {
  translate([0, 0, cap_z]) cylinder(d = head_d, h = cap_top - cap_z);
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
  color("Crimson") translate([-term[0]/2, 2 - term[1]/2, z_board - term[2]]) cube(term);
}
module tube() color("silver", 0.3) translate([0, 0, -60]) difference() { cylinder(d = tube_od, h = 60); translate([0, 0, -1]) cylinder(d = tube_od - 6, h = 62); }
if (view == "cap_print") translate([0, 0, -cap_z]) cap();
if (view == "riser_print") translate([0, 0, -cap_z]) riser();
if (view == "base_print") translate([0, 0, plate_t]) mirror([0, 0, 1]) base();   // plate top on the bed, fingers up
if (view == "closed") { parts(); tube(); }
if (view == "section") intersection() { union() { parts(); tube(); } translate([-100, -100, -100]) cube([200, 100, 300]); }
