// Onefinity touch-probe holder for a vertical surface: the probe drops in point first, as a diamond, and
// leans out 30 deg toward the user, its flat face resting on a support wall on the user's side; machined face
// up, toward the wall, behind a low lip. The two lower edges sit in a 90 deg V; the cords leave the two upper edges.
// Probe frame: u across the face (X), v up the face, w through the thickness (+w = the support wall).
// The cradle is built in that frame, then mirrored and tilted (placed()) and joined to a narrow wall plate by a solid gusset under its point.
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
v_depth = 40;       // V sides: up to about half the probe (side corners at 45)
wall = 6;           // V arms and support wall
front_t = 3;        // low lip on the wall side
front_h = 15;       // front lip height above the point: the top stays open
back_h = 65;        // support wall top above the point, past half the probe

edge_r = 2.5;       // rounding on the support wall's outer edge
corner_r = 3;       // rounding on 2D corners

/* [Wall plate: screws into a vertical wood surface] */
plate_x = 60;       // narrower than the body
plate_h = 66;       // bed to just above the gusset
plate_t = 5;
plate_r = 6;        // plate corner radius
plate_pt = 28;      // height of the cradle's lowest point above the plate's bottom edge
gusset_taper = 0.8; // the gusset is this much narrower at the plate, so its flanks are steeper than 45
gusset_drop = 8;    // the gusset's end on the plate sits this much lower, so its underside stays steep
screw_d = 5;        // #8 / 4 mm wood screw, loose (printed holes run small); teardrop top
csk_d = 10;         // 90 deg countersink on the front face
screw_x = 20;
screw_zs = [10];   // below the cradle point, on the plate's extension

$fn = 48;
e = 0.01;
D = probe_s * sqrt(2);                       // point to top corner
slot = probe_t + 2 * fit_t;
k = (fit_v + wall) * sqrt(2);                // outer V point below the probe point
w_back = slot / 2 + wall;
w_front = -slot / 2 - front_t;

// --- probe frame, 2D in (u, v) ---
module diamond() polygon([[0, 0], [D / 2, D / 2], [0, D], [-D / 2, D / 2]]);
module outer_v(h) polygon([[0, -k], [h + k, h], [-(h + k), h]]);
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

module cradle_outer() {
    slab(-slot / 2, w_back) intersection() { outer_v(v_depth); back_2d(); }   // the lower flanks stay sharp: a rounded downward edge goes flat
    slab(w_front, -slot / 2 + e) outer_v(front_h);
    slab_r(slot / 2, w_back, edge_r) back_2d();
}
module cutter() slab(-slot / 2, slot / 2) cutter_2d();

// Placed: the probe frame mirrored so the support wall (+w) faces the user (-Y), then tilted so the
// top leans out toward the user; the point and the low lip sit close to the wall. Lowest point on the bed.
z_low = -k * cos(tilt) - w_back * sin(tilt);
module placed() translate([0, 0, plate_pt - z_low]) rotate([tilt, 0, 0]) mirror([0, 1, 0]) children();

// plate front face: just inside the low lip's bottom edge, the cradle's nearest point to the wall
y_pf = (slot / 2 + front_t) * cos(tilt) + k * sin(tilt) - 0.5;

module teardrop(d) hull() { circle(d = d); rotate(45) square(d / 2); }   // point up (+Y in 2D)

module plate() difference() {
    translate([0, y_pf, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) round_base(plate_t, 1.5) translate([0, 0]) offset(r = plate_r) offset(delta = -plate_r) translate([-plate_x / 2, 0]) square([plate_x, plate_h]);
    for (x = [-screw_x, screw_x], z = screw_zs) translate([x, y_pf, z]) {
        translate([0, plate_t + e, 0]) rotate([90, 0, 0]) linear_extrude(plate_t + 2 * e) teardrop(screw_d);
        translate([0, -e, 0]) rotate([-90, 0, 0]) cylinder(d1 = csk_d + 2 * e, d2 = screw_d, h = (csk_d - screw_d) / 2 + e);
    }
}

// Gusset: the V profile at the lip's wall side carried straight back to the plate, dropped at the plate so the
// underside is steeper than 45. It meets the plate at a point and blends into it.
module wall_side() placed() slab(w_front + 0.1, -slot / 2 + e) outer_v(v_depth);   // flush with the V arms
module shadow() intersection() {   // the gusset's outline seen from the plate, cut off under the plate's top
    projection() rotate([-90, 0, 0]) wall_side();
    translate([-100, -100]) square([200, 100 + plate_h - 2]);
}
module wedge() hull() {
    wall_side();
    translate([0, y_pf + 1, 0]) rotate([90, 0, 0]) linear_extrude(1) hull() {   // the shadow, narrowed, plus the shadow dropped
        scale([gusset_taper, 1]) shadow();
        translate([0, -gusset_drop]) scale([gusset_taper, 1]) shadow();
    }
}

module holder() {
    difference() {
        union() {
            plate();
            placed() cradle_outer();
            wedge();
        }
        placed() cutter();
        for (x = [-screw_x, screw_x], z = screw_zs) translate([x, y_pf - 30, z]) rotate([-90, 0, 0]) cylinder(d = csk_d, h = 30);   // screwdriver access
    }
}

show_probe = false; // preview only: the probe resting in the slot, flat face on the support wall

module probe() color("silver", 0.6) translate([0, fit_t, -fit_v * sqrt(2)]) mirror([0, 1, 0]) difference() {   // resting on the V, flat face on the support wall
    slab(-probe_t / 2, probe_t / 2) diamond();
    slab(-probe_t / 2 - 1, -probe_t / 2 + pocket_d) scale(pocket_s / probe_s) diamond();
}

holder();
if (show_probe) placed() probe();
