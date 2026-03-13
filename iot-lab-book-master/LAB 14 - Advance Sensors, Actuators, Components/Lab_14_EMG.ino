/****************************************************************************
 * File Name: EMG_Monitoring_Code
 *
 * Updated Version: 25/12/2024 (by Charith PERERA)
 *
 * Purpose:
 *   - Demonstrates reading an analog sensor (e.g., an EMG sensor) multiple times,
 *     averaging the readings, and mapping the value to a Grove LED Bar and an LCD.
 *   - Illustrates how sensor data can be displayed and smoothed in real time.
 *   - Useful for applications where muscle activity, force, or other analog signals
 *     need to be monitored in an IoT setup.
 ****************************************************************************/

// Include libraries for I2C communication, Grove LED Bar, and Grove RGB LCD
#include <Wire.h>
#include <Grove_LED_Bar.h>
#include "rgb_lcd.h"

// Create a Grove_LED_Bar object:
//   Parameters: (clkPin, dataPin, orientation, type)
//   In this case, we use pins 9 and 8 for clock and data, orientation = 0, type = LED_BAR_10.
Grove_LED_Bar bar(9, 8, 0, LED_BAR_10);

// Create an rgb_lcd object for the Grove RGB LCD
rgb_lcd lcd;

// Global variables for tracking analog sensor data
int max_analog_dta      = 300;    // Initial assumed maximum analog reading
int min_analog_dta      = 100;    // Initial assumed minimum analog reading
int static_analog_dta   = 0;      // Baseline reference (static) analog reading

/**
 * Function: getAnalog
 * -------------------
 * Reads the analog sensor multiple times for noise reduction, updates global max
 * and min values, and returns the averaged reading.
 *
 * @param pin  The analog pin number to read from (e.g., A0).
 * @return     The averaged analog reading over 32 samples.
 */
int getAnalog(int pin) {
    long sum = 0;
    
    // 1. Take 32 analog readings to reduce random fluctuations (noise).
    for (int i = 0; i < 32; i++) {
        sum += analogRead(pin);
    }
    
    // 2. Compute the average by right-shifting 5 bits (equivalent to dividing by 32).
    int dta = sum >> 5;  
    
    // 3. Update the global max and min values if the new reading is outside known bounds.
    if (dta > max_analog_dta) {
      max_analog_dta = dta;  
    }
    if (dta < min_analog_dta) {
      min_analog_dta = dta;
    }

    return dta;  // Return the average of the 32 readings.
}

void setup() {
    // 4. Initialize the Grove LCD for a 16-column by 2-row display.
    //    This allows us to write text on two lines of the LCD.
    lcd.begin(16, 2);

    // 5. Begin serial communication at 115200 baud for debugging or data logging.
    Serial.begin(115200);

    long sum = 0;

    // 6. Calibration routine:
    //    - We run a loop 11 times (i = 0 to 10).
    //    - Within each iteration, we take 100 averaged readings of the analog sensor.
    //    - We accumulate these readings in 'sum'.
    //    - After each batch, we set the LED bar level from 10 down to 0 (progress indicator).
    for (int i = 0; i <= 10; i++) {
        for (int j = 0; j < 100; j++) {
            sum += getAnalog(A0);
            delay(2);  // Short delay between readings
        }
        // Decrement the LED bar from 10 down to 0, indicating calibration progress.
        bar.setLevel(10 - i);
    }
    
    // 7. The total is now divided by 1100 (11*100) to find the average reading over
    //    this calibration routine. This average becomes our 'static_analog_dta' baseline.
    sum /= 1100;
    static_analog_dta = sum;  // Use this baseline for further comparisons
}

// Variables used to track and smooth the LED bar level:
int level       = 5;   // Current level of the LED bar
int level_buf   = 5;   // Previous level buffer for detecting changes

void loop() {
    // 8. Read an averaged sensor value from analog pin A0.
    int val = getAnalog(A0);

    // 9. Determine 'level2' based on whether the new reading is above or below
    //    our baseline 'static_analog_dta'.
    int level2;
    
    // If the sensor reading is higher than the baseline, shift the level upward.
    if (val > static_analog_dta) {
        // Map the difference between val and static_analog_dta to a range of 0-5,
        // then add 5 to "center" it on the LED bar.
        level2 = 5 + map(val, static_analog_dta, max_analog_dta, 0, 5);
    } 
    // Otherwise, if it's below the baseline, shift the level downward.
    else {
        // Map the difference to 0-5 in the other direction.
        level2 = 5 - map(val, min_analog_dta, static_analog_dta, 0, 5);
    }
    
    // 10. Smooth the transitions between levels by incrementing or decrementing 'level' 
    //     towards 'level2' by only 1 per loop iteration.
    if (level2 > level) {
        level++;
    } else if (level2 < level) {
        level--;
    }

    // 11. If there's a change in 'level', update the LED bar and display the current value on the LCD.
    if (level != level_buf) {
        level_buf = level;

        // Update the LED bar to the new level.
        bar.setLevel(level);

        // Clear the LCD and print the new EMG (or analog) value.
        lcd.clear();
        lcd.print("EMG value: ");
        lcd.print(val);

        // For debugging or logging, you might also print to Serial:
        // Serial.print("EMG value: ");
        // Serial.println(val);
    }
    delay(10);  // Small delay to avoid updating too quickly
}