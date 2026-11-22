// Onefinity touch-probe holder for a vertical surface: the probe drops in point first, as a diamond, and
// leans out 20 deg toward the user, its flat face resting on a support wall on the user's side; machined face
// up, toward the wall, behind a low lip. The two lower edges sit in a 90 deg V; the cords leave the two upper edges.
// Probe frame: u across the face (X), v up the face, w through the thickness (+w = the support wall).
// The cradle is built in that frame, then mirrored and tilted (placed()) and joined to the wall plate by fins.
// Prints as installed, plate edge and foot on the bed. Every overhang is a 45 deg or steeper slope (see README).

/* [Probe: owner, caliper] */
probe_s = 63.5;     // square side
probe_t = 18.8;     // full thickness (the 9.5 mm lip along the two upper edges)

pocket_s = 54;      // machined pocket, square to the block, in the point corner
pocket_d = 3.8;     // 18.8 - 15

/* [Fit] */
fit_t = 0.6;        // slot clearance, each face
fit_v = 0.6;        // V clearance, each edge

/* [Cradle] */
tilt = 20;          // lean from vertical, top out toward the user
v_depth = 42;       // V sides: up to about half the probe (side corners at 45)
wall = 4;           // V arms and support wall
front_t = 3;        // low lip on the wall side
front_h = 15;       // front lip height above the point: the top stays open
back_h = 65;        // support wall top above the point, past half the probe

/* [Wall plate: screws into a vertical wood surface] */
plate_x = 100;
plate_h = 85;
plate_t = 5;
screw_d = 5;        // #8 / 4 mm wood screw, loose (printed holes run small); teardrop top
csk_d = 10;         // 90 deg countersink on the front face
screw_x = 40;
screw_zs = [12, 75];   // below and above the cradle, clear of the V sides

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
module back_2d() intersection() {   // quarter circle: 90 deg sector about the V point, arc top at back_h
    outer_v(back_h);
    translate([0, -k]) circle(r = back_h + k, $fn = 96);
}
module cutter_2d() offset(delta = fit_v) hull() { diamond(); translate([0, 100]) diamond(); }

// extrude a (u, v) shape over w0..w1
module slab(w0, w1) translate([0, w1, 0]) rotate([90, 0, 0]) linear_extrude(w1 - w0) children();

module cradle_outer() {
    slab(-slot / 2, w_back) outer_v(v_depth);
    slab(w_front, -slot / 2 + e) outer_v(front_h);
    slab(slot / 2 - e, w_back) back_2d();
}
module cutter() slab(-slot / 2, slot / 2) cutter_2d();

// Placed: the probe frame mirrored so the support wall (+w) faces the user (-Y), then tilted so the
// top leans out toward the user; the point and the low lip sit close to the wall. Lowest point on the bed.
z_low = -k * cos(tilt) - w_back * sin(tilt);
module placed() translate([0, 0, 0.5 - z_low]) rotate([tilt, 0, 0]) mirror([0, 1, 0]) children();

// plate front face: just inside the low lip's bottom edge, the cradle's nearest point to the wall
y_pf = (slot / 2 + front_t) * cos(tilt) + k * sin(tilt) - 0.5;

module teardrop(d) hull() { circle(d = d); rotate(45) square(d / 2); }   // point up (+Y in 2D)

module plate() difference() {
    translate([-plate_x / 2, y_pf, 0]) cube([plate_x, plate_t, plate_h]);
    for (x = [-screw_x, screw_x], z = screw_zs) translate([x, y_pf, z]) {
        translate([0, plate_t + e, 0]) rotate([90, 0, 0]) linear_extrude(plate_t + 2 * e) teardrop(screw_d);
        translate([0, -e, 0]) rotate([-90, 0, 0]) cylinder(d1 = csk_d + 2 * e, d2 = screw_d, h = (csk_d - screw_d) / 2 + e);
    }
}

module bottom(h) intersection() { placed() cradle_outer(); translate([-100, -100, 0]) cube([200, 200, h]); }

module holder() {
    difference() {
        union() {
            plate();
            placed() cradle_outer();
            hull() { bottom(12); linear_extrude(0.5) projection() bottom(12); }   // a flat foot on the bed
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
