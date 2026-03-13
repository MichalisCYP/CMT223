/***************************************************************************
* Sketch Name: ledKitTest.ino
*
* Original Version: 02/22/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates toggling an LED (connected to pin D5 on the Grove Base Shield)
*     on and off at a regular interval (500 ms).
*   - Commonly used as an introductory example in Arduino or IoT applications.
***************************************************************************/

// 1. Define the digital pin used to connect the LED kit on the Grove base shield.
#define LED 5  // Connected to D5

// ---------------------------------------------------------------------------
// SETUP
// ---------------------------------------------------------------------------
void setup() {
  // 2. Configure the LED pin as an OUTPUT, allowing it to be driven HIGH or LOW.
  pinMode(LED, OUTPUT);
}

// ---------------------------------------------------------------------------
// LOOP
// ---------------------------------------------------------------------------
void loop() {
  // 3. Turn the LED ON by driving the pin HIGH.
  digitalWrite(LED, HIGH);
  //    Delay for 500 milliseconds (half a second), keeping the LED lit.
  delay(500);

  // 4. Turn the LED OFF by driving the pin LOW.
  digitalWrite(LED, LOW);
  //    Delay for another 500 milliseconds with the LED off.
  delay(500);
}
