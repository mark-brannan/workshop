// Tool caddy, LONG layout (massing study, not a print): front row tray A then the calipers, head left;
// back row C grid, B posts, F thin drivers, all in a line. X right, Y away from the user, Z up.
// parts: caddy
/* [Layout] */
wall = 3;
base_t = 3;
a_len = 50; a_wid = 85;          // zone A tray, open, flat
cal_len = 240; cal_wid = 78;     // calipers; jaw 45 toward the user, 31 behind the beam
cal_beam = 16; cal_head = 40;    // beam width; head length along X (guess)
c_n = 9; c_pitch = 25; c_handle = 18; c_hlen = 90; c_len = 155; c_shaft = 3;   // c_hlen guessed
b_n = 7; b_pitch = 15; b_post = 9.9; b_h = 25;
f_n = 14; f_pitch = 6; f_len = 120; f_handle = 5.2; f_hlen = 87; f_shaft = 3;
k = sin(45);
front_depth = 85;
back_gap = 3;
c_w = (c_n-1)*c_pitch + c_handle + 2;
b_w = (b_n-1)*b_pitch + b_post + 2*5;
f_w = (f_n-1)*f_pitch + 13;
function foot_w(hd) = max(hd, 12)/2 + 3;       // footboard half-height, along its own slope
function zone_depth(hd, L) = foot_w(hd)*k + L*k + foot_w(hd)*k;
back_depth = max(zone_depth(c_handle, c_len), zone_depth(f_handle, f_len));
front_w = wall + a_len + wall + cal_len + wall;
snip_w = 41; snip_h = 47; snip_arm_t = 6; snip_hand_d = 15; snip_hand_in = 10; snip_hand_gap = 8;   // outer 15, bore 10 (user), opening 8 guessed snip_arm_depth = 12;
snip_tilt = 20; snip_len = 18; snip_plate_t = 2.5;   // saddle tilts up toward the other one; 10-30 deg to be confirmed
snip_cx = snip_w/2 + 1 + snip_plate_t;            // centre of the pair, from the holder's left edge
snip_total_w = 2*snip_cx;
strip_slot_t = 6; strip_base_w = 20; strip_top_w = 30; strip_depth = 50; strip_block_w = 44; strip_block_t = 14;
total_w = max(front_w + 5 + b_w - 10 + 5, front_w + 5 + snip_total_w + 6 + strip_block_w + 5, wall + f_w + wall + c_w + wall);
c_y = wall + 36 + cal_beam + 3;      // C footboard sits just behind the calipers' beam
f_y = wall + front_depth + wall;
total_d = max(f_y + zone_depth(f_handle, f_len), c_y + zone_depth(c_handle, c_len)) + wall;
module tray_a() { translate([wall, wall, base_t]) difference() {
    cube([a_len, a_wid, 12]); translate([2,2,2]) cube([a_len-4, a_wid-4, 12]); } }
module calipers() { x0 = wall + a_len + wall; y0 = wall + 31 + 5;
  color("gray") translate([x0, y0, base_t]) { cube([cal_len, cal_beam, 3]);
    translate([0, -45+cal_beam-0, 0]) cube([cal_head, cal_wid, 3]); } }
// Drivers lie at 45 deg, swivel/handle end down at the front, tip up and back. The footboard is a
// plate square to the drivers (its face at 45 deg the other way); two risers cradle the shafts.
module angled(n, pitch, L, hd, hlen, sd, risers, cradle_d=0, clip_s=0) { hw = foot_w(hd); zo = hw*k + 0.5; yo = hw*k; wd = (n-1)*pitch + hd + 4;
  // footboard solid: sloped face on top, down to the base
  translate([-hd/2-2, 0, 0]) rotate([90,0,90]) linear_extrude(wd) polygon([
    [yo-hw*k, zo+hw*k], [yo+hw*k, zo-hw*k], [yo+hw*k, 0], [yo-hw*k, 0]]);
  translate([0, yo, zo]) rotate([-45,0,0]) for (i=[0:n-1]) translate([i*pitch,0,0]) {
    cylinder(d=hd, h=hlen, $fn=32); cylinder(d=sd, h=L, $fn=16); }
  for (s = risers) translate([-hd/2-2, yo+s*k-1.5, 0]) cube([wd, 3, zo+s*k-hd/2*k]);
  if (cradle_d > 0) {
    // lower support: a half-circle trough (cradle_d) at the first riser position; clip: a U slot of the shaft diameter, open at the top
    for (s = [risers[0]]) difference() {
      translate([-hd/2-2, yo+s*k-1.5, 0]) cube([wd, 3, zo+s*k+1]);
      translate([0, yo, zo]) rotate([-45,0,0]) for (i=[0:n-1]) translate([i*pitch,0,0]) cylinder(d=cradle_d, h=L, $fn=32); }
    difference() {
      translate([-hd/2-2, yo+clip_s*k-1.5, 0]) cube([wd, 3, zo+clip_s*k+4]);
      translate([0, yo, zo]) rotate([-45,0,0]) for (i=[0:n-1]) translate([i*pitch,0,0]) cylinder(d=sd+0.4, h=L, $fn=24);
      for (i=[0:n-1]) translate([i*pitch-(sd+0.4)/2, yo+clip_s*k-2, zo+clip_s*k]) cube([sd+0.4, 4, 6]); } } }
module c_zone() { translate([wall+f_w+wall+0.9+c_handle/2+1, c_y, base_t])
  angled(c_n, c_pitch, c_len, c_handle, c_hlen, c_shaft, [30], 13, 91); }
// B: seven posts in one row along X, 15 c-c, in line with the calipers' beam, past its right end
module b_posts() { x0 = front_w + 5 + b_post/2; y0 = wall + 10;
  for (i=[0:b_n-1]) translate([x0+i*b_pitch, y0, base_t]) cylinder(d=b_post, h=b_h, $fn=32); }
module f_zone() { translate([wall + 6, wall+front_depth+wall, base_t])
  angled(f_n, f_pitch, f_len, f_handle, f_hlen, f_shaft, [20, 72]); }
// Wire snips, nose down: two open arms, each topped by a C-shaped hand that takes one shoulder
// (shoulders 41 wide, 47 from the tip). Nothing between the arms. Hand sizes are guessed.
// Each hand: a thin C band (2.5 thick, 12 tall, 10 dia) lying flat, seen from above as ⊂ ⊃ with the
// openings toward each other, so each takes one shoulder's edge sideways as the snips drop between.
// It stands on a 2.5 thick plate at its outer edge; a 45 deg gusset holds the C's inner half.
snip_band_t = 2.5; snip_hand_h = 12;
module soft(r = 1) { offset(r = r, $fn = 24) offset(delta = -r) children(); }   // rounds every convex corner
// Each hand is a saddle: a rounded half-pipe (10 inside width, 2.5 wall, lips 3.5 above the axis) running
// toward the other saddle, open at both ends and along the top, tilted up toward the inside by snip_tilt.
// It hangs from a thin plate behind its outer end (rear support only; nothing under the saddle).
module saddle2d() { R = snip_hand_d/2; Ri = snip_hand_in/2;
  soft(1) difference() { union() { circle(r=R, $fn=48); translate([-R, 0]) square([2*R, 3.5]); }
    union() { circle(r=Ri, $fn=48); translate([-Ri, 0]) square([2*Ri, 10]); } } }
module snip_hand() { zo = snip_h - 5; R = snip_hand_d/2;                        // built for the left hand: inward is +x
  translate([0, 0, zo]) rotate([0, -snip_tilt, 0]) rotate([90, 0, 90]) linear_extrude(snip_len) saddle2d();
  translate([-snip_plate_t, 0, 0]) rotate([90, 0, 90]) linear_extrude(snip_plate_t) soft(1) translate([-R, 0]) square([2*R, zo + 2]); }
module snips() { translate([front_w + 5, wall + 27 + snip_hand_d/2, base_t]) {
    translate([snip_plate_t, 0, 0]) snip_hand();                                      // left hand: inward is +x
    translate([snip_total_w - snip_plate_t, 0, 0]) rotate([0, 0, 180]) snip_hand(); } }  // right hand: a turn, not a mirror
// Strippers: a small tower, nose down in a 6 thick slot, 20 wide at the base widening to 30 at the top,
// 50 deep; handles stand about 120 above, 60 wide, 12 thick (not drawn).
module strippers() { translate([front_w + 5 + snip_total_w + 6, wall + 27, base_t]) difference() {
    cube([strip_block_w, strip_block_t, strip_depth + 2]);
    translate([strip_block_w/2, (strip_block_t + strip_slot_t)/2, 2]) rotate([90, 0, 0]) linear_extrude(strip_slot_t)
      polygon([[-strip_base_w/2, 0], [strip_base_w/2, 0], [strip_top_w/2, strip_depth + 1], [-strip_top_w/2, strip_depth + 1]]); } }
module pocket(w, d, h) { difference() { cube([w+4, d+4, h]); translate([2,2,2]) cube([w, d, h]); } }
// Vase box for rulers and long tools: the back row's remaining width, right of C
vase_x = wall + f_w + wall + c_w + wall;
module vase() { translate([vase_x, f_y, base_t]) pocket(total_w - vase_x - wall - 4, total_d - f_y - wall - 4, 100); }
union() { color("steelblue") cube([total_w, total_d, base_t]); tray_a(); calipers(); c_zone(); b_posts(); f_zone(); snips(); strippers(); vase(); }
