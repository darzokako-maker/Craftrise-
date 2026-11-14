"""
atapiro 1337 #ONE - Mappings & Offsets Manager
"""
import json
import os
from pathlib import Path

def load_mappings(mappings_path=None):
    if mappings_path is None:
        candidates = [
            Path(__file__).resolve().parent / "Mappings.json",
            Path(__file__).resolve().parent.parent.parent / "Mappings.json",
            Path.cwd() / "Mappings.json",
            Path(__file__).resolve().parent.parent / "Mappings.json",
        ]
        for c in candidates:
            if c.exists():
                mappings_path = str(c)
                break

    mappings = {}
    if mappings_path and os.path.exists(mappings_path):
        try:
            with open(mappings_path, 'r', encoding='utf-8', errors='ignore') as f:
                mappings = json.load(f)
        except Exception:
            mappings = {}

    def get_cls(name, fallback=""):
        return mappings.get(name, {}).get("internal", fallback)

    def get_off(cname, fname, fallback=0):
        return mappings.get(cname, {}).get("fields", {}).get(fname, {}).get("offset", fallback)

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
