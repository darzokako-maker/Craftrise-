"""
atapiro 1337 #ONE - CraftRise Unified Modular Client Architecture
"""
import ctypes
import os
import sys
import time
from pathlib import Path

# Force UTF-8 stream handling to eliminate Windows console charmap crash
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.memory import (
    _kernel32, atapiro_set_color, atapiro_reset_color, atapiro_anim,
    atapiro_find_craftrise_pid, atapiro_get_jvm_base, atapiro_retry,
    atapiro_read_u32, atapiro_read_u64, atapiro_key_down, atapiro_is_focused,
    FOREGROUND_GREEN, FOREGROUND_CYAN, FOREGROUND_RED, FOREGROUND_YELLOW,
    FOREGROUND_INTENSITY, K_JAVA_MIRROR_OFFSET
)
from src.core.state import (
    AtapiroMotionContext, atapiro_find_class, atapiro_find_player_offset,
    atapiro_read_game_state
)
from src.core.offsets import load_mappings
from src.modules.manager import ModuleManager
from src.gui.overlay import OverlayManager

def main():
    atapiro_anim("==================================================================", 3, FOREGROUND_CYAN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] atapiro 1337 #ONE - CraftRise NextGen Modular Suite", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("==================================================================", 3, FOREGROUND_CYAN | FOREGROUND_INTENSITY)

    atapiro_anim("[*] searching for CraftRise process...", 6)
    pid = atapiro_retry(atapiro_find_craftrise_pid, timeout_s=120, interval_s=0.5)
    if not pid:
        atapiro_anim("[-] CraftRise (craftrise-x64.exe) bulunamadi!", 6, FOREGROUND_RED | FOREGROUND_INTENSITY)
        atapiro_anim("[-] Once CraftRise launcher'dan oyunu (Oyna'ya basarak) baslatin.", 6, FOREGROUND_YELLOW | FOREGROUND_INTENSITY)
        input("\n[!] Cikmak icin Enter'a basin...")
        sys.exit(1)
    atapiro_anim(f"[+] detected process PID: {pid}", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)

    atapiro_anim("[*] locating jvm.dll...", 6)
    jvm_base = atapiro_retry(lambda: atapiro_get_jvm_base(pid), timeout_s=30, interval_s=0.2)
    if not jvm_base:
        atapiro_anim("[-] failed to find jvm.dll", 6, FOREGROUND_RED | FOREGROUND_INTENSITY)
        input("\n[!] Cikmak icin Enter'a basin...")
        sys.exit(1)
    atapiro_anim(f"[+] jvm.dll base: 0x{jvm_base:X}", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)

    h = _kernel32.OpenProcess(0x1F0FFF, False, pid)
    if not h:
        atapiro_anim("[-] failed to open process (Lutfen Yonetici Olarak / Run as Admin calistirin!)", 6, FOREGROUND_RED | FOREGROUND_INTENSITY)
        input("\n[!] Cikmak icin Enter'a basin...")
        sys.exit(1)

    classes, offsets = load_mappings()
    atapiro_anim("[+] loaded class mappings and struct offsets", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)

    klass_player = classes["EntityPlayerSP"]
    klass_inner = classes["TimerContainer"]
    klass_mc = classes["Minecraft"]
    mc_offset = offsets["Minecraft.theMinecraft"]

    atapiro_anim(f"[*] locating {klass_mc}...", 6)
    k_minecraft = atapiro_retry(lambda: atapiro_find_class(h, jvm_base, klass_mc), timeout_s=30, interval_s=0.2)
    if not k_minecraft:
        atapiro_anim("[-] failed to resolve Minecraft klass", 6, FOREGROUND_RED | FOREGROUND_INTENSITY)
        sys.exit(1)
    atapiro_anim(f"[+] Minecraft klass: 0x{k_minecraft:X}", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)

    atapiro_anim(f"[*] locating {klass_player}...", 6)
    p_klass = atapiro_retry(lambda: atapiro_find_class(h, jvm_base, klass_player), timeout_s=30, interval_s=0.2)
    if not p_klass:
        atapiro_anim("[-] failed to resolve player klass", 6, FOREGROUND_RED | FOREGROUND_INTENSITY)
        input("\nPress Enter to exit...")
        sys.exit(1)
    atapiro_anim(f"[+] player klass: 0x{p_klass:X}", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)

    atapiro_anim(f"[*] locating {klass_inner}...", 6)
    inner_k = atapiro_retry(lambda: atapiro_find_class(h, jvm_base, klass_inner), timeout_s=30, interval_s=0.2)
    if not inner_k:
        atapiro_anim("[-] failed to resolve inner wrapper klass", 6, FOREGROUND_RED | FOREGROUND_INTENSITY)
        input("\nPress Enter to exit...")
        sys.exit(1)
    atapiro_anim(f"[+] inner wrapper klass: 0x{inner_k:X}", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)

    inner_static_offset = offsets["TimerContainer.xorStatic"]
    mc_ctx = AtapiroMotionContext(h, inner_k, inner_static_offset)

    # Initialize Modules & Overlay
    mgr = ModuleManager(h, offsets)
    overlay = OverlayManager(pid, h, offsets, mgr)

    atapiro_anim("================== CONTROLS ==================", 3, FOREGROUND_CYAN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] [INSERT / F12] -> Interactive ClickGUI", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] [R]            -> Aimbot", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] [G]            -> Velocity Bypass", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] [F]            -> Fly", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] [V]            -> UpClip (+3.0 Y)", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] [C]            -> DownClip (-3.0 Y)", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] [Z]            -> ClickTP (Look-Ray Forward)", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] [X]            -> XyzTeleport (Right-Click in GUI for settings)", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] [B]            -> FastPlace", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("[+] [ [ / ] ]      -> Fine-tune FOV (- / +)", 6, FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    atapiro_anim("==============================================", 3, FOREGROUND_CYAN | FOREGROUND_INTENSITY)

    insert_down = False

    while True:
        # Toggle ClickGUI with INSERT (0x2D) or F12 (0x7B)
        ins = (atapiro_key_down(0x2D) or atapiro_key_down(0x7B))
        if ins and not insert_down:
            is_open = overlay.toggle_clickgui()
            sys.stdout.write(f"\r[+] ClickGUI: {'OPEN' if is_open else 'CLOSED'}   \n")
            sys.stdout.flush()
        insert_down = ins

        foc = atapiro_is_focused(pid)
        state = None
        try:
            state = atapiro_read_game_state(h, k_minecraft, mc_offset, p_klass, mc_ctx, offsets)
        except Exception:
            state = None

        # FOV hotkeys
        if foc and not overlay.clickgui.open:
            if atapiro_key_down(0xDB):  # [
                mgr.esp.fov = max(40.0, round(mgr.esp.fov - 0.2, 1))
            elif atapiro_key_down(0xDD):  # ]
                mgr.esp.fov = min(130.0, round(mgr.esp.fov + 0.2, 1))

        ctx = {
            "state": state,
            "focused": foc,
            "mc_ctx": mc_ctx,
            "h": h
        }

        try:
            mgr.tick(ctx)
            overlay.update_state(state)
        except Exception:
            pass

        time.sleep(0.001)

if __name__ == '__main__':
    main()
