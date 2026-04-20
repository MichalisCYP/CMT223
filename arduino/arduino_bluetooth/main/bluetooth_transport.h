#ifndef BLUETOOTH_TRANSPORT_H
#define BLUETOOTH_TRANSPORT_H

#include <Arduino.h>

class UsbSerialTransport {
 public:
  UsbSerialTransport() : serial_(Serial) {}

  void begin(long baudRate) {
    // Serial is already initialized in the main sketch before transport creation
    (void)baudRate;  // Unused parameter
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
  Stream& serial_;
};

#endif
