#ifndef PAYLOAD_FORMATTER_H
#define PAYLOAD_FORMATTER_H

#include <Arduino.h>
#include "environment_sensors.h"

inline String formatTelemetryPayload(const EnvironmentSample& sample,
                                     bool buttonPressed) {
  String payload = "{";
  payload += "\"v\":1";
  payload += ",\"light\":";
  payload += sample.light;
  payload += ",\"sound\":";
  payload += sample.sound;
  payload += ",\"move\":";
  payload += sample.motion;
  payload += ",\"button\":";
  payload += buttonPressed ? 1 : 0;
  payload += "}";
  return payload;
}

inline String formatButtonEventPayload(const char* name) {
  String payload = "{";
  payload += "\"v\":1";
  payload += ",\"btn_event\":\"";
  payload += name;
  payload += "\"}";
  return payload;
}

#endif
