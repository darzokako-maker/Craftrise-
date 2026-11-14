"""
atapiro 1337 #ONE - Module Manager & Persistence Subsystem
"""
import json
import os
from pathlib import Path
from .combat import AimbotModule, VelocityModule
from .movement import FlyModule, UpClipModule, DownClipModule, ClickTPModule, XyzTeleportModule
from .player import FastPlaceModule
from .render import ESPModule, WatermarkModule, ArrayListModule
from ..core.memory import atapiro_key_down

class ModuleManager:
    def __init__(self, h, offsets):
        self.h = h
        self.offsets = offsets
        self.modules = []
        self.categories = ["Combat", "Movement", "Player", "Render"]
        self.last_state = None

        self.aimbot = AimbotModule(h, offsets)
        self.velocity = VelocityModule(h, offsets)
        self.fly = FlyModule(h, offsets)
        self.upclip = UpClipModule(h, offsets)
        self.downclip = DownClipModule(h, offsets)
        self.click_tp = ClickTPModule(h, offsets)
        self.xyz_teleport = XyzTeleportModule(h, offsets)
        self.fast_place = FastPlaceModule(h, offsets)
        self.esp = ESPModule(offsets)
        self.watermark = WatermarkModule()
        self.arraylist = ArrayListModule()

        self.modules = [
            self.aimbot,
            self.velocity,
            self.fly,
            self.upclip,
            self.downclip,
            self.click_tp,
            self.xyz_teleport,
            self.fast_place,
            self.esp,
            self.watermark,
            self.arraylist,
        ]

        self.config_path = Path(__file__).resolve().parent.parent.parent / "config.json"
        self.load_config()

    def get_by_category(self, cat):
        return [m for m in self.modules if m.category == cat]

    def get_by_name(self, name):
        for m in self.modules:
            if m.name.lower() == name.lower():
                return m
        return None

    def tick(self, ctx):
        foc = ctx.get("focused", False)
        st = ctx.get("state")
        self.last_state = st

        # Keybind checks
        if foc:
            for m in self.modules:
                if m.keybind:
                    is_down = atapiro_key_down(m.keybind)
                    if m.handle_key(is_down):
                        self.save_config()

        # Tick all active modules
        for m in self.modules:
            if m.enabled or getattr(m, '_need_trigger', False):
                m.tick(ctx)

    def get_active_list(self):
        res = []
        for m in self.modules:
            if m.enabled and m.name not in ("Watermark", "ArrayList"):
                res.append((m.name, m.color))
        return res

    def save_config(self):
        try:
            cfg = {
                "fov": self.esp.fov,
                "modules": {}
            }
            # Dangerous modules that should not stay active on reboot
            danger = {"Fly", "Velocity", "Aimbot", "UpClip", "DownClip", "ClickTP", "XyzTeleport"}
            for m in self.modules:
                m_dict = {
                    "enabled": False if m.name in danger else m.enabled,
                    "keybind": m.keybind
                }
                if hasattr(m, "distance"):
                    m_dict["distance"] = m.distance
                if m.name == "XyzTeleport":
                    m_dict["x_str"] = m.x_str
                    m_dict["y_str"] = m.y_str
                    m_dict["z_str"] = m.z_str
                    m_dict["loop_mode"] = m.loop_mode
                cfg["modules"][m.name] = m_dict
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    def load_config(self):
        if not self.config_path.exists():
            return
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if "fov" in cfg:
                self.esp.fov = float(cfg["fov"])
            m_cfgs = cfg.get("modules", {})
            danger = {"Fly", "Velocity", "Aimbot", "UpClip", "DownClip", "ClickTP", "XyzTeleport"}
            for m in self.modules:
                if m.name in m_cfgs:
                    m.keybind = int(m_cfgs[m.name].get("keybind", m.keybind))
                    if m.name in danger:
                        m.enabled = False
                    else:
                        m.enabled = bool(m_cfgs[m.name].get("enabled", m.enabled))
                    if hasattr(m, "distance") and "distance" in m_cfgs[m.name]:
                        m.distance = float(m_cfgs[m.name]["distance"])
                    if m.name == "XyzTeleport":
                        m.x_str = str(m_cfgs[m.name].get("x_str", ""))
                        m.y_str = str(m_cfgs[m.name].get("y_str", ""))
                        m.z_str = str(m_cfgs[m.name].get("z_str", ""))
                        m.loop_mode = bool(m_cfgs[m.name].get("loop_mode", False))
        except Exception:
            pass
