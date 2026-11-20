// Shower-sump platform: a flat deck the sump sits on, carried by V-shaped frames that sit in the
// hull's V down in the bilge, forward of amidships. Bilge water runs under the deck and through a
// notch at the keel in each frame.
// Installed axes: X across the boat, Y fore-aft (+Y toward the bow), Z up; z = 0 at the aft keel.
// Print: deck on the bed (part = "print", the default). The frames stand up off it, so nothing overhangs.

part = "print";      // [print, installed]

/* [Sump: footprint on the deck (unmeasured)] */
sump_w = 180;        // across the boat
sump_l = 280;        // fore-aft
margin = 5;          // deck beyond the sump, each side

/* [Hull V (unmeasured)] */
deadrise_aft = 25;   // degrees above horizontal, each side, at the aft frame
deadrise_fwd = 25;   // same at the forward frame; the V gets steeper toward the bow
keel_rise = 0;       // degrees the keel line climbs toward the bow over the platform's length
keel_w = 30;         // flat at the bottom of each frame, where the keel or a hull flat meets it

/* [Build] */
deck_t = 3;
frames = 5;          // evenly spaced, the end ones flush with the deck's ends
frame_t = 4;         // along Y
limber_w = 20;       // water notch at the keel
limber_h = 8;
side = 3;            // square edge outboard of each frame, so the V never ends in a knife edge

W = sump_w + 2 * margin;
L = sump_l + 2 * margin;
e = 0.01;

function lerp(a, b, t) = a + (b - a) * t;
function y_at(i) = -L / 2 + frame_t / 2 + i * (L - frame_t) / (frames - 1);
function t_at(i) = i / (frames - 1);
function keel_z(y) = (y + L / 2) * tan(keel_rise);
function rise(a) = (W / 2 - keel_w / 2) * tan(a);
// deck underside is level, just above the highest frame's outboard top
z_deck = side + max([for (i = [0 : frames - 1]) keel_z(y_at(i)) + rise(lerp(deadrise_aft, deadrise_fwd, t_at(i)))]);
H = z_deck + deck_t;

module frame(i) {
  y = y_at(i);
  a = lerp(deadrise_aft, deadrise_fwd, t_at(i));
  z0 = keel_z(y);
  translate([0, y + frame_t / 2, 0]) rotate([90, 0, 0]) linear_extrude(frame_t)
    difference() {
      polygon([[-keel_w / 2, z0], [keel_w / 2, z0], [W / 2, z0 + rise(a)], [W / 2, z_deck + deck_t / 2],
               [-W / 2, z_deck + deck_t / 2], [-W / 2, z0 + rise(a)]]);
      translate([-limber_w / 2, z0 - e]) square([limber_w, limber_h + e]);
    }
}

module platform() {
  translate([-W / 2, -L / 2, z_deck]) cube([W, L, deck_t]);
  for (i = [0 : frames - 1]) frame(i);
}

if (part == "installed") platform();
else translate([0, 0, H]) rotate([180, 0, 0]) platform();
