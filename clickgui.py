"""
atapiro 1337 #ONE - Interactive ClickGUI System
Extended with UpClip, DownClip, ClickTP & XyzTeleport Multi-Tab Sub-Settings
"""
import ctypes
import time
from .theme import (
    COLOR_BG_DARK, COLOR_PANEL_BG, COLOR_PANEL_HEADER, COLOR_PANEL_BORDER,
    COLOR_ACCENT_CYAN, COLOR_ACCENT_MAGENTA, COLOR_ACCENT_GREEN, COLOR_ACCENT_GOLD,
    COLOR_TEXT_WHITE, COLOR_TEXT_DIM, COLOR_TEXT_MUTED,
    COLOR_BTN_OFF, COLOR_BTN_ON, CATEGORY_COLORS, rgb
)
from ..core.memory import atapiro_key_down
from ..modules.base import VK_NAMES

_user32 = ctypes.windll.user32
_gdi32  = ctypes.windll.gdi32

_user32.GetCursorPos.argtypes = [ctypes.POINTER(ctypes.wintypes.POINT)]
_user32.GetCursorPos.restype = ctypes.c_bool

_user32.ScreenToClient.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.wintypes.POINT)]
_user32.ScreenToClient.restype = ctypes.c_bool

_user32.FillRect.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_void_p]
_user32.FillRect.restype = ctypes.c_int

_gdi32.GetStockObject.argtypes = [ctypes.c_int]
_gdi32.GetStockObject.restype = ctypes.c_void_p

_gdi32.CreateSolidBrush.argtypes = [ctypes.c_ulong]
_gdi32.CreateSolidBrush.restype = ctypes.c_void_p

_gdi32.CreatePen.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
_gdi32.CreatePen.restype = ctypes.c_void_p

_gdi32.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
_gdi32.SelectObject.restype = ctypes.c_void_p

_gdi32.DeleteObject.argtypes = [ctypes.c_void_p]
_gdi32.DeleteObject.restype = ctypes.c_bool

_gdi32.SetTextColor.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
_gdi32.SetTextColor.restype = ctypes.c_ulong

_gdi32.TextOutW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_wchar_p, ctypes.c_int]
_gdi32.TextOutW.restype = ctypes.c_bool

_gdi32.Rectangle.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
_gdi32.Rectangle.restype = ctypes.c_bool

def get_sub_height(m):
    if not getattr(m, 'expanded', False):
        return 0
    if m.name == "XyzTeleport":
        return 142
    if m.name in ("UpClip", "DownClip", "ClickTP"):
        return 74
    return 0

class Panel:
    def __init__(self, title, x, y, width=195):
        self.title = title
        self.x = x
        self.y = y
        self.width = width
        self.collapsed = False
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

class ClickGUI:
    def __init__(self, module_manager):
        self.mgr = module_manager
        self.open = False
        self.binding_module = None
        self.active_input_field = None  # 'x', 'y', or 'z'
        self.pressed_keys = set()
        self.lbutton_prev = False
        self.rbutton_prev = False
        self.active_panel_drag = None

        self.panels = {
            "Combat":   Panel("Combat", 60, 80),
            "Movement": Panel("Movement", 270, 80),
            "Player":   Panel("Player", 480, 80),
            "Render":   Panel("Render", 690, 80),
        }

    def toggle(self):
        self.open = not self.open
        self.binding_module = None
        self.active_input_field = None
        self.active_panel_drag = None
        return self.open

    def update_input(self, hwnd):
        if not self.open:
            return

        # Cursor pos
        pt = ctypes.wintypes.POINT()
        _user32.GetCursorPos(ctypes.byref(pt))
        _user32.ScreenToClient(hwnd, ctypes.byref(pt))
        mx, my = pt.x, pt.y

        lbutton = bool(_user32.GetAsyncKeyState(0x01) & 0x8000)
        clicked = lbutton and not self.lbutton_prev

        rbutton = bool(_user32.GetAsyncKeyState(0x02) & 0x8000)
        r_clicked = rbutton and not self.rbutton_prev

        # Keybind listening mode
        if self.binding_module:
            if atapiro_key_down(0x1B) or atapiro_key_down(0x2E) or atapiro_key_down(0x08):
                self.binding_module.keybind = 0
                self.binding_module = None
                self.mgr.save_config()
                self.lbutton_prev = lbutton
                self.rbutton_prev = rbutton
                return

            for vk in range(1, 255):
                if vk in (0x01, 0x02, 0x1B, 0x2D):
                    continue
                if atapiro_key_down(vk):
                    self.binding_module.keybind = vk
                    self.binding_module = None
                    self.mgr.save_config()
                    break

            self.lbutton_prev = lbutton
            self.rbutton_prev = rbutton
            return

        # Text input typing mode (for XyzTeleport X, Y, Z coordinate boxes)
        if self.active_input_field:
            tp = self.mgr.xyz_teleport

            # Enter or ESC to unfocus
            if atapiro_key_down(0x0D) or atapiro_key_down(0x1B):
                self.active_input_field = None
                self.lbutton_prev = lbutton
                self.rbutton_prev = rbutton
                return

            # Backspace
            if atapiro_key_down(0x08):
                if 0x08 not in self.pressed_keys:
                    self.pressed_keys.add(0x08)
                    curr = getattr(tp, f"{self.active_input_field}_str", "")
                    if curr:
                        setattr(tp, f"{self.active_input_field}_str", curr[:-1])
                        self.mgr.save_config()
            else:
                self.pressed_keys.discard(0x08)

            # Digits 0-9
            for vk in range(0x30, 0x3A):
                c = chr(vk)
                if atapiro_key_down(vk):
                    if vk not in self.pressed_keys:
                        self.pressed_keys.add(vk)
                        curr = getattr(tp, f"{self.active_input_field}_str", "")
                        if len(curr) < 14:
                            setattr(tp, f"{self.active_input_field}_str", curr + c)
                            self.mgr.save_config()
                else:
                    self.pressed_keys.discard(vk)

            # Numpad 0-9
            for vk in range(0x60, 0x6A):
                c = str(vk - 0x60)
                if atapiro_key_down(vk):
                    if vk not in self.pressed_keys:
                        self.pressed_keys.add(vk)
                        curr = getattr(tp, f"{self.active_input_field}_str", "")
                        if len(curr) < 14:
                            setattr(tp, f"{self.active_input_field}_str", curr + c)
                            self.mgr.save_config()
                else:
                    self.pressed_keys.discard(vk)

            # Minus '-'
            for vk in (0xBD, 0x6D):
                if atapiro_key_down(vk):
                    if vk not in self.pressed_keys:
                        self.pressed_keys.add(vk)
                        curr = getattr(tp, f"{self.active_input_field}_str", "")
                        if not curr:
                            setattr(tp, f"{self.active_input_field}_str", "-")
                            self.mgr.save_config()
                else:
                    self.pressed_keys.discard(vk)

            # Dot '.'
            for vk in (0xBE, 0x6E):
                if atapiro_key_down(vk):
                    if vk not in self.pressed_keys:
                        self.pressed_keys.add(vk)
                        curr = getattr(tp, f"{self.active_input_field}_str", "")
                        if "." not in curr and len(curr) < 14:
                            setattr(tp, f"{self.active_input_field}_str", curr + ".")
                            self.mgr.save_config()
                else:
                    self.pressed_keys.discard(vk)

        # Dragging panel header
        if self.active_panel_drag:
            if lbutton:
                p = self.active_panel_drag
                p.x = mx - p.drag_offset_x
                p.y = my - p.drag_offset_y
            else:
                self.active_panel_drag = None

        # Right-click handling: toggle expand/collapse for sub-settings
        if r_clicked:
            for cat_name, panel in self.panels.items():
                px, py, pw = panel.x, panel.y, panel.width
                header_h = 28
                modules = self.mgr.get_by_category(cat_name)
                curr_y = py + header_h + 4
                item_h = 26

                for m in modules:
                    if px + 6 <= mx <= px + pw - 6 and curr_y <= my <= curr_y + item_h - 2:
                        if hasattr(m, 'expanded'):
                            m.expanded = not m.expanded
                            if not m.expanded and m.name == "XyzTeleport":
                                self.active_input_field = None
                            break
                    curr_y += item_h + get_sub_height(m)

        # Left-click handling
        if clicked:
            clicked_inside_input = False
            for cat_name, panel in self.panels.items():
                px, py, pw = panel.x, panel.y, panel.width
                header_h = 28

                # Header click -> drag
                if px <= mx <= px + pw and py <= my <= py + header_h:
                    self.active_panel_drag = panel
                    panel.drag_offset_x = mx - px
                    panel.drag_offset_y = my - py
                    break

                modules = self.mgr.get_by_category(cat_name)
                curr_y = py + header_h + 4
                item_h = 26

                for m in modules:
                    # Toggle checkbox click
                    if px + 6 <= mx <= px + pw - 46 and curr_y <= my <= curr_y + item_h - 2:
                        m.toggle()
                        self.mgr.save_config()
                        break

                    # Keybind button click
                    if px + pw - 44 <= mx <= px + pw - 6 and curr_y <= my <= curr_y + item_h - 2:
                        self.binding_module = m
                        self.active_input_field = None
                        break

                    # Sub-settings click handling for UpClip / DownClip
                    if getattr(m, 'expanded', False) and m.name in ("UpClip", "DownClip"):
                        sub_y = curr_y + item_h
                        # [-] button: sub_y + 4
                        if px + 8 <= mx <= px + 36 and sub_y + 4 <= my <= sub_y + 24:
                            m.distance = max(0.5, round(m.distance - 1.0, 1))
                            self.mgr.save_config()
                        # [+] button: sub_y + 4
                        elif px + pw - 36 <= mx <= px + pw - 8 and sub_y + 4 <= my <= sub_y + 24:
                            m.distance = min(50.0, round(m.distance + 1.0, 1))
                            self.mgr.save_config()

                        # Presets: [ 2b ] [ 3b ] [ 5b ] [ 10b ]
                        elif sub_y + 26 <= my <= sub_y + 44:
                            pw_inner = pw - 16
                            step = pw_inner // 4
                            p1_x = px + 8
                            if p1_x <= mx <= p1_x + step - 2:
                                m.distance = 2.0
                                self.mgr.save_config()
                            elif p1_x + step <= mx <= p1_x + step * 2 - 2:
                                m.distance = 3.0
                                self.mgr.save_config()
                            elif p1_x + step * 2 <= mx <= p1_x + step * 3 - 2:
                                m.distance = 5.0
                                self.mgr.save_config()
                            elif p1_x + step * 3 <= mx <= px + pw - 8:
                                m.distance = 10.0
                                self.mgr.save_config()

                        # Action Trigger Button: sub_y + 48 to sub_y + 68
                        elif px + 8 <= mx <= px + pw - 8 and sub_y + 48 <= my <= sub_y + 68:
                            m._need_trigger = True

                    # Sub-settings click handling for ClickTP
                    if getattr(m, 'expanded', False) and m.name == "ClickTP":
                        sub_y = curr_y + item_h
                        # [-] button: sub_y + 4
                        if px + 8 <= mx <= px + 36 and sub_y + 4 <= my <= sub_y + 24:
                            m.distance = max(1.0, round(m.distance - 1.0, 1))
                            self.mgr.save_config()
                        # [+] button: sub_y + 4
                        elif px + pw - 36 <= mx <= px + pw - 8 and sub_y + 4 <= my <= sub_y + 24:
                            m.distance = min(100.0, round(m.distance + 1.0, 1))
                            self.mgr.save_config()

                        # Presets: [ 3m ] [ 5m ] [ 10m ] [ 20m ]
                        elif sub_y + 26 <= my <= sub_y + 44:
                            pw_inner = pw - 16
                            step = pw_inner // 4
                            p1_x = px + 8
                            if p1_x <= mx <= p1_x + step - 2:
                                m.distance = 3.0
                                self.mgr.save_config()
                            elif p1_x + step <= mx <= p1_x + step * 2 - 2:
                                m.distance = 5.0
                                self.mgr.save_config()
                            elif p1_x + step * 2 <= mx <= p1_x + step * 3 - 2:
                                m.distance = 10.0
                                self.mgr.save_config()
                            elif p1_x + step * 3 <= mx <= px + pw - 8:
                                m.distance = 20.0
                                self.mgr.save_config()

                        # Action Trigger Button: sub_y + 48 to sub_y + 68
                        elif px + 8 <= mx <= px + pw - 8 and sub_y + 48 <= my <= sub_y + 68:
                            m._need_trigger = True

                    # Sub-settings click handling for XyzTeleport
                    if getattr(m, 'expanded', False) and m.name == "XyzTeleport":
                        sub_y = curr_y + item_h

                        # X Input Box: sub_y + 4
                        if px + 30 <= mx <= px + pw - 12 and sub_y + 4 <= my <= sub_y + 24:
                            self.active_input_field = 'x'
                            clicked_inside_input = True

                        # Y Input Box: sub_y + 26
                        elif px + 30 <= mx <= px + pw - 12 and sub_y + 26 <= my <= sub_y + 46:
                            self.active_input_field = 'y'
                            clicked_inside_input = True

                        # Z Input Box: sub_y + 48
                        elif px + 30 <= mx <= px + pw - 12 and sub_y + 48 <= my <= sub_y + 68:
                            self.active_input_field = 'z'
                            clicked_inside_input = True

                        # Set XYZ (Current) button: sub_y + 72
                        elif px + 8 <= mx <= px + 104 and sub_y + 72 <= my <= sub_y + 90:
                            st = getattr(self.mgr, 'last_state', None)
                            if st and st.pos_y > 1.0:
                                m.set_target_coords(st.pos_x, st.pos_y, st.pos_z)
                                self.mgr.save_config()

                        # Clear button: sub_y + 72
                        elif px + 108 <= mx <= px + pw - 8 and sub_y + 72 <= my <= sub_y + 90:
                            m.x_str = ""
                            m.y_str = ""
                            m.z_str = ""
                            self.mgr.save_config()

                        # Loop Mode (C06) toggle: sub_y + 94
                        elif px + 8 <= mx <= px + pw - 8 and sub_y + 94 <= my <= sub_y + 112:
                            m.loop_mode = not m.loop_mode
                            if not m.loop_mode:
                                m.enabled = False
                            self.mgr.save_config()

                        # TELEPORT NOW button: sub_y + 116
                        elif px + 8 <= mx <= px + pw - 8 and sub_y + 116 <= my <= sub_y + 136:
                            m._need_trigger = True

                    curr_y += item_h + get_sub_height(m)

                # Render panel FOV control click handling
                if cat_name == "Render":
                    fov_y = curr_y + 2
                    if fov_y <= my <= fov_y + 20:
                        if px + 8 <= mx <= px + 34:
                            self.mgr.esp.fov = max(40.0, round(self.mgr.esp.fov - 1.0, 1))
                            self.mgr.save_config()
                            break
                        elif px + pw - 34 <= mx <= px + pw - 8:
                            self.mgr.esp.fov = min(130.0, round(self.mgr.esp.fov + 1.0, 1))
                            self.mgr.save_config()
                            break

            if not clicked_inside_input:
                self.active_input_field = None

        self.lbutton_prev = lbutton
        self.rbutton_prev = rbutton

    def render(self, hdc, hwnd):
        if not self.open:
            return

        pt = ctypes.wintypes.POINT()
        _user32.GetCursorPos(ctypes.byref(pt))
        _user32.ScreenToClient(hwnd, ctypes.byref(pt))
        mx, my = pt.x, pt.y

        null_brush = _gdi32.GetStockObject(5)
        now_sec = time.time()
        blink_cursor = int(now_sec * 2.5) % 2 == 0

        for cat_name, panel in self.panels.items():
            px, py, pw = panel.x, panel.y, panel.width
            modules = self.mgr.get_by_category(cat_name)
            extra_h = 32 if cat_name == "Render" else 8
            sub_h = sum(get_sub_height(m) for m in modules)
            total_h = 28 + len(modules) * 26 + extra_h + sub_h

            # Panel background
            bg_rect = ctypes.wintypes.RECT(px, py, px + pw, py + total_h)
            bg_brush = _gdi32.CreateSolidBrush(COLOR_PANEL_BG)
            _user32.FillRect(hdc, ctypes.byref(bg_rect), bg_brush)
            _gdi32.DeleteObject(bg_brush)

            # Panel border
            border_pen = _gdi32.CreatePen(0, 1, COLOR_PANEL_BORDER)
            old_pen = _gdi32.SelectObject(hdc, border_pen)
            old_brush = _gdi32.SelectObject(hdc, null_brush)
            _gdi32.Rectangle(hdc, px, py, px + pw, py + total_h)
            _gdi32.SelectObject(hdc, old_pen)
            _gdi32.SelectObject(hdc, old_brush)
            _gdi32.DeleteObject(border_pen)

            # Header background
            header_rect = ctypes.wintypes.RECT(px + 1, py + 1, px + pw - 1, py + 26)
            header_brush = _gdi32.CreateSolidBrush(COLOR_PANEL_HEADER)
            _user32.FillRect(hdc, ctypes.byref(header_rect), header_brush)
            _gdi32.DeleteObject(header_brush)

            # Category accent line
            cat_col = CATEGORY_COLORS.get(cat_name, COLOR_ACCENT_CYAN)
            line_rect = ctypes.wintypes.RECT(px + 1, py + 26, px + pw - 1, py + 28)
            cat_brush = _gdi32.CreateSolidBrush(cat_col)
            _user32.FillRect(hdc, ctypes.byref(line_rect), cat_brush)
            _gdi32.DeleteObject(cat_brush)

            # Header text
            _gdi32.SetTextColor(hdc, COLOR_TEXT_WHITE)
            _gdi32.TextOutW(hdc, px + 10, py + 6, panel.title, len(panel.title))

            def draw_sub_btn(rx1, ry1, rx2, ry2, text, text_col=COLOR_TEXT_WHITE, bg_col=rgb(30, 36, 52)):
                r = ctypes.wintypes.RECT(rx1, ry1, rx2, ry2)
                b = _gdi32.CreateSolidBrush(bg_col)
                _user32.FillRect(hdc, ctypes.byref(r), b)
                _gdi32.DeleteObject(b)
                _gdi32.SetTextColor(hdc, text_col)
                tx_pos = rx1 + max(2, (rx2 - rx1 - len(text) * 7) // 2)
                _gdi32.TextOutW(hdc, tx_pos, ry1 + 2, text, len(text))

            # Modules list
            curr_y = py + 30
            for m in modules:
                # Hover highlight
                is_hover = (px + 6 <= mx <= px + pw - 6 and curr_y <= my <= curr_y + 24)
                if is_hover:
                    hover_rect = ctypes.wintypes.RECT(px + 4, curr_y, px + pw - 4, curr_y + 24)
                    hover_brush = _gdi32.CreateSolidBrush(rgb(35, 42, 58))
                    _user32.FillRect(hdc, ctypes.byref(hover_rect), hover_brush)
                    _gdi32.DeleteObject(hover_brush)

                # State checkbox pill
                box_col = m.color if m.enabled else COLOR_BTN_OFF
                btn_brush = _gdi32.CreateSolidBrush(box_col)
                btn_rect = ctypes.wintypes.RECT(px + 8, curr_y + 4, px + 18, curr_y + 18)
                _user32.FillRect(hdc, ctypes.byref(btn_rect), btn_brush)
                _gdi32.DeleteObject(btn_brush)

                # Module Name
                name_col = COLOR_TEXT_WHITE if m.enabled else COLOR_TEXT_DIM
                _gdi32.SetTextColor(hdc, name_col)
                _gdi32.TextOutW(hdc, px + 24, curr_y + 3, m.name, len(m.name))

                # Expandable indicator
                if hasattr(m, 'expanded'):
                    ind_txt = "[-]" if m.expanded else "[+]"
                    _gdi32.SetTextColor(hdc, COLOR_ACCENT_MAGENTA)
                    _gdi32.TextOutW(hdc, px + pw - 62, curr_y + 3, ind_txt, len(ind_txt))

                # Keybind pill
                is_binding_this = (self.binding_module == m)
                key_txt = "[...]" if is_binding_this else f"[{m.get_key_name()}]"
                key_col = COLOR_ACCENT_GOLD if is_binding_this else COLOR_TEXT_MUTED
                _gdi32.SetTextColor(hdc, key_col)
                kx = px + pw - len(key_txt) * 7 - 8
                _gdi32.TextOutW(hdc, kx, curr_y + 3, key_txt, len(key_txt))

                # Render expanded sub-settings for UpClip & DownClip
                if getattr(m, 'expanded', False) and m.name in ("UpClip", "DownClip"):
                    sub_y = curr_y + 26
                    sub_rect = ctypes.wintypes.RECT(px + 6, sub_y, px + pw - 6, sub_y + 70)
                    sub_brush = _gdi32.CreateSolidBrush(rgb(16, 20, 30))
                    _user32.FillRect(hdc, ctypes.byref(sub_rect), sub_brush)
                    _gdi32.DeleteObject(sub_brush)

                    # Sub border
                    sub_pen = _gdi32.CreatePen(0, 1, rgb(42, 50, 72))
                    old_p = _gdi32.SelectObject(hdc, sub_pen)
                    old_b = _gdi32.SelectObject(hdc, null_brush)
                    _gdi32.Rectangle(hdc, px + 6, sub_y, px + pw - 6, sub_y + 70)
                    _gdi32.SelectObject(hdc, old_p)
                    _gdi32.SelectObject(hdc, old_b)
                    _gdi32.DeleteObject(sub_pen)

                    # Row 1: [-]  Distance: X.X blocks  [+]
                    draw_sub_btn(px + 8, sub_y + 4, px + 36, sub_y + 22, "-", COLOR_ACCENT_CYAN, rgb(28, 36, 50))
                    dist_lbl = f"Distance: {m.distance:.1f}b"
                    _gdi32.SetTextColor(hdc, COLOR_TEXT_WHITE)
                    _gdi32.TextOutW(hdc, px + 44, sub_y + 5, dist_lbl, len(dist_lbl))
                    draw_sub_btn(px + pw - 36, sub_y + 4, px + pw - 8, sub_y + 22, "+", COLOR_ACCENT_CYAN, rgb(28, 36, 50))

                    # Row 2: Presets [ 2b ] [ 3b ] [ 5b ] [ 10b ]
                    pw_inner = pw - 16
                    step = pw_inner // 4
                    p1_x = px + 8
                    draw_sub_btn(p1_x, sub_y + 26, p1_x + step - 2, sub_y + 44, "2b", COLOR_TEXT_DIM, rgb(24, 28, 40))
                    draw_sub_btn(p1_x + step, sub_y + 26, p1_x + step * 2 - 2, sub_y + 44, "3b", COLOR_TEXT_DIM, rgb(24, 28, 40))
                    draw_sub_btn(p1_x + step * 2, sub_y + 26, p1_x + step * 3 - 2, sub_y + 44, "5b", COLOR_TEXT_DIM, rgb(24, 28, 40))
                    draw_sub_btn(p1_x + step * 3, sub_y + 26, px + pw - 8, sub_y + 44, "10b", COLOR_TEXT_DIM, rgb(24, 28, 40))

                    # Row 3: Action Trigger button
                    btn_text = ">> TRIGGER UPCLIP <<" if m.name == "UpClip" else ">> TRIGGER DOWNCLIP <<"
                    draw_sub_btn(px + 8, sub_y + 48, px + pw - 8, sub_y + 68, btn_text, COLOR_ACCENT_CYAN, rgb(20, 42, 60))

                    curr_y += 74

                # Render expanded sub-settings for ClickTP
                elif getattr(m, 'expanded', False) and m.name == "ClickTP":
                    sub_y = curr_y + 26
                    sub_rect = ctypes.wintypes.RECT(px + 6, sub_y, px + pw - 6, sub_y + 70)
                    sub_brush = _gdi32.CreateSolidBrush(rgb(16, 20, 30))
                    _user32.FillRect(hdc, ctypes.byref(sub_rect), sub_brush)
                    _gdi32.DeleteObject(sub_brush)

                    # Sub border
                    sub_pen = _gdi32.CreatePen(0, 1, rgb(42, 50, 72))
                    old_p = _gdi32.SelectObject(hdc, sub_pen)
                    old_b = _gdi32.SelectObject(hdc, null_brush)
                    _gdi32.Rectangle(hdc, px + 6, sub_y, px + pw - 6, sub_y + 70)
                    _gdi32.SelectObject(hdc, old_p)
                    _gdi32.SelectObject(hdc, old_b)
                    _gdi32.DeleteObject(sub_pen)

                    # Row 1: [-]  Distance: X.X m  [+]
                    draw_sub_btn(px + 8, sub_y + 4, px + 36, sub_y + 22, "-", COLOR_ACCENT_GOLD, rgb(38, 36, 24))
                    dist_lbl = f"Forward: {m.distance:.1f}m"
                    _gdi32.SetTextColor(hdc, COLOR_TEXT_WHITE)
                    _gdi32.TextOutW(hdc, px + 44, sub_y + 5, dist_lbl, len(dist_lbl))
                    draw_sub_btn(px + pw - 36, sub_y + 4, px + pw - 8, sub_y + 22, "+", COLOR_ACCENT_GOLD, rgb(38, 36, 24))

                    # Row 2: Presets [ 3m ] [ 5m ] [ 10m ] [ 20m ]
                    pw_inner = pw - 16
                    step = pw_inner // 4
                    p1_x = px + 8
                    draw_sub_btn(p1_x, sub_y + 26, p1_x + step - 2, sub_y + 44, "3m", COLOR_TEXT_DIM, rgb(24, 28, 40))
                    draw_sub_btn(p1_x + step, sub_y + 26, p1_x + step * 2 - 2, sub_y + 44, "5m", COLOR_TEXT_DIM, rgb(24, 28, 40))
                    draw_sub_btn(p1_x + step * 2, sub_y + 26, p1_x + step * 3 - 2, sub_y + 44, "10m", COLOR_TEXT_DIM, rgb(24, 28, 40))
                    draw_sub_btn(p1_x + step * 3, sub_y + 26, px + pw - 8, sub_y + 44, "20m", COLOR_TEXT_DIM, rgb(24, 28, 40))

                    # Row 3: Action Trigger button
                    draw_sub_btn(px + 8, sub_y + 48, px + pw - 8, sub_y + 68, ">> TELEPORT FORWARD <<", COLOR_ACCENT_GOLD, rgb(46, 40, 20))

                    curr_y += 74

                # Render expanded sub-settings for XyzTeleport
                elif getattr(m, 'expanded', False) and m.name == "XyzTeleport":
                    sub_y = curr_y + 26
                    sub_rect = ctypes.wintypes.RECT(px + 6, sub_y, px + pw - 6, sub_y + 138)
                    sub_brush = _gdi32.CreateSolidBrush(rgb(16, 20, 30))
                    _user32.FillRect(hdc, ctypes.byref(sub_rect), sub_brush)
                    _gdi32.DeleteObject(sub_brush)

                    # Sub border
                    sub_pen = _gdi32.CreatePen(0, 1, rgb(42, 50, 72))
                    old_p = _gdi32.SelectObject(hdc, sub_pen)
                    old_b = _gdi32.SelectObject(hdc, null_brush)
                    _gdi32.Rectangle(hdc, px + 6, sub_y, px + pw - 6, sub_y + 138)
                    _gdi32.SelectObject(hdc, old_p)
                    _gdi32.SelectObject(hdc, old_b)
                    _gdi32.DeleteObject(sub_pen)

                    def render_input_box(label, val_str, by, is_active):
                        _gdi32.SetTextColor(hdc, COLOR_TEXT_DIM)
                        _gdi32.TextOutW(hdc, px + 12, by + 2, label, len(label))

                        bx1 = px + 30
                        bx2 = px + pw - 12
                        by1 = by
                        by2 = by + 20

                        box_bg = rgb(24, 30, 44) if not is_active else rgb(20, 35, 54)
                        b_brush = _gdi32.CreateSolidBrush(box_bg)
                        b_rect = ctypes.wintypes.RECT(bx1, by1, bx2, by2)
                        _user32.FillRect(hdc, ctypes.byref(b_rect), b_brush)
                        _gdi32.DeleteObject(b_brush)

                        pen_col = COLOR_ACCENT_CYAN if is_active else rgb(55, 66, 92)
                        b_pen = _gdi32.CreatePen(0, 1, pen_col)
                        p1 = _gdi32.SelectObject(hdc, b_pen)
                        p2 = _gdi32.SelectObject(hdc, null_brush)
                        _gdi32.Rectangle(hdc, bx1, by1, bx2, by2)
                        _gdi32.SelectObject(hdc, p1)
                        _gdi32.SelectObject(hdc, p2)
                        _gdi32.DeleteObject(b_pen)

                        disp_str = val_str
                        if is_active and blink_cursor:
                            disp_str += "|"
                        if disp_str:
                            _gdi32.SetTextColor(hdc, COLOR_TEXT_WHITE if val_str else COLOR_ACCENT_CYAN)
                            _gdi32.TextOutW(hdc, bx1 + 6, by1 + 2, disp_str, len(disp_str))

                    # 1. X Input Box
                    render_input_box("x:", m.x_str, sub_y + 4, self.active_input_field == 'x')

                    # 2. Y Input Box
                    render_input_box("y:", m.y_str, sub_y + 26, self.active_input_field == 'y')

                    # 3. Z Input Box
                    render_input_box("z:", m.z_str, sub_y + 48, self.active_input_field == 'z')

                    # 4. Set XYZ (Current) & Clear buttons
                    draw_sub_btn(px + 8, sub_y + 72, px + 104, sub_y + 90, "Set XYZ", COLOR_ACCENT_CYAN, rgb(26, 38, 56))
                    draw_sub_btn(px + 108, sub_y + 72, px + pw - 8, sub_y + 90, "Clear", COLOR_TEXT_MUTED, rgb(32, 34, 46))

                    # 5. Loop Mode (C06) toggle
                    loop_txt = "C06 Loop: [ ON ]" if m.loop_mode else "C06 Loop: [ OFF ]"
                    loop_col = COLOR_ACCENT_GREEN if m.loop_mode else COLOR_TEXT_MUTED
                    draw_sub_btn(px + 8, sub_y + 94, px + pw - 8, sub_y + 112, loop_txt, loop_col, rgb(26, 32, 44))

                    # 6. TELEPORT NOW
                    draw_sub_btn(px + 8, sub_y + 116, px + pw - 8, sub_y + 136, ">> TELEPORT NOW <<", COLOR_ACCENT_MAGENTA, rgb(46, 26, 52))

                    curr_y += 142

                curr_y += 26

            # Render panel FOV control
            if cat_name == "Render":
                fov_y = curr_y + 4
                btn_m = ctypes.wintypes.RECT(px + 8, fov_y, px + 34, fov_y + 20)
                b1 = _gdi32.CreateSolidBrush(rgb(38, 44, 60))
                _user32.FillRect(hdc, ctypes.byref(btn_m), b1)
                _gdi32.DeleteObject(b1)
                _gdi32.SetTextColor(hdc, COLOR_ACCENT_CYAN)
                _gdi32.TextOutW(hdc, px + 16, fov_y + 2, "-", 1)

                fov_txt = f"FOV: {self.mgr.esp.fov:.1f}\u00b0"
                _gdi32.SetTextColor(hdc, COLOR_TEXT_WHITE)
                _gdi32.TextOutW(hdc, px + 44, fov_y + 2, fov_txt, len(fov_txt))

                btn_p = ctypes.wintypes.RECT(px + pw - 34, fov_y, px + pw - 8, fov_y + 20)
                b2 = _gdi32.CreateSolidBrush(rgb(38, 44, 60))
                _user32.FillRect(hdc, ctypes.byref(btn_p), b2)
                _gdi32.DeleteObject(b2)
                _gdi32.SetTextColor(hdc, COLOR_ACCENT_CYAN)
                _gdi32.TextOutW(hdc, px + pw - 24, fov_y + 2, "+", 1)

        # Draw custom neon arrow cursor
        cur_brush = _gdi32.CreateSolidBrush(COLOR_ACCENT_CYAN)
        for i in range(12):
            w_line = max(1, 10 - i)
            c_rect = ctypes.wintypes.RECT(mx, my + i, mx + w_line, my + i + 1)
            _user32.FillRect(hdc, ctypes.byref(c_rect), cur_brush)
        _gdi32.DeleteObject(cur_brush)