#include "usbserial_transport.h"
#include "config.h"
#include "environment_sensors.h"
#include "payload_formatter.h"
#include <DHT.h>

UsbSerialTransport transport;
DHT dht(config::PIN_DHT, config::DHT_TYPE);

unsigned long lastTelemetrySentAtMs = 0;
bool buttonState = false;
bool prevButtonState = false;
bool button2State = false;
bool prevButton2State = false;

void setup() {
  Serial.begin(config::SERIAL_BAUD);
  unsigned long serialWaitStartMs = millis();
  while (!Serial &&
         (millis() - serialWaitStartMs < config::SERIAL_WAIT_TIMEOUT_MS)) {
    ;
  }

  pinMode(config::PIN_PIR, INPUT);
  pinMode(config::PIN_LIGHT, INPUT);
  pinMode(config::PIN_SOUND, INPUT);
  pinMode(config::PIN_BUTTON, INPUT);
  pinMode(config::PIN_BUTTON2, INPUT);
  pinMode(config::PIN_DIST, INPUT);

  dht.begin();

  transport.begin(config::SERIAL_BAUD);
  transport.flush();
}

void loop() {
  const unsigned long nowMs = millis();
  buttonState = digitalRead(config::PIN_BUTTON);
  button2State = digitalRead(config::PIN_BUTTON2);

  if (buttonState != prevButtonState) {
    prevButtonState = buttonState;
  }

  if (button2State != prevButton2State) {
    prevButton2State = button2State;
  }

  if (nowMs - lastTelemetrySentAtMs >= config::TELEMETRY_INTERVAL_MS) {
    EnvironmentSample sample = readEnvironment(
        config::PIN_LIGHT, config::PIN_SOUND, config::PIN_PIR, dht,
      config::PIN_DIST, config::DISTANCE_TIMEOUT_US);
    String payload = formatTelemetryPayload(sample, buttonState, button2State);
    transport.writeLine(payload);
    lastTelemetrySentAtMs = nowMs;
  }

  delay(100);
}
