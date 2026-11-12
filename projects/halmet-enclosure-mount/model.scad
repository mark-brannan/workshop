// Frame that holds a Hat Labs HALMET board in the 158x90x60 pre-drilled box.
// Sits on the box's six holed floor bosses; two standoffs take the board's M3 slots.
// Origin: centre of the box floor. X along the box length. Print flat, standoffs up.

mode = "2d";         // [2d:laser profile, 3d:print]
part = "frame";      // [frame, gauge:thin fit check of the same outline]

/* [Box: owner's estimates, tune after a gauge print] */
boss_span = 136;     // holed bosses, centre to centre along the box length
boss_pitch = 21;     // neighbouring bosses on one end
screw_d = 3.4;       // clearance for the screw into a boss
slot_reach = 4;      // each fork slot accepts the boss this far in or out of boss_span

/* [Board position on the floor] */
board_dx = 0;
board_dy = 3;        // away from the gland-nut wall (-Y)

/* [Frame] */
plate_t = 3;
rail_w = 8;
gauge_t = 0.8;

/* [Standoffs] */
standoff_h = 6;      // board underside above the frame; clears pin stubs
standoff_d = 8;
insert_d = 4.0;      // M3 heat-set insert
insert_depth = 6.5;  // blind, from the standoff top
rest_d = 4;          // plain rests on the other diagonal
spacer_hole_d = 3.2; // laser and gauge: M3 through a loose spacer

/* [Hidden] */
$fn = 48;
// From HALMET.kicad_pcb, relative to the centre of the 89 x 58 board.
slots = [[-21.75, 22.5], [22.75, -22.5]];
rests = [[36, 18], [-38.5, -19.5]];
rail_ys = [for (s = slots) s[1] + board_dy];
bar_x0 = boss_span/2 - slot_reach - screw_d/2 - 3;   // inner edge of an end bar
bar_x1 = boss_span/2 + slot_reach;                   // outer edge
y_hi = max(boss_pitch + 6, max(rail_ys) + rail_w/2);
y_lo = min(-boss_pitch - 6, min(rail_ys) - rail_w/2);

module at_board(pts) { for (p = pts) translate([p[0] + board_dx, p[1] + board_dy]) children(); }

module solid2d() {
    offset(r = 1.5) offset(delta = -1.5) {
        for (sx = [-1, 1]) scale([sx, 1]) translate([bar_x0, y_lo]) square([bar_x1 - bar_x0, y_hi - y_lo]);
        for (y = rail_ys) translate([-bar_x0 - 1, y - rail_w/2]) square([2*bar_x0 + 2, rail_w]);
        translate([board_dx - rail_w/2, min(rail_ys)]) square([rail_w, max(rail_ys) - min(rail_ys)]);
        at_board(slots) circle(d = standoff_d + 2);
        at_board(rests) circle(d = rest_d + 4);
    }
}

module fork_slots() {
    for (sx = [-1, 1], k = [-1, 0, 1]) scale([sx, 1]) translate([0, k*boss_pitch]) hull() {
        translate([boss_span/2 - slot_reach, 0]) circle(d = screw_d);
        translate([bar_x1 + 2, 0]) circle(d = screw_d);
    }
}

module profile(spacer_holes) {
    difference() {
        solid2d();
        fork_slots();
        if (spacer_holes) at_board(slots) circle(d = spacer_hole_d);
    }
}

module frame() {
    difference() {
        union() {
            linear_extrude(plate_t) profile(false);
            linear_extrude(plate_t + standoff_h) at_board(slots) circle(d = standoff_d);
            linear_extrude(plate_t + standoff_h) at_board(rests) circle(d = rest_d);
        }
        translate([0, 0, plate_t + standoff_h - insert_depth])
            linear_extrude(insert_depth + 1) at_board(slots) circle(d = insert_d);
    }
}

if (mode == "2d") profile(true);
else if (part == "gauge") linear_extrude(gauge_t) profile(true);
else frame();
