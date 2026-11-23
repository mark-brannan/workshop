// DIN-rail bench stand: one end bracket of a pair, holding four TS35 rails.
// Two rails cross the sloped front face, one above the other; the third lies flat on the foot, in front of them;
// the fourth lies flat inside the frame at the back, under the face, for AC gear: a small PSU, terminals, relays.
// A rail spans between two brackets and is held at each by one M4 screw through a slot in its base, into a pilot
// hole in a pad on the bracket's edge (the scheme of Szmalu's "DIN Rail Stand KIT", Thingiverse 3609072; nothing of its mesh is used).
//
// The profile is drawn in 2D with x toward the front of the desk and y up, then extruded bracket_t:
// print flat, as modelled; view="assembly" stands two brackets up with rails and module envelopes.

/* [View] */
view = "part";            // "part" (print) or "assembly"

/* [Frame] */
a = 60;                   // sloped face, degrees above the desk; modules lean back 90 - a
bar_w = 10;               // width of every bar in the profile
bracket_t = 10;           // thickness of the plate (print height), across the rail

/* [Rails] */
s1 = 70;                  // tier 1 rail centre, along the face from its foot
pitch = 125;              // tier 2 sits this far above tier 1, along the face
face_over = 15;           // face runs this far past the top module's envelope
flat_x = 280;             // flat rail centre, from the back of the stand
flat_pad = 20;            // seat height above the desk, both flat rails
back_x = 60;              // back (AC) rail centre, from the back of the stand
face_shift = 35;          // face starts this far forward of the back post, to make room for the back rail

/* [Fixing] M4 self-tapping screw through the rail base slot */
pilot_d = 3.7;            // guess; printed holes run small, gauge before trusting it
pilot_depth = 18;         // takes an M4 x 16 through the 1 mm rail base with 3 mm spare
pad_len = 30;             // seat pad along the edge
pad_boss = 22;            // seat pad depth behind the edge, around the pilot hole

/* [Module envelope, for the assembly view and the clearance test] */
mod_h = 90;               // DIN module height, across the rail (standard 90)
mod_d = 70;               // module depth out from the rail face (guess: PSU 55-60, meters ~65)
back_mod_d = 65;          // the back rail's modules: small PSU, terminals, relays (guess)
rail_len = 300;           // rail length in the assembly view

/* [Hidden] */
$fn = 48;
e = 0.01;
u = [-cos(a), sin(a)];            // up the face
n = [sin(a), cos(a)];             // out of the face (toward the user)
face_len = s1 + pitch + mod_h / 2 + face_over;
foot0 = [bar_w / 2 + face_shift + face_len * cos(a), bar_w / 2];   // face centreline at its foot
top = foot0 + face_len * u;                           // joined back to the post by a top bar
foot_len = flat_x + mod_h / 2 + 10;

function edge(s) = foot0 + s * u + (bar_w / 2) * n;  // point on the face's outer edge

module bar(p, q) hull() { translate(p) circle(d = bar_w); translate(q) circle(d = bar_w); }
module teardrop(d) hull() { circle(d = d); rotate(45) square(d / 2); }   // point +Y (print up after rotation)

module face_seat(s) {
    c = edge(s);
    hull() for (k = [-1, 1]) {
        translate(c - (bar_w / 2) * n + k * pad_len / 2 * u) circle(d = bar_w);
        translate(c - pad_boss * n + k * pad_len / 4 * u) circle(d = bar_w);
    }
}

module profile() {
    bar([bar_w / 2, bar_w / 2], [foot_len, bar_w / 2]);    // foot, on the desk
    bar([bar_w / 2, bar_w / 2], [bar_w / 2, top[1]]);      // back post
    bar([bar_w / 2, top[1]], top);                         // top bar, post to face
    bar(foot0, top);                                       // sloped face
    bar([bar_w / 2, edge(s1 + pitch)[1] - pad_boss * n[1]], edge(s1 + pitch) - pad_boss * n);   // strut, back post to tier 2 pad
    face_seat(s1);
    face_seat(s1 + pitch);
    flat_seat(flat_x);
    flat_seat(back_x);
}

module flat_seat(x) hull() {                               // a flat rail's raised seat on the foot
    translate([x - pad_len / 2, 0]) square([pad_len, bar_w]);
    for (k = [-1, 1]) translate([x + k * (pad_len / 2 - bar_w / 2), flat_pad - bar_w / 2]) circle(d = bar_w);
}

// a pilot hole into the plate's edge at 2D point c, running in along -dir; teardrop point is print-up (+Z)
module pilot(c, dir) {
    th = atan2(dir[1], dir[0]);
    translate([c[0], c[1], bracket_t / 2]) rotate([0, 0, th]) rotate([0, -90, 0])
        translate([0, 0, -e]) linear_extrude(pilot_depth + e) rotate(-90) teardrop(pilot_d);
}

module bracket() {
    difference() {
        linear_extrude(bracket_t) profile();
        pilot(edge(s1), n);
        pilot(edge(s1 + pitch), n);
        pilot([flat_x, flat_pad], [0, 1]);
        pilot([back_x, flat_pad], [0, 1]);
    }
}

// ---- assembly view only ----
module ts35(len) {   // top-hat rail, 35 x 7.5, base on z = 0, along Y
    rotate([90, 0, 0]) linear_extrude(len, center = true)
        polygon([[-17.5, 7.5], [-17.5, 6.5], [-12.5, 6.5], [-12.5, 0], [12.5, 0], [12.5, 6.5], [17.5, 6.5], [17.5, 7.5],
                 [11.5, 7.5], [11.5, 1], [-11.5, 1], [-11.5, 7.5]]);
}
module envelope(len, d = mod_d) translate([-mod_h / 2, -len / 2, 7.5]) cube([mod_h, len, d - 7.5]);

// place children at 2D edge point c, tilted ang about Y so local +Z is the edge's outward normal; rail along Y
module at_seat(c, ang) translate([c[0], 0, c[1]]) rotate([0, ang, 0]) children();

module assembly() {
    span = rail_len - 2 * 15;
    for (y = [-span / 2, span / 2 + bracket_t]) translate([0, y, 0]) rotate([90, 0, 0]) color("SteelBlue") bracket();
    for (s = [s1, s1 + pitch]) at_seat(edge(s), a) {
        color("Silver") ts35(rail_len);
        color("Orange", 0.35) envelope(rail_len - 60);
    }
    at_seat([flat_x, flat_pad], 0) {
        color("Silver") ts35(rail_len);
        color("Orange", 0.35) envelope(rail_len - 60);
    }
    at_seat([back_x, flat_pad], 0) {
        color("Silver") ts35(rail_len);
        color("Red", 0.35) envelope(rail_len - 60, back_mod_d);
    }
}

if (view == "assembly") assembly(); else bracket();
