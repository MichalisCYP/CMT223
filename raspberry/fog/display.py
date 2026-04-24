from __future__ import annotations

import importlib
import sys
import time
from typing import Dict, Any


class LedEnvironmentDisplay:
    """Grove-LCD RGB backlight display for environmental monitoring.
    
    Shows: Temperature, Humidity, Light, Sound levels.
    Backlight color reflects session status when available.
    Uses direct I2C communication via smbus.
    """

    def __init__(self) -> None:
        self._bus = None
        self._has_display = False
        
        # I2C Addresses for Grove RGB LCD
        self._DISPLAY_RGB_ADDR = 0x62    # Controls backlight color
        self._DISPLAY_TEXT_ADDR = 0x3e   # Controls text display
        
        try:
            # Initialize I2C bus
            if sys.platform == 'uwp':
                import winrt_smbus as smbus
                self._bus = smbus.SMBus(1)
            else:
                import smbus
                try:
                    import RPi.GPIO as GPIO
                    rev = GPIO.RPI_REVISION
                    self._bus = smbus.SMBus(1 if (rev == 2 or rev == 3) else 0)
                except:
                    # Fallback for non-RPi systems or missing GPIO
                    self._bus = smbus.SMBus(1)
            
            self._has_display = True
            print("[LED] I2C bus initialized successfully")
        except Exception as ex:
            print("[LED] Failed to initialize I2C bus: {}".format(ex))
            self._has_display = False

    def _set_rgb(self, r: int, g: int, b: int) -> None:
        """Set RGB backlight color."""
        if not self._has_display or self._bus is None:
            return
        
        try:
            # Configure registers for color mixing
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 0, 0)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 1, 0)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 0x08, 0xaa)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 4, r)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 3, g)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 2, b)
        except Exception as ex:
            print("[LED] Failed to set RGB: {}".format(ex))

    def _text_command(self, cmd: int) -> None:
        """Send a command to the text display controller."""
        if not self._has_display or self._bus is None:
            return
        
        try:
            self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, cmd)
        except Exception as ex:
            print("[LED] Failed to send command: {}".format(ex))

    def _set_text(self, text: str) -> None:
        """Write text to the LCD display (2 lines, 16 chars each)."""
        if not self._has_display or self._bus is None:
            return
        
        try:
            # Clear display
            self._text_command(0x01)
            time.sleep(0.05)
            
            # Display ON, no cursor
            self._text_command(0x08 | 0x04)
            
            # 2-line display mode
            self._text_command(0x28)
            time.sleep(0.05)
            
            # Write characters
            count = 0
            row = 0
            for c in text:
                # Check for newline or 16 characters per line
                if c == '\n' or count == 16:
                    count = 0
                    row += 1
                    if row == 2:
                        break
                    # Move to second line
                    self._text_command(0xc0)
                    if c == '\n':
                        continue
                
                count += 1
                # Write character to LCD data register
                self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x40, ord(c))
        except Exception as ex:
            print("[LED] Failed to set text: {}".format(ex))

    def render(self, environment: Dict[str, Any]) -> None:
        # Line 1: Temperature and Humidity
        line1 = "T:{:.0f}C H:{:.0f}%".format(
            float(environment.get("temperature", 0.0)),
            float(environment.get("humidity", 0.0)),
        )

        # Line 2: Light and Sound
        line2 = "L:{:3d} S:{:3d}".format(
            int(environment.get("light", 0)),
            int(environment.get("sound", 0)),
        )

        text = "{}\n{}".format(line1[:16], line2[:16])

        if self._has_display:
            try:
                self._set_text(text)
                # Green backlight for normal operation
                self._set_rgb(0, 255, 0)
            except Exception as ex:
                print("[LED] Render failed: {} | {}".format(text.replace("\n", " | "), ex))
        else:
            print("[LED] {} | move={}".format(text.replace("\n", " | "), environment.get("move", 0)))


class OledSessionDisplay:
    """Grove-OLED display for session and timer information.
    
    Target Device: GGM096096A4W01 (96x96 OLED)
    Driver IC: SH1107G
    """

    def __init__(self) -> None:
        self._oled_available = False
        self._device = None
        try:
            grove_display = importlib.import_module("grove.display.base")
            sh1107g = getattr(grove_display, "SH1107G")

            # Correct I2C addresses per SH1107G Manual Page 21
            # 0x78 (SA0=0) -> 0x3C 7-bit
            # 0x7A (SA0=1) -> 0x3D 7-bit (Your code had 0x3E)
            for address in (0x3C, 0x3D):
                try:
                    self._device = sh1107g(address=address)
                    print("[OLED] SH1107G initialized at 0x{:02X}".format(address))
                    break
                except Exception as ex:
                    print("[OLED] Init retry at 0x{:02X} failed".format(address))

            if self._device is None:
                raise RuntimeError("Unable to initialize SH1107G display")

            # Manual recommends clearing RAM and setting display ON (0xAF) 
            # during init (Page 16/23)
            self._oled_available = True
            
        except Exception as ex:
            print("[OLED] Init failed: {}".format(ex))
            self._oled_available = False

    def render(self, session_state: Dict[str, Any], focus_state: Dict[str, Any]) -> None:
        # Note: This display is 96x96 pixels, not a character LCD.
        # Ensure the 'sh1107g' driver supports setCursor/write for text.
        
        remaining = int(session_state.get("remaining_seconds", 0))
        minutes = remaining // 60
        seconds = remaining % 60

        status = session_state.get("status", "stopped")
        phase = session_state.get("phase", "")
        focus_score = int(focus_state.get("score", 0))

        state_line = "{} {}".format(status.upper()[:7], phase.upper()[:8])
        timer_line = "{:02d}:{:02d}".format(minutes, seconds)
        focus_line = "Focus: {}%".format(focus_score)

        if self._oled_available and self._device is not None:
            try:
                # Page 23 of manual shows clearing RAM before display
                if hasattr(self._device, "clear"):
                    self._device.clear()

                # The SH1107G uses 16 pages for its 96-line height (Page 23)
                # Ensure row mapping matches the 96x96 coordinate system
                for row, line in enumerate((state_line, timer_line, focus_line)):
                    if hasattr(self._device, "setCursor"):
                        # Offset rows to be readable on the 96px height
                        self._device.setCursor(row * 2, 0) 
                    if hasattr(self._device, "write"):
                        self._device.write(line)
            except Exception as ex:
                print("[OLED] Render error: {}".format(ex))
        else:
            print("[OLED] {} | {} | {}".format(state_line, timer_line, focus_line))
# https://github.com/orji123/Irisoled - future integration