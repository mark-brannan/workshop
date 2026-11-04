// Parametric L-bracket (mm). Same spec as model.py. Plain OpenSCAD, no libraries.

/* [Plates] */
thickness = 3;       // [1:0.5:10]
width = 40;          // shared X extent of both plates
base_depth = 30;     // horizontal plate, along Y
wall_height = 25;    // vertical plate, along Z
outer_fillet = 2;    // round on the outside corner edge

/* [Holes] */
hole_d = 4.2;
holes_per_leg = 2;
hole_pitch = 24;     // between the two holes, along X
hole_chamfer = 1;    // 45 deg chamfer on the top edge of each hole

/* [Hidden] */
$fn = 64;
eps = 0.01;

t = thickness;
r = outer_fillet;

// L profile in (Y, Z): base along +Y, wall along +Z, outside corner at the origin rounded.
module profile() {
    difference() {
        union() { square([base_depth, t]); square([t, wall_height]); }
        square(r);
    }
    intersection() { translate([r, r]) circle(r); square(r); }
}

// A through hole plus its chamfer cone; +Z is the chamfered (outer) face at z = depth.
module hole(depth) {
    translate([0, 0, -eps]) cylinder(d = hole_d, h = depth + 2 * eps);
    translate([0, 0, depth - hole_chamfer])
        cylinder(h = hole_chamfer + eps, r1 = hole_d / 2, r2 = hole_d / 2 + hole_chamfer + eps);
}

module holes_x() {
    for (i = [0 : holes_per_leg - 1])
        translate([width / 2 + (i - (holes_per_leg - 1) / 2) * hole_pitch, 0, 0]) children();
}

module bracket() {
    difference() {
        rotate([90, 0, 90]) linear_extrude(width) profile();
        // base holes, drilled along -Z, chamfer on the top face z = t
        translate([0, (base_depth + t) / 2, 0]) holes_x() hole(t);
        // wall holes along +Y, chamfer on the outside face y = 0
        translate([0, t, (wall_height + t) / 2]) holes_x() rotate([90, 0, 0]) hole(t);
    }
}

bracket();
