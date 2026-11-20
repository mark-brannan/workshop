// Box for the HALPI2-end QwiicBus EndPoint, just outside the HALPI2. Coated or potted: either works.
// The floor is solid and every mounting screw is outside the cavity, so a potted board never comes out.
// Two ears at mid-length take the preferred DIN clip's two M3 screws (51 apart) or two wood screws when
// it hangs upside down under a panel. The body is the board's width plus its walls.
// X along the board: the RJ45 mouth sits in a window in the +x wall, the jack's own body closing it.
// The HALPI2 lead enters the -x wall to a 2.54-pitch screw terminal on the board's header row.
// The Qwiic plugs go in from outside, through small holes in the long walls. Print floor down, no slicer
// supports: a breakaway tree in the RJ45 window holds its top; snip its trunk at the sill.
part = "box";        // box | assembly

/* [Box] */
floor_t = 2.5;
wall = 2;
in_x0 = -3.5;        // the screw terminal overhangs the board's -x end (a guess)
in_half_y = 13.1;    // board 12.7 plus 0.4
lid_z = 23.1;        // floor bottom to the rebate: jack top plus 1.5 (jack height a guess)

/* [Lid rebate, for a coated board] */
lid_t = 3;
ledge = 1;

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
qwiic_x = 12.7;      // the sockets' x on the board; mouths 0.48 inside its edges (board file)
qwiic_hole = [7, 3.6]; // plug 6 wide, socket 2.9 tall (JST-SH, a guess); bottom at the board's top
term_y = 1.27;       // header row centre: GND 3V3 SDA SCL at y -2.54..5.08 (board file, x 1.27)
lead_d = 5.5;        // the HALPI2 lead, a round 4-core about 4 across
lead_z = 4;          // lead axis above the board's top: the terminal's wire entry (a guess)

/* [Print] */
prop_line = 0.5;     // breakaway prop wall: one nozzle line
prop_gap = 0.2;      // one layer between prop and window top, so it lets go

/* [Mounting] */
mount_pitch = 51;    // DIN clip (Printables 420009) heat inserts; any two wood screws when hung under a panel
ear_d = 11;
ear_t = 4;
ear_hole = 4.2;      // M3 pan head into the clip, or a #6 / 3.5 wood screw; K2 holes run small

/* [Hidden] */
$fn = 48;
in_x1 = ep[0] + jack_over;        // the jack's mouth at the +x wall's inside face
ex = (in_x0 + in_x1)/2;           // ears at mid-length
z_b = floor_t + post_h;           // board underside
z_t = z_b + ep[2];                // board top
H = lid_z + lid_t;
holes = [for (x = [2.54, 22.86], sy = [-1, 1]) [x, sy*10.16]];
echo(outside = [in_x1 - in_x0 + 2*wall, 2*(in_half_y + wall), H], over_ears = mount_pitch + ear_d);

module inside2d() translate([in_x0, -in_half_y]) square([in_x1 - in_x0, 2*in_half_y]);

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
      translate([ex - ear_d/2, sy > 0 ? in_half_y : -in_half_y - 1]) square([ear_d, 1]);
    }
  }
  for (p = holes) translate([p[0], p[1], z_b - pilot_depth]) cylinder(d = ep_pilot, h = 10);
  for (sy = [-1, 1]) translate([ex, sy*mount_pitch/2, -1]) cylinder(d = ear_hole, h = ear_t + 2);
  translate([in_x1 - 1, -jack_w/2 - win_fit, z_t]) cube([wall + 2, jack_w + 2*win_fit, jack_h + win_fit]);   // RJ45 window
  for (sy = [-1, 1]) translate([qwiic_x, sy > 0 ? in_half_y + wall + 1 : -in_half_y + 1, z_t]) rotate([90, 0, 0]) linear_extrude(wall + 2) gable(qwiic_hole[0], qwiic_hole[1]);
  translate([in_x0 + 1, term_y, z_t + lead_z]) rotate([0, -90, 0]) cylinder(d = lead_d, h = wall + 2);   // HALPI2 lead
}

// Openings in upright walls end in a 45 degree roof, so no top is a flat overhang.
module gable(w, h) polygon([[-w/2, 0], [w/2, 0], [w/2, h], [0, h + w/2], [-w/2, h]]);

// A breakaway tree in the wall's thickness: a trunk on the sill, 45 degree branches meeting the window top
// every 2 mm or so, one layer below it. Snip the trunk at the sill and pull the tree out.
module window_prop() {
  T = jack_h + win_fit - prop_gap;
  side = jack_w/2 + win_fit - prop_gap;                       // outer tips rest one layer off the side walls
  rise = prop_line*sqrt(2);
  translate([in_x1 + wall - 0.2, 0, z_t]) rotate([90, 0, -90]) linear_extrude(wall - 0.4) {
    translate([-prop_line/2, -0.2]) square([prop_line, T + 0.2]);
    for (s = [-1, 1], d = [side/4 : side/4 : side]) polygon([[0, T - d - rise], [0, T - d], [s*d, T], [s*d, T - rise]]);
  }
}

module boards() {
  color("seagreen") translate([0, -ep[1]/2, z_b]) cube(ep);
  color("silver") translate([ep[0] + jack_over - 23.2, -jack_w/2, z_t]) cube([23.2, jack_w, jack_h]);
  for (sy = [-1, 1]) color("black") translate([qwiic_x - 3, sy > 0 ? 12.7 - 4.6 : -12.7, z_t]) cube([6, 4.6, 2.9]);
  color("limegreen") translate([in_x0, term_y - 5.08, z_t]) cube([7, 10.16, 8.5]);   // 4-way 2.54 terminal
}

if (part == "box") { box(); window_prop(); }
if (part == "assembly") { box(); boards(); }
