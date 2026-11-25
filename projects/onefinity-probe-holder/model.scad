// Onefinity touch-probe holder for a vertical surface: the probe drops in point first, as a diamond, and
// leans out 30 deg toward the user, its flat face resting on a support wall on the user's side; machined face
// up, toward the wall, open between the fins. The two lower edges sit in a 90 deg V; the cords leave the two upper edges.
// Probe frame: u across the face (X), v up the face, w through the thickness (+w = the support wall).
// The cradle is built in that frame, then mirrored and tilted (placed()). Its V side walls run on to the wall plate as fins;
// they run horizontally into the plate and meet it through a concave fillet. One horizontal cut on the bed ends the
// cradle, the fins and the plate; below it the probe's tip hangs free.
// Wall-side of the probe, each fin's inner face steps in over the probe's raised lip on the machined face, flush with the fin. Both screws sit at the top, above the cradle.
// Prints as installed, plate edge and foot on the bed. Every overhang is a 45 deg or steeper slope (see README).

/* [Probe: owner, caliper] */
probe_s = 63.5;     // square side
probe_t = 18.8;     // full thickness (the 9.5 mm lip along the two upper edges)

pocket_s = 54;      // machined pocket, square to the block, in the point corner
pocket_d = 3.8;     // 18.8 - 15

/* [Fit] */
fit_t = 1.0;        // slot clearance, each face
fit_v = 0.8;        // V clearance, each edge

/* [Lead-in: the V opens out toward the top so the probe finds it by sliding] */
flare = 4;          // extra clearance each side at the V's top
flare_from = 12;    // the flare starts this far up the V

/* [Cradle] */
tilt = 30;          // lean from vertical, top out toward the user
v_depth = 43;       // V sides: about half the probe (side corners at 45), high enough for the ledges to reach the lip
wall = 6;           // V arms and support wall
front_t = 3;        // the V floor runs this far past the slot toward the wall, where the plate starts
back_h = 56;        // support wall top above the point: past the probe's centre of mass (46 up), and the arc the arms end on clears the lip

edge_r = 2.5;       // rounding on the support wall's outer edge
arm_r = 2;          // rounding on the V arms' top edges
corner_r = 3;       // rounding on 2D corners

keel_r = 6;         // the V's bottom rounding (cut away by the open point)

/* [Open point: one horizontal cut, the bed, below which the probe's tip hangs free] */
open_v = 12;        // the cut meets the support wall's face this far above the probe point; the slot's wall-side face just above the point, so no sliver of floor

/* [Ledges: wall-side of the probe, each fin's inner face steps in over the raised lip (the 9.5 mm band outside the pocket)] */
ledge_in = 3;       // reach in over the lip, past the probe's edge; the pocket, pocket_d deeper, passes freely

/* [Blend: the fins meet the plate through a concave fillet] */
blend_r = 6;        // fillet radius where the fins meet the plate
blend_n = 12;       // fillet steps

/* [Wall plate: covers where the fins land; screws high, where the load pulls out] */
plate_t = 5;
plate_r = 6;        // plate corner radius
screw_d = 5;        // #8 / 4 mm wood screw, loose (printed holes run small); teardrop top
csk_d = 10;         // 90 deg countersink on the front face
screw_x = 25;
screw_zs = [45];   // just above the cradle (fins top out at 39.9): the countersink clears them for the drill, and the plate stops 11 mm above

$fn = 48;
e = 0.01;
D = probe_s * sqrt(2);                       // point to top corner
slot = probe_t + 2 * fit_t;
k = (fit_v + wall) * sqrt(2);                // outer V point below the probe point
w_back = slot / 2 + wall;
w_front = -slot / 2 - front_t;

// --- probe frame, 2D in (u, v) ---
module diamond() polygon([[0, 0], [D / 2, D / 2], [0, D], [-D / 2, D / 2]]);
module keel_v(h, y0 = 0) hull() {   // 90 deg V, point at y0 rounded to keel_r, top edge at y0 + h
    translate([0, y0 + keel_r * sqrt(2)]) circle(r = keel_r);
    translate([-h, y0 + h - e]) square([2 * h, e]);
}
module outer_v(h) keel_v(h + k, -k);
module rnd(r) offset(r = r) offset(delta = -r) children();     // round the corners of a convex 2D shape
module back_2d() intersection() {   // quarter circle: 90 deg sector about the V point, arc top at back_h; the point stays sharp
    outer_v(back_h);
    union() {
        rnd(corner_r) translate([0, -k]) circle(r = back_h + k, $fn = 96);
        intersection() { outer_v(back_h); translate([0, -k]) circle(r = 4 * corner_r); }
    }
}
// extrude children() over 0..h with the z = 0 perimeter edge rounded to radius r (convex children only)
module round_base(h, r, n = 5) hull() {
    translate([0, 0, r]) linear_extrude(h - r) children();
    for (i = [0:n]) translate([0, 0, r * (1 - sin(90 * i / n))]) linear_extrude(0.01) offset(delta = -r * (1 - cos(90 * i / n))) children();
}
module cutter_2d() union() {
    offset(delta = fit_v) hull() { diamond(); translate([0, 100]) diamond(); }
    f0 = fit_v * sqrt(2); v1 = v_depth + 30; sl = flare / (v_depth - flare_from);
    polygon([[flare_from + f0, flare_from], [v1 + f0 + sl * (v1 - flare_from), v1], [-(v1 + f0 + sl * (v1 - flare_from)), v1], [-(flare_from + f0), flare_from]]);
}

// extrude a (u, v) shape over w0..w1
module slab(w0, w1) translate([0, w1, 0]) rotate([90, 0, 0]) linear_extrude(w1 - w0) children();

module slab_r(w0, w1, r) translate([0, w1, 0]) rotate([90, 0, 0]) round_base(w1 - w0, r) children();   // outer face at w1 rounded

module arm_2d() intersection() { outer_v(v_depth); back_2d(); }
// the probe as seated (fit_v down the V), extended upward
module seated_2d() translate([0, -fit_v * sqrt(2)]) hull() { diamond(); translate([0, 100]) diamond(); }
// only over the lip: a vertical end tapers each ledge back into the fin at 45 deg, starting 4 mm below the lip
ledge_u0 = (pocket_s - 4 - ledge_in) / sqrt(2);
module ledge_2d() offset(r = arm_r) offset(delta = -arm_r) difference() {
    arm_2d();
    offset(delta = -ledge_in) seated_2d();
    translate([-ledge_u0, -50]) square([2 * ledge_u0, 200]);
}
module half_2d(i) translate([i == 0 ? -100 : 0, -100]) square([100, 300]);
module arm_side_2d(i) intersection() {   // one V arm, top edges rounded; unflared, so the fin top stands over the ledges (the slot's cutter flares it)
    offset(r = arm_r) offset(delta = -arm_r) difference() { arm_2d(); offset(delta = fit_v + 0.05) hull() { diamond(); translate([0, 100]) diamond(); } }
    half_2d(i);
}
module support_wall() slab_r(slot / 2, w_back, edge_r) offset(delta = -0.02) back_2d();   // just inside the arms: no shared faces
module cutter() slab(-slot / 2, slot / 2) cutter_2d();

// Placed: the probe frame mirrored so the support wall (+w) faces the user (-Y), then tilted so the
// top leans out toward the user; the cut plane (open_v up the support wall's face) lands on z = 0.
z_cut = open_v * cos(tilt) - slot / 2 * sin(tilt);
module placed() translate([0, 0, -z_cut]) rotate([tilt, 0, 0]) mirror([0, 1, 0]) children();
module to_wall() hull() { children(); translate([0, 100, 0]) children(); }   // swept horizontally toward the wall

// plate front face: just inside the V point's wall-side end, the cradle's nearest point to the wall
y_pf = (slot / 2 + front_t) * cos(tilt) + k * sin(tilt) - 0.5;

module plate_2d() offset(r = plate_r) offset(delta = -plate_r) hull() {   // covers where the fins land, and the screws
    offset(delta = blend_r + 2) fin_print();   // room for the fillet and a 2 mm rim
    for (x = [-screw_x, screw_x], z = screw_zs) translate([x, z]) circle(r = csk_d / 2 + plate_r);
}
module teardrop(d) hull() { circle(d = d); rotate(45) square(d / 2); }   // point up (+Y in 2D)

module plate() difference() {
    translate([0, y_pf, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) round_base(plate_t, 1.5) plate_2d();
    for (x = [-screw_x, screw_x], z = screw_zs) translate([x, y_pf, z]) {
        translate([0, plate_t + e, 0]) rotate([90, 0, 0]) linear_extrude(plate_t + 2 * e) teardrop(screw_d);
        translate([0, -e, 0]) rotate([-90, 0, 0]) cylinder(d1 = csk_d + 2 * e, d2 = screw_d, h = (csk_d - screw_d) / 2 + e);
    }
}

// Fins: each V arm swept horizontally toward the wall until it meets the plate, so they hold the cradle up.
module wall_side() translate([-100, -100, -50]) cube([200, 100 + y_pf + 1, 250]);   // in front of the wall, stopping just inside the plate
module fin(i) to_wall() placed() slab(w_front, w_back) arm_side_2d(i);
module fins() for (i = [0:1]) intersection() { fin(i); wall_side(); }
// ledges: each fin's inner face, wall-side of the probe, stepped in over the lip and swept the same way; fit_t clear of the lip
module ledges() for (i = [0:1]) intersection() { to_wall() placed() slab(-probe_t / 2 - 0.5, -probe_t / 2) intersection() { ledge_2d(); half_2d(i); } wall_side();
    hull() { fin(i); translate([i == 0 ? 12 : -12, 0, 0]) fin(i); }   // no higher than the fin top, carried level inward: the outside stays the fin's own face
}
module fin_print() projection(cut = true) translate([0, 0, y_pf + 0.5]) rotate([-90, 0, 0]) fins();   // (x, z) on the plate face
// Blend: each of the two fins is sliced parallel to the plate; each slice
// grows by the fillet's offset at that distance, and consecutive slices are hulled, so the fillet is smooth.
module piece(i) intersection() { fins(); translate([i == 0 ? -100 : 0, -100, 0]) cube([100, 300, 300]); }
module piece_cut(i, yc) projection(cut = true) translate([0, 0, yc]) rotate([-90, 0, 0]) piece(i);
module blend_layer(i, a) let(d = blend_r * (1 - cos(a)), o = blend_r * (1 - sin(a)), yc = y_pf + 0.2 - d)   // starts just inside the plate: no face shared with it
    translate([0, yc, 0]) rotate([90, 0, 0]) linear_extrude(0.01, center = true) offset(r = o + 0.02) piece_cut(i, yc - 0.01);   // just proud of the piece: no face shared with it
module blend() for (i = [0:1], j = [0:blend_n - 1]) hull() { blend_layer(i, 90 * j / blend_n); blend_layer(i, 90 * (j + 1) / blend_n); }

module holder() intersection() {
    union() {
        difference() {
            union() {
                plate();
                fins();
                placed() support_wall();
                blend();
            }
            placed() cutter();
            for (x = [-screw_x, screw_x], z = screw_zs) translate([x, y_pf - 30, z]) rotate([-90, 0, 0]) cylinder(d = csk_d, h = 30);   // screwdriver access
        }
        ledges();   // outside the blend: its hull would bridge the ledge's end flat
    }
    translate([-200, -200, 0]) cube(400);   // the open point's cut: the bed
}

show_probe = false; // preview only: the probe resting in the slot, flat face on the support wall

module probe() color("silver", 0.6) translate([0, fit_t, -fit_v * sqrt(2)]) difference() {   // resting on the V, flat face on the support wall (+w), pocket toward the wall plate
    slab(-probe_t / 2, probe_t / 2) diamond();
    slab(-probe_t / 2 - 1, -probe_t / 2 + pocket_d) scale(pocket_s / probe_s) diamond();
}

holder();
if (show_probe) placed() probe();
