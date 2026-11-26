// DIN-rail (TS35) mount for the "MRD066A for esp32 terminal adapter" breakout (63 x 77, unknown brand) on four M2 standoffs.
// Flat back; the preferred DIN clips (Printables 420009, ../din-rail-psu-mount/ref_din_clip_heat_insert.stl)
// are printed apart and screwed on from the board side with countersunk M3. The rail runs along X, the board's
// long side (77), so both terminal strips lie along the rail and their wire entries face up and down, toward the
// ducts; the short side (63) and each clip's two screws lie across the rail (Y).
// Print as shown: plate flat on the bed, standoffs up, no supports.

/* [Plate] */
plate_l = 84.9;      // X, along the rail: hole_dx + 12
plate_w = 70.6;      // Y, across the rail: hole_dy + 12
plate_t = 5;
corner_r = 3;

/* [Board holes] centres = inside-to-inside + one 2.2 hole: long side 70.7, short side 56.4 (diagonal 91.4 checks) */
hole_dx = 72.9;
hole_dy = 58.6;

/* [Standoffs] */
standoff_h = 6;      // above the plate; clears pins and solder on the board's back
standoff_d = 6;
insert_d = 3.2;      // M2 heat-set insert (3.5 OD); use ~1.7 to tap M2 straight into the plastic
insert_depth = 4.5;  // from the standoff top

/* [Clips] */
clip_xs = [-20, 20];         // two clips along the rail, as on the PSU mount
clip_ys = [22.05, -28.95];   // each clip's two screws across the rail: fixed hook up (+Y), spring latch down (51 apart)
hole_d = 3.5;                // M3 clearance
csk_d = 6.5;
csk_h = 1.6;                 // head sits below the plate face, under the board

/* [Hidden] */
$fn = 48;

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
        for (x = clip_xs, y = clip_ys) translate([x, y, 0]) {
            translate([0, 0, -1]) cylinder(d = hole_d, h = plate_t + 2);
            translate([0, 0, plate_t - csk_h]) cylinder(d1 = csk_d - 2*csk_h, d2 = csk_d + 2, h = csk_h + 1);
        }
    }
}

base();
