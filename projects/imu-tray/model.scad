// Tray and cover for the ICM-20948 IMU and a QwiicBus EndPoint on a horizontal shelf, mid-boat, dry.
// X along the tray: the RJ45 jack faces -x, its mouth at x = 0; the IMU sits at the +x end. Y across, Z up.
// The cover drops over both boards and the same four screws hold cover and tray to the shelf.
// Print the tray as shown (floor down). The cover part file flips it, roof down: no supports for either.
part = "tray";       // tray | cover | assembly

/* [Floor and walls] */
floor_t = 2.5;
wall = 2;
roof_t = 2;
in_y0 = -15;         // inside, -y side: board edge 12.7 plus room
in_y1 = 24;          // inside, +y side: room for the Qwiic plug on the EndPoint's +y edge and its cable
in_h = 24;           // floor top to roof underside; jack top is about 21 (jack height a guess)
end_gap = 3;         // IMU's far edge to the +x wall

/* [Boards] (Eagle .brd files; parts.md) */
ep = [44.45, 25.4, 1.6];    // SparkFun QwiicBus EndPoint 16988: length (x), width (y), thickness
jack_over = 9.7;            // the jack overhangs the board's -x end (photo, lux-tube-cap)
jack = [23.2, 16.5, 13.5];  // jack length, width, height above the board (height a guess)
imu = [25.4, 17.78, 1.6];   // Adafruit ICM-20948 4554
board_gap = 16;             // EndPoint's +x end to the IMU's -x end: the IMU's Qwiic plug and the cable's bend
post_h = 5;                 // board underside above the floor: clears solder on the boards' backs

/* [Fasteners] (insert holes a guess: no calibration yet) */
ep_insert = [4.0, 5.5];     // M3 heat-set insert: hole, depth
imu_insert = [3.6, 4.5];    // M2.5 brass heat-set insert; brass or nylon screws near the magnetometer
ep_post_d = 7;
imu_post_d = 6;

/* [Mounting] */
ear_hole = 4.8;      // #8 / M4 wood screw, generous for a printed hole
ear_r = 5.5;
ear_t = 3;           // each of tray and cover
ear_xs = [6, 88];

/* [Cable] */
slot_w = 19;         // plug opening in the -x wall, open at the bottom; plug 11.7 wide, boot wider
slot_top = 23;       // above the floor top
tie_x = -30;         // zip-tie saddle for the cat5, so a tug pulls the tray, not the jack
saddle = [7, 16, 11];

/* [Vents] */
vent_w = 2;
vent_h = 9;
vent_pitch = 6;

/* [Hidden] */
$fn = 48;
ep_x0 = jack_over;                 // EndPoint's -x end
ep_x1 = ep_x0 + ep[0];
imu_x0 = ep_x1 + board_gap;
imu_cx = imu_x0 + imu[0]/2;
in_x1 = imu_x0 + imu[0] + end_gap;
// outer footprint of tray floor and cover
ox0 = -wall; ox1 = in_x1 + wall; oy0 = in_y0 - wall; oy1 = in_y1 + wall;
z_b = floor_t + post_h;            // boards' underside
ep_holes = [for (dx = [2.54, 22.86], sy = [-1, 1]) [ep_x1 - dx, sy*10.16]];
imu_holes = [for (sx = [-1, 1], sy = [-1, 1]) [imu_cx + sx*10.16, sy*6.35]];
ears = [for (x = ear_xs) for (y = [oy0 - ear_r + 1, oy1 + ear_r - 1]) [x, y]];
echo(length = ox1 - tie_x + saddle[0]/2, width = oy1 - oy0, height = floor_t + in_h + roof_t);

module footprint() translate([ox0, oy0]) square([ox1 - ox0, oy1 - oy0]);
module ear2d() for (e = ears) translate(e) hull() { circle(r = ear_r); translate([-ear_r, e[1] < 0 ? ear_r - 1 : -ear_r - 1]) square([2*ear_r, 2]); }

module tray() difference() {
  union() {
    linear_extrude(floor_t) { footprint(); ear2d(); translate([tie_x, -saddle[1]/2]) square([ox0 - tie_x + 1, saddle[1]]); }
    for (p = ep_holes) translate([p[0], p[1], 0]) cylinder(d = ep_post_d, h = z_b);
    for (p = imu_holes) translate([p[0], p[1], 0]) cylinder(d = imu_post_d, h = z_b);
    translate([tie_x - saddle[0]/2, -saddle[1]/2, 0]) cube(saddle);
  }
  for (p = ep_holes) translate([p[0], p[1], z_b - ep_insert[1]]) cylinder(d = ep_insert[0], h = 10);
  for (p = imu_holes) translate([p[0], p[1], z_b - imu_insert[1]]) cylinder(d = imu_insert[0], h = 10);
  for (e = ears) translate([e[0], e[1], -1]) cylinder(d = ear_hole, h = 10);
  // saddle: cable groove on top, tie slot through it underneath
  translate([tie_x, 0, saddle[2]]) rotate([0, 90, 0]) cylinder(d = 7, h = saddle[0] + 2, center = true);
  translate([tie_x - 2, -20, saddle[2] - 7]) cube([4, 40, 2.2]);
  // arrow on the floor top, pointing +x: the IMU's x axis (the ICM-20948 board's own arrow sets which way is which)
  translate([imu_cx, 0, floor_t - 0.6]) linear_extrude(1) arrow2d();
  translate([(ep_x0 + ep_x1)/2, 0, -1]) linear_extrude(floor_t + 2) offset(r = 3) square([ep[0] - 26 - 6, 20.32 - 6 - 6], center = true);   // lightening window under the EndPoint
}
module arrow2d() polygon([[-9, -1.2], [3, -1.2], [3, -3.5], [9, 0], [3, 3.5], [3, 1.2], [-9, 1.2]]);

module cover() difference() {
  union() {
    translate([0, 0, floor_t]) linear_extrude(in_h + roof_t) footprint();
    for (e = ears) hull() {               // ears with a 45 degree wedge back to the wall: no overhang printed roof-down
      translate([e[0], e[1], floor_t]) cylinder(r = ear_r, h = ear_t);
      translate([e[0] - ear_r, e[1] < 0 ? oy0 : oy1 - 0.01, floor_t]) cube([2*ear_r, 0.01, ear_t + abs(e[1] - (e[1] < 0 ? oy0 : oy1)) + ear_r]);
    }
  }
  translate([0, in_y0, floor_t - 1]) cube([in_x1, in_y1 - in_y0, in_h + 1]);
  for (e = ears) translate([e[0], e[1], 0]) cylinder(d = ear_hole, h = 100);
  for (e = ears) translate([e[0], e[1], floor_t + ear_t]) cylinder(r = ear_r + 0.3, h = 100);   // screw-head room above the ear
  translate([ox0 - 1, -slot_w/2, floor_t - 1]) cube([wall + 2, slot_w, slot_top + 1]);          // plug opening, open at the bottom
  for (x = [ep_x0 + 4 : vent_pitch : in_x1 - 6], y = [oy0 - 1, in_y1 - 1])                     // vertical vent slots, both long walls, low
    if (x < ear_xs[0] - ear_r - 2 || x > ear_xs[0] + ear_r + 2) if (x < ear_xs[1] - ear_r - 2 || x > ear_xs[1] + ear_r + 2)
      translate([x, y, floor_t + 2]) cube([vent_w, wall + 2, vent_h]);
  translate([imu_cx, 0, floor_t + in_h + roof_t - 0.6]) linear_extrude(1) arrow2d();               // same arrow on the roof, for lining up on the shelf
}

module boards() {
  color("seagreen") translate([ep_x0, -ep[1]/2, z_b]) cube(ep);
  color("silver") translate([0, -jack[1]/2, z_b + ep[2]]) cube(jack);
  color("royalblue") translate([imu_x0, -imu[1]/2, z_b]) cube(imu);
}

if (part == "tray") tray();
if (part == "cover") translate([0, 0, floor_t + in_h + roof_t]) mirror([0, 0, 1]) cover();
if (part == "assembly") { tray(); boards(); %cover(); }
