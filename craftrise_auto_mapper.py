import argparse
import ctypes
import json
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from jvm_reader import JVMProcess
from class_solver import solve_classes
from member_solver import TARGET_MEMBERS, solve_members


def enable_vt():
    if not getattr(sys.stdout, "isatty", lambda: False)():
        return False
    try:
        k32 = ctypes.windll.kernel32
        h = k32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if k32.GetConsoleMode(h, ctypes.byref(mode)):
            return bool(k32.SetConsoleMode(h, mode.value | 0x0004))
    except Exception:
        pass
    return False


USE_COLOR = enable_vt()
C_DIM = "\033[90m" if USE_COLOR else ""
C_CYN = "\033[96m" if USE_COLOR else ""
C_GRN = "\033[92m" if USE_COLOR else ""
C_YLW = "\033[93m" if USE_COLOR else ""
C_MAG = "\033[95m" if USE_COLOR else ""
C_WHT = "\033[97m" if USE_COLOR else ""
C_RST = "\033[0m" if USE_COLOR else ""

CORE_KLASSES = [
    "Minecraft",
    "Entity",
    "EntityLivingBase",
    "EntityPlayer",
    "AbstractClientPlayer",
    "EntityPlayerSP",
    "EntityItem",
    "World",
    "WorldClient",
    "Chunk",
    "Timer",
    "TimerContainer",
    "MotionContainer",
    "BooleanContainer",
    "FloatContainer",
    "IntegerWrapper",
    "GameSettings",
    "KeyBinding",
    "PlayerControllerMP",
    "NetHandlerPlayClient",
    "NetworkManager",
    "NetworkPlayerInfo",
    "GameProfile",
    "Packet",
    "RenderManager",
    "FontRenderer",
    "Container",
    "InventoryPlayer",
    "Slot",
    "ItemStack",
    "Item",
    "EnchantmentHelper",
    "Block",
    "IBlockState",
    "BlockPos",
    "Vec3",
    "AxisAlignedBB",
    "MovingObjectPosition",
    "IChatComponent",
    "GuiScreen",
    "GuiChat",
    "GuiContainer",
    "GuiChest",
    "GuiInventory",
]


def build_json(resolved_classes, members, member_meta):
    data = {}
    for cls_name in sorted(resolved_classes):
        slash = resolved_classes[cls_name]
        data[cls_name] = {
            "obf": slash.replace("/", "."),
            "internal": slash,
            "desc": f"L{slash};",
            "fields": {},
            "methods": {},
        }

    for key, (kind, blk, deobf, obf, desc) in sorted(members.items()):
        if blk not in data:
            continue
        meta = member_meta.get(key, {})
        actual_desc = meta.get("desc") or desc
        if kind == "f":
            data[blk]["fields"][deobf] = {
                "obf": obf,
                "desc": actual_desc,
                "offset": meta.get("offset"),
                "static": bool(meta.get("static")),
            }
        else:
            data[blk]["methods"][deobf] = {
                "obf": obf,
                "desc": actual_desc,
                "static": bool(meta.get("static")),
            }
    return data


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--pid", type=int, default=None)
    parser.add_argument("--proc", type=str, default="craftrise-x64.exe")
    args, _ = parser.parse_known_args()

    t0 = time.perf_counter()
    try:
        jvm = JVMProcess(pid=args.pid, exe_name=args.proc)
    except Exception as exc:
        print(f"err: {exc}")
        return 1

    try:
        print(
            f"{C_CYN}[vm]{C_RST} process  {C_WHT}{args.proc}{C_RST} "
            f"{C_DIM}(pid: {jvm.pid}, handle: 0x{int(jvm.hProc):X}){C_RST}"
        )
        print(
            f"{C_CYN}[vm]{C_RST} module   {C_WHT}jvm.dll{C_RST} @ {C_YLW}0x{jvm.jvm_base:016X}{C_RST}"
        )
        print(
            f"{C_CYN}[vm]{C_RST} structs  {C_WHT}gHotSpotVMStructs{C_RST} @ {C_YLW}0x{jvm.vmstructs_exp:016X}{C_RST} "
            f"-> {C_YLW}0x{jvm.vmstructs_table:016X}{C_RST} "
            f"{C_DIM}({len(jvm.vm_structs)} entries, {len(jvm.vm_types)} vm_types){C_RST}"
        )
        print(
            f"{C_CYN}[vm]{C_RST} narrow   oop_base: {C_YLW}0x{jvm.narrow_oop_base:016X}{C_RST} (shift: {jvm.narrow_oop_shift}) | "
            f"klass_base: {C_YLW}0x{jvm.narrow_klass_base:016X}{C_RST} (shift: {jvm.narrow_klass_shift})"
        )

        t_scan0 = time.perf_counter()
        jvm.load_classes()
        t_scan1 = time.perf_counter()

        print(
            f"{C_CYN}[vm]{C_RST} cld_head {C_WHT}ClassLoaderDataGraph::_head{C_RST} @ {C_YLW}0x{jvm.cld_head_addr:016X}{C_RST} "
            f"-> {C_YLW}0x{jvm.cld_first:016X}{C_RST} "
            f"{C_DIM}({jvm.cld_count} loaders, {jvm.total_jvm_klasses} total klasses){C_RST}"
        )
        print(
            f"{C_CYN}[vm]{C_RST} indexed  {C_GRN}{len(jvm.classes)}{C_RST} target InstanceKlass | "
            f"{C_GRN}{len(jvm.cp_methods)}{C_RST} ConstantPool klass refs "
            f"{C_DIM}({t_scan1 - t_scan0:.2f}s){C_RST}"
        )

        resolved_classes = solve_classes(jvm)
        members, member_meta, missing = solve_members(jvm, resolved_classes)

        mc_oop = 0
        mc_slash = resolved_classes.get("Minecraft")
        if mc_slash and "Minecraft.theMinecraft" in member_meta:
            mc_off = member_meta["Minecraft.theMinecraft"].get("offset")
            if isinstance(mc_off, int) and mc_slash in jvm.classes:
                mc_oop = jvm.read_oop_field(jvm.classes[mc_slash]["mirror"], mc_off)

        if mc_oop:
            print(
                f"{C_CYN}[vm]{C_RST} heap_oop {C_WHT}Minecraft::theMinecraft{C_RST} -> "
                f"{C_GRN}0x{mc_oop:016X}{C_RST} {C_DIM}(klass: 0x{jvm.oop_klass(mc_oop):016X}){C_RST}"
            )

        for cname in CORE_KLASSES:
            slash = resolved_classes.get(cname)
            if not slash:
                continue
            info = jvm.classes.get(slash)
            if info:
                print(
                    f"{C_MAG}[ik]{C_RST} {C_YLW}0x{info['klass']:016X}{C_RST}  "
                    f"sym: {C_DIM}0x{info['sym']:016X}{C_RST}  "
                    f"mirror: {C_DIM}0x{info['mirror']:016X}{C_RST}  "
                    f"{C_WHT}{cname:<22}{C_RST} -> {C_GRN}{slash}{C_RST}"
                )
            else:
                cp_m = len(jvm.cp_methods.get(slash, ()))
                cp_f = len(jvm.cp_fields.get(slash, ()))
                print(
                    f"{C_YLW}[cp]{C_RST} {C_DIM}<unloaded_klass>  "
                    f"cp_methods: {cp_m:<3}       cp_fields: {cp_f:<3}        {C_RST}  "
                    f"{C_WHT}{cname:<22}{C_RST} -> {C_GRN}{slash}{C_RST}"
                )

        for key in TARGET_MEMBERS:
            if key not in members:
                continue
            kind, blk, deobf, obf, desc = members[key]
            meta = member_meta.get(key, {})
            label = f"{blk}::{deobf}"
            if kind == "f":
                off = meta.get("offset")
                off_s = f"0x{off:04X}" if isinstance(off, int) else "n/a   "
                scope = "static" if meta.get("static") else "field "
                print(
                    f"{C_CYN}[fd]{C_RST} {scope} off: {C_YLW}{off_s}{C_RST}              "
                    f"{C_WHT}{label:<34}{C_RST} -> {C_GRN}{obf:<8}{C_RST} {C_DIM}{desc}{C_RST}"
                )
            else:
                mp = meta.get("mp") or 0
                csz = meta.get("code_sz") or 0
                mp_s = f"0x{mp:016X}" if mp else "<cp_method_ref>   "
                print(
                    f"{C_GRN}[mt]{C_RST} Method*: {C_YLW}{mp_s}{C_RST} "
                    f"{C_WHT}{label:<34}{C_RST} -> {C_GRN}{obf:<8}{C_RST} {C_DIM}{desc} ({csz}B){C_RST}"
                )

        classes_snap = dict(jvm.classes)
    finally:
        jvm.close()

    out_path = BASE_DIR / "Mappings.json"
    payload = build_json(resolved_classes, members, member_meta)
    raw_json = json.dumps(payload, ensure_ascii=False, indent=2)
    out_path.write_text(raw_json, encoding="utf-8")

    loaded_resolved = sum(1 for v in resolved_classes.values() if v in classes_snap)
    cp_resolved = len(resolved_classes) - loaded_resolved
    dt = time.perf_counter() - t0
    print(
        f"{C_GRN}[ok]{C_RST} klasses: {C_WHT}{len(resolved_classes)}{C_RST} "
        f"{C_DIM}(live: {loaded_resolved}, cp: {cp_resolved}){C_RST} | "
        f"members: {C_WHT}{len(members)}/{len(TARGET_MEMBERS)}{C_RST} | "
        f"out: {C_GRN}{out_path.name}{C_RST} {C_DIM}({len(raw_json.encode('utf-8')):,}B, {dt:.2f}s){C_RST}"
    )
    if missing:
        print(f"missing: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
