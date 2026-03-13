#!/usr/bin/env python3
# -*- coding: utf-8 -*-

############################################################################
# Script Name: cloud.py
#
# Original Version: 15/04/2022 (by Hakan KAYAN)
# Updated Version: 25/12/2024 (by Charith PERERA)
#
# Description:
#   - Demonstrates gateway communication with ThingsBoard via MQTT.
#   - Reads PIR and light data from an Arduino over Bluetooth Serial.
#   - Publishes these values as telemetry to a ThingsBoard dashboard.
#
# Parameters: PIR Sensor, Light Sensor
############################################################################

import time
import paho.mqtt.client as mqtt
import json
import serial

# -----------------------------------------------------------------------------
# 1. ThingsBoard Configuration
# -----------------------------------------------------------------------------
# Replace 'thingsboard.cs.cf.ac.uk' if you're using a different server, 
# and update ACCESS_TOKEN with your unique token from ThingsBoard.
THINGSBOARD_HOST = 'thingsboard.cs.cf.ac.uk'
ACCESS_TOKEN = 'KV8ua9VXNu9cOQ8Op4DS'  # <== Insert your own access token here.

# Bluetooth serial settings on Raspberry Pi (after pairing/binding, e.g. /dev/rfcomm0)
BLUETOOTH_PORT = '/dev/rfcomm0'
BLUETOOTH_BAUDRATE = 9600
BLUETOOTH_TIMEOUT = 2

# -----------------------------------------------------------------------------
# 2. MQTT Callbacks and Setup
# -----------------------------------------------------------------------------
def on_publish(client, userdata, result):
    """
    Callback when data is successfully published to the MQTT broker.
    Prints 'Success' to confirm the publish event.
    """
    print("Success")

def on_connect(client, userdata, flags, rc, *extra_params):
    """
    Callback for when the client receives a CONNACK response from the server.
    'rc' is the connection result code. 0 indicates success.
    """
    print('Connected with result code ' + str(rc))

def parse_sensor_line(raw_line):
    """
    Parse Bluetooth lines in the format: PIR:<0-or-1>,LIGHT:<0-1023>
    Returns a telemetry dictionary or None if the line is invalid.
    """
    parts = raw_line.split(',')
    parsed = {}

    for part in parts:
        if ':' not in part:
            continue

        key, value = part.split(':', 1)
        key = key.strip().lower()
        value = value.strip()

        if key == 'pir':
            if value in ('0', '1'):
                parsed['pir'] = int(value)
            else:
                return None
        elif key == 'light':
            try:
                parsed['light'] = int(value)
            except ValueError:
                return None

    if 'pir' in parsed and 'light' in parsed:
        return parsed
    return None

def open_bluetooth_serial():
    """
    Open Bluetooth serial connection, retrying until available.
    """
    while True:
        try:
            bt_serial = serial.Serial(
                BLUETOOTH_PORT,
                BLUETOOTH_BAUDRATE,
                timeout=BLUETOOTH_TIMEOUT
            )
            print('Bluetooth serial connected on ' + BLUETOOTH_PORT)
            return bt_serial
        except serial.SerialException as err:
            print('Bluetooth serial unavailable: ' + str(err))
            print('Retrying in 5 seconds...')
            time.sleep(5)

# -----------------------------------------------------------------------------
# 3. Telemetry Payload Setup
# -----------------------------------------------------------------------------
# Store telemetry in a dictionary for easy JSON serialization.
sensor_data = {'pir': 0, 'light': 0}

# -----------------------------------------------------------------------------
# 4. MQTT Client Creation and Configuration
# -----------------------------------------------------------------------------
client = mqtt.Client()

# Provide the ThingsBoard access token for authentication
client.username_pw_set(ACCESS_TOKEN)

# Bind the callbacks
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to ThingsBoard on port 1883
# 60 seconds is the keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)

# Start the MQTT client networking loop
client.loop_start()

# Open Bluetooth serial connection to Arduino sensor node
bluetooth_serial = open_bluetooth_serial()

# -----------------------------------------------------------------------------
# 5. Main Data Collection Loop
# -----------------------------------------------------------------------------
try:
    while True:
        try:
            raw_line = bluetooth_serial.readline().decode('utf-8', errors='ignore').strip()
        except serial.SerialException as err:
            print('Bluetooth serial disconnected: ' + str(err))
            if bluetooth_serial.is_open:
                bluetooth_serial.close()
            bluetooth_serial = open_bluetooth_serial()
            continue

        if not raw_line:
            continue

        parsed_data = parse_sensor_line(raw_line)
        if parsed_data is None:
            print('Ignored invalid payload: ' + raw_line)
            continue

        sensor_data.update(parsed_data)
        print('PIR: {pir}, Light: {light}'.format(**sensor_data))

        # Publish sensor data to ThingsBoard telemetry endpoint.
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)

except KeyboardInterrupt:
    # If user presses Ctrl+C, gracefully close serial and MQTT connection.
    if bluetooth_serial.is_open:
        bluetooth_serial.close()
    client.loop_stop()
    client.disconnect()
    print("Terminated.")
