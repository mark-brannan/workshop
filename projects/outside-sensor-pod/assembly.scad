// Assembly view, not a print: base, five louvres and the cap on their rods, with two stand-in boards on the fin.
include <model.scad>
part = "assembly";
cut = true;          // quarter cut-away to show the cavity

module stack() {
    color("gainsboro") base();
    for (k = [1 : n_louvres]) color("white") translate([0, 0, base_t + boss_h + pitch*k]) rotate([0, 180, 0]) louvre();
    color("white") translate([0, 0, base_t + boss_h + pitch*(n_louvres + 1)]) rotate([0, 180, 0]) cap();
}
module board(sx) {   // 25.4 x 17.78 stand-in, long axis up, parts facing away from the fin
    translate([sx*(fin_t/2 + standoff), 0, board_z]) {
        color("royalblue") translate([sx*0.8, 0, 0]) cube([1.6, board_w, 25.4], center = true);
        color("silver") translate([sx*2.6, 0, 0]) cube([2, 3.5, 3.5], center = true);
    }
}
difference() { stack(); if (cut) translate([0, -100, -1]) cube([100, 100, 200]); }
board(1); board(-1);
