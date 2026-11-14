"""
atapiro 1337 #ONE - Core Memory & Process Subsystem
"""
import ctypes
import ctypes.wintypes
import math
import os
import struct
import sys
import time

try:
    ctypes.windll.winmm.timeBeginPeriod(1)
except Exception:
    pass

_kernel32 = ctypes.windll.kernel32
_ntdll    = ctypes.windll.ntdll
_user32   = ctypes.windll.user32
_gdi32    = ctypes.windll.gdi32
_psapi    = ctypes.windll.psapi

_kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_bool, ctypes.c_ulong]
_kernel32.OpenProcess.restype = ctypes.c_void_p

_kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
_kernel32.CloseHandle.restype = ctypes.c_bool

_kernel32.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
_kernel32.ReadProcessMemory.restype = ctypes.c_bool

_kernel32.WriteProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
_kernel32.WriteProcessMemory.restype = ctypes.c_bool

_kernel32.VirtualQueryEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
_kernel32.VirtualQueryEx.restype = ctypes.c_size_t

_psapi.EnumProcessModules.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
_psapi.EnumProcessModules.restype = ctypes.c_bool

_psapi.GetModuleBaseNameW.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_ulong]
_psapi.GetModuleBaseNameW.restype = ctypes.c_ulong

_user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
_user32.GetAsyncKeyState.restype = ctypes.c_short

_user32.GetForegroundWindow.argtypes = []
_user32.GetForegroundWindow.restype = ctypes.c_void_p

_user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
_user32.GetWindowThreadProcessId.restype = ctypes.c_ulong

try:
    _nt_write = _ntdll.NtWriteVirtualMemory
    _nt_write.restype = ctypes.c_long
    _nt_write.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
except Exception:
    _nt_write = None

_STD_OUTPUT_HANDLE = ctypes.c_uint(-11)
g_hCon = _kernel32.GetStdHandle(_STD_OUTPUT_HANDLE)

FOREGROUND_GREEN     = 0x0002
FOREGROUND_CYAN      = 0x0003
FOREGROUND_RED       = 0x0004
FOREGROUND_MAGENTA   = 0x0005
FOREGROUND_YELLOW    = 0x0006
FOREGROUND_WHITE     = 0x0007
FOREGROUND_INTENSITY = 0x0008

TH32CS_SNAPPROCESS = 2
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ           = 0x0010
MEM_COMMIT                = 0x1000
PAGE_READWRITE            = 0x04
PAGE_EXECUTE_READWRITE    = 0x40

K_DICTIONARY_PTR_OFFSET = 0x7E17F0
K_TABLE_SIZE_OFFSET     = 0x00
K_BUCKETS_OFFSET        = 0x08
K_ENTRY_NEXT_OFFSET     = 0x08
K_ENTRY_LITERAL_OFFSET  = 0x10
K_KLASS_NAME_OFFSET     = 0x10
K_JAVA_MIRROR_OFFSET    = 0x68
K_SYMBOL_LENGTH_OFFSET  = 0x00
K_SYMBOL_BODY_OFFSET    = 0x08

OFFSET_O_INNER_WRAPPER  = 56
OFFSET_O_HASH           = 16
OFFSET_O_MULTIPLIER     = 24
OFFSET_E_SEED           = 32
OFFSET_E_ENCRYPTED      = 16

OFFSET_ARRAY_LIST_SIZE  = 0x10
OFFSET_ARRAY_LIST_DATA  = 0x14
ARRAY_OBJ_BASE          = 16

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ('dwSize',              ctypes.c_ulong),
        ('cntUsage',            ctypes.c_ulong),
        ('th32ProcessID',       ctypes.c_ulong),
        ('th32DefaultHeapID',   ctypes.POINTER(ctypes.c_ulong)),
        ('th32ModuleID',        ctypes.c_ulong),
        ('cntThreads',          ctypes.c_ulong),
        ('th32ParentProcessID', ctypes.c_ulong),
        ('pcPriClassBase',      ctypes.c_long),
        ('dwFlags',             ctypes.c_ulong),
        ('szExeFile',           ctypes.c_wchar * 260),
    ]

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('BaseAddress',       ctypes.c_void_p),
        ('AllocationBase',    ctypes.c_void_p),
        ('AllocationProtect', ctypes.c_ulong),
        ('__alignment1',      ctypes.c_ulong),
        ('RegionSize',        ctypes.c_size_t),
        ('State',             ctypes.c_ulong),
        ('Protect',           ctypes.c_ulong),
        ('Type',              ctypes.c_ulong),
        ('__alignment2',      ctypes.c_ulong),
    ]

def atapiro_set_color(color):
    _kernel32.SetConsoleTextAttribute(g_hCon, color)

def atapiro_reset_color():
    _kernel32.SetConsoleTextAttribute(g_hCon, FOREGROUND_WHITE)

def atapiro_anim(text, delay_ms=6, color=FOREGROUND_WHITE):
    atapiro_set_color(color)
    pause = delay_ms / 1000.0
    for c in text:
        try:
            sys.stdout.write(c)
            sys.stdout.flush()
        except Exception:
            try:
                sys.stdout.write(c.encode('ascii', errors='replace').decode('ascii'))
                sys.stdout.flush()
            except Exception:
                pass
        if pause:
            time.sleep(pause)
    try:
        sys.stdout.write("\n")
        sys.stdout.flush()
    except Exception:
        pass
    atapiro_reset_color()

def atapiro_read_bytes(proc, addr, size):
    if not addr or addr < 0x10000:
        return None
    buf = ctypes.create_string_buffer(size)
    read = ctypes.c_size_t(0)
    if not _kernel32.ReadProcessMemory(proc, ctypes.c_void_p(addr), buf, size, ctypes.byref(read)) or read.value != size:
        return None
    return buf.raw

def atapiro_read_u32(h, addr):
    d = atapiro_read_bytes(h, addr, 4)
    return struct.unpack('<I', d)[0] if d else None

def atapiro_read_i32(h, addr):
    d = atapiro_read_bytes(h, addr, 4)
    return struct.unpack('<i', d)[0] if d else None

def atapiro_read_u64(h, addr):
    d = atapiro_read_bytes(h, addr, 8)
    return struct.unpack('<Q', d)[0] if d else None

def atapiro_read_double(h, addr):
    d = atapiro_read_bytes(h, addr, 8)
    return struct.unpack('<d', d)[0] if d else None

def atapiro_read_float(h, addr):
    d = atapiro_read_bytes(h, addr, 4)
    return struct.unpack('<f', d)[0] if d else None

def atapiro_read_u16(h, addr):
    d = atapiro_read_bytes(h, addr, 2)
    return struct.unpack('<H', d)[0] if d else None

def atapiro_write_bytes(h, addr, data: bytes):
    if not addr or addr < 0x10000:
        return False
    w = ctypes.c_size_t(0)
    if _nt_write is not None:
        if _nt_write(h, ctypes.c_void_p(addr), data, len(data), ctypes.byref(w)) >= 0:
            return True
    return bool(_kernel32.WriteProcessMemory(h, ctypes.c_void_p(addr), data, len(data), ctypes.byref(w)))

def atapiro_write_i32(h, addr, val):
    return atapiro_write_bytes(h, addr, struct.pack('<i', val))

def atapiro_write_u64(h, addr, val):
    return atapiro_write_bytes(h, addr, struct.pack('<Q', val & 0xFFFFFFFFFFFFFFFF))

def atapiro_write_double(h, addr, val):
    return atapiro_write_bytes(h, addr, struct.pack('<d', val))

def atapiro_write_float(h, addr, val):
    return atapiro_write_bytes(h, addr, struct.pack('<f', val))

def atapiro_is_valid_ptr(proc, addr):
    return bool(addr and addr >= 0x10000)

def atapiro_read_symbol(h, addr):
    length = atapiro_read_u16(h, addr + K_SYMBOL_LENGTH_OFFSET)
    if length is None or length <= 0 or length > 256:
        return None
    data = atapiro_read_bytes(h, addr + K_SYMBOL_BODY_OFFSET, length)
    if not data:
        return None
    try:
        return data.decode('utf-8', errors='ignore')
    except Exception:
        return None

def atapiro_read_jstring(h, jstr_obj):
    if not jstr_obj or jstr_obj < 0x10000:
        return ""
    val_arr_ptr = atapiro_read_u32(h, jstr_obj + 12)
    if not val_arr_ptr:
        return ""
    val_arr = val_arr_ptr << 3
    if val_arr < 0x10000:
        return ""
    hdr = atapiro_read_bytes(h, val_arr + 12, 68)
    if not hdr:
        return ""
    length = struct.unpack_from('<i', hdr, 0)[0]
    if length < 1 or length > 32:
        return ""
    try:
        s = hdr[4:4 + length * 2].decode("utf-16le", errors="ignore")
        if s and all(ord(c) >= 32 for c in s):
            return s
    except Exception:
        pass
    return ""

_name_cache = {}

def atapiro_get_player_name(h, e, eid=None):
    if not e or e < 0x10000:
        return "Player"
    if eid is None:
        eid = atapiro_read_i32(h, e + 160)
    cache_key = eid if (eid and eid > 0) else e
    cached = _name_cache.get(cache_key)
    if cached is not None:
        return cached

    if len(_name_cache) > 2000:
        _name_cache.clear()

    # 1. Direct EntityPlayer.name string at e + 732 (or Entity.name at e + 316)
    for str_off in (732, 316):
        ptr = atapiro_read_u32(h, e + str_off)
        if ptr:
            s = atapiro_read_jstring(h, ptr << 3)
            if s and len(s) >= 2:
                _name_cache[cache_key] = s
                return s

    # 2. EntityPlayer.gameProfile at e + 764 -> GameProfile.name at + 68
    gp_ptr = atapiro_read_u32(h, e + 764)
    if gp_ptr:
        s_ptr = atapiro_read_u32(h, (gp_ptr << 3) + 68)
        if s_ptr:
            s = atapiro_read_jstring(h, s_ptr << 3)
            if s and len(s) >= 2:
                _name_cache[cache_key] = s
                return s

    _name_cache[cache_key] = "Player"
    return "Player"

def atapiro_is_bot_entity(h, e, eid=None):
    name = atapiro_get_player_name(h, e, eid)
    return name.startswith("[CR]") or name.startswith("§")

def atapiro_clear_name_cache():
    global _name_cache
    _name_cache.clear()

def atapiro_key_down(vk):
    return bool(_user32.GetAsyncKeyState(vk) & 0x8000)

def atapiro_is_focused(target_pid):
    fg = _user32.GetForegroundWindow()
    if not fg:
        return False
    pid = ctypes.c_ulong(0)
    _user32.GetWindowThreadProcessId(fg, ctypes.byref(pid))
    return pid.value == target_pid or pid.value == os.getpid()

def atapiro_get_command_line(pid):
    handle = _kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not handle:
        return ''
    try:
        class PROCESS_BASIC_INFORMATION(ctypes.Structure):
            _fields_ = [
                ('Reserved1', ctypes.c_void_p),
                ('PebBaseAddress', ctypes.c_void_p),
                ('Reserved2', ctypes.c_void_p * 2),
                ('UniqueProcessId', ctypes.c_void_p),
                ('Reserved3', ctypes.c_void_p)
            ]
        pbi = PROCESS_BASIC_INFORMATION()
        ret = _ntdll.NtQueryInformationProcess(handle, 0, ctypes.byref(pbi), ctypes.sizeof(pbi), None)
        if ret != 0 or not pbi.PebBaseAddress:
            return ''
        proc_params_addr = atapiro_read_u64(handle, pbi.PebBaseAddress + 0x20)
        if not proc_params_addr:
            return ''
        cmd_len = atapiro_read_u16(handle, proc_params_addr + 0x70)
        cmd_buf = atapiro_read_u64(handle, proc_params_addr + 0x78)
        if not cmd_buf or not cmd_len:
            return ''
        raw = atapiro_read_bytes(handle, cmd_buf, cmd_len)
        return raw.decode('utf-16-le', errors='ignore') if raw else ''
    except Exception:
        return ''
    finally:
        _kernel32.CloseHandle(handle)

def atapiro_find_craftrise_pid():
    snap = _kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == -1:
        return None
    pe = PROCESSENTRY32W()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
    if not _kernel32.Process32FirstW(snap, ctypes.byref(pe)):
        _kernel32.CloseHandle(snap)
        return None

    craftrise_pids = []
    java_pids = []
    while True:
        exe = pe.szExeFile.lower()
        if 'craftrise-x64' in exe or exe == 'craftrise.exe':
            craftrise_pids.append(pe.th32ProcessID)
        elif exe in ('javaw.exe', 'java.exe'):
            java_pids.append(pe.th32ProcessID)
        if not _kernel32.Process32NextW(snap, ctypes.byref(pe)):
            break
    _kernel32.CloseHandle(snap)

    if craftrise_pids:
        return craftrise_pids[0]

    for p in java_pids:
        cmd = atapiro_get_command_line(p).lower()
        if 'launcherstartup' not in cmd and 'launcher.jar' not in cmd:
            if 'craftrise' in cmd or 'lpreloader' in cmd or 'rise' in cmd:
                return p

    return None

def atapiro_get_jvm_base(pid):
    h = _kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
    if not h:
        return None
    try:
        mod_handles = (ctypes.c_void_p * 1024)()
        needed = ctypes.c_ulong(0)
        if not _psapi.EnumProcessModules(h, mod_handles, ctypes.sizeof(mod_handles), ctypes.byref(needed)):
            return None
        count = needed.value // ctypes.sizeof(ctypes.c_void_p)
        name_buf = ctypes.create_unicode_buffer(260)
        for i in range(count):
            mod = mod_handles[i]
            if not mod:
                continue
            if _psapi.GetModuleBaseNameW(h, mod, name_buf, 260):
                if name_buf.value.lower() == 'jvm.dll':
                    return mod
        return None
    finally:
        _kernel32.CloseHandle(h)

def atapiro_retry(fn, timeout_s=30, interval_s=0.2):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        r = fn()
        if r:
            return r
        time.sleep(interval_s)
    return None

def atapiro_get_mc_fov():
    appdata = os.environ.get("APPDATA", "")
    paths = [
        os.path.join(appdata, ".craftrise", "options.txt"),
        os.path.join(appdata, ".minecraft", "options.txt"),
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.startswith("fov:"):
                            val = float(line.strip().split("fov:")[1])
                            return round(70.0 + val * 40.0, 1)
            except Exception:
                pass
    return 91.0
