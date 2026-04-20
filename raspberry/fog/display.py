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
    """Grove-OLED display (typically 128x64) for session and timer information.
    
    Shows: Session status/phase, countdown timer, focus score.
    Uses luma.oled library for I2C communication (SSD1306 or SH1106).
    """

    def __init__(self) -> None:
        self._oled_available = False
        self._device = None
        self._canvas = None
        self._font = None
        try:
            serial_module = importlib.import_module("luma.core.interface.serial")
            render_module = importlib.import_module("luma.core.render")
            oled_module = importlib.import_module("luma.oled.device")
            pil_module = importlib.import_module("PIL.ImageFont")

            # Grove-OLED typically at address 0x3C on I2C port 1
            serial = serial_module.i2c(port=1, address=0x3C)
            print("[OLED] I2C serial initialized")
            
            # Try SSD1306 first (most common), fall back to SH1106 if needed
            try:
                self._device = oled_module.ssd1306(serial)
                print("[OLED] SSD1306 device initialized")
            except Exception as e:
                print("[OLED] SSD1306 failed: {}, trying SH1106...".format(e))
                self._device = oled_module.sh1106(serial)
                print("[OLED] SH1106 device initialized")
            
            self._canvas = render_module.canvas
            self._font = pil_module.load_default()
            self._oled_available = True
            print("[OLED] Ready to render")
        except Exception as ex:
            print("[OLED] Init failed: {}".format(ex))
            self._oled_available = False

    def render(self, session_state: Dict[str, Any], focus_state: Dict[str, Any]) -> None:
        # Extract session and focus info
        remaining = int(session_state.get("remaining_seconds", 0))
        minutes = remaining // 60
        seconds = remaining % 60
        
        status = session_state.get("status", "stopped")
        phase = session_state.get("phase", "")
        focus_score = int(focus_state.get("score", 0))
        
        # Format display lines
        state_line = "{} {}".format(status.upper()[:7], phase.upper()[:8])
        timer_line = "{:02d}:{:02d}".format(minutes, seconds)
        focus_line = "Focus: {}%".format(focus_score)

        if self._oled_available and self._device is not None:
            try:
                with self._canvas(self._device) as draw:
                    # Session status and phase (top)
                    draw.text((0, 0), state_line, fill=255, font=self._font)
                    
                    # Large timer display (middle)
                    draw.text((0, 20), timer_line, fill=255, font=self._font)
                    
                    # Focus score (bottom)
                    draw.text((0, 48), focus_line, fill=255, font=self._font)
            except Exception as ex:
                print("[OLED] Render error: {} | {} | {} | Exception: {}".format(state_line, timer_line, focus_line, ex))
        else:
            print("[OLED] {} | {} | {}".format(state_line, timer_line, focus_line))
