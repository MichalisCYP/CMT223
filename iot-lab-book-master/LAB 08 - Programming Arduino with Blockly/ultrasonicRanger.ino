/***************************************************************************
* Sketch Name: ultrasonicDistanceTest
*
* Original Version: 07/06/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates how to measure distance in centimeters using the Ultrasonic 
*     library for Arduino.
*   - Continuously prints the measured distance to the Serial Monitor, 
*     updating every 250 milliseconds.
***************************************************************************/

#include <Ultrasonic.h>

// 1. Create an Ultrasonic object on digital pin 3. 
//    The library uses the configured pin to both send and receive ultrasonic pulses.
Ultrasonic ult3(3);

// ---------------------------------------------------------------------------
// SETUP
// ---------------------------------------------------------------------------
void setup() {
  // 2. Initialize serial communication at 9600 baud. 
  //    This allows us to send data (the measured distance) to the Serial Monitor.
  Serial.begin(9600);
}

// ---------------------------------------------------------------------------
// LOOP
// ---------------------------------------------------------------------------
void loop() {
  // 3. Use the ultrasonic sensor’s MeasureInCentimeters() method to get the distance.
  //    This method sends out an ultrasonic pulse, waits for its echo, 
  //    and calculates the distance based on the time taken.
  long distance = ult3.MeasureInCentimeters();

  // 4. Print the distance in centimeters to the Serial Monitor for real-time observation.
  //    This is useful for debugging or analyzing sensor data.
  Serial.println(distance);

  // 5. Delay for 250 milliseconds before taking the next reading.
  //    Adjust this interval to balance between data granularity and CPU usage.
  delay(250);
}
