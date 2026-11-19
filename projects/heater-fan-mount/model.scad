// Diesel-heater combustion-air fan mount: a 3" flexible duct from a deck vent screws onto the bottom,
// an 80 mm fan pushes the air up, and a slotted collar clamps over the heater's bottom rim with a hose clamp.
// Three printed parts, every one a flat face on the bed:
//   box     a plain rectangular tray: fan socket and, beside it, the controller pocket. Prints knob face down
//           (smooth cabin face); 45 deg gussets behind the fan hold up the back wall, no supports.
//   lid     a flat plate closing fan and pocket, the heater collar standing on it. Prints plate down.
//   spigot  a square flange the size of the fan with the threaded duct spigot. Prints flange down.
// Four M4 screws through lid, fan, box floor and spigot flange hold the stack.
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
pot_bushing = 7.5;  // M7 bushing through the wall
gland = 12.5;       // PG7 cable gland for the 12 V feed

/* [Shell] */
wall = 2;           // box sides and collar: enclosure only (0.3 inH2O is nothing); thin collar fingers flex under the clamp
front = 3;          // knob wall: prints on the bed (smooth cabin face), carries the pot nut
gusset = 20;        // back strip behind the fan: room for 45 deg gussets that hold up the back wall in print
divider = 1.6;      // fan bay to pocket: separates, carries nothing (4 lines)
floor_t = 2;        // fan sits on it; the screws clamp at the corners
plate_t = 2.5;      // lid (the whole unit hangs from it via the collar) and spigot flange (screws, nut pockets)
pocket = 40;        // controller pocket, inside, along +X beside the fan bay
r = 6;              // vertical edge rounding

$fn = 96;
e = 0.01;
W = max(fan + 2 * fit, rim_d + 2 * collar_fit) + 2 * wall;   // box width (X) and fan-bay depth: the collar never overhangs
L = W + divider + pocket;                   // box length (X): fan bay, divider, pocket
H = floor_t + fan_t;                     // box height
pocket_x = W / 2 - wall + divider + pocket / 2;           // pocket centre

include <BOSL2/std.scad>
include <BOSL2/threading.scad>

module rrect(w, d, rr = r) offset(rr) offset(-rr) square([w, d]);
sock = fan + 2 * fit;
module footprint() translate([-W / 2, -W / 2 - (front - wall)]) rrect(L, W + front - wall + gusset);
module fan_square() translate([-W / 2, -W / 2]) rrect(W, W);
module holes(d, h, z = -e) for (x = [-1, 1], y = [-1, 1]) translate([x * fan_holes / 2, y * fan_holes / 2, z]) cylinder(d = d, h = h);

module box() {
  difference() {
    linear_extrude(H) footprint();
    translate([0, 0, floor_t]) linear_extrude(H) translate([-sock / 2, -sock / 2]) square([sock, sock + gusset]);
    translate([W / 2 - wall + divider, -W / 2 + wall, floor_t]) cube([pocket, W - 2 * wall + gusset, H]);
    translate([0, 0, -e]) cylinder(d = fan_bore, h = floor_t + 2 * e);
    holes(4.4, floor_t + 2 * e);
    translate([W / 2 - wall - e, -3, H - 4]) cube([divider + 2 * e, 6, 4 + e]);                          // fan wires into the pocket
    translate([pocket_x - 8, -W / 2 - (front - wall) - e, floor_t + 3 + 1.6 + pot_z]) rotate([-90, 0, 0]) cylinder(d = pot_bushing, h = front + 2 * e);
    translate([pocket_x, W / 2 + gusset - wall - e, floor_t + fan_t / 2]) rotate([-90, 0, 0]) cylinder(d = gland, h = wall + 2 * e);
  }
  // 45 deg gussets off the side walls behind the fan: printed knob face down, the back wall bridges ~41 mm
  for (m = [0, 1]) mirror([m, 0, 0]) translate([0, 0, floor_t - e])
    linear_extrude(fan_t + e) polygon([[-sock / 2, sock / 2], [-sock / 2, sock / 2 + gusset], [-sock / 2 + gusset, sock / 2 + gusset]]);
  translate([pocket_x, -W / 2 + wall + board / 2 + 1, floor_t]) for (x = [-1, 1], y = [-1, 1])
    translate([x * board_holes / 2, y * board_holes / 2]) difference() { cylinder(d = 6, h = 3); cylinder(d = 2.5, h = 3 + e); }
}

module lid() {
  // z = 0 on the face that meets the box (the bed when printed)
  od = rim_d + 2 * collar_fit + 2 * wall;
  difference() {
    union() {
      linear_extrude(plate_t) footprint();
      cylinder(d = od, h = plate_t + rim_grip);
    }
    translate([0, 0, -e]) cylinder(d = fan_bore, h = plate_t + 2 * e);
    translate([0, 0, plate_t]) cylinder(d = rim_d + 2 * collar_fit, h = rim_grip + e);   // the rim lands on the plate
    for (i = [0:slots - 1]) rotate(i * 360 / slots + 30) translate([0, -1, plate_t + 5]) cube([od, 2, rim_grip]);
    holes(4.4, plate_t + 2 * e);
  }
}

module spigot() {
  // z = 0 on the flange face that meets the box (the bed when printed); spigot grows up (down, installed)
  difference() {
    union() {
      linear_extrude(plate_t) fan_square();
      translate([0, 0, plate_t - e]) generic_threaded_rod(d = spigot_d, l = spigot_h, pitch = pitch, profile = rib, left_handed = false, end_len = 1, anchor = BOTTOM);
    }
    translate([0, 0, -e]) cylinder(d = spigot_bore, h = plate_t + spigot_h + 2 * e);
    holes(4.4, plate_t + 2 * e);
    for (x = [-1, 1], y = [-1, 1]) translate([x * fan_holes / 2, y * fan_holes / 2, plate_t - 1.9]) cylinder(d = 8.1, h = 1.9 + e, $fn = 6);   // M4 nuts, 1.3 proud, under the stack
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
  color("#222") translate([-8, -board / 2, 1.6 + pot_z]) rotate([90, 0, 0]) cylinder(d = 14, h = 26);
}

BOX = "#e0e0dc"; LID = "#e0e0dc";
module stack(gap = 0) {
  color(BOX) box();
  translate([0, 0, floor_t + gap]) fan_dummy();
  translate([pocket_x, -W / 2 + wall + board / 2 + 1, floor_t + 3 + gap * 0.6]) board_dummy();
  color(LID) translate([0, 0, H + 2 * gap]) lid();
  color(BOX) translate([0, 0, -gap]) mirror([0, 0, 1]) spigot();
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
