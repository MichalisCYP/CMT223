/***************************************************************************
* Sketch Name: rotaryAngleSensor
*
* Original Version: 07/06/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates reading an analog voltage from pin A3, converting it to a 
*     0–5V range, and then mapping that voltage to an angle (0–300°).
*   - Continuously prints the calculated angle to the Serial Monitor.
*   - Useful in scenarios where a rotational sensor or potentiometer is used
*     to measure angles.
***************************************************************************/

// 1. Declare global variables to store the voltage and the calculated angle.
float voltage;
float degrees;

void setup() {
  // 2. Pin configuration for A3. Since A3 is an analog pin, we typically do NOT
  //    use pinMode in the same way as digital pins. On many Arduino boards, 
  //    you can omit pinMode(A3, INPUT) entirely. If you want to enforce INPUT mode:
  //    pinMode(A3, INPUT);  <-- Usually optional for analog pins

  // 3. Initialize the Serial Monitor at 9600 baud for debugging or observation.
  Serial.begin(9600);
}

void loop() {
  // 4. Read the analog value from pin A3 (range 0–1023 on a typical 10-bit ADC).
  //    Multiply by 5.0 / 1023.0 to convert from ADC counts to voltage (0–5V).
  voltage = analogRead(A3) * 5.0 / 1023.0;

  // 5. Convert the measured voltage to degrees (0–300°).
  //    - This suggests a sensor or potentiometer that outputs 0V at 0° and 5V at 300°.
  //    - If your sensor has a different range, adjust the calculation accordingly.
  degrees = (voltage * 300.0) / 5.0;

  // 6. Print a descriptive message and the current angle to the Serial Monitor.
  Serial.println("The angle between the mark and the starting position: ");
  Serial.println(degrees);

  // 7. Delay for 500 ms so the Serial Monitor updates at ~2 readings/second.
  delay(500);
}
