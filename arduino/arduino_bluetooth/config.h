#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

namespace config {

constexpr uint8_t PIN_BLUETOOTH_RX = 8;
constexpr uint8_t PIN_BLUETOOTH_TX = 9;
constexpr uint8_t PIN_PIR = 2;
constexpr uint8_t PIN_BUTTON = 3;
constexpr uint8_t PIN_LIGHT = A3;
constexpr uint8_t PIN_SOUND = A0;

constexpr unsigned long SERIAL_WAIT_TIMEOUT_MS = 3000;
constexpr unsigned long TELEMETRY_INTERVAL_MS = 1000;
constexpr unsigned long BUTTON_DEBOUNCE_MS = 50;
constexpr unsigned long BUTTON_LONG_PRESS_MS = 1200;

constexpr long SERIAL_BAUD = 9600;
constexpr long BLUETOOTH_BAUD = 9600;

}  // namespace config

#endif
