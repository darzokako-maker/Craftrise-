"""
atapiro 1337 #ONE - Master Overlay & ESP Renderer
High-FPS Zero-Stutter Cached GDI Backbuffer & Bulk RPM Pipeline
"""
import ctypes
import ctypes.wintypes
import math
import struct
import threading
import time
from .clickgui import ClickGUI
from .watermark import WatermarkRenderer
from .theme import COLOR_ACCENT_CYAN, COLOR_TEXT_WHITE, rgb
from ..core.memory import (
    _user32, _gdi32, _kernel32,
    atapiro_read_bytes, atapiro_read_u32,
    atapiro_get_player_name, atapiro_clear_name_cache,
    OFFSET_ARRAY_LIST_SIZE, ARRAY_OBJ_BASE
)

WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, ctypes.c_void_p, ctypes.c_uint, ctypes.c_ulonglong, ctypes.c_longlong)

def _overlay_wndproc(hwnd, msg, wp, lp):
    return _user32.DefWindowProcW(hwnd, msg, wp, lp)

_g_wndproc = WNDPROC(_overlay_wndproc)

class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ('cbSize',        ctypes.c_uint),
        ('style',         ctypes.c_uint),
        ('lpfnWndProc',   WNDPROC),
        ('cbClsExtra',    ctypes.c_int),
        ('cbWndExtra',    ctypes.c_int),
        ('hInstance',     ctypes.c_void_p),
        ('hIcon',         ctypes.c_void_p),
        ('hCursor',       ctypes.c_void_p),
        ('hbrBackground', ctypes.c_void_p),
        ('lpszMenuName',  ctypes.c_wchar_p),
        ('lpszClassName', ctypes.c_wchar_p),
        ('hIconSm',       ctypes.c_void_p)
    ]

def atapiro_world_to_screen(cx, cy, cz, yaw, pitch, tx, ty, tz, sw, sh, fov_deg=91.0):
    p = max(-89.9, min(89.9, pitch))
    kDeg = 0.017453292519943295
    yaw_rad = yaw * kDeg
    pit_rad = p * kDeg

    cy_val = math.cos(yaw_rad)
    sy_val = math.sin(yaw_rad)
    cp_val = math.cos(pit_rad)
    sp_val = math.sin(pit_rad)

    dx = tx - cx
    dy = ty - cy
    dz = tz - cz

    zf = (-cp_val * sy_val) * dx + (-sp_val) * dy + (cp_val * cy_val) * dz
    if zf <= 0.10:
        return None

    xr = (-cy_val) * dx + (-sy_val) * dz
    yu = (-sp_val * sy_val) * dx + cp_val * dy + (sp_val * cy_val) * dz

    aspect = float(sw) / float(sh)
    f_scale = 1.0 / math.tan(fov_deg * 0.5 * kDeg)

    px = (f_scale / aspect) * (xr / zf)
    py = f_scale * (yu / zf)

    sx = (px + 1.0) * 0.5 * sw
    sy = (1.0 - py) * 0.5 * sh
    return sx, sy, zf

class OverlayManager:
    def __init__(self, pid, h, offsets, module_manager):
        self.pid = pid
        self.h = h
        self.offsets = offsets
        self.mgr = module_manager
        self.clickgui = ClickGUI(module_manager)
        self.watermark = WatermarkRenderer()

        self.hwnd = 0
        self.cr_hwnd = 0
        self.state = None
        self.running = True
        self.show_guide = False

        self._init_win32_types()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _init_win32_types(self):
        _user32.DefWindowProcW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_ulonglong, ctypes.c_longlong]
        _user32.DefWindowProcW.restype = ctypes.c_longlong
        _user32.CreateWindowExW.argtypes = [
            ctypes.c_ulong, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_ulong,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        ]
        _user32.CreateWindowExW.restype = ctypes.c_void_p
        _user32.GetDC.argtypes = [ctypes.c_void_p]
        _user32.GetDC.restype = ctypes.c_void_p
        _user32.ReleaseDC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        _user32.ReleaseDC.restype = ctypes.c_int
        _user32.FillRect.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_void_p]
        _user32.FillRect.restype = ctypes.c_int
        _gdi32.CreateCompatibleDC.argtypes = [ctypes.c_void_p]
        _gdi32.CreateCompatibleDC.restype = ctypes.c_void_p
        _gdi32.CreateCompatibleBitmap.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        _gdi32.CreateCompatibleBitmap.restype = ctypes.c_void_p
        _gdi32.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        _gdi32.SelectObject.restype = ctypes.c_void_p
        _gdi32.DeleteObject.argtypes = [ctypes.c_void_p]
        _gdi32.DeleteObject.restype = ctypes.c_bool
        _gdi32.DeleteDC.argtypes = [ctypes.c_void_p]
        _gdi32.DeleteDC.restype = ctypes.c_bool
        _gdi32.CreateSolidBrush.argtypes = [ctypes.c_ulong]
        _gdi32.CreateSolidBrush.restype = ctypes.c_void_p
        _gdi32.CreatePen.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
        _gdi32.CreatePen.restype = ctypes.c_void_p
        _gdi32.CreateFontW.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong,
            ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_wchar_p
        ]
        _gdi32.CreateFontW.restype = ctypes.c_void_p
        _gdi32.SetTextColor.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        _gdi32.SetTextColor.restype = ctypes.c_ulong
        _gdi32.SetBkMode.argtypes = [ctypes.c_void_p, ctypes.c_int]
        _gdi32.SetBkMode.restype = ctypes.c_int
        _gdi32.TextOutW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_wchar_p, ctypes.c_int]
        _gdi32.TextOutW.restype = ctypes.c_bool
        _gdi32.Rectangle.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        _gdi32.Rectangle.restype = ctypes.c_bool
        _gdi32.BitBlt.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_ulong
        ]
        _gdi32.BitBlt.restype = ctypes.c_bool

    def update_state(self, st):
        self.state = st

    def toggle_clickgui(self):
        return self.clickgui.toggle()

    def _find_craftrise_hwnd(self):
        h = _user32.FindWindowW(None, "CraftRise")
        if h:
            return h
        res = [0]
        def cb(w, lp):
            pid = ctypes.c_ulong(0)
            _user32.GetWindowThreadProcessId(w, ctypes.byref(pid))
            if pid.value == self.pid and _user32.IsWindowVisible(w):
                res[0] = w
                return False
            return True
        cb_func = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(cb)
        _user32.EnumWindows(cb_func, 0)
        return res[0]

    def _run(self):
        try:
            _user32.SetProcessWindowStation(_user32.OpenWindowStationW("WinSta0", False, 0x02000000))
            _user32.SetThreadDesktop(_user32.OpenDesktopW("Default", 0, False, 0x02000000))
        except Exception:
            pass

        h_inst = _kernel32.GetModuleHandleW(None)
        wc = WNDCLASSEXW()
        wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wc.style = 3
        wc.lpfnWndProc = _g_wndproc
        wc.hInstance = h_inst
        wc.lpszClassName = "AtapiroClickGUIOverlay"
        _user32.RegisterClassExW(ctypes.byref(wc))

        WS_EX_TOPMOST = 0x00000008
        WS_EX_TRANSPARENT = 0x00000020
        WS_EX_LAYERED = 0x00080000
        WS_EX_TOOLWINDOW = 0x00000080
        WS_EX_NOACTIVATE = 0x08000000
        WS_POPUP = 0x80000000

        self.hwnd = _user32.CreateWindowExW(
            WS_EX_TOPMOST | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE,
            wc.lpszClassName,
            "AtapiroOverlay",
            WS_POPUP,
            0, 0, 1920, 1080,
            None, None, h_inst, None
        )

        LWA_COLORKEY = 1
        _user32.SetLayeredWindowAttributes(self.hwnd, 0x000000, 0, LWA_COLORKEY)
        _user32.ShowWindow(self.hwnd, 5)

        brush_black = _gdi32.CreateSolidBrush(0x000000)
        null_brush = _gdi32.GetStockObject(5)
        pen_box = _gdi32.CreatePen(0, 2, 0x00FFD0)

        font_sub = _gdi32.CreateFontW(14, 0, 0, 0, 600, 0, 0, 0, 0, 0, 0, 2, 0, "Segoe UI")
        font_esp = _gdi32.CreateFontW(12, 0, 0, 0, 600, 0, 0, 0, 0, 0, 0, 2, 0, "Tahoma")

        msg = ctypes.wintypes.MSG()
        last_bounds = None
        is_shown = True
        cached_dc = 0
        cached_bmp = 0
        cached_w = 0
        cached_h = 0

        while self.running:
            while _user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
                _user32.TranslateMessage(ctypes.byref(msg))
                _user32.DispatchMessageW(ctypes.byref(msg))

            if not self.cr_hwnd or not _user32.IsWindow(self.cr_hwnd):
                self.cr_hwnd = self._find_craftrise_hwnd()
                if not self.cr_hwnd:
                    time.sleep(0.1)
                    continue

            fg = _user32.GetForegroundWindow()
            is_fg = (fg == self.cr_hwnd or fg == self.hwnd)
            is_iconic = _user32.IsIconic(self.cr_hwnd)

            if not is_fg or is_iconic:
                if is_shown:
                    _user32.ShowWindow(self.hwnd, 0)
                    is_shown = False
                time.sleep(0.02)
                continue

            rect = ctypes.wintypes.RECT()
            _user32.GetClientRect(self.cr_hwnd, ctypes.byref(rect))
            pt = ctypes.wintypes.POINT(0, 0)
            _user32.ClientToScreen(self.cr_hwnd, ctypes.byref(pt))
            w = rect.right
            h = rect.bottom

            if w <= 100 or h <= 100:
                time.sleep(0.02)
                continue

            cur_bounds = (pt.x, pt.y, w, h)
            if cur_bounds != last_bounds or not is_shown:
                _user32.SetWindowPos(self.hwnd, ctypes.c_void_p(-1), pt.x, pt.y, w, h, 0x0010 | 0x0040)
                if not is_shown:
                    _user32.ShowWindow(self.hwnd, 5)
                    is_shown = True
                last_bounds = cur_bounds

            try:
                self.clickgui.update_input(self.hwnd)

                hdc = _user32.GetDC(self.hwnd)
                if not hdc:
                    time.sleep(0.005)
                    continue

                if not cached_dc or w != cached_w or h != cached_h:
                    if cached_bmp:
                        _gdi32.DeleteObject(cached_bmp)
                    if cached_dc:
                        _gdi32.DeleteDC(cached_dc)
                    cached_dc = _gdi32.CreateCompatibleDC(hdc)
                    cached_bmp = _gdi32.CreateCompatibleBitmap(hdc, w, h)
                    _gdi32.SelectObject(cached_dc, cached_bmp)
                    _gdi32.SetBkMode(cached_dc, 1)
                    cached_w, cached_h = w, h

                mem_dc = cached_dc
                _user32.FillRect(mem_dc, ctypes.byref(rect), brush_black)
                _gdi32.SelectObject(mem_dc, font_sub)

                # 1. Render Watermark
                if self.mgr.watermark.enabled:
                    self.watermark.render(mem_dc, self.mgr.esp.fov)

                # 2. Render Active Modules ArrayList (top right)
                if self.mgr.arraylist.enabled:
                    ay = 16
                    for mod_name, mod_col in self.mgr.get_active_list():
                        _gdi32.SetTextColor(mem_dc, mod_col)
                        ax = w - len(mod_name) * 8 - 30
                        _gdi32.TextOutW(mem_dc, ax, ay, mod_name, len(mod_name))
                        ay += 18

                # 3. Render ESP & Nametags with instant live camera read
                st = self.state
                if st and st.world_obj and st.world_obj != getattr(self, '_last_world_obj', 0):
                    self._last_world_obj = st.world_obj
                    atapiro_clear_name_cache()

                if self.mgr.esp.enabled and st and st.world_obj and st.player_obj:
                    p_offset = self.offsets.get("World.playerEntities", 232)
                    lst = atapiro_read_u32(self.h, st.world_obj + p_offset)
                    if lst:
                        lst_hdr = atapiro_read_bytes(self.h, (lst << 3) + OFFSET_ARRAY_LIST_SIZE, 8)
                        if lst_hdr:
                            sz, dt = struct.unpack('<iI', lst_hdr)
                            if dt and 0 < sz <= 100:
                                arr = dt << 3
                                ptrs_buf = atapiro_read_bytes(self.h, arr + ARRAY_OBJ_BASE, sz * 4)
                                px_off = self.offsets.get("Entity.posX", 64)
                                py_off = self.offsets.get("Entity.posY", 48)
                                pz_off = self.offsets.get("Entity.posZ", 80)
                                yaw_off = self.offsets.get("Entity.rotationYaw", 148)
                                pit_off = self.offsets.get("Entity.rotationPitch", 136)
                                eid_off = self.offsets.get("Entity.entityId", 160)

                                # Read local player camera directly right now for 0ms lag!
                                cam_buf = atapiro_read_bytes(self.h, st.player_obj, 256)
                                if ptrs_buf and cam_buf:
                                    cx = struct.unpack_from('<d', cam_buf, px_off)[0]
                                    cy = struct.unpack_from('<d', cam_buf, py_off)[0] + 1.62
                                    cz = struct.unpack_from('<d', cam_buf, pz_off)[0]
                                    yaw = struct.unpack_from('<f', cam_buf, yaw_off)[0]
                                    pitch = struct.unpack_from('<f', cam_buf, pit_off)[0]
                                else:
                                    cx = st.pos_x
                                    cy = st.pos_y + 1.62
                                    cz = st.pos_z
                                    yaw = st.rotation_yaw
                                    pitch = st.rotation_pitch

                                fov = self.mgr.esp.fov
                                kDeg = 0.017453292519943295
                                f_scale = 1.0 / math.tan(fov * 0.5 * kDeg)

                                _gdi32.SelectObject(mem_dc, pen_box)
                                _gdi32.SelectObject(mem_dc, null_brush)
                                _gdi32.SelectObject(mem_dc, font_esp)

                                ptrs = struct.unpack(f'<{sz}I', ptrs_buf) if ptrs_buf else ()
                                for e_ptr in ptrs:
                                    if not e_ptr:
                                        continue
                                    e = e_ptr << 3
                                    if e == st.player_obj:
                                        continue

                                    # Read Entity struct (0..256) in 1 single RPM call and unpack dynamically
                                    ebuf = atapiro_read_bytes(self.h, e, 256)
                                    if not ebuf:
                                        continue
                                    ex = struct.unpack_from('<d', ebuf, px_off)[0]
                                    ey = struct.unpack_from('<d', ebuf, py_off)[0]
                                    ez = struct.unpack_from('<d', ebuf, pz_off)[0]
                                    if ex == 0.0 and ey == 0.0 and ez == 0.0:
                                        continue
                                    eid = struct.unpack_from('<i', ebuf, eid_off)[0]
                                    pname = atapiro_get_player_name(self.h, e, eid)
                                    if pname.startswith("[CR]"):
                                        continue

                                    dx = ex - cx
                                    dy = ey - (cy - 1.62)
                                    dz = ez - cz
                                    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
                                    if dist > 120.0 or dist < 0.2:
                                        continue

                                    pt_bot = atapiro_world_to_screen(cx, cy, cz, yaw, pitch, ex, ey, ez, w, h, fov)
                                    pt_top = atapiro_world_to_screen(cx, cy, cz, yaw, pitch, ex, ey + 1.85, ez, w, h, fov)

                                    if not pt_bot and not pt_top:
                                        continue

                                    if pt_bot and pt_top:
                                        mid_x = (pt_bot[0] + pt_top[0]) * 0.5
                                        box_h = abs(pt_bot[1] - pt_top[1])
                                        min_y = min(pt_top[1], pt_bot[1])
                                        max_y = max(pt_top[1], pt_bot[1])
                                    elif pt_bot:
                                        mid_x = pt_bot[0]
                                        box_h = (f_scale * 1.85 / pt_bot[2]) * (h * 0.5)
                                        max_y = pt_bot[1]
                                        min_y = max_y - box_h
                                    else:
                                        mid_x = pt_top[0]
                                        box_h = (f_scale * 1.85 / pt_top[2]) * (h * 0.5)
                                        min_y = pt_top[1]
                                        max_y = min_y + box_h

                                    box_w = max(box_h * 0.55, 4.0)
                                    min_x = mid_x - box_w * 0.5
                                    max_x = mid_x + box_w * 0.5

                                    if box_h < 4 or box_w < 2 or box_h > h * 2.5:
                                        continue

                                    _gdi32.Rectangle(mem_dc, int(min_x), int(min_y), int(max_x), int(max_y))

                                    tag = f"{pname} [{dist:.1f}m]"
                                    _gdi32.SetTextColor(mem_dc, 0x00FFFF)
                                    tx = int(mid_x - len(tag) * 3.5)
                                    _gdi32.TextOutW(mem_dc, tx, int(min_y) - 16, tag, len(tag))

                # 4. Render ClickGUI if open
                if self.clickgui.open:
                    _gdi32.SelectObject(mem_dc, font_sub)
                    self.clickgui.render(mem_dc, self.hwnd)

                _gdi32.BitBlt(hdc, 0, 0, w, h, mem_dc, 0, 0, 0x00CC0020)
                _user32.ReleaseDC(self.hwnd, hdc)
            except Exception:
                pass

            time.sleep(0.005)
