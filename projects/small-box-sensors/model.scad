// Carrier for two stacked Adafruit STEMMA QT boards (25.4 x 17.78, holes 20.32 x 12.7) in the 63 x 58 x 35 box.
// Screws to the box's two floor bosses; four M2.5 x 20 screws come up through the posts, the lower board,
// the spacer and the upper board, with nuts on top. Print as shown: plate on the bed, posts up, no supports.
include <box.scad>
part = "carrier";    // carrier | spacer

/* [Plate] */
plate_l = 55;        // x; inside the 58 floor, clear of the short walls
plate_w = 21;        // y
plate_t = 2;
plate_y = -4;        // plate and stack centre, off the box centre, away from the connector wall
corner_r = 2;

/* [Floor bosses] */
slot_w = 3.4;        // M3 self-tapper clearance
slot_play = 4;       // each way along x; covers the 39 to 47 guess for the boss pitch

/* [Board bays] */
hole_dx = 20.32;     // Adafruit board file
hole_dy = 12.7;
post_h = 3;          // lower board's underside above the plate; clears its solder joints
post_d = 5.5;
screw_d = 2.9;       // M2.5 clearance, printed
head_d = 5;          // M2.5 pan head, in a pocket under the plate
head_h = 1.2;        // pocket depth; the rest of the head hangs in the 4 mm under the plate
spacer_h = 8;        // between the boards; room for the lower board's parts and its plugs
spacer_d = 5;
spacer_web = 1.6;    // bars joining the spacer tubes in pairs

/* [Hidden] */
$fn = 48;
posts = [for (sx = [-1, 1], sy = [-1, 1]) [sx*hole_dx/2, plate_y + sy*hole_dy/2]];

module rrect(l, w, r) { hull() for (sx = [-1, 1], sy = [-1, 1]) translate([sx*(l/2 - r), sy*(w/2 - r)]) circle(r = r); }

module carrier() {
    difference() {
        union() {
            linear_extrude(plate_t) union() {
                translate([0, plate_y]) rrect(plate_l, plate_w, corner_r);
                rrect(plate_l, 10, corner_r);                      // boss tabs sit on the box centre line
            }
            for (p = posts) translate([p[0], p[1], 0]) cylinder(d = post_d, h = plate_t + post_h);
        }
        for (sx = [-1, 1]) translate([sx*boss_pitch/2, 0, -1]) linear_extrude(plate_t + 2)
            hull() for (d = [-slot_play, slot_play]) translate([d, 0]) circle(d = slot_w);
        for (p = posts) translate([p[0], p[1], -1]) {
            cylinder(d = screw_d, h = plate_t + post_h + 2);
            cylinder(d = head_d, h = head_h + 1);
        }
        translate([0, plate_y, -1]) linear_extrude(plate_t + 2) rrect(hole_dx - post_d - 3, hole_dy - 2, 2);   // lightening window
    }
}

module spacer() {
    difference() {
        union() {
            for (p = posts) translate([p[0], p[1] - plate_y, 0]) cylinder(d = spacer_d, h = spacer_h);
            for (sy = [-1, 1]) translate([-hole_dx/2, sy*hole_dy/2 - spacer_web/2, 0]) cube([hole_dx, spacer_web, spacer_web]);   // bars on the long sides only: the ends stay open for the plugs
        }
        for (p = posts) translate([p[0], p[1] - plate_y, -1]) cylinder(d = screw_d, h = spacer_h + 2);
    }
}

if (part == "carrier") carrier();
if (part == "spacer") spacer();
