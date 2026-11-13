// Small enclosure for the segment display module (the one on the halmet tier).
// Two prints. The shell prints face down: its outer front face is z = 0, the
// display looks out through a window, and the board screws up against four
// posts. The back cover (part-back.scad) closes it; its four tubes press on the
// board's back, and four M2.5 x 20 self-tappers go cover -> tube -> board -> post.

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
disp_dx = 0;         // display centre off board centre; guessed centred
disp_dy = 0;
disp_recess = 0.5;   // display face sits this far behind the shell's outer face
window_clear = 0.3;  // per side around the display body

/* [Shell] */
wall = 2;
face_t = 2;
board_clear = 0.5;   // per side, board edge to inner wall
corner_r = 2;
post_d = 5.6;         // fuses into the walls
pilot_d = 2.2;       // M2.5 self-tapping into plastic, calibration pending
rear_clear = 11;     // board back to cover; header pins and wires live here

/* [Back cover] */
cover_t = 2.5;
lip_h = 2;
lip_t = 1.2;
lip_clear = 0.25;    // per side, guessed, unmeasured fit
tube_d = 4.8;
screw_clear_d = 2.9;
cable_l = 9;         // cable slot through the cover, at the -X end
cable_w = 4;
cable_x = -13;

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

module rrect(l, w, r) { offset(r = r) square([l - 2*r, w - 2*r], center = true); }

module shell() {
    difference() {
        union() {
            difference() {
                linear_extrude(shell_h) rrect(out_l, out_w, corner_r);
                translate([0, 0, face_t]) linear_extrude(shell_h) square([in_l, in_w], center = true);
            }
            for (h = holes) translate([h[0], h[1], 0]) cylinder(d = post_d, h = board_z);
        }
        translate([disp_dx, disp_dy, -1])
            linear_extrude(face_t + 2) square([disp_l + 2*window_clear, disp_w + 2*window_clear], center = true);
        for (h = holes) translate([h[0], h[1], face_t - 1]) cylinder(d = pilot_d, h = board_z);
    }
}

// Back cover, modelled as printed: outer face on the bed, lip and tubes up.
module back() {
    difference() {
        union() {
            linear_extrude(cover_t) rrect(out_l, out_w, corner_r);
            translate([0, 0, cover_t]) linear_extrude(lip_h) difference() {
                square([in_l - 2*lip_clear, in_w - 2*lip_clear], center = true);
                square([in_l - 2*lip_clear - 2*lip_t, in_w - 2*lip_clear - 2*lip_t], center = true);
            }
            for (h = holes) translate([h[0], h[1], 0]) cylinder(d = tube_d, h = cover_t + rear_clear);
        }
        for (h = holes) translate([h[0], h[1], -1]) cylinder(d = screw_clear_d, h = cover_t + rear_clear + 2);
        translate([cable_x, 0, -1]) linear_extrude(cover_t + lip_h + 2) rrect(cable_l, cable_w, cable_w/2 - 0.01);
    }
}

module board() {
    color("darkgreen") translate([0, 0, board_z]) linear_extrude(board_t) difference() {
        square([board_l, board_w], center = true);
        for (h = holes) translate(h) circle(d = hole_d);
    }
    color("dimgray") translate([disp_dx, disp_dy, disp_recess]) linear_extrude(disp_h) square([disp_l, disp_w], center = true);
}

if (part == "shell") shell();
else if (part == "back") back();
else {
    shell();
    %board();
    translate([0, 0, shell_h + cover_t]) mirror([0, 0, 1]) back();
}
