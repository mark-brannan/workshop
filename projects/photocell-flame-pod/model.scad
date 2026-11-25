// Photocell flame pod: a small PETG shell for one LM393 photoresistor module.
// Origin: inside floor corner at the photocell end, centred across. X along the module, header end at +X.
// Print floor down, as modelled. The module sits component side up on two edge ledges and a boss.
// Potted (default): a pin on the boss locates the board; epoxy fills to just under the trimpot top, so
// board, header, leads and cable entry are sealed, the trimpot stays adjustable and the cell stands proud on its leads.
// The rim stands just over the trimpot; a snap cover (part-cover.scad) closes over it, the cell up through a hole.
// Lidded: one M3 down through the board into a nut pressed into the boss; a clear acrylic lid
// (part-lid.scad) on four corner columns, the photocell just under it.
// The cable leaves through the -Y side wall near the header-end corner, clear of the end tabs,
// the cable is held by the epoxy in the exit.

/* [Module: LM393 photoresistor, on hand (owner, caliper)] */
board_l = 31;
board_w = 14;
board_t = 1.6;        // guessed, standard PCB
hole_from_hdr = 7;    // hole centre from the header end, centred across: ~4 hole, rim 5 from the end
pot_h = 4.9;          // trimpot top above the board top (owner, caliper, 2026-11-24)
cell_h = 11.5;        // photocell top above the board top, bent up on its leads (owner)
cell_d = 5;           // guessed: common 5 mm CdS cell
cell_t = 2.5;         // guessed: cell body thickness; potting stops at its underside
fit = 0.3;            // per side, board edge to inner wall; guessed, PETG fit uncalibrated

/* [Build] */
potted = true;
lead = "solder";      // [solder, dupont]
plug_out = 15;        // dupont: board edge to the plug's back end; guessed, 14 housing + header spacer
solder_out = 9;       // solder: board edge to the end of the heatshrink over the pins; guessed
cable_d = 4.5;        // exit width for a 3-core cable; guessed, caliper the cable
pin_z = 1.27;         // header pin row above the board top; right-angle header, guessed
end_clear = 1;        // cable exit's far edge to the inner end wall

/* [Shell] */
wall = 1.6;           // 4 lines at 0.4
floor_t = 2;
corner_r = 2;         // outside vertical corners
ledge = 2;            // board underside above the floor: clears solder stubs
ledge_lip = 1.2;      // ledge reach in under the board edge: solder pads sit 1.4 in (halmet-enclosure-mount)
cell_bare = 4;        // no side ledge under the photocell end this far in: its leads' solder
seat_l = 2;           // corner seats under the photocell end's two corners, this far in; the leads' solder is mid-board, clear (owner's ask, 2026-11-24)
stop_h = 1;           // end stop over the corner seats, above the board top: the board can't slide or tip toward the cell
hdr_bare = 3;         // nor under the header end's solder row
boss_d = 7.5;
locate_d = 2.6;       // potted: pin up through the board hole; 3.4 would not go in a printed PETG shell (owner, 2026-11-24)
locate_tip = 0.6;     // 45° chamfer on the pin top, a lead-in for the hole
cell_end = 4;         // board's photocell end to the inner end wall: the cell body overhangs here
pour_above = 4;       // potted: epoxy line above the board top: over the cable, under the trimpot top (owner, 2026-11-24)
pot_clear = 0.3;      // potted: rim above the trimpot top, so the cover closes over it (owner, 2026-11-24)

/* [Snap cover, potted only] */
cover_t = 1.6;        // plate on the rim
skirt_t = 1.2;        // skirt round the outside of the walls
skirt_h = 4;          // skirt below the rim; clears the end tabs
cover_gap = 0.2;      // per side, skirt to wall; the piezo lid at 0.2 fitted snug across (owner, 2026-11-24)
catch = 0.7;          // lip reach into the wall groove; the piezo lid at ~0.6 grazed and fell off (owner, 2026-11-24); the knob
catch_x = [18, 32];   // long-wall lips mid-wall, where the skirt bows most; clear of the cable exit
catch_y = 8;          // end-wall lips, centred across; the header end's is clear of the cable notch at the -Y corner
end_catch = 0.7;      // end-wall lip reach: the short skirt is stiff near its corners; the first cover says if it wants less
cell_x_on = 1;        // photocell centre in from the board's photocell end; guessed, from the photo
cell_hole_d = 8;      // generous: the cell is bent up by hand, its position is guessed
notch_clear = 0.5;    // per side, round the cable where it passes the skirt
glyph = true;         // fire glyph on the cover's top face, outlined by a 90° V groove (owner, 2026-11-25)
glyph_h = 25;         // tip to base, along X, tip toward the header end
groove_w = 1.2;       // V groove width at the face; 90°, so half as deep

/* [Lidded only] */
nut_af = 5.5;         // M3 hex nut across flats
nut_t = 2.4;
nut_fit = 0.15;       // per side; press fit, uncalibrated
screw_d = 3.4;        // M3 clearance, through the floor
top_clear = 1;        // photocell top to the lid's underside
column_d = 4.4;       // lid-screw columns near the four inside corners
col_in = 1.9;         // column centre in from the inner wall faces: the lid hole sits 3.5 from the lid edge
pilot_d = 2.2;        // M2.5 self-tapping; calibration pending
pilot_h = 8;
lid_t = 3;            // clear acrylic, laser cut
lid_hole_d = 2.9;     // M2.5 clearance

/* [Mounting tabs] */
tabs = true;
tab_l = 8;            // past each end wall
tab_t = 2.5;
tab_hole = 3.5;       // M3 or #6 pan head

part = "shell";        // [shell, cover, assembly, none]

/* [Hidden] */
$fn = 48;
include <art/fire-glyph.scad>
lead_l = lead == "dupont" ? plug_out : solder_out;
bx0 = cell_end;                      // board's photocell end
bx1 = bx0 + board_l;                 // board's header end
exit_x = bx1 + lead_l + cable_d/2;   // cable exit centre, past the plug or heatshrink
in_l = exit_x + cable_d/2 + end_clear;
in_w = board_w + 2*fit;
out_l = in_l + 2*wall;
out_w = in_w + 2*wall;
hole_x = bx1 - hole_from_hdr;
board_z = floor_t + ledge;           // board underside
board_top = board_z + board_t;
pour_z = board_top + pour_above;           // potted: epoxy line
shell_h = potted ? board_top + pot_h + pot_clear : board_top + cell_h + top_clear;
cable_z = board_top + pin_z;               // cable centre, level with the header pins
cols = [for (x = [col_in, in_l - col_in], y = [-(in_w/2 - col_in), in_w/2 - col_in]) [x, y]];

module rrect(l, w, r) { offset(r = r) square([l - 2*r, w - 2*r], center = true); }
module outline() { translate([in_l/2, 0]) rrect(out_l, out_w, corner_r); }

module tab_2d() {
    for (s = [-1, 1]) hull() {
        translate([in_l/2 + s*(in_l/2 + wall - corner_r), 0]) square([0.02, out_w], center = true);
        translate([in_l/2 + s*(in_l/2 + wall + tab_l - out_w/4), 0]) rrect(out_w/2, out_w, out_w/4 - 0.01);
    }
}
function tab_holes() = [for (s = [-1, 1]) [in_l/2 + s*(in_l/2 + wall + tab_l/2), 0]];

module shell() {
    difference() {
        union() {
            difference() {
                linear_extrude(shell_h) outline();
                translate([0, -in_w/2, floor_t]) cube([in_l, in_w, shell_h]);
            }
            if (tabs) linear_extrude(tab_t) tab_2d();
            // edge ledges, one under each long edge of the board
            for (s = [-1, 1]) translate([bx0 + cell_bare, s > 0 ? in_w/2 - fit - ledge_lip : -in_w/2, floor_t - 0.01])
                cube([board_l - cell_bare - hdr_bare, ledge_lip + fit, ledge + 0.01]);
            // corner seats under the photocell end, each with an end stop rising from the end wall to past the board top
            for (s = [-1, 1]) translate([0, s > 0 ? in_w/2 - fit - ledge_lip : -in_w/2, floor_t - 0.01]) {
                cube([bx0 + seat_l, ledge_lip + fit, ledge + 0.01]);
                cube([bx0 - fit, ledge_lip + fit, ledge + board_t + stop_h + 0.01]);
            }
            translate([hole_x, 0, floor_t - 0.01]) cylinder(d = boss_d, h = ledge + 0.01);
            if (potted) translate([hole_x, 0, board_z - 0.01]) {
                cylinder(d = locate_d, h = board_t - locate_tip + 0.01);
                translate([0, 0, board_t - locate_tip]) cylinder(d1 = locate_d, d2 = locate_d - 2*locate_tip, h = locate_tip + 0.01);
            }
            else intersection() {   // lid-screw columns in the inside corners
                for (c = cols) translate([c[0], c[1], 0]) cylinder(d = column_d, h = shell_h);
                translate([0, -in_w/2, 0]) cube([in_l, in_w, shell_h]);
            }
        }
        if (!potted) {
            // M3 down through board and boss into a pressed-in nut; clearance on through the floor
            translate([hole_x, 0, -1]) cylinder(d = screw_d, h = board_z + 2);
            translate([hole_x, 0, board_z - nut_t]) cylinder(d = (nut_af + 2*nut_fit) / cos(30), h = nut_t + 1, $fn = 6);
            for (c = cols) translate([c[0], c[1], shell_h - pilot_h]) cylinder(d = pilot_d, h = pilot_h + 1);
        }
        // cable exit in the -Y side wall, round-bottomed, open to the rim
        translate([exit_x - cable_d/2, -in_w/2 - wall - 1, cable_z]) cube([cable_d, wall + 2, shell_h]);
        translate([exit_x, -in_w/2 + 1, cable_z]) rotate([90, 0, 0]) cylinder(d = cable_d, h = wall + 2);
        if (tabs) for (h = tab_holes()) translate([h[0], h[1], -1]) cylinder(d = tab_hole, h = tab_t + 2);
        if (potted) for (s = [-1, 1], e = [false, true]) catch_profile(s, groove = true, end = e);
    }
}

// Snap catch: a 45° V lip on the cover skirt's inside, into a 45° V groove round the wall's outside,
// one mid-wall on each of the four walls. Both faces at 45°: the cover pops off to reach the trimpot,
// and neither needs support printed either way up.
lip_z = shell_h - skirt_h + 0.3 + cover_gap + catch;   // the V's apex height
module catch_profile(s, groove, end = false) {
    c = end ? end_catch : catch;
    w = end ? out_l/2 : out_w/2;       // wall's outside face, from the shell's centre
    y0 = groove ? w + 0.01 : w + cover_gap + 0.01;
    tip = groove ? w - c - 0.1 : w - c;
    h = abs(y0 - tip);
    pts = [[s*y0, lip_z - h], [s*tip, lip_z], [s*y0, lip_z + h]];
    if (end) translate([in_l/2, catch_y/2, 0]) rotate([90, 0, 0]) linear_extrude(catch_y) polygon(pts);
    else translate([catch_x[0], 0, 0]) rotate([90, 0, 90]) linear_extrude(catch_x[1] - catch_x[0]) polygon(pts);
}

cell_x = bx0 + cell_x_on;
module cover() {
    z0 = shell_h;
    difference() {
        union() {
            translate([0, 0, z0]) linear_extrude(cover_t) offset(r = cover_gap + skirt_t) outline();
            translate([0, 0, z0 - skirt_h]) linear_extrude(skirt_h + 0.01) difference() {
                offset(r = cover_gap + skirt_t) outline();
                offset(r = cover_gap) outline();
            }
            for (s = [-1, 1], e = [false, true]) catch_profile(s, groove = false, end = e);
        }
        translate([cell_x, 0, z0 - 1]) cylinder(d = cell_hole_d, h = cover_t + 2);
        if (glyph) translate([glyph_x, 0, z0 + cover_t]) rotate(-90) glyph_groove();
        // the cable passes the skirt in a notch open at the skirt's foot
        translate([exit_x - cable_d/2 - notch_clear, -out_w/2 - cover_gap - skirt_t - 1, z0 - skirt_h - 1])
            cube([cable_d + 2*notch_clear, cover_gap + skirt_t + 2, skirt_h + 1]);
    }
}

// Fire glyph outline as a 90° V groove into the face below z = 0: a hull of two inverted cones per edge,
// each hull convex, so the mesh is the same every build. Printed face down, both groove walls are 45° chamfers.
glyph_x = (cell_x + cell_hole_d/2 + in_l + wall + cover_gap + skirt_t) / 2;   // centred in the plate past the cell hole
module glyph_groove() {
    d = groove_w / 2;
    for (path = fire_glyph_paths) for (i = [0 : len(path) - 1])
        hull() for (p = [path[i], path[(i + 1) % len(path)]])
            translate(glyph_h * p) translate([0, 0, -d]) cylinder(r1 = 0, r2 = d + 0.01, h = d + 0.01, $fn = 12);
}

// Lidded build: the lid's cut profile, the shell's outline with two holes on a diagonal over the columns.
lid_cols = [cols[0], cols[3]];
module lid_2d() {
    difference() {
        outline();
        for (c = lid_cols) translate(c) circle(d = lid_hole_d);
    }
}

// Stand-ins for the review render only: board, trimpot, photocell, header, lead and cable.
module module_standin() {
    translate([bx0, -board_w/2, board_z]) difference() {
        cube([board_l, board_w, board_t]);
        translate([board_l - hole_from_hdr, board_w/2, -1]) cylinder(d = 4, h = board_t + 2);
    }
    translate([bx0 + 12, -3, board_top]) cube([7, 6, pot_h]);
    translate([bx0 + 1, 0, board_top + cell_h - cell_t]) cylinder(d = cell_d, h = cell_t);
    for (y = [-1.5, 1.5]) translate([bx0 + 1, y, board_top]) cylinder(d = 0.5, h = cell_h - cell_t, $fn = 8);
    translate([bx1 - 2.5, -3.8, board_top]) cube([2.5 + lead_l, 7.6, 2.54]);
    translate([exit_x, 0, cable_z]) rotate([90, 0, 0]) cylinder(d = cable_d - 0.3, h = out_w/2 + 0 + 6);
}

if (part == "shell") shell();
else if (part == "cover") cover();
else if (part == "assembly") {
    shell();
    color("tan") module_standin();
    if (potted) color("lightsteelblue") translate([0, 0, 8]) cover();   // lifted 8 to show both
    if (!potted) color("lightblue", 0.5) translate([0, 0, shell_h + 8]) linear_extrude(lid_t) lid_2d();
}
