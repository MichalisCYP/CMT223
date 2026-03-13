/***************************************************************************
* Sketch Name: lightSensor
*
* Original Version: 07/06/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates how to read analog values from a light sensor connected
*     to analog pin A0.
*   - Prints the sensor reading to the Serial Monitor every 250 ms.
*   - Useful for measuring ambient light levels in an IoT or electronics project.
***************************************************************************/

void setup() {
  // 1. Configure the analog pin A0.
  //    Although many Arduino boards auto-configure analog pins, we can optionally
  //    use pinMode(A0, INPUT). If you see pinMode(A0, 0) in older code, it might
  //    represent an 'INPUT' constant. On most Arduino boards, analogRead() does
  //    not require explicit pinMode setup for analog pins. We'll keep it for clarity.
  pinMode(A0, INPUT);

  // 2. Start serial communication at 9600 baud. This allows monitoring
  //    sensor readings in the Arduino Serial Monitor or any serial terminal.
  Serial.begin(9600);
}

void loop() {
  // 3. Print a label to make the output more readable.
  Serial.println("Light Value:");

  // 4. Read the analog value from pin A0 (range 0–1023).
  //    A reading of 0 indicates minimal light, while 1023 indicates
  //    maximum light (when using the default 5V reference).
  int lightValue = analogRead(A0);

  // 5. Print the light sensor reading to the Serial Monitor.
  Serial.println(lightValue);

  // 6. Delay 250 ms before reading again.
  //    This rate provides ~4 readings per second. Adjust as needed.
  delay(250);
}
