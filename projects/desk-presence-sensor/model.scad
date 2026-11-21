// Desk presence sensor: D1 mini (ESP8266), LD2410C radar, SSD1306 OLED and a
// TM1637 4-digit display in one slim box that tapes flat to a monitor arm.
//
// Two parts. The FRONT PLATE carries everything: both display windows, the board posts,
// the radar and D1 mini ribs. It is a flat print, wired open on the bench. The BACK TRAY is
// the walls, the USB hole and the flat face that tapes to the arm; the plate pushes into its
// open front and four snap leaves in the long walls catch it against four stop ribs.
//
// Placed (assembled) coordinates: z = 0 is the tray's front rim, +z toward the arm, X across
// (45 wide), Y up the box as mounted (+Y top, where the USB cable leaves). The plate front sits
// plate_z0 behind the rim. Top to bottom: D1 mini (USB plug through the top wall), radar (no
// hole: it looks through the plate), OLED window, TM1637 window. Every board is on Dupont
// jumpers; the depth is set by the D1 mini's jumpers.
// plate() prints front face down; tray() prints on its tape face (rotated 180 about Y).

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
d1_front_z = 24;     // board's component side, from the plate front: clears the radar and OLED Dupont housings (top at ~19)
d1_usb_over = 1;     // socket proud of the board end, guessed
d1_shield_h = 3.2;   // ESP-12 can above the board, guessed
d1_shield_dy = -13;  // shield centre from the board's top (USB) end, guessed
tape_t = 1;          // foam tape on the pusher post's tip, pressing the D1's back
pusher_d = 6;        // post from the tray back that clamps the D1 onto its pillars
d1_slack = 0.5;
d1_rib_t = 1.2;
d1_rib_leg = 5;
jumper_h = 16.5;     // header plastic + Dupont housing behind the board
bend = 5;            // jumper wire bend room before the cover

/* [USB plug] (guessed: overmolds vary) */
usb_w = 12;
usb_h = 8;

/* [Back tray, plate and clips] */
back_t = 2.5;        // tape face thickness
plate_clr = 0.3;     // plate edge to tray wall, per side
barb = 0.8;          // snap barb height, 45 deg both faces
plate_z0 = 1.3;      // plate front behind the rim: where the barb's catch face meets the plate corner
leaf_len = 14;       // snap leaf length from the rim, cut by two slits
leaf_w = 8;
slit = 0.8;
rib = 1.0;           // stop rib height, 45 deg underside
rib_len = 10;

view = "plate";      // plate | tray | exploded | open | xray | section

/* [Hidden] */
$fn = 48;
in_w = box_w - 2*wall;
// Zones, Y from the inner bottom wall up.
// Bottom to top: radar (R3), TM1637 (R1), OLED (R2), then the D1 mini standing behind the OLED, USB up.
rd_cy = 0.5 + rd_rib_t + rd_slack + rd_h/2;
tm_cy = rd_cy + rd_h/2 + rd_slack + rd_rib_t + gap + tm_clear + tm_w/2;
ol_cy = tm_cy + tm_w/2 + tm_clear + gap + ol_h/2;
d1_bot = ol_cy - ol_h/2 + 2;                     // D1's lower end sits over the OLED's lower edge
d1_cy = d1_bot + d1_l/2;
in_h = d1_cy + d1_l/2 + d1_slack + d1_rib_t + 0.3;
out_h = in_h + 2*wall;
shell_h = plate_z0 + d1_front_z + d1_t + jumper_h + bend;   // tray cavity depth from the rim
box_d = shell_h + back_t;
tm_board_z = tm_recess + tm_disp_h;
ol_board_z = face_t + ol_gap + ol_glass_h;
usb_z = plate_z0 + d1_front_z - 1.4;             // socket centre, from the rim
tm_holes = [for (sx = [-1, 1], sy = [-1, 1]) [sx*tm_hole_dx/2, tm_cy + sy*tm_hole_dy/2]];
ol_holes = [for (sx = [-1, 1], sy = [-1, 1]) [sx*ol_hole_dx/2, ol_cy + sy*ol_hole_dy/2]];
pw = in_w - 2*plate_clr;                         // plate width and height
ph = in_h - 2*plate_clr;
plate_back = plate_z0 + face_t;
hook_ys = [tm_cy, ol_cy + 14];                        // snap leaves, each long wall
rib_ys = [rd_cy, ol_cy + 3];                         // stop ribs, each long wall
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
            translate([sign(h[0])*pw/2, h[1]]) square([0.01, tm_post_d], center = true);
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

// The D1 mini stands behind the displays, USB up. Four corner pillars rise from the plate, beyond
// the OLED edge and clear of the radar ribs, and carry its corners; L-ribs on top locate it.
// Four L-ribs locate the D1 mini's corners; its sides stay open for the reset button.
module d1_ribs_2d() {
    ix = d1_w/2 + d1_slack; iy = d1_l/2 + d1_slack; t = d1_rib_t;
    for (sx = [-1, 1], sy = [-1, 1]) translate([0, d1_cy]) scale([sx, sy]) {
        translate([ix, iy - d1_rib_leg + t]) square([t, d1_rib_leg]);
        translate([ix - d1_rib_leg + t, iy]) square([d1_rib_leg, t]);
    }
}

module d1_pillars_2d() {
    x0 = d1_w/2 - 1;                       // 1 mm of board edge rests on the top pillars
    bx0 = ol_w/2 + 0.1;                    // lower pillars stay outside the OLED board
    for (sx = [-1, 1]) {
        translate([sx*(x0 + pw/2)/2, d1_cy + d1_l/2 - 2]) square([pw/2 - x0, 4], center = true);
        translate([sx*(bx0 + pw/2)/2, d1_bot + 1]) square([pw/2 - bx0, 3], center = true);
    }
}
// 45 deg corbels reach the lower pillars in over the OLED's edge to the D1's corners.
module d1_corbels() {
    x0 = d1_w/2 - 1; bx0 = ol_w/2 + 0.1 + 0.5; zc = d1_front_z - (bx0 - x0);
    for (sx = [-1, 1]) translate([0, d1_bot + 1, 0]) rotate([90, 0, 0]) linear_extrude(3, center = true)
        scale([sx, 1]) polygon([[bx0, zc], [bx0, d1_front_z], [x0, d1_front_z]]);
}

module rd_ribs_2d() {
    translate([0, rd_cy]) difference() {
        square([rd_w + 2*(rd_slack + rd_rib_t), rd_h + 2*(rd_slack + rd_rib_t)], center = true);
        square([rd_w + 2*rd_slack, rd_h + 2*rd_slack], center = true);
        square([rd_w - 6, rd_h + 10], center = true);   // open top and bottom for the jumpers and a glue tool
    }
}

// The USB plug hole in the tray's top wall. Tray prints tape face down, so the rim is up:
// the 45 deg gable points at the rim (a small notch there), no flat ceiling.
module usb_hole() {
    translate([0, in_h - 1, 0]) rotate([-90, 0, 0]) linear_extrude(wall + 2)
        translate([0, -usb_z]) union() {
            square([usb_w, usb_h], center = true);
            translate([0, usb_h/2]) rotate(45) square(usb_w/sqrt(2), center = true);
        }
}

// Everything that belongs to the plate, in placed coordinates (front face at plate_z0).
module plate_placed() {
    translate([0, 0, plate_z0]) intersection() {   // the TM1637 posts would poke past the edge: clip to the outline
        linear_extrude(60) translate([0, cy0]) rrect(pw, ph, 1);
        difference() {
        union() {
            linear_extrude(face_t) translate([0, cy0]) rrect(pw, ph, 1);
            linear_extrude(tm_board_z) tm_posts_2d();
            linear_extrude(ol_board_z) ol_posts_2d();
            linear_extrude(face_t + rd_rib_h) rd_ribs_2d();
            linear_extrude(d1_front_z) d1_pillars_2d();
            d1_corbels();
            linear_extrude(d1_front_z + d1_t + 1) d1_ribs_2d();
        }
        translate([0, 0, -1]) linear_extrude(face_t + 2) {
            tm_disp_keepout();
            translate([0, ol_cy + ol_win_dy]) square([ol_win_w, ol_win_h], center = true);
        }
        for (h = tm_holes) translate([h[0], h[1], face_t - 1]) cylinder(d = tm_pilot_d, h = tm_board_z);
        for (h = ol_holes) translate([h[0], h[1], face_t - 1]) cylinder(d = ol_pilot_d, h = ol_board_z);
        }
    }
}

// Profile (a = inward from the long wall, b = z) extruded along Y, centred on y.
module along_y(sx, y, len, pts) {
    translate([sx*in_w/2, y, 0]) rotate([90, 0, 0]) linear_extrude(len, center = true)
        scale([-sx, 1]) polygon(pts);
}

module tray_placed() {
    difference() {
        union() {
            difference() {
                hull() {
                    linear_extrude(0.01) offset(delta = -face_chamfer) outline();
                    translate([0, 0, face_chamfer]) linear_extrude(box_d - face_chamfer) outline();
                }
                translate([0, cy0, -1]) linear_extrude(shell_h + 1) square([in_w, in_h], center = true);
            }
            for (sx = [-1, 1]) {
                for (y = rib_ys)   // stop ribs: flat face toward the rim, 45 deg underside
                    along_y(sx, y, rib_len, [[0, plate_back], [rib, plate_back], [0, plate_back + rib]]);
                for (y = hook_ys)  // snap barbs on the leaves: 45 deg lead-in and catch
                    along_y(sx, y, leaf_w, [[0, 0], [barb, barb], [0, 2*barb]]);
            }
            // Pusher post: between the two header rows, it presses the D1 onto its pillars through foam tape.
            d1_back = plate_z0 + d1_front_z + d1_t;
            translate([0, d1_cy, d1_back + tape_t]) cylinder(d = pusher_d, h = shell_h - d1_back - tape_t + 0.01);
        }
        for (sx = [-1, 1], y = hook_ys, d = [-1, 1])   // two slits free each leaf, open to the rim
            translate([sx*in_w/2, y + d*(leaf_w/2 + slit/2), leaf_len/2 - 0.5])
                cube([wall*2 + 2, slit, leaf_len + 1], center = true);
        usb_hole();
    }
}

// Printed orientations.
module plate() { translate([0, 0, -plate_z0]) plate_placed(); }
module tray() { translate([0, 0, box_d]) rotate([0, 180, 0]) tray_placed(); }

// Stand-ins for the review render only; one colour per component so they read apart.
module standins() {
    translate([0, 0, plate_z0]) {
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
    }
    color("silver") translate([0, in_h + wall, usb_z]) rotate([-90, 0, 0]) linear_extrude(18) square([10.5, 7], center = true);
}

// Example screen content for the review renders. Text reads correctly seen from the front
// (the front looks along +z, so it is mirrored in X here).
module screens() {
    translate([0, 0, plate_z0]) mirror([1, 0, 0]) {
        color("black") translate([-tm_disp_dx, tm_cy + tm_disp_dy, tm_recess - 0.1]) linear_extrude(0.11)
            square([tm_disp_l - 2, tm_disp_w - 2], center = true);
        color("red") translate([-tm_disp_dx, tm_cy + tm_disp_dy, tm_recess - 0.3]) linear_extrude(0.2)
            text("1:42", size = 8, halign = "center", valign = "center", font = "DejaVu Sans Mono:style=Bold");
        color("black") translate([0, ol_cy + ol_win_dy, face_t + ol_gap - 0.1]) linear_extrude(0.11)
            square([21.7, 10.9], center = true);
        color("white") for (i = [0:2]) translate([0, ol_cy + ol_win_dy + 3.3 - i*3.3, face_t + ol_gap - 0.3])
            linear_extrude(0.2) text(["SITTING 1:42", "PRESENT 98%", "WIFI -61 dBm"][i], size = 1.9,
                halign = "center", valign = "center", font = "DejaVu Sans Mono");
    }
}

// Review views, placed coordinates (the tray's back is up in the renders from +Z).
module ghost(a = 0.18) { color([0.45, 0.6, 0.7, a]) children(); }
module cut_half() {   // remove x > 0 so the stack of boards shows in section
    difference() { children(); translate([0, -500, -500]) cube([500, 1000, 1000]); }
}

// As-mounted orientations, Y up in the image: front = what you see at the desk (+X on the left);
// side = looking from +X, arm on the left and you on the right; top = looking down, arm at the bottom.
module orient(o) {
    if (o == "front") rotate([0, 180, 0]) children();
    else if (o == "side") rotate([0, -90, 0]) children();
    else if (o == "top") rotate([90, 0, 0]) children();
    else children();
}

if (view == "front") orient("front") { tray_placed(); plate_placed(); screens(); }
else if (view == "front_xray") orient("front") { ghost(0.12) tray_placed(); ghost(0.25) plate_placed(); standins(); screens(); }
else if (view == "side_xray") orient("side") { cut_half() tray_placed(); plate_placed(); standins(); }
else if (view == "side") orient("side") cut_half() { tray_placed(); plate_placed(); standins(); }
else if (view == "top_xray") orient("top") { ghost(0.15) tray_placed(); plate_placed(); standins(); }
else if (view == "plate") plate();
else if (view == "tray") tray();
else if (view == "open") { plate_placed(); standins(); }                  // bench state, tray off
else if (view == "xray") { ghost() tray_placed(); plate_placed(); standins(); }
else if (view == "section") cut_half() { tray_placed(); plate_placed(); standins(); }
else {   // exploded: plate and boards pulled 25 mm out of the front
    tray_placed();
    translate([0, 0, -25]) { plate_placed(); standins(); }
}
