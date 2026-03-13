/***************************************************************************
* Sketch Name: BLE
*
* Original Version: 06/12/2021 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates basic BLE (Bluetooth Low Energy) functionality using 
*     a Grove BLE v1.0 module.
*   - Sets the BLE module to Peripheral role, names it "Ratata," and 
*     relays data between the Arduino Serial Monitor and the BLE module.
***************************************************************************/

// ---------------------------------------------------------------------------
// SETUP
// ---------------------------------------------------------------------------
void setup()
{
  // 1. Begin serial communication at 9600 baud for debugging/monitoring via PC.
  Serial.begin(9600);

  // 2. Some boards (e.g., Leonardo) require waiting for Serial to be ready.
  while(!Serial);

  // 3. Call a helper function to configure and initialize the BLE module.
  setupBlueToothConnection();
}

// ---------------------------------------------------------------------------
// LOOP
// ---------------------------------------------------------------------------
void loop()
{
  // 4. Variables for handling incoming and outgoing data.
  char recvChar;
  String WholeCommand = "";

  // 5. Check if the BLE module (Serial1) has data available.
  //    If yes, read it one character at a time and print it to the Serial Monitor.
  while(Serial1.available()){
    recvChar = Serial1.read();
    Serial.print(recvChar);  // Echo BLE data to the Serial Monitor for debugging.
  }

  // 6. Check if the Serial Monitor has data to send to the BLE module.
  while(Serial.available()){
    // 6a. Gather a complete string of characters from the Serial Monitor.
    WholeCommand = SerialString();

    // 6b. Forward that string to the BLE module via Serial1.
    Serial1.print(WholeCommand);

    // 6c. Small delay to prevent flooding the BLE module with rapid data.
    delay(400);
  }
}

// ---------------------------------------------------------------------------
// SUPPORT FUNCTIONS
// ---------------------------------------------------------------------------

/**
 * Function: SerialString
 * ----------------------
 * Reads all available characters from the Serial input (PC side) and combines
 * them into a single string. Returns the collected string once no more data
 * is available.
 */
String SerialString()
{
  String inputString = "";
  while (Serial.available()){
    char inputChar = (char)Serial.read();
    inputString += inputChar;
  }
  return inputString;
}

/**
 * Function: setupBlueToothConnection
 * ----------------------------------
 * Configures the BLE module to:
 *   - Communicate at 9600 baud
 *   - Operate as a Peripheral (ROLE0)
 *   - Be named "Ratata"
 * After sending AT commands, the configuration is flushed to ensure proper setup.
 */
void setupBlueToothConnection()
{
  // 7. Start Serial1 at 9600 baud for BLE communication.
  Serial1.begin(9600);

  // 8. Basic AT command to check communication with the BLE module.
  Serial1.print("AT");
  delay(400);

  // 9. Set the BLE module to Peripheral mode.
  Serial1.print("AT+ROLE0");
  delay(400);

  // 10. Give the BLE module a custom name for easier identification during pairing.
  Serial1.print("AT+NAMERatata");
  Serial1.flush();
}
