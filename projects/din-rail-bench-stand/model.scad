// DIN-rail bench stand: one end bracket of a pair, holding four TS35 rails.
// parts: bench-stand-bracket
// Two rails cross the sloped front face, one above the other; the third lies flat on the foot, in front of them;
// the fourth lies flat inside the frame at the back, under the face, for AC gear: a small PSU, terminals, relays.
//
// After Szmalu's "DIN Rail Stand KIT" (Thingiverse 3609072, CC BY-NC; its top, above the crossbar, is cut from its mesh and used as is: szmalu_top.scad).
// Every rail is held as the original holds its top rail, by that holder lifted from the original's outline: two hooks
// round the lips, the channel open between, no screw. The bars are the original's: a solid 3 mm post, face, crossbar
// and diagonal, and a ladder foot, two 3 mm strips with a slot between. Face rails are set into the face as the
// original's; a diagonal from just below the lower rail's centre to the back rail's holder makes a triangle with the face and foot.
//
// The profile is drawn in 2D with x toward the front of the desk and y up, then extruded bracket_t:
// print flat, as modelled; view="assembly" stands two brackets up with rails and module envelopes;
// view="gauge" is one rail holder, thin, to check the rail's fit before the bracket prints.

include <szmalu_top.scad>   // the original's top, used as is

/* [View] */
view = "part";            // "part" (print), "assembly" or "gauge"

/* [Frame] */
a = 60;                   // sloped face, degrees above the desk; modules lean back 90 - a
bar_w = 10;               // width of the foot, a ladder as the original's: two 3 strips, a 4 slot
strip = 3;                // each of a ladder bar's two strips; the slot between is bar_w - 2 strip
rung_pitch = 70;          // a rung across the ladder slot at least this often
bracket_t = 20;           // thickness of the plate (print height), across the rail
strut = 3;                // back post, face, crossbar and diagonal: solid, 3 wide in the profile, as the original's

/* [Rails] */
s1 = 106.5;                  // tier 1 rail centre, along the face from its foot
pitch = 70;              // tier 2 sits this far above tier 1, along the face
flat_x = 108.5;             // flat rail centre, from the back of the stand
back_x = 21.5;              // back (AC) rail centre: its block flush with the post's back, never behind it

/* [Rail holder] the original's, lifted from its top rail: two hooks round the lips, the channel open between */
rail_clr = 0.3;           // our slot cut each side of the 1 mm rail sheet, inside the original's own
block_wall = 4;           // holder beyond each rail lip
cover = 3;                // holder over the rail's lips, outward
holder_under = 6;         // holder below the rail's base

/* [Module envelope, for the assembly view and the clearance test] */
mod_h = 60;               // module height, across the rail (guess: the small boards planned, not 90 standard DIN gear)
mod_d = 45;               // module depth out from the rail base (guess: buck/boost boards, meters)
back_mod_d = 55;          // the back rail's modules: a small DIN PSU (~55 deep, from memory), terminals, relays (guess)
rail_len = 300;           // rail length in the assembly view

/* [Gauge] */
gauge_t = 10;             // gauge print height

/* [Hidden] */
$fn = 48;
e = 0.01;
u = [-cos(a), sin(a)];            // up the face
n = [sin(a), cos(a)];             // out of the face (toward the user)
top_in = 9;                                         // the face's outer line meets the flat top this far forward of the post's back, as the original
rail_top = 25;                                      // top rail centre, this far down the face from that corner, as the original
face_len = s1 + pitch + rail_top;
foot0 = [top_in - (strut / 2) * sin(a) + face_len * cos(a), bar_w / 2];   // face centreline at its foot
top = foot0 + face_len * u;                           // the corner: face meets the post
foot_len = flat_x + mod_h / 2 + 10;
foot_x0 = min(bar_w / 2, back_x - 17.5 - block_wall + bar_w / 2);   // foot runs back under the back rail's block
top_y = top[1] + (strut / 2) * cos(a);              // flat top: post, top block and face flush, as the original
post_top = [strut / 2, top_y - strut / 2];
post_foot = [strut / 2, bar_w / 2];
foot_end = [foot_len, bar_w / 2];

function edge(s) = foot0 + s * u + (strut / 2 - 7.5 - cover) * n;  // rail base, set into the face so the block's outer side is flush with it, as the original

// rail seats: base point and outward direction
seats = [[edge(s1), n], [edge(s1 + pitch), n], [[flat_x, bar_w], [0, 1]], [[back_x, bar_w], [0, 1]]];
own = [seats[0], seats[2], seats[3]];             // seats with our own block; the top rail is held by the original's top
function local(c, o, x, y) = c + x * [o[1], -o[0]] + y * o;
below = 8;                                          // braces meet a block this far below the rail's centre line
cross_y = local(edge(s1 + pitch), n, 17.5 + block_wall, -bar_w)[1] - strut / 2;   // crossbar's top meets the top block's bottom, as the original
function face_x(y) = foot0[0] - (y - foot0[1]) / tan(a);
j1 = local(edge(s1), n, below, -bar_w / 2);          // diagonal meets the tier 1 block, inside
k0 = [back_x + 17.5 + block_wall - bar_w / 2, bar_w + 7.5 + cover - bar_w / 2];   // back rail block, upper front corner

module bar(p, q, w = bar_w) hull() { translate(p) circle(d = w); translate(q) circle(d = w); }

// local frame at a seat: +y out of the rail (toward the module), +x across the rail's width
module at(c, o) translate(c) rotate(atan2(o[1], o[0]) - 90) children();

module rail2d() polygon([[-17.5, 7.5], [-17.5, 6.5], [-12.5, 6.5], [-12.5, 0], [12.5, 0], [12.5, 6.5], [17.5, 6.5],
                         [17.5, 7.5], [11.5, 7.5], [11.5, 1], [-11.5, 1], [-11.5, 7.5]]);
// the original's holder round its top rail, in that rail's local frame (seats[1] is where the original's top holds it)
module block2d() intersection() {
    translate([-17.5 - block_wall, -holder_under]) square([35 + 2 * block_wall, holder_under + 7.5 + cover]);
    rotate(90 - atan2(n[1], n[0])) translate(-(edge(s1 + pitch) - [0, top_y])) szmalu_top();
}

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
            bar([foot_x0, bar_w / 2], foot_end);   // foot, on the desk, flush with the back of the post
            bar(post_foot, post_top, strut);     // back post
            bar(foot0, top, strut);              // sloped face
            bar(j1, k0, strut);                  // diagonal, tier 1 holder to back rail holder
            for (s = own) at(s[0], s[1]) block2d();
        }
        difference() {
            union() {
                ladder_slot([back_x + 17.5 + block_wall + strip - bar_w + 2, bar_w / 2],   // one plain slot, back holder to flat holder
                            [flat_x - 17.5 - block_wall - strip + bar_w - 2, bar_w / 2]);
            }
            for (s = own) at(s[0], s[1]) offset(delta = strip) block2d();
            for (p = [foot0, post_foot, k0]) translate(p) circle(d = bar_w + 2 * strip);
        }
        for (s = own) at(s[0], s[1]) offset(delta = rail_clr) rail2d();
    }
}

module bracket() linear_extrude(bracket_t) union() {
    intersection() { profile(); translate([-1000, 0]) square([2000, top_y - szmalu_top_cut + 0.5]); }   // ours, below the original's top
    translate([0, top_y]) szmalu_top();
}

// one rail holder, thin: checks the rail's fit before the bracket prints
module gauge() linear_extrude(gauge_t) difference() {
    union() { block2d(); translate([-17.5 - block_wall, -holder_under]) square([35 + 2 * block_wall, strut]); }   // a strut joins the hooks, as the face does
    offset(delta = rail_clr) rail2d();
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
