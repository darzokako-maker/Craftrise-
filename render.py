"""
atapiro 1337 #ONE - Render Modules (ESP, Watermark, HUD)
"""
from .base import Module
from ..core.memory import atapiro_get_mc_fov

class ESPModule(Module):
    def __init__(self, offsets):
        super().__init__(
            name="ESP & Boxes",
            description="2D bounding boxes and player nametags",
            category="Render",
            default_key=0,
            default_enabled=True,
            color=0x00FFD0
        )
        self.offsets = offsets
        self.fov = atapiro_get_mc_fov()

class WatermarkModule(Module):
    def __init__(self):
        super().__init__(
            name="Watermark",
            description="Premium neon status watermark",
            category="Render",
            default_key=0,
            default_enabled=True,
            color=0xDCEB00
        )

class ArrayListModule(Module):
    def __init__(self):
        super().__init__(
            name="ArrayList",
            description="Active modules display in top right",
            category="Render",
            default_key=0,
            default_enabled=True,
            color=0x50FF78
        )
