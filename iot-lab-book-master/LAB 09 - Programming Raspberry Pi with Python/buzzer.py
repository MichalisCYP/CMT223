#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/***************************************************************************
* Sketch Name:buzzer.py
*
* Original Version: 07/06/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates toggling a Grove Buzzer (connected to D8 on the Grove Pi)
*     on and off in a 1-second cycle.
*   - Prints status messages ("start", "stop") to the console to indicate
*     when the buzzer is active.
*   - Provides a basic example of digital output for sound in IoT applications.
***************************************************************************/
"""

import time
import grovepi

# 1. Define the digital port where the Grove Buzzer is connected (D8).
buzzer = 8

# 2. Set the pin mode of D8 to OUTPUT to drive the buzzer.
grovepi.pinMode(buzzer, "OUTPUT")

# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
while True:
    try:
        # 3. Turn the buzzer ON and print a status message.
        grovepi.digitalWrite(buzzer, 1)
        print("start")
        #    Keep the buzzer ON for 1 second.
        time.sleep(1)

        # 4. Turn the buzzer OFF and print a status message.
        grovepi.digitalWrite(buzzer, 0)
        print("stop")
        #    Keep the buzzer OFF for 1 second.
        time.sleep(1)

    except KeyboardInterrupt:
        # 5. If the user presses Ctrl+C, safely turn the buzzer off before exiting.
        grovepi.digitalWrite(buzzer, 0)
        break

    except IOError:
        # 6. If an I/O error occurs (e.g., sensor not detected),
        #    print an error message and continue the loop.
        print("Error")
