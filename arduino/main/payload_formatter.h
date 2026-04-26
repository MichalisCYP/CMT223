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
  payload += ",\"temp\":";
  payload += sample.temperature;
  payload += ",\"hum\":";
  payload += sample.humidity;
  payload += ",\"distance_cm\":";
  payload += sample.distanceCm;
  payload += ",\"button\":";
  payload += buttonState ? 0 : 1;
  payload += "}";
  return payload;
}

#endif
