// K2 Plus tolerance print, ASA. One build plate, three kinds of body:
//   hole plate - 31 through holes 3.0..6.0 mm in 0.1 steps, a 10.0 mm slot;
//   gauge bar  - 10.0 mm wide, the slot's outer-edge twin;
//   peg tabs   - one standing peg per nominal size, on its own labelled tab.
// Every hole and peg is labelled with its modelled diameter. Plain OpenSCAD.

/* [Range] */
d_min = 3.0;
d_max = 6.0;
d_step = 0.1;

/* [Hole plate] */
plate_t = 5;
cols = 8;
pitch_x = 10;       // hole centre to centre
pitch_y = 13;       // row to row, room for the label under each hole
edge = 2;           // plate edge beyond the outer cells
slot_w = 10;        // modelled width; the gauge bar is the same
slot_l = 40;
slot_band = 18;     // strip under the holes that carries the slot

/* [Pegs] */
peg_h = 8;
peg_chamfer = 0.4;  // lead-in on the peg top
tab = [9, 13, 2];   // x, y, thickness
tab_gap = 2;

/* [Labels] */
label_size = 2.5;
label_depth = 0.6;

/* [Hidden] */
$fn = 128;          // 0.001 mm chord error on a 6 mm hole
n = round((d_max - d_min) / d_step) + 1;
rows = ceil(n / cols);
plate = [cols * pitch_x + 2 * edge, rows * pitch_y + slot_band + 2 * edge];
gap = 5;            // between bodies on the build plate

function dia(i) = (round(d_min * 10) + i) / 10;
function label(d) = str(floor(d), ".", round(d * 10) % 10);

module deboss(s, size = label_size) {
    linear_extrude(label_depth + 0.01)
        text(s, size = size, halign = "center", valign = "top", font = "Liberation Sans:style=Bold");
}

function hole_xy(i) = [edge + (i % cols + 0.5) * pitch_x,
                       plate.y - edge - (floor(i / cols) + 0.4) * pitch_y];

module hole_plate() {
    difference() {
        cube([plate.x, plate.y, plate_t]);
        for (i = [0 : n - 1]) {
            translate([each hole_xy(i), -1]) cylinder(d = dia(i), h = plate_t + 2);
            translate([each hole_xy(i) - [0, d_max / 2 + 0.6], plate_t - label_depth]) deboss(label(dia(i)));
        }
        translate([plate.x / 2 - slot_l / 2, edge + slot_band / 2 - slot_w / 2 + 2, -1])
            cube([slot_l, slot_w, plate_t + 2]);
        translate([plate.x / 2, edge + 4, plate_t - label_depth]) deboss(label(slot_w), 2.2);
    }
}

module gauge_bar() {
    difference() {
        cube([slot_l, slot_w, plate_t]);
        translate([slot_l / 2, slot_w / 2 + label_size / 2, plate_t - label_depth]) deboss(label(slot_w));
    }
}

module peg_tab(d) {
    difference() {
        cube(tab);
        translate([tab.x / 2, tab.y - 8.2, tab.z - label_depth]) deboss(label(d));
    }
    translate([tab.x / 2, tab.y - d_max / 2 - 1, tab.z]) {
        cylinder(d = d, h = peg_h - peg_chamfer);
        translate([0, 0, peg_h - peg_chamfer]) cylinder(d1 = d, d2 = d - 2 * peg_chamfer, h = peg_chamfer);
    }
}

hole_plate();
translate([(plate.x - slot_l) / 2, -gap - slot_w, 0]) gauge_bar();
translate([plate.x + gap, 0, 0])
    for (i = [0 : n - 1])
        translate([(i % cols) * (tab.x + tab_gap), plate.y - tab.y - floor(i / cols) * (tab.y + tab_gap), 0])
            peg_tab(dia(i));
