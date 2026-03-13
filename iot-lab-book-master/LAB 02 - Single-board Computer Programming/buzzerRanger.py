#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/***************************************************************************
* Sketch Name: Lab1_code1
*
* Original Version: 04/08/2021 (by Hakan KAYAN)
* Modified From: https://github.com/DexterInd/GrovePi.git
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates how to read distance from a Grove Ultrasonic Ranger (D3)
*     on a Raspberry Pi with GrovePi, and activates a buzzer (D8) when the
*     measured distance is under a threshold (10 cm).
*
* Parameters:
*   - PIR, Light, Button, LED (listed in the header),
*     though this specific code focuses on the ultrasonic sensor and buzzer.
*
* Return:
*   - Prints the measured distance in centimeters,
*   - Activates the buzzer if the distance is < 10 cm.
***************************************************************************/
"""

import time
import sys
import grovepi

# -----------------------------------------------------------------------------
# 1. Hardware Setup
# -----------------------------------------------------------------------------
#  - The Grove Buzzer is connected to digital port D8.
#    We configure it as an OUTPUT pin to turn sound ON/OFF.
#  - The Grove Ultrasonic Ranger is connected to digital port D3.
#    We use `grovepi.ultrasonicRead()` to obtain distance in centimeters.
# -----------------------------------------------------------------------------
buzzer = 8
grovepi.pinMode(buzzer, "OUTPUT")

# -----------------------------------------------------------------------------
# 2. Configure the I2C Bus
# -----------------------------------------------------------------------------
#  - "RPI_1" indicates that we want the GrovePi to use the hardware I2C bus #1 
#    on the Raspberry Pi (typical for most Pi models).
# -----------------------------------------------------------------------------
grovepi.set_bus("RPI_1")

# -----------------------------------------------------------------------------
# 3. Assign the Ultrasonic Ranger Port
# -----------------------------------------------------------------------------
#  - The sensor is on digital port D3. 
#    We'll call `grovepi.ultrasonicRead(ultrasonic_ranger)` to get distance in cm.
# -----------------------------------------------------------------------------
ultrasonic_ranger = 3

# -----------------------------------------------------------------------------
# MAIN LOOP
# -----------------------------------------------------------------------------
#  - Continuously reads the distance, prints it, and checks if distance < 10 cm.
#    If so, the buzzer will sound for ~1 second. Otherwise, the buzzer is silent.
# -----------------------------------------------------------------------------
while True:
    try:
        # 4. Read the distance in centimeters from the ultrasonic sensor.
        distance = grovepi.ultrasonicRead(ultrasonic_ranger)

        # 5. Print the measured distance to stdout (the console).
        #    The "\r" in the string allows you to potentially overwrite the same line.
        sys.stdout.write("The distance is %d cm\r" % distance)

        # 6. If the distance is < 10 cm, turn the buzzer ON for 1 second.
        if distance < 10:
            grovepi.digitalWrite(buzzer, 1)
            time.sleep(1)
        else:
            # 7. If distance >= 10 cm, turn the buzzer OFF for 1 second.
            grovepi.digitalWrite(buzzer, 0)
            time.sleep(1)

    except KeyboardInterrupt:
        # 8. If user presses Ctrl+C, turn the buzzer OFF and break out of the loop.
        grovepi.digitalWrite(buzzer, 0)
        break

    except IOError:
        # 9. In case of I/O error (e.g., sensor not responding), print "Error" and continue.
        print("Error")
