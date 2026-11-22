// Fit-check gauge, generated: shop gauge projects/halpi2-endpoint-box "box()" 1 6
// Two horizontal slices of the finished part, re-extruded thin. Rerun the command to change it;
// a hand-written gauge replaces this file and drops this first line.
use <model.scad>

/* [Gauge] */
z_plate = 1;   // slice height through the plate: its outline and through-holes
z_wall = 6;    // slice height through the walls the object sits against; below 0 for none
gauge_t = 1;       // gauge plate thickness
gauge_rise = 2;    // gauge wall height above the plate

module gauge_slice() {
    linear_extrude(gauge_t) projection(cut = true) translate([0, 0, -z_plate]) children();
    if (z_wall >= 0) translate([0, 0, gauge_t - 0.01]) linear_extrude(gauge_rise + 0.01) projection(cut = true) translate([0, 0, -z_wall]) children();
}

gauge_slice() box();
