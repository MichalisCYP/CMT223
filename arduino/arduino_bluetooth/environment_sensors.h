#ifndef ENVIRONMENT_SENSORS_H
#define ENVIRONMENT_SENSORS_H

#include <Arduino.h>

struct EnvironmentSample {
  int light;
  int sound;
  int motion;
};

inline EnvironmentSample readEnvironment(uint8_t lightPin, uint8_t soundPin,
                                         uint8_t pirPin) {
  EnvironmentSample sample;
  sample.light = analogRead(lightPin);
  sample.sound = analogRead(soundPin);
  sample.motion = digitalRead(pirPin);
  return sample;
}

#endif
