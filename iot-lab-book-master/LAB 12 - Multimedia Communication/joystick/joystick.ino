/****************************************************************************
 * File Name: Grove_Thumb_Joystick_Example
 *
 * Updated Version: 25/12/2024 (by Charith PERERA)
 *
 * Purpose:
 *   - Demonstrates how to read the X and Y coordinates from a Grove Thumb Joystick.
 *   - Prints the readings to the Serial Monitor for easy observation.
 *   - Useful in IoT applications as a user input device (e.g., controlling robotics,
 *     navigation in menus, or adjusting settings).
 *
 * Reference:
 *   - https://wiki.seeedstudio.com/Grove-Thumb_Joystick/
 ****************************************************************************/

/*
  The following code is available at:
  https://wiki.seeedstudio.com/Grove-Thumb_Joystick/
*/

// ---------------------------------------------------------------------------
// SETUP
// ---------------------------------------------------------------------------
void setup()
{
    // 1. Begin serial communication at 9600 baud for monitoring the analog values.
    Serial.begin(9600);
}

// ---------------------------------------------------------------------------
// LOOP
// ---------------------------------------------------------------------------
void loop()
{
    // 2. Read the X and Y coordinates from the two analog pins (A0 and A1).
    //    Values range from 0 to 1023 on most Arduino boards.
    int sensorValueX = analogRead(A0);
    int sensorValueY = analogRead(A1);

    // 3. Print the readings to the Serial Monitor in a human-readable format.
    //    This helps you visualize how the joystick is being moved.
    Serial.print("The X and Y coordinate is: ");
    Serial.print(sensorValueX, DEC);
    Serial.print(", ");
    Serial.println(sensorValueY, DEC);
    Serial.println(" ");  // Blank line for clarity

    // 4. Delay for 200 milliseconds before reading again.
    //    Adjust as necessary based on the desired sampling rate or responsiveness.
    delay(200);
}

