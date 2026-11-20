// Box for the HALPI2-end QwiicBus EndPoint, just outside the HALPI2. Coated or potted: either works.
// The floor is solid and every mounting screw is outside the cavity, so a potted board never comes out.
// Two ears at mid-length take the preferred DIN clip's two M3 screws (51 apart) or two wood screws when
// it hangs upside down under a panel. The walls jog inward at the ears so a screw head clears them.
// X along the board: the RJ45 mouth sits in a window in the +x wall, the jack's own body closing it.
// The Qwiic sockets face +-y, 12.7 from the board's -x end; their cables leave by notches in the rims.
// Pot to below the notches. Print as shown, floor down, no supports.
part = "box";        // box | assembly

/* [Box] */
floor_t = 2.5;
wall = 2.5;
in_x0 = -1.5;        // the board's -x end to the -x wall
in_half_y = 20;      // inside half-width: board 12.7 plus 7.3 for each Qwiic plug and its cable's turn upward
lid_z = 23.1;        // floor bottom to the rebate: jack top plus 1.5 (jack height a guess)

/* [Lid rebate, for a coated board] */
lid_t = 3;
ledge = 1.2;

/* [Board] (SparkFun 16988 board file, parts.md) */
ep = [44.45, 25.4, 1.6];
jack_over = 9.7;     // jack past the board's +x end (photo, lux-tube-cap)
jack_w = 16.5;
jack_h = 13.5;       // above the board's top: a guess
post_h = 4;          // board underside above the floor: clears the jack's through-hole tails
ep_pilot = 2.6;      // M3 tapped into the post (board holes 3.2)
pilot_depth = 5;
post_d = 6;

/* [Openings] */
win_fit = 0.3;       // jack to window, each side
notch_w = 5;         // Qwiic cable notch in each long wall's rim
notch_z = 14;        // notch bottom above the floor bottom; the resin stops under it
qwiic_x = 12.7;      // the sockets' x on the board (board file)

/* [Mounting] */
mount_pitch = 51;    // DIN clip (Printables 420009) heat inserts; any two wood screws when hung under a panel
ear_d = 11;
ear_t = 4;
ear_hole = 4.2;      // M3 pan head into the clip, or a #6 / 3.5 wood screw; K2 holes run small
jog = 3;             // wall stepped in at each ear, so a head up to 12 across clears it
jog_l = 14;          // along x

/* [Hidden] */
$fn = 48;
in_x1 = ep[0] + jack_over;        // the jack's mouth at the +x wall's inside face
ex = (in_x0 + in_x1)/2;           // ears at mid-length
z_b = floor_t + post_h;           // board underside
z_t = z_b + ep[2];                // board top
H = lid_z + lid_t;
holes = [for (x = [2.54, 22.86], sy = [-1, 1]) [x, sy*10.16]];
echo(outside = [in_x1 - in_x0 + 2*wall, 2*(in_half_y + wall), H], over_ears = mount_pitch + ear_d);

module inside2d() difference() {
  translate([in_x0, -in_half_y]) square([in_x1 - in_x0, 2*in_half_y]);
  for (sy = [-1, 1]) translate([ex - jog_l/2, sy > 0 ? in_half_y - jog : -in_half_y - 1]) square([jog_l, jog + 1]);
}

module box() difference() {
  union() {
    difference() {
      linear_extrude(H) offset(delta = wall) inside2d();
      translate([0, 0, floor_t]) linear_extrude(H) inside2d();
      translate([0, 0, lid_z]) linear_extrude(H) offset(delta = ledge) inside2d();
    }
    for (p = holes) translate([p[0], p[1], 0]) cylinder(d = post_d, h = z_b);
    for (sy = [-1, 1]) linear_extrude(ear_t) hull() {
      translate([ex, sy*mount_pitch/2]) circle(d = ear_d);
      translate([ex - ear_d/2, sy > 0 ? in_half_y - jog : -in_half_y + jog - 1]) square([ear_d, 1]);
    }
  }
  for (p = holes) translate([p[0], p[1], z_b - pilot_depth]) cylinder(d = ep_pilot, h = 10);
  for (sy = [-1, 1]) translate([ex, sy*mount_pitch/2, -1]) cylinder(d = ear_hole, h = ear_t + 2);
  translate([in_x1 - 1, -jack_w/2 - win_fit, z_t]) cube([wall + 2, jack_w + 2*win_fit, jack_h + win_fit]);   // RJ45 window
  for (sy = [-1, 1]) translate([qwiic_x - notch_w/2, sy > 0 ? in_half_y - 1 : -in_half_y - wall - 1, notch_z]) cube([notch_w, wall + 2, H]);
}

module boards() {
  color("seagreen") translate([0, -ep[1]/2, z_b]) cube(ep);
  color("silver") translate([ep[0] + jack_over - 23.2, -jack_w/2, z_t]) cube([23.2, jack_w, jack_h]);
  for (sy = [-1, 1]) color("black") translate([qwiic_x - 3, sy > 0 ? 12.7 - 4 : -12.7 - 0.5, z_t]) cube([6, 4.5, 3]);
}

if (part == "box") box();
if (part == "assembly") { box(); boards(); }
