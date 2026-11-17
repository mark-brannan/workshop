// Fit-check gauge, hand-written: the screen's body without its slats and roof.
// It proves the pegs in the board's holes, the cable in its notch and an M3 self-tapper in a pilot hole,
// and its back plate is the drill template for the two bulkhead screws.
include <model.scad>
part = "gauge";

intersection() {
    body();
    union() {
        translate([-out_w, y_lo - 1, -1]) cube([2*out_w, y_hi - y_lo + 2, plate_t + 1]);                    // back plate, mount holes
        translate([-out_w, y_lo - 1, -1]) cube([2*out_w, louv_run - bite + 0.99, body_h + 2]);              // floor, notch, two posts with pilots
        for (s = seats) translate([s[0], s[1], -1]) cylinder(d = pad_d + 1, h = body_h + 2);                // pads and pegs
    }
}
