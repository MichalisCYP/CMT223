#ifndef BUTTON_HANDLER_H
#define BUTTON_HANDLER_H

#include <Arduino.h>

enum ButtonEvent {
  BUTTON_EVENT_NONE,
  BUTTON_EVENT_SHORT,
  BUTTON_EVENT_LONG
};

class ButtonHandler {
 public:
  ButtonHandler(uint8_t pin, bool activeLow, unsigned long debounceMs,
                unsigned long longPressMs)
      : pin_(pin),
        activeLow_(activeLow),
        debounceMs_(debounceMs),
        longPressMs_(longPressMs),
        stableState_(false),
        lastRawState_(false),
        lastDebounceMs_(0),
        pressStartMs_(0),
        longEventSent_(false) {}

  void begin() {
    if (activeLow_) {
      pinMode(pin_, INPUT_PULLUP);
    } else {
      pinMode(pin_, INPUT);
    }

    bool raw = rawPressed();
    stableState_ = raw;
    lastRawState_ = raw;
    lastDebounceMs_ = millis();
  }

  ButtonEvent update(unsigned long nowMs) {
    bool raw = rawPressed();
    if (raw != lastRawState_) {
      lastDebounceMs_ = nowMs;
      lastRawState_ = raw;
    }

    if (nowMs - lastDebounceMs_ < debounceMs_) {
      return BUTTON_EVENT_NONE;
    }

    if (stableState_ != raw) {
      stableState_ = raw;
      if (stableState_) {
        pressStartMs_ = nowMs;
        longEventSent_ = false;
      } else {
        if (!longEventSent_ && pressStartMs_ > 0) {
          return BUTTON_EVENT_SHORT;
        }
      }
    }

    if (stableState_ && !longEventSent_ && pressStartMs_ > 0 &&
        (nowMs - pressStartMs_ >= longPressMs_)) {
      longEventSent_ = true;
      return BUTTON_EVENT_LONG;
    }

    return BUTTON_EVENT_NONE;
  }

  bool isPressed() const {
    return stableState_;
  }

 private:
  bool rawPressed() const {
    int value = digitalRead(pin_);
    return activeLow_ ? (value == LOW) : (value == HIGH);
  }

  uint8_t pin_;
  bool activeLow_;
  unsigned long debounceMs_;
  unsigned long longPressMs_;
  bool stableState_;
  bool lastRawState_;
  unsigned long lastDebounceMs_;
  unsigned long pressStartMs_;
  bool longEventSent_;
};

#endif
