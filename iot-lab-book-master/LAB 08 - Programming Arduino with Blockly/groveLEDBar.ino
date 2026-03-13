/***************************************************************************
* Sketch Name: groveLEDBar
*
* Original Version: 07/06/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates how to control a 10-segment Grove LED Bar using the Grove_LED_Bar library.
*   - Initializes the LED bar with clock pin D5 and data pin D4, then “walks” the
*     brightness level from 0 (all off) to 10 (all on).
*   - Provides a simple introductory example of incremental LED bar control.
***************************************************************************/

#include <Grove_LED_Bar.h>

// 1. Create a Grove_LED_Bar object, specifying:
//    - clock pin (5), data pin (4),
//    - orientation (0 => red-to-green, 1 => green-to-red),
//    - and the LED_BAR_10 constant to indicate 10 segments.
Grove_LED_Bar bar(5, 4, 0, LED_BAR_10);

void setup() {
  // 2. Initialize the LED bar. This function sets up communication 
  //    with the clock and data pins and prepares it for updates.
  bar.begin();
}

void loop() {
  // 3. “Walk” through each of the 10 LEDs in ascending order of brightness.
  //    The for-loop increments from 0 (all LEDs off) to 10 (all LEDs on).
  for (int i = 0; i <= 10; i++) {
    // 3a. Set the current LED bar level to 'i', lighting up i segments.
    bar.setLevel(i);
    
    // 3b. Delay 100 milliseconds before moving to the next level.
    delay(100);
  }
}
