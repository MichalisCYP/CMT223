/***************************************************************************
* Sketch Name: BLE Sensor
*
* Original Version: 07/12/2021 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates basic Bluetooth Low Energy (BLE) functionality using
*     a Grove BLE v1.0 module, alongside an ultrasonic sensor to measure
*     distance and control an LED.
*   - Sends distance-based alerts (Danger, Warning, Safe) to a paired BLE device.
*   - Illustrates how to configure a BLE module, read sensor data, and provide
*     feedback via an LED.
***************************************************************************/

// 1. Include the Ultrasonic library for distance measurement.
//    The Ultrasonic sensor is initialized on digital pin 7.
#include "Ultrasonic.h"
Ultrasonic ultrasonic(7);

// 2. Define the LED pin and configure it as an output to provide visual feedback.
#define LED 5

// ---------------------------------------------------------------------------
// SETUP
// ---------------------------------------------------------------------------
void setup()
{
  // 3. Initialize the LED pin as OUTPUT.
  pinMode(LED, OUTPUT);

  // 4. Start serial communication at 9600 baud for debugging messages.
  Serial.begin(9600);
  while(!Serial);

  // 5. Call a dedicated function to set up the BLE module connection parameters.
  //    (e.g., role, name).
  setupBlueToothConnection();
}

// ---------------------------------------------------------------------------
// LOOP
// ---------------------------------------------------------------------------
void loop()
{
  // 6. Measure the distance using the ultrasonic sensor and print it out.
  unsigned long distance = range();  // in centimeters

  Serial.print("Distance is: ");
  Serial.print(distance);
  Serial.println(" cm");

  // 7. Based on the measured distance, send a status message (Danger, Warning, Safe)
  //    to the BLE device using Serial1, and control the LED accordingly.
  if (distance < 30) {
    // If distance is less than 30 cm: "Danger"
    Serial1.println("Danger");
    digitalWrite(LED, HIGH);
    delay(500);
  } 
  else if (distance >= 30 && distance <= 100) {
    // If distance is between 30 and 100 cm: "Warning"
    Serial1.println("Warning");
    blinking();
  } 
  else {
    // If distance is above 100 cm: "Safe"
    Serial1.println("Safe");
    digitalWrite(LED, LOW);
    delay(500);
  }

  // 8. Handle incoming data from the BLE module (Serial1) and from the Serial Monitor.
  char recvChar;
  String WholeCommand = "";

  // 8a. If there's data from the BLE device, read and print it to the Serial Monitor.
  while (Serial1.available()) {
    recvChar = Serial1.read();
    Serial.print(recvChar);  // Echo the received data for debugging.
  }

  // 8b. If there's data from the Serial Monitor (PC), capture it as a string
  //     and send it to the BLE device.
  while (Serial.available()) {
    WholeCommand = SerialString();
    Serial1.print(WholeCommand);
    delay(400);
  }
}

// ---------------------------------------------------------------------------
// SUPPORTING FUNCTIONS
// ---------------------------------------------------------------------------

/**
 * Function: SerialString
 * ----------------------
 * Reads characters from Serial (the PC Serial Monitor) until there is no more data.
 * Concatenates the characters into a string, which is then returned.
 */
String SerialString()
{
  String inputString = "";
  while (Serial.available()) {
    char inputChar = (char)Serial.read();
    inputString += inputChar;
  }
  return inputString;
}

/**
 * Function: setupBlueToothConnection
 * ----------------------------------
 * Configures the BLE module’s basic parameters via Serial1:
 *   - Baud rate: 9600
 *   - Role: Peripheral (ROLE0)
 *   - Name: "Ratata"
 */
void setupBlueToothConnection()
{
  Serial1.begin(9600);
  Serial1.print("AT");
  delay(400);

  // Set the BLE module to Peripheral role.
  Serial1.print("AT+ROLE0");
  delay(400);

  // Assign the BLE module name as "Ratata".
  Serial1.print("AT+NAMERatata");
  Serial1.flush();
}

/**
 * Function: blinking
 * ------------------
 * Toggles the LED ON and OFF with a 500 ms delay each time.
 * Used for the "Warning" state in the main loop.
 */
void blinking()
{
  digitalWrite(LED, HIGH);  // Turn the LED on
  delay(500);
  digitalWrite(LED, LOW);   // Turn the LED off
  delay(500);
}

/**
 * Function: range
 * ---------------
 * Measures the distance using the ultrasonic sensor (in centimeters),
 * introduces a short delay (10 ms), and returns the measured value.
 */
unsigned long range()
{
  unsigned long RangeInCentimeters;
  RangeInCentimeters = ultrasonic.MeasureInCentimeters();
  delay(10);
  return RangeInCentimeters;
}
