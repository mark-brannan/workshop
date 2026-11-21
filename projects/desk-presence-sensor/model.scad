// Desk presence sensor: D1 mini (ESP8266), LD2410C radar, SSD1306 OLED and a
// TM1637 4-digit display in one box that tapes flat to a monitor arm.
//
// Three parts. The SHELL is the front face and all four walls in one deep print: both display
// windows, the board posts, the radar ribs and the D1 mini's slots. The BACK plate is a flat
// tape face whose four tabs snap gently into the shell's open back. The RETAINER is a strip
// pressed into the D1's slots behind it, so the taped back never holds a board.
//
// Placed coordinates: z = 0 is the outer front face, +z toward the arm, X across (45 wide),
// Y up as mounted (+Y top). Bottom to top on the face: radar (looks through the face),
// TM1637, OLED. The D1 mini stands on edge behind the radar and TM1637 wiring, USB end up,
// near the +X wall; it slides in from the back along a floor slot and a wall ledge slot.
// The USB cable rises behind the OLED and leaves through a slot in the top wall, open to the back rim.
// shell() prints face down; back() prints tape face down; retainer() prints on its flat side.

/* [Box] */
box_w = 45;          // matches the monitor arm stem
wall = 1.5;          // sides; the TM1637 board leaves 0.25 per side at 45 wide
face_t = 1.5;        // front face; the radar looks through it
corner_r = 3;        // vertical corners
face_chamfer = 0.8;  // 45 deg on the front edge (it faces the bed)
gap = 2.5;           // between board zones, Y

/* [TM1637, bottom display] (owner, caliper, from segment-display-enclosure) */
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

/* [OLED, top display] (generic drawing, not calipered) */
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
rd_stack = 19.5;     // radar board + header + Dupont housings, from the outer face, guessed

/* [D1 mini, on edge] (vendor drawing, not calipered) */
d1_l = 34.2;         // Y, USB end up
d1_w = 25.6;         // Z, front to back
d1_t = 1;
d1_shield_h = 3.2;   // ESP-12 can, toward the +X wall, guessed
can_clr = 0.5;       // can to the wall
d1_z0 = rd_stack + 1;   // board's front edge: behind the radar's Dupont housings
slot_clr = 0.25;     // per side, board in its slots
slot_deep = 1.5;     // board edge engagement, each slot
d1_y0 = 1.5;         // board's lower edge above the inner floor
d1_slack = 0.5;      // up, so the board slides
usb_gap = 13;        // ledge cut away around the USB socket and plug, Z
cable_slot_w = 8;    // top wall slot, X; the plug fits from inside, the cable lies in it
jumper_h = 16.5;     // header plastic + Dupont housing beside the board, -X

/* [Back plate and snaps] */
back_t = 2.5;        // tape face thickness
tab_len = 6;         // snap tab, into the shell
tab_t = 1.2;
tab_w = 10;
tab_clr = 0.2;       // tab to the wall
bump = 0.5;          // 45 deg both faces: gentle
bump_z = 3;          // bump centre in front of the shell rim

/* [Retainer] */
ret_t = 3;           // along Z, behind the board
ret_body = 2.5;      // across X, flush with the board's -X face

view = "shell";      // shell | back | retainer | front | front_xray | side_xray | open | exploded

/* [Hidden] */
$fn = 48;
in_w = box_w - 2*wall;
rd_cy = 0.5 + rd_rib_t + rd_slack + rd_h/2;
tm_cy = rd_cy + rd_h/2 + rd_slack + rd_rib_t + gap + tm_clear + tm_w/2;
ol_cy = tm_cy + tm_w/2 + tm_clear + gap + ol_h/2;
in_h = ol_cy + ol_h/2 + 0.5;
out_h = in_h + 2*wall;
cy0 = in_h/2;
tm_board_z = tm_recess + tm_disp_h;
ol_board_z = face_t + ol_gap + ol_glass_h;
tm_holes = [for (sx = [-1, 1], sy = [-1, 1]) [sx*tm_hole_dx/2, tm_cy + sy*tm_hole_dy/2]];
ol_holes = [for (sx = [-1, 1], sy = [-1, 1]) [sx*ol_hole_dx/2, ol_cy + sy*ol_hole_dy/2]];
d1_x = in_w/2 - can_clr - d1_shield_h - d1_t/2;   // board mid-plane
d1_z1 = d1_z0 + d1_w;
d1_zc = (d1_z0 + d1_z1)/2;
d1_y1 = d1_y0 + d1_l;
shell_d = d1_z1 + ret_t + 0.5;                    // rim, from the front face
box_d = shell_d + back_t;
slot_w = d1_t + 2*slot_clr;
rail_x0 = d1_x - slot_w/2 - 1.5;                  // rails run from here to the +X wall
floor_top = d1_y0 + slot_deep;
ledge_y0 = d1_y1 + d1_slack - slot_deep;          // ledge underside
ledge_y1 = ledge_y0 + slot_deep + 2;
ledge_z0 = tm_board_z + tm_t + 4;                 // ledge starts behind the TM1637 and its solder joints
tab_ys = [cy0 - 22, cy0 + 22];
cable_x = d1_x;

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
    intersection() {
        square([in_w + 0.02, 2*in_h], center = true);
        difference() {
            for (h = tm_holes) hull() {
                translate(h) circle(d = tm_post_d);
                translate([sign(h[0])*in_w/2, h[1]]) square([0.01, tm_post_d], center = true);
            }
            tm_disp_keepout();
        }
    }
}

module ol_posts_2d() {
    difference() {
        for (h = ol_holes) translate(h) circle(d = ol_post_d);
        ol_glass_keepout();
    }
}

module rd_ribs_2d() {
    translate([0, rd_cy]) difference() {
        square([rd_w + 2*(rd_slack + rd_rib_t), rd_h + 2*(rd_slack + rd_rib_t)], center = true);
        square([rd_w + 2*rd_slack, rd_h + 2*rd_slack], center = true);
        square([rd_w - 6, rd_h + 10], center = true);   // open top and bottom for the jumpers and a glue tool
    }
}

// D1 slots. The floor rail rises from the face, so its slot is solid in front of the board: that is the stop.
module floor_rail() {
    difference() {
        translate([rail_x0, -0.01, 0]) cube([in_w/2 - rail_x0 + 0.01, floor_top + 0.01, shell_d]);
        translate([d1_x - slot_w/2, d1_y0, d1_z0]) cube([slot_w, slot_deep + 1, shell_d]);
    }
}
// Ledge rail on the +X wall at the board's top edge, cut away around the USB socket. Both segments
// start on a 45 deg slope out of the wall (the shell prints face down).
module ledge_rail() {
    w = in_w/2 - rail_x0; xa = in_w/2 + 0.01; g0 = d1_zc - usb_gap/2; g1 = d1_zc + usb_gap/2;
    difference() {
        translate([0, ledge_y1, 0]) rotate([90, 0, 0]) linear_extrude(ledge_y1 - ledge_y0) {
            polygon([[xa, ledge_z0], [rail_x0, ledge_z0 + w], [rail_x0, g0], [xa, g0]]);
            polygon([[xa, g1], [rail_x0, g1 + w], [rail_x0, shell_d - 0.01], [xa, shell_d - 0.01]]);
        }
        translate([d1_x - slot_w/2, ledge_y0 - 1, 0]) cube([slot_w, slot_deep + 1, shell_d + 1]);
    }
}

// Snap groove in the side walls: a 45 deg V matching the tab bumps.
module snap_grooves() {
    for (sx = [-1, 1], y = tab_ys)
        translate([sx*in_w/2, y, shell_d - bump_z]) rotate([90, 0, 0]) linear_extrude(tab_w + 2, center = true)
            polygon([[0, -bump - 0.1], [sx*(bump + 0.1), 0], [0, bump + 0.1]]);
}

module shell() {
    difference() {
        union() {
            difference() {
                hull() {
                    linear_extrude(0.01) offset(delta = -face_chamfer) outline();
                    translate([0, 0, face_chamfer]) linear_extrude(shell_d - face_chamfer) outline();
                }
                translate([0, cy0, face_t]) linear_extrude(shell_d) square([in_w, in_h], center = true);
            }
            linear_extrude(tm_board_z) tm_posts_2d();
            linear_extrude(ol_board_z) ol_posts_2d();
            linear_extrude(face_t + rd_rib_h) rd_ribs_2d();
            floor_rail();
            ledge_rail();
        }
        translate([0, 0, -1]) linear_extrude(face_t + 2) {
            tm_disp_keepout();
            translate([0, ol_cy + ol_win_dy]) square([ol_win_w, ol_win_h], center = true);
        }
        for (h = tm_holes) translate([h[0], h[1], face_t - 1]) cylinder(d = tm_pilot_d, h = tm_board_z);
        for (h = ol_holes) translate([h[0], h[1], face_t - 1]) cylinder(d = ol_pilot_d, h = ol_board_z);
        // cable slot through the top wall, open to the rim: no roof to print
        translate([cable_x - cable_slot_w/2, in_h - 1, d1_zc - 4]) cube([cable_slot_w, wall + 2, shell_d]);
        snap_grooves();
    }
}

// Back plate, placed: tape face outermost, four tabs reaching into the shell mouth.
module back_placed() {
    translate([0, 0, shell_d]) linear_extrude(back_t) outline();
    for (sx = [-1, 1], y = tab_ys) {
        x_out = sx*(in_w/2 - tab_clr);
        translate([x_out - (sx > 0 ? tab_t : 0), y - tab_w/2, shell_d - tab_len]) cube([tab_t, tab_w, tab_len + 0.01]);
        translate([x_out, y, shell_d - bump_z]) rotate([90, 0, 0]) linear_extrude(tab_w, center = true)
            polygon([[0, -bump], [sx*bump, 0], [0, bump]]);
    }
}

// Retainer, placed: a body between the rails, tongues into both slots, flush with the board's -X face.
module retainer_placed() {
    x0 = d1_x - slot_w/2 + 0.05;
    translate([x0, floor_top + 0.2, d1_z1 + 0.2]) cube([ret_body, ledge_y0 - floor_top - 0.4, ret_t]);
    translate([x0, d1_y0 + 0.1, d1_z1 + 0.2]) cube([slot_w - 0.1, ledge_y0 + slot_deep - d1_y0 + d1_slack - 0.3, ret_t]);
}

module back() { translate([0, 0, box_d]) rotate([0, 180, 0]) back_placed(); }
module retainer() { rotate([0, -90, 0]) translate([-(d1_x - slot_w/2 + 0.05), 0, 0]) retainer_placed(); }

// Stand-ins for the review renders only.
module standins() {
    color("seagreen") translate([0, tm_cy, tm_board_z]) linear_extrude(tm_t) square([tm_l, tm_w], center = true);
    color("tomato") translate([0, ol_cy, ol_board_z]) linear_extrude(1.2) square([ol_w, ol_h], center = true);
    color("orchid") translate([0, rd_cy, face_t]) linear_extrude(1) square([rd_w, rd_h], center = true);
    color("black") translate([-5, rd_cy, face_t]) linear_extrude(rd_stack - face_t) square([12.7, 2.5], center = true);
    color("royalblue") translate([d1_x - d1_t/2, d1_y0, d1_z0]) cube([d1_t, d1_l, d1_w]);
    color("dimgray") {
        translate([tm_disp_dx, tm_cy + tm_disp_dy, tm_recess]) linear_extrude(tm_disp_h) square([tm_disp_l, tm_disp_w], center = true);
        translate([0, ol_cy + ol_glass_dy, face_t + ol_gap]) linear_extrude(ol_glass_h) square([ol_glass_w, ol_glass_l], center = true);
        translate([d1_x + d1_t/2, d1_y1 - 13 - 7.5, d1_zc - 6]) cube([d1_shield_h, 15, 12]);
    }
    color("black") for (sz = [-1, 1])   // D1 jumper housings, two rows of eight, toward -X
        translate([d1_x - d1_t/2 - jumper_h, d1_y0 + d1_l/2 - 10.15, d1_zc + sz*11.43 - 1.27]) cube([jumper_h, 20.3, 2.54]);
    color("silver") translate([d1_x, d1_y1, d1_zc]) rotate([-90, 0, 0]) linear_extrude(in_h + wall - d1_y1 + 6) square([7, 10.5], center = true);
}

module screens() {
    mirror([1, 0, 0]) {
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

module ghost(a = 0.18) { color([0.45, 0.6, 0.7, a]) children(); }
module cut_side() {   // remove x > d1_x + 3 (beyond the D1) so its slots and the stack show in section
    difference() { children(); translate([d1_x + 3, -500, -500]) cube([500, 1000, 1000]); }
}

// As mounted, Y up in the image: front = at the desk (+X on the left); side = looking from +X, arm on the left.
module orient(o) {
    if (o == "front") rotate([0, 180, 0]) children();
    else if (o == "side") rotate([0, -90, 0]) children();
    else children();
}

if (view == "front") orient("front") { shell(); back_placed(); screens(); }
else if (view == "front_xray") orient("front") { ghost(0.15) shell(); standins(); screens(); }
else if (view == "side_xray") orient("side") { cut_side() shell(); ghost(0.3) back_placed(); color("orange") retainer_placed(); standins(); }
else if (view == "shell") shell();
else if (view == "back") back();
else if (view == "retainer") retainer();
else if (view == "open") { shell(); standins(); color("orange") retainer_placed(); }
else { shell(); standins(); translate([0, 0, 25]) back_placed(); }
