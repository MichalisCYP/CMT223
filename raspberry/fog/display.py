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
        self._last_text = ""
        self._last_color = (-1, -1, -1)
        
        try:
            import smbus
            # Successfully detected on Bus 1
            self._bus = smbus.SMBus(1)
            self._has_display = True
            self._init_display()
            print("[LED] RGB LCD detected on I2C-1")
        except Exception as ex:
            print(f"[LED] Init failed: {ex}")

    def _init_display(self):
        if not self._has_display: return
        try:
            # Initialize display settings once
            self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, 0x28) # 2-line mode
            time.sleep(0.05)
            self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, 0x08 | 0x04) # Display ON, Cursor OFF
            self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, 0x01) # Clear
            time.sleep(0.05)
        except Exception as ex:
            print(f"[LED] Display init command failed: {ex}")

    def _set_rgb(self, r, g, b):
        if not self._has_display: return
        if (r, g, b) == self._last_color: return
        
        try:
            # Command sequence for Grove RGB Backlight
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 0, 0)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 1, 0)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 0x08, 0xaa)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 4, r)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 3, g)
            self._bus.write_byte_data(self._DISPLAY_RGB_ADDR, 2, b)
            self._last_color = (r, g, b)
        except Exception as ex:
            print("[LED] RGB write failed: {}".format(ex))

    def _set_text(self, text):
        if not self._has_display: return
        
        # Normalize text to 32 characters (16 per line) to avoid clearing
        lines = text.split('\n')
        l1 = lines[0][:16].ljust(16)
        l2 = lines[1][:16].ljust(16) if len(lines) > 1 else "".ljust(16)
        full_text = l1 + l2
        
        if full_text == self._last_text:
            return

        try:
            # Reset cursor to beginning instead of clearing to avoid flicker
            self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, 0x80) 
            
            for i, c in enumerate(full_text):
                if i == 16:
                    # Move to second line
                    self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x80, 0xc0)
                self._bus.write_byte_data(self._DISPLAY_TEXT_ADDR, 0x40, ord(c))
            
            self._last_text = full_text
        except Exception as ex:
            print("[LED] Text write failed: {}".format(ex))

    def render(self, environment: Dict[str, Any], session: Dict[str, Any] = None, focus: Dict[str, Any] = None):
        # 1. Determine Backlight Color
        status = (session or {}).get("status", "STOPPED").upper()
        phase = (session or {}).get("phase", "focus").upper()
        score = (focus or {}).get("score", 0)

        if status == "RUNNING":
            if phase == "FOCUS":
                if score >= 80:
                    self._set_rgb(0, 255, 0)   # Green: Good Focus
                elif score >= 50:
                    self._set_rgb(255, 200, 0) # Yellow/Orange: Warning
                else:
                    self._set_rgb(255, 0, 0)   # Red: Distracted
            else:
                self._set_rgb(0, 100, 255)     # Blue: Break time
        elif status == "PAUSED":
            self._set_rgb(255, 255, 0)         # Bright Yellow: Paused
        else:
            self._set_rgb(128, 0, 128)         # Purple: Stopped/Idle

        # 2. Format Line 1: Center [PHASE]
        display_phase = "FOCUS FLOW" if phase == "FOCUS" else phase
        l1 = "{:^16}".format(display_phase[:16])

        # 3. Format Line 2: T:XX H:XX F:XX
        temp = environment.get("temperature", 0)
        hum = environment.get("humidity", 0)
        l2 = "T:{:.0f} H:{:.0f}% F:{:d}%".format(temp, hum, int(score))

        self._set_text(f"{l1}\n{l2}")
class OledSessionDisplay:
    def __init__(self) -> None:
        self._oled_available = False
        self._device = None
        self._font_status = None
        self._font_timer = None
        self._font_phase = None
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
            try:
                # Attempt to load premium fonts, fallback to default
                self._font_status = imagefont_module.truetype("DejaVuSans-Bold.ttf", 20)
                self._font_timer = imagefont_module.truetype("DejaVuSans.ttf", 32)
                self._font_phase = imagefont_module.truetype("DejaVuSans.ttf", 14)
            except Exception:
                default = imagefont_module.load_default()
                self._font_status = default
                self._font_timer = default
                self._font_phase = default
                
            self._oled_available = True
            print("[OLED] SH1107G initialized with enhanced fonts")
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

        try:
            with self._canvas(self._device) as draw:
                # 1. Background Frame (Active Area 96x96)
                draw.rectangle((0, 0, 95, 95), outline="white", width=1)
                draw.line((10, 30, 86, 30), fill="white") # Upper separator
                draw.line((10, 78, 86, 78), fill="white") # Lower separator
                
                # 2. Status (Centered, Top)
                try:
                    bbox = draw.textbbox((0, 0), status, font=self._font_status)
                    w = bbox[2] - bbox[0]
                except AttributeError:
                    w, _ = draw.textsize(status, font=self._font_status)
                draw.text(((96 - w) // 2, 6), status, fill="white", font=self._font_status)
                
                # 3. Phase (Centered, below separator)
                try:
                    bbox = draw.textbbox((0, 0), phase, font=self._font_phase)
                    w = bbox[2] - bbox[0]
                except AttributeError:
                    w, _ = draw.textsize(phase, font=self._font_phase)
                draw.text(((96 - w) // 2, 34), phase, fill="white", font=self._font_phase)
                
                # 4. Timer (Centered, Middle)
                try:
                    bbox = draw.textbbox((0, 0), timer, font=self._font_timer)
                    w = bbox[2] - bbox[0]
                except AttributeError:
                    w, _ = draw.textsize(timer, font=self._font_timer)
                draw.text(((96 - w) // 2, 48), timer, fill="white", font=self._font_timer)
                
                # 5. Decoration: subtle corner marks
                draw.line((2, 2, 8, 2), fill="white")
                draw.line((2, 2, 2, 8), fill="white")
                draw.line((88, 2, 94, 2), fill="white")
                draw.line((94, 2, 94, 8), fill="white")
                
        except Exception as ex:
            print(f"[OLED] Render Error: {ex}")