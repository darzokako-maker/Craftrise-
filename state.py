"""
atapiro 1337 #ONE - Game State & Encrypted Motion Subsystem
"""
import ctypes
import struct
import time
from .memory import (
    atapiro_read_bytes, atapiro_read_u16, atapiro_read_u32, atapiro_read_i32,
    atapiro_read_u64, atapiro_read_float, atapiro_read_double,
    atapiro_write_bytes, atapiro_write_u64, atapiro_write_double,
    K_DICTIONARY_PTR_OFFSET, K_TABLE_SIZE_OFFSET, K_BUCKETS_OFFSET,
    K_ENTRY_NEXT_OFFSET, K_ENTRY_LITERAL_OFFSET, K_KLASS_NAME_OFFSET,
    K_SYMBOL_LENGTH_OFFSET, K_SYMBOL_BODY_OFFSET, K_JAVA_MIRROR_OFFSET,
    OFFSET_O_INNER_WRAPPER, OFFSET_O_MULTIPLIER, OFFSET_O_HASH,
    OFFSET_E_SEED, OFFSET_E_ENCRYPTED
)

def atapiro_pack_double(value):
    return struct.unpack('<Q', struct.pack('<d', value))[0]

def atapiro_unpack_double(bits):
    return struct.unpack('<d', struct.pack('<Q', bits & 0xFFFFFFFFFFFFFFFF))[0]

def atapiro_hash_code(val, multiplier):
    b = atapiro_pack_double(val)
    hash_code = ctypes.c_int32(b ^ (b >> 32)).value
    return float(hash_code) * multiplier + 31.0

_cached_jvm_classes = None

def atapiro_find_class(proc, jvm, class_name):
    global _cached_jvm_classes
    nb = class_name if isinstance(class_name, bytes) else class_name.encode('utf-8')
    d_ptr = atapiro_read_u64(proc, jvm + K_DICTIONARY_PTR_OFFSET)
    if d_ptr:
        t_size = atapiro_read_i32(proc, d_ptr + K_TABLE_SIZE_OFFSET)
        if t_size and (0 < t_size < 1_000_000):
            b_ptr = atapiro_read_u64(proc, d_ptr + K_BUCKETS_OFFSET)
            if b_ptr:
                raw = atapiro_read_bytes(proc, b_ptr, t_size * 8)
                if raw:
                    heads = struct.unpack(f'<{t_size}Q', raw)
                    t_len = len(nb)
                    for h in heads:
                        entry = h
                        while entry:
                            k = atapiro_read_u64(proc, entry + K_ENTRY_LITERAL_OFFSET)
                            if k:
                                sym = atapiro_read_u64(proc, k + K_KLASS_NAME_OFFSET)
                                if sym:
                                    sl = atapiro_read_u16(proc, sym + K_SYMBOL_LENGTH_OFFSET)
                                    if sl == t_len:
                                        sd = atapiro_read_bytes(proc, sym + K_SYMBOL_BODY_OFFSET, sl)
                                        if sd == nb:
                                            return k
                            nxt = atapiro_read_u64(proc, entry + K_ENTRY_NEXT_OFFSET)
                            if nxt is None:
                                break
                            entry = nxt & ~1

    try:
        from jvm_reader import find_process_pid, JVMProcess
        if _cached_jvm_classes is None:
            pid = find_process_pid('craftrise-x64.exe')
            if pid:
                jp = JVMProcess(pid)
                jp.load_classes()
                _cached_jvm_classes = {k: v['klass'] for k, v in jp.classes.items()}
                jp.close()
        if _cached_jvm_classes and isinstance(class_name, str):
            if class_name in _cached_jvm_classes:
                return _cached_jvm_classes[class_name]
    except Exception:
        pass
    return 0

def atapiro_find_player_offset(proc_handle, instance, klass, pos_y_off=48):
    for def_off in (296, 352, 528, 460, 456, 464, 452, 468, 472, 448):
        ptr = atapiro_read_u32(proc_handle, instance + def_off)
        if ptr:
            obj = ptr << 3
            k = atapiro_read_u32(proc_handle, obj + 8)
            if (k == (klass >> 3) or (k << 3) == klass) and abs(atapiro_read_double(proc_handle, obj + pos_y_off) or 0.0) > 0.1:
                return def_off
    for offset in range(8, 1000, 4):
        ptr = atapiro_read_u32(proc_handle, instance + offset)
        if not ptr:
            continue
        obj = ptr << 3
        k = atapiro_read_u32(proc_handle, obj + 8)
        if not k:
            continue
        if (k == (klass >> 3) or (k << 3) == klass) and abs(atapiro_read_double(proc_handle, obj + pos_y_off) or 0.0) > 0.1:
            return offset
    return 296

class AtapiroGameState:
    __slots__ = (
        'instance_ptr', 'player_obj', 'pos_x', 'pos_y', 'pos_z',
        'rotation_yaw', 'rotation_pitch', 'bb_ptr', 'min_y', 'max_y',
        'motion_x_ptr', 'motion_y_ptr', 'motion_z_ptr',
        'motion_x', 'motion_y', 'motion_z', 'world_obj'
    )
    def __init__(self):
        self.instance_ptr = 0
        self.player_obj = 0
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0
        self.rotation_yaw = 0.0
        self.rotation_pitch = 0.0
        self.bb_ptr = 0
        self.min_y = 0.0
        self.max_y = 0.0
        self.motion_x_ptr = 0
        self.motion_y_ptr = 0
        self.motion_z_ptr = 0
        self.motion_x = 0.0
        self.motion_y = 0.0
        self.motion_z = 0.0
        self.world_obj = 0

class AtapiroMotionContext:
    def __init__(self, handle, inner_klass, inner_static_offset):
        self.h = handle
        self.inner_klass = inner_klass
        self.inner_static_offset = inner_static_offset
        self.mirror = atapiro_read_u64(self.h, self.inner_klass + K_JAVA_MIRROR_OFFSET) or 0
        self.static_val = (atapiro_read_u64(self.h, self.mirror + self.inner_static_offset) or 0) if self.mirror else 0

    def get_inner_ptr(self, o):
        inner = atapiro_read_u32(self.h, o + OFFSET_O_INNER_WRAPPER)
        return (inner << 3) if inner else 0

    def read_motion(self, ptr):
        if not ptr:
            return 0.0
        o = ptr << 3
        e = self.get_inner_ptr(o)
        if not e:
            return 0.0
        # Read valB (e+16), valA (e+24), seed/xorKey (e+32) in 1 single 24-byte RPM call
        buf = atapiro_read_bytes(self.h, e + 16, 24)
        if not buf:
            return 0.0
        enc, _, seed = struct.unpack('<QQQ', buf)
        key = (seed + self.static_val) & 0xFFFFFFFFFFFFFFFF
        return atapiro_unpack_double(enc ^ key)

    def write_motion(self, ptr, val):
        if not ptr:
            return False
        o = ptr << 3
        e = self.get_inner_ptr(o)
        if not e:
            return False
        seed = atapiro_read_u64(self.h, e + OFFSET_E_SEED) or 0
        key = (seed + self.static_val) & 0xFFFFFFFFFFFFFFFF
        # Write hash (o+16 = 31.0) and multiplier (o+24 = 0.0) in 1 single 16-byte write
        atapiro_write_bytes(self.h, o + 16, struct.pack('<dd', 31.0, 0.0))
        b = atapiro_pack_double(val) & 0xFFFFFFFFFFFFFFFF
        enc = b ^ key
        # Write valB (e+16 = enc) and valA (e+24 = enc) in 1 single 16-byte write
        atapiro_write_bytes(self.h, e + 16, struct.pack('<QQ', enc, enc))
        return True

_last_player_offset = 296

def atapiro_read_game_state(h, k_minecraft, mc_offset, p_klass, mc_ctx, offsets):
    global _last_player_offset
    st = AtapiroGameState()

    mirror = atapiro_read_u64(h, k_minecraft + K_JAVA_MIRROR_OFFSET)
    if not mirror:
        return None

    narrow = atapiro_read_u32(h, mirror + mc_offset)
    if not narrow:
        return None
    st.instance_ptr = narrow << 3

    p = 0
    p_ptr = atapiro_read_u32(h, st.instance_ptr + _last_player_offset)
    if p_ptr:
        cand = p_ptr << 3
        k = atapiro_read_u32(h, cand + 8)
        if k and (k == (p_klass >> 3) or (k << 3) == p_klass):
            p = cand

    if not p:
        for off in (296, 352, 528, 460, 456, 464, 452, 468, 472, 448, 476, 480):
            cand_ptr = atapiro_read_u32(h, st.instance_ptr + off)
            if cand_ptr:
                cand = cand_ptr << 3
                k = atapiro_read_u32(h, cand + 8)
                if k and (k == (p_klass >> 3) or (k << 3) == p_klass):
                    _last_player_offset = off
                    p = cand
                    break

    if not p:
        return None

    st.player_obj = p

    # Read entire Entity struct (0..396) in 1 single RPM call instead of 10 separate calls!
    p_buf = atapiro_read_bytes(h, p, 396)
    if not p_buf:
        return None

    px_off = offsets.get("Entity.posX", 64)
    py_off = offsets.get("Entity.posY", 48)
    pz_off = offsets.get("Entity.posZ", 80)
    yaw_off = offsets.get("Entity.rotationYaw", 148)
    pit_off = offsets.get("Entity.rotationPitch", 136)
    bb_off = offsets.get("Entity.boundingBox", 312)
    mx_off = offsets.get("Entity.motionX", 304)
    my_off = offsets.get("Entity.motionY", 292)
    mz_off = offsets.get("Entity.motionZ", 320)
    w_off = offsets.get("Entity.worldObj", 288)

    st.pos_x = struct.unpack_from('<d', p_buf, px_off)[0]
    st.pos_y = struct.unpack_from('<d', p_buf, py_off)[0]
    st.pos_z = struct.unpack_from('<d', p_buf, pz_off)[0]
    st.rotation_yaw = struct.unpack_from('<f', p_buf, yaw_off)[0]
    st.rotation_pitch = struct.unpack_from('<f', p_buf, pit_off)[0]

    bb = struct.unpack_from('<I', p_buf, bb_off)[0]
    if bb:
        st.bb_ptr = bb << 3
        bb_buf = atapiro_read_bytes(h, st.bb_ptr, 64)
        if bb_buf:
            st.max_y = struct.unpack_from('<d', bb_buf, offsets.get("AABB.maxY", 32))[0]
            st.min_y = struct.unpack_from('<d', bb_buf, offsets.get("AABB.minY", 40))[0]

    st.motion_x_ptr = struct.unpack_from('<I', p_buf, mx_off)[0]
    st.motion_y_ptr = struct.unpack_from('<I', p_buf, my_off)[0]
    st.motion_z_ptr = struct.unpack_from('<I', p_buf, mz_off)[0]

    st.motion_x = mc_ctx.read_motion(st.motion_x_ptr)
    st.motion_y = mc_ctx.read_motion(st.motion_y_ptr)
    st.motion_z = mc_ctx.read_motion(st.motion_z_ptr)

    w = struct.unpack_from('<I', p_buf, w_off)[0]
    if not w:
        w = atapiro_read_u32(h, st.instance_ptr + offsets.get("Minecraft.theWorld", 236)) or 0
    st.world_obj = (w << 3) if w else 0

    return st
