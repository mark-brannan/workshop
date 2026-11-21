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
board_t = 1.6;
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
// Hangs under a horizontal panel, plate up. The panel is the roof; the cover is a floor with one
// centre hole under a shallow arch that meets the floor at both sides. Fins under the arch keep every
// span short enough to print without support; gaps in the fins let air cross between them.
// Air comes in the hole, runs out under the arch to its two open ends, up and in.
oh_hole_d = 10;      // the floor's one opening, under the arch's crown
oh_baffle_l = 27;    // y; leaves 4.9 at each end for the air to turn
oh_floor_t = 1.2;   // six 0.2 layers; the wall variant's cover keeps cover_t
oh_arch_t = 0.6;    // three 0.2 layers at the crown
oh_fin_t = 0.8;     // two 0.4 lines
oh_fin_pitch = 5.5;  // x; four fins, the middle two run through the hole as vanes
oh_fin_gap = 3;      // y; one gap in each fin either side of the hole
oh_fin_gap_y = 7;    // gap centres
oh_exit_y = 15.5;    // cable exit: arched hole in the +x long wall, toward the Qwiic end, routed rearward
oh_exit_w = 5;
oh_exit_h = 6;       // from the tie block's top, where the cable rides, to the arch's crown
oh_tie_w = 4;        // tunnel width, 0.2 of it sunk into the long wall so no face is shared; tie anchor inside, against the exit: a block on the plate, its tunnel along y under the cable; ties to 3.6 wide
oh_tie_h = 1.6;      // tunnel height, arch crown included
oh_tie_roof = 1.2;   // block above the tunnel's crown; the cable lies on it
oh_tie_len = 2.4;    // block along y, the tie's run under the cable
oh_tie_side = 0.8;   // block inboard of the tunnel; the long wall is its other side
oh_tie_flare = 0.6;  // chamfer round each tunnel mouth, so the tie finds its way in
oh_insert_d = 3.2;   // M2 heat-set insert hole; insert size a guess (3.2 x 4) until the bag or calipers say
oh_insert_l = 4;
oh_insert_extra = 0.5; // hole past the insert's end, for the plastic it pushes down
oh_screw_d = 2.4;    // M2 clearance in the cover's floor
oh_cboss_d = 6.2;      // cover bosses round the inserts
oh_round_r = 1.5;    // every outside convex edge but the bed's; 2.5 or more would reach the cable exit
oh_pad_d = 6;        // board seat: insert pads under two holes on one diagonal
oh_lip = 1.2;        // seat ledge reaches this far in under the board's edge
oh_seat_wall = 1.2;  // seat walls round the board, flush with its face; stop it turning on two screws
oh_qwiic_w = 10;   // gap in each short seat wall for the Qwiic plug, on the centre line; 8 was a little tight

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

oh_boss_x = in_w/2 - oh_cboss_d/2 + 0.5;
oh_boss_y = house_h/2 - wall - oh_cboss_d/2 + 0.3;
oh_bosses = [[-oh_boss_x, oh_boss_y], [oh_boss_x, -oh_boss_y]];      // one diagonal; the other corner is free for the cable
oh_cover_holes = [for (b = oh_bosses) [b[0], -b[1]]];                // the cover's screw holes, on the other diagonal: they line up with the body's once the cover is turned over
oh_posts = [[-hole_dy/2, hole_dx/2], [hole_dy/2, -hole_dx/2]];      // board screws, on the same diagonal
oh_seat_z = plate_t + pad_h;                                   // board's back
oh_tie_cx = in_w/2 - oh_tie_w/2 + 0.2;                         // tunnel centre: 0.2 into the long wall
oh_tie_top = plate_t + oh_tie_h + oh_tie_roof;                // 5.8: the cable's bed at the exit
oh_fillet_r = roof_y - (oh_exit_y + oh_tie_len/2);             // 1.7: wall-foot fillets; inside the end wall it starts at the tunnel's far mouth
oh_pocket = [board_w + 2*fit, board_l + 2*fit];

// The board's seat: a ledge under its edges, insert pads under two holes, walls to its face
// with a gap in each short wall for the Qwiic plug.
module oh_seat() {
    linear_extrude(oh_seat_z) difference() {
        square(oh_pocket, center = true);
        square([board_w - 2*oh_lip, board_l - 2*oh_lip], center = true);
    }
    for (p = oh_posts) translate([p[0], p[1], 0]) cylinder(d = oh_pad_d, h = oh_seat_z);
    linear_extrude(oh_seat_z + board_t) difference() {
        square(oh_pocket + 2*[oh_seat_wall, oh_seat_wall], center = true);
        square(oh_pocket, center = true);
        square([oh_qwiic_w, oh_pocket[1] + 2*oh_seat_wall + 1], center = true);
    }
}

// The tie tunnel's section about its centre line: sides, then a half ellipse to the crown.
module tie_tunnel2d() { hull() { translate([-oh_tie_w/2, 0]) square([oh_tie_w, oh_tie_h/2]); translate([0, oh_tie_h/2]) scale([oh_tie_w/2, oh_tie_h/2]) circle(r = 1); } }
// A hole with a round top: straight sides, then a half circle, so it prints without support.
module arch2d(w, h) { hull() { translate([-w/2, 0]) square([w, eps]); translate([0, h - w/2]) circle(d = w); translate([-w/2, 0]) square([w, h - w/2]); } }

// Fillet along x for len, against a wall face at y = 0 (wall in -y), on a floor at z = 0.
// A true quarter-round profile, 32 facets. Its centre sits 0.05 in from both tangents, so the arc
// crosses into floor and wall at a shallow angle instead of touching them: smooth, and manifold.
module fillet2d(r = oh_fillet_r, n = 32, d = 0.05) { polygon(concat([for (i = [0:n]) let(a = 270 - 90*i/n) [r - d + r*cos(a), r - d + r*sin(a)]], [[-d, -d]])); }
module foot_fillet(len, r = oh_fillet_r) { rotate([90, 0, 90]) linear_extrude(len) fillet2d(r); }

// The outside without its cavity: plate, house, and the foot fillets onto the end flanges, all sharp,
// run past the bed and the cover's seat so those edges stay square.
module oh_envelope() {
    translate([0, 0, -2]) linear_extrude(plate_t + 2) rrect(plate_w, plate_h, corner_r);
    translate([-plate_w/2, -house_h/2, -2]) cube([plate_w, house_h, face_z + 4]);
    for (m = [0, 1]) mirror([0, m, 0]) translate([-plate_w/2, house_h/2, plate_t]) foot_fillet(plate_w);
}

// The envelope with every convex edge rounded by one rolling ball (a morphological opening:
// erode by the ball, then grow by it), so plate edge, house corners and foot fillets blend tangent.
module oh_rounded_envelope(r = oh_round_r) {
    box = [plate_w + 10, plate_h + 10, face_z + 14];
    minkowski() {
        difference() {
            translate([0, 0, face_z/2]) cube(box, center = true);
            minkowski() {
                difference() { translate([0, 0, face_z/2]) cube(box + [4, 4, 4], center = true); oh_envelope(); }
                sphere(r = r, $fn = 48);
            }
        }
        sphere(r = r, $fn = 48);
    }
}

// The interior's fillet in one piece: the interior box less a box with its bottom and vertical
// edges rounded r, so foot fillets meet at each corner in a sphere octant and the wall corners
// above are rounded too. Centres 0.05 in from the faces, as foot_fillet's, keeps it manifold.
module inner_fillet(r = oh_fillet_r, d = 0.05) {
    cx = in_w/2 - (r - d); cy = roof_y - (r - d); h = face_z - plate_t;
    difference() {
        translate([-in_w/2, -roof_y, plate_t - eps]) cube([in_w, 2*roof_y, h]);   // eps short of the walls' tops: flush tops make a non-manifold edge
        translate([0, 0, plate_t]) hull() for (sx = [-1, 1], sy = [-1, 1]) translate([sx*cx, sy*cy, r - d]) {
            sphere(r = r, $fn = 64);
            cylinder(r = r, h = h, $fn = 64);
        }
    }
}

module oh_insert_hole(top) { translate([0, 0, top - oh_insert_l - oh_insert_extra]) cylinder(d = oh_insert_d, h = oh_insert_l + oh_insert_extra + 1); }

module overhead_body() {
    difference() {
        intersection() {
        union() {
            linear_extrude(plate_t) rrect(plate_w, plate_h, corner_r);
            linear_extrude(face_z) difference() {                                                     // four walls
                square([plate_w, house_h], center = true);
                square([in_w, house_h - 2*wall], center = true);
            }
            for (b = oh_bosses) translate([b[0], b[1], plate_t - eps]) cylinder(d = oh_cboss_d, h = face_z - plate_t + eps);
            oh_seat();
            translate([in_w/2 - oh_tie_w - oh_tie_side, oh_exit_y - oh_tie_len/2, plate_t - eps])
                cube([oh_tie_w + oh_tie_side + eps, oh_tie_len, oh_tie_h + oh_tie_roof + eps]);   // tie block, against the long wall
            inner_fillet();                                                                                   // every inside foot and corner rounded; the +y end's turns the tie back up
            for (m = [0, 1]) mirror([0, m, 0]) translate([-plate_w/2, house_h/2, plate_t]) foot_fillet(plate_w, oh_fillet_r + 0.5);   // oversize: the envelope trims it to size; matching surfaces pinch the mesh
        }
        oh_rounded_envelope();                                                                            // the outside's convex edges rounded
        }
        mount_holes();
        translate([plate_w/2 + 1, oh_exit_y, oh_tie_top]) rotate([90, 0, -90]) linear_extrude(wall + 2) arch2d(oh_exit_w, oh_exit_h);   // cable exit, sill level with the block
        translate([oh_tie_cx, oh_exit_y + oh_tie_len/2 + 0.05, plate_t - eps]) rotate([90, 0, 0]) linear_extrude(oh_tie_len + 0.1) tie_tunnel2d();   // tie tunnel along y
        intersection() {                                                                                  // its mouths chamfered, inward only: the cove beyond stays whole
            for (sy = [-1, 1]) translate([oh_tie_cx, oh_exit_y + sy*oh_tie_len/2, plate_t - eps]) rotate([90, 0, 0]) mirror([0, 0, sy < 0 ? 1 : 0]) hull() {
                translate([0, 0, -0.05]) linear_extrude(0.06) offset(delta = oh_tie_flare) tie_tunnel2d();
                translate([0, 0, -0.05]) linear_extrude(oh_tie_flare + 0.05) tie_tunnel2d();
            }
            translate([in_w/2 - oh_tie_w - oh_tie_flare - 1, 0, plate_t - eps]) cube([oh_tie_w + oh_tie_flare + 1.2, house_h, oh_tie_top]);
        }
        for (b = oh_bosses) translate(b) oh_insert_hole(face_z);
        for (p = oh_posts) translate(p) oh_insert_hole(oh_seat_z);
    }
}

oh_arch_w = in_w - 2*fit;
oh_arch_h = face_z - baffle_z;                                   // 4.4: the crown's outside sits where the old baffle's back did
oh_arch_r = (pow(oh_arch_w/2, 2) + pow(oh_arch_h, 2)) / (2*oh_arch_h);
oh_arch_c = oh_arch_r - oh_arch_h;                               // circle centre, below the floor
oh_fin_x = [for (i = [-1.5 : 1 : 1.5]) i*oh_fin_pitch];
oh_fin_segs = [[-oh_baffle_l/2 + eps, -oh_fin_gap_y - oh_fin_gap/2], [-oh_fin_gap_y + oh_fin_gap/2, oh_fin_gap_y - oh_fin_gap/2], [oh_fin_gap_y + oh_fin_gap/2, oh_baffle_l/2 - eps]];   // ends short of the arch's by eps: coplanar ends make a non-manifold edge

// Profiles in (x, height above the floor's inner face); oh_extrude stands them on the floor along y.
module oh_arch_profile() {
    intersection() {
        translate([0, -oh_arch_c]) difference() { circle(r = oh_arch_r, $fn = 360); circle(r = oh_arch_r - oh_arch_t, $fn = 360); }
        translate([-oh_arch_w/2, -eps]) square([oh_arch_w, face_z]);
    }
}
module oh_fin_profile(h0 = -eps) {
    intersection() {
        translate([0, -oh_arch_c]) circle(r = oh_arch_r - oh_arch_t + 0.05, $fn = 360);
        for (x = oh_fin_x) translate([x - oh_fin_t/2, h0]) square([oh_fin_t, face_z]);
    }
}
module oh_extrude(y0, y1) { translate([0, y1, face_z]) rotate([90, 0, 0]) mirror([0, 1, 0]) linear_extrude(y1 - y0) children(); }

module overhead_cover() {
    difference() {
        translate([0, 0, face_z]) linear_extrude(oh_floor_t) rrect(plate_w, house_h, oh_round_r);    // floor, its corners the house's
        translate([0, 0, face_z - 1]) cylinder(d = oh_hole_d, h = oh_floor_t + 2);
        for (b = oh_cover_holes) translate([b[0], b[1], face_z - 1]) cylinder(d = oh_screw_d, h = oh_floor_t + 2);
    }
    oh_extrude(-oh_baffle_l/2, oh_baffle_l/2) oh_arch_profile();
    for (s = oh_fin_segs) oh_extrude(s[0], s[1]) oh_fin_profile();
    intersection() {                                                                                  // the fins carry on down through the hole to the bed as vanes
        oh_extrude(-oh_hole_d/2, oh_hole_d/2) oh_fin_profile(-oh_floor_t);
        translate([0, 0, face_z - eps]) cylinder(d = oh_hole_d + 0.1, h = oh_floor_t + eps);
    }
}

module overhead_cover_print() { translate([0, 0, face_z + oh_floor_t]) rotate([180, 0, 0]) overhead_cover(); }

module overhead_assembly() { overhead_body(); overhead_cover(); }

if (part == "body") body();
if (part == "overhead_body") overhead_body();
if (part == "overhead_cover") overhead_cover_print();
if (part == "overhead_assembly") overhead_assembly();
if (part == "overhead_section") difference() { overhead_assembly(); translate([1, -50, -1]) cube([50, 100, 50]); }
if (part == "cover") cover_print();
if (part == "assembly") assembly();
if (part == "section") difference() { assembly(); translate([1, -50, -1]) cube([50, 100, 50]); }
