"""
atapiro 1337 #ONE - Movement Modules (Fly, UpClip, DownClip, ClickTP, XyzTeleport)
Stealth Flag-Free Packet Dispatch Logic
"""
import math
import random
import sys
import time
from .base import Module
from ..core.memory import (
    atapiro_key_down, atapiro_write_double, atapiro_write_float,
    atapiro_set_color, atapiro_reset_color,
    FOREGROUND_GREEN, FOREGROUND_CYAN, FOREGROUND_YELLOW, FOREGROUND_RED, FOREGROUND_INTENSITY
)

FLY_SPEED = 3.5
FLY_VERT = 1.8
FLY_GLIDE = 0.04
FLY_SMOOTH = 0.35

class FlyModule(Module):
    def __init__(self, h, offsets):
        super().__init__(
            name="Fly",
            description="Vector motion fly with dynamic jitter bypass",
            category="Movement",
            default_key=ord('F'),
            default_enabled=False,
            color=0x50FF78
        )
        self.h = h
        self.offsets = offsets
        self.fly_speed = FLY_SPEED
        self.vert_speed = FLY_VERT
        self.glide = FLY_GLIDE
        self.smooth = FLY_SMOOTH

    def handle_key(self, is_down):
        if is_down and not self._key_down:
            self._key_down = True
            self.toggle()
            atapiro_set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY if self.enabled else FOREGROUND_CYAN)
            sys.stdout.write(f'\r[+] fly {"ON " if self.enabled else "OFF"}   \n')
            sys.stdout.flush()
            atapiro_reset_color()
            return True
        elif not is_down:
            self._key_down = False
        return False

    def tick(self, ctx):
        if not self.enabled:
            return

        st = ctx.get("state")
        foc = ctx.get("focused", True)
        mc_ctx = ctx.get("mc_ctx")

        if not foc or not st or not st.player_obj or not mc_ctx:
            return

        yw = (st.rotation_yaw + (random.uniform(0.0, 1.0) - 0.5) * 0.3) * math.pi / 180.0
        tx, ty, tz = 0.0, 0.0, 0.0

        def r():
            return 1.0 + (random.uniform(0.0, 1.0) - 0.5) * 0.03

        if atapiro_key_down(ord('W')):
            v = r()
            tx -= math.sin(yw) * self.fly_speed * v
            tz += math.cos(yw) * self.fly_speed * v
        if atapiro_key_down(ord('S')):
            v = r()
            tx += math.sin(yw) * self.fly_speed * v
            tz -= math.cos(yw) * self.fly_speed * v
        if atapiro_key_down(ord('A')):
            v = r()
            s = yw - math.pi / 2.0
            tx -= math.sin(s) * self.fly_speed * v
            tz += math.cos(s) * self.fly_speed * v
        if atapiro_key_down(ord('D')):
            v = r()
            s = yw + math.pi / 2.0
            tx -= math.sin(s) * self.fly_speed * v
            tz += math.cos(s) * self.fly_speed * v

        if atapiro_key_down(0x20):    # Space
            ty += self.vert_speed * r()
        if atapiro_key_down(0xA0):  # LShift
            ty -= self.vert_speed * r()
        if not atapiro_key_down(0x20) and not atapiro_key_down(0xA0):
            ty -= self.glide

        if st.motion_x_ptr:
            mc_ctx.write_motion(st.motion_x_ptr, st.motion_x * self.smooth + tx * (1.0 - self.smooth))
        if st.motion_y_ptr:
            mc_ctx.write_motion(st.motion_y_ptr, st.motion_y * self.smooth + ty * (1.0 - self.smooth))
        if st.motion_z_ptr:
            mc_ctx.write_motion(st.motion_z_ptr, st.motion_z * self.smooth + tz * (1.0 - self.smooth))

        atapiro_write_float(self.h, st.player_obj + self.offsets.get("Entity.fallDistance", 240), 0.0)

class UpClipModule(Module):
    def __init__(self, h, offsets):
        super().__init__(
            name="UpClip",
            description="Teleports player upwards by configured blocks",
            category="Movement",
            default_key=ord('V'),
            default_enabled=False,
            color=0x00E0FF
        )
        self.h = h
        self.offsets = offsets
        self.distance = 3.0
        self.expanded = False
        self.last_clip = 0.0
        self._need_trigger = False

    def toggle(self):
        self._need_trigger = True
        return True

    def trigger(self, st):
        now = time.monotonic()
        if now - self.last_clip < 0.12 or not st or not st.player_obj:
            return
        self.last_clip = now

        p = st.player_obj
        target_y = st.pos_y + self.distance

        # Pure vertical displacement: do NOT touch prevPosY so Minecraft calculates d1 != 0
        # and dispatches C04/C06 packet naturally to server.
        atapiro_write_double(self.h, p + self.offsets.get("Entity.posY", 48), target_y)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.lastTickPosY", 40), target_y)
        atapiro_write_float(self.h, p + self.offsets.get("Entity.fallDistance", 240), 0.0)

        if st.bb_ptr:
            new_min_y = st.min_y + self.distance
            new_max_y = st.max_y + self.distance
            atapiro_write_double(self.h, st.bb_ptr + self.offsets.get("AABB.minY", 40), new_min_y)
            atapiro_write_double(self.h, st.bb_ptr + self.offsets.get("AABB.maxY", 32), new_max_y)

        atapiro_set_color(FOREGROUND_CYAN | FOREGROUND_INTENSITY)
        sys.stdout.write(f'\r[+] UpClip (+{self.distance:.1f} blocks) -> Y: {target_y:.2f}\n')
        sys.stdout.flush()
        atapiro_reset_color()

    def handle_key(self, is_down):
        if is_down and not self._key_down:
            self._key_down = True
            self._need_trigger = True
            return True
        elif not is_down:
            self._key_down = False
        return False

    def tick(self, ctx):
        if self._need_trigger or self.enabled:
            st = ctx.get("state")
            if st and st.player_obj:
                self.trigger(st)
            self._need_trigger = False
            self.enabled = False

class DownClipModule(Module):
    def __init__(self, h, offsets):
        super().__init__(
            name="DownClip",
            description="Teleports player downwards by configured blocks",
            category="Movement",
            default_key=ord('C'),
            default_enabled=False,
            color=0x00A0FF
        )
        self.h = h
        self.offsets = offsets
        self.distance = 3.0
        self.expanded = False
        self.last_clip = 0.0
        self._need_trigger = False

    def toggle(self):
        self._need_trigger = True
        return True

    def trigger(self, st):
        now = time.monotonic()
        if now - self.last_clip < 0.12 or not st or not st.player_obj:
            return
        self.last_clip = now

        p = st.player_obj
        target_y = st.pos_y - self.distance

        atapiro_write_double(self.h, p + self.offsets.get("Entity.posY", 48), target_y)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.lastTickPosY", 40), target_y)
        atapiro_write_float(self.h, p + self.offsets.get("Entity.fallDistance", 240), 0.0)

        if st.bb_ptr:
            new_min_y = st.min_y - self.distance
            new_max_y = st.max_y - self.distance
            atapiro_write_double(self.h, st.bb_ptr + self.offsets.get("AABB.minY", 40), new_min_y)
            atapiro_write_double(self.h, st.bb_ptr + self.offsets.get("AABB.maxY", 32), new_max_y)

        atapiro_set_color(FOREGROUND_CYAN | FOREGROUND_INTENSITY)
        sys.stdout.write(f'\r[+] DownClip (-{self.distance:.1f} blocks) -> Y: {target_y:.2f}\n')
        sys.stdout.flush()
        atapiro_reset_color()

    def handle_key(self, is_down):
        if is_down and not self._key_down:
            self._key_down = True
            self._need_trigger = True
            return True
        elif not is_down:
            self._key_down = False
        return False

    def tick(self, ctx):
        if self._need_trigger or self.enabled:
            st = ctx.get("state")
            if st and st.player_obj:
                self.trigger(st)
            self._need_trigger = False
            self.enabled = False

class ClickTPModule(Module):
    def __init__(self, h, offsets):
        super().__init__(
            name="ClickTP",
            description="Teleports forward in looking direction by configured distance",
            category="Movement",
            default_key=ord('Z'),
            default_enabled=False,
            color=0xFFD000
        )
        self.h = h
        self.offsets = offsets
        self.distance = 5.0
        self.expanded = False
        self.last_tp = 0.0
        self._need_trigger = False

    def toggle(self):
        self._need_trigger = True
        return True

    def trigger(self, st):
        now = time.monotonic()
        if now - self.last_tp < 0.12 or not st or not st.player_obj:
            return
        self.last_tp = now

        p = st.player_obj
        yaw = st.rotation_yaw * math.pi / 180.0
        pitch = st.rotation_pitch * math.pi / 180.0

        dx = -math.sin(yaw) * math.cos(pitch) * self.distance
        dy = -math.sin(pitch) * self.distance
        dz = math.cos(yaw) * math.cos(pitch) * self.distance

        target_x = st.pos_x + dx
        target_y = st.pos_y + dy
        target_z = st.pos_z + dz

        atapiro_write_float(self.h, p + self.offsets.get("Entity.fallDistance", 240), 0.0)

        # Write position + lastTick. Keep prevPos untouched for natural C04/C06 packet dispatch.
        atapiro_write_double(self.h, p + self.offsets.get("Entity.posX", 64), target_x)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.posY", 48), target_y)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.posZ", 80), target_z)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.lastTickPosX", 96), target_x)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.lastTickPosY", 40), target_y)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.lastTickPosZ", 72), target_z)

        if st.bb_ptr:
            new_min_y = st.min_y + dy
            new_max_y = st.max_y + dy
            atapiro_write_double(self.h, st.bb_ptr + self.offsets.get("AABB.minY", 40), new_min_y)
            atapiro_write_double(self.h, st.bb_ptr + self.offsets.get("AABB.maxY", 32), new_max_y)

        atapiro_set_color(FOREGROUND_YELLOW | FOREGROUND_INTENSITY)
        sys.stdout.write(f'\r[+] ClickTP (+{self.distance:.1f}m look-ray) -> ({target_x:.1f}, {target_y:.1f}, {target_z:.1f})\n')
        sys.stdout.flush()
        atapiro_reset_color()

    def handle_key(self, is_down):
        if is_down and not self._key_down:
            self._key_down = True
            self._need_trigger = True
            return True
        elif not is_down:
            self._key_down = False
        return False

    def tick(self, ctx):
        if self._need_trigger or self.enabled:
            st = ctx.get("state")
            if st and st.player_obj:
                self.trigger(st)
            self._need_trigger = False
            self.enabled = False

class XyzTeleportModule(Module):
    def __init__(self, h, offsets):
        super().__init__(
            name="XyzTeleport",
            description="Teleports player to set target X, Y, Z coordinates with C06 loop option",
            category="Movement",
            default_key=ord('X'),
            default_enabled=False,
            color=0xFF50B0
        )
        self.h = h
        self.offsets = offsets
        self.x_str = ""
        self.y_str = ""
        self.z_str = ""
        self.loop_mode = False
        self.expanded = False
        self.last_tp = 0.0
        self._need_trigger = False

    def set_target_coords(self, tx, ty, tz):
        self.x_str = f"{tx:.2f}"
        self.y_str = f"{ty:.2f}"
        self.z_str = f"{tz:.2f}"

    def get_target_coords(self):
        sx = self.x_str.strip()
        sy = self.y_str.strip()
        sz = self.z_str.strip()
        if not sx or not sy or not sz:
            return None
        try:
            vx = float(sx)
            vy = float(sy)
            vz = float(sz)
            if math.isnan(vx) or math.isnan(vy) or math.isnan(vz):
                return None
            return vx, vy, vz
        except ValueError:
            return None

    def toggle(self):
        if not self.loop_mode:
            self._need_trigger = True
            self.enabled = False
            return True
        else:
            self.enabled = not self.enabled
            return self.enabled

    def teleport(self, st):
        coords = self.get_target_coords()
        if not coords or not st or not st.player_obj:
            return False

        tx, ty, tz = coords
        p = st.player_obj

        atapiro_write_float(self.h, p + self.offsets.get("Entity.fallDistance", 240), 0.0)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.posX", 64), tx)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.posY", 48), ty)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.posZ", 80), tz)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.lastTickPosX", 96), tx)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.lastTickPosY", 40), ty)
        atapiro_write_double(self.h, p + self.offsets.get("Entity.lastTickPosZ", 72), tz)

        if st.bb_ptr:
            atapiro_write_double(self.h, st.bb_ptr + self.offsets.get("AABB.minY", 40), ty)
            atapiro_write_double(self.h, st.bb_ptr + self.offsets.get("AABB.maxY", 32), ty + 1.8)
        return True

    def handle_key(self, is_down):
        if is_down and not self._key_down:
            self._key_down = True
            if self.loop_mode:
                self.enabled = not self.enabled
                atapiro_set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY if self.enabled else FOREGROUND_CYAN)
                sys.stdout.write(f'\r[+] XyzTeleport Loop {"ON" if self.enabled else "OFF"}   \n')
                sys.stdout.flush()
                atapiro_reset_color()
            else:
                self._need_trigger = True
            return True
        elif not is_down:
            self._key_down = False
        return False

    def tick(self, ctx):
        st = ctx.get("state")

        now = time.monotonic()
        if self._need_trigger:
            if self.teleport(st):
                coords = self.get_target_coords()
                atapiro_set_color(FOREGROUND_CYAN | FOREGROUND_INTENSITY)
                sys.stdout.write(f'\r[+] XyzTeleport -> ({coords[0]:.2f}, {coords[1]:.2f}, {coords[2]:.2f})\n')
                sys.stdout.flush()
                atapiro_reset_color()
            else:
                atapiro_set_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
                sys.stdout.write('\r[-] XyzTeleport: Coords empty or invalid! Enter X, Y, Z in ClickGUI first!\n')
                sys.stdout.flush()
                atapiro_reset_color()
            self._need_trigger = False
            return

        if self.enabled and self.loop_mode:
            if now - self.last_tp >= 0.04:
                self.last_tp = now
                self.teleport(st)
