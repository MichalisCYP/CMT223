from __future__ import annotations
import importlib
import sys
import time
from typing import Dict, Any

class LedEnvironmentDisplay:
    """Grove-LCD RGB backlight display fixed for I2C-3."""

    def __init__(self) -> None:
        self._bus = None
        self._has_display = False
        self._DISPLAY_RGB_ADDR = 0x62
        self._DISPLAY_TEXT_ADDR = 0x3e
        
        try:
            import smbus
            # Explicitly targeting I2C bus 3 for Raspberry Pi Grove
            self._bus = smbus.SMBus(3)
            self._has_display = True
            print("[LED] I2C-3 bus initialized successfully")
        except Exception as ex:
            print("[LED] Failed to initialize I2C-3: {}".format(ex))

    def _set_rgb(self, r: int, g: int, b: int) -> None:
        if not self._has_display: return
        try:
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 0, 0)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 1, 0)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 0x08, 0xaa)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 4, r)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 3, g)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 2, b)
        except Exception: pass

    def _text_command(self, cmd: int) -> None:
        if self._has_display:
            self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, cmd)

    def _set_text(self, text: str) -> None:
        if not self._has_display: return
        try:
            self._text_command(0x01) # Clear
            time.sleep(0.05)
            self._text_command(0x08 | 0x04) # Display ON
            self._text_command(0x28) # 2-line mode
            
            count = 0
            for c in text[:32]:
                if c == '\n' or count == 16:
                    self._text_command(0xc0) # Move to line 2
                    if c == '\n': continue
                count += 1
                self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x40, ord(c))
        except Exception: pass

    def render(self, environment: Dict[str, Any]) -> None:
        line1 = "T:{:.0f}C H:{:.0f}%".format(environment.get("temperature", 0), environment.get("humidity", 0))
        line2 = "L:{:3d} S:{:3d}".format(environment.get("light", 0), environment.get("sound", 0))
        self._set_text(f"{line1[:16]}\n{line2[:16]}")
        self._set_rgb(0, 255, 0)


class OledSessionDisplay:
    """Fixed for SH1107G 96x96 OLED on I2C-3."""

    def __init__(self) -> None:
        self._oled_available = False
        self._device = None
        self._canvas = None
        
        try:
            serial_module = importlib.import_module("luma.core.interface.serial")
            render_module = importlib.import_module("luma.core.render")
            oled_module = importlib.import_module("luma.oled.device")
            
            # 1. SH1107G Addressing: SA0=0 is 0x3C, SA0=1 is 0x3D
            # 2. Port: 3 for your Grove setup
            serial = serial_module.i2c(port=3, address=0x3C)
            
            # 3. Model: sh1107 device with 96x96 resolution per datasheet specs
            self._device = oled_module.sh1107(serial, width=96, height=96)
            self._canvas = render_module.canvas
            self._oled_available = True
            print("[OLED] SH1107G 96x96 initialized on I2C-3")
        except Exception as ex:
            print("[OLED] Init failed: {}".format(ex))

    def render(self, session_state: Dict[str, Any], focus_state: Dict[str, Any]) -> None:
        remaining = int(session_state.get("remaining_seconds", 0))
        timer_line = "{:02d}:{:02d}".format(remaining // 60, remaining % 60)
        status_line = "{} {}".format(session_state.get("status", "").upper()[:7], 
                                     session_state.get("phase", "").upper()[:8])
        focus_line = "Focus: {}%".format(focus_state.get("score", 0))

        if self._oled_available and self._device is not None:
            try:
                with self._canvas(self._device) as draw:
                    # Drawing within the 96x96 active area boundaries
                    draw.text((0, 0), status_line, fill="white")
                    draw.text((20, 35), timer_line, fill="white") # Centered timer
                    draw.text((0, 80), focus_line, fill="white")
            except Exception as ex:
                print("[OLED] Render error: {}".format(ex))
        else:
            print(f"[OLED Print] {status_line} | {timer_line} | {focus_line}")