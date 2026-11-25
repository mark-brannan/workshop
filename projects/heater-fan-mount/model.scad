// Diesel-heater combustion-air fan mount: a 3" flexible duct from a deck vent screws onto the bottom,
// an 80 mm fan pushes the air up, and a slotted collar clamps over the heater's bottom rim with a hose clamp.
// Three printed parts, every one a flat face on the bed:
//   box     a plain rectangular tray: fan socket and, beside it, the controller pocket. Prints floor down, open
//           top up. The knob hole bridges its own small crown; single-line 45 deg webs from both sides, cut out
//           after, hold up the crown of the gland hole.
//   lid     a flat plate closing fan and pocket, the heater collar standing on it. Prints plate down.
//   spigot  a square flange that drops into the fan socket, under the fan, with the threaded duct spigot hanging
//           out through the floor: the box's underside stays flat. Prints flange down.
// The fan's own four M4 countersunk screws come up through box floor, spigot flange, fan and lid; heads flush in
// the floor; nuts on top of the lid, each sunk 1 mm in a hex pocket inside a low mound, level with the mound's top.
// Origin: fan axis on Z, z = 0 on the box's underside, Z up as installed. Knob faces -Y (the cabin);
// the 12 V gland is on the back (+Y), against the bulkhead, out of sight.

part = "assembly";   // [box, lid, spigot, assembly, exploded, section, plate]

/* [Fan: GDA8025 IP68, vendor drawing; thickness ~24.5 owner] */
fan = 80;
fan_t = 25;
fan_holes = 71.5;   // square, matches the v4 test print
fan_bore = 76;      // air path
fit = 0.4;          // fan to socket, each side

/* [Duct: 3" flex, wire helix right-hand, pitch 15-19 (owner's estimate: residential HVAC or marine blower hose)] */
duct_id = 76.2;     // 3" nominal, at the wire
pitch = 15;         // ESTIMATE, owner: 15-19; measure 10 turns at the boat
rib_h = 2;          // helical rib that sits between the duct's wire turns
spigot_h = 25;
spigot_wall = 2;     // tube inside the duct: holds shape, no load beyond the duct's own grip
spigot_d = duct_id - 0.2 + 2 * rib_h;   // rib crest; the core is a snug slip inside the wire
spigot_bore = duct_id - 0.2 - 2 * spigot_wall;
// rib profile in pitch units: x along the axis, y radial from the crest; 45 deg flanks print upright
rib = [[-1/2, -rib_h / pitch], [-(1.5 + rib_h) / pitch, -rib_h / pitch], [-1.5 / pitch, 0], [1.5 / pitch, 0], [(1.5 + rib_h) / pitch, -rib_h / pitch], [1/2, -rib_h / pitch]];

/* [Heater rim: UNMEASURED - the rim gauge prints first] */
rim_d = 75.4;       // outside of the heater's bottom rim: ~76 bore was near a friction fit on the old part (owner)
rim_grip = 22;      // collar height over the rim
collar_fit = 0.3;   // collar bore 76.0 over the rim
slots = 6;          // fingers the hose clamp pulls in

/* [Controller: 1803BK PWM board 32 x 32 (35 with break-off edge), holes ~26 square] */
board = 33;
board_holes = 26;
pot_z = 7;          // UNMEASURED: pot shaft centre above the board's top
pot_bushing = 7.5;  // M7 bushing through the wall; the pot is centred on the board (owner), so knob, board and pocket share one X
knob_d = 15.5;      // knob skirt, owner: the LED window stays clear of it
led_x = 8.5;        // indicator LED from the module's right edge, seen from the cabin (owner)
led_win = 3;        // LED window aperture, square to the face; its 3 mm top bridges, then the fill covers it
led_shift = 0.5;    // window centre from the LED along X: outboard, clear of the knob
led_chamfer = 1;    // 45 deg chamfer round the window's inside edge: funnels the clear fill and keys the plug against pushing out
gland_web = 0.45;   // one extrusion line, 45 deg, from each side of the gland hole to its crown; cut out after printing
gland = 16;         // PG9 cable gland for the 12 V feed (thread 15.2, printed hole oversize); was PG7 12.5

/* [Screws: the fan's own M4 countersunk; owner: 35 overall, 32.5 threaded] */
screw_l = 35;
head_d = 7.3;       // countersink at the bed: the head is 6.7 across (owner), plus 0.6 since printed holes come undersize
nut_h = 2.8;        // M4 hex nut, on top of the lid (owner)
nut_sink = 1;       // hex pocket into the lid's top: holds the nut against turning, one screwdriver from below
nut_d = 8.5;        // pocket across the hex's corners: a 7 mm nut, plus allowance since printed holes come undersize
mound_d = 26;       // each nut sits in a low mound: its foot, toward the middle of the lid
mound_top = 10;     // its flat top, level with the top of the nut; the sides sweep down concave and meet the plate flat
lid_round = 0.6;    // roundover on the lid plate's top edge; the mounds fall to it, so the edge is one height all round
step = 0.1;         // curved faces are built in slabs this thick, finer than a layer
flange_t = 2;       // spigot flange, clamped flat between fan and floor
flange_fit = 0.2;   // flange to fan socket, each side
thread_gap = 0.6;   // floor hole to the spigot's rib crest, each side

/* [Shell] */
wall = 2;           // box sides and collar: enclosure only (0.3 inH2O is nothing); thin collar fingers flex under the clamp
front = 3;          // knob wall: prints on the bed (smooth cabin face), carries the pot nut
divider = 1.6;      // fan bay to pocket: separates, carries nothing (4 lines)
floor_t = 2;        // fan sits on it; the screws clamp at the corners
plate_t = 2.5;      // lid: the whole unit hangs from it via the collar
pocket = 40;        // controller pocket, inside, along +X beside the fan bay: board 33 plus 3.5 each side
r = 6;              // vertical edge rounding
bed_chamfer = 0.8;  // 45 deg chamfer round the box's bed edge: takes up elephant's foot, a clean line at the spigot seam
fillet = 2;         // pocket floor and front corners
boss_fillet = 1.2;  // flare at the foot of each board standoff

$fn = 96;
e = 0.01;
W = max(fan + 2 * fit, rim_d + 2 * collar_fit) + 2 * wall;   // box width (X) and fan-bay depth: the collar never overhangs
L = W + divider + pocket;                   // box length (X): fan bay, divider, pocket
fan_z = floor_t + flange_t;              // the fan sits on the spigot's flange
H = fan_z + fan_t;                       // box height
pocket_x = W / 2 - wall + divider + pocket / 2;           // pocket centre
board_top = floor_t + 3 + 1.6;
led_win_x = pocket_x + board / 2 - led_x + led_shift;
led_win_z = board_top + 1;

include <BOSL2/std.scad>
include <BOSL2/threading.scad>
include <BOSL2/rounding.scad>

module rrect(w, d, rr = r) offset(rr) offset(-rr) square([w, d]);
sock = fan + 2 * fit;
// box outline: knob wall (front, -Y) is thicker than the rest
module footprint() translate([-W / 2, -W / 2 - (front - wall)]) rrect(L, W + front - wall);
// a round hole through a vertical wall, axis along Y, cut from y = 0 toward -Y
module hole_y(d, h) rotate([90, 0, 0]) linear_extrude(h) circle(d = d);
module fan_square() translate([-W / 2, -W / 2]) rrect(W, W);
// 90 deg countersinks for the screw heads, flush with the box's underside (z = 0), 45 deg walls opening onto the bed
csk_h = (head_d - 4.4) / 2;
module countersinks() for (x = [-1, 1], y = [-1, 1]) translate([x * fan_holes / 2, y * fan_holes / 2, -e]) cylinder(d1 = head_d + 2 * e, d2 = 4.4, h = csk_h + e);
module holes(d, h, z = -e) for (x = [-1, 1], y = [-1, 1]) translate([x * fan_holes / 2, y * fan_holes / 2, z]) cylinder(d = d, h = h);

module box() {
  px0 = W / 2 - wall + divider; py0 = -W / 2 + wall; py1 = W / 2 - wall;
  difference() {
    hull() { linear_extrude(e) offset(-bed_chamfer) footprint(); translate([0, 0, bed_chamfer]) linear_extrude(H - bed_chamfer) footprint(); }
    translate([-sock / 2, -sock / 2, floor_t]) cube([sock, sock, H]);
    // controller pocket: filleted floor and corners
    translate([0, 0, floor_t]) offset_sweep(round_corners([[px0, py0], [px0 + pocket, py0], [px0 + pocket, py1], [px0, py1]],
      method = "circle", radius = fillet, $fn = 32), height = H, bottom = os_circle(r = fillet), steps = 8);
    // the threaded spigot passes down through; the floor's corners stop its flange. Kept inside the socket's walls.
    translate([0, 0, -e]) linear_extrude(floor_t + 2 * e) intersection() { circle(d = spigot_d + 2 * thread_gap); square(sock, center = true); }
    holes(4.4, floor_t + 2 * e);
    countersinks();
    // fan wires into the pocket: a notch in the divider, open at the top
    translate([W / 2 - wall - e, -3, H - 4]) cube([divider + 2 * e, 6, 4 + e]);
    translate([pocket_x, -W / 2 + wall + e, board_top + pot_z]) hole_y(pot_bushing, front + 2 * e);
    // LED window: square aperture through the knob wall, chamfered at 45 deg on its inside
    translate([led_win_x, -W / 2 + wall + e, led_win_z]) rotate([90, 0, 0]) {
      linear_extrude(front + 2 * e) square(led_win, center = true);
      // runs 0.5 on into the aperture so the two cuts cross rather than share an edge
      translate([0, 0, -e]) linear_extrude(led_chamfer + e + 0.5, scale = (led_win - 1) / (led_win + 2 * (led_chamfer + e)))
        square(led_win + 2 * (led_chamfer + e), center = true);
    }
    translate([pocket_x, W / 2 + e, floor_t + fan_t / 2]) hole_y(gland, wall + 2 * e);
  }
  // gland hole's print support: a line rising at 45 deg from each side of the hole to its crown, the full wall deep
  translate([pocket_x, W / 2 - e, floor_t + fan_t / 2]) rotate([90, 0, 0]) linear_extrude(wall - 2 * e) intersection() {
    circle(d = gland + 0.4);
    for (m = [0, 1]) mirror([m, 0]) translate([-gland / 4, gland / 4]) rotate(45) square([gland, gland_web], center = true);
  }
  // board standoffs: round, flared foot, pilot hole
  translate([pocket_x, -W / 2 + wall + board / 2 + 1, floor_t - e]) for (x = [-1, 1], y = [-1, 1])
    translate([x * board_holes / 2, y * board_holes / 2]) difference() {
      offset_sweep(circle(d = 6, $fn = 48), height = 3 + e, bottom = os_circle(r = -boss_fillet), steps = 6);
      translate([0, 0, -e]) cylinder(d = 2.5, h = 3 + 3 * e, $fn = 24);
    }
}

// the plate, its top edge rounded over
module lid_plate() {
  linear_extrude(plate_t - lid_round) footprint();
  for (k = [0 : round(lid_round / step) - 1]) let (zr = (k + 1) * step)
    translate([0, 0, plate_t - lid_round + k * step - e]) linear_extrude(step + e) offset(delta = -(lid_round - sqrt(max(0, lid_round * lid_round - zr * zr)))) footprint();
}
// a nut mound: height falls off as the square of the distance from its foot, so it meets the plate flat (concave).
// Toward the plate's edge the foot is the edge itself, so the mound adds nothing to the edge's height.
module mound(x, y) {
  h = nut_h - nut_sink;
  run = W / 2 - fan_holes / 2 - lid_round - mound_top / 2 - 0.05;
  for (k = [0 : round(h / step) - 1]) let (q = sqrt((k + 1) * step / h))
    translate([0, 0, plate_t + k * step - e]) linear_extrude(step + e) intersection() {
      translate([x, y]) circle(d = mound_top + (mound_d - mound_top) * (1 - q));
      offset(delta = -(lid_round + run * q)) footprint();
    }
}

module lid() {
  // z = 0 on the face that meets the box (the bed when printed)
  od = rim_d + 2 * collar_fit + 2 * wall;
  difference() {
    union() {
      lid_plate();
      cylinder(d = od, h = plate_t + rim_grip);
      for (x = [-1, 1], y = [-1, 1]) mound(x * fan_holes / 2, y * fan_holes / 2);
    }
    translate([0, 0, -e]) cylinder(d = fan_bore, h = plate_t + 2 * e);
    translate([0, 0, plate_t]) cylinder(d = rim_d + 2 * collar_fit, h = rim_grip + e);   // the rim lands on the plate
    for (i = [0:slots - 1]) rotate(i * 360 / slots + 30) translate([0, -1, plate_t + 5]) cube([od, 2, rim_grip]);
    holes(4.4, plate_t + 2 * e);
    for (x = [-1, 1], y = [-1, 1]) translate([x * fan_holes / 2, y * fan_holes / 2, plate_t - nut_sink]) cylinder(d = nut_d, h = nut_h + e, $fn = 6);
  }
}

module flange_square() { w = sock - 2 * flange_fit; translate([-w / 2, -w / 2]) rrect(w, w, 1); }
module spigot() {
  // z = 0 on the flange face under the fan (the bed when printed); the spigot grows up (down, installed), through the floor
  difference() {
    union() {
      linear_extrude(flange_t) flange_square();
      translate([0, 0, flange_t - e]) generic_threaded_rod(d = spigot_d, l = floor_t + spigot_h, pitch = pitch, profile = rib, left_handed = false, end_len = 1, anchor = BOTTOM);
    }
    translate([0, 0, -e]) cylinder(d = spigot_bore, h = flange_t + floor_t + spigot_h + 2 * e);
    holes(4.4, flange_t + 2 * e);
    // a head taller than the floor is thick runs on into the flange's floor face
    if (csk_h > floor_t) translate([0, 0, fan_z]) rotate([180, 0, 0]) countersinks();
  }
}

// context, not printed
module fan_dummy() color("#2b2b2b") difference() {
  translate([0, 0, fan_t / 2]) cube([fan, fan, fan_t], center = true);
  translate([0, 0, -e]) cylinder(d = fan_bore - 1, h = fan_t + 2 * e);
}
module board_dummy() {
  color("#2c8a3e") translate([-board / 2, -board / 2, 0]) cube([board, board, 1.6]);
  color("#3aa") translate([-14, -12, 1.6]) cube([12, 12, 10]);
  color("#36c") translate([4, -14, 1.6]) cube([10, 28, 10]);
  color("#222") translate([0, -board / 2, 1.6 + pot_z]) rotate([90, 0, 0]) cylinder(d = 14, h = 26);
}

BOX = "#e0e0dc"; LID = "#e0e0dc";
module stack(gap = 0) {
  color(BOX) box();
  translate([0, 0, fan_z + gap]) fan_dummy();
  translate([pocket_x, -W / 2 + wall + board / 2 + 1, floor_t + 3 + gap * 0.6]) board_dummy();
  color(LID) translate([0, 0, H + 2 * gap]) lid();
  color(BOX) translate([0, 0, fan_z + gap / 2]) rotate([180, 0, 0]) spigot();   // turned over, as a hand does it: a mirror would draw the thread left-hand
}

module plate() {
  color(BOX) translate([0, 0, 0]) box();
  color(LID) translate([W + 20, 0, 0]) lid();
  color(BOX) translate([-W - 10, 0, 0]) spigot();
}

if (part == "box") box();
else if (part == "lid") lid();
else if (part == "spigot") spigot();
else if (part == "exploded") stack(30);
else if (part == "section") difference() { stack(); translate([0, -200, -100]) cube([400, 400, 400]); }
else if (part == "plate") plate();
else if (part == "back") stack();
else if (part == "assembly") stack();
