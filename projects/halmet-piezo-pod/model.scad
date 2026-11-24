// HALMET piezo pod: a box with a snap-on lid on an engine-room bulkhead or deckhead.
// The XY-MOS trigger module sits in a seat on a plinth, its terminal pins in a blind pocket, two M2.5 screws at
// the far end.
// The flanged 12 V buzzer sits as low as the module allows, its ears on two bosses that grow out of the long
// walls on 45° corbels, leaving the floor beside the module clear for wires; the buzzer is turned in plan
// (ear_angle) so its ears reach the walls. Two ledges mid-wall seat the flange's edge, so it sits on four points.
// Two M3 screws hold the ears down into heat-set inserts in the bosses, inside the box, under the lid.
// Two cable-tie bridges on the floor along the mousehole-side wall tie the cables down against vibration.
// The round body comes up through a hole in the lid, its top flush with the lid or just proud (proud).
// The lid snaps on with one long finger down each long wall, its ridge clicking into a pocket in the wall; a stiff
// stop across each end wall keys it lengthwise, so it sits located on all four walls (owner). The fingers stop
// short of the buzzer's ear tips; the ears are point-symmetric, so the lid fits either way round.
// The buzzer's leads stay inside.
// Origin: back face (against the bulkhead), centred. X across, Y up the bulkhead, Z out from it.
// Print the box floor down and the lid (part-lid.scad) outer face down, as modelled.
// Ledges stand on 45° gussets; snap ridge and pocket are 45° both faces.
// The two cables (HALMET signal, boat 12 V) enter through a mousehole at the foot of the end wall at the
// module's terminal end, its roof a semicircle. Two rounded-triangle tabs at the ends screw to the bulkhead.
// Outside edges square, box and lid flush at the seam; only the lid's top edge is rounded. Inside: the floor
// meets the walls on a fillet, the inside corners are rounded, the rim has a lead-in for the lid's skirt.

/* [Parts] */
mod_l = 33.8;         // XY-MOS module, owner caliper
mod_w = 16.7;         // owner caliper
mod_h = 12;           // board bottom to the top of its parts; seller listings, not calipered
board_t = 1.1;        // owner, ~1.1
pin_out = 2.6;        // terminal pins below the board; owner caliper
pocket_w = 11.2;      // pin pocket, across the board; owner
pocket_l = 6.1;       // along the board; owner
pocket_gap = 3;       // owner caliper: board's terminal end to the pin block's near edge
pocket_r = pocket_gap + pocket_l/2;  // pocket centre to the terminal end
pin_relief = 0.25;    // pocket grown this much each side past the owner's numbers
hole_pitch = 13.2;    // module holes, across the board at the far end; scaled off the owner's photo by the board's 16.7 width (12.5 printed too narrow)
hole_gap = 0.1;       // owner caliper: board's far end to the near edge of a screw hole
hole_d = 2.6;         // module screw hole; owner caliper
hole_e = hole_gap + hole_d/2;        // hole centre to the far end
buzzer_d = 29;        // flanged buzzer on hand, round body; owner, caliper
buzzer_h = 15;        // overall; owner, approximate
ear_t = 4.5;          // ear flange at the buzzer's back; owner, caliper
ear_span = 47.4;      // ear tip to ear tip; owner, caliper
ear_pitch = 40;       // ear hole to ear hole; owner, by eye
ear_r = 3.5;          // ear tip radius; by eye

/* [Box] */
in_w = 36;            // across: the buzzer's leads leave its side, toward a long wall
in_l = 56;            // up the bulkhead
wall = 2;
floor_t = 2.4;
corner_r = 3;         // outside vertical corners
buzz_clear = 1;       // module top to the buzzer's back; mod_h is from listings
proud = 3;            // buzzer top above the lid's top; 0 = flush; owner wants ~3 showing
in_r = 1.5;           // inside vertical corners
floor_fillet = 2;     // floor to wall, inside
chamfer_b = 0;        // back edge, against the bulkhead: square
round_t = 0;          // rim's outer edge: square, flush with the lid at the seam
lead_in = 0.4;        // rim's inner edge, for the lid's skirt

/* [Module seat] */
plinth_h = 3;         // board raised clear of its pins (pin_out) with margin
fit = 0.3;            // board to rim, each side
rim_t = 1.2;
rim_h = 1.5;          // above the board's seat
m25_pilot = 2.2;      // M2.5 self-tapping; printed holes come out small; calibration pending
m25_depth = 5;        // plinth and most of the floor: room for a longer screw

/* [Buzzer bosses, ledges and heat-set inserts] */
insert_hole_d = 4.0;  // M3 heat-set insert, short (M3 x 4); the hole its maker gives. Not bought
insert_l = 4;         // insert length
insert_wall = 1.6;    // plastic round the insert's hole
insert_floor = 1.2;   // solid under the insert's hole, then the corbel
ear_tip_gap = 1.2;    // ear tip to the long wall; sets the buzzer's turn
ledge_reach = 5.5;    // seat ledge out from the long wall; the flange's edge overlaps it ~2
ledge_l = 12;         // along the wall
ledge_t = 1.2;        // flat top before the 45° corbel

/* [Cable-tie bridges] */
tie_span = 5;         // tunnel across, for a tie up to 4.8 wide
tie_gap = 1.8;        // tunnel height under the deck
tie_deck_t = 2.2;     // deck thickness; its ends are fully round so the tie bends round them
tie_deck_w = 3;       // deck width, the way the tie runs
tie_pier = 1.6;       // pier thickness each end
tie_xy = [[-12.5, -22.5], [-12.9, -9]];  // inside the mousehole; beside the module on the signal wire's way to J1, clear of the ledge above

/* [Snap lid] */
lid_t = 2.4;
body_hole_d = 29.8;   // printed holes come out small
skirt_t = 1.2;        // snap finger thickness
skirt_h = 8.5;        // finger length down from the lid's underside; long so it bends, not the wall
finger_end = 1;       // finger's corner end to the inside corner's round
ear_clear = 1.2;      // finger's other end to the buzzer's ear tip, in plan
skirt_gap = 0.2;      // finger to wall
snap_z = 7;           // ridge centre, below the lid's underside
snap_d = 0.8;         // ridge height off the finger; the knob if it is too stiff or too loose
groove_d = 0.9;       // pocket depth into the wall
groove_play = 0.5;    // pocket longer than the finger, each end
lid_round = 0.8;      // outer face's edge, the top in use; the inner face's edge is square
stop_t = 1.6;         // end stop, across each end wall between the inside corners' rounds; stiff: it locates, the fingers hold
stop_h = 3;           // down from the lid's underside
stop_gap = 0.2;       // stop to end wall
stop_c = 0.6;         // 45° lead-in on the stop's tip, wall side

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
col_r = insert_hole_d/2 + insert_wall;
ear_angle = asin((in_w/2 - ear_tip_gap - ear_r) / (ear_span/2 - ear_r));  // buzzer turn: ear tips ear_tip_gap off the long walls
ear_dir = [-sin(ear_angle), cos(ear_angle)];         // ear axis in plan; ear holes at ±ear_pitch/2 along it
ledge_z = seat_z + mod_h + buzz_clear;               // boss and ledge tops, the ears' underside
depth = ledge_z + buzzer_h - proud - lid_t;          // floor to the lid's underside
function ear_xy(s) = s*ear_pitch/2*ear_dir;
seat_w = mod_w + 2*fit + 2*rim_t;
seat_l = mod_l + 2*fit + 2*rim_t;
tip_y = (ear_span/2 - ear_r)*cos(ear_angle) - ear_r;  // ear tip's near edge, along Y from the centre
finger_hi = in_l/2 - in_r - finger_end;              // on the +X wall the finger runs from -(tip_y - ear_clear) to here;
finger_lo = -(tip_y - ear_clear);                    // the -X wall's is the same turned 180°, its ear at the other end
finger_w = finger_hi - finger_lo;
finger_y = (finger_hi + finger_lo)/2;

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
    // Two hulls: one hull over all would slope the walls out the whole height (the rim's lead-in
    // spread down to the floor), which left the old snap ridges nothing to catch on.
    hull() {
        for (i = [0:n]) let(a = 90*i/n, k = f - f*sin(a))
            translate([0, 0, floor_t + f - f*cos(a)]) linear_extrude(eps) rrect(in_w - 2*k, in_l - 2*k, max(in_r - k, 0.1));
        translate([0, 0, depth - lead_in]) linear_extrude(eps) rrect(in_w, in_l, in_r);
    }
    hull() {
        translate([0, 0, depth - lead_in - eps]) linear_extrude(eps) rrect(in_w, in_l, in_r);
        translate([0, 0, depth]) linear_extrude(1) rrect(in_w + 2*lead_in, in_l + 2*lead_in, in_r + lead_in);
    }
}

// Mousehole: straight sides from z = 0, semicircular roof; drawn in XZ, through Y.
// The roof's crown is a short flat-ish span in print (owner's choice over a pointed roof).
module mousehole(w, side, through) {
    rotate([90, 0, 0]) linear_extrude(through, center = true) {
        translate([-w/2, -1]) square([w, side + 1]);
        translate([0, side]) circle(d = w);
    }
}

// 45° both faces; centred on the origin, along Y, pointing +X.
module ridge(d, l) { rotate([90, 0, 0]) linear_extrude(l, center = true) polygon([[0, -d], [d, 0], [0, d]]); }

module seat() {
    difference() {
        translate([-seat_w/2, -seat_l/2, floor_t - eps]) cube([seat_w, seat_l, plinth_h + rim_h + eps]);
        translate([-mod_w/2 - fit, -mod_l/2 - fit, seat_z]) cube([mod_w + 2*fit, mod_l + 2*fit, rim_h + 1]);
        translate([-pocket_w/2 - pin_relief, -mod_l/2 + pocket_r - pocket_l/2 - pin_relief, floor_t]) cube([pocket_w + 2*pin_relief, pocket_l + 2*pin_relief, plinth_h + 1]);
    }
}

// Insert boss: a round top at the ear hole, joined into the long wall, carried on a 45° corbel.
boss_bot = ledge_z - insert_l - 0.8 - insert_floor;
module boss(sy) {
    p = ear_xy(sy);
    sx = p[0] < 0 ? -1 : 1;
    reach = in_w/2 - (abs(p[0]) - col_r);   // inner edge of the boss to the wall
    mirror([sx < 0 ? 1 : 0, 0, 0]) hull() {
        translate([abs(p[0]), p[1], boss_bot]) cylinder(r = col_r, h = ledge_z - boss_bot);
        translate([in_w/2 - eps, p[1] - col_r, boss_bot - reach]) cube([wall/2, 2*col_r, ledge_z - boss_bot + reach]);
    }
}

// Seat ledge mid-wall: flat top at ledge_z under the flange's edge, 45° corbel below.
module seat_ledge(sx) {
    mirror([sx < 0 ? 1 : 0, 0, 0]) hull() {
        translate([in_w/2 - ledge_reach, -ledge_l/2, ledge_z - ledge_t]) cube([ledge_reach + wall/2, ledge_l, ledge_t]);
        translate([in_w/2 - eps, -ledge_l/2, ledge_z - ledge_t - ledge_reach]) cube([wall/2, ledge_l, eps]);
    }
}

// Cable-tie bridge: a deck on two piers, the tie runs under it across X; the cable lies on top along Y.
// The deck's ends are fully round, so the tie bends round them. The tunnel's roof is a short flat span (owner accepts).
module tie_bridge(p) {
    h = tie_gap + tie_deck_t;
    translate([p[0], p[1], floor_t - eps]) rotate([90, 0, 0]) {
        linear_extrude(tie_span + 2*tie_pier, center = true)
            translate([0, tie_gap + tie_deck_t/2]) hull() for (s = [-1, 1]) translate([s*(tie_deck_w - tie_deck_t)/2, 0]) circle(d = tie_deck_t);
        for (s = [-1, 1]) translate([0, 0, s*(tie_span/2 + tie_pier/2)]) linear_extrude(tie_pier, center = true)
            translate([-tie_deck_w/2, 0]) square([tie_deck_w, tie_gap + tie_deck_t/2 + eps]);
    }
}

module insert_holes() {
    for (sy = [-1, 1]) translate([each ear_xy(sy), ledge_z - insert_depth]) {
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
            for (sy = [-1, 1]) boss(sy);
            for (sx = [-1, 1]) seat_ledge(sx);
            for (p = tie_xy) tie_bridge(p);
            for (sy = [-1, 1]) tab(sy);
            seat();
        }
        insert_holes();
        for (sx = [-1, 1]) translate([sx*hole_pitch/2, mod_l/2 - hole_e, seat_z - m25_depth]) cylinder(d = m25_pilot, h = m25_depth + 1);
        translate([hole_x, -in_l/2, floor_t]) mousehole(hole_w, hole_side, 2*wall + 2*floor_fillet + 2);
        for (a = [0, 180]) rotate([0, 0, a]) translate([in_w/2, finger_y, depth - snap_z]) ridge(groove_d, finger_w + 2*groove_play);
    }
}

// End stop: a stiff rib across the +Y end wall between the corner rounds, 45° lead-in at its tip.
module end_stop() {
    y0 = in_l/2 - stop_gap - stop_t;
    translate([-(in_w/2 - in_r), 0, lid_t - eps]) rotate([90, 0, 90]) linear_extrude(in_w - 2*in_r)
        polygon([[y0, 0], [y0 + stop_t, 0], [y0 + stop_t, stop_h - stop_c], [y0 + stop_t - stop_c, stop_h], [y0, stop_h]]);
}

module lid() {
    sk_x = in_w/2 - skirt_gap;
    difference() {
        union() {
            translate([0, 0, lid_t]) mirror([0, 0, 1]) slab(out_w, out_l, corner_r, lid_t, 0, lid_round);
            for (a = [0, 180]) rotate([0, 0, a]) translate([0, finger_y, 0]) {
                translate([sk_x - skirt_t, -finger_w/2, lid_t - eps]) cube([skirt_t, finger_w, skirt_h + eps]);
                translate([sk_x - eps, 0, lid_t + snap_z]) ridge(snap_d, finger_w);
            }
            for (a = [0, 180]) rotate([0, 0, a]) end_stop();
        }
        translate([0, 0, -1]) cylinder(d = body_hole_d, h = lid_t + 2);
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
    translate([0, 0, ledge_z]) rotate([0, 0, ear_angle]) difference() {
        union() {
            cylinder(d = buzzer_d, h = buzzer_h);
            linear_extrude(ear_t) hull() { circle(d = buzzer_d); for (sy = [-1, 1]) translate([0, sy*(ear_span/2 - ear_r)]) circle(r = ear_r); }
        }
        for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, -1]) cylinder(d = 3.2, h = ear_t + 2);
    }
}

module m25_screw() { cylinder(d = 4.5, h = 1.7); translate([0, 0, -8]) cylinder(d = 2.5, h = 8); }
module m3_screw(l = 10) { cylinder(d = 5.5, h = 2); translate([0, 0, -l]) cylinder(d = 3, h = l); }
module insert_standin() { color("goldenrod") difference() { cylinder(d = insert_hole_d + 0.6, h = insert_l); translate([0, 0, -1]) cylinder(d = 2.5, h = insert_l + 2); } }

// Half section through the ear axis when show is "cutaway": through the inserts, screws and buzzer.
// Each part is cut on its own so it keeps its colour.
module cut() { if (show == "cutaway") intersection() { children(); rotate([0, 0, ear_angle]) translate([-100, -100, -10]) cube([100, 200, 100]); } else children(); }

// Everything in place: box, module and its M2.5 screws, inserts, buzzer, lid, M3 screws.
module assembled() {
    color("orange") cut() box();
    cut() module_standin();
    color("silver") cut() for (sx = [-1, 1]) translate([sx*hole_pitch/2, mod_l/2 - hole_e, seat_z + board_t]) m25_screw();
    color("goldenrod") cut() for (sy = [-1, 1]) translate([each ear_xy(sy), ledge_z - insert_l]) insert_standin();
    color("white") cut() buzzer_standin();
    color("gold") cut() lid_on();
    color("silver") cut() for (sy = [-1, 1]) translate([each ear_xy(sy), ledge_z + ear_t]) m3_screw(8);
}

explode = 22;  // gap between layers in the exploded drawing

module exploded() {
    g = explode;
    color("orange") box();
    translate([0, 0, g]) module_standin();
    color("silver") for (sx = [-1, 1]) translate([sx*hole_pitch/2, mod_l/2 - hole_e, seat_z + board_t + 1.6*g]) m25_screw();
    for (sy = [-1, 1]) translate([each ear_xy(sy), ledge_z - insert_l + 1.6*g]) insert_standin();
    translate([0, 0, 2.2*g]) color("white") buzzer_standin();
    translate([0, 0, 3.2*g]) color("gold") lid_on();
    color("silver") for (sy = [-1, 1]) translate([each ear_xy(sy), ledge_z + ear_t + 2.8*g]) m3_screw(8);
}

show = "box";  // [box, assembly, exploded, cutaway]
if (show == "assembly") assembled();
else if (show == "exploded") exploded();
else if (show == "cutaway") assembled();
else box();
