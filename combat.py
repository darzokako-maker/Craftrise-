"""
atapiro 1337 #ONE - Combat Modules (Aimbot & Velocity)
"""
import math
import struct
from .base import Module
from ..core.memory import (
    atapiro_read_bytes, atapiro_read_u32, atapiro_read_i32,
    atapiro_write_i32, atapiro_write_float, atapiro_is_bot_entity,
    OFFSET_ARRAY_LIST_SIZE, ARRAY_OBJ_BASE
)

K_FAKE_ENTITY_ID = -9999

class AimbotModule(Module):
    def __init__(self, h, offsets):
        super().__init__(
            name="Aimbot",
            description="Locks crosshair onto nearest enemy player",
            category="Combat",
            default_key=ord('R'),
            default_enabled=False,
            color=0x50E6FF
        )
        self.h = h
        self.offsets = offsets

    def tick(self, ctx):
        st = ctx.get("state")
        if not self.enabled or not st or not st.world_obj or not st.player_obj:
            return

        real_ents, bot_ents = self._get_entities(st.world_obj, st.player_obj)
        target = self._get_target(st, real_ents) or self._get_target(st, bot_ents)
        if not target:
            return

        ex, ey, ez = target
        dx = ex - st.pos_x
        dy = (ey + 1.62) - (st.pos_y + 1.62)
        dz = ez - st.pos_z
        dist = math.sqrt(dx * dx + dz * dz)
        if dist < 0.05:
            return

        raw_yaw = math.degrees(math.atan2(-dx, dz))
        diff_yaw = (raw_yaw - st.rotation_yaw + 180.0) % 360.0 - 180.0
        yaw = st.rotation_yaw + diff_yaw
        pitch = max(-89.9, min(89.9, -math.degrees(math.atan2(dy, dist))))

        p = st.player_obj
        yaw_off = self.offsets.get("Entity.rotationYaw", 148)
        pit_off = self.offsets.get("Entity.rotationPitch", 136)
        prev_yaw_off = self.offsets.get("Entity.prevRotationYaw", 200)
        prev_pit_off = self.offsets.get("Entity.prevRotationPitch", 172)

        atapiro_write_float(self.h, p + yaw_off, yaw)
        atapiro_write_float(self.h, p + prev_yaw_off, yaw)
        atapiro_write_float(self.h, p + pit_off, pitch)
        atapiro_write_float(self.h, p + prev_pit_off, pitch)

    def _get_entities(self, w_obj, self_player):
        p_offset = self.offsets.get("World.playerEntities", 232)
        lst = atapiro_read_u32(self.h, w_obj + p_offset)
        if not lst:
            return [], []
        lst_hdr = atapiro_read_bytes(self.h, (lst << 3) + OFFSET_ARRAY_LIST_SIZE, 8)
        if not lst_hdr:
            return [], []
        sz, dt = struct.unpack('<iI', lst_hdr)
        if sz <= 0 or sz > 200 or not dt:
            return [], []
        arr = dt << 3
        ptrs_buf = atapiro_read_bytes(self.h, arr + ARRAY_OBJ_BASE, sz * 4)
        if not ptrs_buf:
            return [], []
        ptrs = struct.unpack(f'<{sz}I', ptrs_buf)

        px_off = self.offsets.get("Entity.posX", 64)
        py_off = self.offsets.get("Entity.posY", 48)
        pz_off = self.offsets.get("Entity.posZ", 80)
        eid_off = self.offsets.get("Entity.entityId", 160)

        real_res = []
        bot_res = []
        for e_ptr in ptrs:
            if not e_ptr:
                continue
            e = e_ptr << 3
            if e == self_player:
                continue
            # Read Entity struct (0..256) in 1 single RPM call and unpack dynamically
            ebuf = atapiro_read_bytes(self.h, e, 256)
            if not ebuf:
                continue
            px = struct.unpack_from('<d', ebuf, px_off)[0]
            py = struct.unpack_from('<d', ebuf, py_off)[0]
            pz = struct.unpack_from('<d', ebuf, pz_off)[0]
            if px == 0.0 and py == 0.0 and pz == 0.0:
                continue
            eid = struct.unpack_from('<i', ebuf, eid_off)[0]
            if atapiro_is_bot_entity(self.h, e, eid):
                bot_res.append((px, py, pz))
            else:
                real_res.append((px, py, pz))
        return real_res, bot_res

    def _get_target(self, st, ents):
        best = None
        min_d = 99999.0
        sx, sy, sz = st.pos_x, st.pos_y, st.pos_z
        for px, py, pz in ents:
            dx = px - sx
            dy = py - sy
            dz = pz - sz
            d2 = dx * dx + dy * dy + dz * dz
            if d2 < 0.04 or d2 > 6400.0:
                continue
            if d2 < min_d:
                min_d = d2
                best = (px, py, pz)
        return best

class VelocityModule(Module):
    def __init__(self, h, offsets):
        super().__init__(
            name="Velocity",
            description="Bypasses knockback packets by masking entity ID",
            category="Combat",
            default_key=ord('G'),
            default_enabled=False,
            color=0xFF64DC
        )
        self.h = h
        self.offset = offsets.get("Entity.entityId", 160)
        self.real_id = 0

    def tick(self, ctx):
        st = ctx.get("state")
        if not st or not st.player_obj:
            return

        p_obj = st.player_obj
        if getattr(self, "_last_p_obj", 0) != p_obj:
            self._last_p_obj = p_obj
            self.real_id = 0

        if self.enabled:
            curr = atapiro_read_i32(self.h, p_obj + self.offset) or 0
            if curr != K_FAKE_ENTITY_ID and curr != 0:
                self.real_id = curr
            atapiro_write_i32(self.h, p_obj + self.offset, K_FAKE_ENTITY_ID)
        elif self.real_id != 0:
            atapiro_write_i32(self.h, p_obj + self.offset, self.real_id)
            self.real_id = 0

    def on_disable(self):
        st = getattr(self, "_last_st", None)
        if st and st.player_obj and self.real_id != 0:
            atapiro_write_i32(self.h, st.player_obj + self.offset, self.real_id)
            self.real_id = 0
