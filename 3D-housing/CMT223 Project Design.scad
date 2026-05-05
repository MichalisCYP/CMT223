/* =====================================================================
   "THE ULTIMATE BEAST" - MAC STUDIO "PERSONALITY" EDITION (V2)
   Architecture: Apple-Style Rounded Rectangle (Squircle) Unibody
   Updates: Removed LED Bar for a cleaner aesthetic.
   ===================================================================== */

$fn = 80; // Smooth commercial curves

// --- 1. GLOBAL DIMENSIONS ---
wall = 3.5;
width = 150;     // Left to right
depth = 130;     // Front to back
height = 220;    // Total vertical height
corner_r = 25;   // Apple-style sweeping corner radius

// --- 2. COMPONENT SIZES & TOLERANCES ---
// Tiny OLED "Eyes" (Standard 0.96" OLED viewable area)
oled_w = 26;   oled_h = 14;   oled_r = 2;  
oled_spread = 50; // Distance between the two eyes

// Wide & Skinny LCD (Standard 16x2 character LCD viewable area)
lcd_w = 72;    lcd_h = 24;    lcd_r = 2;   

// Control Cluster
btn_d = 16.5;                 // 16mm Pomodoro Buttons
pot_d = 8.5;                  // 8.5mm hole for Rotary Angle Sensor shaft
control_spacing = 22;         // Tightly grouped under the LCD

// Ultrasonic Ranger (Posture Tracking)
sonar_d = 16.5;               
sonar_gap = 26;           

// Camera Servos
servo_w = 13;  servo_l = 25;  

// =====================================================================
// --- HELPER MODULES ---
// =====================================================================

module squircle_profile(w, d, r) {
    hull() {
        translate([-w/2+r, -d/2+r]) circle(r=r);
        translate([w/2-r, -d/2+r]) circle(r=r);
        translate([-w/2+r, d/2-r]) circle(r=r);
        translate([w/2-r, d/2-r]) circle(r=r);
    }
}

module rounded_rect(w, h, th, r) {
    linear_extrude(height=th, center=true)
    hull() {
        translate([-w/2+r, -h/2+r]) circle(r=r);
        translate([w/2-r, -h/2+r]) circle(r=r);
        translate([-w/2+r, h/2-r]) circle(r=r);
        translate([w/2-r, h/2-r]) circle(r=r);
    }
}

// =====================================================================
// --- PART 1: THE SILVER UNIBODY SHELL ---
// =====================================================================

module mac_style_shell() {
    color("Silver") 
    difference() {
        
        // A. Solid Outer Shell
        linear_extrude(height) squircle_profile(width, depth, corner_r);
        
        // B. Hollow Inner Cavity (Guarantees perfect 3.5mm walls)
        translate([0, 0, -1]) 
            linear_extrude(height - wall + 1) 
            squircle_profile(width - wall*2, depth - wall*2, corner_r - wall);

        // --- C. THE DASHBOARD (Front Face at Y = -depth/2) ---
        
        // 1. Dual OLED "Eyes" (Top of the face)
        translate([-oled_spread/2, -depth/2, 175]) 
            rotate([90, 0, 0]) rounded_rect(oled_w, oled_h, 20, oled_r);
        translate([oled_spread/2, -depth/2, 175]) 
            rotate([90, 0, 0]) rounded_rect(oled_w, oled_h, 20, oled_r);
            
        // 2. Ultrasonic Posture Sensors ("Nose / Cheeks" area)
        translate([-sonar_gap/2, -depth/2, 135]) 
            rotate([90, 0, 0]) cylinder(h=20, d=sonar_d, center=true);
        translate([sonar_gap/2, -depth/2, 135]) 
            rotate([90, 0, 0]) cylinder(h=20, d=sonar_d, center=true);
            
        // 3. Wide/Skinny LCD Display (Middle)
        translate([0, -depth/2, 85]) 
            rotate([90, 0, 0]) rounded_rect(lcd_w, lcd_h, 20, lcd_r);
            
        // 4. Control Cluster (Tightly grouped at the bottom)
        // Left Button (Start)
        translate([-control_spacing, -depth/2, 30]) 
            rotate([90, 0, 0]) cylinder(h=20, d=btn_d, center=true); 
        // Center Button (Stop)
        translate([0, -depth/2, 30]) 
            rotate([90, 0, 0]) cylinder(h=20, d=btn_d, center=true);   
        // Right Rotary Angle Sensor (Potentiometer)
        translate([control_spacing, -depth/2, 30]) 
            rotate([90, 0, 0]) cylinder(h=20, d=pot_d, center=true);  

        // --- D. THE ROOF (Top Face at Z = height) ---
        
        // 5. Camera 1: Desk-Facing Servo Mount (Front Edge)
        translate([0, -depth/2 + 15, height]) cube([servo_l, servo_w, 20], center=true);
        // 6. Camera 2: User-Facing Servo Mount (Back Edge)
        translate([0, depth/2 - 15, height]) cube([servo_l, servo_w, 20], center=true);

        // 7. Precision Acoustic Mesh (For speaker and loudness sensor)
        for (x = [-45 : 6 : 45]) {
            for (y = [-35 : 6 : 35]) {
                if (sqrt(x*x + y*y) < 40) {
                    translate([x, y, height]) cylinder(h=20, d=3.5, center=true);
                }
            }
        }

        // --- E. REAR UTILITIES ---
        
        // 8. Cable Pass-through / Power Port
        translate([0, depth/2, 15]) 
            rotate([90, 0, 0]) rounded_rect(40, 15, 20, 3);
            
        // 9. Secondary Heat Exhaust Vents
        for (z = [160 : 12 : 200]) {
            translate([0, depth/2, z]) 
                rotate([90, 0, 0]) rounded_rect(50, 4, 20, 2);
        }
    }
}

// =====================================================================
// --- PART 2: THE INTERNAL CHASSIS (SLED) ---
// =====================================================================

module internal_sled() {
    color("DimGray")
    union() {
        // 1. Locking Base Plate
        difference() {
            linear_extrude(4) squircle_profile(width - wall*2 - 1, depth - wall*2 - 1, corner_r - wall);
            translate([0, 15, -1]) rounded_rect(50, 30, 10, 5);
        }
        
        // 2. Structural Pillars
        translate([width/2 - 25, depth/2 - 25, 0]) cylinder(h=150, d=8);
        translate([-width/2 + 25, depth/2 - 25, 0]) cylinder(h=150, d=8);
        translate([width/2 - 25, -depth/2 + 25, 0]) cylinder(h=150, d=8);
        translate([-width/2 + 25, -depth/2 + 25, 0]) cylinder(h=150, d=8);
        
        // 3. Pi Mount Tier 1
        translate([0, 0, 25]) pi_mounting_tray();
        // 4. Pi Mount Tier 2
        translate([0, 0, 100]) pi_mounting_tray();
    }
}

module pi_mounting_tray() {
    difference() {
        translate([0, 0, 2]) rounded_rect(width - 40, depth - 40, 4, 10);
        translate([0, 0, 2]) rounded_rect(60, 50, 10, 5);
    }
    // 2.5mm Pegs for Raspberry Pi 4
    translate([-29, 24.5, 4]) cylinder(h=5, d=2.5);
    translate([29, 24.5, 4]) cylinder(h=5, d=2.5);
    translate([-29, -24.5, 4]) cylinder(h=5, d=2.5);
    translate([29, -24.5, 4]) cylinder(h=5, d=2.5);
}

// =====================================================================
// --- RENDER COMMANDS ---
// =====================================================================

mac_style_shell();
// translate([0, 0, -30]) internal_sled();