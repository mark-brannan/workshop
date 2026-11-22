// Desk presence sensor: D1 mini (ESP8266), LD2410C radar, SSD1306 OLED and a
// TM1637 4-digit display in one box that tapes flat to a monitor arm.
//
// Three parts. The SHELL is the front face and all four walls in one print: both display
// windows, the board posts and the radar ribs. The TRAY screws onto the TM1637's back with
// the TM1637's own screws and carries the D1 mini flat behind the radar and TM1637. The BACK
// plate is a flat tape face whose four tabs snap gently into the shell's open back.
//
// Placed coordinates: z = 0 is the outer front face, +z toward the arm, X across (45 wide),
// Y up as mounted (+Y top). Bottom to top on the face: radar (looks through the face),
// TM1637, OLED. Behind the TM1637, the tray; on the tray, the D1 mini flat, USB end up, ESP
// can toward the arm. The USB plug points straight up behind the OLED and the cable leaves
// through a slot in the top wall, open to the back rim.
// shell() prints face down; back() prints tape face down; tray() prints on its front (the face
// that sits on the TM1637), D1 side up.

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
tm_joint_h = 1.5;    // guessed: clipped pins and solder on the board's back
tm_pin_row = 10.16;  // guessed: display pin rows apart (0.36" 4-digit), centred on the display
tm_pin_span = 12.7;  // guessed: six pins per row, 2.54 pitch

/* [OLED, top display] (generic drawing, not calipered) */
ol_w = 27.3;         // X
ol_h = 27.8;         // Y, header at the top edge, pins out the back
ol_hole_dx = 23.3;
ol_hole_dy = 23.6;
ol_t = 1.6;          // guessed, standard PCB
ol_pins = 1.7;       // clipped header pins behind the board, guessed
ol_glass_h = 2.4;    // guessed: board front to glass face
ol_glass_w = 26.7;   // guessed, typical 0.96" glass
ol_glass_l = 19.3;
ol_glass_dy = 0;     // guessed: glass centred between the hole rows
ol_win_w = 24;       // active area 21.7 x 10.9 plus margin
ol_win_h = 13;
ol_win_dy = 1.5;     // guessed: active area above the board centre (header end)
ol_gap = 0.3;        // glass face to the face interior, before ol_fwd
ol_fwd = 1.8;        // glass moved toward the outside; 1.8 is flush (the glass pocket runs through the face)
ol_bevel = 0.5;      // 45 deg chamfer around the glass at the outside face, sloping in toward it
ol_pilot_d = 1.6;    // M2 self-tapping, calibration pending
ol_post_d = 3.6;

/* [LD2410C radar] (vendor, not calipered) */
rd_w = 22;           // X
rd_h = 16;           // Y
rd_t = 1;            // board, guessed
rd_back = 3;         // clipped pins plus soldered wire behind the board
rd_slack = 0.5;      // per side
rd_rib_t = 1.2;
rd_rib_h = 4;        // above the face interior
rd_lip = 0.7;        // snap lip over the board edge, each side; both slopes 45 deg: push in or out, no supports
rd_lip_len = 4;      // along Y, two per side, each on its own flexing beam
rd_hook = 0.9;       // bottom hooks over the board's lower edge
rd_lip_gap = 0.1;    // board back to where the lip underside starts
rd_beam_t = 0.8;     // beam thickness: the rib thinned from outside so the lip can flex
rd_slot = 1;         // cut either side of a beam
/* [OLED frame] */
ol_slack = 0.3;      // board edge to rib, per side
ol_rib_t = 1.2;

/* [D1 mini, flat] (vendor drawing, not calipered) */
d1_l = 34.2;         // Y, USB end up
d1_w = 25.6;         // X
d1_t = 1;
d1_shield_h = 3.2;   // ESP-12 can, on the back (arm) side
d1_under = 2;        // CH340 and the rest on the front side, into the tray's window
d1_y0 = 5;           // board's lower edge above the inner floor
d1_clr = 0.2;        // board edge to the lip wall and to the hook post
usb_h = 1.5;         // guessed: socket axis above the board's can side
usb_lip = 0.8;       // guessed: socket mouth past the board's top edge
plug_w = 11;         // guessed USB plug overmold, X
plug_t = 7.5;        // guessed, Z
plug_l = 18;         // guessed, Y
cable_d = 4;         // guessed
cable_slot_w = 5.5;  // top wall slot, X; open to the back rim
back_clr = 0.3;      // deepest part to the back plate

/* [Tray] */
tray_t = 4;          // TM1637 back to the D1's front face: joints, wires and the D1's underside parts
tray_side = 0.3;     // tray edge to the side wall
tray_hole_d = 3.0;   // M2.5 clearance, generous (printed holes come undersize)
rail_x = 13.4;       // windows run between the side rails: D1 edge plus room for its pad joints
seat = 3;            // D1 resting on the tray at each short end, Y
seat_x = 9.8;        // top seats start here (corners only: the socket and CH340 sit between)
lip_t = 1.6;         // lip wall, Y
lip_hw = 8;          // centre stop block half width, X; the corner hooks run outward from here
catch = 0.6;         // top hook reach over the board
lip_catch = 0.8;     // lower corner hook reach over the board (deeper: two short hooks hold the whole edge)
stop_rec = 1.0;      // guessed (owner: under 1 mm): pocket in the seat by the stop block, clear of what sticks out of the wifi module under the board
hook_x0 = 8;         // hook from here outward, clear of the plug
hook_w = 4.3;
hook_t = 1.0;        // post, Y; flexes away from the board
hook_slot = 0.8;     // free gap either side of the post
hook_root = 0.6;     // post joins the tray only in this bottom layer
strap_t = 1.6;       // bed-side strap closing the plug gap; leaves room under a plug fatter than guessed
hdr_win = [-17.3, 28.5, 40.3];   // TM1637 header joints, -X end: window x from the edge to [0], y [1] to [2]

/* [Back plate and snaps] */
back_t = 2.5;        // tape face thickness
tab_len = 6;         // snap tab, into the shell
tab_t = 1.2;
tab_w = 10;
tab_clr = 0.2;       // tab to the wall
bump = 0.5;          // 45 deg both faces: gentle
bump_z = 3;          // bump centre in front of the shell rim

view = "shell";      // shell | back | tray | front | front_xray | side_xray | open | exploded | layers

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
ol_glass_z = face_t + ol_gap - ol_fwd;   // glass front face
ol_board_z = ol_glass_z + ol_glass_h;
ol_back_z = ol_board_z + ol_t + ol_pins;
tm_holes = [for (sx = [-1, 1], sy = [-1, 1]) [sx*tm_hole_dx/2, tm_cy + sy*tm_hole_dy/2]];
ol_holes = [for (sx = [-1, 1], sy = [-1, 1]) [sx*ol_hole_dx/2, ol_cy + sy*ol_hole_dy/2]];
// The depth stack, front to back.
tray_z0 = tm_board_z + tm_t;                       // tray front face on the TM1637's back
d1_z0 = tray_z0 + tray_t;                          // D1 front face on the tray
d1_y1 = d1_y0 + d1_l;
usb_z = d1_z0 + d1_t + usb_h;                      // socket and plug axis
plug_y0 = d1_y1 + usb_lip;
shell_d = max(usb_z + plug_t/2, d1_z0 + d1_t + d1_shield_h) + back_clr;   // rim, from the front face
box_d = shell_d + back_t;
cable_z0 = usb_z - cable_d/2 - 0.5;                // cable slot floor
tray_hw = in_w/2 - tray_side;
tray_y0 = d1_y0 - d1_clr - lip_t;
tray_y1 = tm_cy + tm_w/2 + 1.35;
post_y0 = d1_y1 + d1_clr;
post_y1 = post_y0 + hook_t;
tm_win_y1 = post_y1 + hook_slot;                   // the band above here bears on the TM1637's back, clear of its display pins
seat_y1 = post_y0 - hook_slot;
catch_z = d1_z0 + d1_t + 0.05 - d1_clr;            // catch underside where it meets its wall or post
tab_ys = [cy0 - 22, cy0 + 22];

function xs(sx, a, b) = [min(sx*a, sx*b), max(sx*a, sx*b)];   // the X span a..b, mirrored to side sx
module rrect(w, h, r) { offset(r = r) square([w - 2*r, h - 2*r], center = true); }
module outline(grow = 0) { translate([0, cy0]) rrect(box_w + 2*grow, out_h + 2*grow, corner_r + grow); }
// 2D profile in (Y, Z), extruded along X from x0 to x1.
module yz(x0, x1) { translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(x1 - x0) children(); }

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

// Radar snap: four lips, two per side rib, each on a beam freed by slots and thinned from outside.
// Both slopes are 45 deg, so the board pushes in (and gently out) and nothing needs support.
module rd_lips() {
    zb = face_t + rd_t + rd_lip_gap;
    for (sx = [-1, 1])
        translate([sx*(rd_w/2 + rd_slack), rd_cy + (rd_h/2 - rd_lip_len/2 - 1), 0])
            rotate([90, 0, 0]) linear_extrude(rd_lip_len, center = true)
                polygon([[sx*0.2, zb], [-sx*rd_lip, zb + rd_lip], [-sx*rd_lip, zb + rd_lip + 0.3],
                         [sx*0.2, zb + 2*rd_lip + 0.3]]);
}
// Radar bottom hooks: the board's lower edge tucks under them at an angle, then the board lies flat
// and the upper snap lips click over it. 45 deg undersides, no supports.
module rd_hooks() {
    zb = face_t + rd_t + rd_lip_gap;
    for (sx = [-1, 1])
        translate([sx*(rd_w/2 - 1), rd_cy - (rd_h/2 + rd_slack), 0])
            rotate([90, 0, 90]) linear_extrude(3, center = true)
                polygon([[-0.2, zb], [rd_hook, zb + rd_hook], [rd_hook, zb + rd_hook + 0.3], [-0.2, zb + 2*rd_hook + 0.3]]);
}
// What the beams are cut free with.
module rd_beam_cuts() {
    for (sx = [-1, 1]) { dy = 1;
        y0 = rd_h/2 - 1 - rd_lip_len;                      // beam spans y0 .. y0 + rd_lip_len from the radar centre
        x_in = rd_w/2 + rd_slack;
        for (y = [y0 - rd_slot, y0 + rd_lip_len])
            translate([sx*(x_in + rd_rib_t/2), rd_cy + dy*(y + rd_slot/2), face_t + 10])
                cube([rd_rib_t + 1, rd_slot, 20], center = true);
        translate([sx*(x_in + rd_rib_t - (rd_rib_t - rd_beam_t)/2 + 0.5), rd_cy + dy*(y0 + rd_lip_len/2), face_t + 10])
            cube([(rd_rib_t - rd_beam_t) + 1, rd_lip_len, 20], center = true);
    }
}

// OLED seat: ribs round the board's sides and bottom; the top edge meets the wall.
module ol_frame_2d() {
    translate([0, ol_cy]) difference() {
        translate([0, (ol_h/2 + 0.5 - (ol_h/2 + ol_slack + ol_rib_t))/2])
            square([ol_w + 2*(ol_slack + ol_rib_t), ol_h/2 + 0.5 + ol_h/2 + ol_slack + ol_rib_t], center = true);
        square([ol_w + 2*ol_slack, ol_h + 2*ol_slack], center = true);
    }
}

module rd_ribs_2d() {
    translate([0, rd_cy]) difference() {
        square([rd_w + 2*(rd_slack + rd_rib_t), rd_h + 2*(rd_slack + rd_rib_t)], center = true);
        square([rd_w + 2*rd_slack, rd_h + 2*rd_slack], center = true);
        square([rd_w - 6, rd_h + 10], center = true);   // open top and bottom for the wires and a glue tool
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
            rd_lips();
            rd_hooks();
            linear_extrude(ol_board_z + ol_t) ol_frame_2d();
        }
        translate([0, 0, -1]) linear_extrude(face_t + 2) {
            tm_disp_keepout();
            translate([0, ol_cy + ol_win_dy]) square([ol_win_w, ol_win_h], center = true);
        }
        // glass pocket: through the face when flush, else from behind leaving a lip in front
        translate([0, 0, ol_glass_z <= 0 ? -1 : ol_glass_z]) linear_extrude(face_t + 1) offset(delta = 0.05) ol_glass_keepout();
        // chamfer: the pocket flares outward over its first ol_bevel mm at the outside face
        translate([0, ol_cy + ol_glass_dy, 0]) hull() {
            translate([0, 0, -0.01]) linear_extrude(0.01) square([ol_glass_w + 0.7 + 2*ol_bevel, ol_glass_l + 0.7 + 2*ol_bevel], center = true);
            translate([0, 0, ol_bevel]) linear_extrude(0.01) square([ol_glass_w + 0.72, ol_glass_l + 0.72], center = true);  // 0.01 proud: no shared wall with the pocket
        }
        for (h = tm_holes) translate([h[0], h[1], face_t - 1]) cylinder(d = tm_pilot_d, h = tm_board_z);
        for (h = ol_holes) translate([h[0], h[1], face_t - 1]) cylinder(d = ol_pilot_d, h = ol_board_z);
        // cable slot through the top wall, open to the rim: no roof to print
        translate([-cable_slot_w/2, in_h - 1, cable_z0]) cube([cable_slot_w, wall + 2, shell_d]);
        snap_grooves();
        rd_beam_cuts();
    }
}

// Tray, placed. A frame whose front face bears on the TM1637's back wherever it is bare: side
// rails, a band above the display pins and the plate below the board, with the screw pads in
// them. Windows clear the display pins, the header joints, the D1's underside and the plug.
module tray_frame_2d(strap = false) {   // strap: the plug pass stops at the top band, closing the frame
    difference() {
        translate([0, (tray_y0 + tray_y1)/2]) rrect(2*tray_hw, tray_y1 - tray_y0, 1);
        translate([-rail_x, d1_y0 + seat]) square([2*rail_x, tm_win_y1 - d1_y0 - seat]);   // D1 underside, display pins
        translate([-tray_hw - 1, hdr_win[1]]) square([hdr_win[0] + tray_hw + 1, hdr_win[2] - hdr_win[1]]);
        translate([-plug_w/2 - 0.8, tm_win_y1 - 1]) square([plug_w + 1.6, strap ? 1 : tray_y1]);   // plug passes
        for (h = tm_holes) translate(h) circle(d = tray_hole_d);
    }
}

module hook_profile() {   // (Y, Z): post, catch with a 45 deg underside and a 45 deg lead-in
    zt = catch_z + 2*(catch + d1_clr);
    polygon([[post_y0, tray_z0], [post_y1, tray_z0], [post_y1, zt], [post_y0, zt],
             [post_y0 - catch - d1_clr, catch_z + catch + d1_clr], [post_y0, catch_z]]);
}

module lip_profile() {    // (Y, Z): wall with a 45 deg underside catch over the board's lower edge
    w = d1_y0 - d1_clr; tip = w + lip_catch + d1_clr;
    polygon([[tray_y0, tray_z0], [w, tray_z0], [w, catch_z], [tip, catch_z + lip_catch + d1_clr],
             [tip, catch_z + lip_catch + d1_clr + 0.4], [tray_y0, catch_z + lip_catch + d1_clr + 0.4]]);
}

module tray_placed() {
    difference() {
        translate([0, 0, tray_z0]) linear_extrude(tray_t) tray_frame_2d();
        translate([-lip_hw, d1_y0, tray_z0 + tray_t - stop_rec]) cube([2*lip_hw, seat, stop_rec + 1]);   // seat pocket by the stop block
    }
    for (sx = [-1, 1]) {
        s = xs(sx, seat_x, rail_x + 0.01); r = xs(sx, hook_x0, rail_x + 0.01); p = xs(sx, hook_x0, hook_x0 + hook_w);
        translate([s[0], d1_y1 - seat, tray_z0]) cube([s[1] - s[0], seat_y1 - d1_y1 + seat, tray_t]);    // top seat
        translate([r[0], seat_y1 - 0.01, tray_z0]) cube([r[1] - r[0], tm_win_y1 - seat_y1 + 0.02, hook_root]);  // hook root
        yz(p[0], p[1]) hook_profile();
    }
    // lower edge: the lip profile across the full width, its catch cut away in the centre. What is left there is the stop
    // block (the board's lower edge bears on it, flush with the board's face so the module's can clears it, no overhang);
    // the two corner hooks stand outside it.
    difference() {
        yz(-rail_x, rail_x) lip_profile();
        translate([-lip_hw, tray_y0 - 1, tray_z0 + tray_t + d1_t]) cube([2*lip_hw, lip_t + 3, 3]);
    }
    translate([0, 0, tray_z0]) linear_extrude(strap_t) tray_frame_2d(strap = true);   // strap under the plug
}

module back() { translate([0, 0, box_d]) rotate([0, 180, 0]) back_placed(); }
module tray() { translate([0, 0, -tray_z0]) tray_placed(); }

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

// Stand-ins for the review renders only. cut = true sections each at cut_x, keeping its colour on the cut face.
module paint(c, cut) { if (cut) color(c) cut_side() children(); else color(c) children(); }
module si_radar(cut = false) {
    paint("orchid", cut) translate([0, rd_cy, face_t]) linear_extrude(rd_t) square([rd_w, rd_h], center = true);
    paint("black", cut) translate([0, rd_cy + rd_h/2 - 1.5, face_t + rd_t]) linear_extrude(rd_back) square([12.7, 2], center = true);
}
module si_tm(cut = false) {
    paint("seagreen", cut) translate([0, tm_cy, tm_board_z]) linear_extrude(tm_t) square([tm_l, tm_w], center = true);
    paint("dimgray", cut) translate([tm_disp_dx, tm_cy + tm_disp_dy, tm_recess]) linear_extrude(tm_disp_h) square([tm_disp_l, tm_disp_w], center = true);
}
module si_ol(cut = false) {
    paint("tomato", cut) translate([0, ol_cy, ol_board_z]) linear_extrude(ol_t) square([ol_w, ol_h], center = true);
    paint("dimgray", cut) translate([0, ol_cy + ol_glass_dy, ol_glass_z]) linear_extrude(ol_glass_h) square([ol_glass_w, ol_glass_l], center = true);
}
module si_d1(cut = false) {
    paint("royalblue", cut) translate([-d1_w/2, d1_y0, d1_z0]) cube([d1_w, d1_l, d1_t]);
    paint("dimgray", cut) {
        translate([-6, d1_y0 + 7, d1_z0 + d1_t]) cube([12, 15, d1_shield_h]);             // ESP-12 can
        translate([-4, d1_y1 - 12, d1_z0 - d1_under]) cube([8, 8, d1_under]);             // CH340, underside
        translate([-4, d1_y1 - 5 + usb_lip, d1_z0 + d1_t]) cube([8, 5, 2*usb_h]);         // USB socket
    }
}
module si_plug(cut = false) {
    paint("silver", cut) {
        translate([0, plug_y0, usb_z]) rotate([-90, 0, 0]) linear_extrude(plug_l) square([plug_w, plug_t], center = true);
        translate([0, plug_y0 + plug_l, usb_z]) rotate([-90, 0, 0]) cylinder(d = cable_d, h = in_h + wall - d1_y1 - plug_l + 6);
    }
}
module standins(cut = false) { si_radar(cut); si_tm(cut); si_ol(cut); si_d1(cut); si_plug(cut); }

// Exploded along the depth, layer by layer in assembly order, box upright, seen from behind.
explode = 32;
module exploded() {
    rotate([90, 0, 0]) {
        shell();
        translate([0, 0, 1*explode]) { si_radar(); si_ol(); }
        translate([0, 0, 2*explode]) si_tm();
        translate([0, 0, 3*explode]) color("orange") tray_placed();
        translate([0, 0, 4.3*explode]) { si_d1(); si_plug(); }
        translate([0, 0, 6.2*explode]) back_placed();
    }
}

module screens() {
    mirror([1, 0, 0]) {
        color("black") translate([-tm_disp_dx, tm_cy + tm_disp_dy, tm_recess - 0.1]) linear_extrude(0.11)
            square([tm_disp_l - 2, tm_disp_w - 2], center = true);
        color("red") translate([-tm_disp_dx, tm_cy + tm_disp_dy, tm_recess - 0.3]) linear_extrude(0.2)
            text("1:42", size = 8, halign = "center", valign = "center", font = "DejaVu Sans Mono:style=Bold");
        color("black") translate([0, ol_cy + ol_win_dy, ol_glass_z - 0.1]) linear_extrude(0.11)
            square([21.7, 10.9], center = true);
        color("white") for (i = [0:2]) translate([0, ol_cy + ol_win_dy + 3.3 - i*3.3, ol_glass_z - 0.3])
            linear_extrude(0.2) text(["SITTING 1:42", "PRESENT 98%", "WIFI -61 dBm"][i], size = 1.9,
                halign = "center", valign = "center", font = "DejaVu Sans Mono");
    }
}

module ghost(a = 0.18) { color([0.45, 0.6, 0.7, a]) children(); }
cut_x = hook_x0 + hook_w/2;   // section through a hook, a top seat and the D1; the plug shows behind it
module cut_side() { difference() { children(); translate([cut_x, -500, -500]) cube([500, 1000, 1000]); } }

// As mounted, Y up in the image: front = at the desk (+X on the left); side = looking from +X, arm on the left.
module orient(o) {
    if (o == "front") rotate([0, 180, 0]) children();
    else if (o == "side") rotate([0, -90, 0]) children();
    else children();
}

if (view == "front") orient("front") { shell(); back_placed(); screens(); }
else if (view == "front_xray") orient("front") { ghost(0.15) shell(); color("orange", 0.6) tray_placed(); standins(); screens(); }
else if (view == "side_xray") orient("side") { color("lightgray") cut_side() shell(); ghost(0.3) back_placed(); color("orange") cut_side() tray_placed(); standins(cut = true); }
else if (view == "shell") shell();
else if (view == "back") back();
else if (view == "tray") tray();
else if (view == "layers") exploded();
else if (view == "open") { shell(); standins(); color("orange") tray_placed(); }
else { shell(); standins(); color("orange") tray_placed(); translate([0, 0, 25]) back_placed(); }
