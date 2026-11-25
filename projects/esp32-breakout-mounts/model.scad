// DIN-rail (TS35) mount for an ESP32 breakout board on four M3 standoffs.
// Same base-plate and peg-hole pattern as ../din-rail-psu-mount, so the owner's
// DIN clips (thing:2415668) press into the underside. The rail runs along X.
// Print as shown: plate flat on the bed, standoffs up, no supports.

/* [Plate] */
plate_l = 93.2;      // X, along the rail: hole_dx + 12
plate_w = 89.0;      // Y, across the rail: hole_dy + 12
plate_t = 5;         // peg holes are blind, 3.5 deep from the underside
corner_r = 3;

/* [Board holes] centres, from outside-edge caliper readings 84.4 x 80.2, diagonal 115.2, holes 3.1-3.3, taken as 3.2 */
hole_dx = 81.2;
hole_dy = 77.0;

/* [Standoffs] */
standoff_h = 6;      // above the plate; clears pins and solder on the board's back
standoff_d = 7.5;
insert_d = 4.0;      // M3 heat-set insert; use ~2.6 to tap M3 straight into the plastic
insert_depth = 5.5;  // from the standoff top, stays inside the plate

/* [Clips] */
clip_x = 25;
peg_hole_d = 4.0;
peg_hole_depth = 3.5;

/* [Hidden] */
$fn = 48;
peg_ys = [5.9 - 20.745, 35.9 - 20.745];   // peg centres across the rail, as in the PSU mount

module base() {
    difference() {
        union() {
            linear_extrude(plate_t)
                offset(r = corner_r) square([plate_l - 2*corner_r, plate_w - 2*corner_r], center = true);
            for (sx = [-1, 1], sy = [-1, 1])
                translate([sx*hole_dx/2, sy*hole_dy/2, 0]) cylinder(d = standoff_d, h = plate_t + standoff_h);
        }
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx*hole_dx/2, sy*hole_dy/2, plate_t + standoff_h - insert_depth])
                cylinder(d = insert_d, h = insert_depth + 1);
        for (sx = [-1, 1], py = peg_ys)
            translate([sx*clip_x, py, -1]) cylinder(d = peg_hole_d, h = peg_hole_depth + 1);
    }
}

base();
