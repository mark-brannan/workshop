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
snip_w = 40; snip_h = 45; snip_arm_t = 6; snip_hand_d = 15; snip_hand_in = 10; snip_hand_gap = 8;   // outer 15, bore 10 (user), opening 8 guessed snip_arm_depth = 12;
snip_wall = 3; snip_thumb_t = 4; snip_thumb_len = 9; snip_clear = 2; snip_tilt = 15; snip_tip_up = 3; snip_lean = 8;   // tip hangs 3 above the base
snip_W = snip_w + snip_clear - snip_hand_in;                 // web centre to web centre (32)
snip_L = (snip_h + snip_tip_up)*tan(snip_lean);                 // how far the wall's foot stands out from its top
snip_total_w = snip_W + 2*(snip_hand_in/2 + snip_wall + snip_L);   // outer width of the pair, feet included
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
// Wire snips, nose down, hung by the shoulders (45 from the tip, 40 wide, where the recurve begins).
// One continuous shape: a back wall across the pair curls forward at each end through a round web into a
// short thumb, and the whole wall leans out 8 deg as it descends so it stands on the base at a steady angle
// (nothing floats). Seen from above ⊂ ⊃ joined at the back, 10 inside at the top, 3 wall, 12 tall at the
// top, no floor between. Top edge fully round. Each thumb (4 thick, 9 long) rises 15 deg toward the inside;
// the pair is 2 wider than the shoulders so they push up into the thumbs; a leg under each thumb leans back.
snip_hand_h = 12;
module pill(d, h, fn = 48) { cylinder(d = d, h = h - d/2, $fn = fn); translate([0, 0, h - d/2]) sphere(d = d, $fn = fn); }
module seg(p, q, dp, dq, hp, hq) { hull() { translate(p) pill(dp, hp); translate(q) pill(dq, hq); } }
module slant(p, q, bp, bq, d, z0) { hull() { translate([p.x, p.y, z0]) pill(d, snip_hand_h); translate([q.x, q.y, z0]) pill(d, snip_hand_h);
    translate([bp.x, bp.y, 0]) cylinder(d = d, h = 1, $fn = 48); translate([bq.x, bq.y, 0]) cylinder(d = d, h = 1, $fn = 48); } }
module snips() { Ri = snip_hand_in/2; r = Ri + snip_wall/2; R = Ri + snip_wall; z0 = snip_h + snip_tip_up; n = 12; L = snip_L;
  translate([front_w + 5 + R + L, wall + 27 + R + L, base_t]) {
    slant([0, r], [snip_W, r], [0, r + L], [snip_W, r + L], snip_wall, z0);                     // back wall
    for (s = [1, -1]) { cx = s > 0 ? 0 : snip_W;                                                 // s = +1 left hand, -1 right
      for (i = [0:n-1]) { a0 = 90 + 180*i/n; a1 = 90 + 180*(i + 1)/n;                            // web: half circle round the shoulder's edge
        slant([cx + s*r*cos(a0), r*sin(a0)], [cx + s*r*cos(a1), r*sin(a1)],
              [cx + s*(r + L)*cos(a0), (r + L)*sin(a0)], [cx + s*(r + L)*cos(a1), (r + L)*sin(a1)], snip_wall, z0); }
      yt = -Ri - snip_thumb_t/2; ztip = z0 + snip_thumb_len*tan(snip_tilt);
      translate([0, 0, z0]) seg([cx, -r, 0], [cx, yt, 0], snip_wall, snip_thumb_t, snip_hand_h, snip_hand_h);   // web into thumb
      seg([cx, yt, z0], [cx + s*snip_thumb_len, yt, ztip], snip_thumb_t, snip_thumb_t, snip_hand_h, snip_hand_h);
      hull() { translate([cx + s*(snip_thumb_len - 1), yt, ztip - 1.5]) cylinder(d = 3.5, h = 1.5, $fn = 48);   // leg, leaning back
        translate([cx + s*0.5, yt, z0 - 1.5]) cylinder(d = 3.5, h = 1.5, $fn = 48);
        translate([cx - s*1.5, yt - snip_L, 0]) cylinder(d = 3.5, h = 0.5, $fn = 48);
        translate([cx + s*2.5, yt - snip_L, 0]) cylinder(d = 3.5, h = 0.5, $fn = 48); } } } }
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
