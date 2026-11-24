// HALMET piezo pod: a box with a snap-on lid on an engine-room bulkhead or deckhead.
// The XY-MOS trigger module sits in a seat on a plinth, its terminal pins in a blind pocket, two M2 screws at
// the far end.
// The flanged 12 V buzzer sits under the lid, its ears on two ledges at the end walls, its round body up
// through a hole in the lid. Two M3 screws go down through the lid and the ears into heat-set inserts in the
// ledges, clamping lid and ears together; the lid also snaps on. Its leads stay inside.
// Origin: back face (against the bulkhead), centred. X across, Y up the bulkhead, Z out from it.
// Print the box floor down and the lid (part-lid.scad) outer face down, as modelled.
// Ledges stand on 45° gussets; snap ridge and groove are 45° both faces.
// The two cables (HALMET signal, boat 12 V) enter through a mousehole at the foot of the end wall at the
// module's terminal end, its roof a 45° point. Two rounded-triangle tabs at the ends screw to the bulkhead.
// Outside edges: 45° chamfer where they face down in print, rounded where they face up. Inside: the floor
// meets the walls on a fillet, the inside corners are rounded, the rim has a lead-in for the lid's skirt.

/* [Parts] */
mod_l = 33.8;         // XY-MOS module, owner caliper
mod_w = 16.7;         // owner caliper
mod_h = 12;           // board bottom to the top of its parts; seller listings, not calipered
board_t = 1.6;        // GUESS: not calipered
pin_out = 2.6;        // terminal pins below the board; owner caliper
pocket_w = 11.2;      // pin pocket, across the board; owner
pocket_l = 6.1;       // along the board; owner
pocket_r = 4;         // GUESS: pocket centre to the terminal end
pocket_slack = 0.6;   // pocket longer each way: the module slides this far to pass under a ledge
hole_pitch = 12.5;    // module holes, across the board at the far end; owner, unsure
hole_e = 2.5;         // GUESS: hole centre to the far end
buzzer_d = 29;        // flanged buzzer on hand, round body; owner, caliper
buzzer_h = 15;        // overall; owner, approximate
ear_t = 4.5;          // ear flange at the buzzer's back; owner, caliper
ear_span = 47.4;      // ear tip to ear tip; owner, caliper
ear_pitch = 40;       // ear hole to ear hole; owner, by eye

/* [Box] */
in_w = 36;            // across: the buzzer's leads leave its side, toward a long wall
in_l = 56;            // up the bulkhead
wall = 2;
floor_t = 2.4;
corner_r = 3;         // outside vertical corners
slide_clear = 0.3;    // module top to the ledges' underside
in_r = 1.5;           // inside vertical corners
floor_fillet = 2;     // floor to wall, inside
chamfer_b = 0.6;      // back edge, against the bulkhead (faces down in print)
round_t = 0.6;        // rim's outer edge
lead_in = 0.4;        // rim's inner edge, for the lid's skirt

/* [Module seat] */
plinth_h = 3;         // board raised clear of its pins (pin_out) with margin
fit = 0.3;            // board to rim, each side
rim_t = 1.2;
rim_h = 1.5;          // above the board's seat
m2_pilot = 1.7;       // M2 self-tapping; calibration pending
m2_depth = 5;         // plinth and most of the floor: room for a longer screw

/* [Buzzer ledges and heat-set inserts] */
insert_hole_d = 4.0;  // M3 heat-set insert, short (M3 x 4); the hole its maker gives. Not bought
insert_l = 4;         // insert length
insert_wall = 1.6;    // plastic round the insert's hole
ledge_w = 8;          // across; at least the boss, insert_hole_d + 2*insert_wall
ledge_skin = 1;       // below the insert hole's bottom
lid_screw_d = 3.6;    // M3 clearance through the lid; printed holes come out small

/* [Snap lid] */
lid_t = 2.4;
body_hole_d = 29.8;   // printed holes come out small
skirt_t = 1.2;
skirt_h = 4;          // down from the lid's underside, along the long walls
skirt_l = 40;
skirt_gap = 0.2;      // skirt to wall
snap_z = 2.5;         // ridge centre, below the lid's underside
snap_d = 0.6;         // ridge height off the skirt
groove_d = 0.8;       // groove depth into the wall
lid_chamfer = 0.8;    // outer face's edge (faces down in print)
lid_round = 0.4;      // inner face's edge, against the rim

/* [Cable mousehole, terminal end wall] */
hole_w = 9;           // two cables side by side
hole_side = 3;        // straight sides, floor to the arch's spring line
hole_x = -12.5;         // off to one side, clear of the gusset and the tab

/* [Bulkhead tabs] */
tab_t = 3;
tab_reach = 7;        // screw centre past the end wall
tab_r = 5.5;          // apex radius: room for a pan head
tab_base = 8;         // half-width where the tab meets the wall; clear of the mousehole
tab_round = 1;        // tab's top edge
tab_fillet = 1.5;     // 45° fillet, tab top to wall
mount_d = 4.5;        // #8 or M4

/* [Hidden] */
$fn = 64;
eps = 0.01;
out_w = in_w + 2*wall;
out_l = in_l + 2*wall;
seat_z = floor_t + plinth_h;                         // board underside
insert_depth = insert_l + 0.8;                       // blind hole, room for melt
ledge_t = insert_depth + ledge_skin;                 // ledge's front face, before the gusset
ledge_front = ear_pitch/2 - insert_hole_d/2 - insert_wall;  // over the module's end, by design
ledge_z = seat_z + mod_h + slide_clear + ledge_t;    // ledge top, ears' underside
depth = ledge_z + ear_t;                             // floor to the lid's underside
seat_w = mod_w + 2*fit + 2*rim_t;
seat_l = mod_l + 2*fit + 2*rim_t;

module rrect(w, l, r) { offset(r = r) square([w - 2*r, l - 2*r], center = true); }

// Convex slab, rounded-rectangle plan, h high: 45° chamfer cb at the bottom, round rt at the top.
// A hull of layers, so the mesh is the same every run.
module slab(w, l, r, h, cb, rt, n = 6) {
    hull() {
        linear_extrude(eps) rrect(w - 2*cb, l - 2*cb, max(r - cb, 0.1));
        translate([0, 0, cb]) linear_extrude(h - cb - rt) rrect(w, l, r);
        for (i = [1:n]) let(a = 90*i/n, k = rt*(1 - cos(a)))
            translate([0, 0, h - rt + rt*sin(a) - eps]) linear_extrude(eps) rrect(w - 2*k, l - 2*k, max(r - k, 0.1));
    }
}

// The box's inside: filleted to the floor, lead-in chamfer at the rim, open above.
module cavity(n = 6) {
    f = floor_fillet;
    hull() {
        for (i = [0:n]) let(a = 90*i/n, k = f - f*sin(a))
            translate([0, 0, floor_t + f - f*cos(a)]) linear_extrude(eps) rrect(in_w - 2*k, in_l - 2*k, max(in_r - k, 0.1));
        translate([0, 0, depth - lead_in]) linear_extrude(eps) rrect(in_w, in_l, in_r);
        translate([0, 0, depth]) linear_extrude(1) rrect(in_w + 2*lead_in, in_l + 2*lead_in, in_r + lead_in);
    }
}

// Mousehole: straight sides from z = 0, round roof with a 45° point; drawn in XZ, through Y.
module mousehole(w, side, through) {
    rotate([90, 0, 0]) linear_extrude(through, center = true) {
        translate([-w/2, -1]) square([w, side + 1]);
        translate([0, side]) hull() { circle(d = w); polygon([[-w/2*cos(45), w/2*sin(45)], [w/2*cos(45), w/2*sin(45)], [0, w/2*sqrt(2)]]); }
    }
}

// 45° both faces; centred on the origin, along Y, pointing +X.
module ridge(d, l) { rotate([90, 0, 0]) linear_extrude(l, center = true) polygon([[0, -d], [d, 0], [0, d]]); }

module seat() {
    difference() {
        translate([-seat_w/2, -seat_l/2, floor_t - eps]) cube([seat_w, seat_l, plinth_h + rim_h + eps]);
        // rims along the long sides only: the module slides along its length to pass under a ledge
        translate([-mod_w/2 - fit, -seat_l/2 - 1, seat_z]) cube([mod_w + 2*fit, seat_l + 2, rim_h + 1]);
        translate([-pocket_w/2, -mod_l/2 + pocket_r - pocket_l/2 - pocket_slack, floor_t]) cube([pocket_w, pocket_l + 2*pocket_slack, plinth_h + 1]);
    }
}

module ledge(sy) {
    mirror([0, sy < 0 ? 1 : 0, 0]) {
        rotate([90, 0, 90]) linear_extrude(ledge_w, center = true)
            polygon([[in_l/2 + 1, ledge_z], [ledge_front, ledge_z], [ledge_front, ledge_z - ledge_t],
                     [in_l/2 + 1, ledge_z - ledge_t - (in_l/2 + 1 - ledge_front)]]);
    }
}

module insert_holes() {
    for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, ledge_z - insert_depth]) {
        cylinder(d = insert_hole_d, h = insert_depth + 1);
        translate([0, 0, insert_depth - 0.5]) cylinder(d1 = insert_hole_d, d2 = insert_hole_d + 1.2, h = 0.6);  // lead-in
    }
}

module tab_plan(k) {
    hull() {
        for (sx = [-1, 1]) translate([sx*(tab_base - 2), out_l/2 - 2]) circle(r = 2 - k);
        translate([0, out_l/2 + tab_reach]) circle(r = tab_r - k);
    }
}

module tab(sy, n = 5) {
    f = tab_fillet;
    mirror([0, sy < 0 ? 1 : 0, 0]) difference() {
        union() {
            hull() {
                linear_extrude(eps) tab_plan(chamfer_b);
                translate([0, 0, chamfer_b]) linear_extrude(tab_t - chamfer_b - tab_round) tab_plan(0);
                for (i = [1:n]) let(a = 90*i/n, k = tab_round*(1 - cos(a)))
                    translate([0, 0, tab_t - tab_round + tab_round*sin(a) - eps]) linear_extrude(eps) tab_plan(k);
            }
            // 45° fillet where the tab's top meets the end wall
            rotate([90, 0, 90]) linear_extrude(2*(tab_base - 2), center = true)
                polygon([[out_l/2 - 1, tab_t - 0.5], [out_l/2 + f, tab_t - 0.5], [out_l/2 - 1, tab_t + f + 1]]);
        }
        translate([0, out_l/2 + tab_reach, -1]) cylinder(d = mount_d, h = tab_t + 2);
    }
}

module box() {
    difference() {
        union() {
            difference() {
                slab(out_w, out_l, corner_r, depth, chamfer_b, round_t);
                cavity();
            }
            intersection() {
                for (sy = [-1, 1]) ledge(sy);
                cavity();
            }
            for (sy = [-1, 1]) tab(sy);
            seat();
        }
        insert_holes();
        for (sx = [-1, 1]) translate([sx*hole_pitch/2, mod_l/2 - hole_e, seat_z - m2_depth]) cylinder(d = m2_pilot, h = m2_depth + 1);
        translate([hole_x, -in_l/2, floor_t]) mousehole(hole_w, hole_side, 2*wall + 2*floor_fillet + 2);
        for (sx = [-1, 1]) translate([sx*in_w/2, 0, depth - snap_z]) mirror([sx < 0 ? 1 : 0, 0, 0]) ridge(groove_d, skirt_l + 2);
    }
}

module lid() {
    sk_x = in_w/2 - skirt_gap;
    difference() {
        union() {
            slab(out_w, out_l, corner_r, lid_t, lid_chamfer, lid_round);
            for (sx = [-1, 1]) mirror([sx < 0 ? 1 : 0, 0, 0]) {
                translate([sk_x - skirt_t, -skirt_l/2, lid_t - eps]) cube([skirt_t, skirt_l, skirt_h + eps]);
                translate([sk_x - eps, 0, lid_t + snap_z]) ridge(snap_d, skirt_l);
            }
        }
        translate([0, 0, -1]) cylinder(d = body_hole_d, h = lid_t + 2);
        for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, -1]) cylinder(d = lid_screw_d, h = lid_t + 2);
    }
}

// Lid in place, flipped onto the box, for the assembly drawing.
module lid_on() { translate([0, 0, depth + lid_t]) mirror([0, 0, 1]) lid(); }

module module_standin() {
    color("darkgreen") translate([-mod_w/2, -mod_l/2, seat_z]) cube([mod_w, mod_l, board_t]);
    color("seagreen") translate([-mod_w/2 + 1, -mod_l/2 + 1, seat_z + board_t]) cube([mod_w - 2, mod_l - 2 - 2*hole_e, mod_h - board_t]);
    color("silver") translate([-pocket_w/2 + 1, -mod_l/2 + pocket_r - pocket_l/2 + 1, seat_z - pin_out]) cube([pocket_w - 2, pocket_l - 2, pin_out]);
}

module buzzer_standin() {
    translate([0, 0, ledge_z]) difference() {
        union() {
            cylinder(d = buzzer_d, h = buzzer_h);
            linear_extrude(ear_t) hull() { circle(d = buzzer_d); for (sy = [-1, 1]) translate([0, sy*(ear_span/2 - 3.5)]) circle(r = 3.5); }
        }
        for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, -1]) cylinder(d = 3.2, h = ear_t + 2);
    }
}

module m2_screw() { cylinder(d = 3.8, h = 1.4); translate([0, 0, -8]) cylinder(d = 2, h = 8); }
module m3_screw(l = 10) { cylinder(d = 5.5, h = 2); translate([0, 0, -l]) cylinder(d = 3, h = l); }
module insert_standin() { color("goldenrod") difference() { cylinder(d = insert_hole_d + 0.6, h = insert_l); translate([0, 0, -1]) cylinder(d = 2.5, h = insert_l + 2); } }

// Half section on X = 0 when show is "cutaway", through the inserts, screws and buzzer; the -X half
// (mousehole side) is kept. Each part is cut on its own so it keeps its colour.
module cut() { if (show == "cutaway") intersection() { children(); translate([-100, -100, -10]) cube([100, 200, 100]); } else children(); }

// Everything in place: box, module and its M2 screws, inserts, buzzer, lid, M3 screws.
module assembled() {
    color("orange") cut() box();
    cut() module_standin();
    color("silver") cut() for (sx = [-1, 1]) translate([sx*hole_pitch/2, mod_l/2 - hole_e, seat_z + board_t]) m2_screw();
    color("goldenrod") cut() for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, ledge_z - insert_l]) insert_standin();
    color("white") cut() buzzer_standin();
    color("gold") cut() lid_on();
    color("silver") cut() for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, depth + lid_t]) m3_screw();
}

explode = 22;  // gap between layers in the exploded drawing

module exploded() {
    g = explode;
    color("orange") box();
    translate([0, 0, g]) module_standin();
    color("silver") for (sx = [-1, 1]) translate([sx*hole_pitch/2, mod_l/2 - hole_e, seat_z + board_t + 1.6*g]) m2_screw();
    for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, ledge_z - insert_l + 1.6*g]) insert_standin();
    translate([0, 0, 2.2*g]) color("white") buzzer_standin();
    translate([0, 0, 3.2*g]) color("gold") lid_on();
    color("silver") for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, depth + lid_t + 4*g]) m3_screw();
}

show = "box";  // [box, assembly, exploded, cutaway]
if (show == "assembly") assembled();
else if (show == "exploded") exploded();
else if (show == "cutaway") assembled();
else box();
