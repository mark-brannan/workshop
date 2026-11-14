// DIN-rail (TS35) mount for a 58 x 85 mm enclosed AC-DC supply: a flat back, the DIN clips printed apart and screwed on.
// A 2.5 mm solid plate the PSU's own size, screwed (M3) to its two diagonal holes, with cut-outs for the PSU's
// pill and a loose hole where its U slot mates. A lip 8 mm tall runs round all four sides of the PSU, square-cornered inside, rounded outside; it is a thin wall
// except on the lower (-Y) side, where a 33.5 mm stretch (8.5 mm from the left edge) is a 15 mm wide, 8 mm tall shelf with two chamfered zip-tie slot pairs through it:
// a cord (one AC, one DC) leaves the PSU straight down and lies on the shelf, held by a zip tie through a slot pair either side of it.
// Print flat back down (z = 0): the PSU sits on the plate's top face inside the lip, a pocket 8 mm deep.
// The DIN clips are separate parts: one or two of Maxstupo's "DIN Rail Clip (Heat Insert Version)" (Printables 420009, CC BY 4.0,
// ref_din_clip_heat_insert.stl, printed as part-din-clip.scad), each with two M3 heat inserts. Two countersunk M3 screws per clip
// go down through the plate from the PSU side into the inserts; the heads sit below the pocket floor, under the PSU.
// Three clip positions: one clip in the centre, or two spread wide. The PSU's own two screws are countersunk from
// the back, heads flush, so a clip can lie over them; mount the PSU first, then the clips.

/* [Plate] */
plate_l = 58;        // X, along the rail: the PSU's footprint (box, caliper), no overhang
plate_w = 85;        // Y, across the rail (the vertical, long side): the PSU's footprint
ext = 15;            // the lower (-Y) lip is this wide, measured from the PSU's edge: the strain-relief shelf
shelf_len = 33.5;    // the shelf runs this far along X; the rest of the lower edge is the thin lip
shelf_x = -plate_l/2 + 8.5;   // the shelf starts 8.5 mm in from the PSU's left edge (left in the top-down view)
plate_t = 2.5;       // the frame
corner_r = 3;       // outside corners of the lip
fillet_r = 4;        // where the shelf meets the thin lip, and the shelf's own outer corners

/* [Lip] the PSU sits in a pocket, the lip rises from the PSU (top) face of the plate */
lip_h = 8;           // lip height above the top face of the plate
lip_t = 2;           // lip wall thickness on the three thin sides, outside the PSU's own footprint

/* [PSU mounting features] (caliper ~; x right, y toward the back, centred on the footprint, left = left in normal view) */
hole_d = 3.5;        // M3, easy slip fit; the head bears on the rail side
slot_w = 3.4;        // the PSU's U slot and pill width (~)
holes = [[-23.2, -36.7], [-23.2, 29.8]];   // blind holes in the PSU underside: fit test 1 moved each 1 mm in X (to centre) and 1 mm in Y (toward each other)
top_hole = [-22.75, 38.7];  // loose M3 hole where the PSU's U slot mates (not a slot in the mount); fit test 1 moved it 0.75 mm toward the centre
pill = [25, -39];    // closed pill, 5.5 long tip to tip, long axis along Y (guess); fit test 1 moved it 1.5 mm to the outer edge (+X) and 1.5 mm down (-Y)
pill_len = 5.5;

/* [DIN clips] screwed to the back; the rail runs along X, its centre line on y = 0 */
clip_xs = [-20, 0, 20];      // three clip positions along the rail: one clip at 0, or two at -20 / 20
clip_ys = [22.05, -28.95];   // each clip's two insert holes, across the rail: its fixed hook up (+Y), spring latch down;
                             // its own model has them at x = 5 (hook) and 56, rail centre 27.05, so 51 apart
csk_d = 6.5;         // countersink top diameter: an ISO 10642 M3 head (6.0 nominal) sits a little below the face
csk_h = 1.6;         // countersink depth; the plate keeps 0.9 mm under it

/* [Zip-tie strain relief: slot pairs through the shelf and plate; the cable lies on top of the shelf, the tie loops under the back] */
tie_w = 5.5;         // slot length across the tie: takes ties up to 5 mm wide (standard), small ones too
tie_t = 2.2;         // slot width
tie_gap = 8;         // slot centre to slot centre, along X: the cord (~5-7 mm, guess) lies between them, running along Y
tie_c = 1.2;         // underside chamfer on each slot's outer edge, where the tie turns under the back
tie_ri = 2.5;        // roundover radius on each slot's inner (web-side) bottom edge: the tie pulls in and around it under the back
tie_off = 8;         // the two pairs sit this far either side of the shelf centre
tie_xs = [shelf_x + shelf_len/2 - tie_off, shelf_x + shelf_len/2 + tie_off];  // pair positions along X

/* [Hidden] */
$fn = 48;

tie_y = -plate_w/2 - ext/2;   // the slot pairs centre line, mid-shelf
// the pocket is the PSU's own square-cornered footprint; only the outside is rounded
module pocket() square([plate_l, plate_w], center = true);
// outer edge: lip_t round the PSU, rounded corners; on the lower side a shelf ext wide for shelf_len along X
module outline_raw() union() {
    offset(r = corner_r) square([plate_l + 2*lip_t - 2*corner_r, plate_w + 2*lip_t - 2*corner_r], center = true);
    translate([shelf_x, -plate_w/2 - ext]) square([shelf_len, ext + corner_r]);
}
// every outside corner rounded (convex), every inside corner where the shelf meets the thin lip filleted (concave)
module outline() offset(r = -fillet_r) offset(delta = fillet_r) offset(r = corner_r) offset(delta = -corner_r) outline_raw();

// the PSU's pill as a plate cut-out (closed slot); the top hole is a plain loose M3 hole
module slots2d() {
    translate(top_hole) circle(d = hole_d);
    hull() for (s = [-1, 1]) translate([pill[0], pill[1] + s*(pill_len - slot_w)/2]) circle(d = slot_w);
}

// A cord leaves the PSU's lower edge straight down (-Y) and lies on the shelf; each pair of slots straddles it, slot length
// along Y (across the tie), slot width along X. s = -1 / +1 is the left / right slot of a pair, its chamfer opening away
// from the web between them.
module tie_chamfers() {
    for (x = tie_xs, s = [-1, 1]) translate([x + s*tie_gap/2, tie_y]) hull() {
        translate([s*tie_c/2, 0, -0.5]) linear_extrude(0.5) square([tie_t + tie_c, tie_w], center = true);
        translate([0, 0, tie_c]) linear_extrude(0.01) square([tie_t, tie_w], center = true);
    }
}

// roundover on the web-side bottom edge of each slot, so the tie bends round a curve, not a sharp corner
module tie_roundovers() {
    for (x = tie_xs, s = [-1, 1]) translate([x + s*tie_gap/2 - s*tie_t/2, tie_y, 0]) rotate([90, 0, 0])
        linear_extrude(tie_w, center = true) scale([-s, 1]) difference() {
            translate([-0.01, -0.5]) square([tie_ri + 0.01, tie_ri + 0.5]);
            translate([tie_ri, tie_ri]) circle(r = tie_ri);
        }
}

// whole-height cuts (they pass through the shelf and the plate); z = 0 is the flat back
module tie_slots() { for (x = tie_xs, s = [-1, 1]) translate([x + s*tie_gap/2, tie_y, -1]) linear_extrude(lip_h + plate_t + 2) square([tie_t, tie_w], center = true); }

// M3 through-hole with a 90 degree countersink opening into the pocket (up) or onto the back (down)
module csk_hole(up) {
    translate([0, 0, -1]) cylinder(d = hole_d, h = plate_t + 2);
    if (up) translate([0, 0, plate_t - csk_h]) cylinder(d1 = csk_d - 2*csk_h, d2 = csk_d + 2, h = csk_h + 1);
    else translate([0, 0, -1]) cylinder(d1 = csk_d + 2, d2 = csk_d - 2*csk_h, h = csk_h + 1);
}

module mount() {
    difference() {
        union() {
            linear_extrude(plate_t) difference() {                                   // the flat back, z = 0 is the rail side
                outline();
                slots2d();
            }
            translate([0, 0, plate_t - 0.01]) linear_extrude(lip_h + 0.01) difference() { outline(); pocket(); }   // the lip, rising from the PSU side
        }
        for (x = clip_xs, y = clip_ys) translate([x, y, 0]) csk_hole(up = true);   // clip screws, heads under the PSU
        for (h = holes) translate(h) csk_hole(up = false);                       // PSU screws, heads flush with the back: a clip may sit over them
        tie_slots();
        tie_chamfers();
        tie_roundovers();
    }
}

mount();
