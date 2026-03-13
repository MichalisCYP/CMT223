/****************************************************************************
 * File Name: Grove_RGB_LCD_Example
 *
 * Updated Version: 25/12/2024 (by Charith PERERA)
 *
 * Purpose:
 *   - Demonstrates how to display text on a Grove LCD with RGB backlight.
 *   - Shows how to control the LCD's backlight color and print dynamic data
 *     (in this case, time since startup).
 *   - Can be adapted in IoT projects to provide device status, sensor readings,
 *     or system alerts in a user-friendly way.
 *
 * Reference:
 *   - https://wiki.seeedstudio.com/Grove-LCD_RGB_Backlight/
 ****************************************************************************/

/*
  The following code is available at:
  https://wiki.seeedstudio.com/Grove-LCD_RGB_Backlight/
*/

// 1. Include necessary libraries for I2C communication and the Grove RGB LCD.
#include <Wire.h>
#include "rgb_lcd.h"

// 2. Create an rgb_lcd object to interact with the LCD.
rgb_lcd lcd;

// 3. Define the initial color for the LCD backlight (Red, Green, Blue).
//    Range is 0–255 for each color channel.
const int colorR = 255;   // Red channel
const int colorG = 0;     // Green channel
const int colorB = 0;     // Blue channel

// ---------------------------------------------------------------------------
// SETUP
// ---------------------------------------------------------------------------
void setup() 
{
    // 4. Initialize the LCD with 16 columns and 2 rows.
    //    This matches the standard Grove 16x2 LCD.
    lcd.begin(16, 2);

    // 5. Set the initial LCD backlight color using the RGB values defined above.
    lcd.setRGB(colorR, colorG, colorB);

    // 6. Print a simple message to the LCD.
    lcd.print("hello, world!");

    // 7. Pause briefly (1 second) to allow the message to be easily seen.
    delay(1000);
}

// ---------------------------------------------------------------------------
// LOOP
// ---------------------------------------------------------------------------
void loop() 
{
    // 8. Set the cursor to the first column of the second row (line index 1).
    //    Note: The first row is index 0, the second row is index 1.
    lcd.setCursor(0, 1);

    // 9. Print the number of seconds since the program started running
    //    (i.e., since the last reset or power-up).
    lcd.print(millis() / 1000);

    // 10. Update the display every 100 milliseconds.
    //     In many IoT projects, you might display sensor readings or system
    //     uptime in a similar way.
    delay(100);
}
