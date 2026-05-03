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
        except Exception as ex:
            print("[LED] RGB write failed: {}".format(ex))

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
        except Exception as ex:
            print("[LED] Text write failed: {}".format(ex))

    def render(self, environment: Dict[str, Any]):
        l1 = "T:{:.0f}C H:{:.0f}%".format(environment.get("temperature", 0), environment.get("humidity", 0))
        l2 = "L:{:3d} S:{:3d}".format(environment.get("light", 0), environment.get("sound", 0))
        self._set_text(f"{l1[:16]}\n{l2[:16]}")
        self._set_rgb(0, 255, 0) # Normal operation Green
class OledSessionDisplay:
    def __init__(self) -> None:
        self._oled_available = False
        self._device = None
        self._font_small = None
        self._font_timer = None
        try:
            serial_module = importlib.import_module("luma.core.interface.serial")
            render_module = importlib.import_module("luma.core.render")
            oled_module = importlib.import_module("luma.oled.device")
            imagefont_module = importlib.import_module("PIL.ImageFont")
            
            # Detected address 0x3C on Port 1
            serial = serial_module.i2c(port=1, address=0x3C)
            
            # Fix: Initialize at 128x128 to satisfy the luma.oled driver constraints.
            # The SH1107G driver IC supports this, even though our panel uses 96x96.
            self._device = oled_module.sh1107(serial, width=128, height=128, rotate=0)
            
            self._canvas = render_module.canvas
            self._font_small = imagefont_module.load_default()
            try:
                self._font_timer = imagefont_module.truetype("DejaVuSans.ttf", 28)
            except Exception:
                self._font_timer = imagefont_module.load_default()
            self._oled_available = True
            print("[OLED] SH1107G initialized (Buffered at 128x128)")
        except Exception as ex:
            print(f"[OLED] Init failed: {ex}")

    @staticmethod
    def _format_timer(remaining_seconds: Any) -> str:
        try:
            seconds = max(0, int(float(remaining_seconds)))
        except (TypeError, ValueError):
            seconds = 0
        return "{:02d}:{:02d}".format(seconds // 60, seconds % 60)

    def render(self, session_state: Dict[str, Any], focus_state: Dict[str, Any]):
        if not self._oled_available: return
        
        status = session_state.get("status", "STOPPED").upper()
        timer = self._format_timer(session_state.get("remaining_seconds", 0))
        phase = str(session_state.get("phase", "focus")).upper()
        focus = f"Focus: {focus_state.get('score', 0)}%"

        try:
            with self._canvas(self._device) as draw:
                # IMPORTANT: Only draw within the 96x96 Active Area.
                # Data outside 96x96 will not be visible on your physical panel.
                draw.text((0, 0), status[:12], fill="white", font=self._font_small)
                draw.text((0, 14), phase[:12], fill="white", font=self._font_small)
                draw.text((6, 34), timer, fill="white", font=self._font_timer)
                draw.text((0, 82), focus[:20], fill="white", font=self._font_small)
        except Exception as ex:
            print(f"[OLED] Render Error: {ex}")