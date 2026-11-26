// Print plate: three shells and three covers in one PETG job, in print orientation (a turn and a shift each, no mirror).
// Plate origin is the bed centre, +Y the back. Bodies run down the middle; covers sit away from the centre
// on the left (front and back) and the front right. The back right stays empty.
include <model.scad>
part = "none";

pitch = 26;   // row spacing, front to back: a shell is ~17.8 wide, a cover ~20.6
cover_x = 80; // cover column centres, left (-) and right (+) of the bodies

module shell_at(y) translate([-in_l/2, y, 0]) shell();
module cover_at(x, y) translate([x, y, 0]) translate([-in_l/2, 0, 0]) rotate([180, 0, 0]) translate([0, 0, -(shell_h + cover_t)]) cover();

for (y = [-pitch, 0, pitch]) shell_at(y);
cover_at(-cover_x,  pitch);   // left back
cover_at(-cover_x, -pitch);   // left front
cover_at( cover_x, -pitch);   // front right
