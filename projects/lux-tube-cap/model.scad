// Lux sensor head that caps a 38.1 mm (1.5") tube, zip-tied on. Axis = tube axis, z up, z = 0 is the tube's top face.
// The QwiicBus EndPoint stands on edge, RJ45 jack down, so the cat5 plug rises straight into it: from inside the tube (exit = "center")
// or from a bay in the head with the cable leaving through the wall (exit = "side"). The VEML7700 lies on a deck above it under the window.
view = "closed";    // closed | exploded | section | body_print | lid_print | ring_print | deck_print
exit = "center";    // center | side
tube_od = 38.1;
skirt_id = tube_od + 0.4; skirt_od = 46; skirt_h = 15;
head_od = 46; wall = 3; Ri = head_od/2 - wall;
floor_t = 3;
// Window, same stack as lux-sensor-mount: cabochon loaded from below, dome through a lip, 1 mm PTFE square behind it, ring screwed up into the lid.
cab_d = 24.8; cab_h = 6;     // owner's cabochon, measured
ptfe_s = 25; ptfe_t = 1;
capture = 1.5; seat_gap = 0.15; bevel = 30;
lid_t = 6; lid_od = 50; drip_h = 4;
ring_t = 2; ring_d = 26; ring_ap = 18; ring_ear = 16.5;
m3_insert = [4.0, 4];  cb = [6.4, 2.5];
// Boards
ep = [25.4, 44.45, 1.6];     // SparkFun QwiicBus EndPoint 16988, Eagle .brd: width, length, thickness
jack = [16.5, 23.2, 13.5];   // RJ45 jack: width, length, height above board (height a guess)
jack_over = 9.7;             // jack overhangs the board's end (photo)
plug = [11.7, 21, 14];       // bootless RJ45 plug: width, length, height with latch
plug_z = 6.5;                // plug axis above the board's top face (guess)
lux = [16.51, 16.51, 1.6];   // Adafruit VEML7700 4162
board_gap = 1.5; deck_t = 3;
y0 = -plug_z - ep[2];        // EndPoint's back face; plug axis on the head axis
// Heights
z_mouth = exit == "center" ? floor_t + 1.5 : floor_t + plug[1] + 1;   // jack mouth: plug length of bay below it in the side version
z_b = z_mouth + jack_over;   // EndPoint's lower end
z_top = z_b + ep[1];
z_d = z_top + 0.5;           // top of the posts and the left card guide = underside of the deck
lux_bot = z_d + deck_t;
Z = lux_bot + lux[2] + board_gap + ring_t;   // lid underside
post_y = 17;
hole_d = 20;                 // floor hole for the plug (center version); the plug's diagonal is 18.3
exit_z = floor_t + 4.5;      // side version: cable hole centre, a little above the plug's rear face
echo(z_mouth = z_mouth, z_top = z_top, Z = Z, overall = Z + lid_t, skirt = skirt_h);
$fn = 120;
cab_R = (pow(cab_d/2, 2) + cab_h*cab_h)/(2*cab_h);
glass_z = Z + ptfe_t; lip_r = cab_d/2 - capture;
lip_h = sqrt(cab_R*cab_R - lip_r*lip_r) - (cab_R - cab_h);
module glass(o = 0) translate([0, 0, glass_z - (cab_R - cab_h)]) intersection() { sphere(r = cab_R + o); translate([-50, -50, cab_R - cab_h]) cube(100); }

xe = ep[0]/2;
module card_block(sx, top) mirror([sx > 0 ? 0 : 1, 0, 0]) difference() {   // rib from the wall to the board's edge; a slot holds 1.5 mm of the edge
  translate([xe - 1.5, y0 - 1.5, 0]) cube([Ri + 3 - xe + 1.5, ep[2] + 3, top]);
  translate([xe - 1.6, y0 - 0.15, z_b - 0.2]) cube([1.8, ep[2] + 0.3, 200]);
}
port_z = z_top - 12.7;       // EndPoint's Qwiic ports, one on each long edge; the right one stays clear
module inside() translate([0, 0, floor_t]) cylinder(r = Ri, h = Z);
module body() difference() {
  union() {
    translate([0, 0, -skirt_h]) cylinder(d = skirt_od, h = skirt_h + Z);
  }
  translate([0, 0, -skirt_h - 1]) cylinder(d = skirt_id, h = skirt_h + 1);          // sleeve over the tube
  inside();
  for (z = [-4, -11]) translate([0, 0, z - 2]) difference() { cylinder(d = skirt_od + 1, h = 4); cylinder(d = skirt_od - 2.4, h = 4); }   // zip-tie grooves, 1.2 deep
  for (a = [0:90:270]) rotate(a + 45) translate([skirt_id/2 - 1, -0.75, -skirt_h - 1]) cube([10, 1.5, skirt_h - 1 + 1]);   // four slits so the ties close the sleeve
  if (exit == "center") translate([0, 0, -1]) cylinder(d = hole_d, h = floor_t + 2);
  else translate([0, 0, exit_z]) rotate([90, 0, 0]) cylinder(d = 8, h = 40);          // cable out of the -y wall
}
module furniture() intersection() {
  cylinder(r = Ri + 1, h = Z);
  union() {
    card_block(-1, z_d); card_block(1, port_z - 6);
    for (s = [-1, 1]) translate([0, s*post_y, 0]) difference() { cylinder(d = 7, h = z_d); translate([0, 0, z_d - m3_insert[1]]) cylinder(d = m3_insert[0], h = m3_insert[1] + 1); }
  }
}
module head() { body(); intersection() { translate([0, 0, floor_t - 0.01]) cylinder(r = Ri + 1, h = Z); furniture(); } }
module corners(x0, y0_, sx, sy, h) for (cx = [0, 1], cy = [0, 1]) {   // L-shaped corner blocks round the VEML
  px = x0 + cx*sx; py = y0_ + cy*sy;
  translate([cx ? px - 6 : px, cy ? py : py - 2, 0]) cube([6, 2, h]);
  translate([cx ? px - 0.01 : px - 1.99, cy ? py - 6 : py - 0.01, 0]) cube([2, 6.01, h]);
}
module deck() difference() {   // prints flat; sits on the posts and the left card guide
  union() { cylinder(d = 2*Ri - 0.4, h = deck_t); translate([0, 0, deck_t - 0.01]) corners(-lux[0]/2 - 0.2, -lux[1]/2 - 0.2, lux[0] + 0.4, lux[1] + 0.4, 2.21); }
  for (s = [-1, 1]) translate([0, s*post_y, -1]) cylinder(d = 3.4, h = deck_t + 2);
  translate([9.5, y0 - 1, -1]) cube([8, 7, deck_t + 2]);          // Qwiic cable up from the EndPoint's right-hand port
}
module lid() difference() {
  union() {
    translate([0, 0, Z]) cylinder(d = lid_od, h = lid_t);
    translate([0, 0, Z - drip_h]) difference() { cylinder(d = lid_od, h = drip_h); translate([0, 0, -1]) cylinder(d = head_od + 0.6, h = drip_h + 2); }   // drip skirt over the head's wall
    for (s = [-1, 1]) translate([0, s*post_y, z_d + deck_t]) cylinder(d = 7, h = Z - z_d - deck_t + 0.01);   // bosses press the deck down
  }
  translate([-(ptfe_s + 0.4)/2, -(ptfe_s + 0.4)/2, Z - 1]) cube([ptfe_s + 0.4, ptfe_s + 0.4, ptfe_t + 1]);   // square PTFE pocket; the glass passes up through it
  glass(seat_gap);
  translate([0, 0, glass_z + lip_h + 0.4]) cylinder(h = 20, r1 = lip_r, r2 = lip_r + 20/tan(bevel));
  for (s = [-1, 1]) translate([s*ring_ear, 0, Z - 1]) cylinder(d = m3_insert[0], h = m3_insert[1] + 1);      // ring inserts
  for (s = [-1, 1]) translate([0, s*post_y, z_d + deck_t - 1]) { cylinder(d = 3.4, h = 50); translate([0, 0, Z + lid_t - cb[1] - (z_d + deck_t - 1)]) cylinder(d = cb[0], h = 10); }   // deck screws from the top
}
module ring() translate([0, 0, Z - ring_t]) difference() {
  union() { cylinder(d = ring_d, h = ring_t); for (s = [-1, 1]) hull() { cylinder(d = 7, h = ring_t); translate([s*ring_ear, 0, 0]) cylinder(d = 7, h = ring_t); } }
  translate([0, 0, -1]) cylinder(d = ring_ap, h = ring_t + 2);
  for (s = [-1, 1]) translate([s*ring_ear, 0, -1]) cylinder(d = 3.4, h = ring_t + 2);
}
module ptfe() color("white") translate([-ptfe_s/2, -ptfe_s/2, Z]) cube([ptfe_s, ptfe_s, ptfe_t]);
module dome() color("LightCyan", 0.6) glass();
module boards() {
  color("red", 0.9) translate([-xe, y0, z_b]) cube([ep[0], ep[2], ep[1]]);
  color("DimGray") translate([-jack[0]/2, y0 + ep[2], z_mouth]) cube([jack[0], jack[2], jack[1]]);
  color("green") translate([-lux[0]/2, -lux[1]/2, lux_bot]) cube(lux);
}
module cable() { color("SkyBlue") translate([-plug[0]/2, -plug[2]/2, z_mouth - plug[1]]) cube([plug[0], plug[2], plug[1]]);
  color("blue") if (exit == "center") translate([0, 0, -60]) cylinder(d = 5, h = 60 + z_mouth - plug[1]);
  else hull() { translate([0, 0, z_mouth - plug[1]]) sphere(d = 5); translate([0, -Ri - 8, exit_z]) sphere(d = 5); } }
module tube() color("silver", 0.3) translate([0, 0, -60]) difference() { cylinder(d = tube_od, h = 60); translate([0, 0, -1]) cylinder(d = tube_od - 6, h = 62); }
lift = view == "exploded" ? 30 : 0;
if (view == "body_print") translate([0, 0, skirt_h]) head();
if (view == "lid_print") translate([0, 0, -Z]) lid();
if (view == "ring_print") translate([0, 0, -(Z - ring_t)]) ring();
if (view == "deck_print") deck();
if (view == "closed" || view == "exploded" || view == "section") {
  if (view == "section") {
    intersection() { union() { color("SteelBlue") head(); color("Peru") translate([0, 0, z_d]) deck(); color("CadetBlue") lid(); dome(); ptfe(); color("orange") ring(); } translate([-200, -200, -100]) cube([400, 200, 400]); }
  } else { color("SteelBlue") head(); color("Peru") translate([0, 0, z_d + lift/2]) deck(); translate([0, 0, lift]) { color("CadetBlue") lid(); dome(); ptfe(); color("orange") translate([0, 0, -lift/3]) ring(); } }
  tube(); boards(); cable();
}
