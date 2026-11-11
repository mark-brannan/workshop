// DIN-rail (TS35) mount for an 80 x 110 mm enclosed AC-DC supply.
// A flat base plate screws to the PSU's two diagonal holes. Two DIN clips,
// the owner's design (Thingiverse thing:2415668, "Half Height Breadboard DIN
// Mount", DIN_Clip.stl), press into peg holes in the plate. Each clip has a
// fixed hook on one end and a flexing hooked arm on the other, so two clips
// give two fixed and two flex latches. The rail runs along X, the 80 mm axis:
// the 110 mm side stands up and down.
// Print the base with the PSU face down (z = 0). Clips print flat as shown.

/* [Show] */
part = "print";      // [print:All parts laid out for printing, assembled:Assembled, base:Base plate only, clip:One clip only]

/* [Plate] */
plate_l = 80;        // X, along the rail
plate_w = 110;       // Y, across the rail (the vertical, long side)
plate_t = 5;         // peg holes are blind, 3.5 deep
corner_r = 3;

/* [PSU mounting holes] (caliper ~, diagonal pair) */
hole_dx = 47;        // centre to centre along X (the 80 mm side)
hole_dy = 75;        // centre to centre along Y (the 110 mm side)
hole_d = 2.8;        // M2.5 clearance. The PSU holes take 2.5 mm, 3.3 mm at the very most
cbore_d = 5.2;       // screw-head pocket on the rail side
cbore_depth = 2;

/* [Clips] */
clip_w = 6;          // clip thickness along the rail; 6 is the original design
clip_x = 25;         // clip centre distance from the plate centre, along the rail
peg_d = 4.0;         // the clip's two pegs, from the original STL
peg_len = 3.25;
peg_hole_d = 4.0;    // hole in the plate; tune for the press fit
peg_hole_depth = 3.5;

/* [Hidden] */
$fn = 48;
// Clip outline from DIN_Clip.stl, mm. Origin = clip base corner; y up is away
// from the plate. Rail seat is y = 12.18, hook lips at y = 13.18. The flex arm
// is the left stem with the long hook; the right lip is fixed.
clip_outer = [[0,0],[0.71,15.61],[-3.21,19.48],[0.17,18.79],[0.75,18.64],[1.3,18.42],[1.84,18.15],
  [2.33,17.82],[2.8,17.44],[3.22,17.02],[3.59,16.55],[3.91,16.04],[4.17,15.51],[4.38,14.95],
  [4.52,14.37],[4.6,13.77],[4.62,13.18],[2.37,13.18],[2.37,3.18],[2.38,3.08],[2.48,2.91],
  [2.65,2.81],[2.75,2.8],[2.84,2.81],[3.01,2.91],[3.07,2.99],[3.12,3.18],[3.12,12.18],
  [38.37,12.18],[38.37,13.18],[35.98,14.47],[35.91,14.55],[35.84,14.74],[35.87,14.95],
  [35.99,15.12],[36.08,15.18],[41.84,15.18],[41.84,0]];
clip_hole = [[8.62,2.5],[36.34,2.5],[36.76,2.53],[37.18,2.62],[37.58,2.77],[37.96,2.98],[38.3,3.23],
  [38.6,3.54],[38.86,3.88],[39.07,4.25],[39.22,4.65],[39.31,5.07],[39.34,5.5],[39.34,9.68],
  [8.62,9.68],[8.19,9.65],[7.78,9.55],[7.37,9.41],[7.0,9.2],[6.66,8.94],[6.35,8.64],[6.1,8.3],
  [5.89,7.92],[5.74,7.52],[5.65,7.1],[5.62,6.68],[5.62,5.5],[5.65,5.07],[5.74,4.65],[5.89,4.25],
  [6.1,3.88],[6.35,3.54],[6.66,3.23],[7.0,2.98],[7.37,2.77],[7.78,2.62],[8.19,2.53]];
peg_xs = [5.9, 35.9];                 // peg centres along the clip
rail_cx = (3.12 + 38.37) / 2;         // 20.745: rail centreline in clip coordinates

// Clip in its own frame: profile in XY, thickness along Z, pegs toward -Y.
module clip() {
    linear_extrude(clip_w) difference() { polygon(clip_outer); polygon(clip_hole); }
    for (px = peg_xs) translate([px, 0.01, clip_w / 2]) rotate([90, 0, 0]) cylinder(d = peg_d, h = peg_len + 0.01);
}

// Clip installed: base on the plate top, rail centreline at y = 0, centred on x = cx.
module clip_placed(cx) {
    translate([cx - clip_w / 2, 0, plate_t]) rotate([90, 0, 90])
        translate([-rail_cx, 0, 0]) clip();
}
// Plate position of a peg, for the blind holes.
function peg_y(px) = px - rail_cx;

module base() {
    difference() {
        linear_extrude(plate_t)
            offset(r = corner_r) square([plate_l - 2*corner_r, plate_w - 2*corner_r], center = true);
        for (p = [[-1, -1], [1, 1]]) translate([p[0]*hole_dx/2, p[1]*hole_dy/2, 0]) {
            translate([0, 0, -1]) cylinder(d = hole_d, h = plate_t + 2);
            translate([0, 0, plate_t - cbore_depth]) cylinder(d = cbore_d, h = cbore_depth + 1);
        }
        for (sx = [-1, 1], px = peg_xs)
            translate([sx*clip_x, peg_y(px), plate_t - peg_hole_depth]) cylinder(d = peg_hole_d, h = peg_hole_depth + 1);
    }
}

module assembled() {
    base();
    for (sx = [-1, 1]) clip_placed(sx*clip_x);
}

module print_layout() {
    base();
    // clips lie flat beside the plate, in the original STL orientation
    for (i = [0, 1]) translate([-44 + i*50, plate_w/2 + 8, 0]) clip();
}

if (part == "base") base();
else if (part == "clip") clip();
else if (part == "assembled") assembled();
else print_layout();
