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
hull_angle = 66;     // degrees above horizontal: hull leans 23 stbd, 25 port from vertical (speed square, rough), mean 24; owner keeps 24: flexible ends conform, hull to be sanded and bedded in thickened epoxy

/* [Sump screws and opening (from the Fusion v6 deck)] */
holes = [[93, 25], [93, -34], [100, 0], [-93, 25], [-93, -34], [-100, 0]];   // the sump's wing holes
hole_d = 3;          // undersize pilot: drill to 3.3 and tap M4 for a nylon screw after printing (owner, 2026-11-24)
boss_d = 9;
boss_h = 12;         // screw depth below the deck top
opening = [176, 59]; // cut out of the deck middle, under the sump; leaves 15 mm strips at the 89 mm length (Fusion had 176 x 80 on 110)

/* [Build] */
deck_t = 4;
skirt_h = 20;        // vertical depth of the bonding face
skirt_t = 4;         // measured square to the face
bond_gap = 1.5;      // adhesive, each side: the skirt sits this far inside the hull line

/* [Stiffening and bond key] */
arch_t = 2;          // end arches: skirt to skirt under each end of the deck, thickness fore-aft
arch_band = 4;       // depth of the arch under the deck at its crown (centre)
fin_n = 3;           // ridges along each bonding face, running fore-aft
fin_h = 1;           // how far a ridge stands off the face, inside the bond_gap of epoxy
fin_w = 1.2;         // ridge width at its root (3 lines)
rivet_d = 4;         // through-holes in each skirt, epoxy sets through them
rivet_pitch = 8;     // fore-aft, in two rows staggered by half a pitch
rivet_rows = [6.5, 14];  // slant distance down the face to each row: between the ridges
rivet_reach = 36;    // outermost hole centre, fore and aft, clear of the arches

/* [Cable ties: one per wing wraps the wing and the sump lengthwise, top and bottom (owner, 2026-11-25). It runs over
   the wing hugging the box body, off each wing tip, down the deck's end face slanting inboard, through a slit in each
   end arch, and under the sump. Inboard of the screw bosses, so the run under the deck clears them] */
tie_x = 85;          // slit centre from the centreline: inboard of the bosses (88.5), a little narrower than the wings
tie_zc = -7.5;       // slit centre height: its upper end stays clear under the deck
tie_slit_l = 6.5;    // slit length, square to the tie's run: a 4.8 x 1.3 tie with room
tie_slit_w = 2.2;    // slit width, round-ended
tie_top_x = 95.4;    // where the tie leaves the wing tip: hugging the box wall (x = 93) plus half the tie's width
tie_top_z = 3;       // the wing's top there: wing thickness, a guess (unmeasured)
tie_lead = 1;        // fairlead: a groove the slit's length wide, this deep into the deck's end face, along the tie's slant
tie_round = 2;       // radius of every edge the tie bends around: the slit's outer mouth and the fairlead's top lip
e = 0.01;
run = skirt_h / tan(hull_angle);              // inward step of the skirt over its depth
tn = skirt_t / sin(hull_angle);               // skirt thickness, measured across X
tie_lean = atan2(tie_top_x - tie_x, tie_top_z - tie_zc);  // the tie's slant off vertical down the end face; the slit is square to it

// deck and skirts apart: a hull() of whole end sections would fill the space under the deck
module platform() difference() {
  frame();
  for (h = holes) translate([h[0], h[1], -boss_h - e]) cylinder(d = hole_d, h = boss_h + 2 * e, $fn = 24);
  translate([-opening[0] / 2, -opening[1] / 2, -deck_t - e]) cube([opening[0], opening[1], deck_t + 2 * e]);
  for (s = [-1, 1], f = [-1, 1]) scale([s, f, 1]) tie_slit();
  // a hole that meets a boss stops at it, so the pilot keeps its wall
  difference() {
    for (s = [-1, 1]) scale([s, 1, 1]) for (r = [0 : len(rivet_rows) - 1])
      for (y = [-rivet_reach + r * rivet_pitch / 2 : rivet_pitch : rivet_reach]) rivet(y, rivet_rows[r]);
    for (h = holes) translate([h[0], h[1], -boss_h - 1]) cylinder(d = boss_d + 1, h = boss_h + 1, $fn = 32);  // +1: no face shared with the boss
  }
}

// one end arch's tie slit, square to the tie's slant, with the fairlead groove down the deck's end face above it.
// Local frame on the end face: u along the slit, v up the tie's run toward the wing; y through the arch
module tie_slit() {
  yf = len / 2 - tie_lead;                  // groove floor: the slit's outer mouth
  yi = len / 2 - arch_t - 0.1;              // just past the arch's inner face, so no slice lies on it
  ro = tie_round; ri = 0.6;
  q = function(r, t) t <= 0 ? r : t >= r ? 0 : r - sqrt(r * r - (r - t) * (r - t));  // quarter-round growth at depth t
  g = function(y) max(q(ro, yf - y), q(ri, y - yi));
  ys = concat([yi - 2], [for (t = [0 : ri / 4 : ri]) yi + t], [for (t = [ro : -ro / 8 : 0]) yf - t], [yf + 2]);
  translate([tie_x, 0, tie_zc]) rotate([0, tie_lean, 0]) {
    // the slit, its mouths flared by quarter-rounds
    for (i = [0 : len(ys) - 2]) hull() for (y = [ys[i], ys[i + 1]])
      translate([0, y, 0]) rotate([-90, 0, 0]) linear_extrude(e) stadium(tie_slit_l, tie_slit_w, g(y));
    // fairlead groove up the tie's run, from below the slit to above the deck top
    top = (-tie_zc + 2) / cos(tie_lean);
    translate([-tie_slit_l / 2, yf, -tie_slit_w / 2 - ro]) cube([tie_slit_l, tie_lead + 2, top + tie_slit_w / 2 + ro]);
  }
  // the groove's top lip, where it meets the deck top: rounded, blended to 45 degrees at the bed in print
  intersection() {
    translate([tie_x, 0, tie_zc]) rotate([0, tie_lean, 0])
      translate([-tie_slit_l / 2, yf - 5, 0]) cube([tie_slit_l, 10, -tie_zc / cos(tie_lean) + 5]);
    translate([-200, 0, 0]) rotate([90, 0, 90]) linear_extrude(400) lip_cutter(yf, tie_round);
  }
}

// a convex quarter-round on the edge at (y0, 0), material at y < y0 and z < 0; the last 45 degrees a chamfer
module lip_cutter(y0, r) {
  c = [y0 - r, -r];
  k = r * (1 - sin(45));
  polygon(concat([[y0 + 2, 2], [y0 + 2, -r]], [for (a = [0 : 5 : 45]) c + r * [cos(a), sin(a)]],
                 [[c[0] + r * cos(45) - k, 0], [c[0] + r * cos(45) - k, 2]]));
}

// a round-ended slot l x w in the XY plane, grown by g all round
module stadium(l, w, g) hull() for (s = [-1, 1]) translate([s * (l - w) / 2, 0]) circle(d = w + 2 * g, $fn = 24);

// a hole square through the skirt, pointed toward the skirt's foot, which is up in print
module rivet(y, sl) {
  hw = (w_aft / 2 + (w_fwd - w_aft) / 2 * (y / len + 0.5)) - bond_gap / sin(hull_angle);
  q = [hw - sl * cos(hull_angle), y, -sl * sin(hull_angle)];
  // local x along the skirt, y down the face, z into the skirt
  multmatrix([[0, -cos(hull_angle), -sin(hull_angle), q[0]],
              [1, 0, 0, q[1]],
              [0, -sin(hull_angle), cos(hull_angle), q[2]]])
    translate([0, 0, -fin_h - 1]) linear_extrude(skirt_t + fin_h + 3)
      hull() { circle(d = rivet_d, $fn = 24); translate([0, rivet_d / 2 * sqrt(2)]) square(e, center = true); }
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
  // ridges on each bonding face, keyed into the epoxy. The face toward the skirt's foot is square to the
  // skirt and takes the sump's weight; the flank toward the deck is the one that faces down in print (~70 deg)
  for (s = [-1, 1]) for (i = [0 : fin_n - 1]) hull() for (p = [[hw_a, -len / 2], [hw_f, len / 2]])
    translate([0, p[1], 0]) rotate([90, 0, 0]) linear_extrude(e, center = true)
      scale([s, 1]) fin_profile(p[0], skirt_h / sin(hull_angle) * (i + 0.5) / fin_n);
  // end arches: tie the skirts together across each end, under the deck's 15 mm end strips
  for (p = [[hw_a, -len / 2 + arch_t / 2 + e], [hw_f, len / 2 - arch_t / 2 - e]])  // e: no face shared with the deck end
    translate([0, p[1], 0]) rotate([90, 0, 0]) linear_extrude(arch_t, center = true) arch_profile(p[0]);
}

// one ridge, a slant distance sl down the outer face from its top edge at x = hw
module fin_profile(hw, sl) {
  d = [-cos(hull_angle), -sin(hull_angle)];  // down the face
  n = [sin(hull_angle), -cos(hull_angle)];   // out of the face, toward the hull
  q = [hw, 0] + sl * d;
  polygon([q + 0.2 * n, q + fin_h * n, q - fin_w * d + 0.2 * n, q - fin_w * d - 0.2 * n, q - 0.2 * n]);
}

// a half-ellipse from the foot of one skirt's inner face to the other, crown arch_band under the deck
module arch_profile(hw) {
  a = hw - run - tn;
  b = skirt_h - deck_t - arch_band;
  mid = tn / 2;  // reach into the skirts, never past their outer face
  polygon(concat(
    [[-(hw - mid), -deck_t + e], [hw - mid, -deck_t + e], [hw - run - mid, -skirt_h]],
    [for (t = [0 : 4 : 180]) [a * cos(t), -skirt_h + b * sin(t)]],
    [[-(hw - run - mid), -skirt_h]]));
}

if (part == "installed") platform();
else rotate([180, 0, 0]) platform();
