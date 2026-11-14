"""
atapiro 1337 #ONE - Premium Watermark Renderer
"""
import ctypes
from .theme import (
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_ACCENT_CYAN,
    COLOR_ACCENT_MAGENTA, COLOR_ACCENT_GOLD, COLOR_ACCENT_GREEN,
    COLOR_TEXT_WHITE, COLOR_TEXT_DIM
)

_gdi32 = ctypes.windll.gdi32
_user32 = ctypes.windll.user32

class WatermarkRenderer:
    def __init__(self):
        self.x = 18
        self.y = 16
        self.width = 340
        self.height = 32
        self._bg_brush = 0
        self._border_pen = 0
        self._accent_brush = 0
        self._null_brush = 0

    def _ensure_gdi(self):
        if not self._bg_brush:
            self._bg_brush = _gdi32.CreateSolidBrush(COLOR_PANEL_BG)
            self._border_pen = _gdi32.CreatePen(0, 1, COLOR_PANEL_BORDER)
            self._accent_brush = _gdi32.CreateSolidBrush(COLOR_ACCENT_CYAN)
            self._null_brush = _gdi32.GetStockObject(5)

    def render(self, hdc, fov, fps=60):
        self._ensure_gdi()

        # Background rect
        rect = ctypes.wintypes.RECT(self.x, self.y, self.x + self.width, self.y + self.height)
        _user32.FillRect(hdc, ctypes.byref(rect), self._bg_brush)

        # Border
        old_pen = _gdi32.SelectObject(hdc, self._border_pen)
        old_brush = _gdi32.SelectObject(hdc, self._null_brush)
        _gdi32.Rectangle(hdc, self.x, self.y, self.x + self.width, self.y + self.height)

        # Accent top glow strip
        top_rect = ctypes.wintypes.RECT(self.x + 1, self.y + 1, self.x + self.width - 1, self.y + 3)
        _user32.FillRect(hdc, ctypes.byref(top_rect), self._accent_brush)

        _gdi32.SelectObject(hdc, old_pen)
        _gdi32.SelectObject(hdc, old_brush)

        # Text rendering
        cx = self.x + 10
        cy = self.y + 8

        # "ATAPIRO"
        _gdi32.SetTextColor(hdc, COLOR_ACCENT_CYAN)
        t1 = "ATAPIRO"
        _gdi32.TextOutW(hdc, cx, cy, t1, len(t1))
        cx += len(t1) * 8 + 6

        # "1337"
        _gdi32.SetTextColor(hdc, COLOR_ACCENT_GOLD)
        t2 = "1337"
        _gdi32.TextOutW(hdc, cx, cy, t2, len(t2))
        cx += len(t2) * 8 + 4

        # "#ONE"
        _gdi32.SetTextColor(hdc, COLOR_ACCENT_MAGENTA)
        t3 = "#ONE"
        _gdi32.TextOutW(hdc, cx, cy, t3, len(t3))
        cx += len(t3) * 8 + 8

        # Divider "|"
        _gdi32.SetTextColor(hdc, COLOR_TEXT_DIM)
        div = "|"
        _gdi32.TextOutW(hdc, cx, cy, div, len(div))
        cx += 12

        # "FOV: XX.X°"
        _gdi32.SetTextColor(hdc, COLOR_ACCENT_GREEN)
        t4 = f"FOV: {fov:.1f}\u00b0"
        _gdi32.TextOutW(hdc, cx, cy, t4, len(t4))
        cx += len(t4) * 8 + 10

        # "[CraftRise]"
        _gdi32.SetTextColor(hdc, COLOR_TEXT_DIM)
        t5 = "[CR]"
        _gdi32.TextOutW(hdc, cx, cy, t5, len(t5))
