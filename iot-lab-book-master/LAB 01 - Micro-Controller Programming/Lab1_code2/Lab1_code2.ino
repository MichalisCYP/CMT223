/***************************************************************************
* Sketch Name: Lab1_code2
*
* Original Version: 14/11/2020 (by Hakan KAYAN)
* Updated Version: 24/12/2024 (by Charith PERERA)
*
* Note: This code demonstrates how to control a servo based on a button input.
*       In an IoT context, the button press could be replaced or augmented by 
*       sensor data (e.g., PIR sensor, light sensor) to automate actions.
***************************************************************************/

// 1. Include the Servo library, which contains functions to control servo motors.
#include <Servo.h>  

// 2. Define the digital pin to which the button is connected.
//    In many IoT applications, a push button can manually trigger an event 
//    (e.g., turning on lights, opening doors, etc.).
const int buttonPin = 4;

// 3. Declare a variable to store the button's state (HIGH or LOW).
int buttonState;

// 4. Create a Servo object named 'myservo'. We will use the methods inside
//    this object to control the position (angle) of the servo motor.
Servo myservo;

// 5. This variable will store the servo position (in degrees).
//    Even though we are not using 'pos' directly in the loop here, it is 
//    commonly used for incremental or sweeping movements.
int pos = 0;

void setup() {
  // 6. Attach the servo object to digital pin 5. The servo library 
  //    will internally handle the timing to position the servo.
  myservo.attach(5);

  // 7. It is best practice to specify the pin mode for the button.
  //    If your button is wired so that pressing it reads HIGH, you should 
  //    set the pin to INPUT or INPUT_PULLDOWN (depending on your board).
  //    If you have a pull-up resistor, use INPUT_PULLUP. For simplicity, 
  //    we assume you have an external pull-down resistor.
  pinMode(buttonPin, INPUT);
}

void loop() {
  // 8. Read the current state of the button (HIGH or LOW).
  buttonState = digitalRead(buttonPin);

  // 9. If the button is pressed (i.e., reads HIGH), rotate the servo to 180°.
  //    This simulates an action triggered by the button in an IoT scenario, 
  //    such as opening a lock or pointing a sensor in a certain direction.
  if (buttonState == HIGH) {
    myservo.write(180);    // Move servo to 180 degrees
    delay(15);             // Short delay to give servo time to reach position
  } 
  // 10. Otherwise (button not pressed), rotate the servo to 0°.
  else {
    myservo.write(0);      // Move servo back to 0 degrees
    // No delay needed if you want it to respond quickly 
    // to the next button press
  }
}
