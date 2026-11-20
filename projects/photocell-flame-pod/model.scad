// Photocell flame pod: a small PETG tray for one LM393 photoresistor module.
// Origin: inside floor corner at the photocell end, centred across. X along the module, header end at +X.
// Print floor down, as modelled. The module sits component side up on two edge ledges and a boss.
// Potted (default): a pin on the boss locates the board; epoxy fills to the photocell's body, so
// board, trimpot, leads and cable entry are sealed and the cell's face stands proud.
// Lidded: one M3 down through the board into a nut pressed into the boss; a clear acrylic lid
// (part-lid.scad) on four corner columns, the photocell just under it.
// The cable leaves through the -Y side wall near the header-end corner, clear of the end tabs,
// and an outside tie block under the exit takes a cable tie.

/* [Module: LM393 photoresistor, on hand (owner, caliper)] */
board_l = 31;
board_w = 14;
board_t = 1.6;        // guessed, standard PCB
hole_from_hdr = 7;    // hole centre from the header end, centred across: ~4 hole, rim 5 from the end
pot_h = 4.6;          // trimpot top above the board top (owner)
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

/* [Tray] */
wall = 1.6;           // 4 lines at 0.4
floor_t = 2;
corner_r = 2;         // outside vertical corners
ledge = 2;            // board underside above the floor: clears solder stubs
ledge_lip = 1.2;      // ledge reach in under the board edge: solder pads sit 1.4 in (halmet-enclosure-mount)
cell_bare = 4;        // no ledge under the photocell end this far in: its leads' solder
hdr_bare = 3;         // nor under the header end's solder row
boss_d = 7.5;
locate_d = 3.4;       // potted: pin up through the ~4 board hole
cell_end = 4;         // board's photocell end to the inner end wall: the cell body overhangs here
pour_rim = 0.5;       // potted: wall above the epoxy line, a dam for the pour

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

/* [Mounting tabs and cable tie] */
tabs = true;
tab_l = 8;            // past each end wall
tab_t = 2.5;
tab_hole = 3.5;       // M3 or #6 pan head
tie_w = 4;            // tunnel under the tie block, along X; ties to 3.6 wide
tie_h = 1.8;
tie_side = 1.2;       // block either side of the tunnel
tie_out = 3.5;        // block out from the side wall, the cable's run over it

part = "tray";        // [tray, assembly, none]

/* [Hidden] */
$fn = 48;
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
pour_z = board_top + cell_h - cell_t;      // potted: epoxy line, the cell body's underside
tray_h = potted ? pour_z + pour_rim : board_top + cell_h + top_clear;
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

// Outside the -Y wall, under the exit: the cable lies on top, a tie runs through the tunnel along X.
module tie_block() {
    bw = tie_w + 2*tie_side;
    difference() {
        translate([exit_x - bw/2, -out_w/2 - tie_out, 0]) cube([bw, tie_out + wall, cable_z - cable_d/2]);
        translate([exit_x - bw/2 - 1, -out_w/2 - tie_out + (tie_out - tie_w)/2, -1]) cube([bw + 2, tie_w, tie_h + 1]);
    }
}

module tray() {
    difference() {
        union() {
            difference() {
                linear_extrude(tray_h) outline();
                translate([0, -in_w/2, floor_t]) cube([in_l, in_w, tray_h]);
            }
            if (tabs) linear_extrude(tab_t) tab_2d();
            tie_block();
            // edge ledges, one under each long edge of the board
            for (s = [-1, 1]) translate([bx0 + cell_bare, s > 0 ? in_w/2 - fit - ledge_lip : -in_w/2, floor_t - 0.01])
                cube([board_l - cell_bare - hdr_bare, ledge_lip + fit, ledge + 0.01]);
            translate([hole_x, 0, floor_t - 0.01]) cylinder(d = boss_d, h = ledge + 0.01);
            if (potted) translate([hole_x, 0, board_z - 0.01]) cylinder(d = locate_d, h = board_t + 0.01);
            else intersection() {   // lid-screw columns in the inside corners
                for (c = cols) translate([c[0], c[1], 0]) cylinder(d = column_d, h = tray_h);
                translate([0, -in_w/2, 0]) cube([in_l, in_w, tray_h]);
            }
        }
        if (!potted) {
            // M3 down through board and boss into a pressed-in nut; clearance on through the floor
            translate([hole_x, 0, -1]) cylinder(d = screw_d, h = board_z + 2);
            translate([hole_x, 0, board_z - nut_t]) cylinder(d = (nut_af + 2*nut_fit) / cos(30), h = nut_t + 1, $fn = 6);
            for (c = cols) translate([c[0], c[1], tray_h - pilot_h]) cylinder(d = pilot_d, h = pilot_h + 1);
        }
        // cable exit in the -Y side wall, round-bottomed, open to the rim
        translate([exit_x - cable_d/2, -in_w/2 - wall - 1, cable_z]) cube([cable_d, wall + 2, tray_h]);
        translate([exit_x, -in_w/2 + 1, cable_z]) rotate([90, 0, 0]) cylinder(d = cable_d, h = wall + 2);
        if (tabs) for (h = tab_holes()) translate([h[0], h[1], -1]) cylinder(d = tab_hole, h = tab_t + 2);
    }
}

// Lidded build: the lid's cut profile, the tray's outline with two holes on a diagonal over the columns.
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
    translate([exit_x, 0, cable_z]) rotate([90, 0, 0]) cylinder(d = cable_d - 0.3, h = out_w/2 + tie_out + 6);
}

if (part == "tray") tray();
else if (part == "assembly") {
    tray();
    color("tan") module_standin();
    if (!potted) color("lightblue", 0.5) translate([0, 0, tray_h + 8]) linear_extrude(lid_t) lid_2d();
}
