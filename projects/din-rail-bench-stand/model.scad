// DIN-rail bench stand: one end bracket of a pair, holding four TS35 rails.
// parts: bench-stand-bracket
// Two rails cross the sloped front face, one above the other; the third lies flat on the foot, in front of them;
// the fourth lies flat inside the frame at the back, under the face, for AC gear: a small PSU, terminals, relays.
//
// After Szmalu's "DIN Rail Stand KIT" (Thingiverse 3609072; nothing of its mesh is used): each rail passes through
// the bracket in a slot of its own cross-section, held between the slot's flat faces, and one M4 screw through
// the slot's cover and the rail's base pins it lengthwise. The plate is thick across the rail and the bars are
// ladders, two thin strips with a slot between, as the original's foot is. As the original, the face ends in the
// top rail's block, and a crossbar from the back post meets that block just below the rail's centre; a diagonal
// from just below the lower rail's centre to the back rail's block makes a triangle with the face and foot.
//
// The profile is drawn in 2D with x toward the front of the desk and y up, then extruded bracket_t:
// print flat, as modelled; view="assembly" stands two brackets up with rails and module envelopes;
// view="gauge" is one rail block, thin, to check the slot and screw fit before the bracket prints.

/* [View] */
view = "part";            // "part" (print), "assembly" or "gauge"

/* [Frame] */
a = 60;                   // sloped face, degrees above the desk; modules lean back 90 - a
bar_w = 11;               // width of every bar in the profile
strip = 3;                // each of a ladder bar's two strips; the slot between is bar_w - 2 strip
rung_pitch = 70;          // a rung across the ladder slot at least this often
bracket_t = 20;           // thickness of the plate (print height), across the rail

/* [Rails] */
s1 = 70;                  // tier 1 rail centre, along the face from its foot
pitch = 125;              // tier 2 sits this far above tier 1, along the face
flat_x = 280;             // flat rail centre, from the back of the stand
back_x = 60;              // back (AC) rail centre, from the back of the stand
face_shift = 35;          // face starts this far forward of the back post, to make room for the back rail

/* [Rail slot] TS35 passes through, held between the slot's faces */
rail_clr = 0.3;           // slot clearance each side of the 1 mm rail sheet; guess, gauge it
block_wall = 4;           // block beyond each rail lip
cover = 3;                // block over the rail's lips, outward

/* [Fixing] M4 x 16 screw through the cover, the rail's base slot, into a pilot below */
clear_d = 4.6;            // through the cover and the plastic in the rail's channel; guess
pilot_d = 3.7;            // guess; printed holes run small, gauge before trusting it
pilot_depth = 9;          // below the rail's base

/* [Module envelope, for the assembly view and the clearance test] */
mod_h = 90;               // DIN module height, across the rail (standard 90)
mod_d = 70;               // module depth out from the rail base (guess: PSU 55-60, meters ~65)
back_mod_d = 65;          // the back rail's modules: small PSU, terminals, relays (guess)
rail_len = 300;           // rail length in the assembly view

/* [Gauge] */
gauge_t = 10;             // gauge print height

/* [Hidden] */
$fn = 48;
e = 0.01;
u = [-cos(a), sin(a)];            // up the face
n = [sin(a), cos(a)];             // out of the face (toward the user)
face_len = s1 + pitch + 17.5 + block_wall + bar_w / 2;   // face ends at the top rail block, as the original
foot0 = [bar_w / 2 + face_shift + face_len * cos(a), bar_w / 2];   // face centreline at its foot
top = foot0 + face_len * u;                           // joined back to the post by a top bar
foot_len = flat_x + mod_h / 2 + 10;
post_top = [bar_w / 2, top[1]];
post_foot = [bar_w / 2, bar_w / 2];
foot_end = [foot_len, bar_w / 2];

function edge(s) = foot0 + s * u + (bar_w / 2) * n;  // rail base on the face's outer edge

// rail seats: base point and outward direction
seats = [[edge(s1), n], [edge(s1 + pitch), n], [[flat_x, bar_w], [0, 1]], [[back_x, bar_w], [0, 1]]];
function local(c, o, x, y) = c + x * [o[1], -o[0]] + y * o;
below = 8;                                          // braces meet a block this far below the rail's centre line
j2 = local(edge(s1 + pitch), n, below, -bar_w / 2);  // crossbar meets the tier 2 block, inside
j1 = local(edge(s1), n, below, -bar_w / 2);          // diagonal meets the tier 1 block, inside
k0 = [back_x + 17.5 + block_wall - bar_w / 2, bar_w + 7.5 + cover - bar_w / 2];   // back rail block, upper front corner
cross_from = [bar_w / 2, j2[1]];

module bar(p, q, w = bar_w) hull() { translate(p) circle(d = w); translate(q) circle(d = w); }
module teardrop(d) hull() { circle(d = d); rotate(45) square(d / 2); }   // point +Y (print up after rotation)

// local frame at a seat: +y out of the rail (toward the module), +x across the rail's width
module at(c, o) translate(c) rotate(atan2(o[1], o[0]) - 90) children();

module rail2d() polygon([[-17.5, 7.5], [-17.5, 6.5], [-12.5, 6.5], [-12.5, 0], [12.5, 0], [12.5, 6.5], [17.5, 6.5],
                         [17.5, 7.5], [11.5, 7.5], [11.5, 1], [-11.5, 1], [-11.5, 7.5]]);
module block2d() offset(r = 2) offset(delta = -2)
    translate([-17.5 - block_wall, -bar_w]) square([35 + 2 * block_wall, bar_w + 7.5 + cover]);

module ladder_slot(p, q) {
    d = q - p; L = norm(d); k = ceil((L - 2 * bar_w) / rung_pitch);
    difference() {
        bar(p + bar_w * d / L, q - bar_w * d / L, bar_w - 2 * strip);
        for (i = [1 : k - 1]) translate(p + (bar_w + i * (L - 2 * bar_w) / k) * d / L)
            rotate(atan2(d[1], d[0])) square([strip, bar_w], center = true);
    }
}

module profile() {
    difference() {
        union() {
            bar(post_foot, foot_end);            // foot, on the desk
            bar(post_foot, post_top);            // back post
            bar(post_top, top);                  // top bar, post to face
            bar(foot0, top);                     // sloped face
            hull() { at(seats[1][0], seats[1][1]) block2d(); translate(top) circle(d = bar_w); }   // apex: top block fills the corner, as the original
            bar(cross_from, j2);                 // crossbar, post to tier 2 block below the rail centre
            bar(j1, k0);                         // diagonal, tier 1 block to back rail block
            for (s = seats) at(s[0], s[1]) block2d();
        }
        difference() {
            union() {
                ladder_slot(post_foot, foot_end);
                ladder_slot(post_foot, post_top);
                ladder_slot(post_top, top);
                ladder_slot(foot0, top);
                ladder_slot(cross_from, j2);
                ladder_slot(j1, k0);
            }
            for (s = seats) at(s[0], s[1]) offset(delta = strip) block2d();
            for (p = [foot0, cross_from, j1, j2, k0]) translate(p) circle(d = bar_w + 2 * strip);
        }
        for (s = seats) at(s[0], s[1]) offset(delta = rail_clr) rail2d();
    }
}

// the screw hole at a seat: clearance from the block's outer face to the rail base, then a pilot below.
// Horizontal in print, so a teardrop pointing +Z.
module screw_hole(c, o, z) {
    th = atan2(o[1], o[0]);
    translate([c[0], c[1], z]) rotate([0, 0, th]) rotate([0, 90, 0]) rotate([0, 0, 90]) {
        translate([0, 0, -e]) linear_extrude(7.5 + cover + 1) teardrop(clear_d);
        translate([0, 0, -pilot_depth]) linear_extrude(pilot_depth + e) teardrop(pilot_d);
    }
}

module bracket() {
    difference() {
        linear_extrude(bracket_t) profile();
        for (s = seats) screw_hole(s[0], s[1], bracket_t / 2);
    }
}

// one rail block, as on the face, thin: checks the slot fit and the screw before the bracket prints
module gauge() {
    difference() {
        linear_extrude(gauge_t) difference() { block2d(); offset(delta = rail_clr) rail2d(); }
        screw_hole([0, 0], [0, 1], gauge_t / 2);
    }
}

// ---- assembly view only ----
module ts35(len) rotate([90, 0, 0]) linear_extrude(len, center = true) rail2d();   // base on z = 0, along Y
module envelope(len, d = mod_d) translate([-mod_h / 2, -len / 2, 7.5]) cube([mod_h, len, d - 7.5]);

// place children at 2D point c, tilted so local +Z is the outward direction o; rail along Y
module at_seat(c, o) translate([c[0], 0, c[1]]) rotate([0, 90 - atan2(o[1], o[0]), 0]) children();

module assembly() {
    span = rail_len - 2 * 15;
    for (y = [-span / 2 + bracket_t, span / 2]) translate([0, y, 0]) rotate([90, 0, 0]) color("SteelBlue") bracket();
    for (i = [0 : 3]) at_seat(seats[i][0], seats[i][1]) {
        color("Silver") ts35(rail_len);
        color(i == 3 ? "Red" : "Orange", 0.35) envelope(span - 2 * bracket_t, i == 3 ? back_mod_d : mod_d);
    }
}

if (view == "assembly") assembly(); else if (view == "gauge") gauge(); else bracket();
