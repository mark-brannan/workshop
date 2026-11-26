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
strip_slot_t = 6; strip_base_w = 20; strip_top_w = 30; strip_depth = 50;
strip_block_w = 2*(strip_slot_t/2 + 1 + snip_wall + (strip_depth + 2)*tan(snip_lean) + 3);   // the ring's foot across, fillets included
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
// One continuous swept wall: seen from above ⊂ ⊃ joined at the back. Its inner face runs from the left
// thumb's tip, round the left web (10 inside), along the back wall, round the right web to the right thumb's
// tip, one tangent-smooth curve. A single cross-section is swept along it: 3 thick (4 on the thumbs),
// fully round on top, a 3 concave fillet each side at the base, and a lean that eases from vertical at the
// shoulders out to the base (foot stands snip_L out). Thumbs (9 long) rise 15 deg toward the inside and end
// in a round nose. One polyhedron, no hulls, no seams.
snip_hand_h = 12; snip_fillet = 3; snip_lean_pow = 1.5; snip_thumb_ease = 3;
function sn_smooth(x) = let(t = max(0, min(1, x))) t*t*(3 - 2*t);
function sn_rise(x) = x <= 0 ? 0 : x < snip_thumb_ease ? x*x/(2*snip_thumb_ease) : x - snip_thumb_ease/2;
function sn_off(z, z0, L) = z >= z0 ? 0 : L*pow(1 - max(z, 0)/z0, snip_lean_pow);   // outward lean, L at the base
function sn_flare(z) = z >= snip_fillet ? 0 : snip_fillet - sqrt(snip_fillet*snip_fillet - pow(snip_fillet - max(z, 0), 2));
// one cross-section: [u outward, z], 0.5 below the base up the inner face, over the round top, down the outer face
function sn_profile(t, top, z0, L) = let(
    zt = top - t/2, zs = concat([-0.5], [for (i = [0:7]) snip_fillet*pow(i/8, 1.6)], [for (i = [0:16]) snip_fillet + (zt - snip_fillet)*i/16]),
    c = function(z) sn_off(z, z0, L) + t/2, h = function(z) t/2 + sn_flare(z))
  concat([for (z = zs) [c(z) - h(z), z, c(z)]],
         [for (i = [1:11]) let(a = 180 - 180*i/12) [c(zt) + t/2*cos(a), zt + t/2*sin(a), c(zt)]],
         [for (j = [len(zs)-1:-1:0]) let(z = zs[j]) [c(z) + h(z), z, c(z)]]);
module snips() { Ri = snip_hand_in/2; R = Ri + snip_wall; z0 = snip_h + snip_tip_up; L = snip_L; W = snip_W;
  ztop = z0 + snip_hand_h; tl = snip_thumb_len; nt = 18; nc = 12;
  // stations: [x, y, tangent, distance along the thumb from its root (<0: steps into the web), nose angle, tip direction]
  thumb = function(x0, sx) concat([for (i = [0:nc-1]) [x0 + sx*tl, -Ri, [-1, 0], tl, 89.5*(1 - i/nc), [sx, 0]]],
                                  [for (i = [0:nt]) let(d = tl*(1 - i/nt)) [x0 + sx*d, -Ri, [-1, 0], d, 0, [sx, 0]]]);
  rt = thumb(W, -1);
  st = concat(thumb(0, 1),
    [for (i = [1:35]) let(a = 270 - 180*i/36) [Ri*cos(a), Ri*sin(a), [sin(a), -cos(a)], -1 - i, 0, [0, 0]]],
    [for (i = [0:32]) [W*i/32, Ri, [1, 0], -100, 0, [0, 0]]],
    [for (i = [1:35]) let(a = 90 - 180*i/36) [W + Ri*cos(a), Ri*sin(a), [sin(a), -cos(a)], -1 - (36 - i), 0, [0, 0]]],
    [for (i = [len(rt)-1:-1:0]) rt[i]]);
  sweep([for (p = st) let(
      d = p[3], on = d >= 0, arcd = on ? 0 : -d - 1,                       // arcd: steps into the web from the thumb
      t = snip_wall + (snip_thumb_t - snip_wall)*(on ? 1 : 1 - sn_smooth(arcd/8)),
      top = ztop + (on ? tan(snip_tilt)*sn_rise(d) : 0))
    [p[0], p[1], p[2], t, top, z0, L, p[4], p[5]]], false, [front_w + 5 + R + L, wall + 27 + R + L, base_t]); }
// The sweep both holders share. A station: [x, y, tangent, thickness, top, z0 (lean ends), lean at base,
// nose angle, tip direction]. The section's inner face sits on (x, y); outward is left of the tangent.
// closed: the last station joins the first. Open: each end turns round its own centre line in a nose.
module sweep(st, closed, at) {
  profs = [for (p = st) let(n = [-p[2].y, p[2].x], phi = p[7], tip = p[8])
    [for (uv = sn_profile(p[3], p[4], p[5], p[6])) let(e = uv[0] - uv[2], u = uv[2] + e*cos(phi), f = abs(e)*sin(phi))
      [p[0] + n.x*u + tip.x*f, p[1] + n.y*u + tip.y*f, uv[1]]]];
  m = len(profs[0]); k = len(profs);
  // the nose ends are near-flat slivers: close each as a strip pairing inner and outer points, never one bent polygon
  cap = function(j, i) let(a = [i*m + j, i*m + j + 1, i*m + m - 2 - j, i*m + m - 1 - j],
                           f = j + 1 == m - 2 - j ? [[a[0], a[1], a[3]]] : [a]) i == 0 ? f : [for (q = f) [for (v = [len(q)-1:-1:0]) q[v]]];
  translate(at) polyhedron(points = [for (pr = profs) each pr],
    faces = concat([for (i = [0:closed ? k-1 : k-2], j = [0:m-1]) let(i1 = (i+1)%k) [i*m + j, i1*m + j, i1*m + (j+1)%m, i*m + (j+1)%m]],
                   closed ? [] : [for (j = [0:(m-3)/2]) each cap(j, 0)], closed ? [] : [for (j = [0:(m-3)/2]) each cap(j, k-1)]), convexity = 6); }
// Strippers, nose down: the jaws 6 thick, 20 wide at the tip widening to 30 at 50 up; handles stand about
// 120 above, 60 wide, 12 thick (not drawn). The same swept wall as the snips, closed into a ring round the
// jaws: inside 2 over the jaws' thickness and their widest width, the long side front to back, standing on the
// jaws' tips. Round top, base fillets, the lean easing out to the foot.
strip_in_w = strip_slot_t + 2; strip_in_l = strip_top_w + 2; strip_h = strip_depth + 2; strip_z0 = strip_h - snip_hand_h;
strip_L = strip_h*tan(snip_lean);
strip_foot = strip_block_w/2;   // ring centre to the outer edge of the foot
module strippers() { r = strip_in_w/2; S = strip_in_l - strip_in_w; n = 24;
  // the inner face, clockwise seen from above: down the right side, round the front, up the left, round the back
  st = concat([for (i = [0:15]) [r, S - S*i/16, [0, -1]]],
    [for (i = [0:n-1]) let(a = -180*i/n) [r*cos(a), r*sin(a), [sin(a), -cos(a)]]],
    [for (i = [0:15]) [-r, S*i/16, [0, 1]]],
    [for (i = [0:n-1]) let(a = 180 - 180*i/n) [r*cos(a), S + r*sin(a), [sin(a), -cos(a)]]]);
  sweep([for (p = st) [p[0], p[1], p[2], snip_wall, strip_h, strip_z0, strip_L, 0, [0, 0]]], true,
        [front_w + 5 + snip_total_w + 6 + strip_foot, wall + 27 + strip_foot, base_t]); }
module pocket(w, d, h) { difference() { cube([w+4, d+4, h]); translate([2,2,2]) cube([w, d, h]); } }
// Vase box for rulers and long tools: the back row's remaining width, right of C
vase_x = wall + f_w + wall + c_w + wall;
module vase() { translate([vase_x, f_y, base_t]) pocket(total_w - vase_x - wall - 4, total_d - f_y - wall - 4, 100); }
union() { color("steelblue") cube([total_w, total_d, base_t]); tray_a(); calipers(); c_zone(); b_posts(); f_zone(); snips(); strippers(); vase(); }
