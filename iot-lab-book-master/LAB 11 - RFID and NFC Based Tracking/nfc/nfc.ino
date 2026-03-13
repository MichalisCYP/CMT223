/***************************************************************************
* Sketch Name: nfc
*
* Original Version: 25/05/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Note: 
*   - This code demonstrates how to use a Grove NFC/RFID module (PN532)
*     to detect NFC tags, write a message to them, and read/print the tag's
*     UID to both the Serial Monitor and an LCD display.
*   - An LED is toggled to indicate when a tag is present.
***************************************************************************/

// 1. Include the libraries needed for NFC communication and the Grove LCD.
#include <NfcAdapter.h>                     // Provides the NfcAdapter class for reading/writing tags
#include <PN532/PN532_HSU/PN532_HSU.h>      // Provides PN532-specific methods for serial communication
#include <rgb_lcd.h>                        // Library for controlling the RGB backlight LCD

// 2. Create a PN532 HSU (High Speed UART) object using Serial1 as the communication interface.
//    Note: Some Arduino boards have multiple hardware serial ports. Others may require a
//    software serial library. Check your board’s specifications for Serial1 availability.
PN532_HSU pn532hsu(Serial1);

// 3. Create an NFC adapter object that uses the PN532 HSU interface to interact with NFC tags.
NfcAdapter nfc(pn532hsu);

// 4. Create an rgb_lcd object for a 16x2 or compatible Grove LCD with adjustable RGB backlight.
rgb_lcd lcd;

// 5. Define the digital pin number for an LED, which will be used as a visual indicator.
#define LED 4

void setup() {
  // 6. Initialize the LCD with 16 columns and 2 rows. This matches the
  //    standard size of the Grove RGB LCD.
  lcd.begin(16, 2);
  
  // 7. Begin serial communication with the computer at 9600 baud. 
  //    This allows sending messages (e.g., debug info) to the Serial Monitor.
  Serial.begin(9600);

  // 8. Some boards require waiting for Serial to be ready; this loop ensures
  //    the port is available before proceeding (especially on some ARM-based boards).
  while(!Serial);

  // 9. Print an initial setup message to the Serial Monitor, indicating the NFC reader is starting.
  Serial.println("NDEF Reader");

  // 10. Configure the LED pin as an OUTPUT, so it can be driven HIGH or LOW to turn the LED on/off.
  pinMode(LED, OUTPUT);

  // 11. Initialize the NFC hardware by calling nfc.begin().
  //     This sets up the PN532 module for communication and prepares it to detect NFC tags.
  nfc.begin();
}

void loop() {
  // 12. Print a status message to the Serial Monitor indicating that the system 
  //     is scanning for an NFC tag. This message repeats each loop iteration.
  Serial.println("Scanning for an NFC tag...");

  // 13. Check if an NFC tag is present within range using nfc.tagPresent().
  //     This method returns true if a valid tag is detected.
  if (nfc.tagPresent()) {
    // 13a. When a tag is detected, print confirmation to the Serial Monitor.
    Serial.println("NFC TAG FOUND");

    // 13b. Turn ON the LED to provide a visual cue that a tag is close to the reader.
    digitalWrite(LED, HIGH);

    // 14. Create an NdefMessage object to write a simple text or URI record to the NFC tag.
    //     Here, we add a URI record containing "Hello World". 
    //     Feel free to modify the text to another URL or message.
    NdefMessage message = NdefMessage();
    message.addUriRecord("Hello World");

    // 15. Attempt to write this new message to the NFC tag using nfc.write().
    bool success = nfc.write(message);
    
    // 15a. If the write operation was successful, print a confirmation.
    //      Otherwise, notify the user that the write operation failed.
    if (success) {
      Serial.println("Write succeeded.");
    } else {
      // NOTE: The original code had a capitalization error ("SERIAL.println").
      //       Ensuring consistency here as "Serial.println".
      Serial.println("Write failed.");
    }

    // 16. Use nfc.read() to read the contents of the tag after the write attempt,
    //     creating an NfcTag object with the tag’s information.
    NfcTag tag = nfc.read();

    // 17. Extract the UID (Unique Identifier) from the tag. This value is helpful
    //     for identifying each tag uniquely.
    String UID = tag.getUidString();

    // 17a. Split the UID string into two halves. This is simply a formatting choice
    //      for displaying the UID on two lines of the LCD if the UID is lengthy.
    String firstHalf = UID.substring(0, UID.length() / 2);
    String secondHalf = UID.substring(UID.length() / 2);

    // 18. Clear the LCD screen to remove any previous text.
    lcd.clear();

    // 18a. Move the cursor to the first row (index 0) and print "UID: " plus the first half.
    lcd.setCursor(0, 0);
    lcd.print("UID: ");
    lcd.print(firstHalf);

    // 18b. Move to the second row (index 1) and print the second half.
    lcd.setCursor(0, 1);
    lcd.print(secondHalf);

    // 19. The print() method of the NfcTag object displays additional information 
    //     about the tag via the Serial Monitor (e.g., tag type, size, NDEF records).
    tag.print();
  }

  // 20. Add a brief 500ms delay between scans to avoid printing too many messages
  //     in quick succession. This also provides time for the LED to remain ON briefly.
  delay(500);

  // 20a. Turn the LED OFF after the brief delay, preparing for the next scan cycle.
  digitalWrite(LED, LOW);
}
