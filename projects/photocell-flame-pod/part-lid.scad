// Lid for the lidded build (potted = false): 3 mm clear acrylic, laser cut from the DXF.
// parts: lid
include <model.scad>
part = "none";
mode = "2d";   // [2d:laser profile, 3d:extruded for the render]

if (mode == "2d") lid_2d(); else linear_extrude(lid_t) lid_2d();
