"""
atapiro 1337 #ONE - Dynamic Live Mappings & Offsets Manager
"""
import json
import os
import time
from pathlib import Path

def resolve_live_mappings(pid, timeout_s=30):
    from ..mapper.jvm_reader import JVMProcess
    from ..mapper.class_solver import solve_classes
    from ..mapper.member_solver import solve_members

    t0 = time.time()
    while time.time() - t0 < timeout_s:
        jvm = None
        try:
            jvm = JVMProcess(pid=pid)
            jvm.load_classes()
            resolved_classes = solve_classes(jvm)
            if "Minecraft" in resolved_classes and "EntityPlayerSP" in resolved_classes:
                members, member_meta, _ = solve_members(jvm, resolved_classes)
                data = {}
                for cls_name, slash in resolved_classes.items():
                    data[cls_name] = {
                        "internal": slash,
                        "fields": {},
                        "methods": {},
                    }
                for key, (kind, blk, deobf, obf, desc) in members.items():
                    if blk not in data:
                        continue
                    meta = member_meta.get(key, {})
                    if kind == "f":
                        data[blk]["fields"][deobf] = {
                            "obf": obf,
                            "desc": meta.get("desc") or desc,
                            "offset": meta.get("offset"),
                            "static": bool(meta.get("static")),
                        }
                return data
        except Exception:
            pass
        finally:
            if jvm is not None:
                try:
                    jvm.close()
                except Exception:
                    pass
        time.sleep(0.5)
    return {}

def load_mappings(mappings_path=None, pid=None):
    mappings = {}
    if pid:
        mappings = resolve_live_mappings(pid)

    if not mappings:
        if mappings_path is None:
            candidates = [
                Path.cwd() / "Mappings.json",
                Path(__file__).resolve().parent / "Mappings.json",
                Path(__file__).resolve().parent.parent.parent / "Mappings.json",
                Path(__file__).resolve().parent.parent / "Mappings.json",
            ]
            for c in candidates:
                if c.exists():
                    mappings_path = str(c)
                    break

        if mappings_path and os.path.exists(mappings_path):
            try:
                with open(mappings_path, 'r', encoding='utf-8', errors='ignore') as f:
                    mappings = json.load(f)
            except Exception:
                mappings = {}

    def get_cls(name, fallback=""):
        return mappings.get(name, {}).get("internal", fallback)

    def get_off(cname, fname, fallback=0):
        val = mappings.get(cname, {}).get("fields", {}).get(fname, {}).get("offset")
        return val if val is not None else fallback

    classes = {
        "Minecraft": get_cls("Minecraft", "craftrise/ɳ"),
        "EntityPlayerSP": get_cls("EntityPlayerSP", "craftrise/ɍВ"),
        "Entity": get_cls("Entity", "craftrise/ɍɍ"),
        "TimerContainer": get_cls("TimerContainer", "crsecond/ɟ"),
    }

    offsets = {
        "Minecraft.theMinecraft": get_off("Minecraft", "theMinecraft", 376),
        "Minecraft.thePlayer": get_off("Minecraft", "thePlayer", 296),
        "Minecraft.theWorld": get_off("Minecraft", "theWorld", 236),
        "Minecraft.rightClickDelayTimer": get_off("Minecraft", "rightClickDelayTimer", 184),
        "TimerContainer.xorStatic": get_off("TimerContainer", "xorStatic", 112),
        "Entity.posX": get_off("Entity", "posX", 64),
        "Entity.posY": get_off("Entity", "posY", 48),
        "Entity.posZ": get_off("Entity", "posZ", 80),
        "Entity.lastTickPosX": get_off("Entity", "lastTickPosX", 96),
        "Entity.lastTickPosY": get_off("Entity", "lastTickPosY", 40),
        "Entity.lastTickPosZ": get_off("Entity", "lastTickPosZ", 72),
        "Entity.prevPosX": get_off("Entity", "prevPosX", 104),
        "Entity.prevPosY": get_off("Entity", "prevPosY", 88),
        "Entity.prevPosZ": get_off("Entity", "prevPosZ", 24),
        "Entity.rotationYaw": get_off("Entity", "rotationYaw", 148),
        "Entity.rotationPitch": get_off("Entity", "rotationPitch", 136),
        "Entity.prevRotationYaw": get_off("Entity", "prevRotationYaw", 200),
        "Entity.prevRotationPitch": get_off("Entity", "prevRotationPitch", 172),
        "Entity.fallDistance": get_off("Entity", "fallDistance", 240),
        "Entity.entityId": get_off("Entity", "entityId", 160),
        "Entity.boundingBox": get_off("Entity", "boundingBox", 312),
        "Entity.motionX": get_off("Entity", "motionX", 304),
        "Entity.motionY": get_off("Entity", "motionY", 292),
        "Entity.motionZ": get_off("Entity", "motionZ", 320),
        "Entity.worldObj": get_off("Entity", "worldObj", 288),
        "World.playerEntities": get_off("World", "playerEntities", 232),
        "AABB.minY": 40,
        "AABB.maxY": 32,
        "AABB.minX": 48,
        "AABB.maxX": 16,
        "AABB.minZ": 24,
        "AABB.maxZ": 56,
    }

    return classes, offsets