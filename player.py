"""
atapiro 1337 #ONE - Player Modules (FastPlace)
"""
from .base import Module
from ..core.memory import atapiro_key_down, atapiro_write_i32

class FastPlaceModule(Module):
    def __init__(self, h, offsets=None):
        super().__init__(
            name="FastPlace",
            description="Eliminates block placement delay timer",
            category="Player",
            default_key=ord('B'),
            default_enabled=True,
            color=0x00E0FF
        )
        self.h = h
        self.offsets = offsets or {}

    def tick(self, ctx):
        st = ctx.get("state")
        foc = ctx.get("focused", False)
        if self.enabled and foc and st and st.instance_ptr and atapiro_key_down(0x02):
            delay_off = self.offsets.get("Minecraft.rightClickDelayTimer", 184)
            atapiro_write_i32(self.h, st.instance_ptr + delay_off, 0)
