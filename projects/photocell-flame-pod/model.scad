// Photocell flame pod: a small PETG tray for one LM393 photoresistor module, closed by a clear
// laser-cut acrylic lid (part-lid.scad) that the photocell looks out through.
// Origin: inside floor corner at the photocell end, centred across. X along the module, header end at +X.
// Print floor down, as modelled. The module sits component side up on two edge ledges and a boss;
// one M3 screw goes down through its hole into a nut pressed into the boss. The photocell is bent
// up on its leads to just under the lid. The cable leaves through a slot in the header-end wall,
// open to the rim, which the lid closes. Two M2.5 self-tappers through the lid into corner columns.

/* [Module: LM393 photoresistor, on hand (owner, caliper)] */
board_l = 31;
board_w = 14;
board_t = 1.6;        // guessed, standard PCB
hole_from_hdr = 7;    // hole centre from the header end, centred across: ~4 hole, rim 5 from the end
pot_h = 4.6;          // trimpot top above the board top (owner)
cell_h = 11.5;        // photocell top above the board top, bent up on its leads (owner)
cell_d = 5;           // guessed: common 5 mm CdS cell
fit = 0.3;            // per side, board edge to inner wall; guessed, PETG fit uncalibrated

/* [Lead-out] */
lead = "dupont";      // [dupont, solder]
plug_out = 15;        // dupont: board edge to the plug's back end; guessed, 14 housing + header spacer
solder_out = 9;       // solder: board edge to the end of the heatshrink over the pins; guessed
wire_clear = 2;       // plug or heatshrink end to the inner end wall
cable_d = 4.5;        // slot width for a 3-core cable; guessed, caliper the cable
pin_z = 1.27;         // header pin row above the board top; right-angle header, guessed

/* [Tray] */
wall = 1.6;           // 4 lines at 0.4
floor_t = 2;
corner_r = 2;         // outside vertical corners
ledge = 2;            // board underside above the floor: clears solder stubs, room for the nut
ledge_lip = 1.2;      // ledge reach in under the board edge: solder pads sit 1.4 in (halmet-enclosure-mount)
cell_bare = 4;        // no ledge under the photocell end this far in: its leads' solder
hdr_bare = 3;         // nor under the header end's solder row
boss_d = 7.5;
nut_af = 5.5;         // M3 hex nut across flats
nut_t = 2.4;
nut_fit = 0.15;       // per side; press fit, uncalibrated
screw_d = 3.4;        // M3 clearance, through the floor: any M3 x 6 to 10
cell_end = 4;         // board's photocell end to the inner end wall: the cell body overhangs here
top_clear = 1;        // photocell top to the lid's underside
column_d = 5;         // lid-screw columns in the four inside corners
pilot_d = 2.2;        // M2.5 self-tapping; calibration pending
pilot_h = 8;

/* [Mounting tabs] */
tabs = true;
tab_l = 8;            // past each end wall
tab_t = 2.5;
tab_hole = 3.5;       // M3 or #6 pan head

/* [Lid: 3 mm clear acrylic, laser cut] */
lid_t = 3;
lid_hole_d = 2.9;     // M2.5 clearance

part = "tray";        // [tray, assembly, none]

/* [Hidden] */
$fn = 48;
lead_l = lead == "dupont" ? plug_out : solder_out;
in_l = cell_end + board_l + lead_l + wire_clear;
in_w = board_w + 2*fit;
out_l = in_l + 2*wall;
out_w = in_w + 2*wall;
bx0 = cell_end;                      // board's photocell end
bx1 = bx0 + board_l;                 // board's header end
hole_x = bx1 - hole_from_hdr;
board_z = floor_t + ledge;           // board underside
board_top = board_z + board_t;
tray_h = board_top + cell_h + top_clear;   // rim, the lid's underside
cable_z = board_top + pin_z;               // cable centre, level with the header pins
cols = [for (x = [0, in_l], y = [-in_w/2, in_w/2]) [x, y]];

module rrect(l, w, r) { offset(r = r) square([l - 2*r, w - 2*r], center = true); }
module outline() { translate([in_l/2, 0]) rrect(out_l, out_w, corner_r); }

module tab_2d() {
    for (s = [-1, 1]) hull() {
        translate([in_l/2 + s*(in_l/2 + wall - corner_r), 0]) square([0.02, out_w], center = true);
        translate([in_l/2 + s*(in_l/2 + wall + tab_l - out_w/4), 0]) rrect(out_w/2, out_w, out_w/4 - 0.01);
    }
}
function tab_holes() = [for (s = [-1, 1]) [in_l/2 + s*(in_l/2 + wall + tab_l/2), 0]];

module tray() {
    difference() {
        union() {
            difference() {
                linear_extrude(tray_h) outline();
                translate([0, -in_w/2, floor_t]) cube([in_l, in_w, tray_h]);
            }
            if (tabs) linear_extrude(tab_t) tab_2d();
            // edge ledges, one under each long edge of the board
            for (s = [-1, 1]) translate([bx0 + cell_bare, s > 0 ? in_w/2 - fit - ledge_lip : -in_w/2, floor_t - 0.01])
                cube([board_l - cell_bare - hdr_bare, ledge_lip + fit, ledge + 0.01]);
            translate([hole_x, 0, floor_t - 0.01]) cylinder(d = boss_d, h = ledge + 0.01);
            // lid-screw columns in the inside corners
            intersection() {
                for (c = cols) translate([c[0], c[1], 0]) cylinder(d = column_d, h = tray_h);
                translate([0, -in_w/2, 0]) cube([in_l, in_w, tray_h]);
            }
        }
        // M3 down through board and boss into a pressed-in nut; clearance on through the floor
        translate([hole_x, 0, -1]) cylinder(d = screw_d, h = board_z + 2);
        translate([hole_x, 0, board_z - nut_t]) cylinder(d = (nut_af + 2*nut_fit) / cos(30), h = nut_t + 1, $fn = 6);
        for (c = cols) translate([c[0], c[1], tray_h - pilot_h]) cylinder(d = pilot_d, h = pilot_h + 1);
        // cable slot in the header-end wall, open to the rim
        translate([in_l - 1, -cable_d/2, cable_z]) cube([wall + 2, cable_d, tray_h]);
        translate([in_l - 1, 0, cable_z]) rotate([0, 90, 0]) cylinder(d = cable_d, h = wall + 2);
        if (tabs) for (h = tab_holes()) translate([h[0], h[1], -1]) cylinder(d = tab_hole, h = tab_t + 2);
    }
}

// The lid's cut profile: the tray's outline, two holes on a diagonal over the columns.
lid_cols = [cols[0], cols[3]];
module lid_2d() {
    difference() {
        outline();
        for (c = lid_cols) translate(c) circle(d = lid_hole_d);
    }
}

// Stand-ins for the review render only: board, trimpot, photocell, header and plug.
module module_standin() {
    translate([bx0, -board_w/2, board_z]) difference() {
        cube([board_l, board_w, board_t]);
        translate([board_l - hole_from_hdr, board_w/2, -1]) cylinder(d = 4, h = board_t + 2);
    }
    translate([bx0 + 12, -3, board_top]) cube([7, 6, pot_h]);
    translate([bx0 + 1, 0, board_top + cell_h - 2]) cylinder(d = cell_d, h = 2);
    for (y = [-1.5, 1.5]) translate([bx0 + 1 + y*0.6, y*0.4, board_top]) cylinder(d = 0.5, h = cell_h - 2, $fn = 8);
    translate([bx1 - 2.5, -3.8, board_top]) cube([2.5, 7.6, 2.54]);
    if (lead == "dupont") translate([bx1, -3.8, board_top]) cube([lead_l, 7.6, 2.54]);
}

if (part == "tray") tray();
else if (part == "assembly") {
    tray();
    color("tan") module_standin();
    color("lightblue", 0.5) translate([0, 0, tray_h + 8]) linear_extrude(lid_t) lid_2d();
}
