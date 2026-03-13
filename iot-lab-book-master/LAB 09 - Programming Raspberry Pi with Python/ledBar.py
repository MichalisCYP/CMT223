#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/***************************************************************************
* Sketch Name: ledBar.py
*
* Original Version: 07/06/2022 (by Hakan KAYAN)
* Updated Version: 25/12/2024 (by Charith PERERA)
*
* Description:
*   - Demonstrates various functions of the Grove LED Bar (connected to D5).
*   - Showcases initialization, orientation toggling, setting specific LEDs,
*     toggling, setting bit states, and advanced patterns like bouncing and
*     random lighting.
*   - Provides a thorough example of how to fully control a Grove LED Bar
*     using the GrovePi library in Python.
*
* Target Audience:
*   - Undergraduate students learning about electronics, sensors/actuators,
*     and fundamental Python coding practices for IoT or robotics projects.
***************************************************************************/
"""

import time
import grovepi
import random

# -----------------------------------------------------------------------------
# 1. Hardware Setup: 
#    - The Grove LED Bar is connected to digital port D5 on the Grove Base Shield.
#      This port has four pins: DI (Data In), DCKI (Clock), VCC (5V), and GND.
# -----------------------------------------------------------------------------
ledbar = 5

# -----------------------------------------------------------------------------
# 2. Configure the LED Bar Port:
#    - We set the pinMode to "OUTPUT" because we are sending signals 
#      to the LED Bar to control its LEDs.
# -----------------------------------------------------------------------------
grovepi.pinMode(ledbar, "OUTPUT")

# -----------------------------------------------------------------------------
# 3. Short Pause:
#    - The sleep function allows the pin configuration to register properly 
#      before we start sending commands to the LED Bar.
# -----------------------------------------------------------------------------
time.sleep(1)

# -----------------------------------------------------------------------------
# Main Loop:
#    - Here, we group a series of tests (labeled "Test 1", "Test 2", etc.) 
#      to demonstrate different functions of the Grove LED Bar.
#    - We use a while True loop to continuously cycle through these tests.
#      However, each test itself is just a demonstration. You could adapt 
#      this to your needs or remove tests you don’t need.
# -----------------------------------------------------------------------------
while True:
    try:
        # Test 1: Initialize the LED Bar (Red to Green orientation)
        # ---------------------------------------------------------
        #  - grovepi.ledBar_init(pin, orientation)
        #  - orientation can be:
        #      0 = LEDs light from red (one end) to green (opposite end)
        #      1 = LEDs light from green (one end) to red (opposite end)
        print("Test 1) Initialise - red to green")
        grovepi.ledBar_init(ledbar, 0)
        time.sleep(0.5)

        # Test 2: Set the "Level" of the LED Bar
        # --------------------------------------
        #  - grovepi.ledBar_setLevel(pin, level)
        #  - level ranges from 0 (all off) to 10 (all on).
        #  - This is convenient for quickly displaying a quantity on a scale of 0–10.
        print("Test 2) Set level")
        for i in range(0, 11):
            grovepi.ledBar_setLevel(ledbar, i)
            time.sleep(0.2)
        time.sleep(0.3)

        # Setting specific levels manually (e.g., 8, 2, 5)
        grovepi.ledBar_setLevel(ledbar, 8)
        time.sleep(0.5)
        grovepi.ledBar_setLevel(ledbar, 2)
        time.sleep(0.5)
        grovepi.ledBar_setLevel(ledbar, 5)
        time.sleep(0.5)

        # Test 3: Switch On/Off a Single LED
        # ----------------------------------
        #  - grovepi.ledBar_setLed(pin, led, state)
        #  - led ranges from 1..10, state is 1 (on) or 0 (off).
        print("Test 3) Switch on/off a single LED")
        grovepi.ledBar_setLed(ledbar, 10, 1)
        time.sleep(0.5)
        grovepi.ledBar_setLed(ledbar, 9, 1)
        time.sleep(0.5)
        grovepi.ledBar_setLed(ledbar, 8, 1)
        time.sleep(0.5)
        grovepi.ledBar_setLed(ledbar, 1, 0)
        time.sleep(0.5)
        grovepi.ledBar_setLed(ledbar, 2, 0)
        time.sleep(0.5)
        grovepi.ledBar_setLed(ledbar, 3, 0)
        time.sleep(0.5)

        # Test 4: Toggle a Single LED
        # ---------------------------
        #  - grovepi.ledBar_toggleLed(pin, led) flips the LED: on -> off, off -> on
        print("Test 4) Toggle a single LED")
        grovepi.ledBar_toggleLed(ledbar, 1)
        time.sleep(0.5)
        grovepi.ledBar_toggleLed(ledbar, 2)
        time.sleep(0.5)
        grovepi.ledBar_toggleLed(ledbar, 9)
        time.sleep(0.5)
        grovepi.ledBar_toggleLed(ledbar, 10)
        time.sleep(0.5)

        # Test 5: Set State (All 10 LEDs) With Bits
        # -----------------------------------------
        #  - grovepi.ledBar_setBits(pin, state)
        #  - 'state' is a 10-bit integer: 0..1023 (0b0000000000..0b1111111111).
        #    Each bit corresponds to one LED. 
        #    Example: 0b1111111111 (decimal 1023) turns on all LEDs.
        print("Test 5) Set state (all 10 LEDs) with bits")
        for i in range(0, 32):
            grovepi.ledBar_setBits(ledbar, i)
            time.sleep(0.2)
        time.sleep(0.3)

        # Test 6: Get the Current State
        # -----------------------------
        #  - state = grovepi.ledBar_getBits(pin)
        #  - This returns the 10-bit integer representing the currently lit LEDs.
        print("Test 6) Get current state")
        state = grovepi.ledBar_getBits(ledbar)
        print("With first 5 LEDs lit, the state should be 31 or 0x1F (binary 00000011111).")
        print(state)

        # Shifting the state left by 5 bits moves the lit LEDs to the upper half.
        state = state << 5
        time.sleep(0.5)

        # Test 7: Apply the Modified State
        # ---------------------------------
        #  - Now that we shifted the bits, the LEDs should appear on the opposite side.
        print("Test 7) Set state using modified bits")
        grovepi.ledBar_setBits(ledbar, state)
        time.sleep(0.5)

        # Test 8: Swap Orientation
        # ------------------------
        #  - grovepi.ledBar_orientation(pin, orientation)
        #  - This re-maps LED indices from left->right or right->left 
        #    without losing the current pattern.
        print("Test 8) Swap orientation - green to red (1) vs. red to green (0)")
        grovepi.ledBar_orientation(ledbar, 1)
        time.sleep(0.5)
        grovepi.ledBar_orientation(ledbar, 0)
        time.sleep(0.5)
        grovepi.ledBar_orientation(ledbar, 1)
        time.sleep(0.5)

        # Test 9: Set Level Again (Now Using the New Orientation)
        # -------------------------------------------------------
        print("Test 9) Set level again (new orientation)")
        for i in range(0, 11):
            grovepi.ledBar_setLevel(ledbar, i)
            time.sleep(0.2)
        time.sleep(0.3)

        # Test 10: Set a Single LED Again
        # -------------------------------
        print("Test 10) Set a single LED again")
        grovepi.ledBar_setLed(ledbar, 1, 0)
        time.sleep(0.5)
        grovepi.ledBar_setLed(ledbar, 3, 0)
        time.sleep(0.5)
        grovepi.ledBar_setLed(ledbar, 5, 0)
        time.sleep(0.5)

        # Test 11: Toggle a Single LED Again
        # ----------------------------------
        print("Test 11) Toggle a single LED again")
        grovepi.ledBar_toggleLed(ledbar, 2)
        time.sleep(0.5)
        grovepi.ledBar_toggleLed(ledbar, 4)
        time.sleep(0.5)

        # Test 12: Get State Again
        # ------------------------
        print("Test 12) Get state again")
        state = grovepi.ledBar_getBits(ledbar)

        # Shift the state right by 5 bits, moving lit LEDs from the upper half to the lower half.
        state = state >> 5
        time.sleep(0.5)

        # Test 13: Set State Again
        # ------------------------
        print("Test 13) Set state again")
        grovepi.ledBar_setBits(ledbar, state)
        time.sleep(0.5)

        # Test 14: Step Through All 10 LEDs
        # ---------------------------------
        #  - This increments the 'level' from 0..10, effectively turning on
        #    each LED in sequence from one end to the other.
        print("Test 14) Step through all 10 LEDs in sequence")
        for i in range(0, 11):
            grovepi.ledBar_setLevel(ledbar, i)
            time.sleep(0.2)
        time.sleep(0.3)

        # Test 15: Bounce Pattern
        # -----------------------
        #  - This logic "bounces" a set of lit LEDs from left to right, then back.
        #  - Great for visualizing shifting bits in real time.
        print("Test 15) Bounce pattern")
        # Start with 2 LEDs lit on the left side.
        grovepi.ledBar_setLevel(ledbar, 2)
        state = grovepi.ledBar_getBits(ledbar)

        # Bounce to the right
        for i in range(0, 9):
            state <<= 1  # Shift all bits to the left by 1
            grovepi.ledBar_setBits(ledbar, state)
            time.sleep(0.2)

        # Bounce to the left
        for i in range(0, 9):
            state >>= 1  # Shift all bits to the right by 1
            grovepi.ledBar_setBits(ledbar, state)
            time.sleep(0.2)
        time.sleep(0.3)

        # Test 16: Random States
        # ----------------------
        #  - Assigns random 10-bit values, producing random LED patterns.
        #  - Illustrates how you can quickly change the LED bar for fun or testing.
        print("Test 16) Random states")
        for i in range(0, 21):
            state = random.randint(0, 1023)  # 0..1023
            grovepi.ledBar_setBits(ledbar, state)
            time.sleep(0.2)
        time.sleep(0.3)

        # Test 17: Invert Pattern
        # -----------------------
        #  - Start with 0x155 (341 decimal), which lights every second LED (binary 0101010101).
        #  - Then XOR with 0x3FF (binary 1111111111) to invert bits, flipping on/off states.
        print("Test 17) Invert pattern")
        state = 341  # 0b0101010101
        for i in range(0, 5):
            grovepi.ledBar_setBits(ledbar, state)
            time.sleep(0.2)
            state = 0x3FF ^ state  # Invert bits
            grovepi.ledBar_setBits(ledbar, state)
            time.sleep(0.2)
        time.sleep(0.3)

        # Test 18: Walk Through All Possible Combinations (0..1023)
        # ---------------------------------------------------------
        #  - This exhaustively sets every possible 10-bit pattern on the LED Bar.
        #  - Demonstrates the maximum range of states, turning each LED on/off in all combos.
        print("Test 18) Walk through all possible combinations")
        for i in range(0, 1024):
            grovepi.ledBar_setBits(ledbar, i)
            time.sleep(0.1)
        time.sleep(0.4)

    except KeyboardInterrupt:
        # -----------------------------------------------------------------------------
        # 4. On Ctrl+C, turn all LEDs off and exit the loop.
        #    This ensures the LED Bar is in a known (off) state before the program ends.
        # -----------------------------------------------------------------------------
        grovepi.ledBar_setBits(ledbar, 0)
        break

    except IOError:
        # -----------------------------------------------------------------------------
        # 5. If an I/O error occurs (e.g., the GrovePi can’t communicate with the hardware),
        #    print an error message and continue the while loop.
        #    This prevents the entire program from crashing on a single I/O hiccup.
        # -----------------------------------------------------------------------------
        print("Error")
