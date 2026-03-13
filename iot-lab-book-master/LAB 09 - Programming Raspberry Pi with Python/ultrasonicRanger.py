#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/***************************************************************************
* Sketch Name: ultrasonicRangerTest.py
*
* Original Version: 07/06/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates how to read distance measurements from a Grove Ultrasonic
*     Ranger connected to digital port D4.
*   - Uses grovepi.set_bus("RPI_1") to configure the I2C bus on a Raspberry Pi.
*   - Continuously prints the detected distance (in centimeters) to the console.
*
***************************************************************************/
"""

import grovepi
import time

# -----------------------------------------------------------------------------
# 1. I2C Bus Configuration (for Raspberry Pi):
#    - By default, GrovePi attempts to use the RPI_1 bus. Here we explicitly set
#      grovepi.set_bus("RPI_1") to ensure it uses the hardware I2C bus on the Pi.
# -----------------------------------------------------------------------------
grovepi.set_bus("RPI_1")

# -----------------------------------------------------------------------------
# 2. Hardware Setup:
#    - The Grove Ultrasonic Ranger is connected to digital port D4 on the Grove
#      Base Shield (SIG, NC, VCC, GND).
#    - This sensor sends out an ultrasonic pulse and measures the time for the
#      echo to return, calculating distance in centimeters.
# -----------------------------------------------------------------------------
ultrasonic_ranger = 4  # D4 port index

# -----------------------------------------------------------------------------
# MAIN LOOP
# -----------------------------------------------------------------------------
while True:
    try:
        # 3. Read the distance from the ultrasonic sensor in centimeters.
        #    - grovepi.ultrasonicRead(pin) returns an integer typically between
        #      a few centimeters (minimum range) up to around 400+ cm depending
        #      on the sensor’s specifications and environment.
        distance_cm = grovepi.ultrasonicRead(ultrasonic_ranger)

        # 4. Print the distance to the console for monitoring or debugging.
        print(distance_cm)

    except Exception as e:
        # 5. If there’s an unexpected error (e.g., I2C communication failure),
        #    print an error message and continue the loop.
        print("Error: {}".format(e))

    # 6. Short delay to avoid overwhelming the I2C bus with constant read requests.
    #    Adjust this based on how frequently you need distance updates.
    time.sleep(0.1)
