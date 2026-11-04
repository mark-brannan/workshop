// 2D plate for laser (DXF) and the same sketch extruded for print (STL).
// Build with mode="2d" for DXF and -D mode="3d" for STL. Plain OpenSCAD.

/* [Output] */
mode = "2d"; // [2d, 3d]

/* [Plate] */
length = 100;
width = 60;
thickness = 3;       // only used in 3d mode

/* [Features] */
hole_d = 3.2;
hole_inset = 5;      // hole centre from each edge
slot_length = 20;    // centre-to-centre
slot_width = 6;

/* [Hidden] */
$fn = 64;

module plate() {
    difference() {
        square([length, width], center = true);
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * (length / 2 - hole_inset), sy * (width / 2 - hole_inset)]) circle(d = hole_d);
        hull() for (sx = [-1, 1]) translate([sx * slot_length / 2, 0]) circle(d = slot_width);
    }
}

if (mode == "3d") linear_extrude(thickness) plate();
else plate();
