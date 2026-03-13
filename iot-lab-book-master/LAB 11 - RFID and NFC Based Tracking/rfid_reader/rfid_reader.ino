/***************************************************************************
* Sketch Name: nfc
*
* Original Version: 07/06/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates reading and forwarding NFC/RFID data.
*   - Code taken from https://wiki.seeedstudio.com/Grove-125KHz_RFID_Reader/.
*
***************************************************************************/

// 1. Create a buffer to temporarily store data that arrives from the RFID module.
unsigned char buffer[64];  // buffer array for data received over serial port
int count = 0;             // counter for the buffer array

// ---------------------------------------------------------------------------
// SETUP
// ---------------------------------------------------------------------------
void setup()
{
  // 2. Initialize Serial1 at 9600 baud. 
  //    - On some boards (e.g., Arduino Mega, Leonardo), Serial1 is a hardware serial port.
  //    - On others, you might need a software serial library to emulate a second serial port.
  Serial1.begin(9600);

  // 3. Initialize the default serial port at 9600 baud for output to the Serial Monitor.
  //    This allows debugging or observing data on your computer.
  Serial.begin(9600);
}

// ---------------------------------------------------------------------------
// LOOP
// ---------------------------------------------------------------------------
void loop()
{
  // 4. Check if there is incoming data from the RFID module on Serial1.
  //    If available, read each byte until the buffer is full (64 bytes) or no more data remains.
  if (Serial1.available())
  {
    while (Serial1.available())
    {
      buffer[count++] = Serial1.read();  // Read one byte from RFID and store it in the buffer
      if (count == 64) break;            // Prevent buffer overflow by stopping at 64 bytes
    }

    // 5. Write the captured data to the primary Serial port so that you can
    //    see it in the Arduino Serial Monitor (e.g., for debugging or logging).
    Serial.write(buffer, count);

    // 6. Clear the contents of the buffer to avoid leftover data when new data arrives.
    clearBufferArray();  
    count = 0;  // Reset the position counter for the next round of incoming data
  }

  // 7. If there is incoming data from the Serial Monitor (PC side),
  //    forward it to the RFID module by writing it to Serial1.
  if (Serial.available())
  {
    Serial1.write(Serial.read());
  }
}

// ---------------------------------------------------------------------------
// CLEAR BUFFER ARRAY
// ---------------------------------------------------------------------------
/**
 * Function: clearBufferArray
 * --------------------------
 * Sets each element in the buffer to NULL (0), effectively wiping out any
 * previously stored data. This helps ensure we start fresh with an empty
 * buffer the next time we read from Serial1.
 */
void clearBufferArray()
{
  for (int i = 0; i < count; i++)
  {
    buffer[i] = NULL;
  }
}
