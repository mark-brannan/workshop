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

/* [Tie eyes: a lug off each deck end under each wing tip; a tie runs fore-aft over the wing against the box body,
   wraps both tips and passes down through these, so the wing can't slide fore or aft] */
tie_eye_x = 94.5;    // slot centre from the centreline: under the wing tip's furthest point (x 93 to 96.6), beside the body
tie_eye_slot = [6.5, 2.2];  // x, y: a 4.8 x 1.3 tie with room
tie_eye_gap = 2;     // deck end to the slot: clears the wing tip, which overhangs the deck end by up to 1.5
tie_eye_wall = 2;    // lug wall beside the slot, across x
tie_eye_bar = 3;     // outer bar, along y: the tie wraps round it
tie_eye_lead = 1;    // fairlead: a groove the slot's width down the bar's outer face, so the tie's return strand stays in line
tie_eye_h = 5;       // down from the deck top: 1 below the deck, onto the end arch; clear of the hull at the forward end

e = 0.01;
run = skirt_h / tan(hull_angle);              // inward step of the skirt over its depth
tn = skirt_t / sin(hull_angle);               // skirt thickness, measured across X

// deck and skirts apart: a hull() of whole end sections would fill the space under the deck
module platform() difference() {
  frame();
  for (h = holes) translate([h[0], h[1], -boss_h - e]) cylinder(d = hole_d, h = boss_h + 2 * e, $fn = 24);
  translate([-opening[0] / 2, -opening[1] / 2, -deck_t - e]) cube([opening[0], opening[1], deck_t + 2 * e]);
  for (s = [-1, 1], f = [-1, 1]) scale([s, f, 1])
    translate([tie_eye_x - tie_eye_slot[0] / 2, len / 2 + tie_eye_gap, -tie_eye_h - 1]) {
      cube([tie_eye_slot[0], tie_eye_slot[1], tie_eye_h + 2]);
      translate([0, tie_eye_slot[1] + tie_eye_bar - tie_eye_lead, 0]) cube([tie_eye_slot[0], tie_eye_lead + 1, tie_eye_h + 2]);
    }
  // a hole that meets a boss stops at it, so the pilot keeps its wall
  difference() {
    for (s = [-1, 1]) scale([s, 1, 1]) for (r = [0 : len(rivet_rows) - 1])
      for (y = [-rivet_reach + r * rivet_pitch / 2 : rivet_pitch : rivet_reach]) rivet(y, rivet_rows[r]);
    for (h = holes) translate([h[0], h[1], -boss_h - 1]) cylinder(d = boss_d + 1, h = boss_h + 1, $fn = 32);  // +1: no face shared with the boss
  }
}

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
  // tie eyes: a lug off each end of the deck under each wing tip, the slot through it vertical (no overhang in print)
  for (s = [-1, 1], f = [-1, 1]) scale([s, f, 1])
    translate([tie_eye_x - tie_eye_slot[0] / 2 - tie_eye_wall, len / 2 - e, -tie_eye_h])
      cube([tie_eye_slot[0] + 2 * tie_eye_wall, tie_eye_gap + tie_eye_slot[1] + tie_eye_bar + e, tie_eye_h]);
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
