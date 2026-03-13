/***************************************************************************
* Sketch Name: lcdTest.ino
*
* Original Version: 02/22/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates using a Grove RGB LCD to display text and cycle through
*     different backlight colors. Displays a “hello, world!” message initially,
*     then continuously updates the LCD backlight and prints the elapsed time.
***************************************************************************/

// 1. Include the library for the Grove RGB LCD.
#include "rgb_lcd.h"

// 2. Create an rgb_lcd object to interact with the LCD (16 columns x 2 rows).
rgb_lcd lcd;

// 3. Define initial RGB values for the backlight color (ranging from 0 to 255).
const int colorR = 125;
const int colorG = 125;
const int colorB = 125;

// ---------------------------------------------------------------------------
// SETUP
// ---------------------------------------------------------------------------
void setup() 
{
  // 4. Initialize the LCD with 16 columns and 2 rows.
  lcd.begin(16, 2);

  // 5. Set the LCD’s backlight to the initial color (125, 125, 125).
  lcd.setRGB(colorR, colorG, colorB);

  // 6. Print a welcome message on the top row of the LCD.
  lcd.print("hello, world!");

  // 7. Pause briefly (1 second) to allow the user to read the message.
  delay(1000);
}

// ---------------------------------------------------------------------------
// LOOP
// ---------------------------------------------------------------------------
void loop() 
{
  // 8. Cycle through three color phases (red, green, and blue).
  //    Each phase increments one color channel from 0 to 254 (or 255) 
  //    while keeping the other channels at 0.
  //    This creates a gradual color transition effect on the LCD backlight.

  // 8a. Red Phase
  for(int i = 0; i < 255; i++){
    // Increase red from 0 to 254, keep green & blue at 0
    lcd.setRGB(i, 0, 0);
  }

  // 8b. Green Phase
  for(int i = 0; i < 255; i++){
    // Increase green from 0 to 254, keep red & blue at 0
    lcd.setRGB(0, i, 0);
  }

  // 8c. Blue Phase
  for(int i = 0; i < 255; i++){
    // Increase blue from 0 to 254, keep red & green at 0
    lcd.setRGB(0, 0, i);
  }

  // 9. Move the LCD cursor to the first column of the second row (index 1).
  lcd.setCursor(0, 1);

  // 10. Print the number of seconds elapsed since the program started 
  //     (dividing `millis()` by 1000).
  lcd.print(millis() / 1000);

  // 11. Small delay to slow down how frequently the LCD refreshes.
  //     Adjust this if you want faster or slower updates.
  delay(100);
}
