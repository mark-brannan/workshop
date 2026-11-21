// Desk presence sensor: D1 mini (ESP8266), LD2410C radar, SSD1306 OLED and a
// TM1637 4-digit display in one slim box that tapes flat to a monitor arm.
//
// Shell prints face down: the outer front face is z = 0, X is across (45 wide),
// Y is up the box as mounted (+Y top, where the USB cable leaves). Seen from the
// front, X is mirrored. Top to bottom: D1 mini (USB plug through the top wall),
// radar (no hole: it looks through the face), OLED window, TM1637 window.
// The back cover (part-cover.scad) is the flat face that tapes to the arm;
// four M3 countersunk screws go into heat-set inserts in the shell's side posts.
// Every board is on Dupont jumpers; the depth is set by the D1 mini's jumpers.

/* [Box] */
box_w = 45;          // matches the monitor arm stem
wall = 1.5;          // sides; the TM1637 board leaves 0.25 per side at 45 wide
face_t = 1.5;        // front face; the radar looks through it
corner_r = 3;        // vertical corners
face_chamfer = 0.8;  // 45 deg on the front edge (it faces the bed)
gap = 2.5;           // between board zones, Y

/* [TM1637, bottom] (owner, caliper, from segment-display-enclosure) */
tm_l = 41.5;
tm_w = 23.5;
tm_t = 1.6;          // guessed, standard PCB
tm_hole_dx = 37.5;
tm_hole_dy = 19;
tm_disp_l = 30;
tm_disp_w = 14;
tm_disp_h = 7;       // display face above the board's front
tm_disp_dx = -0.75;  // toward the header end (-X)
tm_disp_dy = -0.25;
tm_recess = 0.5;     // display face behind the outer face
tm_clear = 0.25;     // board edge to wall, per side
tm_pilot_d = 2.2;    // M2.5 self-tapping, calibration pending
tm_post_d = 5;
win_clear = 0.3;     // per side around the display body

/* [OLED, middle] (generic drawing, not calipered) */
ol_w = 27.3;         // X
ol_h = 27.8;         // Y, header at the top edge, pins out the back
ol_hole_dx = 23.3;
ol_hole_dy = 23.6;
ol_glass_h = 2.4;    // guessed: board front to glass face
ol_glass_w = 26.7;   // guessed, typical 0.96" glass
ol_glass_l = 19.3;
ol_glass_dy = 0;     // guessed: glass centred between the hole rows
ol_win_w = 24;       // active area 21.7 x 10.9 plus margin
ol_win_h = 13;
ol_win_dy = 1.5;     // guessed: active area above the board centre (header end)
ol_gap = 0.3;        // glass face to the face interior
ol_pilot_d = 1.6;    // M2 self-tapping, calibration pending
ol_post_d = 3.6;

/* [LD2410C radar] (vendor, not calipered) */
rd_w = 22;           // X
rd_h = 16;           // Y
rd_slack = 0.5;      // per side
rd_rib_t = 1.2;
rd_rib_h = 4;        // above the face interior

/* [D1 mini, top] (vendor drawing, not calipered) */
d1_l = 34.2;         // Y, USB end up
d1_w = 25.6;         // X
d1_t = 1;
d1_front_z = 8;      // board's component side, from the outer face
d1_usb_over = 1;     // socket proud of the board end, guessed
d1_shield_h = 3.2;   // ESP-12 can above the board, guessed
d1_shield_dy = -13;  // shield centre from the board's top (USB) end, guessed
tape_t = 1;          // foam tape between the can and its pad
d1_slack = 0.5;
d1_rib_t = 1.2;
d1_rib_leg = 5;
jumper_h = 16.5;     // header plastic + Dupont housing behind the board
bend = 5;            // jumper wire bend room before the cover

/* [USB plug] (guessed: overmolds vary) */
usb_w = 12;
usb_h = 8;

/* [Cover and screws] */
cover_t = 2.5;
lip_h = 2;
lip_t = 1.2;
lip_clear = 0.25;
post_d = 6.5;
insert_d = 4.2;      // M3 heat-set insert, calibration pending
insert_depth = 6;
screw_d = 3.4;
csk_d = 6.4;         // M3 countersunk head

view = "shell";      // shell | cover | assembly

/* [Hidden] */
$fn = 48;
in_w = box_w - 2*wall;
// Zones, Y from the inner bottom wall up.
tm_cy = tm_clear + tm_w/2;
ol_cy = tm_w + 2*tm_clear + gap + ol_h/2;
rd_cy = ol_cy + ol_h/2 + gap + rd_rib_t + rd_slack + rd_h/2;
d1_cy = rd_cy + rd_h/2 + rd_slack + rd_rib_t + gap + d1_slack + d1_l/2;
in_h = d1_cy + d1_l/2 + d1_usb_over;
out_h = in_h + 2*wall;
shell_h = d1_front_z + d1_t + jumper_h + bend;   // rim, from the outer face
box_d = shell_h + cover_t;
tm_board_z = tm_recess + tm_disp_h;
ol_board_z = face_t + ol_gap + ol_glass_h;
usb_z = d1_front_z - 1.4;                        // socket centre: 2.8 tall on the board front
pad_top = d1_front_z - d1_shield_h - tape_t;
tm_holes = [for (sx = [-1, 1], sy = [-1, 1]) [sx*tm_hole_dx/2, tm_cy + sy*tm_hole_dy/2]];
ol_holes = [for (sx = [-1, 1], sy = [-1, 1]) [sx*ol_hole_dx/2, ol_cy + sy*ol_hole_dy/2]];
post_x = in_w/2 - post_d/2 + 0.5;               // fused into the side walls
posts = [for (sx = [-1, 1], y = [ol_cy, d1_cy - d1_l/2 + 4]) [sx*post_x, y]];
cy0 = in_h/2;                                    // box centre, Y

module rrect(w, h, r) { offset(r = r) square([w - 2*r, h - 2*r], center = true); }
module outline(grow = 0) { translate([0, cy0]) rrect(box_w + 2*grow, out_h + 2*grow, corner_r + grow); }

module tm_disp_keepout() {
    translate([tm_disp_dx, tm_cy + tm_disp_dy])
        square([tm_disp_l + 2*win_clear, tm_disp_w + 2*win_clear], center = true);
}
module ol_glass_keepout() {
    translate([0, ol_cy + ol_glass_dy]) square([ol_glass_w + 0.6, ol_glass_l + 0.6], center = true);
}

// TM1637 corner posts, filled out to the side walls, clipped clear of the display.
module tm_posts_2d() {
    difference() {
        for (h = tm_holes) hull() {
            translate(h) circle(d = tm_post_d);
            translate([sign(h[0])*in_w/2, h[1]]) square([0.01, tm_post_d], center = true);
        }
        tm_disp_keepout();
    }
}

module ol_posts_2d() {
    difference() {
        for (h = ol_holes) translate(h) circle(d = ol_post_d);
        ol_glass_keepout();
    }
}

// Four L-ribs locate the D1 mini's corners; its sides stay open for the reset button.
module d1_ribs_2d() {
    ix = d1_w/2 + d1_slack; iy = d1_l/2 + d1_slack; t = d1_rib_t;
    for (sx = [-1, 1], sy = [-1, 1]) translate([0, d1_cy]) scale([sx, sy]) {
        translate([ix, iy - d1_rib_leg + t]) square([t, d1_rib_leg]);
        translate([ix - d1_rib_leg + t, iy]) square([d1_rib_leg, t]);
    }
}

module rd_ribs_2d() {
    translate([0, rd_cy]) difference() {
        square([rd_w + 2*(rd_slack + rd_rib_t), rd_h + 2*(rd_slack + rd_rib_t)], center = true);
        square([rd_w + 2*rd_slack, rd_h + 2*rd_slack], center = true);
        square([rd_w - 6, rd_h + 10], center = true);   // open top and bottom for the jumpers and a glue tool
    }
}

// The USB plug hole in the top wall: a 45 deg gable over the plug, no flat ceiling.
module usb_hole() {
    translate([0, in_h - 1, 0]) rotate([-90, 0, 0]) linear_extrude(wall + 2)
        translate([0, -usb_z]) union() {
            square([usb_w, usb_h], center = true);
            translate([0, -usb_h/2]) rotate(45) square(usb_w/sqrt(2), center = true);
        }
}

module shell() {
    difference() {
        union() {
            difference() {
                hull() {
                    linear_extrude(0.01) offset(delta = -face_chamfer) outline();
                    translate([0, 0, face_chamfer]) linear_extrude(shell_h - face_chamfer) outline();
                }
                translate([0, cy0, face_t]) linear_extrude(shell_h) square([in_w, in_h], center = true);
            }
            linear_extrude(tm_board_z) tm_posts_2d();
            linear_extrude(ol_board_z) ol_posts_2d();
            linear_extrude(face_t + rd_rib_h) rd_ribs_2d();
            linear_extrude(d1_front_z + d1_t + 1) d1_ribs_2d();
            translate([0, d1_cy + d1_l/2 + d1_shield_dy, 0]) linear_extrude(pad_top)
                square([9, 9], center = true);
            for (p = posts) translate(p) linear_extrude(shell_h) hull() {
                circle(d = post_d);
                translate([sign(p[0])*(in_w/2 + 0.5) - p[0], 0]) square([1, post_d], center = true);
            }
        }
        translate([0, 0, -1]) linear_extrude(face_t + 2) {
            tm_disp_keepout();
            translate([0, ol_cy + ol_win_dy]) square([ol_win_w, ol_win_h], center = true);
        }
        for (h = tm_holes) translate([h[0], h[1], face_t - 1]) cylinder(d = tm_pilot_d, h = tm_board_z);
        for (h = ol_holes) translate([h[0], h[1], face_t - 1]) cylinder(d = ol_pilot_d, h = ol_board_z);
        for (p = posts) translate([p[0], p[1], shell_h - insert_depth]) cylinder(d = insert_d, h = insert_depth + 1);
        usb_hole();
    }
}

// Back cover as printed: tape face on the bed, lip up.
module cover() {
    difference() {
        union() {
            linear_extrude(cover_t) outline();
            translate([0, cy0, cover_t]) linear_extrude(lip_h) difference() {
                square([in_w - 2*lip_clear, in_h - 2*lip_clear], center = true);
                square([in_w - 2*lip_clear - 2*lip_t, in_h - 2*lip_clear - 2*lip_t], center = true);
                for (p = posts) translate(p) circle(d = post_d + 1);
            }
        }
        for (p = posts) translate([p[0], p[1], 0]) {
            translate([0, 0, -1]) cylinder(d = screw_d, h = cover_t + 2);
            translate([0, 0, -0.01]) cylinder(d1 = csk_d, d2 = screw_d, h = (csk_d - screw_d)/2);
        }
    }
}

// Stand-ins for the review render only; one colour per component so they read apart.
module standins() {
    color("seagreen") translate([0, tm_cy, tm_board_z]) linear_extrude(tm_t) square([tm_l, tm_w], center = true);
    color("tomato") translate([0, ol_cy, ol_board_z]) linear_extrude(1.2) square([ol_w, ol_h], center = true);
    color("orchid") translate([0, rd_cy, face_t]) linear_extrude(1) square([rd_w, rd_h], center = true);
    color("royalblue") translate([0, d1_cy, d1_front_z]) linear_extrude(d1_t) square([d1_w, d1_l], center = true);
    color("dimgray") {
        translate([tm_disp_dx, tm_cy + tm_disp_dy, tm_recess]) linear_extrude(tm_disp_h) square([tm_disp_l, tm_disp_w], center = true);
        translate([0, ol_cy + ol_glass_dy, face_t + ol_gap]) linear_extrude(ol_glass_h) square([ol_glass_w, ol_glass_l], center = true);
        translate([0, d1_cy + d1_l/2 + d1_shield_dy, d1_front_z - d1_shield_h]) linear_extrude(d1_shield_h) square([12, 15], center = true);
    }
    color("black") for (sx = [-1, 1])   // D1 jumper housings, two rows of eight
        translate([sx*11.43, d1_cy, d1_front_z + d1_t]) linear_extrude(jumper_h) square([2.54, 20.3], center = true);
    color("silver") translate([0, in_h + wall, usb_z]) rotate([-90, 0, 0]) linear_extrude(18) square([10.5, 7], center = true);
}

// Review views of the parts against each other (the cover hides everything when it is on).
// Translucent shell and cover so the boards read through them; stand-ins stay solid.
module ghost(a = 0.18) { color([0.45, 0.6, 0.7, a]) children(); }
module cover_seated() { translate([0, 0, shell_h + cover_t]) mirror([0, 0, 1]) cover(); }
module cut_half() {   // remove x > 0 so the stack of boards shows in section
    difference() { children(); translate([0, -500, -500]) cube([500, 1000, 1000]); }
}

if (view == "shell") shell();
else if (view == "cover") cover();
else if (view == "open") { shell(); standins(); }                                   // no cover
else if (view == "xray") { ghost() shell(); standins(); ghost() translate([0, 0, 14]) cover_seated(); }
else if (view == "section") cut_half() { shell(); standins(); cover_seated(); }     // seated, cut at x = 0
else {
    shell();
    standins();
    translate([0, 0, shell_h + cover_t + 12]) mirror([0, 0, 1]) cover();   // exploded 12 mm
}
