#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/***************************************************************************
* Sketch Name: Lab2_code3
*
* Original Version: 13/02/2024 (by Yasar Majib)
* Modified From: https://github.com/DexterInd/GrovePi.git
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates how to read temperature and humidity from an I2C-based DHT 
*     sensor (black-colored, address 0x38) connected to a Raspberry Pi.
*   - Uses an LCD with RGB backlight to display the readings, via two I2C 
*     addresses: one for text (0x3e) and one for the backlight (default 0x62).
*   - Outputs the readings in JSON format (e.g., {"temp": 25.3, "humidity": 60.2}).
*
* Parameters:
*   - Temperature & Humidity Sensors (black DHT, I2C, address = 0x38)
*   - Grove-LCD RGB Backlight (I2C addresses 0x62 for color, 0x3e for text)
*
* Return:
*   - Continuously updates the LCD with temperature (°C) & humidity (%)
*   - Prints the same readings in JSON to stdout
***************************************************************************/
"""

import time
import smbus
import sys
import os
import math
import json
import grovepi

# -----------------------------------------------------------------------------
# 1. Determine I2C Bus and Device Addresses
# -----------------------------------------------------------------------------
#  - The black DHT sensor is read at address 0x38. 
#  - The Grove LCD can have different I2C addresses depending on its version.
#    In this script, we use 0x62 for the RGB backlight and 0x3e for text commands.
# -----------------------------------------------------------------------------
sensor = 0x38  # I2C address for the black DHT sensor

# This device may have:
#   - For older LCD version 4.0, typical addresses: 0x62 (RGB), 0x3e (text).
#   - For LCD version 5.0, addresses might be 0x30 and 0x3e.
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

# Check the platform and revision to assign the correct I2C bus on the Pi.
if sys.platform == 'uwp':
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
# 2. Grove LCD Control Functions
# -----------------------------------------------------------------------------
def setRGB(r, g, b):
    """
    setRGB(r, g, b):
      - Controls the Grove LCD's backlight color by writing the desired (r, g, b)
        values to the I2C registers at DISPLAY_RGB_ADDR.
      - r, g, b each range from 0..255, providing a wide color palette.
    """
    # Initialize relevant registers for color control
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0, 0)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 1, 0)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x08, 0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 4, r)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 3, g)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 2, b)

def textCommand(cmd):
    """
    textCommand(cmd):
      - Sends a command byte (cmd) to the LCD's text command register 
        (DISPLAY_TEXT_ADDR, register 0x80).
      - Used internally by setText() for clearing the screen, setting cursor, etc.
    """
    bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x80, cmd)

def setText(text):
    """
    setText(text):
      - Clears the display, sets it for 2-line mode, and writes 
        up to 32 characters (16 chars per line).
      - If '\n' or 16 chars are reached, moves to the second line. 
      - Additional characters beyond two lines are ignored.
    """
    # Clear display (command 0x01)
    textCommand(0x01)
    time.sleep(0.05)
    # Display on (0x08), no cursor (0x04)
    textCommand(0x08 | 0x04)
    # 2-line mode (0x28)
    textCommand(0x28)
    time.sleep(0.05)

    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            # Move to next line if newline or 16 chars have been written
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)  # command to move cursor to second line
            if c == '\n':
                continue
        count += 1
        # Write ASCII of character to display data register (0x40)
        bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x40, ord(c))


# -----------------------------------------------------------------------------
# MAIN SCRIPT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Set an initial color for the LCD backlight
    setRGB(5, 250, 0)  # Example: near-green color
    time.sleep(2)

    # 2. Check if the DHT sensor is initializing properly
    #    read one byte from register 0x71 and verify it
    data = bus.read_i2c_block_data(sensor, 0x71, 1)
    if (data[0] | 0x08) == 0:
        print('Initialization error')
        os._exit(1)

    # 3. Continuously read & display temperature/humidity
    while True:
        try:
            # 3a. Instruct sensor (0xac) with parameters [0x33,0x00] to measure T/H
            bus.write_i2c_block_data(sensor, 0xac, [0x33, 0x00])
            time.sleep(0.1)  # small wait for data acquisition

            # 3b. Read 7 bytes from register 0x71, which contain raw T/H
            data = bus.read_i2c_block_data(sensor, 0x71, 7)

            # 3c. Extract raw temperature from indexes 3..5
            Traw = ((data[3] & 0xf) << 16) + (data[4] << 8) + data[5]
            temp = 200 * float(Traw) / (2 ** 20) - 50

            # 3d. Extract raw humidity from indexes 1..3
            Hraw = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)
            humidity = 100 * float(Hraw) / (2 ** 20)

            # 3e. Sleep 3 seconds between cycles (per sensor recommendations)
            time.sleep(3)

            # 3f. Convert to JSON with one decimal place for each value
            x = json.dumps({
                'temp': round(temp, 1),
                'humidity': round(humidity, 1)
            })

            # 3g. Validate readings: if neither temperature nor humidity are NaN
            if not math.isnan(temp) and not math.isnan(humidity):
                # Write this JSON string to the LCD (shows up to 32 chars)
                setText(x)
                time.sleep(0.1)
                # Also print to stdout so it appears in logs or the console
                sys.stdout.write(x)

        except KeyboardInterrupt:
            # 4. Gracefully exit if the user presses Ctrl+C
            print("Terminated.")
            os._exit(0)
