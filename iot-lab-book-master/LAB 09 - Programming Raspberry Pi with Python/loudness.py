#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/***************************************************************************
* Sketch Name: loudnessSensorTest.py
*
* Original Version: 07/06/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates how to read analog values from a Grove Loudness Sensor
*     connected to analog port A2 on the Grove base shield.
*   - Continuously prints the measured sound level to the console.
*   - Serves as a simple introduction to analog sensor reading in Python 
*     with the GrovePi library.
*
***************************************************************************/
"""

import time
import grovepi

# -----------------------------------------------------------------------------
# 1. Hardware Setup:
#    - The Grove Loudness Sensor is connected to the analog port A2.
#    - The port pins are typically labeled SIG (signal), NC (not connected), 
#      VCC (power), and GND (ground).
# -----------------------------------------------------------------------------
loudness_sensor = 2  # A2 corresponds to index 2 in GrovePi

# -----------------------------------------------------------------------------
# MAIN LOOP
# -----------------------------------------------------------------------------
while True:
    try:
        # 2. Read the loudness sensor value from the analog pin A2.
        #    - The returned value typically ranges from 0 (no sound) 
        #      to around 1023 (very loud).
        sensor_value = grovepi.analogRead(loudness_sensor)

        # 3. Print the sensor value to the console for monitoring or debugging.
        #    You can adjust how frequently it's read by modifying time.sleep().
        print(f"Sensor Value = {sensor_value}")

        # 4. Delay for 0.5 seconds before reading again.
        time.sleep(0.5)

    except IOError:
        # 5. If an I/O error occurs (e.g., communication issue with GrovePi), 
        #    print an error message and continue the loop instead of crashing.
        print("Error")
