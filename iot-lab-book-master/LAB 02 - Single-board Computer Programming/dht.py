#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/***************************************************************************
* Sketch Name: Lab1_code1
*
* Original Version: 07/09/2021 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates how to read temperature and humidity values from a DHT sensor 
*     (blue variant) using the GrovePi library on an Arduino-compatible board.
*   - Continuously prints the readings in JSON format to the console.
*   - Checks for invalid (NaN) data and outputs an appropriate message if no valid data.
*
* Parameters:
*   - PIR, Light, Button, LED (listed in the header),
*     though this specific code focuses on reading from the DHT sensor on D4.
*
* Return:
*   - Temperature (°C), Humidity (%), printed as JSON when valid
***************************************************************************/
"""

import time
import sys
import os
import math
import json
import grovepi

# -----------------------------------------------------------------------------
# 1. DHT Sensor Setup
# -----------------------------------------------------------------------------
#  - The DHT sensor is attached to digital port D4 on the Grove Base Shield.
#  - 'blue = 0' refers to the "blue" version of the Grove DHT (often DHT11).
# -----------------------------------------------------------------------------
sensor = 4  # Digital port D4 for the DHT sensor
blue = 0    # 0 => Grove 'blue' DHT sensor (DHT11)
white = 1   # 1 => 'white' sensor (DHT22), not used here

# -----------------------------------------------------------------------------
# MAIN LOOP
# -----------------------------------------------------------------------------
#  - Repeatedly read temperature and humidity from the DHT sensor, 
#    then print them in JSON format if valid. 
#  - Sleeps 3 seconds between reads to avoid over-polling the sensor.
# -----------------------------------------------------------------------------
while True:
    try:
        # 2. Read from the DHT sensor (blue variant).
        #    grovepi.dht(port, type) returns [temp, humidity].
        [temp, humidity] = grovepi.dht(sensor, blue)

        # 3. Sleep briefly to avoid saturating the sensor with requests.
        time.sleep(3)

        # 4. Create a JSON string from the readings, e.g. {"temperature":24.2,"humidity":58.1}.
        x = json.dumps({'temperature': temp, 'humidity': humidity})

        # 5. Check for valid (non-NaN) data before printing. 
        #    If either temp or humidity is NaN, skip or print a placeholder message.
        if not math.isnan(temp) and not math.isnan(humidity):
            # Use 'print(..., end="", flush=True)' to print on the same line 
            # and flush output immediately, if desired.
            print(x, end='', flush=True)
        else:
            print("No data.", flush=True)

    except KeyboardInterrupt:
        # 6. Gracefully exit if the user presses Ctrl+C. 
        #    'os._exit(0)' ensures immediate termination without tracebacks.
        print("Terminated.")
        os._exit(0)
