// Shower-sump platform: a flat deck the size of the sump's base, set at the height where the sump's
// wings just reach the hull. Its two long edges are skirts leaning in at the hull's angle; they are the
// bonding faces, bedded in thickened epoxy or 5200. Nothing reaches down to the keel.
// Installed axes: X across the boat, Y fore-aft (+Y toward the bow), Z up; z = 0 at the deck's top.
// Print: deck on the bed (part = "print", the default). The skirts lean in 90 - hull_angle from vertical.

part = "print";      // [print, installed]

/* [Sump base, which sets the deck (tape, aboard 2026-11-21)] */
w_aft = 234.25;      // 8 3/4 in taped (222.25) + 12: widened 6 per side to cover the sump wing lobes (owner, 2026-11-22)
w_fwd = 208;         // 7 1/2 in taped (190.5) + 17.5: widened until the traced wing outline sits inside the deck (test_wing_fit.py)
len = 88.9;          // 3 1/2 in: the tab length; owner's working spacing of the two widths, not a tape reading

/* [Hull] */
hull_angle = 66;     // degrees above horizontal: hull leans 23 stbd, 25 port from vertical (speed square, rough), mean 24 -> 66

/* [Sump screws and opening (from the Fusion v6 deck)] */
holes = [[93, 25], [93, -34], [100, 0], [-93, 25], [-93, -34], [-100, 0]];   // the sump's wing holes
hole_d = 3;          // self-tapping pilot, as Fusion had it
boss_d = 9;
boss_h = 12;         // screw depth below the deck top
opening = [176, 59]; // cut out of the deck middle, under the sump; leaves 15 mm strips at the 89 mm length (Fusion had 176 x 80 on 110)

/* [Build] */
deck_t = 4;
skirt_h = 20;        // vertical depth of the bonding face
skirt_t = 4;         // measured square to the face
bond_gap = 1.5;      // adhesive, each side: the skirt sits this far inside the hull line

e = 0.01;
run = skirt_h / tan(hull_angle);              // inward step of the skirt over its depth
tn = skirt_t / sin(hull_angle);               // skirt thickness, measured across X

// deck and skirts apart: a hull() of whole end sections would fill the space under the deck
module platform() difference() {
  frame();
  for (h = holes) translate([h[0], h[1], -boss_h - e]) cylinder(d = hole_d, h = boss_h + 2 * e, $fn = 24);
  translate([-opening[0] / 2, -opening[1] / 2, -deck_t - e]) cube([opening[0], opening[1], deck_t + 2 * e]);
}

module frame() {
  hw_a = w_aft / 2 - bond_gap / sin(hull_angle);
  hw_f = w_fwd / 2 - bond_gap / sin(hull_angle);
  // deck: a trapezoid in plan
  translate([0, 0, -deck_t]) linear_extrude(deck_t)
    polygon([[-hw_a, -len / 2], [hw_a, -len / 2], [hw_f, len / 2], [-hw_f, len / 2]]);
  // bosses stop at the skirt's outer face (the hull), so none pokes past it into a flat overhang
  intersection() {
    for (h = holes) translate([h[0], h[1], -boss_h]) cylinder(d = boss_d, h = boss_h, $fn = 32);
    hull() {
      translate([0, 0, -e]) linear_extrude(e) polygon([[-hw_a, -len / 2], [hw_a, -len / 2], [hw_f, len / 2], [-hw_f, len / 2]]);
      inset = boss_h / tan(hull_angle);
      translate([0, 0, -boss_h]) linear_extrude(e)
        polygon([[-hw_a + inset, -len / 2], [hw_a - inset, -len / 2], [hw_f - inset, len / 2], [-hw_f + inset, len / 2]]);
    }
  }
  for (s = [-1, 1]) hull() for (p = [[hw_a, -len / 2], [hw_f, len / 2]])
    translate([0, p[1], 0]) rotate([90, 0, 0]) linear_extrude(e, center = true)
      scale([s, 1]) polygon([[p[0], 0], [p[0] - run, -skirt_h], [p[0] - run - tn, -skirt_h], [p[0] - tn, 0]]);
}

if (part == "installed") platform();
else rotate([180, 0, 0]) platform();
