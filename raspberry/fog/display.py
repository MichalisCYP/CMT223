from __future__ import annotations

import importlib
from typing import Dict, Any


class LedEnvironmentDisplay:
    """Grove-LCD RGB backlight display for environmental monitoring.
    
    Shows: Temperature, Humidity, Light, Sound levels.
    Backlight color reflects session status when available.
    """

    def __init__(self) -> None:
        self._lcd_module = None
        self._has_backlight = False
        try:
            self._lcd_module = importlib.import_module("grove_rgb_lcd")
            self._has_backlight = hasattr(self._lcd_module, "setRGB")
        except Exception:
            self._lcd_module = None

    def _set_backlight(self, r: int, g: int, b: int) -> None:
        """Set RGB backlight color if available."""
        if self._has_backlight and self._lcd_module is not None:
            try:
                setRGB = getattr(self._lcd_module, "setRGB", None)
                if setRGB is not None:
                    setRGB(r, g, b)
            except Exception:
                pass

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

        if self._lcd_module is not None:
            try:
                setText = getattr(self._lcd_module, "setText", None)
                if setText is not None:
                    setText(text)
                # Green backlight for normal operation
                self._set_backlight(0, 255, 0)
            except Exception:
                print("[LED] {} | move={}".format(text.replace("\n", " | "), environment.get("move", 0)))
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
