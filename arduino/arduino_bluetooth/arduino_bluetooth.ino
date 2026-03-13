/***************************************************************************
* Sketch Name: arduino_bluetooth
*
* Original Version: 03/03/2020 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates Bluetooth communication between an Arduino and a
*     Raspberry Pi or other Bluetooth-capable device.
*   - Reads a PIR (motion) sensor on digital pin 2 and a light sensor on
*     analog pin A3.
*   - Sends both readings as a single structured message via Bluetooth.
*   - Configures a SoftwareSerial connection on digital pins 8 (RX) and 9 (TX)
*     for the Bluetooth module.
***************************************************************************/

// 1. Include the SoftwareSerial library so we can use digital pins for serial RX/TX.
#include <SoftwareSerial.h>

// 2. Assign pins for the SoftwareSerial (Bluetooth) module and the PIR sensor.
#define RxD 8    // Arduino RX pin for Bluetooth
#define TxD 9    // Arduino TX pin for Bluetooth
#define PIR_MOTION_SENSOR 2  // PIR sensor input pin
#define LIGHT_SENSOR A3       // Light sensor analog input pin

// 3. Instantiate a SoftwareSerial object using pins RxD and TxD.
SoftwareSerial blueToothSerial(RxD, TxD);

void setup()
{
  // 4. Start the hardware Serial for debugging and messages to the Serial Monitor.
  Serial.begin(9600);
  //    Some Arduino boards require waiting for Serial to be ready (e.g., Leonardo).
  while(!Serial) { ; }
  Serial.println("Started");

  // 5. Configure the sensor pins and Bluetooth pins.
  //    - pinMode(RxD, INPUT) is optional because SoftwareSerial handles it.
  //    - pinMode(TxD, OUTPUT) is also handled by SoftwareSerial, but we keep it for clarity.
  pinMode(PIR_MOTION_SENSOR, INPUT);
  pinMode(LIGHT_SENSOR, INPUT);
  pinMode(RxD, INPUT);
  pinMode(TxD, OUTPUT);

  // 6. Set up the Bluetooth module with the desired baud rate, role, and name.
  setupBlueToothConnection();

  // 7. Flush any lingering data on both the hardware and software serial buffers.
  Serial.flush();
  blueToothSerial.flush();
}

void loop()
{
  // 8. Check if there is any data coming from the Bluetooth module (blueToothSerial).
  //    If so, read it character by character and print it to the Arduino Serial Monitor.
  if (blueToothSerial.available() > 0) {
    char incoming = blueToothSerial.read();
    Serial.print(incoming);
  }

  // 9. Read PIR and light sensors, then send one line that is easy to parse on Raspberry Pi.
  int pirState = digitalRead(PIR_MOTION_SENSOR);
  int lightValue = analogRead(LIGHT_SENSOR);

  blueToothSerial.print("PIR:");
  blueToothSerial.print(pirState);
  blueToothSerial.print(",LIGHT:");
  blueToothSerial.println(lightValue);

  Serial.print("PIR:");
  Serial.print(pirState);
  Serial.print(",LIGHT:");
  Serial.println(lightValue);

  delay(1000);
}

/***************************************************************************
* Function Name: setupBlueToothConnection
* Description:   Initializes the Bluetooth connection with AT commands.
*                Configures the baud rate, role, name, and authentication.
***************************************************************************/
void setupBlueToothConnection()
{
  // 10. Begin a software serial session at 9600 baud for the Bluetooth module.
  blueToothSerial.begin(9600);

  // 11. Send a series of AT commands to configure the BLE module.
  blueToothSerial.print("AT");
  delay(2000);

  // Set the module’s baud rate to 9600 (AT+BAUD4 typically means 9600).
  blueToothSerial.print("AT+BAUD4");
  delay(2000);

  // Set the module’s role to “S” (often means slave/peripheral).
  blueToothSerial.print("AT+ROLES");
  delay(2000);

  // Assign a name (up to 12 characters). Here, it’s “Slave”.
  blueToothSerial.print("AT+NAMESlave");
  delay(2000);

  // Enable authentication (AT+AUTH1).
  blueToothSerial.print("AT+AUTH1");
  delay(2000);

  // 12. Flush any residual data from the software serial buffer.
  blueToothSerial.flush();
  Serial.println("Finished Bluetooth Setup");
}
