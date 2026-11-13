// Small enclosure for the TM1637 4-digit segment display module.
// Two prints. The shell prints face down: its outer front face is z = 0, the
// display looks out through a window, and the board's front rests on four posts
// fused into the corners. The module's right-angle header is on the board's
// front at the -X end; its bent pins point out along -X and the Dupont plug
// goes on at an angle to the side, through an opening in the -X end wall. The back cover (part-back.scad)
// closes the box: a tongue fills the end-wall notch above the plug, four tubes
// press on the board's flat back, and four M2.5 x 12 self-tappers go
// cover -> tube -> board -> post.

/* [Board] (calipers, owner) */
board_l = 41.5;
board_w = 23.5;
board_t = 1.6;       // guessed, standard PCB
hole_dx = 37.5;      // centre to centre, long side
hole_dy = 19;        // centre to centre, short side
hole_d = 2.8;

/* [Display] (calipers, owner) */
disp_l = 30;
disp_w = 14;
disp_h = 7;          // display face above the board's front
disp_dx = -0.75;     // toward the header (-X): pin end 5 (owner, exact); clean end measured 7.1, 6.5 by difference
disp_dy = -0.25;     // 4.5 to the -Y edge, 5 to +Y (caliper); -Y is the bottom edge seen from the front, pins on the right
disp_recess = 0.5;   // display face sits this far behind the shell's outer face
window_clear = 0.3;  // per side around the display body

/* [Header] (owner, caliper) */
hdr_w = 10.2;        // 4 pins x 2.54
pin_span = 5;        // board's back surface to the top of the pins' bend
pin_out = 6.8;       // pins past the board edge
plug_clear = 0.4;    // added to the opening's height and per side of its width

/* [Shell] */
wall = 2;
face_t = 2;
board_clear = 0.5;   // per side, board edge to inner wall
corner_r = 2;
post_d = 5;
pilot_d = 2.2;       // M2.5 self-tapping into plastic, calibration pending
rear_clear = 3;      // board back to cover: solder joints only

/* [Back cover] */
cover_t = 2.5;
lip_h = 2;
lip_t = 1.2;
lip_clear = 0.25;    // per side, guessed, unmeasured fit
tube_d = 4.8;
screw_clear_d = 2.9;

part = "shell";      // shell | back | assembly

/* [Hidden] */
$fn = 48;
in_l = board_l + 2*board_clear;
in_w = board_w + 2*board_clear;
out_l = in_l + 2*wall;
out_w = in_w + 2*wall;
board_z = disp_recess + disp_h;            // board front face
shell_h = board_z + board_t + rear_clear;  // rim
holes = [for (sx = [-1, 1], sy = [-1, 1]) [sx*hole_dx/2, sy*hole_dy/2]];
notch_w = hdr_w + 2*plug_clear + 0.5;
notch_z = board_z + board_t - pin_span - plug_clear;  // bottom of the end-wall opening
tongue_clear = 0.2;

module rrect(l, w, r) { offset(r = r) square([l - 2*r, w - 2*r], center = true); }

// Keep-out for the display body inside the shell.
module disp_keepout() {
    translate([disp_dx, disp_dy, 0])
        square([disp_l + 2*window_clear, disp_w + 2*window_clear], center = true);
}

// Corner post: a round boss around the hole, filled out to the corner walls,
// clipped clear of the display body.
module posts_2d() {
    difference() {
        for (h = holes) hull() {
            translate(h) circle(d = post_d);
            translate([sign(h[0])*in_l/2, sign(h[1])*in_w/2]) square(0.01, center = true);
            translate([sign(h[0])*in_l/2, h[1]]) square(0.01, center = true);
            translate([h[0], sign(h[1])*in_w/2]) square(0.01, center = true);
        }
        disp_keepout();
    }
}

module shell() {
    difference() {
        union() {
            difference() {
                linear_extrude(shell_h) rrect(out_l, out_w, corner_r);
                translate([0, 0, face_t]) linear_extrude(shell_h) square([in_l, in_w], center = true);
            }
            linear_extrude(board_z) posts_2d();
        }
        translate([0, 0, -1]) linear_extrude(face_t + 2) disp_keepout();
        for (h = holes) translate([h[0], h[1], face_t - 1]) cylinder(d = pilot_d, h = board_z);
        // header end: open from the rim down to the bottom of the plug window
        translate([-out_l/2 - 1, -notch_w/2, notch_z]) cube([wall + 2, notch_w, shell_h]);
    }
}

// Back cover, modelled as printed: outer face on the bed, lip, tubes and tongue up.
module back() {
    tongue_h = shell_h - (board_z + board_t);   // fills the notch from the rim down to the board's back
    difference() {
        union() {
            linear_extrude(cover_t) rrect(out_l, out_w, corner_r);
            translate([0, 0, cover_t]) linear_extrude(lip_h) difference() {
                square([in_l - 2*lip_clear, in_w - 2*lip_clear], center = true);
                square([in_l - 2*lip_clear - 2*lip_t, in_w - 2*lip_clear - 2*lip_t], center = true);
            }
            for (h = holes) translate([h[0], h[1], 0]) cylinder(d = tube_d, h = cover_t + rear_clear);
            // tongue sits in the -X end wall's notch
            translate([-out_l/2, -(notch_w/2 - tongue_clear), 0])
                cube([wall, notch_w - 2*tongue_clear, cover_t + tongue_h]);
        }
        for (h = holes) translate([h[0], h[1], -1]) cylinder(d = screw_clear_d, h = cover_t + rear_clear + 2);
    }
}

// Stand-ins for review renders only: board, display, header and plug.
module module_standin() {
    translate([0, 0, board_z]) linear_extrude(board_t) difference() {
        square([board_l, board_w], center = true);
        for (h = holes) translate(h) circle(d = hole_d);
    }
    translate([disp_dx, disp_dy, disp_recess]) linear_extrude(disp_h) square([disp_l, disp_w], center = true);
    pz = board_z + board_t - pin_span;
    translate([-board_l/2 - pin_out, -hdr_w/2, pz]) cube([pin_out + 2.5, hdr_w, 2.54]);   // header + bent pins
}

if (part == "shell") shell();
else if (part == "back") back();
else {
    shell();
    module_standin();
    translate([0, 0, shell_h + cover_t + 10]) mirror([0, 0, 1]) back();  // exploded 10 mm
}
