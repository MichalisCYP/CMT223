#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/***************************************************************************
* Sketch Name: Lab2_code4
*
* Original Version: 13/02/2024 (by Yasar Majib)
* Modified From: https://github.com/DexterInd/GrovePi.git
* Updated Version: 18/02/2025 (by Ewan CROWLE)
*
* Description:
*   - Demonstrates reading temperature and humidity from an I2C DHT sensor
*     at address 0x38 on a Raspberry Pi.
*   - Displays the rounded values on a Grove-LCD with RGB backlight.
*   - Uses RPi.GPIO, smbus, and grovepi libraries for sensor I/O and 
*     LCD control, along with JSON formatting.
*
* Parameters:
*   - Temperature & Humidity Sensors (black DHT, I2C, address=0x38)
*   - Grove-LCD RGB Backlight (display text & set backlight color)
*
* Return:
*   - Continuously updates LCD with temperature (°C) & humidity (%)
***************************************************************************/
"""

import time
import smbus
import sys
import os
import math
import json
import grovepi
import RPi.GPIO as GPIO

# -----------------------------------------------------------------------------
# 1. Hardware Addresses and Bus Setup
# -----------------------------------------------------------------------------
#  - This black-colored DHT sensor is an I2C module typically found at 0x38.
#  - The Grove-LCD uses two addresses: 0x30 for RGB control (in this revision),
#    and 0x3e for text display commands.
# -----------------------------------------------------------------------------
sensor = 0x38              # I2C address of the black DHT sensor
DISPLAY_RGB_ADDR = 0x30    # I2C address for controlling the LCD backlight
DISPLAY_TEXT_ADDR = 0x3e   # I2C address for controlling the LCD text

# Determine the Raspberry Pi revision and assign the correct I2C bus.
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)   # Newer Pi boards use I2C bus 1
else:
    bus = smbus.SMBus(0)   # Older boards might use I2C bus 0

# -----------------------------------------------------------------------------
# 2. RGB Backlight Control for the Grove-LCD
# -----------------------------------------------------------------------------
#  - The setRGB function allows setting the LCD backlight color via RGB channels.
#  - The textCommand & setText functions control the text display and formatting.
# -----------------------------------------------------------------------------

def setRGB(r, g, b):
    """
    setRGB(r, g, b):
      r, g, b values range from 0..255, controlling red, green, and blue 
      channels of the LCD backlight. 
      Example usage: setRGB(255, 0, 0) => bright red backlight.
    """
    # The internal registers must be set in a specific sequence 
    # to enable color mixing and brightness control.
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x04, 0x15)

    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x06, r)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x07, g)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x08, b)

def textCommand(cmd):
    """
    Sends a command byte to the LCD command register (DISPLAY_TEXT_ADDR).
    This is used internally by setText to initialize or configure 
    the LCD (clear display, set line modes, etc.).
    """
    bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x80, cmd)

def setText(text):
    """
    Clears the LCD, configures display settings, and writes up to 32 characters
    across two lines (16 chars each). If there's a newline or the first line 
    hits 16 characters, text continues on the second line.
    """
    # Clear display
    textCommand(0x01)
    time.sleep(0.05)
    # Display on, no cursor
    textCommand(0x08 | 0x04)
    # 2-line display mode
    textCommand(0x28)
    time.sleep(0.05)

    count = 0
    row = 0

    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            # If we already moved to the second line, stop writing further text
            if row == 2:
                break
            # Command 0xc0 moves cursor to the beginning of the second line
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x40, ord(c))

# -----------------------------------------------------------------------------
# 3. Main Script - Read Sensor, Show on LCD
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        # 3a. Set an initial backlight color (r, g, b). 
        #     For example, (5, 250, 0) => near green hue.
        setRGB(5, 250, 0)
        time.sleep(2)

        # 3b. “Wake” or initialize the DHT sensor to see if it’s responding.
        data_init = bus.read_i2c_block_data(sensor, 0x71, 1)
        if (data_init[0] | 0x08) == 0:
            print('Initialization error')
            os._exit(1)

        # 3c. Continuously read temperature/humidity in a loop, then display.
        while True:
            # Send command (0xac, [0x33,0x00]) to start measuring temperature & humidity
            bus.write_i2c_block_data(sensor, 0xac, [0x33, 0x00])
            time.sleep(0.1)  # Short wait for the sensor to gather data

            # Read 7 bytes from 0x71, containing raw temperature & humidity.
            data = bus.read_i2c_block_data(sensor, 0x71, 7)

            # Extract raw temperature from bits in data[3..5].
            Traw = ((data[3] & 0x0f) << 16) + (data[4] << 8) + data[5]
            temp = 200 * float(Traw) / (2 ** 20) - 50

            # Extract raw humidity from bits in data[1..3].
            Hraw = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)
            humidity = 100 * float(Hraw) / (2 ** 20)

            # Pause 3 seconds between consecutive measurements 
            # (the sensor’s recommended reading interval).
            time.sleep(3)

            # Round to 1 decimal place for a nicer display.
            temp_rounded = round(temp, 1)
            hum_rounded  = round(humidity, 1)

            # Format the data as JSON, e.g. {'temp': 24.5, 'humidity': 60.2}
            x = json.dumps({'temp': temp_rounded, 'humidity': hum_rounded})

            # Check for NaN (not a number) to ensure valid measurements.
            if not math.isnan(temp) and not math.isnan(humidity):
                # Display the JSON on the LCD (truncates if > 32 chars).
                setText(x)

                # Also print to stdout so we can see it in logs or console.
                # By default, no newline is added; you could change that if desired.
                sys.stdout.write(x)

    except KeyboardInterrupt:
        # 3d. If user presses Ctrl+C, print a message and exit gracefully.
        print("Terminated.")
        os._exit(0)
