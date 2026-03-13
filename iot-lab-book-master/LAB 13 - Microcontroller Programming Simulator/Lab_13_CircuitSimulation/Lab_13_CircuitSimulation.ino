/****************************************************************************
 * File Name: Simple_Analog_Read_LED_Indicator
 *
 * Updated Version: 25/12/2024 (by Charith PERERA)
 *
 * Purpose:
 *   - Reads an analog value from pin A5 (e.g., from a sensor or potentiometer).
 *   - Lights up pairs of LEDs based on the read value’s range.
 *   - Provides a basic framework for visualizing sensor readings, which can 
 *     be extended to IoT projects by sending data to the cloud or activating 
 *     other actuators.
 ****************************************************************************/

// 1. Define the pin used for reading analog input and the pins for controlling LEDs.
int port = A5;   // The analog input pin (not used directly below, but declared for clarity)

int led1 = 13;   // LED pin 1
int led2 = 12;   // LED pin 2
int led3 = 11;   // LED pin 3
int led4 = 10;   // LED pin 4
int led5 = 9;    // LED pin 5
int led6 = 8;    // LED pin 6

// 2. This variable will store the analog reading (range: 0 to 1023 on most Arduino boards).
int reading;

void setup()
{
  // 3. Initialize the serial monitor for debugging or logging.
  Serial.begin(9600);

  // 4. Set each LED pin as an OUTPUT so we can control it (turn it ON or OFF).
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  pinMode(led4, OUTPUT);
  pinMode(led5, OUTPUT);
  pinMode(led6, OUTPUT);
}

void loop()
{
  // 5. Read the analog value from pin A5. This could be from a sensor or a potentiometer.
  //    The value typically ranges from 0 (lowest) to 1023 (highest).
  reading = analogRead(A5);
  
  // 6. Print the reading to the Serial Monitor for observation or debugging.
  Serial.println(reading);
  delay(100);  // Small delay to slow down the serial print rate.

  // 7. Based on the analog reading, turn ON or OFF certain LEDs to indicate different ranges.
  //    Here we define simple thresholds: 0, 341, 682, and 683+.
  
  if(reading == 0)
  {
    // When the reading is exactly zero, turn off led1 and led2.
    digitalWrite(led1, LOW);
    digitalWrite(led2, LOW);
    // Notice that led3, led4, led5, and led6 aren't mentioned here,
    // so their previous states remain the same.
  }
  else if(reading >= 0 && reading <= 341)
  {
    // If the reading is between 0 and 341 (excluding 0 itself above),
    // turn ON led1 & led2, and turn OFF led3 & led4.
    digitalWrite(led1, HIGH);
    digitalWrite(led2, HIGH);
    digitalWrite(led3, LOW);
    digitalWrite(led4, LOW);
  }
  else if(reading >= 341 && reading <= 682)
  {
    // If the reading is between 341 and 682,
    // turn ON led3 & led4, and turn OFF led5 & led6.
    digitalWrite(led3, HIGH);
    digitalWrite(led4, HIGH);
    digitalWrite(led5, LOW);
    digitalWrite(led6, LOW);
  }
  else if(reading >= 683)
  {
    // If the reading is 683 or above,
    // turn ON led5 & led6.
    digitalWrite(led5, HIGH);
    digitalWrite(led6, HIGH);
  }
}
