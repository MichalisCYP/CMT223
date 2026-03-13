#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/***************************************************************************
* Sketch Name: Lab2_code2
*
* Original Version: 13/02/2024 (by Yasar Majib)
* Modified From: https://github.com/DexterInd/GrovePi.git
* Updated Version: 18/02/2025 (by Ewan CROWLE)
*
* Description:
*   - Demonstrates how to read temperature and humidity from a DHT sensor
*     (blue module type) connected to digital port D4 on a Raspberry Pi 
*     using the grovepi library.
*   - Displays the sensor readings on a Grove LCD with an RGB backlight
*     (using two I2C addresses, 0x30 for color and 0x3e for text).
*   - Prints the temperature/humidity as JSON to stdout for easy logging.
*
* Parameters:
*   - Temperature & Humidity Sensors (DHT, blue-type) on digital port 4
*   - Grove-LCD RGB Backlight (I2C addresses 0x30 for RGB, 0x3e for text)
*
* Return:
*   - Continuously updates the LCD with temperature (°C) & humidity (%)
*   - Outputs the same sensor data as JSON to the console
***************************************************************************/
"""

import time
import sys
import os
import grovepi
import math
import json

# 1. Define the DHT sensor port and sensor type.
#    - The 'blue' sensor usually corresponds to the DHT11, while a 'white' sensor 
#      might be a DHT22 or DHTPro. Check grovepi.dht docs if in doubt.
sensor = 4   # The DHT sensor is attached to digital port D4
blue = 0     # 0 indicates a "blue" DHT sensor (DHT11).

# -----------------------------------------------------------------------------
# 2. I2C Setup for Grove LCD
# -----------------------------------------------------------------------------
#  - On some boards, the Grove LCD uses addresses:
#       0x62 (RGB) and 0x3e (text) (older v4.0).
#    This script uses addresses: 0x30 (RGB) and 0x3e (text) (newer v5.0).
#    Adjust these constants if your LCD has different addresses.
# -----------------------------------------------------------------------------
DISPLAY_RGB_ADDR = 0x30
DISPLAY_TEXT_ADDR = 0x3e

# 3. Determine I2C Bus
#    - On Raspberry Pi, 'smbus.SMBus(1)' is common for rev 2 or 3. 
#      If you have an older board (rev 1), or Windows IoT (uwp), adjust accordingly.
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
# 4. LCD Backlight and Text Functions
# -----------------------------------------------------------------------------
#    - The setRGB() function sets the background color via (r, g, b) channels.
#    - textCommand() issues instructions (e.g., clear display).
#    - setText() writes up to 32 characters (two rows of 16 each).
# -----------------------------------------------------------------------------

def setRGB(r, g, b):
    """
    setRGB(r, g, b):
      - Controls the Grove LCD backlight color by writing to the 
        device at DISPLAY_RGB_ADDR.
      - r, g, b range from 0..255 for red, green, and blue channels.
    """
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x04, 0x15)

    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x06, r)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x07, g)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x08, b)

def textCommand(cmd):
    """
    Sends a command byte to the LCD text command register at DISPLAY_TEXT_ADDR (0x80).
    Used internally by setText() to configure display settings or move the cursor.
    """
    bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x80, cmd)

def setText(text):
    """
    Clears the display, configures it for 2-line mode, then writes 
    up to 32 characters. If it hits 16 chars or a newline, 
    it moves to the second line. Excess text is ignored.
    """
    # Clear display
    textCommand(0x01)
    time.sleep(0.05)
    # Display on, no cursor
    textCommand(0x08 | 0x04)
    # 2-line mode
    textCommand(0x28)
    time.sleep(0.05)

    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            # Move to next line
            count = 0
            row += 1
            if row == 2:  # Only 2 lines available
                break
            textCommand(0xc0)  # Move cursor to second line
            if c == '\n':
                continue
        count += 1
        # Write character to the LCD data register (0x40)
        bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x40, ord(c))

# -----------------------------------------------------------------------------
# 5. Main Logic
# -----------------------------------------------------------------------------
#  - Continuously reads temperature & humidity from a DHT sensor
#    using grovepi, then shows the readings on the LCD. 
#  - Also prints them in JSON format to stdout for logging or debugging.
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # 5a. Set the LCD backlight to a sample color (r=5, g=250, b=0 => bright greenish).
    setRGB(5, 250, 0)
    time.sleep(2)

    # 5b. Enter an infinite loop to read the sensor and update the LCD.
    while True:
        try:
            # Read from the DHT sensor using grovepi.dht(port, type).
            # 'temp' is in Celsius, 'humidity' in % RH.
            [temp, humidity] = grovepi.dht(sensor, blue)

            # Wait a few seconds to avoid rapid reads (the sensor or the code 
            # might produce unreliable results if called too frequently).
            time.sleep(3)

            # Convert sensor readings to a JSON string.
            # We do minimal rounding or formatting here, 
            # but you can do round(temp,1) if desired.
            x = json.dumps({'temp': temp, 'humidity': humidity})

            # Check that both temp and humidity are valid (not NaN).
            if not math.isnan(temp) and not math.isnan(humidity):
                # Update LCD with the JSON text. 
                # If it exceeds 32 chars, it may wrap or truncate.
                setText(x)
                time.sleep(0.1)

                # Print the JSON to stdout, e.g. {"temp":23.5,"humidity":50}
                # By default, no newline is added, so you might want to add one.
                sys.stdout.write(x)
                
        except KeyboardInterrupt:
            # If the user presses Ctrl+C, cleanly exit.
            print("Terminated.")
            os._exit(0)
