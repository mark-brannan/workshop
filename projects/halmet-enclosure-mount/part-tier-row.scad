// Flat tier carrying an OLED and two TM1637 modules end to end, the LM393 light sensor in a cradle on top, under the OLED.
// Prints flat on its underside, no supports: nothing hangs below the plate. Millimetres, installed orientation:
// plate top at z = 0, everything else up. Origin as model.scad (box floor centre). Three M3 from above hold it to the standoffs.
/* [Plate] */
plate_t = 2.5;
x0 = 21.3;  x1 = 72;     // plate edges; the back part stops at x_back for the lid-screw column
x_back = 63.8;
y_front = -38;  y_back = 39.5;  y_col = 31.4;   // the full-width part spans -y_col..y_col; front edge is the lower-right post's radius tangent
round_r = 1.5;
/* [Tier screws: M3 through, head on top, into the frame's standoffs] */
tier_pts = [[19, -22.5], [24, 36], [70, 10.85]];
tier_hole = 3.4;
island_d = 8;            // solid round each screw, an ear where it falls off the plate
head_d = 6.5;            // M3 pan head on the tier top
/* [Modules, one centre line, end to end: 24 + 24 + 28] */
cx = 43.55;              // 0.5 left of first packing, the most the front-left tier screw's island allows
tm_y = [-25, -1];        // TM1637 centres, 23 x 41 boards
tm_w = 41;  tm_h = 23;
oled_y = 25.4;           // 27.3 x 27.8 board
oled_w = 27.3;  oled_h = 27.8;
tm_dx = 37.5;  tm_dy = 19;   // module screw spacing
oled_dx = 23.3;  oled_dy = 23.6;
tm_boss_h = 3;  tm_boss_d = 6;  tm_hole = 2.8;       // M2.5
oled_standoff_h = 10;  oled_pad_d = 4.5;  oled_hole = 2.5;   // OLED on stock M2 F/F standoffs, 10 long (2.3 over the sensor stack), M2 screws through plain holes from under the tier, the plate round each hole flat
lid_col_x = 68;  lid_col_y = 34;   // lid-screw column, inner corner (from the 158 x 90 outside)
col_gap = 0.25;          // a boss beside the column is cut this far short of it (the board edge's gap as first packed)
win_inset = 5;           // opening under the two TM1637s, this far inside their screw centres
win_round = 1.5;
tm_edge = tm_dx/2 + 2.4; // right edge, straight, past the right-hand screw line by hole radius + 1: the bent header pins need the rest
oled_pin_in = 1.6;       // OLED header row from its front edge (toward the glands): a slot under it for the plug
plug_w = 12;  plug_d = 4;
/* [Lightening: plate nothing stands on is cut away] */
post_margin = 1.5;       // plate kept round a boss, past its radius
swoop_r = 8;             // outline: inside corners swept at this radius, so ears flow into the edge
corner_r = 3;            // outline: outside corners
mid_y1 = 15.4;           // centre: window under the OLED's I2C header, up to short of the sensor cradle's front wall
/* [Light sensor on top: LM393 module, component side up, one M3 up from under the tier, nut on top] */
ldr_x0 = 17.3;  ldr_y = 25.4;  ldr_l = 31;  ldr_w = 14;   // photocell end at ldr_x0: 4 mm out past the plate's left edge, the ledges start on it (x0 = ldr_x0 + ldr_cell_clear)
ldr_hole_in = 7;         // screw hole from the header end
ldr_part_h = 4.6;        // trimpot above the board top
pcb_t = 1.6;
ldr_ledge = 1.5;         // edge ledges, clear of the solder stubs
ldr_lip = 1.2;           // how far a ledge reaches in under the board's edge
ldr_cell_clear = 4;      // nothing under the photocell end this far in
ldr_wall = 1.2;  ldr_fit = 0.3;
ldr_boss_d = 7;          // pad round the screw, at ledge height
ldr_head_d = 6.2;  ldr_head_h = 2.2;   // screw-head recess in the underside
ldr_win_edge = 0.3;      // window under the board stops this far inside the ledges
$fn = 48;

tm_posts = [for (y = tm_y, sx = [-1, 1], sy = [-1, 1]) [cx + sx*tm_dx/2, y + sy*tm_dy/2]];
oled_posts = [for (sx = [-1, 1], sy = [-1, 1]) [cx + sx*oled_dx/2, oled_y + sy*oled_dy/2]];
lr_post = [cx + tm_dx/2, tm_y[0] - tm_dy/2];   // lower-right TM1637 post: the plate's corner is concentric with it
lr_r = tm_boss_d/2 + 0.5;   // 0.5 mm of plate round the post
ldr_post = [ldr_x0 + ldr_l - ldr_hole_in, ldr_y];

module rr(a, b, c, d) { offset(r = round_r) offset(delta = -round_r) translate([a, b]) square([c - a, d - b]); }
function clamp(v, lo, hi) = min(max(v, lo), hi);

// Ear: the screw's island hulled to the nearest point well inside the plate.
module ear2d(p) {
    r = island_d/2;
    inner = abs(p[1]) <= y_col - r ? [x0 + r, x1 - r] : [x0 + r, x_back - r];
    hull() { translate(p) circle(r = r); translate([clamp(p[0], inner[0], inner[1]), clamp(p[1], y_front + r, y_back - r)]) circle(r = r); }
}
module bosses2d(posts, d) { for (p = posts) translate(p) circle(d = d); }   // round, never clipped
// Right side: a straight brace from the OLED's back-right post, tangent to both it and the right ear, round the ear
// to its underside, then straight down the right edge, on the line tm_edge past the TM1637s' screw centres.
ear_leave = -90;         // where the outline leaves the right ear's underside, degrees from +x
module right_keep2d() {
    a = oled_posts[3];  ra = oled_pad_d/2 + post_margin;   // back-right OLED post
    b = tier_pts[2];    rb = island_d/2;                    // right ear
    u = (b - a) / norm(b - a);
    n = [-u[1], u[0]];                       // away from the plate
    sp = (ra - rb) / norm(b - a);
    m = n*sqrt(1 - sp*sp) + u*sp;            // normal of the common outer tangent
    ta = a + ra*m;
    top = atan2(m[1], m[0]);
    arc = [for (i = [0:24]) let(t = top + (ear_leave - top)*i/24) b + rb*[cos(t), sin(t)]];
    p0 = b + rb*[cos(ear_leave), sin(ear_leave)];
    p3 = [cx + tm_edge, lr_post[1]];                // the right edge: one straight line
    s = [[p3[0], p0[1]], p3];
    polygon(concat([[ta[0], 100], ta], arc, s, [[p3[0], -100], [-100, -100], [-100, 100]]));
}
module plate2d() {
    offset(r = corner_r) offset(delta = -corner_r) difference() {
        offset(r = -swoop_r) offset(delta = swoop_r) {   // swept after the cut, so ears flow into the edge
            intersection() {
                union() {
                    rr(x0, y_front, x_back, y_back);
                    rr(x0, -y_col, x1, y_col);
                    for (p = tier_pts) ear2d(p);
                    bosses2d(tm_posts, tm_boss_d + 1);
                    translate([cx, y_front]) square([100, y_back - y_front]);   // out to the right side's line
                    intersection() {   // the lower-right corner: the post's own radius, cut at the front edge
                        translate(lr_post) circle(r = lr_r);
                        translate([x0, y_front]) square([100, 100]);
                    }
                }
                right_keep2d();
            }
        }
    }
    intersection() {   // every boss stands on plate where the corner rounding nicks it; none past the straight right edge
        bosses2d(tm_posts, tm_boss_d + 0.4);
        translate([-100, -100]) square([100 + cx + tm_edge, 200]);
    }
    bosses2d(oled_posts, oled_pad_d + 0.4);
}
module windows2d() {
    module win(y) translate([cx - tm_dx/2 + win_inset, y - tm_dy/2 + win_inset]) square([tm_dx - 2*win_inset, tm_dy - 2*win_inset]);
    // one window under both TM1637s, run on up under the OLED's I2C header: full width to short of the OLED's front
    // bosses, then between them to short of the sensor cradle (it takes in the header plug's slot)
    ob = oled_y - oled_dy/2 - oled_pad_d/2 - post_margin;      // below the OLED's front bosses
    ox = oled_dx/2 - oled_pad_d/2 - post_margin;               // between them
    offset(r = win_round) offset(delta = -win_round) offset(r = -win_round) offset(delta = win_round) union() {
        hull() for (y = tm_y) win(y);
        translate([cx - tm_dx/2 + win_inset, 0]) square([tm_dx - 2*win_inset, ob]);
        translate([cx - ox, 0]) square([2*ox, mid_y1]);
    }
    translate([cx - plug_w/2, oled_y - oled_h/2 + oled_pin_in - plug_d/2]) square([plug_w, plug_d]);   // OLED header plug
    // under the light sensor, between its ledges, from the photocell end's bare zone to short of the screw pad
    w = ldr_w + 2*ldr_fit;
    wx0 = max(ldr_x0 + ldr_cell_clear, x0 + 4);   // a 4 mm rail stays along the plate's left edge, tying the back-left screw ear to the rest
    translate([wx0, ldr_y - (w/2 - ldr_fit - ldr_lip) + ldr_win_edge])
        square([ldr_post[0] - ldr_boss_d/2 - 1 - wx0, 2*(w/2 - ldr_fit - ldr_lip - ldr_win_edge)]);
    // right of the OLED: the brace to the right ear, cut back to a rim along the diagonal edge, a ring round the ear and a margin round the
    // OLED's right-hand bosses and the TM1637s' back-right boss
    rim = 2.4;
    offset(r = win_round) offset(delta = -win_round) difference() {
        union() {
            intersection() {
                offset(delta = -rim) plate2d();
                translate([oled_posts[3][0] + oled_pad_d/2 + post_margin, tm_posts[7][1] + tm_boss_d/2 + post_margin]) square([100, 100]);
            }
            // a rounded-rectangle bay under the OLED's right half, between its right-hand posts, 2.7 mm short of the sensor ledges' ends
            offset(r = 3) offset(delta = -3) translate([51, 19.5]) square([9, 11.5]);
        }
        translate(tier_pts[2]) circle(r = island_d/2 + 1);
    }
}

// Sensor cradle (as model.scad's tier): edge ledges and a screw pad lift the board off its solder, side walls stop it turning.
module ldr_cradle() {
    w = ldr_w + 2*ldr_fit;
    linear_extrude(ldr_ledge) {
        for (s = [-1, 1]) let(ly = ldr_y + (s < 0 ? -w/2 : w/2 - ldr_fit - ldr_lip),
            // a tier screw head over the ledge moves its start past the head too
            lx = max(concat([ldr_x0 + ldr_cell_clear], [for (c = tier_pts)
                if (c[0] < ldr_x0 + ldr_l/2 && abs(c[1] - ly - (ldr_fit + ldr_lip)/2) < head_d/2 + 0.5 + (ldr_fit + ldr_lip)/2) c[0] + head_d/2 + 0.5])))
            translate([lx, ly]) square([ldr_x0 + ldr_l - lx, ldr_fit + ldr_lip]);
        translate(ldr_post) circle(d = ldr_boss_d);
    }
    linear_extrude(ldr_ledge + pcb_t) for (s = [-1, 1]) let(
        y0 = ldr_y + (s < 0 ? -w/2 - ldr_wall : w/2),
        // a tier screw head over the wall's photocell half moves the wall's start past the head
        wx0 = max(concat([x0], [for (c = tier_pts)
            if (c[0] < ldr_x0 + ldr_l/2 && abs(c[1] - y0 - ldr_wall/2) < head_d/2 + 0.5 + ldr_wall/2) c[0] + head_d/2 + 0.5])))
        translate([wx0, y0]) square([ldr_x0 + ldr_l - 1.5 - wx0, ldr_wall]);
}

module tier_row() {
    difference() {
        union() {
            translate([0, 0, -plate_t]) linear_extrude(plate_t) difference() { plate2d(); windows2d(); }
            translate([0, 0, -0.01]) {
                linear_extrude(tm_boss_h + 0.01) intersection() { bosses2d(tm_posts, tm_boss_d); translate([-100, -100]) square([100 + cx + tm_edge, 200]); }
                ldr_cradle();
            }
        }
        for (p = tier_pts) translate([p[0], p[1], -plate_t - 1]) cylinder(d = tier_hole, h = plate_t + 2);
        for (p = tm_posts) translate([p[0], p[1], -plate_t - 1]) cylinder(d = tm_hole, h = plate_t + tm_boss_h + 2);
        for (p = oled_posts) translate([p[0], p[1], -plate_t - 1]) cylinder(d = oled_hole, h = plate_t + 2);
        translate([ldr_post[0], ldr_post[1], -plate_t - 1]) cylinder(d = tier_hole, h = 20);   // M3 up through the board, nut on top
        translate([ldr_post[0], ldr_post[1], -plate_t - 1]) cylinder(d = ldr_head_d, h = 1 + ldr_head_h);   // head recess
    }
}

// assembly.scad `use`s this file and cannot see its variables: it reads them here.
function row(k) = let(t = [["cx", cx], ["tm_y", tm_y], ["tm_posts", tm_posts], ["oled_y", oled_y], ["tm_boss_h", tm_boss_h],
    ["oled_standoff_h", oled_standoff_h], ["oled_pin_in", oled_pin_in], ["ldr_x0", ldr_x0], ["ldr_y", ldr_y], ["ldr_post", ldr_post]])
    t[search([k], t)[0]][1];

tier_row();
