#!/usr/bin/env python3
# -*- coding: utf-8 -*-

############################################################################
# Script Name: cloud.py
#
# Original Version: 15/04/2022 (by Hakan KAYAN)
# Updated Version: 25/12/2024 (by Charith PERERA)
#
# Description:
#   - Demonstrates dual-way communication with ThingsBoard via MQTT.
#   - Reads temperature and humidity from an I2C sensor connected at address 0x38,
#     and publishes the data to ThingsBoard.
#   - Subscribes to RPC commands to toggle a Grove Buzzer on/off, sending the 
#     current buzzer state along with sensor telemetry.
#
# Parameters: Buzzer, Temp & Humidity Sensor (I2C-based)
############################################################################

import os
import time
import paho.mqtt.client as mqtt
import json
import grovepi
import smbus

# -----------------------------------------------------------------------------
# 1. I2C and Sensor Configuration
# -----------------------------------------------------------------------------
#  - This section sets up the I2C bus and addresses. I2C is a serial protocol
#    that allows multiple sensors/actuators to share just two wires (SDA, SCL).
#  - The sensor here uses the address 0x38 on the I2C bus #1 (common on Raspberry Pi).
# -----------------------------------------------------------------------------
address = 0x38                 # The I2C address for the temperature/humidity sensor
i2cbus = smbus.SMBus(1)        # Use I2C bus 1 on the Raspberry Pi
time.sleep(0.5)                # Short delay to ensure sensor has time to initialize

# -----------------------------------------------------------------------------
# 2. ThingsBoard Configuration
# -----------------------------------------------------------------------------
#  - We connect to a ThingsBoard server for storing and visualizing sensor data.
#  - 'thingsboard.cs.cf.ac.uk' is the server address for your institution.
#  - ACCESS_TOKEN is a unique string that authenticates this device to ThingsBoard.
#    Ensure you use your own token to post data to your own ThingsBoard dashboard.
# -----------------------------------------------------------------------------
THINGSBOARD_HOST = 'thingsboard.cs.cf.ac.uk'
ACCESS_TOKEN = 'KV8ua9VXNu9cOQ8Op4DS'  # Replace with your actual token as needed

# -----------------------------------------------------------------------------
# 3. MQTT Callbacks
# -----------------------------------------------------------------------------
#  - These callback functions are automatically called by the paho-mqtt library 
#    in response to various MQTT events (publishing, receiving messages, connecting).
# -----------------------------------------------------------------------------
def on_publish(client, userdata, result):
    """
    Called whenever a message is successfully published to the MQTT broker.
    Prints 'Success' to confirm the publish event, helping you verify 
    that data actually reached the server.
    """
    print("Success")

def on_message(client, userdata, msg):
    """
    Called when the client receives a message on a subscribed topic.
    For this script, we listen for RPC requests that instruct the device
    to toggle the buzzer. The message payload is in JSON format, which we decode.
    """
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    data = json.loads(msg.payload)
    
    # If the method is "setValue", we interpret "params" to be either True or False,
    # which determines the buzzer's ON/OFF state.
    if data['method'] == 'setValue':
        print(data['params'])
        buzzer_state['State'] = data['params']
        # The grovepi.digitalWrite function sends a digital HIGH or LOW to the buzzer pin
        # depending on whether we pass True (HIGH) or False (LOW).
        grovepi.digitalWrite(buzzer, data['params'])

def on_connect(client, userdata, flags, rc, *extra_params):
    """
    Called after the client attempts to connect to the MQTT broker.
    rc (result code) = 0 means a successful connection.
    This is a good place to log or print a message indicating the connection status.
    """
    print('Connected with result code ' + str(rc))

# -----------------------------------------------------------------------------
# 4. Sensor and Actuator Declarations
# -----------------------------------------------------------------------------
#  - Here, we define the time interval for sending new data and set up any 
#    dictionaries that store the sensor values. We also configure the buzzer pin.
# -----------------------------------------------------------------------------
INTERVAL = 3  # Interval (seconds) between consecutive sensor readings and publishes
sensor_data = {'temperature': 0, 'humidity': 0}  # Will hold the latest temp/humidity
next_reading = time.time()                       # Tracks the next scheduled reading time

buzzer = 8                                       # Grove Buzzer connected to digital pin D8
grovepi.pinMode(buzzer, "OUTPUT")                # Set the buzzer pin as an OUTPUT
buzzer_state = {'State': False}                  # Initially, the buzzer is OFF (False)

# -----------------------------------------------------------------------------
# 5. MQTT Client Creation and Configuration
# -----------------------------------------------------------------------------
#  - The paho.mqtt library needs a client instance to manage connections and 
#    message events. We'll attach our callback functions and connect to the 
#    ThingsBoard server using our access token.
# -----------------------------------------------------------------------------
client = mqtt.Client()

# Provide the ACCESS_TOKEN for device authentication to ThingsBoard.
client.username_pw_set(ACCESS_TOKEN)

# Bind our callbacks for connect, publish, and message events.
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

# Connect to the ThingsBoard server on port 1883 (standard MQTT).
# The third parameter (60) is the keepalive interval in seconds.
client.connect(THINGSBOARD_HOST, 1883, 60)

# Subscribe to RPC commands from ThingsBoard to let remote users
# toggle the buzzer by sending "setValue" method calls.
client.subscribe('v1/devices/me/rpc/request/+')

# Start the MQTT network loop in a separate thread, so the script can continue
# running and processing sensor data while maintaining an MQTT connection.
client.loop_start()

# -----------------------------------------------------------------------------
# 6. Main Data Collection Loop
# -----------------------------------------------------------------------------
#  - This loop continuously reads from the I2C temperature/humidity sensor,
#    publishes the readings to ThingsBoard, and includes the current buzzer state.
#  - The loop also respects an INTERVAL to prevent rapid spamming of the server
#    and to allow enough time for the sensor to measure stable values.
# -----------------------------------------------------------------------------
try:
    while True:
        # 6a. First, "wake" the sensor by reading some initial data 
        #     from register 0x71. This is a recommended step for some sensors 
        #     to ensure they're in an active state before you send commands.
        data_init = i2cbus.read_i2c_block_data(address, 0x71, 1)
        if (data_init[0] | 0x08) == 0:
            print('Error initializing sensor')

        # 6b. Write the command (0xac) with parameters [0x33, 0x00] to begin 
        #     temperature/humidity measurement. This is sensor-specific.
        i2cbus.write_i2c_block_data(address, 0xac, [0x33, 0x00])

        # 6c. Wait 3 seconds for the sensor to complete the measurement.
        #     This timing can vary by sensor; check its datasheet.
        time.sleep(3)

        # 6d. Read 7 bytes from the sensor’s register 0x71. This block of data 
        #     includes temperature and humidity in raw, encoded form.
        data = i2cbus.read_i2c_block_data(address, 0x71, 7)

        # 6e. Extract the raw temperature (Traw) and humidity (Hraw) values 
        #     from the data array. The sensor typically encodes these in 
        #     specific bits that we shift and combine.
        Traw = ((data[3] & 0x0f) << 16) + (data[4] << 8) + data[5]
        Hraw = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)

        # 6f. Convert the raw values into human-friendly units:
        #     Temperature (temp) in degrees Celsius, humidity in %.
        #     Each sensor may have a different formula based on its datasheet.
        temp = 200.0 * float(Traw) / 2**20 - 50
        humidity = 100.0 * float(Hraw) / 2**20

        # 6g. Print the measured temperature and humidity to the console for debugging,
        #     showing the user real-time sensor data.
        print(u"Temperature: {:g}\u00b0C, Humidity: {:g}%".format(temp, humidity))

        # 6h. Update our dictionary that holds the current sensor data.
        sensor_data['temperature'] = temp
        sensor_data['humidity'] = humidity

        # 6i. Publish both the sensor readings and the buzzer state to ThingsBoard.
        #     The 'json.dumps' function converts our Python dictionaries to JSON strings.
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), qos=1)
        client.publish('v1/devices/me/telemetry', json.dumps(buzzer_state), qos=1)

        # 6j. Increment the next_reading time by our INTERVAL (3 seconds).
        #     This ensures we maintain a consistent reading rate.
        next_reading += INTERVAL

        # 6k. Calculate how long until our next scheduled read/publish.
        #     If there's remaining time, sleep so we don’t flood the server.
        sleep_time = next_reading - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

# -----------------------------------------------------------------------------
# 7. Graceful Shutdown on Ctrl+C
# -----------------------------------------------------------------------------
except KeyboardInterrupt:
    # When the user presses Ctrl+C, stop the MQTT loop, disconnect from the broker,
    # and exit the script. The 'os._exit(0)' call ensures a clean shutdown.
    client.loop_stop()
    client.disconnect()
    print("Terminated.")
    os._exit(0)
