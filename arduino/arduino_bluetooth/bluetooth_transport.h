#ifndef BLUETOOTH_TRANSPORT_H
#define BLUETOOTH_TRANSPORT_H

#include <Arduino.h>
#include <SoftwareSerial.h>

class BluetoothTransport {
 public:
  BluetoothTransport(uint8_t rxPin, uint8_t txPin)
      : serial_(rxPin, txPin) {}

  void begin(long baudRate) {
    serial_.begin(baudRate);
  }

  void setup() {
    // Send AT commands to configure the Bluetooth module
    // Set baud rate to 9600
    serial_.print("AT+BAUD4");
    delay(2000);

    // Set role to slave (S)
    serial_.print("AT+ROLES");
    delay(2000);

    // Set name
    serial_.print("AT+NAMESOORYAOMG");
    delay(2000);

    // Enable authentication
    serial_.print("AT+AUTH1");
    delay(2000);

    // Flush any residual data
    serial_.flush();
  }

  bool available() {
    return serial_.available() > 0;
  }

  char read() {
    return static_cast<char>(serial_.read());
  }

  void writeLine(const String& line) {
    serial_.println(line);
  }

  void flush() {
    serial_.flush();
  }

 private:
  SoftwareSerial serial_;
};

#endif
