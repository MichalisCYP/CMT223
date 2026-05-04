#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

namespace config {

constexpr uint8_t PIN_PIR = 2;    // Grove PIR sensor signal
constexpr uint8_t PIN_LIGHT = A3;  // Grove light sensor analog output
constexpr uint8_t PIN_SOUND = A0;  // Grove sound sensor analog output
constexpr uint8_t PIN_BUTTON = 4;   // Grove button signal
constexpr uint8_t PIN_BUTTON2 = 8;  // Second button on D8
constexpr uint8_t PIN_DHT = 5;     // Grove DHT sensor signal
constexpr uint8_t PIN_DIST = 6;    // Grove ultrasonic ranger signal

constexpr unsigned long SERIAL_WAIT_TIMEOUT_MS = 3000;
constexpr unsigned long TELEMETRY_INTERVAL_MS = 2000;
constexpr unsigned long DISTANCE_TIMEOUT_US = 30000;

constexpr long SERIAL_BAUD = 9600;
constexpr uint8_t DHT_TYPE = 11;  // Grove DHT11 module

}  // namespace config

#endif
