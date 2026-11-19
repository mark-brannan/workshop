// Bridge gauge, hand-written (shop gauge only slices flat, so it cannot test a ceiling). Prints as shown, plate down.
// Just the VEML bridge end of the tray: plate, legs, slab, lip. Measure the sag of the slab's underside against 34.9 mm.
include <model.scad>
view = "gauge";
if (view == "gauge") translate([0, -reach, -tray_bot])
  intersection() { tray(); translate([-30, plinth_y0 - 4, tray_bot - 1]) cube([60, plinth + 8, 40]); }
