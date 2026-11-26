// Print plate of the preferred DIN clip: 5 pairs, 10 clips, one PETG job, flat face down.
// Maxstupo's "DIN Rail Clip (Heat Insert Version)", Printables 420009 (CC BY 4.0), unchanged:
// 60 x 18 x 7.5, centred on y, x from 0. Plate origin is the bed centre, +Y the back.
// Each row is a pair: the right clip is the left one turned 180 degrees about Z (a turn, no mirror).
/* [Layout] */
pairs = 5;     // rows
gap_x = 6;     // between the two clips of a pair
pitch = 22;    // row spacing; the clip is 18 deep
clip_l = 60;

module clip() import("ref_din_clip_heat_insert.stl");

for (i = [0 : pairs - 1]) {
    y = (i - (pairs - 1) / 2) * pitch;
    translate([-gap_x / 2 - clip_l, y, 0]) clip();
    translate([ gap_x / 2 + clip_l, y, 0]) rotate([0, 0, 180]) clip();
}
