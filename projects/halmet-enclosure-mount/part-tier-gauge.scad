// Tier fit gauge: two flat plates with square, parallel sides, one per display module.
// Every size is a parameter, so the plate's width and length can be calipered against the
// numbers below and the holes checked against the module itself. Not the photocell.
// The centre is cut out, leaving a band `rim` wide, so the board shows through. Print flat.

/* [What to print] */
which = "both";        // [both, seg, oled]

/* [Segment display: TM1637 board, holes calipered by the owner (parts.md)] */
seg_hole_dx = 37.5;    // hole centre to centre, along the board's length
seg_hole_dy = 19;      // across the board
/* [OLED: SSD1306 0.96", generic drawing, caliper the one in hand] */
oled_hole_dx = 23.3;
oled_hole_dy = 23.6;

/* [Gauge] */
hole_d = 2.8;          // M2.5 clearance; the tier uses 2.8
margin = 4;            // plate edge beyond each hole's outer edge
thickness = 3;         // thick enough to stay stiff in the hand
rim = 8;               // width of the solid band round the plate; the centre inside it is cut out (0 = solid)
gap = 8;               // between the two plates when both are printed

/* [Hidden] */
$fn = 48;
// Plate size is the hole centre spacing plus 2 * (margin + hole_d / 2): the plate edge sits
// `margin` outside each hole's outer edge, so outer-edge-to-outer-edge of the holes is
// spacing + hole_d, and the plate is that plus 2 * margin.
function plate_w(dx) = dx + hole_d + 2 * margin;
function plate_l(dy) = dy + hole_d + 2 * margin;

module plate(dx, dy) {
    linear_extrude(thickness) difference() {
        square([plate_w(dx), plate_l(dy)], center = true);
        if (rim > 0) square([plate_w(dx) - 2 * rim, plate_l(dy) - 2 * rim], center = true);
        for (sx = [-1, 1], sy = [-1, 1]) translate([sx * dx / 2, sy * dy / 2]) circle(d = hole_d);
    }
}

sw = plate_w(seg_hole_dx);
ow = plate_w(oled_hole_dx);
if (which == "seg") plate(seg_hole_dx, seg_hole_dy);
else if (which == "oled") plate(oled_hole_dx, oled_hole_dy);
else {
    translate([0, -(plate_l(seg_hole_dy) + gap) / 2 ]) plate(seg_hole_dx, seg_hole_dy);
    translate([0, (plate_l(oled_hole_dy) + gap) / 2]) plate(oled_hole_dx, oled_hole_dy);
}
