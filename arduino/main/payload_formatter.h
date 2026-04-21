#ifndef PAYLOAD_FORMATTER_H
#define PAYLOAD_FORMATTER_H

#include <Arduino.h>
#include "environment_sensors.h"

inline String formatTelemetryPayload(const EnvironmentSample& sample,
                                     bool buttonState) {
  String payload = "{";
  payload += "\"v\":1";
  payload += ",\"light\":";
  payload += sample.light;
  payload += ",\"sound\":";
  payload += sample.sound;
  payload += ",\"move\":";
  payload += sample.motion;
  payload += ",\"button\":";
  payload += buttonState ? 1 : 0;
  payload += "}";
  return payload;
}

#endif
