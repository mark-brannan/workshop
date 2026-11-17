// Stand-in for the 63 x 58 x 35 ABS box (black or clear lid), for assemblies. Not a print.
// Origin: centre of the inside floor. x along the 63 side, y along the 58 side, z up.
// Numbers are the vendor's or read off vendor photos; README lists which. None calipered.

/* [Box, vendor] */
box_l = 63;          // outer, x
box_w = 58;          // outer, y
box_h = 35;          // outer, lid on
col_clear = 39;      // clear wall between corner columns, both walls

/* [Box, read off photos] */
box_wall = 2.5;      // gives the vendor's 53 inside across y
box_floor = 3;
lid_h = 8.5;         // lid outer height
lid_top = 2.5;       // lid plate thickness
lid_lip = 4;         // lid's inner rim, in from the inside wall face
gasket_step = 4.5;   // thickened wall band under the seam
gasket_in = 1.5;     // how far that band stands in from the wall
boss_pitch = 43;     // floor screw bosses, along x, centred; 39 to 47 by two readings of the photo
boss_d = 6;
boss_h = 4;
boss_hole = 2.5;     // takes an M3 self-tapper (guess)
boss_wing = 10;      // wing length across y
boss_wing_t = 2;
boss_wing_h = 2.5;

in_l = box_l - 2*box_wall;                 // 58
in_w = box_w - 2*box_wall;                 // 53
col_x = (in_l - col_clear) / 2;            // 9.5, column size along x
col_y = (in_w - col_clear) / 2;            // 7, column size along y
rim_z = box_h - lid_h - box_floor;         // 23.5, seam above the inside floor
ceil_z = box_h - lid_top - box_floor;      // 29.5, lid underside above the inside floor
wall_top_z = rim_z - gasket_step;          // 19, top of the plain wall a nut can seat on

module box_columns(h = rim_z) {
    for (sx = [-1, 1], sy = [-1, 1]) scale([sx, sy, 1])
        translate([in_l/2 - col_x, in_w/2 - col_y, 0]) cube([col_x, col_y, h]);
}

module box_bosses() {
    for (sx = [-1, 1]) translate([sx*boss_pitch/2, 0, 0]) difference() {
        union() {
            cylinder(d = boss_d, h = boss_h, $fn = 32);
            translate([-boss_wing_t/2, -boss_wing/2, 0]) cube([boss_wing_t, boss_wing, boss_wing_h]);
        }
        translate([0, 0, 0.5]) cylinder(d = boss_hole, h = boss_h, $fn = 24);
    }
}

// holes: list of [wall, along, z, dia]; wall is "x+", "x-", "y+", "y-"; along is the position along that wall from its centre
module wall_hole(h) {
    wall = h[0]; a = h[1]; z = h[2]; d = h[3];
    if (wall == "y+" || wall == "y-") translate([a, (wall == "y+" ? 1 : -1) * (in_w/2 + box_wall/2), z])
        rotate([90, 0, 0]) cylinder(d = d, h = box_wall + 4, center = true, $fn = 48);
    else translate([(wall == "x+" ? 1 : -1) * (in_l/2 + box_wall/2), a, z])
        rotate([0, 90, 0]) cylinder(d = d, h = box_wall + 4, center = true, $fn = 48);
}

module box_body(holes = []) {
    difference() {
        translate([-box_l/2, -box_w/2, -box_floor]) cube([box_l, box_w, box_floor + rim_z]);
        translate([-in_l/2, -in_w/2, 0]) cube([in_l, in_w, rim_z + 1]);
        for (h = holes) wall_hole(h);
    }
    difference() {
        union() {
            box_columns();
            translate([0, 0, wall_top_z]) difference() {      // gasket band
                translate([-in_l/2, -in_w/2, 0]) cube([in_l, in_w, gasket_step]);
                translate([-in_l/2 + gasket_in, -in_w/2 + gasket_in, -1]) cube([in_l - 2*gasket_in, in_w - 2*gasket_in, gasket_step + 2]);
            }
        }
        for (h = holes) wall_hole(h);
    }
    box_bosses();
}

module box_lid() {
    translate([0, 0, rim_z]) difference() {
        translate([-box_l/2, -box_w/2, 0]) cube([box_l, box_w, lid_h]);
        translate([-in_l/2 + lid_lip, -in_w/2 + lid_lip, -1]) cube([in_l - 2*lid_lip, in_w - 2*lid_lip, lid_h - lid_top + 1]);
    }
}

// The space parts may occupy: the cross-shaped floor up to the gasket band, then the lid's recess.
module box_free() {
    difference() {
        translate([-in_l/2, -in_w/2, 0]) cube([in_l, in_w, wall_top_z]);
        box_columns(wall_top_z + 1);
    }
    translate([-in_l/2 + gasket_in, -in_w/2 + gasket_in, wall_top_z]) difference() {
        cube([in_l - 2*gasket_in, in_w - 2*gasket_in, gasket_step]);
        translate([-gasket_in, -gasket_in, -1]) intersection() { translate([gasket_in, gasket_in, 0]) cube([in_l - 2*gasket_in, in_w - 2*gasket_in, 10]); box_columns(10); }
    }
    translate([-in_l/2 + lid_lip, -in_w/2 + lid_lip, rim_z]) cube([in_l - 2*lid_lip, in_w - 2*lid_lip, ceil_z - rim_z]);
}
