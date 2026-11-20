// Lid, 3 mm: clear acrylic cut from the DXF, or print the 3MF flat. Drops into the tray's rebate, flush with the wall tops.
include <model.scad>
part = "none";
mode = "2d";   // [2d:laser profile, 3d:extruded for the print]

if (mode == "2d") lid_2d(); else linear_extrude(lid_t) lid_2d();
