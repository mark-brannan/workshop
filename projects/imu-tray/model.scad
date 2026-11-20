// Enclosure for the ICM-20948 IMU and a QwiicBus EndPoint on a horizontal shelf, mid-boat, dry. Four feet at the corners take the shelf screws, outside the box.
// X along the tray: the RJ45 jack faces -x, its mouth at the -x wall's inside face (x = 0); the IMU sits at the +x end. Y across, Z up.
// The walls end in a rebate that takes a 3 mm lid: clear acrylic cut from the DXF, or the same outline printed (part-lid.scad).
// Print as shown, floor down, no supports.
part = "tray";       // tray | assembly

/* [Tray] */
floor_t = 2.5;
wall = 2.5;
in_y0 = -15;         // inside, -y side: board edge 12.7 plus room
in_y1 = 24;          // inside, +y side: the Qwiic plug on the EndPoint's +y edge, its cable, and the shelf screws
lid_z = 24.5;        // floor bottom to the lid's underside; jack top is 22.6 (jack height a guess)
end_gap = 3;         // IMU's far edge to the +x wall

/* [Lid rebate] */
lid_t = 3;           // 3 mm acrylic or a 3 mm printed plate; sits flush with the wall tops
ledge = 1.2;         // the lid's edge rests on this much of the wall
lid_gap = 0.3;       // lid edge to the rebate, each side (K40 kerf unmeasured)

/* [Boards] (Eagle .brd files; parts.md) */
ep = [44.45, 25.4, 1.6];    // SparkFun QwiicBus EndPoint 16988: length (x), width (y), thickness
jack_over = 9.7;            // the jack overhangs the board's -x end (photo, lux-tube-cap)
jack = [23.2, 16.5, 13.5];  // jack length, width, height above the board (height a guess)
plug_z = 6.5;               // plug axis above the board's top (guess)
imu = [25.4, 17.78, 1.6];   // Adafruit ICM-20948 4554
board_gap = 16;             // EndPoint's +x end to the IMU's -x end: the IMU's Qwiic plug and the cable's bend
post_h = 5;                 // board underside above the floor: clears solder on the boards' backs

/* [Screws] (hole sizes a guess: no calibration yet) */
pilot = [2.1, 6];           // M2.5 self-tapper into PETG: hole, depth from the post top. Same screw for both boards
post_d = 6;
shelf_hole = 4.8;           // four #8 / M4 pan-head wood screws, one per foot
foot_l = 11;                // past the end wall
foot_w = 10;                // across, from the box's side face inward: clear of the plug opening
foot_t = 3;

/* [Plug opening] */
slot_w = 19;         // in the -x wall, open at the top; plug 11.7 wide, boot wider

/* [Hidden] */
$fn = 48;
ep_x0 = jack_over;
ep_x1 = ep_x0 + ep[0];
imu_x0 = ep_x1 + board_gap;
imu_cx = imu_x0 + imu[0]/2;
in_x1 = imu_x0 + imu[0] + end_gap;
z_b = floor_t + post_h;            // boards' underside
H = lid_z + lid_t;                 // wall top
slot_z = z_b + ep[2] + plug_z - 8; // bottom of the plug opening: 1 mm under the plug
ep_holes = [for (dx = [2.54, 22.86], sy = [-1, 1]) [ep_x1 - dx, sy*10.16]];
imu_holes = [for (sx = [-1, 1], sy = [-1, 1]) [imu_cx + sx*10.16, sy*6.35]];
oy0 = in_y0 - wall; oy1 = in_y1 + wall;
feet = [for (x = [-wall - foot_l/2, in_x1 + wall + foot_l/2], y = [oy0 + foot_w/2, oy1 - foot_w/2]) [x, y]];
echo(outside = [in_x1 + 2*wall, in_y1 - in_y0 + 2*wall, H], with_feet = in_x1 + 2*wall + 2*foot_l);

module inside2d() translate([0, in_y0]) square([in_x1, in_y1 - in_y0]);
module lid_2d() translate([-ledge + lid_gap, in_y0 - ledge + lid_gap]) square([in_x1 + 2*(ledge - lid_gap), in_y1 - in_y0 + 2*(ledge - lid_gap)]);

module tray() difference() {
  union() {
    difference() {
      linear_extrude(H) offset(delta = wall) inside2d();
      translate([0, 0, floor_t]) linear_extrude(H) inside2d();
      translate([0, 0, lid_z]) linear_extrude(H) offset(delta = ledge) inside2d();           // rebate for the lid
    }
    for (p = concat(ep_holes, imu_holes)) translate([p[0], p[1], 0]) cylinder(d = post_d, h = z_b);
    for (f = feet) translate([f[0], f[1], 0]) linear_extrude(foot_t)
      hull() { translate([f[0] < 0 ? 0 : -foot_l/2 - 2, -foot_w/2]) square([foot_l/2 + 2, foot_w]); translate([f[0] < 0 ? -foot_l/2 + foot_w/2 : foot_l/2 - foot_w/2, 0]) circle(d = foot_w); }   // 2 mm into the wall
  }
  for (p = concat(ep_holes, imu_holes)) translate([p[0], p[1], z_b - pilot[1]]) cylinder(d = pilot[0], h = 10);
  for (f = feet) translate([f[0], f[1], -1]) cylinder(d = shelf_hole, h = 10);
  translate([-wall - 1, -slot_w/2, slot_z]) cube([wall + 2, slot_w, H]);                     // plug opening
  translate([imu_cx, 0, floor_t - 0.6]) linear_extrude(1) arrow2d();                          // the IMU's +x, under the board
  translate([(ep_x0 + ep_x1)/2, 0, -1]) linear_extrude(floor_t + 2) offset(r = 3) square([ep[0] - 26 - 6, 20.32 - 12], center = true);   // lightening window under the EndPoint
}
module arrow2d() polygon([[-9, -1.2], [3, -1.2], [3, -3.5], [9, 0], [3, 3.5], [3, 1.2], [-9, 1.2]]);

module boards() {
  color("seagreen") translate([ep_x0, -ep[1]/2, z_b]) cube(ep);
  color("silver") translate([0, -jack[1]/2, z_b + ep[2]]) cube(jack);
  color("royalblue") translate([imu_x0, -imu[1]/2, z_b]) cube(imu);
}

if (part == "tray") tray();
if (part == "assembly") { tray(); boards(); %translate([0, 0, lid_z]) linear_extrude(lid_t) lid_2d(); }
