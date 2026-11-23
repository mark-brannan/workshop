// HALMET piezo pod: a box with a snap-on lid on an engine-room bulkhead or deckhead.
// The XY-MOS trigger module sits in a seat on a plinth, its terminal pins in a blind pocket, two M2 screws at
// the far end. The flanged 12 V buzzer sits under the lid, its ears on two pegs on ledges at the end walls,
// its round body up through a hole in the lid; the lid snaps down and clamps the ears. Its leads stay inside.
// Origin: back face (against the bulkhead), centred. X across, Y up the bulkhead, Z out from it.
// Print the box floor down and the lid (part-lid.scad) outer face down, as modelled.
// Ledges stand on 45° gussets; snap ridge and groove are 45° both faces.
// The two cables (HALMET signal, boat 12 V) enter through a notch in the bottom wall, off to one side of the
// ledge, run out to the rim; the lid closes it. Two rounded-triangle tabs at the ends screw to the bulkhead.

/* [Parts] */
mod_l = 33.8;         // XY-MOS module, owner caliper
mod_w = 16.7;         // owner caliper
mod_h = 12;           // board bottom to the top of its parts; seller listings, not calipered
board_t = 1.6;        // GUESS: not calipered
pin_out = 2.6;        // terminal pins below the board; owner caliper
pocket_w = 11.2;      // pin pocket, across the board; owner
pocket_l = 6.1;       // along the board; owner
pocket_r = 4;         // GUESS: pocket centre to the terminal end
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
top_clear = 3;        // module top to the buzzer's back

/* [Module seat] */
plinth_h = 3;         // board raised clear of its pins (pin_out) with margin
fit = 0.3;            // board to rim, each side
rim_t = 1.2;
rim_h = 1.5;          // above the board's seat
m2_pilot = 1.7;       // M2 self-tapping; calibration pending
m2_depth = 5;         // plinth and most of the floor: room for a longer screw

/* [Buzzer ledges and pegs] */
ledge_w = 8;          // across
ledge_front = 17;     // ledge front face, from centre; past the module's end
peg_d = 2.8;          // under the ear hole (M3 clearance on the buzzer); unmeasured
peg_h = 3.5;          // ear_t less clearance

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

/* [Cable notch, bottom wall] */
notch_w = 12;         // two cables side by side
notch_d = 7;          // down from the rim
notch_x = -11;        // off to one side, clear of the ledge

/* [Bulkhead tabs] */
tab_t = 3;
tab_reach = 7;        // screw centre past the end wall
tab_r = 5.5;          // apex radius: room for a pan head
tab_base = 10;        // half-width where the tab meets the wall
mount_d = 4.5;        // #8 or M4

/* [Hidden] */
$fn = 64;
eps = 0.01;
out_w = in_w + 2*wall;
out_l = in_l + 2*wall;
seat_z = floor_t + plinth_h;                         // board underside
depth = seat_z + mod_h + top_clear + ear_t;          // floor to the lid's underside
ledge_z = depth - ear_t;                             // ledge top, ears' underside
seat_w = mod_w + 2*fit + 2*rim_t;
seat_l = mod_l + 2*fit + 2*rim_t;

module rrect(w, l, r) { offset(r = r) square([w - 2*r, l - 2*r], center = true); }

// 45° both faces; centred on the origin, along Y, pointing +X.
module ridge(d, l) { rotate([90, 0, 0]) linear_extrude(l, center = true) polygon([[0, -d], [d, 0], [0, d]]); }

module seat() {
    difference() {
        translate([-seat_w/2, -seat_l/2, floor_t - eps]) cube([seat_w, seat_l, plinth_h + rim_h + eps]);
        translate([-mod_w/2 - fit, -mod_l/2 - fit, seat_z]) cube([mod_w + 2*fit, mod_l + 2*fit, rim_h + 1]);
        translate([-pocket_w/2, -mod_l/2 + pocket_r - pocket_l/2, floor_t]) cube([pocket_w, pocket_l, plinth_h + 1]);
    }
}

module ledge(sy) {
    mirror([0, sy < 0 ? 1 : 0, 0]) {
        rotate([90, 0, 90]) linear_extrude(ledge_w, center = true)
            polygon([[in_l/2 + eps, ledge_z], [ledge_front, ledge_z], [ledge_front, ledge_z - 2],
                     [in_l/2 + eps, ledge_z - 2 - (in_l/2 - ledge_front)]]);
        translate([0, ear_pitch/2, ledge_z - eps]) {
            cylinder(d = peg_d, h = peg_h - 0.5 + eps);
            translate([0, 0, peg_h - 0.5]) cylinder(d1 = peg_d, d2 = peg_d - 1, h = 0.5);
        }
    }
}

module tab(sy) {
    mirror([0, sy < 0 ? 1 : 0, 0]) difference() {
        linear_extrude(tab_t) hull() {
            for (sx = [-1, 1]) translate([sx*(tab_base - 2), out_l/2 - 2]) circle(r = 2);
            translate([0, out_l/2 + tab_reach]) circle(r = tab_r);
        }
        translate([0, out_l/2 + tab_reach, -1]) cylinder(d = mount_d, h = tab_t + 2);
    }
}

module box() {
    difference() {
        union() {
            difference() {
                linear_extrude(depth) rrect(out_w, out_l, corner_r);
                translate([0, 0, floor_t]) linear_extrude(depth) square([in_w, in_l], center = true);
            }
            for (sy = [-1, 1]) { ledge(sy); tab(sy); }
            seat();
        }
        for (sx = [-1, 1]) translate([sx*hole_pitch/2, mod_l/2 - hole_e, seat_z - m2_depth]) cylinder(d = m2_pilot, h = m2_depth + 1);
        translate([notch_x - notch_w/2, -out_l/2 - 1, depth - notch_d]) cube([notch_w, wall + 2, notch_d + 1]);
        for (sx = [-1, 1]) translate([sx*in_w/2, 0, depth - snap_z]) mirror([sx < 0 ? 1 : 0, 0, 0]) ridge(groove_d, skirt_l + 2);
    }
}

module lid() {
    sk_x = in_w/2 - skirt_gap;
    difference() {
        union() {
            linear_extrude(lid_t) rrect(out_w, out_l, corner_r);
            for (sx = [-1, 1]) mirror([sx < 0 ? 1 : 0, 0, 0]) {
                translate([sk_x - skirt_t, -skirt_l/2, lid_t - eps]) cube([skirt_t, skirt_l, skirt_h + eps]);
                translate([sk_x - eps, 0, lid_t + snap_z]) ridge(snap_d, skirt_l);
            }
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
    translate([0, 0, ledge_z]) difference() {
        union() {
            cylinder(d = buzzer_d, h = buzzer_h);
            linear_extrude(ear_t) hull() { circle(d = buzzer_d); for (sy = [-1, 1]) translate([0, sy*(ear_span/2 - 3.5)]) circle(r = 3.5); }
        }
        for (sy = [-1, 1]) translate([0, sy*ear_pitch/2, -1]) cylinder(d = 3.2, h = ear_t + 2);
    }
}

module m2_screw() { cylinder(d = 3.8, h = 1.4); translate([0, 0, -8]) cylinder(d = 2, h = 8); }

explode = 22;  // gap between layers in the exploded drawing

module exploded() {
    g = explode;
    color("orange") box();
    translate([0, 0, g]) module_standin();
    color("silver") for (sx = [-1, 1]) translate([sx*hole_pitch/2, mod_l/2 - hole_e, seat_z + board_t + 1.6*g]) m2_screw();
    translate([0, 0, 2.2*g]) color("white") buzzer_standin();
    translate([0, 0, 3.2*g]) color("gold") lid_on();
}

show = "box";  // [box, assembly, exploded]
if (show == "assembly") { color("orange") box(); module_standin(); color("white") buzzer_standin(); color("gold", 0.5) lid_on(); }
else if (show == "exploded") exploded();
else box();
