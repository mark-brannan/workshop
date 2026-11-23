// HALMET piezo pod: an open hood that holds the buzzer-on-FET carrier on an engine-room bulkhead.
// Origin: back face (against the bulkhead), bottom edge, centred across.
// X across the bulkhead, Y out from it, Z up. Print as modelled: open bottom on the bed.
// The carrier (FET, resistors, diode, 3-pin terminal) slides up from below in two side-wall
// grooves until its top edge stops at the groove ends; the buzzer is stacked on its front face,
// port facing out, open to the air. A 45-degree gable roof sheds drips; the bottom is open so
// water drains and the cable comes in from below. One zip tie through the two low wall slots
// holds the cable and stops the carrier sliding out; snip it to service the carrier.

/* [Carrier and buzzer: not yet bought, so room, not calipers] */
carrier_w = 25;       // widest carrier the grooves take
carrier_h = 30;       // carrier height, bottom terminal included
carrier_t = 1.6;      // guessed, standard PCB
comp_h = 11;          // tallest part on the carrier's front: the screw terminal, guessed
buzzer_d = 12;        // drawing and tests only: the hood has no front wall
buzzer_h = 9.5;       // buzzer body above the carrier's front face
fit = 0.3;            // per side, carrier in its groove; guessed, uncalibrated

/* [Hood] */
plate_t = 3;          // back plate, against the bulkhead
wall = 3;             // side walls
groove_d = 1.5;       // groove depth into each side wall
back_gap = 3;         // carrier's back face off the plate: solder stubs
front_clear = 1;      // side walls stand this far past the tallest part
roof_t = 2;           // roof thickness, square to its slope
bottom_gap = 8;       // carrier's bottom edge above the hood's: cable bend and the tie
top_clear = 2;        // groove end to the roof's eave inside

/* [Mounting] */
ear_w = 12;           // ear past each side wall
ear_h = 22;           // ear height from the bottom
screw_d = 4.5;        // #8 or M4 pan head into the bulkhead; teardrop, point up

/* [Zip tie] */
tie_w = 4.5;          // slot height: ties to 3.6 wide
tie_t = 2;            // slot width: ties to 1.5 thick
tie_z = 1.5;          // slot bottom above the hood's bottom

/* [Hidden] */
$fn = 48;
eps = 0.01;
in_w = carrier_w + 2*fit - 2*groove_d;           // between the side walls
out_w = in_w + 2*wall;
depth = plate_t + back_gap + carrier_t + comp_h + front_clear;
carrier_y = plate_t + back_gap;                  // carrier's back face
carrier_z = bottom_gap;
groove_top = carrier_z + carrier_h + fit;
eave = groove_top + groove_d + top_clear;        // inner roof starts here at the walls
peak_in = eave + in_w/2;
rise = roof_t * sqrt(2);                         // vertical offset of a 45-degree roof roof_t thick
peak_out = peak_in + rise;
eave_out = eave - wall + rise;                   // where the outer roof meets the wall's outside
height = peak_out;
ear_x = out_w/2 + ear_w/2;
tie_y = plate_t + 0.5;

// Outer profile in XZ: walls and the gable.
module outer_2d() {
    polygon([[-out_w/2, 0], [out_w/2, 0], [out_w/2, eave_out], [0, peak_out], [-out_w/2, eave_out]]);
}
module inner_2d() {
    polygon([[-in_w/2, -1], [in_w/2, -1], [in_w/2, eave], [0, peak_in], [-in_w/2, eave]]);
}
module plate_2d() {
    outer_2d();
    translate([-out_w/2 - ear_w, 0]) square([out_w + 2*ear_w, ear_h]);
}

// Extrude an XZ profile along +Y from y0 to y1.
module along_y(y0, y1) { translate([0, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0) children(); }

// Teardrop in XZ, point up, radius r.
module teardrop_2d(r) { hull() { circle(r); translate([0, r*sqrt(2) - eps]) square(eps*2, center = true); } }

module groove(side) {
    // Open at the bottom; the top end rises at 45 degrees toward the cavity, so it holds itself up.
    x_deep = side * (in_w/2 + groove_d);
    x_face = side * in_w/2;
    y0 = carrier_y - fit;
    yl = carrier_t + 2*fit;
    hull() {
        translate([min(x_deep, x_face), y0, -1]) cube([groove_d, yl, groove_top + 1]);
        translate([x_face - side*eps - eps/2, y0, -1]) cube([eps, yl, groove_top + groove_d + 1]);
    }
}

module tie_slot() {
    // Through both side walls along X; pointed top.
    translate([0, 0, 0]) rotate([0, 90, 0]) linear_extrude(out_w + 2, center = true)
        // In this frame the 2D x is -Z and 2D y is Y.
        translate([-(tie_z + tie_w/2), tie_y + tie_t/2])
            hull() {
                square([tie_w, tie_t], center = true);
                translate([-tie_w/2 - tie_t/2, 0]) square(eps, center = true);
            }
}

module screw_holes() {
    for (s = [-1, 1]) translate([s * ear_x, plate_t + 1, ear_h/2])
        rotate([90, 0, 0]) linear_extrude(plate_t + 2) teardrop_2d(screw_d/2);
}

module pod() {
    difference() {
        union() {
            along_y(0, plate_t) plate_2d();
            along_y(plate_t - eps, depth) difference() { outer_2d(); inner_2d(); }
        }
        groove(1);
        groove(-1);
        tie_slot();
        screw_holes();
    }
}

// Stand-ins for the drawing only.
module carrier_standin() {
    color("seagreen") translate([-carrier_w/2, carrier_y, carrier_z]) cube([carrier_w, carrier_t, carrier_h]);
    color("dimgray") translate([0, carrier_y + carrier_t, carrier_z + carrier_h - buzzer_d/2 - 2])
        rotate([-90, 0, 0]) cylinder(d = buzzer_d, h = buzzer_h);
}

show = "pod";  // [pod, assembly]
if (show == "assembly") { color("orange") pod(); carrier_standin(); }
else pod();
