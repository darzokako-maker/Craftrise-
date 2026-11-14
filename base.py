"""
atapiro 1337 #ONE - Base Module Architecture
"""

import sys
from ..core.memory import atapiro_set_color, atapiro_reset_color, FOREGROUND_GREEN, FOREGROUND_CYAN, FOREGROUND_INTENSITY

VK_NAMES = {
    0: "NONE",
    0x01: "M1",
    0x02: "M2",
    0x04: "M3",
    0x05: "M4",
    0x06: "M5",
    0x10: "SHIFT",
    0x11: "CTRL",
    0x12: "ALT",
    0x20: "SPACE",
    0x2D: "INS",
    0x2E: "DEL",
    0x70: "F1",
    0x71: "F2",
    0x72: "F3",
    0x73: "F4",
    0x74: "F5",
    0x75: "F6",
    0x76: "F7",
    0x77: "F8",
    0x78: "F9",
    0x79: "F10",
    0x7A: "F11",
    0x7B: "F12",
    0xA0: "LSHIFT",
    0xA1: "RSHIFT",
    0xA2: "LCTRL",
    0xA3: "RCTRL",
    0xDB: "[",
    0xDD: "]",
}

for i in range(ord('A'), ord('Z') + 1):
    VK_NAMES[i] = chr(i)
for i in range(ord('0'), ord('9') + 1):
    VK_NAMES[i] = chr(i)

class Module:
    def __init__(self, name, description, category, default_key=0, default_enabled=False, color=0x00FFD0):
        self.name = name
        self.description = description
        self.category = category
        self.keybind = default_key
        self.enabled = default_enabled
        self.color = color
        self._key_down = False
        self.settings = {}

    def get_key_name(self):
        return VK_NAMES.get(self.keybind, f"0x{self.keybind:02X}" if self.keybind else "NONE")

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.on_enable()
        else:
            self.on_disable()
        atapiro_set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY if self.enabled else FOREGROUND_CYAN)
        sys.stdout.write(f"\r[+] {self.name.lower()} {'ON ' if self.enabled else 'OFF'}   \n")
        sys.stdout.flush()
        atapiro_reset_color()
        return self.enabled

    def on_enable(self):
        pass

    def on_disable(self):
        pass

    def tick(self, ctx):
        pass

    def handle_key(self, is_down):
        fired = False
        if is_down and not self._key_down:
            self.toggle()
            fired = True
        self._key_down = is_down
        return fired
