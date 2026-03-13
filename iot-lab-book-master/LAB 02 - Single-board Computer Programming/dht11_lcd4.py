#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/***************************************************************************
* Sketch Name: Lab2_code1
*
* Original Version: 13/02/2024 (by Yasar Majib)
* Modified From: https://github.com/DexterInd/GrovePi.git
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates how to read temperature and humidity from a DHT sensor 
*     (blue variant) connected to digital port D4 on a Raspberry Pi, using the
*     grovepi library.
*   - Displays these readings on a Grove LCD with an RGB backlight.
*   - Outputs the sensor data in JSON format (e.g., {"temp": 25.2, "humidity": 48.1}) 
*     to the console.
*
* Parameters:
*   - Temperature & Humidity Sensors (blue-type DHT) on digital port 4
*   - Grove-LCD RGB Backlight (I2C addresses: 0x62 for color, 0x3e for text)
*
* Return:
*   - Continuously updates the LCD with temperature (°C) & humidity (%),
*   - Prints the same sensor data as JSON to the console.
***************************************************************************/
"""

import time
import sys
import os
import math
import json
import grovepi

# -----------------------------------------------------------------------------
# 1. Define the DHT Sensor Port and Type
# -----------------------------------------------------------------------------
#  - The 'blue' sensor typically corresponds to DHT11, which can read less accurate
#    but faster measurements. If you had a 'white' sensor, it might be DHT22.
#  - Here, 'sensor = 4' means the DHT sensor is on digital port D4.
# -----------------------------------------------------------------------------
sensor = 4
blue = 0  # 0 => "blue" DHT sensor (DHT11)

# -----------------------------------------------------------------------------
# 2. Determine I2C Bus for the Grove LCD
# -----------------------------------------------------------------------------
#  - On modern Raspberry Pi boards (Rev 2 or 3), we use I2C bus #1.
#  - The addresses for the LCD are 0x62 (RGB) and 0x3e (text).
#    If your LCD is a different revision, you may need 0x30 for RGB.
# -----------------------------------------------------------------------------
if sys.platform == 'uwp':
    # Windows IoT scenario
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)

# -----------------------------------------------------------------------------
# 3. I2C Addresses for the Grove LCD
# -----------------------------------------------------------------------------
DISPLAY_RGB_ADDR = 0x62   # Controls LCD backlight color
DISPLAY_TEXT_ADDR = 0x3e  # Controls LCD text display

# -----------------------------------------------------------------------------
# 4. Grove LCD RGB Control Functions
# -----------------------------------------------------------------------------
def setRGB(r, g, b):
    """
    setRGB(r, g, b):
      - Controls the backlight color of the Grove LCD.
      - r, g, b are each 0..255. For example, setRGB(255,0,0) => bright red.
    """
    # Configure relevant registers to enable color mixing
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0, 0)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 1, 0)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x08, 0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 4, r)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 3, g)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 2, b)

def textCommand(cmd):
    """
    textCommand(cmd):
      - Issues a command byte (cmd) to the LCD’s control register (0x80).
      - Typically used internally by setText() to clear the display, 
        set line modes, etc.
    """
    bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x80, cmd)

def setText(text):
    """
    setText(text):
      - Clears the display, configures it for 2-line mode, and writes 
        up to 32 characters (16 per line).
      - If it reaches 16 characters or encounters '\n', it moves to 
        the second line. Any text beyond two lines is not shown.
    """
    # Clear display
    textCommand(0x01)
    time.sleep(0.05)
    # Display ON (0x08), no cursor => (0x04)
    textCommand(0x08 | 0x04)
    # 2-line display mode (0x28)
    textCommand(0x28)
    time.sleep(0.05)

    count = 0
    row = 0
    for c in text:
        # Check for newline or 16 characters
        if c == '\n' or count == 16:
            count = 0
            row += 1
            # Stop if we're already on line 2 (only 2 lines total)
            if row == 2:
                break
            # Command 0xc0 => move cursor to start of second line
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        # Write the character's ASCII value to the LCD data register (0x40)
        bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x40, ord(c))

# -----------------------------------------------------------------------------
# 5. Main Script
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    # 5a. Set the LCD backlight to a sample color (r=5, g=250, b=0 => near green).
    setRGB(5, 250, 0)
    time.sleep(2)

    # 5b. Loop indefinitely to read sensor data and display it.
    while True:
        try:
            # 5c. Use grovepi.dht() to read the DHT sensor:
            #     - 'temp' in degrees Celsius
            #     - 'humidity' as a percentage
            [temp, humidity] = grovepi.dht(sensor, blue)

            # 5d. Wait 3 seconds between reads to allow stable DHT measurements.
            time.sleep(3)

            # 5e. Build a JSON string with the sensor values, e.g., {"temp":23.5, "humidity":55.7}.
            x = json.dumps({'temp': temp, 'humidity': humidity})

            # 5f. Check if both temp and humidity are valid (not NaN).
            if not math.isnan(temp) and not math.isnan(humidity):
                # 5g. Display the JSON string on the LCD. 
                #     The LCD can only show up to 32 chars (2 lines x 16 chars).
                setText(x)
                time.sleep(0.1)

                # 5h. Print the same data to stdout (e.g., for logging).
                sys.stdout.write(x)

        except KeyboardInterrupt:
            # 5i. If user presses Ctrl+C, print a termination message and exit gracefully.
            print("Terminated.")
            os._exit(0)
