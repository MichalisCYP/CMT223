#include "bluetooth_transport.h"
#include "button_handler.h"
#include "config.h"
#include "environment_sensors.h"
#include "payload_formatter.h"

UsbSerialTransport transport;
ButtonHandler button(config::PIN_BUTTON, true, config::BUTTON_DEBOUNCE_MS,
                     config::BUTTON_LONG_PRESS_MS);

unsigned long lastTelemetrySentAtMs = 0;

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
  button.begin();

  transport.begin(config::SERIAL_BAUD);
  transport.flush();
}

void loop() {
  const unsigned long nowMs = millis();

  ButtonEvent event = button.update(nowMs);
  if (event == BUTTON_EVENT_SHORT) {
    String payload = formatButtonEventPayload("SHORT");
    transport.writeLine(payload);
  } else if (event == BUTTON_EVENT_LONG) {
    String payload = formatButtonEventPayload("LONG");
    transport.writeLine(payload);
  }

  if (nowMs - lastTelemetrySentAtMs >= config::TELEMETRY_INTERVAL_MS) {
    EnvironmentSample sample =
        readEnvironment(config::PIN_LIGHT, config::PIN_SOUND, config::PIN_PIR);
    String payload = formatTelemetryPayload(sample, button.isPressed());
    transport.writeLine(payload);
    lastTelemetrySentAtMs = nowMs;
  }

  delay(25);
}
