// Tool caddy, LONG layout (massing study, not a print): front row tray A then the calipers, head left;
// back row C grid, B posts, F thin drivers, all in a line. X right, Y away from the user, Z up.
// parts: base
/* [Layout] */
wall = 3;
base_t = 3;
a_len = 85; a_wid = 50;          // zone A tray, open, flat
cal_len = 240; cal_wid = 78;     // calipers; jaw 45 toward the user, 31 behind the beam
cal_beam = 16; cal_head = 40;    // beam width; head length along X (guess)
c_pitch = 25; c_handle = 18; c_cols = 3; c_rows = 3;
b_n = 7; b_pitch = 15; b_post = 9.9; b_h = 25;
f_n = 14; f_pitch = 6; f_depth = 85; f_h = 51;
front_depth = 84;
back_gap = 3;
c_w = (c_cols-1)*c_pitch + c_handle + 2;
b_w = (b_n-1)*b_pitch + b_post + 2*5;
f_w = (f_n-1)*f_pitch + 13;
back_depth = max((c_rows-1)*c_pitch + c_handle + 2, f_depth);
front_w = wall + a_len + wall + cal_len + wall;
total_w = max(front_w, wall + c_w + wall + b_w + wall + f_w + wall);
total_d = wall + front_depth + wall + back_depth + wall;
module tray_a() { translate([wall, wall, base_t]) difference() {
    cube([a_len, a_wid, 12]); translate([2,2,2]) cube([a_len-4, a_wid-4, 12]); } }
module calipers() { x0 = wall + a_len + wall; y0 = wall + 31 + 5;
  color("gray") translate([x0, y0, base_t]) { cube([cal_len, cal_beam, 3]);
    translate([0, -45+cal_beam-0, 0]) cube([cal_head, cal_wid, 3]); } }
module c_grid() { x0 = wall + c_handle/2 + 1; y0 = wall + front_depth + wall + c_handle/2 + 1;
  for (i=[0:c_cols-1], j=[0:c_rows-1]) translate([x0+i*c_pitch, y0+j*c_pitch, base_t])
    difference() { cylinder(d=c_handle+4, h=40, $fn=40); translate([0,0,2]) cylinder(d=c_handle, h=40, $fn=40); } }
module b_posts() { x0 = wall + c_w + wall + 5 + b_post/2; y0 = wall + front_depth + wall + 8;
  for (i=[0:b_n-1]) translate([x0+i*b_pitch, y0, base_t]) cylinder(d=b_post, h=b_h, $fn=32); }
module f_zone() { x0 = wall + c_w + wall + b_w + wall + 6; y0 = wall + front_depth + wall + 2;
  for (i=[0:f_n-1]) translate([x0+i*f_pitch, y0, base_t]) hull() { cube([4, 1, 1]);
    translate([0, f_depth-6, f_h-1]) cube([4, 1, 1]); }
  translate([x0-3, y0-3, base_t]) cube([f_w, 2, 14]); }
union() { color("steelblue") cube([total_w, total_d, base_t]); tray_a(); calipers(); c_grid(); b_posts(); f_zone(); }
