"""
atapiro 1337 #ONE - GUI Theme & Styling
"""

# Theme Palette (RGB packed for GDI 0x00BBGGRR)
# Note: Win32 GDI uses COLORREF: 0x00BBGGRR (Blue in high byte, Red in low byte)

def rgb(r, g, b):
    return (b << 16) | (g << 8) | r

COLOR_BG_DARK        = rgb(15, 17, 23)        # #0F1117
COLOR_PANEL_BG       = rgb(22, 25, 35)        # #161923
COLOR_PANEL_HEADER   = rgb(30, 34, 48)        # #1E2230
COLOR_PANEL_BORDER   = rgb(45, 52, 72)        # #2D3448

COLOR_ACCENT_CYAN    = rgb(0, 240, 255)       # Neon Cyan
COLOR_ACCENT_MAGENTA = rgb(255, 60, 180)      # Neon Magenta
COLOR_ACCENT_GREEN   = rgb(60, 255, 120)      # Neon Green
COLOR_ACCENT_GOLD    = rgb(255, 210, 40)      # Neon Gold
COLOR_ACCENT_RED     = rgb(255, 70, 70)       # Crimson

COLOR_TEXT_WHITE     = rgb(240, 245, 255)
COLOR_TEXT_DIM       = rgb(130, 140, 165)
COLOR_TEXT_MUTED     = rgb(80, 90, 115)

COLOR_BTN_OFF        = rgb(35, 40, 55)
COLOR_BTN_ON         = rgb(0, 200, 180)

CATEGORY_COLORS = {
    "Combat":   rgb(255, 75, 95),
    "Movement": rgb(60, 255, 130),
    "Player":   rgb(0, 220, 255),
    "Render":   rgb(255, 205, 50),
}
