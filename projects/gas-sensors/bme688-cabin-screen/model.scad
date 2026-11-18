// Cabin screen for one Adafruit BME688 board (25.4 x 17.78, holes 20.32 x 12.7), open to the air.
// Two prints: a body that screws to the panelling or a DIN clip, and a cover with a baffle behind it.
// Air comes in a slot that faces down, rises between cover and baffle, turns over the baffle's top
// and falls onto the chip. Nothing outside has a straight line to the board.
// On the wall +Y is up and Z is out from the panel. Print the body as shown, back on the bed.
// The cover prints face down (part-cover.scad); the baffle bridges its three ribs.
part = "body";       // body, cover, assembly, section; overhead_body, overhead_cover, overhead_assembly, overhead_section

/* [Back plate] */
plate_w = 32;        // x
plate_h = 62;        // y
plate_t = 3;
corner_r = 2;
mount_pitch = 51;    // two holes on the centre line: the DIN clip's heat inserts, or wood screws
mount_d = 3.4;       // M3 clearance
csk_d = 6.5;         // countersink at the front face

/* [Housing] */
house_h = 40;        // y, centred on the plate
depth = 16;          // z, front of the cover
wall = 1.6;
roof_over = 1;       // roof past the cover's face, with a lip that holds the cover's top edge
lip_h = 1;
floor_y = -15;       // underside of the chamber floor; the skirt below it shelters the inlet and the cable
notch_x = 8;         // cable notch in the floor, off centre, clear of the lower mount screw
notch_w = 5;
notch_d = 5;

/* [Board] */
board_l = 25.4;      // Adafruit board file; long edge upright
board_w = 17.78;
hole_dx = 20.32;
hole_dy = 12.7;
board_y = 4;         // board centre; leaves 4 mm under it for the Qwiic plug
pad_h = 2;
pad_d = 5;
pilot_d = 2.1;       // M2.5 self-tapping into the print

/* [Cover] */
cover_t = 1.6;
baffle_z = 10;       // baffle's back face; the chamber is plate_t to here
baffle_t = 1.2;
baffle_top = 14;     // y; the roof's underside is at 18.4, so air turns through 4.4
fit = 0.3;           // baffle to side wall, each side
rib_w = 1.2;
boss_d = 4.6;         // two cover screws, in the skirt
boss_y = -17.5;
cover_screw_d = 2.9; // M2.5 clearance

/* [Overhead variant] */
// Hangs under a horizontal panel, plate up. The panel is the roof; the cover is a floor with a row of
// holes and a baffle above it. Air comes in the holes, runs along peaked channels to the baffle's two
// ends, up and in. The channels' 45-degree roofs print without support or bridges, floor on the bed.
oh_hole_d = 5;       // one hole under each channel; four of them open as much as one 10 mm hole
oh_baffle_l = 27;    // y; leaves 4.9 at each end for the air to turn
oh_chan_n = 4;       // channels between floor and baffle, running along y
oh_chan_pitch = 6.9; // x; each channel is 6.4 wide at the floor, peaked 3.2 up at 45 degrees
win_y = 15;          // cable window in one long wall, beside the Qwiic plug

/* [Hidden] */
$fn = 48;
eps = 0.01;
in_w = plate_w - 2*wall;                 // 28.8 between the side walls
face_z = depth - cover_t;                // 14.4: the side walls' fronts, where the cover seats
roof_y = house_h/2 - wall;               // 18.4: roof underside
boss_x = in_w/2 - boss_d/2 + 0.5;
posts = [for (sx = [-1, 1], sy = [-1, 1]) [sx*hole_dy/2, board_y + sy*hole_dx/2]];

module rrect(l, w, r) { hull() for (sx = [-1, 1], sy = [-1, 1]) translate([sx*(l/2 - r), sy*(w/2 - r)]) circle(r = r); }

module mount_holes() {
    for (sy = [-1, 1]) translate([0, sy*mount_pitch/2, -1]) {
        cylinder(d = mount_d, h = plate_t + 2);
        translate([0, 0, plate_t + 1 - (csk_d - mount_d)/2]) cylinder(d1 = mount_d, d2 = csk_d + eps, h = (csk_d - mount_d)/2 + eps);
    }
}

module body() {
    difference() {
        union() {
            linear_extrude(plate_t) rrect(plate_w, plate_h, corner_r);
            for (sx = [-1, 1]) translate([sx*(plate_w/2 - wall/2) - wall/2, -house_h/2, plate_t - eps]) cube([wall, house_h, face_z - plate_t + eps]);   // side walls
            translate([-plate_w/2, roof_y, plate_t - eps]) cube([plate_w, wall, depth + roof_over - plate_t + eps]);                                    // roof
            translate([-plate_w/2, roof_y - lip_h, depth + 0.2]) cube([plate_w, lip_h + eps, roof_over - 0.2]);                                         // lip
            translate([-in_w/2 - eps, floor_y, plate_t - eps]) cube([in_w + 2*eps, wall, baffle_z - 0.2 - plate_t + eps]);                              // chamber floor
            for (sx = [-1, 1]) translate([sx*boss_x, boss_y, plate_t - eps]) cylinder(d = boss_d, h = face_z - plate_t + eps);                           // cover bosses
            for (p = posts) translate([p[0], p[1], plate_t - eps]) cylinder(d = pad_d, h = pad_h + eps);                                                 // board pads
        }
        mount_holes();
        translate([notch_x - notch_w/2, floor_y - 1, baffle_z - 0.2 - notch_d]) cube([notch_w, wall + 2, notch_d + 1]);       // cable notch, open to the front
        for (sx = [-1, 1]) translate([sx*boss_x, boss_y, face_z - 8]) cylinder(d = pilot_d, h = 9);
        for (p = posts) translate([p[0], p[1], 1]) cylinder(d = pilot_d, h = plate_t + pad_h);
    }
}

module cover() {
    difference() {
        translate([-plate_w/2, -house_h/2, face_z]) cube([plate_w, house_h/2 + roof_y - 0.2, cover_t]);                       // face, tucked under the roof
        for (sx = [-1, 1]) translate([sx*boss_x, boss_y, face_z - 1]) cylinder(d = cover_screw_d, h = cover_t + 2);
    }
    translate([-in_w/2 + fit, floor_y, baffle_z]) cube([in_w - 2*fit, baffle_top - floor_y, baffle_t]);                        // baffle
    for (x = [-in_w/2 + fit, -rib_w/2, in_w/2 - fit - rib_w])                                                                 // ribs, above the bosses
        translate([x, floor_y + 1, baffle_z + baffle_t - eps]) cube([rib_w, baffle_top - floor_y - 1, face_z - baffle_z - baffle_t + 2*eps]);
}

module cover_print() { translate([0, 0, depth]) rotate([180, 0, 0]) cover(); }

module assembly() { body(); cover(); }

oh_boss_y = house_h/2 - wall - boss_d/2 + 0.3;
oh_bosses = [[-boss_x, oh_boss_y], [boss_x, -oh_boss_y]];      // one diagonal; the other corner has the cable window
oh_posts = [for (sx = [-1, 1], sy = [-1, 1]) [sx*hole_dy/2, sy*hole_dx/2]];

module overhead_body() {
    difference() {
        union() {
            linear_extrude(plate_t) rrect(plate_w, plate_h, corner_r);
            translate([0, 0, plate_t - eps]) linear_extrude(face_z - plate_t + eps) difference() {      // four walls
                square([plate_w, house_h], center = true);
                square([in_w, house_h - 2*wall], center = true);
            }
            for (b = oh_bosses) translate([b[0], b[1], plate_t - eps]) cylinder(d = boss_d, h = face_z - plate_t + eps);
            for (p = oh_posts) translate([p[0], p[1], plate_t - eps]) cylinder(d = pad_d, h = pad_h + eps);
        }
        mount_holes();
        translate([in_w/2 - 1, win_y - notch_w/2, plate_t]) cube([wall + 2, notch_w, notch_d]);         // cable window
        for (b = oh_bosses) translate([b[0], b[1], face_z - 8]) cylinder(d = pilot_d, h = 9);
        for (p = oh_posts) translate([p[0], p[1], 1]) cylinder(d = pilot_d, h = plate_t + pad_h);
    }
}

oh_chan_h = face_z - baffle_z - baffle_t;                       // 3.2: floor to the baffle's face
oh_chan_x = [for (i = [0 : oh_chan_n - 1]) (i - (oh_chan_n - 1)/2) * oh_chan_pitch];

module overhead_cover() {
    difference() {
        union() {
            translate([-plate_w/2, -house_h/2, face_z]) cube([plate_w, house_h, cover_t]);              // floor
            translate([-in_w/2 + fit, -oh_baffle_l/2, baffle_z]) cube([in_w - 2*fit, oh_baffle_l, face_z - baffle_z + eps]);   // baffle, solid to the floor
        }
        for (x = oh_chan_x) {
            translate([x, oh_baffle_l/2 + eps, face_z + eps]) rotate([90, 0, 0])                          // channel: 45-degree peak, open at both ends
                linear_extrude(oh_baffle_l + 2*eps) polygon([[-oh_chan_h, 0], [oh_chan_h, 0], [0, -oh_chan_h]]);
            translate([x, 0, face_z - eps]) cylinder(d = oh_hole_d, h = cover_t + 1);   // starts at the floor: no pocket in the channel walls
        }
        for (b = oh_bosses) translate([b[0], b[1], face_z - 1]) cylinder(d = cover_screw_d, h = cover_t + 2);
    }
}

module overhead_cover_print() { translate([0, 0, depth]) rotate([180, 0, 0]) overhead_cover(); }

module overhead_assembly() { overhead_body(); overhead_cover(); }

if (part == "body") body();
if (part == "overhead_body") overhead_body();
if (part == "overhead_cover") overhead_cover_print();
if (part == "overhead_assembly") overhead_assembly();
if (part == "overhead_section") difference() { overhead_assembly(); translate([1, -50, -1]) cube([50, 100, 50]); }
if (part == "cover") cover_print();
if (part == "assembly") assembly();
if (part == "section") difference() { assembly(); translate([1, -50, -1]) cube([50, 100, 50]); }
