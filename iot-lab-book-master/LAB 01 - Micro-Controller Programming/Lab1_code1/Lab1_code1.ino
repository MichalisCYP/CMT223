/***************************************************************************
* Sketch Name: Lab1_code1
*
* Latest Version: 14/11/2020 (by Hakan KAYAN)
* Updated Version: 24/12/2024 (by Charith PERERA)
*
* Note: This code demonstrates how to read a button state, detect motion using
*       a PIR sensor, measure light levels via an analog pin, and control an LED.
*       In an IoT setting, these readings can be sent to a cloud server or used 
*       to trigger actions in real time.
***************************************************************************/

// 1. Define the digital pin connected to the PIR motion sensor.
#define PIR_MOTION_SENSOR 2  

// 2. Assign the pin numbers for the LED and the button.
const int ledPin = 3;     // the number of the LED pin (D3)
const int buttonPin = 4;  // the number of the pushbutton pin (D4)

// 3. Declare variables to store sensor states and the LED state.
int buttonState;          // the state of the button (HIGH or LOW)
int ledState = LOW;       // the current state of the LED (HIGH or LOW)
int MotionState;          // the state of the Motion SENSOR (PIR), HIGH or LOW

void setup() {
  // 4. Configure the pins for the button, PIR sensor, and LED.
  //    - buttonPin: input (button)
  //    - PIR_MOTION_SENSOR: input (motion detection)
  //    - ledPin: output (LED)
  pinMode(buttonPin, INPUT);
  pinMode(PIR_MOTION_SENSOR, INPUT);
  pinMode(ledPin, OUTPUT);
  
  // 5. Initialize the LED to the default state defined in ledState.
  digitalWrite(ledPin, ledState);

  // 6. Begin serial communication at 9600 bits per second.
  //    This allows you to print sensor values or states to the Serial Monitor.
  Serial.begin(9600);
}

void loop() {
  // 7. Read the current state of the button and the motion sensor.
  //    - buttonState will be HIGH if pressed, LOW if not.
  //    - MotionState will be HIGH if motion is detected, LOW otherwise.
  buttonState = digitalRead(buttonPin);
  MotionState = digitalRead(PIR_MOTION_SENSOR);

  // 8. Read the light level from analog pin A3.
  //    The returned value ranges from 0 (darkest) to 1023 (brightest).
  int light = analogRead(A3);

  // 9. Map the light sensor value (0–800 range) to a simpler 0–10 scale.
  //    For example:
  //        0   -> 0 (darkest)
  //        800 -> 10 (lightest)
  //    If your sensor can go beyond 800, adjust accordingly.
  light = map(light, 0, 800, 0, 10);

  // 10. If the button is pressed (i.e., buttonState is HIGH), execute the LED fade.
  //     Then print "Dark" or "Light" depending on the light sensor reading.
  if (buttonState == HIGH) {
    // 10a. Fade-in effect: gradually increase the LED brightness 
    //      from 0 (off) to 255 (fully on).
    for (int i = 0; i <= 255; i++) {
      analogWrite(ledPin, i);  // PWM value for LED brightness
      delay(10);               // short delay for smooth fading
    }

    // 10b. Check the light level. If the mapped value is <= 5, it is relatively dark.
    if (light <= 5) {
      Serial.println("Dark");
    } else {
      Serial.println("Light");
    }
  }

  // 11. If the button is not pressed (buttonState is LOW), check for motion.
  if (buttonState == LOW) {
    // 11a. If the PIR sensor detects motion (MotionState == HIGH),
    //      print "Movement" and wait for 3 seconds.
    if (MotionState == HIGH) {
      Serial.println("Movement");
      delay(3000);
    }
    // 11b. Otherwise, if no movement is detected, print "Watching" and wait for 3 seconds.
    else {
      Serial.println("Watching");
      delay(3000);
    }
  }
}
