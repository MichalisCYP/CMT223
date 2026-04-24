#ifndef ENVIRONMENT_SENSORS_H
#define ENVIRONMENT_SENSORS_H

#include <Arduino.h>
#include <DHT.h>

struct EnvironmentSample {
  int light;
  int sound;
  int motion;
  float temperature;
  float humidity;
  int distanceCm;
};

inline int readGroveUltrasonicDistanceCm(uint8_t signalPin, unsigned long timeoutUs) {
  pinMode(signalPin, OUTPUT);
  digitalWrite(signalPin, LOW);
  delayMicroseconds(2);
  digitalWrite(signalPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(signalPin, LOW);

  pinMode(signalPin, INPUT);
  const unsigned long durationUs = pulseIn(signalPin, HIGH, timeoutUs);
  if (durationUs == 0) {
    return -1;
  }

  return static_cast<int>(durationUs / 58UL);
}

inline EnvironmentSample readEnvironment(uint8_t lightPin, uint8_t soundPin,
                                         uint8_t pirPin, DHT& dht,
                                         uint8_t distancePin,
                                         unsigned long distanceTimeoutUs) {
  EnvironmentSample sample;
  sample.light = analogRead(lightPin);
  sample.sound = analogRead(soundPin);
  sample.motion = digitalRead(pirPin);
  sample.temperature = dht.readTemperature();
  sample.humidity = dht.readHumidity();
  sample.distanceCm = readGroveUltrasonicDistanceCm(distancePin, distanceTimeoutUs);

  if (isnan(sample.temperature)) {
    sample.temperature = 0.0f;
  }
  if (isnan(sample.humidity)) {
    sample.humidity = 0.0f;
  }

  return sample;
}

#endif
