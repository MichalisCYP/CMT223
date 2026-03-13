/***************************************************************************
* Sketch Name: bassControl
*
* Original Version: 24/01/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description: Control the bass level of a speaker while changing LCD RGB 
*              backlight color via joystick input.
*
***************************************************************************/

// 1. Include necessary libraries for I2C communication (Wire), 
//    and for controlling the Grove RGB LCD module.
#include <Wire.h>
#include "rgb_lcd.h"

// 2. Define the digital pin used to drive the speaker.
#define SPEAKER 4

// 3. Create an rgb_lcd object to interact with the Grove LCD RGB display.
rgb_lcd lcd;

// 4. Variables to store the initial color values (R, G, B) for the LCD backlight.
//    Values range from 0–255 for each channel.
int colorR = 123;
int colorG = 123;
int colorB = 123;

// 5. A variable to control the timing of the speaker's tone (the "bass" value).
//    Larger values = slower toggle = lower pitch.
int bass = 1000;

// ---------------------------------------------------------------------------
// SETUP
// ---------------------------------------------------------------------------
void setup() 
{
  // 6. Configure the speaker pin as an output and set it LOW initially.
  pinMode(SPEAKER, OUTPUT);
  digitalWrite(SPEAKER, LOW);

  // 7. Initialize the LCD:
  //    - 16 columns and 2 rows (common Grove LCD setup).
  lcd.begin(16, 2);

  // 8. Set the backlight color to the default values (R=123, G=123, B=123).
  lcd.setRGB(colorR, colorG, colorB);

  // 9. Print a greeting message on the first row of the LCD.
  lcd.print("Hello Friend!");

  // 10. Give the user a moment (1 second) to read the message.
  delay(1000);

  // 11. It’s good practice to start serial communication if you want to 
  //     print debug information or sensor values.
  Serial.begin(9600);
}

// ---------------------------------------------------------------------------
// LOOP
// ---------------------------------------------------------------------------
void loop() 
{
  // 12. Read x-axis (A0) and y-axis (A1) values from the joystick.
  //     These usually range from 0 to 1023 on most Arduino boards.
  int sensorValue1 = analogRead(A0);  // X-axis
  int sensorValue2 = analogRead(A1);  // Y-axis

  // 13. Print the joystick coordinates to the Serial Monitor.
  Serial.print("The X and Y coordinate is: ");
  Serial.print(sensorValue1);
  Serial.print(", ");
  Serial.println(sensorValue2);
  Serial.println(" ");  
  delay(200); // Slight delay to avoid flooding the serial monitor.

  // 14. Define the "neutral" or "center" values for the joystick.
  //     (These may vary slightly depending on the module’s calibration.)
  int joystickXDef = 509;
  int joystickYDef = 519;

  // 15. Update the LCD to show the current bass value.
  //     - First row: "Bass value:"
  //     - Second row: numerical value of 'bass'.
  lcd.setCursor(0, 0);
  lcd.print("Bass value:");
  lcd.setCursor(0, 1);
  lcd.print(bass);

  // 16. Adjust the bass value based on X-axis movement:
  //     - If the joystick is moved left (value < joystickXDef), decrease the bass.
  //     - If the joystick is moved right (value > joystickXDef), increase the bass.
  //     - Check for special case near 510 to avoid random spikes.
  if (sensorValue1 < joystickXDef && sensorValue1 != 510) {
    bass = bass - 200;  // Bass down
  } 
  else if (sensorValue1 > joystickXDef && sensorValue1 != 510) {
    bass = bass + 200;  // Bass up
  }

  // 17. Adjust the LCD backlight color based on Y-axis movement:
  //     - If the joystick is moved up (value > joystickYDef), set color to RED (255,0,0).
  //     - If the joystick is moved down (value < joystickYDef), set color to GREEN (0,255,0).
  //     - Check for special case near 520 to avoid random spikes.
  if (sensorValue2 > joystickYDef && sensorValue2 != 520) {
    colorR = 255; colorG = 0;   colorB = 0;   // RED
  } 
  else if (sensorValue2 < joystickYDef && sensorValue2 != 520) {
    colorR = 0;   colorG = 255; colorB = 0;   // GREEN
  }

  // 18. Apply the newly set color to the LCD backlight.
  lcd.setRGB(colorR, colorG, colorB);

  // 19. Generate a square wave on the speaker pin to produce a tone.
  //     - Do 100 cycles of toggling HIGH/LOW, each lasting 'bass' microseconds.
  for (int i = 0; i < 100; i++)
  {
    digitalWrite(SPEAKER, HIGH);
    delayMicroseconds(bass);
    digitalWrite(SPEAKER, LOW);
    delayMicroseconds(bass);
  }

  // 20. Delay for 1 second before reading the joystick and updating again.
  //     This ensures the user has time to see or hear the result 
  //     before the next cycle.
  delay(1000);
}
