// Diesel-heater combustion-air fan mount: a 3" flexible duct from a deck vent screws onto the bottom,
// an 80 mm fan pushes the air up, and a slotted collar clamps over the heater's bottom rim with a hose clamp.
// Two printed halves sandwich the fan; four M4 screws through the fan's own holes hold the stack.
// The PWM controller sits in a side pocket, out of the damp airstream, its roof formed by the upper flange.
// Origin: fan axis on Z, z = 0 at the bottom of the duct spigot, Z up as installed. Knob faces -Y (the cabin).
// Print: lower as shown (spigot on the bed); upper flipped, flange face on the bed. No supports either way.

part = "assembly";   // [lower, upper, assembly, exploded, section, plate]

/* [Fan: GDA8025 IP68, vendor drawing; thickness ~24.5 owner] */
fan = 80;
fan_t = 25;
fan_holes = 71.5;   // square, matches the v4 test print
fan_bore = 76;      // air path through both halves
fit = 0.4;          // fan to socket, each side

/* [Duct: 3" flex, threaded spigot sized off the old part (crest ~84, root ~78)] */
spigot_d = 84;
spigot_h = 25;
pitch = 6;          // UNMEASURED: the flex duct's wire pitch
thread_depth = 2.5;

/* [Heater rim: UNMEASURED - the rim gauge prints first] */
rim_d = 90;         // outside of the heater's bottom rim
rim_grip = 22;      // collar height over the rim
collar_fit = 0.6;   // collar bore over the rim, each side, before the clamp closes it
slots = 6;          // fingers the hose clamp pulls in

/* [Controller: 1803BK PWM board 32 x 32 (35 with break-off edge), holes ~26 square] */
board = 33;
board_holes = 26;
pot_z = 7;          // UNMEASURED: pot shaft centre above the board's top
pot_bushing = 7.5;  // M7 bushing through the wall
gland = 12.5;       // PG7 cable gland for the 12 V feed

/* [Shell] */
wall = 3;
flange = 4;         // upper half's plate over fan and pocket
loft = 22;          // spigot-to-square transition: keeps every slope at or under 45 deg
pocket_w = 44;      // along X
pocket_d = 40;      // out from the body along -Y

$fn = 96;
e = 0.01;
body = fan + 2 * fit + 2 * wall;       // square outside of the fan socket
seat_z = spigot_h + loft;              // fan sits here
seam_z = seat_z + fan_t;               // lower/upper split

include <BOSL2/std.scad>
include <BOSL2/threading.scad>

module sq(s) square(s, center = true);

module pocket_outline(grow = 0)
  translate([-pocket_w / 2 - grow, -body / 2 - pocket_d - grow]) square([pocket_w + 2 * grow, pocket_d + 2 * grow + body / 2]);

module lower() {
  difference() {
    union() {
      threaded_rod(d = spigot_d, l = spigot_h, pitch = pitch, $fn = 96, anchor = BOTTOM, end_len = 2);
      // circle-to-square loft, then the fan socket walls
      hull() {
        translate([0, 0, spigot_h - e]) cylinder(d = spigot_d - 2 * thread_depth, h = e);
        translate([0, 0, seat_z - e]) linear_extrude(e) sq(body);
      }
      translate([0, 0, seat_z - e]) linear_extrude(fan_t + e) sq(body);
      // controller pocket, its floor lofted down at 45 deg so it prints unsupported
      hull() {
        translate([0, 0, seat_z]) linear_extrude(fan_t) pocket_outline();
        translate([0, 0, seat_z - pocket_d]) linear_extrude(e) intersection() { pocket_outline(); translate([-pocket_w, -body / 2]) square([2 * pocket_w, body]); }
      }
    }
    // air path
    translate([0, 0, -e]) cylinder(d = spigot_d - 2 * thread_depth - 2 * wall, h = spigot_h + 2 * e);
    hull() {
      translate([0, 0, spigot_h]) cylinder(d = spigot_d - 2 * thread_depth - 2 * wall, h = e);
      translate([0, 0, seat_z - wall]) cylinder(d = fan_bore, h = e);
    }
    translate([0, 0, seat_z - wall - e]) cylinder(d = fan_bore, h = wall + 2 * e);
    // fan socket
    translate([0, 0, seat_z]) linear_extrude(fan_t + e) sq(fan + 2 * fit);
    // pocket cavity: closed from the socket except a wire notch at the seam
    translate([0, 0, seat_z]) linear_extrude(fan_t + e) intersection() {
      offset(delta = -wall) pocket_outline();
      translate([-pocket_w, -body / 2 - pocket_d]) square([2 * pocket_w, pocket_d + e]);
    }
    translate([-wall, -body / 2 - e, seam_z - 4]) cube([2 * wall + 4, wall + 2 * e, 4 + e]);
    // knob bushing and cable gland through the pocket's front wall
    translate([-8, -body / 2 - pocket_d - e, seat_z + 3 + 1.6 + pot_z]) rotate([-90, 0, 0]) cylinder(d = pot_bushing, h = wall + 2 * e);
    translate([12, -body / 2 - pocket_d - e, seat_z + fan_t / 2]) rotate([-90, 0, 0]) cylinder(d = gland, h = wall + 2 * e);
    // fan screws: clearance up, nut pockets under the seat
    for (x = [-1, 1], y = [-1, 1]) translate([x, y, 0] * fan_holes / 2) {
      translate([0, 0, seat_z - 12]) cylinder(d = 4.4, h = 13);
      translate([0, 0, seat_z - wall - 12]) cylinder(d = 8.1, h = 12, $fn = 6);
    }
  }
  // board standoffs on the pocket floor
  translate([0, -body / 2 - pocket_d / 2, seat_z]) for (x = [-1, 1], y = [-1, 1])
    translate([x, y, 0] * board_holes / 2) difference() { cylinder(d = 6, h = 3); cylinder(d = 2.5, h = 3 + e); }
}

module upper() {
  // z = 0 on the seam face (the bed when printed)
  difference() {
    union() {
      linear_extrude(flange) union() { sq(body); pocket_outline(); }
      hull() {
        translate([0, 0, flange - e]) cylinder(d = fan_bore + 2 * wall, h = e);
        translate([0, 0, flange + loft]) cylinder(d = rim_d + 2 * collar_fit + 2 * wall, h = e);
      }
      translate([0, 0, flange + loft]) cylinder(d = rim_d + 2 * collar_fit + 2 * wall, h = rim_grip);
    }
    translate([0, 0, -e]) cylinder(d = fan_bore, h = flange + 2 * e);
    hull() {
      translate([0, 0, flange]) cylinder(d = fan_bore, h = e);
      translate([0, 0, flange + loft - wall]) cylinder(d = rim_d - 6, h = e);
    }
    // rim seat: a ledge the rim lands on, then the collar bore
    translate([0, 0, flange + loft - wall]) cylinder(d = rim_d - 6, h = wall + e);
    translate([0, 0, flange + loft]) cylinder(d = rim_d + 2 * collar_fit, h = rim_grip + e);
    // fingers for the hose clamp
    for (i = [0:slots - 1]) rotate(i * 360 / slots) translate([0, -1, flange + loft + 4]) cube([rim_d, 2, rim_grip]);
    for (x = [-1, 1], y = [-1, 1]) translate([x, y, 0] * fan_holes / 2) {
      translate([0, 0, -e]) cylinder(d = 4.4, h = flange + 2 * e);
    }
  }
}

// context, not printed
module fan_dummy() color("#333") difference() {
  translate([0, 0, fan_t / 2]) cube([fan, fan, fan_t], center = true);
  translate([0, 0, -e]) cylinder(d = fan_bore - 1, h = fan_t + 2 * e);
}
module board_dummy() {
  color("#2c8a3e") translate([-board / 2, -board / 2, 0]) cube([board, board, 1.6]);
  color("#3bb") translate([-14, -12, 1.6]) cube([12, 12, 10]);
  color("#36f") translate([4, -14, 1.6]) cube([10, 28, 10]);
  color("#222") translate([-8, -board / 2, 1.6 + pot_z]) rotate([90, 0, 0]) cylinder(d = 14, h = 30);
}
module rim_dummy() color("silver", 0.5) difference() { cylinder(d = rim_d, h = 40); translate([0, 0, -e]) cylinder(d = rim_d - 2, h = 40 + 2 * e); }
module duct_dummy() color("#aaa", 0.6) translate([0, 0, -60]) difference() { cylinder(d = spigot_d + 2, h = 60 + spigot_h); translate([0, 0, -e]) cylinder(d = spigot_d - 4, h = 61 + spigot_h); }

module stack(gap = 0) {
  color("#e8a33d") lower();
  translate([0, 0, seat_z + gap]) fan_dummy();
  translate([0, -body / 2 - pocket_d / 2, seat_z + 3 + gap / 3]) board_dummy();
  color("#d8cdf0") translate([0, 0, seam_z + 2 * gap]) upper();
  translate([0, 0, seam_z + 2 * gap + flange + loft + 0.5 * gap]) rim_dummy();
  translate([0, 0, -gap]) duct_dummy();
}

if (part == "lower") lower();
else if (part == "upper") upper();
else if (part == "exploded") stack(35);
else if (part == "section") difference() { stack(); translate([0, -150, -100]) cube([300, 300, 400]); }
else if (part != "plate") stack();

// both printed parts as they sit on the bed
module plate() {
  color("#e8a33d") translate([-70, 0, 0]) lower();
  color("#d8cdf0") translate([75, 0, 0]) upper();
}
if (part == "plate") plate();
