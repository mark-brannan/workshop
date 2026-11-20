// Rudder angle sensor, rev 2: an AS5600 Hall chip reads a diametric magnet on the end of a shaft, through a closed 1 mm wall.
// Five prints: bearing body, electronics cup, magnet cap, arm, spacer sleeve. Each prints flat, no slicer supports (README).
// Frame: z up the shaft, body floor at z = 0, +x along the board's long side and the flange holes,
// the arm's centre along +y. Nothing here is measured (README).

/* [Bearings and shaft] */
bearing_id = 8;      // 608: 8 x 22 x 7, the owner's stated on-hand size. R8 and 686 sets: the test file
bearing_od = 22;
bearing_w = 7;
race_od = 12;        // inner ring's outer diameter: the cap and the hub bear on this only (guess)
race_gap_od = 19;    // outer ring's inner diameter: the cap stays inside it (guess)
bearing_span = 6;    // spacer sleeve length between the two bearings
shaft_d = 8;

/* [Magnet] */
magnet_d = 6;        // diametric disc
magnet_t = 2.5;

/* [Board: Adafruit 6357 from its Eagle .brd] */
board_l = 25.4;
board_w = 17.78;
board_t = 1.6;       // guess
board_r = 2.54;
hole_dx = 20.32;     // mounting holes, a rectangle centred on the board
hole_dy = 12.7;
hole_d = 2.5;
chip_off = [0, 0];   // chip centre from board centre
chip_h = 1.6;        // SOIC-8 above the board (guess)
tall_h = 2.95;       // tallest part above the board: the two JST SH sockets (guess)
tall = [[-10.12, 0, 4.25, 6.1], [10.12, 0, 4.25, 6.1]];   // tall parts: centre x, y from the chip, size x, y. [] for a board with none
under_board = 8;     // room under the board for the header and the plug lying flat (guess)

/* [Magnet to chip] */
floor_t = 1.0;       // closed wall under the magnet
mag_air = 0.5;       // magnet face to the wall
chip_air = 0.4;      // chip top to the wall's underside

/* [Fits: the repo's calibration table is unmeasured, so every one is a guess] */
bore_fit = 0.1;      // bearing bore over bearing_od
shaft_fit = 0.0;     // cap bore over shaft_d: press, then glue
magnet_fit = 0.1;    // cap pocket over magnet_d
clamp_fit = 0.2;     // arm bore over shaft_d, before the pinch screw closes it
board_clear = 0.5;   // cup pocket round the board, each side
pin_fit = 0.3;       // locating pin under hole_d
stud_fit = 0.15;     // cone socket over cone stud, on the radius

/* [Flange: the pedestal's seat] */
flange_pitch = 40;   // two holes on the x axis
flange_hole_d = 4.8; // M4, as the pedestal's
m4_head = 7.0;       // socket cap head, no washer (guess)
arm_zero = 90;       // arm's centre direction, degrees from the line of the flange holes
travel = 40;         // arm swing each side of centre that must leave both flange screws reachable
flange_edge = 2.6;   // plastic outside each hole
flange_t = 6;

/* [Walls] */
wall = 3;            // round the bearings
cup_wall = 3.5;
cup_floor = 2;
sleeve_wall = 1.2;   // spacer sleeve: bears on the outer races only
ledge_min = 0.8;     // seat under the lower bearing's outer race
cap_clear = 0.5;     // cap to chamber, on the radius
nose_wall = 1.2;     // cap wall round the magnet, at the magnet's face
cap_grip = 5;        // cap's hold on the shaft

/* [Arm] */
arm_radii = [60, 80, 100];  // ball stud holes; the one used equals the quadrant stud's radius. 100 is the pedestal's arm_len
arm_t = 5;
arm_w = 12;
hub_h = 10;
m3_clear = 3.4;
m3_head = 6.4;
m3_nut = 5.7;        // across flats
pinch_grip = 12;     // plastic between screw head and nut
slit_w = 1.2;

/* [Spray and drain: additions, not asked for] */
skirt_lap = 3;       // hub skirt's overlap down the body's top
skirt_gap = 0.6;
skirt_wall = 1.6;
weep_d = 2;          // drain from the magnet chamber; 0 for none

/* [Cable] */
cable_d = 5;

/* [View] */
view = "plate";      // plate | assembly | exploded | section | body_print | cup_print | cap_print | arm_print | spacer_print
rudder = 0;          // assembly only: arm angle from its centre, degrees

/* [Hidden] */
$fn = 96;
eps = 0.01;
gap = chip_air + floor_t + mag_air;                       // magnet face to chip top
nose_od = magnet_d + magnet_fit + 2*nose_wall;            // cap's end round the magnet
cap_od = max(race_od + 2, max(nose_od, shaft_d + 3));
nose_h = (cap_od - nose_od)/2;                            // 45 degree cone from the nose out to cap_od
cap_trans = max(0, (shaft_d + shaft_fit - magnet_d - magnet_fit)/2);   // 45 degree cone where the magnet is the smaller
cap_h = cap_grip + cap_trans + magnet_t;
chamber_d = cap_od + 2*cap_clear;
well_d = nose_od + 2*cap_clear;                           // chamber at the floor; it opens at 45 degrees to chamber_d
function chamber_r(z) = min(well_d/2 + max(z - floor_t, 0), chamber_d/2);
ledge_z = floor_t + mag_air + cap_h;                      // lower bearing sits here
tower_h = ledge_z + 2*bearing_w + bearing_span;
tower_od = bearing_od + bore_fit + 2*wall;
cav_l = board_l + 2*board_clear;
cav_w = board_w + 2*board_clear;
foot_l = max(flange_pitch + flange_hole_d + 2*flange_edge, tower_od + 6);
foot_w = max(cav_w + 2*cup_wall, tower_od + 6);
board_top = -(chip_air + chip_h);                         // z of the board's top face
cup_h = -board_top + board_t + under_board + cup_floor;
relief_h = tall_h - chip_h - chip_air + 0.4;              // how far the tall parts stand into the body
stud_d = 4;
stud = [cav_l/2 + 1.6 + stud_d/2, foot_w/2 - 1.6 - stud_d/2];
boss_h = 0.6;                                             // hub's step onto the inner race
hub_od = tower_od + 2*skirt_gap + 2*skirt_wall;
arm_len = max(arm_radii) + 6;
pinch_x = (shaft_d + clamp_fit)/2 + 1 + m3_clear/2;
arm_top = tower_h + boss_h + hub_h;
shaft_bot = floor_t + mag_air + magnet_t + cap_trans;
echo(gap = gap, shaft_len = arm_top - shaft_bot, cup_h = cup_h, tower_h = tower_h, foot = [foot_l, foot_w], cap_od = cap_od);

assert(gap >= 0.5 && gap <= 3, "magnet to chip is outside the AS5600's 0.5 to 3 mm");
assert(chamber_d <= bearing_od - 2*ledge_min, "the cap's chamber leaves no seat under the lower bearing: smaller cap or larger bearing");
assert(cap_od - max(magnet_d + magnet_fit, shaft_d + shaft_fit) >= 2, "cap wall under 1 mm");
assert(cav_l/2 + 1.5 <= flange_pitch/2 - flange_hole_d/2, "the board pocket reaches the flange holes: widen flange_pitch");
assert(flange_t >= 3.5, "flange too thin for the cone sockets");
assert(cap_od < race_gap_od, "the cap reaches the outer ring");
assert(chamber_d > race_od, "the lower bearing's inner ring would sit on the ledge");
assert((cap_od - race_od)/2 + nose_h <= cap_h, "cap too short for its two cones: longer cap_grip");
assert(nose_od/2 + cap_trans + magnet_t - (shaft_d + shaft_fit)/2 >= 1, "cap wall under 1 mm at the shaft's end");
assert(flange_pitch/2 - m4_head/2 >= max(tower_od/2 + 2, hub_od/2), "a flange screw head is under the tower or the hub: widen flange_pitch");
assert(flange_pitch/2*sin(arm_zero - travel) >= arm_w/2 + m4_head/2, "the arm covers a flange screw inside its travel");
// The chamber is a 45 degree funnel from a narrow well, so it passes inside the reliefs and the bearing sits above their roofs.
if (relief_h > 0) for (t = tall) {
    w = t[2] + 0.8; d = t[3] + 0.8;
    ri = norm([max(abs(t[0]) - w/2, 0), max(abs(t[1]) - d/2, 0)]);
    side = w < d ? abs(t[1]) <= d/2 : abs(t[0]) <= w/2;   // nearest face is a long side: its roof leans away at 45 degrees too
    top = relief_h + min(w, d)/2;
    assert(ri - chamber_r(side ? relief_h : top) >= 1.7, "a tall part on the board stands up into the magnet chamber: remove it or move it out");
    assert(ledge_z >= top + 1.2 || ri >= bearing_od/2 + 1.2, "a tall part's relief reaches the bearing bore: longer cap_grip");
}

// What the seat under this needs, for a model that reads this one through `use` (rudder-sensor-pedestal):
// footprint [x, y], flange [hole pitch along x, hole diameter], heights [cup floor to flange face, flange face to arm top],
// the arm's centre direction from the hole line, and the stud radii.
function sensor_foot() = [foot_l, foot_w];
function sensor_flange() = [flange_pitch, flange_hole_d];
function sensor_heights() = [cup_h, arm_top];
function sensor_arm_zero() = arm_zero;
function sensor_arm_radii() = arm_radii;
function sensor_m4_head() = m4_head;

module rrect(w, d, h, r = 4) linear_extrude(h) offset(r) square([w - 2*r, d - 2*r], center = true);
// hole along y with a pointed top: prints without support
module tear_y(d, l) rotate([90, 0, 0]) linear_extrude(l, center = true) hull() { circle(d = d); polygon([[-d/2*cos(45), d/2*sin(45)], [d/2*cos(45), d/2*sin(45)], [0, d/2*sqrt(2)]]); }
module flange_holes(z0, h) for (s = [-1, 1]) translate([s*flange_pitch/2, 0, z0]) cylinder(d = flange_hole_d, h = h);
module studs(grow = 0, point = false) for (s = [-1, 1]) translate([s*stud[0], s*stud[1], -eps])
    cylinder(d1 = stud_d + 2*grow, d2 = point ? 0 : 0.8 + 2*grow, h = point ? stud_d/2 + grow : stud_d/2 - 0.4);

// ---- bearing body: prints as modelled, floor down
module tall_reliefs() if (relief_h > 0) for (t = tall) {
    w = t[2] + 0.8; d = t[3] + 0.8;
    translate([t[0], t[1], -eps]) hull() {   // gable roof along the longer side: no flat ceiling
        translate([-w/2, -d/2, 0]) cube([w, d, relief_h]);
        if (w < d) translate([-eps, -d/2, relief_h + w/2]) cube([2*eps, d, eps]);
        else translate([-w/2, -eps, relief_h + d/2]) cube([w, 2*eps, eps]);
    }
}
module body() difference() {
    union() {
        rrect(foot_l, foot_w, flange_t);
        cylinder(d = tower_od, h = tower_h);
        translate([0, 0, flange_t - eps]) cylinder(d1 = tower_od + 4, d2 = tower_od, h = 2);
    }
    translate([0, 0, floor_t]) cylinder(d1 = well_d, d2 = chamber_d, h = (chamber_d - well_d)/2);
    translate([0, 0, floor_t + (chamber_d - well_d)/2 - eps]) cylinder(d = chamber_d, h = ledge_z - floor_t);
    translate([0, 0, ledge_z]) cylinder(d = bearing_od + bore_fit, h = tower_h);
    translate([0, 0, tower_h - 0.5]) cylinder(d1 = bearing_od + bore_fit, d2 = bearing_od + bore_fit + 1, h = 0.5 + eps);
    flange_holes(-1, flange_t + 2);
    studs(stud_fit, point = true);
    tall_reliefs();
    if (weep_d > 0) translate([0, -foot_w/2, floor_t + weep_d/2]) tear_y(weep_d, foot_w);
}

// ---- electronics cup: prints as modelled, open top up; potted to the rim
module hole_xy() for (sx = [-1, 1], sy = [-1, 1]) translate([sx*hole_dx/2 - chip_off[0], sy*hole_dy/2 - chip_off[1], 0]) children();
module cup() {
    floor_z = -cup_h + cup_floor;
    difference() {
        translate([0, 0, -cup_h]) rrect(foot_l, foot_w, cup_h);
        translate([-chip_off[0], -chip_off[1], floor_z]) rrect(cav_l, cav_w, cup_h, board_r);
        flange_holes(-cup_h - 1, cup_h + 2);
        translate([0, foot_w/2, floor_z + cable_d/2 + 0.8]) tear_y(cable_d + 0.5, foot_w - cav_w + 2);
    }
    // a post under each board hole, run back into the pocket's corner, and a pin through the hole
    intersection() {
        translate([-chip_off[0], -chip_off[1], floor_z - eps]) rrect(cav_l + 1, cav_w + 1, cup_h, board_r);
        union() {
            for (sx = [-1, 1], sy = [-1, 1]) hull() for (k = [0, 1])
                translate([sx*(hole_dx/2 + 4*k) - chip_off[0], sy*(hole_dy/2 + 4*k) - chip_off[1], floor_z - eps])
                    cylinder(d = hole_d + 2, h = board_top - board_t - floor_z + eps);
            hole_xy() translate([0, 0, floor_z]) cylinder(d = hole_d - pin_fit, h = board_top - floor_z);
        }
    }
    studs();
}

// ---- magnet cap: prints bearing side down, magnet pocket up
module cap() difference() {
    ch = (cap_od - race_od)/2;   // 45 degree chamfer: only the inner race is touched
    union() {
        cylinder(d1 = race_od, d2 = cap_od, h = ch);
        translate([0, 0, ch - eps]) cylinder(d = cap_od, h = cap_h - ch - nose_h + eps);
        translate([0, 0, cap_h - nose_h - eps]) cylinder(d1 = cap_od, d2 = nose_od, h = nose_h + eps);   // nose: clears the JST reliefs' roofs
    }
    translate([0, 0, -eps]) cylinder(d = shaft_d + shaft_fit, h = cap_grip + eps);
    translate([0, 0, cap_grip - eps]) cylinder(d1 = shaft_d + shaft_fit, d2 = magnet_d + magnet_fit, h = cap_trans + 2*eps);
    translate([0, 0, cap_grip + cap_trans]) cylinder(d = magnet_d + magnet_fit, h = magnet_t + eps);
}

// ---- spacer sleeve
module spacer() difference() {
    cylinder(d = bearing_od - 0.2, h = bearing_span);
    translate([0, 0, -eps]) cylinder(d = bearing_od - 2*sleeve_wall, h = bearing_span + 2*eps);
}

// ---- arm: prints top face down, so hub, skirt and the step onto the inner race all grow upward
module arm() difference() {
    union() {
        hull() { cylinder(d = arm_w, h = arm_t); translate([arm_len, 0, 0]) cylinder(d = arm_w, h = arm_t); }   // narrow from the hub: clear of the flange screws
        cylinder(d = hub_od, h = hub_h);
        translate([0, 0, hub_h - eps]) cylinder(d = race_od, h = boss_h + eps);
        translate([0, 0, hub_h - eps]) difference() {
            cylinder(d = hub_od, h = boss_h + skirt_lap + eps);
            translate([0, 0, -eps]) cylinder(d = hub_od - 2*skirt_wall, h = boss_h + skirt_lap + 3*eps);
        }
    }
    translate([0, 0, -eps]) cylinder(d = shaft_d + clamp_fit, h = hub_h + boss_h + 2*eps);
    translate([-hub_od, -slit_w/2, -eps]) cube([hub_od + shaft_d/2 + 2.5, slit_w, hub_h + boss_h + skirt_lap + 1]);
    translate([-pinch_x, 0, hub_h/2]) {
        tear_y(m3_clear, 2*hub_od);
        translate([0, pinch_grip/2 + hub_od/2, 0]) tear_y(m3_head, hub_od);
        translate([0, -pinch_grip/2, 0]) rotate([90, 0, 0]) rotate([0, 0, 30]) cylinder(d = m3_nut/cos(30), h = hub_od, $fn = 6);
    }
    for (r = arm_radii) translate([r, 0, -eps]) cylinder(d = m3_clear, h = arm_t + 2*eps);
}

// ---- not printed: bearings, shaft, magnet, board
// colour, then the section cut in world coordinates, so each cut face keeps its part's colour
module C(c) color(c) if (view == "section") difference() { children(); translate([-200, -400, -100]) cube(400); } else children();
module bearing(z) {
    C("silver") translate([0, 0, z]) difference() { cylinder(d = bearing_od, h = bearing_w); translate([0, 0, -eps]) cylinder(d = race_gap_od, h = bearing_w + 2*eps); }
    C("silver") translate([0, 0, z]) difference() { cylinder(d = race_od, h = bearing_w); translate([0, 0, -eps]) cylinder(d = bearing_id, h = bearing_w + 2*eps); }
    C("dimgray") translate([0, 0, z + 0.4]) difference() { cylinder(d = race_gap_od + 0.2, h = bearing_w - 0.8); translate([0, 0, -eps]) cylinder(d = race_od - 0.2, h = bearing_w); }
}
module magnet(z) for (s = [0, 1]) C(s ? "red" : "royalblue") translate([0, 0, z]) intersection() {
    cylinder(d = magnet_d, h = magnet_t);
    translate([s ? 0 : -magnet_d, -magnet_d, -1]) cube([magnet_d, 2*magnet_d, magnet_t + 2]);
}
module board(dz) {
    o = [-chip_off[0], -chip_off[1], board_top + dz];
    C("seagreen") translate(o + [0, 0, -board_t]) difference() {
        rrect(board_l, board_w, board_t, board_r);
        for (sx = [-1, 1], sy = [-1, 1]) translate([sx*hole_dx/2, sy*hole_dy/2, -1]) cylinder(d = hole_d, h = board_t + 2);
    }
    C("black") translate([-2.45, -1.95, board_top + dz]) cube([4.9, 3.9, chip_h]);
    C("ivory") for (t = tall) translate([t[0] - t[2]/2, t[1] - t[3]/2, board_top + dz]) cube([t[2], t[3], tall_h]);
    // right-angle header under the board, its pins run back under it, and the plug
    C("dimgray") translate(o + [-7.62, -board_w/2 + 1.27, -board_t - 2.54]) cube([15.24, 2.54, 2.54]);
    C("goldenrod") translate(o + [-3.9, -board_w/2 + 3.9, -board_t - 2.7]) cube([7.8, 14, 2.6]);
}
module assembly(lift = 0) {
    C("orange") body();
    C("steelblue") translate([0, 0, -3*lift]) cup();
    board(-1.5*lift);
    C("gold") translate([0, 0, ledge_z + lift]) rotate([180, 0, 0]) cap();
    C("khaki") translate([0, 0, ledge_z + bearing_w + 3*lift]) spacer();
    C("tomato") translate([0, 0, arm_top + 5.5*lift]) rotate([0, 0, arm_zero + rudder]) rotate([180, 0, 0]) arm();
    bearing(ledge_z + 2*lift);
    bearing(ledge_z + bearing_w + bearing_span + 4*lift);
    C("gainsboro") translate([0, 0, shaft_bot + lift]) cylinder(d = shaft_d, h = arm_top - shaft_bot);
    magnet(floor_t + mag_air + lift);
}
module plate() {
    body();
    translate([0, -foot_w - 6, cup_h]) cup();
    translate([-arm_len/2, foot_w/2 + hub_od/2 + 6, 0]) arm();
    translate([-foot_l/2 - cap_od/2 - 6, 0, 0]) cap();
    translate([-foot_l/2 - bearing_od/2 - 6, -foot_w, 0]) spacer();
}

if (view == "assembly") assembly();
else if (view == "exploded") assembly(12);
else if (view == "section") assembly();
else if (view == "body_print") body();
else if (view == "cup_print") translate([0, 0, cup_h]) cup();
else if (view == "cap_print") cap();
else if (view == "arm_print") arm();
else if (view == "spacer_print") spacer();
else plate();
