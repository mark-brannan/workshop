// Louvred screen for one Adafruit BME688 board (25.4 x 17.78, holes 20.32 x 12.7): a small Stevenson screen for a cabin bulkhead.
// Back plate on the bulkhead, -y down, +z into the room. Slatted side walls let air cross the chip and block a straight line in.
// The board hangs on four pegs and the cover's posts keep it there. The cable lies in a notch in the floor that the cover closes; a cable tie inside stops it pulling out.
// Print as shown: back plate on the bed, no supports; every wall and slat is a straight extrusion. The cover is part-cover.scad.
part = "body";

/* [Chamber, inside] */
in_w = 21;           // x; the board is 17.78
in_h = 49;           // y, floor to roof
in_d = 20;           // z, back plate to cover
plate_t = 2;
floor_t = 2.4;
roof_t = 2.4;

/* [Louvres] */
louv_run = 7;        // a slat runs this far outward and drops as far: 45 degrees
louv_t = 1.2;
louv_pitch = 5;      // at most; the slats are spread evenly up the wall

/* [Board seat] */
board_l = 25.4;      // Adafruit board file
board_w = 17.78;
hole_dx = 20.32;
hole_dy = 12.7;
pcb_t = 1.6;         // guess
board_y = 25.7;      // board centre above the floor; its long side is upright, the plug end down
pad_h = 8;           // board's underside off the back plate, so the chip sits mid-chamber
pad_d = 5;
peg_d = 2.1;         // in the board's 2.5 holes
peg_h = 2.6;         // 1 proud of the board

/* [Cable notch] */
notch_w = 6;         // cable is a guess at 4.5
notch_depth = 8;     // down from the cover

/* [Screws] */
mount_d = 4.5;       // 4 mm wood screw to the bulkhead
mount_lo_y = 6;      // both on the centre line; the cable is laid in after the body is on the wall
mount_hi_y = 44;
pilot_d = 2.5;       // M3 self-tapper (guess; the gauge proves it)
pilot_depth = 12;

/* [Cover] */
cover_t = 2;
cover_hole = 3.4;
post_base_d = 6;
post_tip_d = 4.5;
press_gap = 0.3;     // post tip to the board

/* [Hidden] */
$fn = 48;
bite = 0.5;                              // the end slats run this far into the corner posts
out_w = in_w + 2*louv_run;
y_lo = -floor_t;
y_hi = in_h + roof_t;
body_h = plate_t + in_d;
slat_v = louv_t / cos(45);               // a slat's thickness measured up the wall
slat_span = y_hi - y_lo - 2*louv_run + 2*bite - louv_run - slat_v;
n_slat = ceil(slat_span / louv_pitch) + 1;
pitch = slat_span / (n_slat - 1);
notch_z = body_h - notch_depth + notch_w/2;
post_l = in_d - pad_h - pcb_t - press_gap;
seats = [for (sx = [-1, 1], sy = [-1, 1]) [sx*hole_dy/2, board_y + sy*hole_dx/2]];
pilots = [for (sx = [-1, 1], y = [y_lo + louv_run/2, y_hi - louv_run/2]) [sx*(in_w/2 + louv_run/2), y]];

module outline() { translate([-out_w/2, y_lo]) square([out_w, y_hi - y_lo]); }

module walls() {
    translate([-out_w/2, y_lo]) square([out_w, floor_t]);
    translate([-out_w/2, y_hi - roof_t]) square([out_w, roof_t]);
    for (m = [0, 1]) mirror([m, 0]) {
        for (y = [y_lo, y_hi - louv_run]) translate([in_w/2, y]) square(louv_run);                 // corner posts
        for (k = [0 : n_slat - 1]) translate([in_w/2, y_lo + louv_run - bite + k*pitch])
            polygon([[0, louv_run], [0, louv_run + slat_v], [louv_run, slat_v], [louv_run, 0]]);  // slats, down and out
    }
}

module body() {
    difference() {
        union() {
            linear_extrude(plate_t) offset(delta = -0.01) outline();   // inset, so no face lies on a wall's face
            linear_extrude(body_h) walls();
            for (s = seats) translate([s[0], s[1], plate_t - 0.01]) {
                cylinder(d = pad_d, h = pad_h + 0.01);
                cylinder(d = peg_d, h = pad_h + peg_h + 0.01);
            }
        }
        translate([0, y_lo - 1, notch_z]) rotate([-90, 0, 0]) cylinder(d = notch_w, h = floor_t + 2);   // cable notch, open to the cover
        translate([-notch_w/2, y_lo - 1, notch_z]) cube([notch_w, floor_t + 2, in_d]);
        for (y = [mount_lo_y, mount_hi_y]) translate([0, y, -1]) cylinder(d = mount_d, h = plate_t + 2);
        for (p = pilots) translate([p[0], p[1], body_h - pilot_depth]) cylinder(d = pilot_d, h = pilot_depth + 1);
    }
}

// Printed inner face up. It goes on turned over, posts toward the board.
module cover() {
    linear_extrude(cover_t) difference() {
        outline();
        for (p = pilots) translate(p) circle(d = cover_hole);
    }
    for (s = seats) translate([s[0], s[1], cover_t - 0.01]) difference() {
        cylinder(d1 = post_base_d, d2 = post_tip_d, h = post_l + 0.01);
        translate([0, 0, post_l - (peg_h - pcb_t) - 0.5]) cylinder(d = peg_d + 0.8, h = peg_h);   // socket over the peg's tip
    }
}

if (part == "body") body();
if (part == "cover") cover();
