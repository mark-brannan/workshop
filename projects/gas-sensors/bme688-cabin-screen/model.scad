// Overhead cabin screen for one Adafruit BME688 board (25.4 x 17.78, holes 20.32 x 12.7), open to the air.
// Hangs under a horizontal panel, plate up. Two prints: a body and a cover whose arch faces OUT, away from the board.
// Print the body plate down (part-overhead-body.scad) and the cover floor down (part-overhead-cover.scad); the cover
// goes onto the body just as it sits on the bed, arch outward. It never goes on arch-in: the arch doesn't fit inside.
part = "overhead_assembly";   // overhead_body, overhead_cover, overhead_assembly, overhead_section

/* [Back plate] */
plate_w = 32;        // x
plate_h = 62;        // y
plate_t = 3;
mount_pitch = 51;    // two holes on the centre line: the DIN clip's heat inserts, or wood screws
mount_d = 3.4;       // M3 clearance
csk_d = 6.5;         // countersink at the front face

/* [Housing] */
house_h = 40;        // y, centred on the plate
depth = 16;          // z, front of the cover
wall = 1.6;

/* [Board] */
board_l = 25.4;      // Adafruit board file; long edge upright
board_w = 17.78;
hole_dx = 20.32;
hole_dy = 12.7;
pad_h = 2;
board_t = 1.6;

/* [Cover] */
cover_t = 1.6;
baffle_z = 10;       // sets the arch's height: face_z - baffle_z = 4.4 (name left from the old inner baffle)
baffle_t = 1.2;
fit = 0.3;           // arch narrower than the inside by this, each side

/* [Overhead] */
// Hangs under a horizontal panel, plate up. The panel is the roof; the cover is the floor, with one
// centre hole and a shallow arch over it on the OUTSIDE, meeting the floor at both sides: a drip shield.
// Fins under the arch keep every span short enough to print without support; gaps in the fins let air
// cross between them. Air comes in at the arch's open ends, runs under it to the hole, and up into the box.
oh_hole_d = 10;      // the floor's one opening, under the arch's crown
oh_baffle_l = 27;    // y; the arch's length
oh_floor_t = 1.2;   // six 0.2 layers
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
oh_pilot_d = 2.2;    // M2.5 self-tapping pilot; printed holes come out small, so the first print is the test
oh_pilot_l = 4.5;   // blind; an M2.5 x 6 through the board (1.6) reaches 0.1 short of the bottom
oh_screw_d = 2.9;    // M2.5 clearance in the cover's floor
oh_cboss_d = 6.2;      // cover bosses round the pilot holes
oh_round_r = 1.5;    // every outside convex edge but the bed's; 2.5 or more would reach the cable exit
oh_pad_d = 6;        // board seat: pads under the four holes
oh_lip = 1.2;        // seat ledge reaches this far in under the board's edge
oh_seat_wall = 1.2;  // seat walls round the board, flush with its face; stop it turning on two screws
oh_qwiic_w = 10;     // gap in each short seat wall for the Qwiic plug, on the centre line; 8 was a little tight

/* [Hidden] */
// Facet count comes from the radius ($fa/$fs), not a fixed $fn. The part-*.scad files `use` this file, which
// drops its top-level $fa/$fs, so each printed part has a wrapper that sets them again.
fa = 6;
fs = 0.4;
$fa = fa;
$fs = fs;
eps = 0.01;
in_w = plate_w - 2*wall;                 // 28.8 between the side walls
face_z = depth - cover_t;                // 14.4: the side walls' fronts, where the cover seats
roof_y = house_h/2 - wall;               // 18.4: roof underside

module rrect(l, w, r) { hull() for (sx = [-1, 1], sy = [-1, 1]) translate([sx*(l/2 - r), sy*(w/2 - r)]) circle(r = r); }

module mount_holes() {
    for (sy = [-1, 1]) translate([0, sy*mount_pitch/2, -1]) {
        cylinder(d = mount_d, h = plate_t + 2);
        translate([0, 0, plate_t + 1 - (csk_d - mount_d)/2]) cylinder(d1 = mount_d, d2 = csk_d + eps, h = (csk_d - mount_d)/2 + eps);
    }
}

oh_boss_x = in_w/2 - oh_cboss_d/2 + 0.5;
oh_boss_y = house_h/2 - wall - oh_cboss_d/2 + 0.3;
oh_bosses = [[-oh_boss_x, oh_boss_y], [oh_boss_x, -oh_boss_y]];      // one diagonal; the other corner is free for the cable
oh_cover_holes = [for (b = oh_bosses) [b[0], -b[1]]];                // overhead_cover() draws the cover upside down (arch toward the plate), so its holes are on the other diagonal; overhead_cover_print() turns it over, arch out, holes over the towers
oh_posts = [for (sx = [-1, 1], sy = [-1, 1]) [sx*hole_dy/2, sy*hole_dx/2]];   // board screws, all four holes
oh_seat_z = plate_t + pad_h;                                   // board's back
oh_tie_cx = in_w/2 - oh_tie_w/2 + 0.2;                         // tunnel centre: 0.2 into the long wall
oh_tie_top = plate_t + oh_tie_h + oh_tie_roof;                // 5.8: the cable's bed at the exit
oh_fillet_r = roof_y - (oh_exit_y + oh_tie_len/2);             // 1.7: wall-foot fillets; inside the end wall it starts at the tunnel's far mouth
oh_pocket = [board_w + 2*fit, board_l + 2*fit];

// The board's seat: a ledge under its edges, pads under the four holes, walls to its face
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

// The outside, its convex edges rolled by one ball of r: plate edge, house corners and foot fillets blend
// tangent. The section in y-z (plate, house, foot fillets r oh_fillet_r, convex corners r) is swept along x
// with r roundovers at both ends: one polyhedron, the same mesh every build. It replaced a double
// minkowski() whose mesh changed from run to run and was rarely closed (1 build in 6 on 2026-11-23).
// Runs past the bed and the cover's seat so those edges stay square. The plate's plan corners come out r.
// The section in y-z offset s inward: straight sides move in by s, convex arcs (r) shrink about their
// centres and the concave foot fillets (rf) grow about theirs, so every offset has the same points.
function oh_sect(s, r, rf, n = 12) = let(
    py = plate_h/2, hy = house_h/2, zb = -2, zt = face_z + 2, pt = plate_t, rc = max(r - s, 0.01), rv = rf + s,
    arcs = [[[-py + r, zb + r], rc, 180, 270], [[py - r, zb + r], rc, 270, 360], [[py - r, pt - r], rc, 0, 90],
            [[hy + rf, pt + rf], rv, 270, 180], [[hy - r, zt - r], rc, 0, 90], [[-hy + r, zt - r], rc, 90, 180],
            [[-hy - rf, pt + rf], rv, 0, -90], [[-py + r, pt - r], rc, 90, 180]])
    [for (a = arcs) for (i = [0:n]) let(t = a[2] + (a[3] - a[2])*i/n) a[0] + a[1]*[cos(t), sin(t)]];

module oh_rounded_envelope(r = oh_round_r, rf = oh_fillet_r, n = 12) {
    ends = [for (j = [0:n]) let(a = 90*j/n) [r*(1 - cos(a)), r*(1 - sin(a))]];      // [distance in from the end, offset]
    layers = concat([for (e = ends) [-plate_w/2 + e[0], e[1]]], [for (j = [n:-1:0]) [plate_w/2 - ends[j][0], ends[j][1]]]);
    m = len(oh_sect(0, r, rf)); nl = len(layers);
    pts = [for (l = layers) for (p = oh_sect(l[1], r, rf)) [l[0], p[0], p[1]]];
    sides = [for (l = [0:nl - 2], i = [0:m - 1]) let(a = l*m + i, b = l*m + (i + 1)%m, c = (l + 1)*m + (i + 1)%m, d = (l + 1)*m + i)
             each [[a, c, b], [a, d, c]]];
    polyhedron(pts, concat(sides, [[for (i = [0:m - 1]) i], [for (i = [m - 1:-1:0]) (nl - 1)*m + i]]));
}

// The interior's fillet in one piece: the interior box less a box with its bottom and vertical
// edges rounded r, so foot fillets meet at each corner in a sphere octant and the wall corners
// above are rounded too. Centres 0.05 in from the faces keep it manifold.
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

module oh_pilot_hole(top) { translate([0, 0, top - oh_pilot_l]) cylinder(d = oh_pilot_d, h = oh_pilot_l + 1); }

module overhead_body() {
    difference() {
        intersection() {
        union() {
            // Plate and walls run 0.5 past the envelope, so every outside face is the envelope's alone:
            // a face of each lying in one plane pinched the STL into edges shared by four faces.
            linear_extrude(plate_t) rrect(plate_w + 1, plate_h + 1, oh_round_r + 0.5);
            linear_extrude(face_z) difference() {                                                     // four walls
                square([plate_w + 1, house_h + 1], center = true);
                square([in_w, house_h - 2*wall], center = true);
            }
            for (b = oh_bosses) translate([b[0], b[1], plate_t - eps]) cylinder(d = oh_cboss_d, h = face_z - plate_t + eps);
            oh_seat();
            translate([in_w/2 - oh_tie_w - oh_tie_side, oh_exit_y - oh_tie_len/2, plate_t - eps])
                cube([oh_tie_w + oh_tie_side + eps, oh_tie_len, oh_tie_h + oh_tie_roof + eps]);   // tie block, against the long wall
            inner_fillet();                                                                                   // every inside foot and corner rounded; the +y end's turns the tie back up
            for (m = [0, 1]) mirror([0, m, 0]) translate([-plate_w/2 - 1, house_h/2 - wall/2, plate_t - eps])
                cube([plate_w + 2, wall/2 + oh_fillet_r + 1, oh_fillet_r + 1]);   // a block over the outside foot fillets: the envelope cuts their surface. A second curved surface here, even an oversize one, left slivers at the corners that pinch the STL
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
        for (b = oh_bosses) translate(b) oh_pilot_hole(face_z);
        for (p = oh_posts) translate(p) oh_pilot_hole(oh_seat_z);
    }
}

oh_arch_w = in_w - 2*fit;
oh_arch_h = face_z - baffle_z;                                   // 4.4: the arch's crown, outside, above the floor's inner face
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

// Drawn upside down, arch pointing at the plate: a construction pose, never the assembled one.
// The cover as made and as fitted is overhead_cover_print(): floor down, arch up and outward.
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

module overhead_cover_print() { $fa = fa; $fs = fs; translate([0, 0, face_z + oh_floor_t]) rotate([180, 0, 0]) overhead_cover(); }

module overhead_body_print() { $fa = fa; $fs = fs; overhead_body(); }

module overhead_assembly() { overhead_body(); translate([0, 0, face_z]) overhead_cover_print(); }  // the cover as fitted: straight off the bed onto the walls' fronts, arch outward

if (part == "overhead_body") overhead_body_print();
if (part == "overhead_cover") overhead_cover_print();
if (part == "overhead_assembly") overhead_assembly();
if (part == "overhead_section") difference() { overhead_assembly(); translate([1, -50, -1]) cube([50, 100, 50]); }
