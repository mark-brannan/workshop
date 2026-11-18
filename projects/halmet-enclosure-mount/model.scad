// Frame that holds a Hat Labs HALMET board in the 158x90x60 pre-drilled box.
// Screws to the box's six holed floor bosses and rests on its four no-hole posts;
// two standoffs take the board's M3 slots. Zip-tie slots give the wiring strain relief.
// A separate tier (part-tier.scad) screws onto it and carries the displays at rim height.
// An LM393 light sensor rides in a cradle on the tier, under the OLED; its photocell peeks out past the tier's left edge.
// Origin: centre of the box floor. X along the box length. Print flat, standoffs up; the tier prints upside down.

mode = "2d";         // [2d:laser profile, 3d:print]
part = "frame";      // [frame, gauge:thin solid fit check with the raised features, tier:display tier, 3D only]

/* [Box: owner's estimates, tune after a gauge print] */
boss_span = 143;     // holed bosses, centre to centre: 140 printed, its screws sat at the fork mouths (photo), so +3 (1.5 a side)
boss_pitch = 21.7;   // neighbouring bosses on one end: 21 printed, outer screws hit inside their slots; 22.5 printed, a touch wide (photo); 22 printed; 21.7 next
screw_d = 3.4;       // M3 clearance: the tier's standoff screws
slot_d = 2.8;        // M2.5 clearance: the screws into the bosses (pill slots)
end_ext = 2.9;       // each end bar reaches this much past the slots' reach: a 1.5 rim past the closed slot end; the floor is 151 inside
slot_reach = 1;      // each pill slot accepts the boss this far in or out of boss_span; closed ends
boss_h = 3.5;        // holed boss height above the floor
boss_d = 6;          // holed boss outside diameter (photo)
lid_col_x = 64.8;    // lid-screw column in each corner, full height: inner edge along X (photo)
lid_col_y = 32.4;    // and across Y; keep the display clear of both

/* [Rest posts: four no-hole posts on the long sides] */
post_dx = 80;        // centre to centre along the length (photo 77 to 80)
post_dy = 70;        // centre to centre across the width (photo 67 to 69)
post_h = 2.5;        // ~1 below the bosses (owner); the flat frame clears them by that, a stick-on pad closes it
frame_w = 75;        // gland side: pads stop at -frame_w/2, short of the gland nuts
pad_r = 4.5;         // semicircle tab over each back rest post (post ~5 diameter)
tab_r = 3.5;         // front (gland side) tabs: narrower, a rounded lobe 7 across, centred tab_dy inside the post so it still covers it
tab_dy = 1;
tab_blend = 3;       // concave fillet where the lobe meets the front edge
tab_bevel = 2.5;     // the front tabs slope down this much from the plate's front edge to the tip, clear of the gland nuts

/* [Zip-tie strain relief: slot pairs, the tie loops under the frame] */
tie_w = 4;           // slot length; takes ties up to 3.6 mm wide
tie_t = 2;           // slot width
tie_gap = 5;         // slot centre to slot centre
tie_c = 1;           // underside chamfer on each slot's outer edge, where the tie turns under
tie_bar_y = -29;     // slot pairs along the gland-side edge
tie_bar_xs = [-55, -33, -11, 11, 33, 55];  // evenly along the gland-side edge
tie_end_ys = [-10.5, 10.5];  // slot pairs on the left end, between bosses

/* [Board position on the floor] */
board_dx = -20.75;   // left edge just clear of the left fork slots
board_dy = 12.5;     // back edge about at the box's back wall (owner checked the fit)

/* [Display tier: a flat plate on four M3 F/F hex standoffs] */
rim_z = 39;          // box floor to rim (owner)
tier_t = 2.5;        // its top sits at the rim, give or take 5 (owner)
tier_x0 = 26;         // left edge; the left side stays open for the USB plug and wiring
tier_x1 = 72;        // right edge, a cantilever past the right wall
tier_y0 = -16;       // front edge
tier_cols = [[31, 34.5], [60.5, 30], [37, -11.25], [58, -11.25]];  // standoff centres; back right clear of the OLED header
tier_standoff = 19.7;  // M3 hex standoff, into the pad's insert (owner's calipers)
tier_boss_d = 7;     // printed pad under each standoff
tier_pad_h = 8;      // pad top above the plate's underside: a blind M3 heat-set insert and a 1.5 floor
mod_standoff = 15;   // M2.5 F/F standoffs, tier to module: the tallest that clears the lid
lid_depth = 17;      // rim to lid ceiling (owner, caliper; the gasket may add 0.5)
tier_round = 1.5;    // tier: outside-corner radius
tier_win_inset = 5;  // tier: segment display window, this far inside the module's screw centres
tier_win_round = 1.5; // tier: corner radius of the joined segment / OLED-plug opening
ldr_win_edge = 0.3;  // tier: window under the sensor stops this far inside the ledges
oled_pin_in = 1.6;   // OLED header pin row from its edge (generic; caliper it); the header is on the front edge, toward the glands
head_d = 6.5;        // M3 pan head, screwed up from under the plate
head_h = 2.5;
m25_d = 2.8;         // module screws: M2.5 through the tier into an F/F standoff under the module
oled_w = 27.3;       // 0.96" SSD1306, generic
oled_h = 27.8;
oled_hole_dx = 23.3; // caliper the one in hand
oled_hole_dy = 23.6;
oled_x = 49.65;      // back posts inside the plate's back edge, right edge 0.5 clear of the lid-screw column
oled_y = 25.2;
seg_w = 41;          // TM1637 4-digit module (owner)
seg_h = 23;
seg_hole_dx = 37.5;  // owner, caliper (parts.md); 36 from rough calipers was 1.5 narrow
seg_hole_dy = 19;    // owner
seg_gap = 1.5;       // below the OLED, toward the glands

/* [Light sensor on the tier: LM393 photoresistor module, 31 x 14, one M3 hole (owner's, on hand)] */
ldr_x0 = 25.5;       // photocell end, at the tier's left edge; as far right as the back-right tier screw head allows
ldr_y = 23.8;        // between the OLED's standoff columns, clear of the back-left tier screw head
ldr_l = 31;          // owner, caliper
ldr_w = 14;
ldr_hole_in = 7;     // hole centre from the header end, centred across: its rim 5 from that end and both edges (owner)
ldr_part_h = 4.6;    // trimpot above the board top: 6.2 from the board's underside (owner)
pcb_t = 1.6;
ldr_ledge = 1.5;     // the module sits on edge ledges this high, clear of its solder stubs
ldr_lip = 1.2;       // how far a ledge reaches in under the board's edge: solder pads sit 1.4 in
ldr_cell_clear = 4;  // nothing under the photocell end this far in: solder from the cell's leads
ldr_wall = 1.2;      // cradle side walls, flush with the PCB top: stop it turning on its one screw
ldr_fit = 0.3;       // per side
ldr_boss_d = 7;      // pad round the screw, at ledge height
ldr_head_d = 6.2;    // round recess in the tier's underside for the M3 screw head (pan head 5.5 across, plus clearance)
ldr_head_h = 2.2;    // its depth from the underside: a 2 mm head, leaving 1.8 of tier and ledge pad above
ldr_pin_l = 6;       // header pins past the header end (owner); bend or swap them once the module is placed

/* [Plate: hex-lightened] */
plate_t = 4.0;
plate_y_lo = -33;    // gland-side edge between the lid-screw columns
plate_y_hi = 39.5;   // back edge between the lid-screw columns, tangent to the rear post tabs
rim_w = 2;           // solid rim round the outline
hex_flat = 9;         // hex cell across flats
hex_web = 2.0;       // wall between cells
hex_x0 = 1.5;        // grid offset
hex_y0 = 3;
gauge_t = 1;          // fit-check plate: five 0.2 mm layers
gauge_rise = 2;       // fit-check standoffs, rests and tier bosses: stubs this tall, holes through
gauge_cell = 24.5;      // fit-check windows: hex cells this wide across flats; 24 left a window tangent to a tier-stub hole
gauge_web = 4;

/* [Standoffs] */
standoff_h = 5;      // board underside above the frame
standoff_d = 7;
insert_d = 4.0;      // M3 heat-set insert, pressed in from the top; the hole runs through the plate
rest_d = 4;          // plain rests on the other diagonal
spacer_hole_d = 3.2; // laser and gauge: M3 through a loose spacer
support_xy = [0, 0]; // centre of the box floor: through hole for an M3 heat-set insert, an adjustable standoff screws in from below as a centre prop

/* [Hidden] */
$fn = 48;
// From HALMET.kicad_pcb, relative to the centre of the 89 x 58 board.
slots = [[-21.75, 22.5], [22.75, -22.5]];
recess = max(0, boss_h - post_h);   // underside pockets this deep over the six holed bosses, so the plate sits on the rest posts, not propped on the bosses
body_t = plate_t;
rests = [[36, 18], [-38.5, -19.5]];
bar_x0 = boss_span/2 - slot_reach - screw_d/2 - 3;   // inner edge of an end bar
bar_x1 = boss_span/2 + slot_reach + end_ext;                   // outer edge
seg_x = oled_x;
seg_y = oled_y - oled_h/2 - seg_gap - seg_h/2;
oled_posts = [for (sx = [-1, 1], sy = [-1, 1]) [oled_x + sx*oled_hole_dx/2, oled_y + sy*oled_hole_dy/2]];
seg_posts = [for (sx = [-1, 1], sy = [-1, 1]) [seg_x + sx*seg_hole_dx/2, seg_y + sy*seg_hole_dy/2]];
ldr_post = [ldr_x0 + ldr_l - ldr_hole_in, ldr_y];   // the module's one M3 hole
tier_z0 = tier_pad_h;                  // standoff feet: top of the pads
tier_z1 = tier_z0 + tier_standoff + tier_t;  // top of the tier plate
y_hi = boss_pitch + 6;    // end bars
y_lo = -boss_pitch - 6;

module at_board(pts) { for (p = pts) translate([p[0] + board_dx, p[1] + board_dy]) children(); }

// Front tab over a gland-side rest post: a lobe that blends into the front edge with a concave fillet.
module front_tab2d(sx) {
    offset(r = -tab_blend) offset(r = tab_blend) union() {
        translate([sx*post_dx/2 - tab_r - 2*tab_blend, plate_y_lo]) square([2*(tab_r + 2*tab_blend), 3]);   // strip flush with the plate's front edge, wide enough for the fillet to run out tangent
        translate([sx*post_dx/2, -post_dy/2 + tab_dy]) circle(r = tab_r);
    }
}

// Outline: one plate over the bosses, the four rest posts, the board and the display.
module outline2d() {
    intersection() {
        union() {
            offset(r = 2) offset(delta = -2) for (r = plate_rects) translate([r[0], r[1]]) square([r[2] - r[0], r[3] - r[1]]);
            for (sx = [-1, 1]) translate([sx*post_dx/2, post_dy/2]) circle(r = pad_r);
            for (sx = [-1, 1]) front_tab2d(sx);
            at_board(slots) circle(r = standoff_d/2 + 0.5);   // the back one stays inside the straight back edge
        }
        translate([-100, -frame_w/2]) square([200, 100 + frame_w/2]);
    }
}

// Lattice: hex cells inside the rim, a web clear of every solid island
// (screw ends, post pads, standoffs, rests, display posts, tie slots).
plate_rects = concat(                         // outline as [x0, y0, x1, y1] boxes
    [[-bar_x1, y_lo, bar_x1, y_hi], [-lid_col_x + 1, plate_y_lo, lid_col_x - 1, plate_y_hi]],
    []);   // the front tabs are front_tab2d
keep_rects = concat(
    [[-100, -100, -(boss_span/2 - slot_reach - screw_d/2 - 1.5), 100], [boss_span/2 - slot_reach - screw_d/2 - 1.5, -100, 100, 100]],
    [[-lid_col_x + 1, -100, lid_col_x - 1, tie_bar_y + tie_w/2 + 2]],   // solid band along the gland side
    [for (x = tie_bar_xs) [x - tie_gap/2 - tie_t/2 - 2, tie_bar_y - tie_w/2 - 2, x + tie_gap/2 + tie_t/2 + 2, tie_bar_y + tie_w/2 + 2]],
    [for (y = tie_end_ys) [-bar_x1, y - tie_gap/2 - tie_t/2 - 2, -(bar_x0 + bar_x1)/2 + tie_w/2 + 2, y + tie_gap/2 + tie_t/2 + 2]]);
keep_discs = concat(   // [x, y, r]
    [for (sx = [-1, 1]) [sx*post_dx/2, post_dy/2, pad_r]],
    [for (sx = [-1, 1]) [sx*post_dx/2, -post_dy/2 + tab_dy, tab_r]],
    [for (s = slots) [s[0] + board_dx, s[1] + board_dy, standoff_d/2 + 2]],
    [for (s = rests) [s[0] + board_dx, s[1] + board_dy, rest_d/2 + 2]],
    [for (c = tier_cols) [c[0], c[1], tier_boss_d/2]],
    [[support_xy[0], support_xy[1], standoff_d/2 + 2]]);


module keep2d() {
    for (r = keep_rects) translate([r[0], r[1]]) square([r[2] - r[0], r[3] - r[1]]);
    for (d = keep_discs) translate([d[0], d[1]]) circle(r = d[2]);
}

// Full hex grid clipped to the rim and a web clear of the islands; cells cut there stay,
// slivers narrower than 2.5 mm drop out.
module lattice2d(flat = hex_flat, web = hex_web, x0 = hex_x0, y0 = hex_y0, rim = rim_w) {
    r = flat/sqrt(3); pitch = flat + web;
    offset(r = 1.25) offset(r = -1.25) intersection() {
        difference() { offset(delta = -rim) outline2d(); offset(delta = web) keep2d(); }
        for (i = [-12:12], j = [-8:8])
            translate([x0 + i*pitch + (j % 2 == 0 ? 0 : pitch/2), y0 + j*pitch*sqrt(3)/2])
                offset(r = 0.8) offset(delta = -0.8) rotate(30) circle(r = r, $fn = 6);
    }
}

module solid2d() { difference() { outline2d(); lattice2d(); } }

// Children at each tie slot's centre: slot length along local Y, local +X away from its pair's web.
module tie_each() {
    for (x = tie_bar_xs, s = [-1, 1]) translate([x + s*tie_gap/2, tie_bar_y]) mirror([s < 0 ? 1 : 0, 0]) children();
    for (y = tie_end_ys, s = [-1, 1]) translate([-(bar_x0 + bar_x1)/2, y + s*tie_gap/2]) rotate(90) mirror([s < 0 ? 1 : 0, 0]) children();
}

module tie_slots() { tie_each() square([tie_t, tie_w], center = true); }

module tie_chamfers() {
    tie_each() hull() {
        translate([0, 0, -1]) linear_extrude(1) translate([tie_c/2, 0]) square([tie_t + tie_c, tie_w + 0.02], center = true);
        translate([0, 0, tie_c]) linear_extrude(0.01) square([tie_t - 0.02, tie_w + 0.02], center = true);
    }
}

module fork_slots() {
    for (sx = [-1, 1], k = [-1, 0, 1]) scale([sx, 1]) translate([0, k*boss_pitch]) hull() {
        translate([boss_span/2 - slot_reach, 0]) circle(d = slot_d);
        translate([boss_span/2 + slot_reach, 0]) circle(d = slot_d);
    }
}

module profile(spacer_holes) {
    difference() {
        solid2d();
        fork_slots();
        tie_slots();
        if (spacer_holes) at_board(slots) circle(d = spacer_hole_d);
    }
}

// Standoffs, rests and tier pads at their true heights; the board standoffs take inserts,
// the pads an M3 from below into the tier standoff, its head counterbored.
module raised() {
    linear_extrude(body_t + standoff_h) at_board(slots) circle(d = standoff_d);
    linear_extrude(body_t + standoff_h) at_board(rests) circle(d = rest_d);
    linear_extrude(tier_z0) for (c = tier_cols) translate(c) circle(d = tier_boss_d);
}

module insert_holes() {
    translate([0, 0, -1]) linear_extrude(tier_z0 + 2) for (c = tier_cols) translate(c) circle(d = insert_d, $fn = 64);
    translate([0, 0, -1]) linear_extrude(body_t + standoff_h + 2) at_board(slots) circle(d = insert_d, $fn = 64);
}

module tab_bevel_cut() {
    run = frame_w/2 + plate_y_lo;   // tab length past the plate's front edge
    rotate([90, 0, 90]) linear_extrude(200, center = true) polygon([
        [plate_y_lo + 0.5, body_t + tab_bevel*0.5/run], [-frame_w/2 - 1, body_t - tab_bevel*(run + 1)/run],
        [-frame_w/2 - 1, body_t + 1], [plate_y_lo + 0.5, body_t + 1]]);
}

// Z = 0 is the top of the rest posts; the holed bosses reach up into the pockets.
module frame() {
    difference() {
        union() {
            linear_extrude(body_t) profile(false);
            raised();
        }
        insert_holes();
        translate([support_xy[0], support_xy[1], -1]) cylinder(d = insert_d, h = body_t + 2);   // centre prop: through, insert from the top
        tie_chamfers();
        tab_bevel_cut();
        if (recess > 0) recess_cut();
    }
}

// 45-degree walls: the pocket over each boss prints without supports.
module recess_cut() {
    r1 = boss_d/2 + 0.2;
    for (sx = [-1, 1], k = [-1, 0, 1]) scale([sx, 1, 1]) translate([0, k*boss_pitch, -1]) hull()
        for (x = [boss_span/2 - slot_reach, boss_span/2 + slot_reach]) translate([x, 0, 0]) cylinder(h = recess + 1, r1 = r1 + recess + 1, r2 = r1);
}

// Fast fit check: the frame's outline and slots on a thin plate with big windows; short stubs mark
// the standoffs, rests and tier bosses, each holed through at its centre.
module gauge() {
    difference() {
        union() {
            linear_extrude(gauge_t) difference() {
                outline2d(); fork_slots(); tie_slots();
                lattice2d(gauge_cell, gauge_web, 0, 0, 4);
            }
            linear_extrude(gauge_t + gauge_rise) {
                at_board(slots) circle(d = standoff_d);
                at_board(rests) circle(d = rest_d);
                for (c = tier_cols) translate(c) circle(d = tier_boss_d);
            }
        }
        translate([0, 0, -1]) linear_extrude(gauge_t + gauge_rise + 2) {
            at_board(slots) circle(d = insert_d);
            at_board(rests) circle(d = 1.5);
            for (c = tier_cols) translate(c) circle(d = insert_d);
        }
    }
}

// Tier, in box coordinates (Z = 0 on the rest posts): a flat plate at the rim on four F/F standoffs,
// screwed down from above; modules on M2.5 F/F standoffs, screwed up from below.
module tier_rect2d() {   // the space the tier may use: clear of the lid-screw columns
    translate([tier_x0, tier_y0]) square([tier_x1 - tier_x0, lid_col_y - 1 - tier_y0]);
    translate([tier_x0, tier_y0]) square([lid_col_x - 1 - tier_x0, plate_y_hi - tier_y0]);
}

// A plain plate over the allowed space, square-sided, with one opening from under the segment display up to
// the OLED's header plug, and a window under the light sensor. Solid elsewhere.
module tier_plate2d() {
    offset(r = tier_round) offset(delta = -tier_round) tier_rect2d();
}

module seg_win2d() {   // under the segment display, tier_win_inset inside its screw centres
    translate([seg_x - seg_hole_dx/2 + tier_win_inset, seg_y - seg_hole_dy/2 + tier_win_inset])
        square([seg_hole_dx - 2*tier_win_inset, seg_hole_dy - 2*tier_win_inset]);
}
module oled_plug2d() {   // the Dupont plug on the OLED header pins passes through here
    translate([oled_x - 6.5, oled_y - oled_h/2 + oled_pin_in - 2.3]) square([13, 4.4]);
}

module tier_windows2d() {
    // the two joined: straight sides from the segment window to the plug window's bottom edge, so the OLED's
    // front posts keep their land; symmetric about the displays' centre line, corners rounded
    offset(r = tier_win_round) offset(delta = -tier_win_round) union() {
        hull() { seg_win2d(); intersection() { oled_plug2d(); translate([0, oled_y - oled_h/2 + oled_pin_in - 2.3]) square([200, 0.01]); } }
        oled_plug2d();
    }
    // under the light sensor, between its ledges, from the photocell end's bare zone to short of the screw pad
    w = ldr_w + 2*ldr_fit;
    x0 = ldr_x0 + ldr_cell_clear;
    translate([x0, ldr_y - (w/2 - ldr_fit - ldr_lip) + ldr_win_edge])
        square([ldr_post[0] - ldr_boss_d/2 - 1 - x0, 2*(w/2 - ldr_fit - ldr_lip - ldr_win_edge)]);
}

// Sensor cradle: a floor bridging the band under the OLED, edge ledges and a pad round the screw that lift
// the module off its solder stubs, and side walls that stop it turning. Both ends open: photocell and header.
ldr_c = ldr_w/2 + ldr_fit + ldr_wall;   // floor half-width
module ldr_floor2d() { offset(r = 1.5) offset(delta = -1.5) translate([ldr_x0, ldr_y - ldr_c]) square([ldr_l, 2*ldr_c]); }

module ldr_cradle() {
    w = ldr_w + 2*ldr_fit;
    linear_extrude(ldr_ledge) {
        for (s = [-1, 1]) translate([ldr_x0 + ldr_cell_clear, ldr_y + (s < 0 ? -w/2 : w/2 - ldr_fit - ldr_lip)])
            square([ldr_l - ldr_cell_clear, ldr_fit + ldr_lip]);
        translate(ldr_post) circle(d = ldr_boss_d);
    }
    linear_extrude(ldr_ledge + pcb_t) difference() {
        for (s = [-1, 1]) let(
            y0 = ldr_y + (s < 0 ? -w/2 - ldr_wall : w/2),
            // a tier screw head over the wall's photocell half moves the wall's start past the head, no sliver left
            x0 = max(concat([ldr_x0 + 1.5], [for (c = tier_cols)
                if (c[0] < ldr_x0 + ldr_l/2 && abs(c[1] - y0 - ldr_wall/2) < head_d/2 + 0.5 + ldr_wall/2) c[0] + head_d/2 + 0.5])))
            translate([x0, y0]) square([ldr_x0 + ldr_l - 1.5 - x0, ldr_wall]);
        for (p = oled_posts) translate(p) circle(d = 6.5);   // M2.5 standoffs pass beside the walls
    }
}

module tier() {
    difference() {
        union() {
            translate([0, 0, tier_z1 - tier_t]) linear_extrude(tier_t) difference() {
                tier_plate2d();
                tier_windows2d();
                for (c = tier_cols) translate(c) circle(d = screw_d);
                for (p = concat(oled_posts, seg_posts)) translate(p) circle(d = m25_d);
            }
            translate([0, 0, tier_z1 - 0.01]) intersection() { ldr_cradle(); linear_extrude(10) offset(delta = -0.3) ldr_floor2d(); }
        }
        translate([ldr_post[0], ldr_post[1], tier_z1 - tier_t - 1]) cylinder(d = screw_d, h = 30);   // M3 up from underneath, nut on the board top
        translate([ldr_post[0], ldr_post[1], tier_z1 - tier_t - 1]) cylinder(d = ldr_head_d, h = 1 + ldr_head_h);   // screw-head recess in the underside
    }
}

if (part == "tier") tier();
else if (part == "gauge") gauge();
else if (part != "frame") ;   // assembly.scad draws its own
else if (mode == "2d") profile(true);
else frame();
