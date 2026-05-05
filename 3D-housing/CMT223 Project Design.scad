// FocusFlow Enclosure
// Got the exact dimensions off seedwiki so everything should snap in

w = 160;
d = 160;
h = 320;
pi_cover_h = 35; 
wall = 3;
tol = 0.5; // gap tolerance because the printer over-extrudes a bit

// component sizes
ribbon_w = 30;
ribbon_d = 4;
cam_w = 25;
cam_h = 24;
lcd_w = 72;
lcd_h = 25;
oled_w = 27;
oled_h = 20;
btn_r = 6;
us_r = 8;
us_spacing = 25.5;
pir_r = 12;
small_sensor_r = 5;
dht_w = 13;
dht_h = 16;
cable_hole_r = 15;

$fn = 60;

module main_body() {
    difference() {
        cube([w, d, h], center=true);
        cube([w - (wall*2), d - (wall*2), h - (wall*2)], center=true);
        
        // back panel opening
        translate([0, d/2, 0]) 
            cube([w - (wall*4), wall*4, h - (wall*4)], center=true);
            
        // top slit for the pi cam ribbon
        translate([0, -(d/2) + 20, h/2]) 
            cube([ribbon_w, ribbon_d, wall*4], center=true);
            
        // peg holes for the pi lid
        translate([(w/2)-10, (d/2)-10, h/2]) cylinder(h=wall*4, r=2.5, center=true);
        translate([-(w/2)+10, (d/2)-10, h/2]) cylinder(h=wall*4, r=2.5, center=true);
        translate([(w/2)-10, -(d/2)+10, h/2]) cylinder(h=wall*4, r=2.5, center=true);
        translate([-(w/2)+10, -(d/2)+10, h/2]) cylinder(h=wall*4, r=2.5, center=true);
            
        // cutting out the front face
        translate([0, -(d/2), 120]) cube([cam_w, wall*4, cam_h], center=true);
        translate([0, -(d/2), 65]) cube([lcd_w, wall*4, lcd_h], center=true);
        translate([0, -(d/2), 5]) cube([oled_w, wall*4, oled_h], center=true);
            
        translate([-35, -(d/2), -30]) rotate([90, 0, 0]) cylinder(h=wall*4, r=btn_r, center=true);
        translate([35, -(d/2), -30]) rotate([90, 0, 0]) cylinder(h=wall*4, r=btn_r, center=true);
            
        // ultrasonic eyes
        translate([-(us_spacing/2), -(d/2), -75]) rotate([90, 0, 0]) cylinder(h=wall*4, r=us_r, center=true);
        translate([(us_spacing/2), -(d/2), -75]) rotate([90, 0, 0]) cylinder(h=wall*4, r=us_r, center=true);
            
        // bottom row sensors
        translate([-40, -(d/2), -115]) rotate([90, 0, 0]) cylinder(h=wall*4, r=small_sensor_r, center=true);
        translate([0, -(d/2), -115]) rotate([90, 0, 0]) cylinder(h=wall*4, r=pir_r, center=true);
        translate([40, -(d/2), -115]) rotate([90, 0, 0]) cylinder(h=wall*4, r=small_sensor_r, center=true);
            
        // front engraving
        translate([0, -(d/2) + wall, -145]) 
            rotate([90, 0, 0]) 
            linear_extrude(wall*2) 
            text("Focus Flow", size=18, font="Arial:style=Bold", halign="center", valign="center");

        // dht sensor cutout on the right side
        translate([(w/2), 0, -45]) cube([wall*4, dht_w, dht_h], center=true);
    }
}

module back_door() {
    door_w = w - (wall*4) - tol;
    door_h = h - (wall*4) - tol;
    
    translate([0, (d/2) - (wall/2), 0]) {
        difference() {
            cube([door_w, wall, door_h], center=true);
            
            // power cable hole at the bottom
            translate([0, 0, -(door_h/2)]) 
                rotate([90, 0, 0]) cylinder(h=wall*4, r=cable_hole_r, center=true);
        }
    }
}

module pi_cover() {
    // container for the pi to sit on top
    translate([0, 0, (h/2) + (pi_cover_h/2)]) {
        difference() {
            cube([w, d, pi_cover_h], center=true);
            
            translate([0, 0, -wall])
                cube([w - (wall*2), d - (wall*2), pi_cover_h], center=true);
                
            // vents so it doesnt overheat during cv tasks
            for(vx = [-50 : 20 : 50]) {
                for(vy = [-50 : 20 : 50]) {
                    translate([vx, vy, pi_cover_h/2])
                        cylinder(h=wall*4, r=4, center=true);
                }
            }
            
            // cable routing out the back of the hat
            translate([0, (d/2), -(pi_cover_h/2) + 10])
                cube([40, wall*4, 20], center=true);
        }
        
        // pegs to snap it into the main body
        translate([(w/2)-10, (d/2)-10, -(pi_cover_h/2) - 2]) cylinder(h=4, r=2, center=true);
        translate([-(w/2)+10, (d/2)-10, -(pi_cover_h/2) - 2]) cylinder(h=4, r=2, center=true);
        translate([(w/2)-10, -(d/2)+10, -(pi_cover_h/2) - 2]) cylinder(h=4, r=2, center=true);
        translate([-(w/2)+10, -(d/2)+10, -(pi_cover_h/2) - 2]) cylinder(h=4, r=2, center=true);
    }
}

// comment out what you dont need to print right now
main_body();
back_door();
pi_cover();