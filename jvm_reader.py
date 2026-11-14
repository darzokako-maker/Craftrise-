import collections
import ctypes
import struct
k32 = ctypes.windll.kernel32
PROCESS_QUERY_INFORMATION = 1024
PROCESS_VM_READ = 16
TH32CS_SNAPPROCESS = 2
TH32CS_SNAPMODULE = 8
TH32CS_SNAPMODULE32 = 16

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [('dwSize', ctypes.c_uint32), ('cntUsage', ctypes.c_uint32), ('th32ProcessID', ctypes.c_uint32), ('th32DefaultHeapID', ctypes.c_size_t), ('th32ModuleID', ctypes.c_uint32), ('cntThreads', ctypes.c_uint32), ('th32ParentProcessID', ctypes.c_uint32), ('pcPriClassBase', ctypes.c_int32), ('dwFlags', ctypes.c_uint32), ('szExeFile', ctypes.c_wchar * 260)]

class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [('dwSize', ctypes.c_uint32), ('th32ModuleID', ctypes.c_uint32), ('th32ProcessID', ctypes.c_uint32), ('GlblcntUsage', ctypes.c_uint32), ('ProccntUsage', ctypes.c_uint32), ('modBaseAddr', ctypes.c_void_p), ('modBaseSize', ctypes.c_uint32), ('hModule', ctypes.c_void_p), ('szModule', ctypes.c_wchar * 256), ('szExePath', ctypes.c_wchar * 260)]

def find_process_pid(exe_name='craftrise-x64.exe'):
    target = exe_name.lower()
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap in (-1, 0, 18446744073709551615):
        return 0
    try:
        pe = PROCESSENTRY32W(dwSize=ctypes.sizeof(PROCESSENTRY32W))
        if k32.Process32FirstW(snap, ctypes.byref(pe)):
            while True:
                if pe.szExeFile.lower() == target:
                    return int(pe.th32ProcessID)
                if not k32.Process32NextW(snap, ctypes.byref(pe)):
                    break
    finally:
        k32.CloseHandle(snap)
    return 0

def find_module_base(pid, mod_name='jvm.dll'):
    target = mod_name.lower()
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
    if snap in (-1, 0, 18446744073709551615):
        return 0
    try:
        me = MODULEENTRY32W(dwSize=ctypes.sizeof(MODULEENTRY32W))
        if k32.Module32FirstW(snap, ctypes.byref(me)):
            while True:
                if me.szModule.lower() == target:
                    return int(me.modBaseAddr or 0)
                if not k32.Module32NextW(snap, ctypes.byref(me)):
                    break
    finally:
        k32.CloseHandle(snap)
    return 0

def parse_method_desc(desc):
    if not desc or not desc.startswith('(') or ')' not in desc:
        return None
    try:
        args = []
        i = 1
        while desc[i] != ')':
            s = i
            while desc[i] == '[':
                i += 1
            if desc[i] == 'L':
                i = desc.index(';', i) + 1
            else:
                i += 1
            args.append(desc[s:i])
        return (args, desc[i + 1:])
    except Exception:
        return None

class ClassCP:

    def __init__(self, jvm, klass_addr):
        self.jvm = jvm
        self.klass = klass_addr
        self.mirror = jvm.r8(klass_addr + jvm.off_klass_mirror)
        self.cp = jvm.r8(klass_addr + jvm.off_ik_constants)
        self.cp_cache = jvm.r8(self.cp + jvm.off_cp_cache) if self.cp else 0
        self.cp_len = jvm.r4(self.cp + jvm.off_cp_length) if self.cp else 0
        tags_arr = jvm.r8(self.cp + jvm.off_cp_tags) if self.cp else 0
        self.tags = jvm.rpm(tags_arr + 4, self.cp_len) if tags_arr and 0 < self.cp_len < 32768 else b''
        slots_raw = jvm.rpm(self.cp + jvm.sizeof_cp, self.cp_len * 8) if len(self.tags) == self.cp_len else b''
        self.slots = struct.unpack(f'<{self.cp_len}Q', slots_raw) if len(slots_raw) == self.cp_len * 8 else ()
        self.cache_len = jvm.r4(self.cp_cache + jvm.off_cpc_length) if self.cp_cache else 0
        jobj = jvm.r8(self.cp + jvm.off_cp_resolved_refs) if self.cp else 0
        self.res_refs_oop = jvm.r8(jobj) if jobj else 0

    def utf8(self, idx):
        if 0 < idx < len(self.slots) and self.tags[idx] == 1:
            return self.jvm.read_symbol(self.slots[idx])
        return ''

    def class_name(self, idx):
        if not 0 < idx < len(self.slots):
            return ''
        t = self.tags[idx]
        val = self.slots[idx]
        if t == 7:
            return self.jvm.read_symbol(self.jvm.r8(val + self.jvm.off_klass_name))
        if t in (100, 103, 104):
            return self.jvm.read_symbol(val)
        return ''

    def member_ref_from_cp(self, cp_idx):
        if not 0 < cp_idx < len(self.slots):
            return None
        t = self.tags[cp_idx]
        if t not in (9, 10, 11):
            return None
        packed = self.slots[cp_idx] & 4294967295
        k_idx = packed & 65535
        nt_idx = packed >> 16 & 65535
        owner = self.class_name(k_idx)
        if 0 < nt_idx < len(self.slots) and self.tags[nt_idx] == 12:
            nt_packed = self.slots[nt_idx] & 4294967295
            n_idx = nt_packed & 65535
            s_idx = nt_packed >> 16 & 65535
            return (owner, self.utf8(n_idx), self.utf8(s_idx))
        return None

    def member_ref_from_cache(self, cache_idx):
        if not self.cp_cache or not 0 <= cache_idx < self.cache_len:
            return None
        entry_addr = self.cp_cache + self.jvm.sizeof_cpc + cache_idx * self.jvm.sizeof_cpce
        indices = self.jvm.r8(entry_addr + self.jvm.off_cpce_indices)
        cp_idx = indices & 65535
        return self.member_ref_from_cp(cp_idx)

    def resolved_ref_str(self, ref_idx):
        if not self.res_refs_oop:
            return None
        arr_len = self.jvm.r4(self.res_refs_oop + 12)
        if not 0 <= ref_idx < arr_len:
            return None
        elem_oop = self.jvm.read_oop_field(self.res_refs_oop, 16 + ref_idx * 4)
        if not elem_oop:
            return None
        kn = self.jvm.oop_sym_name(elem_oop)
        if kn == 'java/lang/String':
            return self.jvm.read_jstring(elem_oop)
        return f'<{kn}>'

    def const_val(self, cp_idx):
        if not 0 < cp_idx < len(self.slots):
            return None
        t = self.tags[cp_idx]
        v = self.slots[cp_idx]
        if t == 3:
            return struct.unpack('<i', struct.pack('<I', v & 4294967295))[0]
        if t == 4:
            return round(struct.unpack('<f', struct.pack('<I', v & 4294967295))[0], 6)
        if t == 5:
            return struct.unpack('<q', struct.pack('<Q', v))[0]
        if t == 6:
            return round(struct.unpack('<d', struct.pack('<Q', v))[0], 6)
        if t in (8, 101, 105):
            return self.jvm.read_symbol(v)
        if t in (7, 100, 103, 104):
            return f'Class<{self.class_name(cp_idx)}>'
        return None

class JVMProcess:

    def __init__(self, pid=None, exe_name='craftrise-x64.exe'):
        self.pid = pid or find_process_pid(exe_name)
        if not self.pid:
            raise RuntimeError(f"Process '{exe_name}' bulunamadi! Oyunun arkada acik oldugundan emin ol.")
        self.jvm_base = find_module_base(self.pid, 'jvm.dll')
        if not self.jvm_base:
            raise RuntimeError(f'PID {self.pid} icinde jvm.dll modulu bulunamadi!')
        self.hProc = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, self.pid)
        if not self.hProc:
            err = k32.GetLastError()
            raise RuntimeError(f'OpenProcess(PID={self.pid}) basarisiz oldu (WinError {err}).')
        self.sym_cache = {}
        self._cp_cache = {}
        self._disasm_cache = {}
        self.vm_structs = {}
        self.vm_types = {}
        self._parse_hotspot_tables()
        self.off_sym_len = self._off('Symbol::_length', 0)
        self.off_sym_body = self._off('Symbol::_body', 8)
        self.off_cld_klasses = self._off('ClassLoaderData::_klasses', 40)
        self.off_cld_next = self._off('ClassLoaderData::_next', 72)
        self.off_klass_name = self._off('Klass::_name', 16)
        self.off_klass_mirror = self._off('Klass::_java_mirror', 104)
        self.off_klass_super = self._off('Klass::_super', 112)
        self.off_klass_next_link = self._off('Klass::_next_link', 136)
        self.off_klass_acc = self._off('Klass::_access_flags', 152)
        self.off_ik_constants = self._off('InstanceKlass::_constants', 216)
        self.off_ik_jfc = self._off('InstanceKlass::_java_fields_count', 262)
        self.off_ik_methods = self._off('InstanceKlass::_methods', 384)
        self.off_ik_ifaces = self._off('InstanceKlass::_local_interfaces', 400)
        self.off_ik_fields = self._off('InstanceKlass::_fields', 432)
        self.off_cp_tags = self._off('ConstantPool::_tags', 8)
        self.off_cp_cache = self._off('ConstantPool::_cache', 16)
        self.off_cp_resolved_refs = self._off('ConstantPool::_resolved_references', 40)
        self.off_cp_length = self._off('ConstantPool::_length', 60)
        self.sizeof_cp = self.vm_types.get('ConstantPool', 80)
        self.off_cpc_length = self._off('ConstantPoolCache::_length', 0)
        self.sizeof_cpc = self.vm_types.get('ConstantPoolCache', 16)
        self.sizeof_cpce = self.vm_types.get('ConstantPoolCacheEntry', 32)
        self.off_cpce_indices = self._off('ConstantPoolCacheEntry::_indices', 0)
        self.off_method_cm = self._off('Method::_constMethod', 8)
        self.off_method_acc = self._off('Method::_access_flags', 32)
        self.off_cm_code_sz = self._off('ConstMethod::_code_size', 30)
        self.off_cm_name_idx = self._off('ConstMethod::_name_index', 32)
        self.off_cm_sig_idx = self._off('ConstMethod::_signature_index', 34)
        self.sizeof_cm = self.vm_types.get('ConstMethod', 48)
        noop_base_addr = self.vm_structs['Universe::_narrow_oop._base']['address']
        noop_shift_addr = self.vm_structs['Universe::_narrow_oop._shift']['address']
        nkl_base_addr = self.vm_structs['Universe::_narrow_klass._base']['address']
        nkl_shift_addr = self.vm_structs['Universe::_narrow_klass._shift']['address']
        self.narrow_oop_base = self.r8(noop_base_addr)
        self.narrow_oop_shift = self.r4(noop_shift_addr)
        self.narrow_klass_base = self.r8(nkl_base_addr)
        self.narrow_klass_shift = self.r4(nkl_shift_addr)
        self.classes = {}
        self.klass_to_name = {}
        self.mirror_to_name = {}
        self.children = collections.defaultdict(list)
        self.impls = collections.defaultdict(list)
        self.cp_fields = collections.defaultdict(set)
        self.cp_methods = collections.defaultdict(set)
        self.cp_method_callers = collections.defaultdict(set)

    def close(self):
        if getattr(self, 'hProc', 0):
            k32.CloseHandle(self.hProc)
            self.hProc = 0

    def _off(self, key, default):
        entry = self.vm_structs.get(key)
        return int(entry['offset']) if entry and (not entry['static']) else default

    def rpm(self, addr, size):
        if not addr or addr < 65536 or size <= 0:
            return b''
        buf = (ctypes.c_char * size)()
        rd = ctypes.c_size_t()
        if k32.ReadProcessMemory(self.hProc, ctypes.c_void_p(addr), buf, size, ctypes.byref(rd)):
            return bytes(buf[:rd.value])
        return b''

    def r8(self, addr):
        b = self.rpm(addr, 8)
        return struct.unpack('<Q', b)[0] if len(b) == 8 else 0

    def r8s(self, addr):
        b = self.rpm(addr, 8)
        return struct.unpack('<q', b)[0] if len(b) == 8 else 0

    def r4(self, addr):
        b = self.rpm(addr, 4)
        return struct.unpack('<I', b)[0] if len(b) == 4 else 0

    def r4s(self, addr):
        b = self.rpm(addr, 4)
        return struct.unpack('<i', b)[0] if len(b) == 4 else 0

    def r2(self, addr):
        b = self.rpm(addr, 2)
        return struct.unpack('<H', b)[0] if len(b) == 2 else 0

    def r1(self, addr):
        b = self.rpm(addr, 1)
        return b[0] if len(b) == 1 else 0

    def cstr(self, addr, max_len=256):
        b = self.rpm(addr, max_len)
        return b.split(b'\x00', 1)[0].decode('utf-8', 'replace') if b else ''

    def _get_hotspot_exports(self):
        dos = self.rpm(self.jvm_base, 64)
        if len(dos) < 64 or dos[:2] != b'MZ':
            raise RuntimeError('jvm.dll DOS header okunamadi!')
        e_lfanew = struct.unpack('<I', dos[60:64])[0]
        nt = self.rpm(self.jvm_base + e_lfanew, 288)
        exp_rva, exp_sz = struct.unpack('<II', nt[136:144])
        exp = self.rpm(self.jvm_base + exp_rva, exp_sz)
        num_names, funcs_rva, names_rva, ord_rva = struct.unpack('<IIII', exp[24:40])
        names_arr = struct.unpack(f'<{num_names}I', self.rpm(self.jvm_base + names_rva, num_names * 4))
        ords_arr = struct.unpack(f'<{num_names}H', self.rpm(self.jvm_base + ord_rva, num_names * 2))
        out = {}
        for i in range(num_names):
            name = self.cstr(self.jvm_base + names_arr[i], 128)
            if 'HotSpot' in name:
                frva = self.r4(self.jvm_base + funcs_rva + ords_arr[i] * 4)
                out[name] = self.jvm_base + frva
        return out

    def _parse_hotspot_tables(self):
        exps = self._get_hotspot_exports()
        if 'gHotSpotVMStructs' not in exps:
            raise RuntimeError("jvm.dll icinde gHotSpotVMStructs export'u bulunamadi!")
        self.vmstructs_exp = exps['gHotSpotVMStructs']
        self.vmtypes_exp = exps.get('gHotSpotVMTypes', 0)
        cur = self.r8(exps['gHotSpotVMStructs'])
        self.vmstructs_table = cur
        stride = self.r8(exps['gHotSpotVMStructEntryArrayStride'])
        off_type = self.r8(exps['gHotSpotVMStructEntryTypeNameOffset'])
        off_field = self.r8(exps['gHotSpotVMStructEntryFieldNameOffset'])
        off_tstr = self.r8(exps['gHotSpotVMStructEntryTypeStringOffset'])
        off_static = self.r8(exps['gHotSpotVMStructEntryIsStaticOffset'])
        off_offset = self.r8(exps['gHotSpotVMStructEntryOffsetOffset'])
        off_addr = self.r8(exps['gHotSpotVMStructEntryAddressOffset'])
        while True:
            fn_ptr = self.r8(cur + off_field)
            if not fn_ptr:
                break
            tn = self.cstr(self.r8(cur + off_type))
            fn = self.cstr(fn_ptr)
            self.vm_structs[f'{tn}::{fn}'] = {'type': self.cstr(self.r8(cur + off_tstr)), 'static': bool(self.r4(cur + off_static)), 'offset': self.r8(cur + off_offset), 'address': self.r8(cur + off_addr)}
            cur += stride
        if 'gHotSpotVMTypes' in exps:
            t_cur = self.r8(exps['gHotSpotVMTypes'])
            t_stride = self.r8(exps['gHotSpotVMTypeEntryArrayStride'])
            t_name_off = self.r8(exps['gHotSpotVMTypeEntryTypeNameOffset'])
            t_size_off = self.r8(exps['gHotSpotVMTypeEntrySizeOffset'])
            while True:
                tn_ptr = self.r8(t_cur + t_name_off)
                if not tn_ptr:
                    break
                self.vm_types[self.cstr(tn_ptr)] = self.r8(t_cur + t_size_off)
                t_cur += t_stride

    def read_symbol(self, sym_addr):
        if not sym_addr:
            return ''
        sym_addr &= ~3
        cached = self.sym_cache.get(sym_addr)
        if cached is not None:
            return cached
        hdr = self.rpm(sym_addr, 64)
        if len(hdr) < self.off_sym_body:
            return ''
        ln = struct.unpack('<H', hdr[self.off_sym_len:self.off_sym_len + 2])[0]
        if ln == 0 or ln > 16384:
            return ''
        body_off = self.off_sym_body
        if ln <= len(hdr) - body_off:
            s = hdr[body_off:body_off + ln].decode('utf-8', 'replace')
        else:
            s = self.rpm(sym_addr + body_off, ln).decode('utf-8', 'replace')
        self.sym_cache[sym_addr] = s
        return s

    def decode_oop(self, narrow):
        if not narrow:
            return 0
        return self.narrow_oop_base + (narrow << self.narrow_oop_shift)

    def decode_klass(self, narrow_klass):
        if not narrow_klass:
            return 0
        return self.narrow_klass_base + (narrow_klass << self.narrow_klass_shift)

    def read_oop_field(self, obj_addr, offset):
        if not obj_addr:
            return 0
        return self.decode_oop(self.r4(obj_addr + offset))

    def oop_klass(self, oop):
        if not oop:
            return 0
        return self.decode_klass(self.r4(oop + 8))

    def oop_sym_name(self, oop):
        kl = self.oop_klass(oop)
        return self.read_symbol(self.r8(kl + self.off_klass_name)) if kl else ''

    def oop_class_name(self, oop):
        kl = self.oop_klass(oop)
        return self.klass_to_name.get(kl, '') or (self.read_symbol(self.r8(kl + self.off_klass_name)) if kl else '')

    def read_jstring(self, str_oop):
        if not str_oop:
            return ''
        char_arr = self.read_oop_field(str_oop, 12)
        if not char_arr:
            return ''
        length = self.r4(char_arr + 12)
        if length == 0 or length > 4096:
            return ''
        raw = self.rpm(char_arr + 16, length * 2)
        return raw.decode('utf-16-le', 'replace')

    def read_hashmap_str_to_class(self, map_oop):
        out = {}
        if not map_oop:
            return out
        table_oop = 0
        for off in range(12, 48, 4):
            cand = self.read_oop_field(map_oop, off)
            if cand and 'HashMap$Node' in self.oop_sym_name(cand):
                table_oop = cand
                break
        if not table_oop:
            return out
        arr_len = self.r4(table_oop + 12)
        if arr_len <= 0 or arr_len > 65536:
            return out
        for i in range(arr_len):
            node = self.read_oop_field(table_oop, 16 + i * 4)
            steps = 0
            while node and steps < 64:
                steps += 1
                k_oop = self.read_oop_field(node, 16)
                v_oop = self.read_oop_field(node, 20)
                nxt = self.read_oop_field(node, 24)
                if self.oop_sym_name(k_oop) == 'java/lang/String' and v_oop in self.mirror_to_name:
                    out[self.read_jstring(k_oop)] = self.mirror_to_name[v_oop]
                elif v_oop and self.oop_sym_name(v_oop) == 'java/lang/String' and (k_oop in self.mirror_to_name):
                    out[self.read_jstring(v_oop)] = self.mirror_to_name[k_oop]
                node = nxt
        return out

    def enum_constant_names(self, cls_name):
        info = self.classes.get(cls_name)
        if not info or info['super'] != 'java/lang/Enum':
            return []
        mirror = info['mirror']
        names = []
        for f in info['fields']:
            if f['static'] and f['desc'] == f'L{cls_name};':
                e_oop = self.read_oop_field(mirror, f['offset'])
                if e_oop:
                    nm = self.read_jstring(self.read_oop_field(e_oop, 16))
                    if nm:
                        names.append(nm)
        return names

    def load_classes(self):
        cld_head = self.vm_structs['ClassLoaderDataGraph::_head']['address']
        cld = self.r8(cld_head)
        self.cld_head_addr = cld_head
        self.cld_first = cld
        all_klasses = []
        seen_cld = set()
        while cld and cld not in seen_cld:
            seen_cld.add(cld)
            k = self.r8(cld + self.off_cld_klasses)
            seen_k = set()
            while k and k not in seen_k:
                seen_k.add(k)
                nm = self.read_symbol(self.r8(k + self.off_klass_name))
                if nm and (not nm.startswith('[')) and ('$$Lambda' not in nm):
                    all_klasses.append((nm, k))
                k = self.r8(k + self.off_klass_next_link)
            cld = self.r8(cld + self.off_cld_next)
        self.cld_count = len(seen_cld)
        self.total_jvm_klasses = len(all_klasses)
        target_prefixes = ('craftrise/', 'crsecond/', 'com/mojang/authlib/')
        for nm, k in all_klasses:
            if not nm.startswith(target_prefixes):
                continue
            k_hdr = self.rpm(k, 456)
            if len(k_hdr) < 440:
                continue
            acc = struct.unpack('<I', k_hdr[self.off_klass_acc:self.off_klass_acc + 4])[0] & 65535
            mirror = struct.unpack('<Q', k_hdr[self.off_klass_mirror:self.off_klass_mirror + 8])[0]
            sup_ptr = struct.unpack('<Q', k_hdr[self.off_klass_super:self.off_klass_super + 8])[0]
            sup_nm = self.read_symbol(self.r8(sup_ptr + self.off_klass_name)) if sup_ptr else ''
            ifaces_ptr = struct.unpack('<Q', k_hdr[self.off_ik_ifaces:self.off_ik_ifaces + 8])[0]
            ifaces = []
            if ifaces_ptr:
                if_cnt = self.r4(ifaces_ptr)
                if 0 < if_cnt <= 64:
                    raw_if = self.rpm(ifaces_ptr + 8, if_cnt * 8)
                    if len(raw_if) == if_cnt * 8:
                        for ip in struct.unpack(f'<{if_cnt}Q', raw_if):
                            inm = self.read_symbol(self.r8(ip + self.off_klass_name))
                            if inm:
                                ifaces.append(inm)
            jfc = struct.unpack('<H', k_hdr[self.off_ik_jfc:self.off_ik_jfc + 2])[0]
            marr = struct.unpack('<Q', k_hdr[self.off_ik_methods:self.off_ik_methods + 8])[0]
            farr = struct.unpack('<Q', k_hdr[self.off_ik_fields:self.off_ik_fields + 8])[0]
            ccp = ClassCP(self, k)
            self._cp_cache[nm] = ccp
            for idx in range(1, len(ccp.tags)):
                t = ccp.tags[idx]
                if t in (9, 10, 11):
                    ref = ccp.member_ref_from_cp(idx)
                    if ref and ref[0]:
                        owner, m_name, m_desc = ref
                        if t == 9:
                            self.cp_fields[owner].add((m_name, m_desc))
                        else:
                            self.cp_methods[owner].add((m_name, m_desc))
                            self.cp_method_callers[owner, m_name, m_desc].add(nm)
            fields = []
            if farr and jfc > 0:
                raw_f = self.rpm(farr + 4, jfc * 12)
                if len(raw_f) == jfc * 12:
                    u2s = struct.unpack(f'<{jfc * 6}H', raw_f)
                    for i in range(jfc):
                        f_acc, ni, si, _iv, lo, hi = u2s[i * 6:(i + 1) * 6]
                        off = (hi << 16 | lo) >> 2
                        fields.append({'name': ccp.utf8(ni), 'desc': ccp.utf8(si), 'acc': f_acc & 65535, 'static': bool(f_acc & 8), 'final': bool(f_acc & 16), 'offset': off})
            methods = []
            method_ptrs = {}
            if marr:
                mlen = self.r4(marr)
                if 0 < mlen <= 4000:
                    raw_m = self.rpm(marr + 8, mlen * 8)
                    if len(raw_m) == mlen * 8:
                        for mp in struct.unpack(f'<{mlen}Q', raw_m):
                            m_hdr = self.rpm(mp, 40)
                            if len(m_hdr) < 36:
                                continue
                            cm = struct.unpack('<Q', m_hdr[self.off_method_cm:self.off_method_cm + 8])[0]
                            m_acc = struct.unpack('<I', m_hdr[self.off_method_acc:self.off_method_acc + 4])[0] & 65535
                            cm_hdr = self.rpm(cm, self.sizeof_cm)
                            if len(cm_hdr) < 36:
                                continue
                            code_sz = struct.unpack('<H', cm_hdr[self.off_cm_code_sz:self.off_cm_code_sz + 2])[0]
                            ni = struct.unpack('<H', cm_hdr[self.off_cm_name_idx:self.off_cm_name_idx + 2])[0]
                            si = struct.unpack('<H', cm_hdr[self.off_cm_sig_idx:self.off_cm_sig_idx + 2])[0]
                            mn = ccp.utf8(ni)
                            ms = ccp.utf8(si)
                            first_op = self.r1(cm + self.sizeof_cm) if code_sz == 1 else -1
                            is_dummy_noop = code_sz == 1 and first_op == 177 and (ms == '()V') and (mn not in ('<init>', '<clinit>'))
                            method_ptrs[mn, ms] = mp
                            methods.append({'name': mn, 'desc': ms, 'acc': m_acc, 'static': bool(m_acc & 8), 'code_sz': code_sz, 'mp': mp, 'dummy_noop': is_dummy_noop})
            sym_ptr = struct.unpack('<Q', k_hdr[self.off_klass_name:self.off_klass_name + 8])[0] & ~3
            self.classes[nm] = {'klass': k, 'sym': sym_ptr, 'cp': ccp.cp, 'mirror': mirror, 'acc': acc, 'super': sup_nm, 'interfaces': ifaces, 'fields': fields, 'methods': methods, 'method_ptrs': method_ptrs}
            self.klass_to_name[k] = nm
            if mirror:
                self.mirror_to_name[mirror] = nm
            if sup_nm:
                self.children[sup_nm].append(nm)
            for ifc in ifaces:
                self.impls[ifc].append(nm)
        return len(self.classes)

    def get_cp(self, cls_name):
        if cls_name in self._cp_cache:
            return self._cp_cache[cls_name]
        info = self.classes.get(cls_name)
        if not info:
            return None
        ccp = ClassCP(self, info['klass'])
        self._cp_cache[cls_name] = ccp
        return ccp

    def cp_referenced_classes(self, cls_name):
        ccp = self.get_cp(cls_name)
        if not ccp:
            return set()
        out = set()
        for idx in range(1, len(ccp.tags)):
            if ccp.tags[idx] in (7, 100, 103, 104):
                cn = ccp.class_name(idx)
                if cn:
                    out.add(cn)
        return out

    def cp_int_constants(self, cls_name):
        ccp = self.get_cp(cls_name)
        if not ccp:
            return set()
        out = set()
        for idx in range(1, len(ccp.tags)):
            if ccp.tags[idx] == 3:
                out.add(int(ccp.const_val(idx)))
        return out

    def super_chain(self, cls_name):
        chain = []
        cur = cls_name
        while cur and cur in self.classes:
            chain.append(cur)
            cur = self.classes[cur]['super']
        return chain

    def disasm(self, cls_name, method_name, method_desc):
        key = (cls_name, method_name, method_desc)
        cached = self._disasm_cache.get(key)
        if cached is not None:
            return cached
        info = self.classes.get(cls_name)
        if not info:
            return []
        mp = info['method_ptrs'].get((method_name, method_desc))
        ccp = self.get_cp(cls_name)
        if not mp or not ccp:
            return []
        ops = self.disasm_mp(ccp, mp)
        self._disasm_cache[key] = ops
        return ops

    def disasm_mp(self, ccp, mp):
        cm = self.r8(mp + self.off_method_cm)
        code_sz = self.r2(cm + self.off_cm_code_sz)
        if code_sz == 0:
            return []
        code = self.rpm(cm + self.sizeof_cm, code_sz)
        ops = []
        i = 0
        n = len(code)
        while i < n:
            op = code[i]
            if op == 1:
                ops.append(('aconst_null',))
                i += 1
            elif 2 <= op <= 8:
                ops.append(('iconst', op - 3))
                i += 1
            elif op in (9, 10):
                ops.append(('lconst', op - 9))
                i += 1
            elif 11 <= op <= 13:
                ops.append(('fconst', float(op - 11)))
                i += 1
            elif op in (14, 15):
                ops.append(('dconst', float(op - 14)))
                i += 1
            elif op == 16 and i + 1 < n:
                ops.append(('bipush', struct.unpack('<b', code[i + 1:i + 2])[0]))
                i += 2
            elif op == 17 and i + 2 < n:
                ops.append(('sipush', struct.unpack('>h', code[i + 1:i + 3])[0]))
                i += 3
            elif op == 18 and i + 1 < n:
                ops.append(('ldc', ccp.const_val(code[i + 1])))
                i += 2
            elif op == 19 and i + 2 < n:
                ops.append(('ldc_w', ccp.const_val(struct.unpack('>H', code[i + 1:i + 3])[0])))
                i += 3
            elif op == 20 and i + 2 < n:
                ops.append(('ldc2_w', ccp.const_val(struct.unpack('>H', code[i + 1:i + 3])[0])))
                i += 3
            elif 21 <= op <= 25 and i + 1 < n:
                kind = ['iload', 'lload', 'fload', 'dload', 'aload'][op - 21]
                ops.append((kind, code[i + 1]))
                i += 2
            elif 26 <= op <= 29:
                ops.append(('iload', op - 26))
                i += 1
            elif 30 <= op <= 33:
                ops.append(('lload', op - 30))
                i += 1
            elif 34 <= op <= 37:
                ops.append(('fload', op - 34))
                i += 1
            elif 38 <= op <= 41:
                ops.append(('dload', op - 38))
                i += 1
            elif 42 <= op <= 45:
                ops.append(('aload', op - 42))
                i += 1
            elif 54 <= op <= 58 and i + 1 < n:
                kind = ['istore', 'lstore', 'fstore', 'dstore', 'astore'][op - 54]
                ops.append((kind, code[i + 1]))
                i += 2
            elif 59 <= op <= 62:
                ops.append(('istore', op - 59))
                i += 1
            elif 63 <= op <= 66:
                ops.append(('lstore', op - 63))
                i += 1
            elif 67 <= op <= 70:
                ops.append(('fstore', op - 67))
                i += 1
            elif 71 <= op <= 74:
                ops.append(('dstore', op - 71))
                i += 1
            elif 75 <= op <= 78:
                ops.append(('astore', op - 75))
                i += 1
            elif op == 132 and i + 2 < n:
                ops.append(('iinc', code[i + 1], struct.unpack('<b', code[i + 2:i + 3])[0]))
                i += 3
            elif 153 <= op <= 168 and i + 2 < n:
                ops.append(('branch', op, i + struct.unpack('>h', code[i + 1:i + 3])[0]))
                i += 3
            elif op == 169 and i + 1 < n:
                ops.append(('ret', code[i + 1]))
                i += 2
            elif op == 170:
                pad = 4 - (i + 1 & 3) & 3
                j = i + 1 + pad
                if j + 12 > n:
                    break
                low, high = struct.unpack('>ii', code[j + 4:j + 12])
                cnt = high - low + 1
                if cnt < 0 or j + 12 + cnt * 4 > n:
                    break
                ops.append(('tableswitch', low, high))
                i = j + 12 + cnt * 4
            elif op == 171:
                pad = 4 - (i + 1 & 3) & 3
                j = i + 1 + pad
                if j + 8 > n:
                    break
                npairs = struct.unpack('>i', code[j + 4:j + 8])[0]
                if npairs < 0 or j + 8 + npairs * 8 > n:
                    break
                ops.append(('lookupswitch', npairs))
                i = j + 8 + npairs * 8
            elif 172 <= op <= 177:
                rkind = ['ireturn', 'lreturn', 'freturn', 'dreturn', 'areturn', 'return'][op - 172]
                ops.append((rkind,))
                i += 1
            elif op in (178, 179, 180, 181) and i + 2 < n:
                oname = ['getstatic', 'putstatic', 'getfield', 'putfield'][op - 178]
                cidx = struct.unpack('<H', code[i + 1:i + 3])[0]
                ops.append((oname, ccp.member_ref_from_cache(cidx)))
                i += 3
            elif op in (182, 183, 184) and i + 2 < n:
                oname = ['invokevirtual', 'invokespecial', 'invokestatic'][op - 182]
                cidx = struct.unpack('<H', code[i + 1:i + 3])[0]
                ops.append((oname, ccp.member_ref_from_cache(cidx)))
                i += 3
            elif op == 185 and i + 4 < n:
                cidx = struct.unpack('<H', code[i + 1:i + 3])[0]
                ops.append(('invokeinterface', ccp.member_ref_from_cache(cidx)))
                i += 5
            elif op == 186 and i + 4 < n:
                ops.append(('invokedynamic',))
                i += 5
            elif op in (187, 189, 192, 193) and i + 2 < n:
                oname = {187: 'new', 189: 'anewarray', 192: 'checkcast', 193: 'instanceof'}[op]
                kidx = struct.unpack('>H', code[i + 1:i + 3])[0]
                ops.append((oname, ccp.class_name(kidx)))
                i += 3
            elif op == 188 and i + 1 < n:
                ops.append(('newarray', code[i + 1]))
                i += 2
            elif op == 196 and i + 1 < n:
                wop = code[i + 1]
                if wop == 132:
                    ops.append(('wide_iinc',))
                    i += 6
                else:
                    ops.append(('wide', wop))
                    i += 4
            elif op == 197 and i + 3 < n:
                ops.append(('multianewarray',))
                i += 4
            elif op in (198, 199) and i + 2 < n:
                ops.append(('ifnull' if op == 198 else 'ifnonnull', i + struct.unpack('>h', code[i + 1:i + 3])[0]))
                i += 3
            elif op in (200, 201) and i + 4 < n:
                ops.append(('goto_w',))
                i += 5
            elif 203 <= op <= 210 and i + 2 < n:
                cidx = struct.unpack('<H', code[i + 1:i + 3])[0]
                ops.append(('getfield', ccp.member_ref_from_cache(cidx)))
                i += 3
            elif 211 <= op <= 218 and i + 2 < n:
                cidx = struct.unpack('<H', code[i + 1:i + 3])[0]
                ops.append(('putfield', ccp.member_ref_from_cache(cidx)))
                i += 3
            elif op == 219:
                ops.append(('aload', 0))
                i += 1
            elif op in (220, 221, 222) and i + 3 < n:
                cidx = struct.unpack('<H', code[i + 2:i + 4])[0]
                ops.append(('aload', 0))
                ops.append(('getfield', ccp.member_ref_from_cache(cidx)))
                i += 4
            elif op == 223 and i + 1 < n:
                ops.append(('iload', code[i + 1]))
                i += 2
            elif op == 224 and i + 2 < n:
                ops.append(('iload', code[i + 1]))
                ops.append(('iload', code[i + 2]))
                i += 3
            elif op == 225 and i + 1 < n:
                ops.append(('iload', code[i + 1]))
                ops.append(('caload',))
                i += 2
            elif op == 226 and i + 2 < n:
                cidx = struct.unpack('<H', code[i + 1:i + 3])[0]
                ops.append(('invokevirtual', ccp.member_ref_from_cache(cidx)))
                i += 3
            elif op in (227, 228):
                pad = 4 - (i + 1 & 3) & 3
                j = i + 1 + pad
                if j + 8 > n:
                    break
                npairs = struct.unpack('>i', code[j + 4:j + 8])[0]
                if npairs < 0 or j + 8 + npairs * 8 > n:
                    break
                ops.append(('lookupswitch', npairs))
                i = j + 8 + npairs * 8
            elif op == 229 and i + 1 < n:
                ops.append(('aldc', ccp.resolved_ref_str(code[i + 1])))
                i += 2
            elif op == 230 and i + 2 < n:
                ridx = struct.unpack('<H', code[i + 1:i + 3])[0]
                ops.append(('aldc_w', ccp.resolved_ref_str(ridx)))
                i += 3
            elif op == 231:
                ops.append(('return',))
                i += 1
            else:
                ops.append((f'op_0x{op:02x}',))
                i += 1
        return ops
