from __future__ import annotations
import importlib
import time
from typing import Dict, Any

class LedEnvironmentDisplay:
    def __init__(self) -> None:
        self._bus = None
        self._has_display = False
        self._DISPLAY_RGB_ADDR = 0x62
        self._DISPLAY_TEXT_ADDR = 0x3e
        
        try:
            import smbus
            # Successfully detected on Bus 1
            self._bus = smbus.SMBus(1)
            self._has_display = True
            print("[LED] RGB LCD detected on I2C-1")
        except Exception as ex:
            print(f"[LED] Init failed: {ex}")

    def _set_rgb(self, r, g, b):
        if not self._has_display: return
        try:
            # Command sequence for Grove RGB Backlight
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 0, 0)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 1, 0)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 0x08, 0xaa)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 4, r)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 3, g)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 2, b)
        except: pass

    def _set_text(self, text):
        if not self._has_display: return
        try:
            self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, 0x01) # Clear display
            time.sleep(0.05)
            self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, 0x08 | 0x04) # Display ON
            self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, 0x28) # 2-line mode
            
            for i, c in enumerate(text[:32]):
                if c == '\n' or i == 16:
                    self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, 0xc0) # Line 2
                    if c == '\n': continue
                self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x40, ord(c))
        except: pass

    def render(self, environment: Dict[str, Any]):
        l1 = "T:{:.0f}C H:{:.0f}%".format(environment.get("temperature", 0), environment.get("humidity", 0))
        l2 = "L:{:3d} S:{:3d}".format(environment.get("light", 0), environment.get("sound", 0))
        self._set_text(f"{l1[:16]}\n{l2[:16]}")
        self._set_rgb(0, 255, 0) # Normal operation Green

class OledSessionDisplay:
    def __init__(self) -> None:
        self._oled_available = False
        self._device = None
        try:
            serial_module = importlib.import_module("luma.core.interface.serial")
            render_module = importlib.import_module("luma.core.render")
            oled_module = importlib.import_module("luma.oled.device")
            
            # Use detected address 0x3C and Port 1
            serial = serial_module.i2c(port=1, address=0x3C)
            
            # SH1107 driver with mandatory 96x96 resolution per datasheet [cite: 31, 37]
            self._device = oled_module.sh1107(serial, width=96, height=96, rotate=0)
            self._canvas = render_module.canvas
            self._oled_available = True
            print("[OLED] SH1107G 96x96 ready on I2C-1")
        except Exception as ex:
            print(f"[OLED] Init failed: {ex}")

    def render(self, session_state: Dict[str, Any], focus_state: Dict[str, Any]):
        if not self._oled_available: return
        
        status = session_state.get("status", "STOPPED").upper()
        timer = "{:02d}:{:02d}".format(int(session_state.get("remaining_seconds", 0)) // 60, 
                                       int(session_state.get("remaining_seconds", 0)) % 60)
        focus = f"Focus: {focus_state.get('score', 0)}%"

        try:
            with self._canvas(self._device) as draw:
                # Drawing text within the 96x96 active area [cite: 37]
                draw.text((0, 0), status[:12], fill="white")
                draw.text((20, 35), timer, fill="white")
                draw.text((0, 75), focus, fill="white")
        except Exception as ex:
            print(f"[OLED] Render Error: {ex}")