// DIN-rail (TS35) mount for an 80 x 110 mm enclosed AC-DC supply, one piece.
// A 2.5 mm lightened frame, the PSU's own footprint, screws (M3) to its two diagonal holes.
// Two DIN clips are part of the frame: the profile of marauder156's "DIN rail clip basic module
// for own modification" (Thingiverse thing:3640994, DINrail_Clip.stl), a fixed hook on one side and a
// spring-arm latch on the other, extruded along the rail and standing on the frame. The rail runs
// along X, the 80 mm axis; the 110 mm side stands up and down.
// Print with the PSU face down (z = 0). No supports are planned for the barbs; check the slicer preview.

/* [Plate] */
plate_l = 80;        // X, along the rail: the PSU's footprint, no overhang
plate_w = 110;       // Y, across the rail (the vertical, long side)
plate_t = 2.5;       // the frame
corner_r = 3;
rim_w = 6;           // perimeter band of the lightened frame
boss_d = 11;         // solid round around each screw hole

/* [PSU mounting holes] (caliper ~, diagonal pair) */
hole_dx = 47;        // centre to centre along X (the 80 mm side)
hole_dy = 75;        // centre to centre along Y (the 110 mm side)
hole_d = 3.5;        // M3, easy slip fit; the head bears on the rail side

/* [Clips] */
clip_len = 15;       // each clip's length along the rail; the original STL is 12.3
clip_x = 25;         // clip centre distance from the plate centre, along the rail
strip_pad = 3;       // solid frame band beyond each clip's length, each side

/* [Hidden] */
$fn = 48;
// Clip profile from DINrail_Clip.stl, a section at mid-length, mm. Back face (on the frame) is y = 10;
// y falls away from the frame. The rail centre line is x = 0.5. Two voids free the spring arm and
// the fixed hook's relief; the outline is simplified within 0.03 mm.
clip_outer = [[-30,10],[30,10],[30,3],[29.91,2.51],[29.7,2.06],[29.39,1.68],[29,1.38],[21.55,-2.86],[21.21,-2.96],[20.85,-2.99],[18,-2.99],[15.35,-2.47],[15.35,-1.74],[18,-1.19],[18,-0],[14.34,-0],[13.89,0.05],[13.47,0.19],[13.09,0.43],[12.77,0.75],[12.54,1.13],[12.39,1.55],[12.34,2],[12.34,4.1],[12.31,4.34],[12.21,4.57],[12.07,4.77],[11.88,4.93],[11.66,5.04],[11.42,5.09],[11.17,5.08],[10.94,5.01],[10.72,4.88],[10.55,4.71],[10.42,4.5],[10.35,4.26],[10.34,4.01],[12,-1],[11.98,-5.24],[11.9,-5.45],[11.71,-5.71],[11.44,-5.91],[11.23,-5.99],[8.94,-6.01],[8.73,-5.98],[8.34,-5.78],[8.19,-5.62],[8.01,-5.23],[7.98,-1.01],[7.14,2.78],[6.89,3.37],[6.71,3.64],[6.53,3.9],[6.06,4.33],[5.51,4.66],[4.9,4.86],[4.26,4.93],[-4.18,4.93],[-4.84,4.86],[-5.47,4.64],[-6.03,4.29],[-6.5,3.83],[-6.86,3.27],[-7.09,2.65],[-8,-1],[-8,-5.04],[-8.11,-5.46],[-8.38,-5.8],[-8.78,-5.99],[-11.05,-6.01],[-11.27,-5.98],[-11.66,-5.78],[-11.82,-5.63],[-12,-5.23],[-12.03,-1.03],[-10.79,3.5],[-10.75,3.85],[-10.82,4.19],[-11.09,4.56],[-11.51,4.77],[-14,4.8],[-14.46,4.91],[-14.82,5.22],[-14.94,5.43],[-15,5.66],[-15.01,6.15],[-15.08,6.39],[-15.2,6.61],[-15.37,6.79],[-15.59,6.92],[-15.82,6.99],[-16.07,7.01],[-16.32,6.96],[-16.54,6.85],[-16.73,6.69],[-16.88,6.49],[-16.97,6.26],[-17,0],[-18,0],[-18,-1],[-17,-1.28],[-17,-2.27],[-18.03,-5.18],[-18.35,-5.5],[-18.73,-5.75],[-18.94,-5.83],[-19.16,-5.9],[-19.62,-5.96],[-24.21,-5.94],[-28.86,-4.68],[-29.25,-4.48],[-29.41,-4.34],[-29.57,-4.19],[-29.82,-3.84],[-29.97,-3.43],[-30.03,-3],[-30.03,-1],[-28.43,-1],[-28.41,-2.57],[-28.32,-2.76],[-28.16,-2.9],[-26.84,-3.24],[-26.54,-3.11],[-26.41,-2.93],[-26.37,-2.72],[-28.59,5.34],[-28.72,5.62],[-28.92,5.85],[-29.65,6.24],[-29.91,6.58],[-29.98,6.79]];
clip_void1 = [[28.54,3.18],[28.54,4.8],[13.54,4.8],[13.54,2],[13.56,1.81],[13.72,1.49],[14.01,1.26],[14.37,1.2],[19.2,1.2],[19.2,-1.79],[20.79,-1.79],[21.08,-1.74],[21.34,-1.63],[28.15,2.5],[28.43,2.8]];
clip_void2 = [[-23.17,-2.89],[-25.52,5.47],[-25.84,5.82],[-26.06,5.92],[-26.53,5.97],[-26.98,5.79],[-27.28,5.42],[-27.37,5.07],[-27.35,4.72],[-24.95,-4.22],[-24.76,-4.6],[-24.42,-4.86],[-24,-4.96],[-19.42,-4.93],[-19.03,-4.75],[-18.75,-4.41],[-18,-2.04],[-19,-1.77],[-19,0.99],[-18,0.99],[-18,5.99],[-18.1,6.42],[-18.38,6.77],[-18.57,6.89],[-19,6.99],[-19.5,6.99],[-19.93,6.89],[-20.28,6.62],[-20.47,6.22],[-20.5,-2.46],[-20.6,-2.88],[-20.87,-3.23],[-21.26,-3.43],[-22.49,-3.43],[-22.89,-3.24],[-23.05,-3.08]];

rail_cx = 0.5;
clip_h = 10 + 6.012;   // back face to the lowest hook, y = 10 .. -6.012
strip_w = clip_len + 2*strip_pad;
holes = [[-hole_dx/2, -hole_dy/2], [hole_dx/2, hole_dy/2]];

// Clip profile (x across the rail, y toward the rail) laid into plate axes: Y across, Z up from the frame,
// extruded along X, centred on x = 0. The back face (profile y = 10) sits on the frame, 0.01 into it.
module clip() {
    multmatrix([[0, 0, 1, -clip_len/2], [1, 0, 0, -rail_cx], [0, -1, 0, plate_t + 10 - 0.01], [0, 0, 0, 1]])
        linear_extrude(clip_len) difference() { polygon(clip_outer); polygon(clip_void1); polygon(clip_void2); }
}

module outline() offset(r = corner_r) square([plate_l - 2*corner_r, plate_w - 2*corner_r], center = true);

// Perimeter rim, a solid band under each clip out to the side rim, a boss round each screw hole; the rest is open.
module frame2d() intersection() { outline(); union() {
    difference() { outline(); offset(delta = -rim_w) outline(); }
    for (sx = [-1, 1]) translate([sx*clip_x - strip_w/2, -plate_w/2]) square([strip_w, plate_w]);
    for (h = holes) translate(h) circle(d = boss_d);
} }

module base() {
    difference() {
        linear_extrude(plate_t) frame2d();
        for (h = holes) translate([h[0], h[1], -1]) cylinder(d = hole_d, h = plate_t + 2);
    }
}

module mount() {
    base();
    for (sx = [-1, 1]) translate([sx*clip_x, 0, 0]) clip();
}

mount();
