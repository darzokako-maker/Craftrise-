import collections
import re
from jvm_reader import JVMProcess, parse_method_desc

def solve_classes(jvm):
    classes = jvm.classes
    children = jvm.children
    impls = jvm.impls
    R = {}

    def real_methods(cn):
        info = classes.get(cn)
        return [m for m in info['methods'] if not m['dummy_noop']] if info else []

    def inst_fields(cn):
        info = classes.get(cn)
        if not info:
            return []
        return [f for f in info['fields'] if not f['static'] and (not f['name'].startswith(('fake_', 'var_')))]

    def static_fields(cn):
        info = classes.get(cn)
        if not info:
            return []
        return [f for f in info['fields'] if f['static'] and (not f['name'].startswith(('fake_', 'var_')))]
    for k, v in classes.items():
        fnames = {f['name'] for f in v['fields']}
        mnames = {m['name'] for m in v['methods']}
        if {'allGames', 'swtype', 'displayname'} <= fnames:
            R['CRGameInfo'] = k
        ascii_m = [mn for mn in mnames if mn.isascii() and len(mn) >= 5 and (mn not in ('<init>', '<clinit>', 'values', 'valueOf', 'toString', 'equals', 'hashCode', 'clone'))]
        if {'OF_NAME', 'OF_RELEASE'} <= fnames or (('isShaders' in mnames or 'getGameSettings' in mnames) and len(ascii_m) >= 20):
            R['Config'] = k
        if ('shaderPackLoaded' in fnames or 'activeProgram' in fnames) or (sum((1 for f in v['fields'] if f['static'] and f['desc'] == 'Ljava/nio/IntBuffer;')) >= 3 and sum((1 for f in v['fields'] if f['static'] and f['desc'] == 'Ljava/nio/FloatBuffer;')) >= 2 and (len(v['methods']) >= 100)):
            R['Shaders'] = k
    for k, v in classes.items():
        if len(v['fields']) < 60 or len(v['methods']) < 80:
            continue
        self_desc = f'L{k};'
        for f in v['fields']:
            if f['static'] and f['desc'] == self_desc:
                oop = jvm.read_oop_field(v['mirror'], f['offset'])
                if oop and jvm.oop_class_name(oop) == k:
                    if any(('Logger' in x['desc'] for x in v['fields'])):
                        R['Minecraft'] = k
                        break
        if 'Minecraft' in R:
            break
    if 'Minecraft' not in R:
        raise RuntimeError("Anchor 'Minecraft' bulunamadi!")
    mc_cls = R['Minecraft']
    mc_fdescs = {f['desc'][1:-1] for f in inst_fields(mc_cls) if f['desc'].startswith('L') and f['desc'].endswith(';')}
    for fc in mc_fdescs:
        if fc not in classes:
            continue
        ft_counts = collections.Counter((f['desc'] for f in inst_fields(fc) if f['desc'].startswith('L')))
        for desc, cnt in ft_counts.items():
            if cnt >= 18 and any((f['desc'] == f'[{desc}' for f in inst_fields(fc))):
                R['GameSettings'] = fc
                R['KeyBinding'] = desc[1:-1]
                for sub in classes:
                    if sub.startswith(fc + '$') and classes[sub]['super'] == 'java/lang/Enum':
                        R['GameSettings$Options'] = sub
                        break
                break
        if 'GameSettings' in R:
            break
    for m in real_methods(mc_cls):
        pd = parse_method_desc(m['desc'])
        if pd and len(pd[0]) == 0 and pd[1].startswith('L'):
            ret_c = pd[1][1:-1]
            ch = jvm.super_chain(ret_c)
            if len(ch) == 5 and classes[ch[-1]]['super'] == 'java/lang/Object':
                nd = sum((1 for f in inst_fields(ch[-1]) if f['desc'] == 'D'))
                nf = sum((1 for f in inst_fields(ch[-1]) if f['desc'] == 'F'))
                if nd >= 9 and nf >= 6:
                    R['EntityPlayerSP'], R['AbstractClientPlayer'], R['EntityPlayer'], R['EntityLivingBase'], R['Entity'] = ch
                    break
    if 'Entity' not in R:
        for fc in mc_fdescs:
            ch = jvm.super_chain(fc)
            if len(ch) == 5 and classes[ch[-1]]['super'] == 'java/lang/Object':
                nd = sum((1 for f in inst_fields(ch[-1]) if f['desc'] == 'D'))
                if nd >= 9:
                    R['EntityPlayerSP'], R['AbstractClientPlayer'], R['EntityPlayer'], R['EntityLivingBase'], R['Entity'] = ch
                    break
    for f in inst_fields(R['Entity']):
        if f['desc'].startswith('L'):
            wc = f['desc'][1:-1]
            if wc in classes and len(classes[wc]['methods']) >= 70:
                n_lists = sum((1 for wf in inst_fields(wc) if wf['desc'] == 'Ljava/util/List;'))
                if n_lists >= 4:
                    R['World'] = wc
                    break
    if 'World' in R:
        for sub in children.get(R['World'], []):
            if sub in mc_fdescs:
                R['WorldClient'] = sub
                break
    for fc in mc_fdescs:
        if fc in classes:
            if any((m['desc'] == '(Ljava/lang/String;FFIZ)I' for m in classes[fc]['methods'])):
                R['FontRenderer'] = fc
                break
    for k, v in classes.items():
        if v['super'] != 'java/lang/Enum':
            continue
        ec = set(jvm.enum_constant_names(k))
        if {'DOWN', 'UP', 'NORTH', 'SOUTH', 'WEST', 'EAST'} <= ec:
            R['EnumFacing'] = k
        elif ec == {'SERVERBOUND', 'CLIENTBOUND'}:
            R['EnumPacketDirection'] = k
        elif {'HANDSHAKING', 'PLAY', 'STATUS', 'LOGIN'} <= ec:
            R['EnumConnectionState'] = k
        elif {'NONE', 'EAT', 'DRINK', 'BLOCK', 'BOW'} <= ec:
            R['EnumAction'] = k
        elif {'MONSTER', 'CREATURE', 'AMBIENT', 'WATER_CREATURE'} <= ec:
            R['EnumCreatureType'] = k
    if 'EnumFacing' in R:
        ef_cls = R['EnumFacing']
        for k, v in classes.items():
            if k.startswith(ef_cls + '$') and v['super'] == 'java/lang/Enum':
                ec = set(jvm.enum_constant_names(k))
                if ec == {'X', 'Y', 'Z'}:
                    R['EnumAxis'] = k
                elif ec == {'POSITIVE', 'NEGATIVE'}:
                    R['EnumAxisDirection'] = k
    for k, v in classes.items():
        if v['super'] != 'java/lang/Object':
            continue
        f_inst = inst_fields(k)
        ctors = {m['desc'] for m in v['methods'] if m['name'] == '<init>'}
        mdescs = {m['desc'] for m in v['methods']}
        d_cnt = sum((1 for f in f_inst if f['desc'] == 'D'))
        i_cnt = sum((1 for f in f_inst if f['desc'] == 'I'))
        if d_cnt == 3 and '(DDD)V' in ctors and (f'(DDD)L{k};' in mdescs) and (f'(L{k};)D' in mdescs):
            R['Vec3'] = k
        elif d_cnt == 6 and '(DDDDDD)V' in ctors and (f'(DDD)L{k};' in mdescs):
            R['AxisAlignedBB'] = k
        elif 'java/lang/Comparable' in v['interfaces'] and i_cnt >= 3 and ('(III)V' in ctors) and ('(DDD)V' in ctors) and children.get(k):
            for sub in children[k]:
                sub_ctors = {m['desc'] for m in classes[sub]['methods'] if m['name'] == '<init>'}
                if f"(L{R['Entity']};)V" in sub_ctors:
                    R['Vec3i'] = k
                    R['BlockPos'] = sub
                    break
    for m in real_methods(R['Entity']):
        pd = parse_method_desc(m['desc'])
        if pd and pd[0] == ['D', 'F'] and pd[1].startswith('L'):
            mop_c = pd[1][1:-1]
            if mop_c in classes and mop_c != R.get('Vec3'):
                R['MovingObjectPosition'] = mop_c
                for f in inst_fields(mop_c):
                    if f['desc'].startswith('L'):
                        ec = f['desc'][1:-1]
                        if ec in classes and classes[ec]['super'] == 'java/lang/Enum' and (ec != R.get('EnumFacing')):
                            R['MovingObjectType'] = ec
                break
    if 'World' in R and 'BlockPos' in R:
        for m in real_methods(R['World']):
            pd = parse_method_desc(m['desc'])
            if pd and pd[0] == [f"L{R['BlockPos']};"] and pd[1].startswith('L'):
                ibs_c = pd[1][1:-1]
                if ibs_c in classes and classes[ibs_c]['acc'] & 512:
                    for im in classes[ibs_c]['methods']:
                        ipd = parse_method_desc(im['desc'])
                        if ipd and len(ipd[0]) == 0 and ipd[1].startswith('L'):
                            bc = ipd[1][1:-1]
                            if bc in classes and len(children.get(bc, [])) >= 40:
                                R['IBlockState'] = ibs_c
                                R['Block'] = bc
                                break
                if 'IBlockState' in R:
                    break
    if 'Block' in R:
        blk_desc = f"L{R['Block']};"
        for k, v in classes.items():
            if sum((1 for f in v['fields'] if f['static'] and f['desc'] == blk_desc)) >= 100:
                R['Blocks'] = k
                break
    wrapper_counts = collections.Counter((f['desc'][1:-1] for cls_k in (R['Entity'], R['EntityLivingBase']) for f in inst_fields(cls_k) if f['desc'].startswith('L')))
    for wc, cnt in wrapper_counts.items():
        if cnt < 3 or wc not in classes or wc in R.values():
            continue
        cm = classes[wc]['methods']
        ctors = {m['desc'] for m in cm if m['name'] == '<init>'}
        mdescs = {m['desc'] for m in cm if not m['dummy_noop']}
        if '(D)V' in ctors and '()D' in mdescs:
            R['MotionContainer'] = wc
        elif '(F)V' in ctors and '()F' in mdescs:
            R['FloatContainer'] = wc
        elif '()Z' in mdescs and ('(Z)V' in mdescs or any((d.startswith('(Z') or d.endswith('Z)V') for d in ctors))):
            R['BooleanContainer'] = wc
    for fc in mc_fdescs:
        if fc not in classes or fc in R.values() or classes[fc]['super'] != 'java/lang/Object':
            continue
        ctors = [m['desc'] for m in classes[fc]['methods'] if m['name'] == '<init>']
        if ctors == ['(F)V']:
            for sf in static_fields(fc):
                if sf['desc'].startswith('L'):
                    tc = sf['desc'][1:-1]
                    if tc in classes and any((m['desc'] == '()D' for m in classes[tc]['methods'])) and any((m['desc'] == '(D)V' for m in classes[tc]['methods'])):
                        R['Timer'] = fc
                        R['TimerContainer'] = tc
                        break
            if 'Timer' in R:
                break
    ep_cls = R['EntityPlayer']
    ep_f_cnt = collections.Counter((f['desc'][1:-1] for f in inst_fields(ep_cls) if f['desc'].startswith('L')))
    for fc, cnt in ep_f_cnt.items():
        if fc not in classes:
            continue
        if cnt == 2 and any((f['desc'] == 'Ljava/util/List;' for f in inst_fields(fc))):
            R['Container'] = fc
        arr_cnt = collections.Counter((f['desc'] for f in inst_fields(fc) if f['desc'].startswith('[L')))
        for adesc, acnt in arr_cnt.items():
            if acnt == 2 and any((f['desc'] == f'L{ep_cls};' for f in inst_fields(fc))):
                R['InventoryPlayer'] = fc
                R['ItemStack'] = adesc[2:-1]
    if 'ItemStack' in R:
        is_cls = R['ItemStack']
        for m in classes[is_cls]['methods']:
            if m['name'] == '<init>':
                pd = parse_method_desc(m['desc'])
                if pd and len(pd[0]) == 3 and (pd[0][1:] == ['I', 'I']) and pd[0][0].startswith('L'):
                    ic = pd[0][0][1:-1]
                    if ic in classes and ic != R.get('Block') and (len(children.get(ic, [])) >= 25):
                        R['Item'] = ic
                        break
        if 'Item' in R:
            item_family = {R['Item']} | set(children.get(R['Item'], []))
            for k, v in classes.items():
                n_it = sum((1 for f in v['fields'] if f['static'] and f['desc'].startswith('L') and (f['desc'][1:-1] in item_family)))
                if n_it >= 100:
                    R['Items'] = k
                    break
        if 'Container' in R:
            for m in real_methods(R['Container']):
                pd = parse_method_desc(m['desc'])
                if pd and pd[0] == ['I'] and pd[1].startswith('L'):
                    sc = pd[1][1:-1]
                    if sc in classes and sc != is_cls and any((m2['desc'] == f'()L{is_cls};' for m2 in classes[sc]['methods'])):
                        R['Slot'] = sc
                        break
        eh_sig = f'(IL{is_cls};)I'
        for owner, mset in jvm.cp_methods.items():
            if any((md == eh_sig for _, md in mset)):
                if any((md.startswith(f'([L{is_cls};') or md.startswith(f"(L{R['EntityLivingBase']};") for _, md in mset)):
                    R['EnchantmentHelper'] = owner
                    break
    for m in real_methods(ep_cls):
        pd = parse_method_desc(m['desc'])
        if pd and pd[0] == ['Z'] and pd[1].startswith('L'):
            ei_c = pd[1][1:-1]
            if ei_c.startswith(('craftrise/', 'crsecond/')):
                R['EntityItem'] = ei_c
                break
    for f in inst_fields(ep_cls):
        if f['desc'].startswith('L'):
            fc = f['desc'][1:-1]
            if fc in classes and classes[fc]['super'] == R['Entity'] and (fc != R.get('EntityItem')):
                R['EntityFishHook'] = fc
                break
    if 'ItemStack' in R:
        wc_desc = f"(IIIIL{ep_cls};)L{R['ItemStack']};"
        for fc in mc_fdescs:
            if fc in classes and any((m['desc'] == wc_desc for m in classes[fc]['methods'])):
                R['PlayerControllerMP'] = fc
                break
    for k, v in classes.items():
        if v['super'] == 'io/netty/buffer/ByteBuf':
            R['PacketBuffer'] = k
        if v['acc'] & 512 and len(impls.get(k, [])) >= 50:
            non_clinit = [m for m in v['methods'] if m['name'] != '<clinit>']
            if len(non_clinit) <= 5:
                R['Packet'] = k
    if 'Packet' in R:
        pkt_cls = R['Packet']
        for k, v in classes.items():
            if sum((1 for m in v['methods'] if m['desc'] == f'()L{pkt_cls};')) >= 40:
                R['PacketRegisterer'] = k
                break
        for k, v in classes.items():
            if any((f['desc'] == 'Lio/netty/channel/Channel;' for f in inst_fields(k))):
                if any((m['desc'].startswith(f'(L{pkt_cls};') for m in v['methods'])):
                    R['NetworkManager'] = k
                    break
        for f in inst_fields(R['EntityPlayerSP']):
            if f['desc'].startswith('L'):
                fc = f['desc'][1:-1]
                if fc in classes and any((m['desc'] == f'(L{pkt_cls};)V' for m in classes[fc]['methods'])):
                    if 'NetworkManager' not in R or any((nf['desc'] == f"L{R['NetworkManager']};" for nf in inst_fields(fc))):
                        R['NetHandlerPlayClient'] = fc
                        cr_ifs = [i for i in classes[fc]['interfaces'] if i.startswith(('craftrise/', 'crsecond/'))]
                        if cr_ifs:
                            R['INetHandlerPlayClient'] = cr_ifs[0]
                        break
    for k, v in classes.items():
        if v['super'] != 'java/lang/Object':
            continue
        fdescs = [f['desc'] for f in inst_fields(k)]
        ctors = {m['desc'] for m in v['methods'] if m['name'] == '<init>'}
        mdescs = {m['desc'] for m in v['methods']}
        if 'Ljava/util/UUID;' in fdescs and 'Ljava/lang/String;' in fdescs and ('(Ljava/util/UUID;Ljava/lang/String;)V' in ctors) and ('()Ljava/util/UUID;' in mdescs) and ('()Ljava/lang/String;' in mdescs):
            R['GameProfile'] = k
            break
    acp_cls = R['AbstractClientPlayer']
    if 'GameProfile' in R:
        gp_ret = f"()L{R['GameProfile']};"
        for f in inst_fields(acp_cls):
            if f['desc'].startswith('L'):
                fc = f['desc'][1:-1]
                has_gp = fc in classes and any((m['desc'] == gp_ret for m in classes[fc]['methods'])) or any((md == gp_ret for _, md in jvm.cp_methods.get(fc, set())))
                if has_gp:
                    R['NetworkPlayerInfo'] = fc
                    break
    for m in real_methods(acp_cls):
        if m['desc'].startswith('()L'):
            rc = m['desc'][3:-1]
            if rc in classes and classes[rc]['super'] == 'java/lang/Object' and (rc != R.get('GameProfile')):
                ctors = {x['desc'] for x in classes[rc]['methods'] if x['name'] == '<init>'}
                s_cnt = sum((1 for f in inst_fields(rc) if f['desc'] == 'Ljava/lang/String;'))
                if s_cnt >= 2 and '(Ljava/lang/String;)V' in ctors and ('(Ljava/lang/String;Ljava/lang/String;)V' in ctors):
                    R['ResourceLocation'] = rc
                    break
    ent_ret_ifaces = {m['desc'][3:-1] for m in real_methods(R['Entity']) if m['desc'].startswith('()L') and m['desc'][3:-1] in classes and classes[m['desc'][3:-1]]['acc'] & 512}
    for icc in ent_ret_ifaces:
        if any((m['desc'] == f'(L{icc};)V' for m in real_methods(R['Entity']) + real_methods(R['EntityPlayerSP']))):
            R['IChatComponent'] = icc
            break
    if 'IChatComponent' in R:
        icc = R['IChatComponent']
        for m in classes[icc]['methods']:
            if m['desc'].startswith('()L'):
                rt = m['desc'][3:-1]
                if rt in classes and rt != icc and (not classes[rt]['acc'] & 512):
                    R['ChatStyle'] = rt
                    break
        for sc in impls.get(icc, []):
            text_cands = []
            for sub in children.get(sc, []):
                ctors = [m['desc'] for m in classes[sub]['methods'] if m['name'] == '<init>']
                str_fields = [f['name'] for f in inst_fields(sub) if f['desc'] == 'Ljava/lang/String;']
                if '(Ljava/lang/String;)V' in ctors and len(ctors) == 1 and (len(str_fields) == 1):
                    text_cands.append((sub, str_fields[0]))
            if text_cands:
                R['ChatComponentStyle'] = sc
                chosen = next((sub for sub, fn in text_cands if fn == 'text'), next((sub for sub, fn in text_cands if fn != 'selector'), text_cands[0][0]))
                R['ChatComponentText'] = chosen
                break
    for fc in mc_fdescs:
        if fc in classes and fc not in R.values():
            vf = inst_fields(fc)
            nd = sum((1 for f in vf if f['desc'] == 'D'))
            nf = sum((1 for f in vf if f['desc'] == 'F'))
            if nd >= 6 and nf >= 2 and any((f['desc'] == 'Ljava/util/Map;' for f in vf)) and any((f['desc'] == f"L{R['Entity']};" for f in vf)):
                R['RenderManager'] = fc
                break
    if 'World' in R and 'Block' in R:
        for m in real_methods(R['World']):
            pd = parse_method_desc(m['desc'])
            if pd and pd[0] == ['I', 'I'] and pd[1].startswith('L'):
                cc = pd[1][1:-1]
                if cc in classes and any((m2['desc'] == f"(III)L{R['Block']};" for m2 in classes[cc]['methods'])):
                    R['Chunk'] = cc
                    break
    if 'EnumConnectionState' in R:
        ecs = R['EnumConnectionState']
        cb_pkts = []
        sb_pkts = []
        for sub in children.get(ecs, []):
            for m in classes[sub]['methods']:
                if m['name'] == '<init>':
                    ops = jvm.disasm(sub, '<init>', m['desc'])
                    ldcs = [str(op[1])[6:-1] for op in ops if op[0] in ('ldc', 'ldc_w') and str(op[1]).startswith('Class<')]
                    if len(ldcs) == 1:
                        R['C00Handshake'] = ldcs[0]
                    elif len(ldcs) >= 60:
                        cur_dir = None
                        for op in ops:
                            if op[0] == 'getstatic' and op[1]:
                                cur_dir = op[1][1]
                            elif op[0] in ('ldc', 'ldc_w') and str(op[1]).startswith('Class<'):
                                pcls = str(op[1])[6:-1]
                                if cur_dir == 'CLIENTBOUND':
                                    cb_pkts.append(pcls)
                                elif cur_dir == 'SERVERBOUND':
                                    sb_pkts.append(pcls)
        if cb_pkts and sb_pkts:
            play_pkts = ['C00PacketKeepAlive', 'C01PacketChatMessage', 'C02PacketUseEntity', 'C03PacketPlayer', 'C04PacketPlayerPosition', 'C05PacketPlayerLook', 'C06PacketPlayerPosLook', 'C07PacketPlayerDigging', 'C08PacketPlayerBlockPlacement', 'C09PacketHeldItemChange', 'C0APacketAnimation', 'C0BPacketEntityAction', 'C0CPacketInput', 'C0DPacketCloseWindow', 'C0EPacketClickWindow', 'C0FPacketConfirmTransaction', 'C10PacketCreativeInventoryAction', 'C11PacketEnchantItem', 'C12PacketUpdateSign', 'C13PacketPlayerAbilities', 'C14PacketTabComplete', 'C15PacketClientSettings', 'C16PacketClientStatus', 'C17PacketCustomPayload', 'C18PacketSpectate', 'C19PacketResourcePackStatus', 'S00PacketKeepAlive', 'S01PacketJoinGame', 'S02PacketChat', 'S03PacketTimeUpdate', 'S04PacketEntityEquipment', 'S05PacketSpawnPosition', 'S06PacketUpdateHealth', 'S07PacketRespawn', 'S08PacketPlayerPosLook', 'S09PacketHeldItemChange', 'S0APacketUseBed', 'S0BPacketAnimation', 'S0CPacketSpawnPlayer', 'S0DPacketCollectItem', 'S0EPacketSpawnObject', 'S0FPacketSpawnMob', 'S10PacketSpawnPainting', 'S11PacketSpawnExperienceOrb', 'S12PacketEntityVelocity', 'S13PacketDestroyEntities', 'S14PacketEntity', 'S15PacketEntityRelMove', 'S16PacketEntityLook', 'S17PacketEntityLookMove', 'S18PacketEntityTeleport', 'S19PacketEntityHeadLook', 'S19PacketEntityStatus', 'S1BPacketEntityAttach', 'S1CPacketEntityMetadata', 'S1DPacketEntityEffect', 'S1EPacketRemoveEntityEffect', 'S1FPacketSetExperience', 'S20PacketEntityProperties', 'S21PacketChunkData', 'S22PacketMultiBlockChange', 'S23PacketBlockChange', 'S24PacketBlockAction', 'S25PacketBlockBreakAnim', 'S26PacketMapChunkBulk', 'S27PacketExplosion', 'S28PacketEffect', 'S29PacketSoundEffect', 'S2APacketParticles', 'S2BPacketChangeGameState', 'S2CPacketSpawnGlobalEntity', 'S2DPacketOpenWindow', 'S2EPacketCloseWindow', 'S2FPacketSetSlot', 'S30PacketWindowItems', 'S31PacketWindowProperty', 'S32PacketConfirmTransaction', 'S33PacketUpdateSign', 'S34PacketMaps', 'S35PacketUpdateTileEntity', 'S36PacketSignEditorOpen', 'S37PacketStatistics', 'S38PacketPlayerListItem', 'S39PacketPlayerAbilities', 'S3APacketTabComplete', 'S3BPacketScoreboardObjective', 'S3CPacketUpdateScore', 'S3DPacketDisplayScoreboard', 'S3EPacketTeams', 'S3FPacketCustomPayload', 'S40PacketDisconnect', 'S41PacketServerDifficulty', 'S42PacketCombatEvent', 'S43PacketCamera', 'S44PacketWorldBorder', 'S45PacketTitle', 'S46PacketSetCompressionLevel', 'S47PacketPlayerListHeaderFooter', 'S48PacketResourcePackSend', 'S49PacketUpdateEntityNBT']
            for cname in play_pkts:
                m_s = re.match('^S([0-9A-F]{2})Packet', cname)
                if m_s:
                    idx = int(m_s.group(1), 16)
                    if cname == 'S19PacketEntityHeadLook' and 25 < len(cb_pkts):
                        R[cname] = cb_pkts[25]
                    elif cname == 'S19PacketEntityStatus' and 26 < len(cb_pkts):
                        R[cname] = cb_pkts[26]
                    elif idx == 80 and 74 < len(cb_pkts):
                        R[cname] = cb_pkts[74]
                    elif idx < len(cb_pkts):
                        R[cname] = cb_pkts[idx]
                m_c = re.match('^C([0-9A-F]{2})Packet', cname)
                if m_c and cname not in R:
                    idx = int(m_c.group(1), 16)
                    if idx <= 25 and idx < len(sb_pkts):
                        R[cname] = sb_pkts[idx]
            if len(cb_pkts) > 74:
                R['S50PacketRiseKeepAlive'] = cb_pkts[74]
            if len(cb_pkts) > 23:
                s14_inners = [k for k in classes if k.startswith(cb_pkts[20] + '$') and k not in (cb_pkts[21], cb_pkts[22], cb_pkts[23])]
                if s14_inners:
                    R['S14PacketEntity_Inner'] = s14_inners[0]
            for idx_hex, enum_key in ((2, 'C02PacketUseEntityAction'), (7, 'C07PacketPlayerDigging_Action'), (11, 'C0BPacketEntityAction_Action'), (22, 'C16PacketClientStatus_EnumState')):
                if idx_hex < len(sb_pkts):
                    p_cls = sb_pkts[idx_hex]
                    inners = [k for k in classes if k.startswith(p_cls + '$') and classes[k]['super'] == 'java/lang/Enum']
                    if inners:
                        R[enum_key] = inners[0]
            if len(sb_pkts) > 1 and sb_pkts[1] in classes and ('Packet' in R):
                pkt_base_args = {pd0[0][0][1:-1] for pm in classes[R['Packet']]['methods'] if (pd0 := parse_method_desc(pm['desc'])) and len(pd0[0]) == 1 and pd0[0][0].startswith('L')}
                for m in classes[sb_pkts[1]]['methods']:
                    if m['name'] == '<init>':
                        continue
                    pd = parse_method_desc(m['desc'])
                    if pd and len(pd[0]) == 1 and (pd[1] == 'V') and pd[0][0].startswith('L'):
                        arg_c = pd[0][0][1:-1]
                        if arg_c not in pkt_base_args and arg_c.startswith(('craftrise/', 'crsecond/')):
                            R['INetHandlerPlayServer'] = arg_c
                            break
            cr_sb = [p for p in sb_pkts[26:] if p.startswith('crsecond/') and p in classes]
            for p in cr_sb:
                fdescs = [f['desc'] for f in inst_fields(p)]
                if '[B' in fdescs and ('Ljava/util/UUID;' in fdescs or 'I' in fdescs or fdescs.count('Z') >= 1):
                    pass
            if len(cr_sb) >= 2:
                R['C20PacketRiseVerify'] = cr_sb[0]
                R['C21PacketRiseVoice'] = cr_sb[1]
    for k, v in classes.items():
        if any((f['static'] and f['desc'] == f'L{k};' for f in v['fields'])):
            vf = inst_fields(k)
            sf = static_fields(k)
            if any((f['desc'] == 'Ljava/util/Map;' for f in vf)) and any((f['desc'] == f"L{R.get('FontRenderer', '')};" for f in vf)) and (sum((1 for f in sf if f['desc'] == 'D')) >= 3):
                R['TileEntityRendererDispatcher'] = k
                for m in real_methods(k):
                    pd = parse_method_desc(m['desc'])
                    if pd and len(pd[0]) == 6 and (pd[0][1:] == ['D', 'D', 'D', 'F', 'I']) and pd[0][0].startswith('L'):
                        R['TileEntity'] = pd[0][0][1:-1]
                        break
                break
    if 'TileEntity' in R and R['TileEntity'] in classes:
        te_cls = R['TileEntity']
        for f in inst_fields(te_cls):
            if f['desc'].startswith('L'):
                fc = f['desc'][1:-1]
                if fc in classes and classes[fc]['super'] == 'java/lang/Enum' and (fc not in R.values()):
                    R['TileEntityType'] = fc
                    break
        te_mirror = classes[te_cls]['mirror']
        te_map = {}
        for f in static_fields(te_cls):
            if f['desc'] == 'Ljava/util/Map;':
                m = jvm.read_hashmap_str_to_class(jvm.read_oop_field(te_mirror, f['offset']))
                if len(m) > len(te_map):
                    te_map = m
        TE_KEY_TO_CLS = {'Furnace': 'TileEntityFurnace', 'Chest': 'TileEntityChest', 'LargeChest': 'TileEntityLargeChest', 'EnderChest': 'TileEntityEnderChest', 'RecordPlayer': 'TileEntityJukebox', 'Trap': 'TileEntityDispenser', 'Dropper': 'TileEntityDropper', 'Sign': 'TileEntitySign', 'MobSpawner': 'TileEntityMobSpawner', 'Music': 'TileEntityNote', 'Piston': 'TileEntityPiston', 'Cauldron': 'TileEntityBrewingStand', 'EnchantTable': 'TileEntityEnchantmentTable', 'Airportal': 'TileEntityEndPortal', 'Control': 'TileEntityCommandBlock', 'Beacon': 'TileEntityBeacon', 'Skull': 'TileEntitySkull', 'DLDetector': 'TileEntityDaylightDetector', 'Hopper': 'TileEntityHopper', 'Comparator': 'TileEntityComparator', 'FlowerPot': 'TileEntityFlowerPot', 'Banner': 'TileEntityBanner', 'Bed': 'TileEntityBed'}
        for tk, tcls in te_map.items():
            if tk in TE_KEY_TO_CLS:
                R[TE_KEY_TO_CLS[tk]] = tcls
    for k, v in classes.items():
        map_sfs = [f for f in static_fields(k) if f['desc'] == 'Ljava/util/Map;']
        if len(map_sfs) >= 3:
            best_m = {}
            for mf in map_sfs:
                m = jvm.read_hashmap_str_to_class(jvm.read_oop_field(v['mirror'], mf['offset']))
                if len(m) > len(best_m):
                    best_m = m
            if 'Creeper' in best_m and 'Zombie' in best_m:
                R['EntityList'] = k
                ENT_KEY_TO_CLS = {'Item': 'EntityItem', 'XPOrb': 'EntityXPOrb', 'AreaEffectCloud': 'EntityAreaEffectCloud', 'ThrownEgg': 'EntityEgg', 'LeashKnot': 'EntityLeashKnot', 'Painting': 'EntityPainting', 'Arrow': 'EntityArrow', 'Snowball': 'EntitySnowball', 'Fireball': 'EntityLargeFireball', 'SmallFireball': 'EntitySmallFireball', 'ThrownEnderpearl': 'EntityEnderPearl', 'EyeOfEnderSignal': 'EntityEnderEye', 'ThrownPotion': 'EntityPotion', 'ThrownExpBottle': 'EntityExpBottle', 'ItemFrame': 'EntityItemFrame', 'WitherSkull': 'EntityWitherSkull', 'PrimedTnt': 'EntityTNTPrimed', 'FallingSand': 'EntityFallingBlock', 'FireworksRocketEntity': 'EntityFireworkRocket', 'ArmorStand': 'EntityArmorStand', 'Boat': 'EntityBoat', 'MinecartRideable': 'EntityMinecartEmpty', 'MinecartChest': 'EntityMinecartChest', 'MinecartFurnace': 'EntityMinecartFurnace', 'MinecartTNT': 'EntityMinecartTNT', 'MinecartHopper': 'EntityMinecartHopper', 'MinecartSpawner': 'EntityMinecartMobSpawner', 'MinecartCommandBlock': 'EntityMinecartCommandBlock', 'Mob': 'EntityLiving', 'Monster': 'EntityMob', 'Creeper': 'EntityCreeper', 'Skeleton': 'EntitySkeleton', 'Spider': 'EntitySpider', 'Giant': 'EntityGiantZombie', 'Zombie': 'EntityZombie', 'Slime': 'EntitySlime', 'Ghast': 'EntityGhast', 'PigZombie': 'EntityPigZombie', 'Enderman': 'EntityEnderman', 'CaveSpider': 'EntityCaveSpider', 'Silverfish': 'EntitySilverfish', 'Blaze': 'EntityBlaze', 'LavaSlime': 'EntityMagmaCube', 'EnderDragon': 'EntityDragon', 'WitherBoss': 'EntityWither', 'Bat': 'EntityBat', 'Witch': 'EntityWitch', 'Endermite': 'EntityEndermite', 'Guardian': 'EntityGuardian', 'Pig': 'EntityPig', 'Sheep': 'EntitySheep', 'Cow': 'EntityCow', 'Chicken': 'EntityChicken', 'Squid': 'EntitySquid', 'Wolf': 'EntityWolf', 'MushroomCow': 'EntityMooshroom', 'SnowMan': 'EntitySnowman', 'Ozelot': 'EntityOcelot', 'VillagerGolem': 'EntityIronGolem', 'EntityHorse': 'EntityHorse', 'Rabbit': 'EntityRabbit', 'Villager': 'EntityVillager', 'EnderCrystal': 'EntityEnderCrystal'}
                for ek, ecls in best_m.items():
                    if ek in ENT_KEY_TO_CLS:
                        R[ENT_KEY_TO_CLS[ek]] = ecls
                break
    if 'EntitySnowball' in R and R['EntitySnowball'] in classes:
        R['EntityThrowable'] = classes[R['EntitySnowball']]['super']
    if 'EntityLargeFireball' in R and R['EntityLargeFireball'] in classes:
        R['EntityFireball'] = classes[R['EntityLargeFireball']]['super']
    if 'EntitySquid' in R and R['EntitySquid'] in classes:
        R['EntityWaterMob'] = classes[R['EntitySquid']]['super']
    acp_subs = [k for k in children.get(acp_cls, []) if k != R['EntityPlayerSP']]
    if len(acp_subs) == 1:
        R['EntityOtherPlayerMP'] = acp_subs[0]
    if 'EntityDragon' in R and R['EntityDragon'] in classes:
        for f in inst_fields(R['EntityDragon']):
            if f['desc'].startswith('[L') and f['desc'][2:-1] != R['Entity']:
                R['EntityDragonPart'] = f['desc'][2:-1]
                break
    if 'EntityZombie' in R and R['EntityZombie'] in classes:
        z_sup = classes[R['EntityZombie']]['super']
        R['EntityMob'] = z_sup
        if z_sup in classes:
            for ifc in classes[z_sup]['interfaces']:
                if ifc.startswith(('craftrise/', 'crsecond/')):
                    R['EntityMonster'] = ifc
                    break
    for k, v in classes.items():
        arr_f = [f for f in static_fields(k) if f['desc'] == f'[L{k};']
        if not arr_f:
            continue
        arr_oop = jvm.read_oop_field(v['mirror'], arr_f[0]['offset'])
        if arr_oop and jvm.r4(arr_oop + 12) == 256:
            R['BiomeGenBase'] = k
            str_f = [f for f in inst_fields(k) if f['desc'] == 'Ljava/lang/String;']
            BIOME_NAME_MAP = {'Ocean': 'BiomeGenOcean', 'Plains': 'BiomeGenPlains', 'Desert': 'BiomeGenDesert', 'Extreme Hills': 'BiomeGenHills', 'Forest': 'BiomeGenForest', 'Taiga': 'BiomeGenTaiga', 'Swampland': 'BiomeGenSwamp', 'River': 'BiomeGenRiver', 'Hell': 'BiomeGenHell', 'The End': 'BiomeGenEnd', 'Ice Plains': 'BiomeGenSnow', 'MushroomIsland': 'BiomeGenMushroomIsland', 'Beach': 'BiomeGenBeach', 'Jungle': 'BiomeGenJungle', 'Stone Beach': 'BiomeGenStoneBeach', 'Savanna': 'BiomeGenSavanna', 'Mesa': 'BiomeGenMesa'}
            biome_subclasses_seen = set()
            for sf in static_fields(k):
                if sf['desc'] == f'L{k};':
                    boop = jvm.read_oop_field(v['mirror'], sf['offset'])
                    bcls = jvm.oop_class_name(boop)
                    bname = jvm.read_jstring(jvm.read_oop_field(boop, str_f[0]['offset'])) if boop and str_f else ''
                    if bname in BIOME_NAME_MAP and bcls:
                        R[BIOME_NAME_MAP[bname]] = bcls
                        biome_subclasses_seen.add(bcls)
            for sub in children.get(k, []):
                if sub not in biome_subclasses_seen:
                    if any((f['desc'] == f'L{k};' for f in inst_fields(sub))):
                        R['BiomeGenMutated'] = sub
            for inr in classes:
                if inr.startswith(k + '$'):
                    if classes[inr]['super'] == 'java/lang/Enum':
                        R['BiomeGenBase_TempCategory'] = inr
                    elif classes[inr]['super'] == 'java/lang/Object':
                        R['BiomeGenBase_Height'] = inr
                    else:
                        R['BiomeGenBase_SpawnListEntry'] = inr
                        R['WeightedRandom_Item'] = classes[inr]['super']
            tree_cands = []
            for bf in inst_fields(k):
                if bf['desc'].startswith('L'):
                    bfc = bf['desc'][1:-1]
                    if bfc in classes and bfc not in R.values():
                        if classes[bfc]['super'] == 'java/lang/Object' and len(inst_fields(bfc)) >= 20:
                            R['BiomeDecorator'] = bfc
                        elif classes[bfc]['super'] != 'java/lang/Object':
                            tree_cands.append(bfc)
            for tc in set(tree_cands):
                fds = [f['desc'] for f in inst_fields(tc)]
                if fds.count('D') >= 3:
                    R['WorldGenBigTree'] = tc
                    R['WorldGenAbstractTree'] = classes[tc]['super']
                elif fds.count(f"L{R.get('IBlockState', '')};") >= 2 or ('I' in fds and 'Z' in fds):
                    R['WorldGenTrees'] = tc
                    R['WorldGenAbstractTree'] = classes[tc]['super']
                else:
                    R['WorldGenSwamp'] = tc
            break
    if 'Blocks' in R and 'Block' in R:
        blk_cls = R['Block']
        blocks_cls = R['Blocks']
        blocks_mirror = classes[blocks_cls]['mirror']
        blk_sfields = [(f['name'], f['offset']) for f in inst_fields(blk_cls) if f['desc'] == 'Ljava/lang/String;']
        blk_by_unloc = {}
        blk_all_runtime = {}
        seen_logs = []
        seen_leaves = []

        def is_double_slab(cn):
            if cn not in classes:
                return None
            for m in real_methods(cn):
                if not m['static'] and m['desc'] == '()Z':
                    ins = jvm.disasm(cn, m['name'], m['desc'])
                    if ins == [('iconst', 1), ('ireturn',)]:
                        return True
                    if ins == [('iconst', 0), ('ireturn',)]:
                        return False
            return None
        for f in static_fields(blocks_cls):
            if not f['desc'].startswith('L'):
                continue
            oop = jvm.read_oop_field(blocks_mirror, f['offset'])
            cn = jvm.oop_class_name(oop)
            if not cn or cn not in classes:
                continue
            unlocs = [jvm.read_jstring(jvm.read_oop_field(oop, off)) for _, off in blk_sfields]
            unloc = next((s for s in unlocs if s), '')
            blk_by_unloc.setdefault(unloc, []).append((cn, f['desc'], f['name']))
            blk_all_runtime.setdefault(cn, []).append((unloc, f['desc'], f['name']))
            if unloc == 'log' and cn not in seen_logs:
                seen_logs.append(cn)
            elif unloc == 'leaves' and cn not in seen_leaves:
                seen_leaves.append(cn)
            elif unloc == 'purpurSlab':
                df = is_double_slab(cn)
                if df is True:
                    R['BlockPurpurSlabDouble'] = cn
                elif df is False:
                    R['BlockPurpurSlabHalf'] = cn
        for cn, entries in blk_all_runtime.items():
            unlocs = {e[0] for e in entries}
            if classes[cn]['super'] == blk_cls and {'oreGold', 'oreIron', 'oreCoal'} <= unlocs:
                R['BlockOre'] = cn
            if f'L{cn};' in {e[1] for e in entries} and any(('chest' in u.lower() for u in unlocs)):
                R['BlockChest'] = cn
        UNLOC_TO_BLOCK = {'air': 'BlockAir', 'stone': 'BlockStone', 'grass': 'BlockGrass', 'dirt': 'BlockDirt', 'wood': 'BlockPlanks', 'sapling': 'BlockSapling', 'sand': 'BlockSand', 'gravel': 'BlockGravel', 'sponge': 'BlockSponge', 'glass': 'BlockGlass', 'dispenser': 'BlockDispenser', 'sandStone': 'BlockSandStone', 'musicBlock': 'BlockNote', 'bed': 'BlockBed', 'goldenRail': 'BlockRailPowered', 'detectorRail': 'BlockRailDetector', 'web': 'BlockWeb', 'tallgrass': 'BlockTallGrass', 'deadbush': 'BlockDeadBush', 'Wool': 'BlockColored', 'cloth': 'BlockColored', 'flower1': 'BlockYellowFlower', 'flower2': 'BlockRedFlower', 'tnt': 'BlockTNT', 'bookshelf': 'BlockBookshelf', 'obsidian': 'BlockObsidian', 'torch': 'BlockTorch', 'fire': 'BlockFire', 'mobSpawner': 'BlockMobSpawner', 'redstoneDust': 'BlockRedstoneWire', 'workbench': 'BlockWorkbench', 'crops': 'BlockCrops', 'farmland': 'BlockFarmland', 'furnace': 'BlockFurnace', 'doorOak': 'BlockDoor', 'ladder': 'BlockLadder', 'rail': 'BlockRail', 'lever': 'BlockLever', 'notGate': 'BlockRedstoneTorch', 'cactus': 'BlockCactus', 'clay': 'BlockClay', 'reeds': 'BlockReed', 'jukebox': 'BlockJukebox', 'spruceFence': 'BlockFence', 'pumpkin': 'BlockPumpkin', 'hellrock': 'BlockNetherrack', 'hellsand': 'BlockSoulSand', 'lightgem': 'BlockGlowstone', 'portal': 'BlockPortal', 'cake': 'BlockCake', 'diode': 'BlockRedstoneRepeater', 'stainedGlass': 'BlockStainedGlass', 'trapdoor': 'BlockTrapDoor', 'monsterStoneEgg': 'BlockSilverfish', 'stonebricksmooth': 'BlockStoneBrick', 'fenceIron': 'BlockPane', 'melon': 'BlockMelon', 'pumpkinStem': 'BlockStem', 'vine': 'BlockVine', 'fenceGate': 'BlockFenceGate', 'waterlily': 'BlockLilyPad', 'netherBrick': 'BlockNetherBrick', 'netherStalk': 'BlockNetherWart', 'enchantmentTable': 'BlockEnchantmentTable', 'brewingStand': 'BlockBrewingStand', 'cauldron': 'BlockCauldron', 'endPortalFrame': 'BlockEndPortalFrame', 'dragonEgg': 'BlockDragonEgg', 'redstoneLight': 'BlockRedstoneLamp', 'cocoa': 'BlockCocoa', 'enderChest': 'BlockEnderChest', 'tripWireSource': 'BlockTripWireHook', 'tripWire': 'BlockTripWire', 'commandBlock': 'BlockCommandBlock', 'beacon': 'BlockBeacon', 'cobbleWall': 'BlockWall', 'flowerPot': 'BlockFlowerPot', 'carrots': 'BlockCarrot', 'potatoes': 'BlockPotato', 'skull': 'BlockSkull', 'anvil': 'BlockAnvil', 'weightedPlate_light': 'BlockPressurePlateWeighted', 'comparator': 'BlockRedstoneComparator', 'daylightDetector': 'BlockDaylightDetector', 'blockRedstone': 'BlockCompressedPowered', 'hopper': 'BlockHopper', 'quartzBlock': 'BlockQuartz', 'dropper': 'BlockDropper', 'clayHardenedStained': 'BlockColored', 'thinStainedGlass': 'BlockStainedGlassPane', 'slime': 'BlockSlime', 'barrier': 'BlockBarrier', 'prismarine': 'BlockPrismarine', 'seaLantern': 'BlockSeaLantern', 'hayBlock': 'BlockHay', 'woolCarpet': 'BlockCarpet', 'clayHardened': 'BlockHardenedClay', 'icePacked': 'BlockPackedIce', 'ice': 'BlockIce', 'doublePlant': 'BlockDoublePlant', 'redSandStone': 'BlockRedSandstone', 'boneBlock': 'BlockBone', 'magma': 'BlockMagma', 'concretePowder': 'BlockConcretePowder', 'glazedTerracottaPurple': 'BlockGlazedTerracotta', 'endRod': 'BlockEndRod', 'grassPath': 'BlockGrassPath', 'mycel': 'BlockMycelium', 'pressurePlateStone': 'BlockPressurePlate', 'oreRedstone': 'BlockRedstoneOre', 'stairsNetherBrick': 'BlockStairs'}
        for unloc, bname in UNLOC_TO_BLOCK.items():
            if unloc in blk_by_unloc:
                cns = sorted({x[0] for x in blk_by_unloc[unloc]})
                if len(cns) == 1:
                    R[bname] = cns[0]
        liq_cns = sorted({x[0] for u in ('water', 'lava') for x in blk_by_unloc.get(u, [])})
        if len(liq_cns) == 2:
            c0, c1 = liq_cns
            if len(real_methods(c0)) >= len(real_methods(c1)):
                R['BlockDynamicLiquid'], R['BlockStaticLiquid'] = (c0, c1)
            else:
                R['BlockDynamicLiquid'], R['BlockStaticLiquid'] = (c1, c0)
        if 'snow' in blk_by_unloc:
            for cn in {x[0] for x in blk_by_unloc['snow']}:
                if static_fields(cn):
                    R['BlockSnow'] = cn
                else:
                    R['BlockSnowBlock'] = cn
        if 'mushroom' in blk_by_unloc:
            for cn in {x[0] for x in blk_by_unloc['mushroom']}:
                if classes[cn]['super'] == blk_cls:
                    R['BlockHugeMushroom'] = cn
                else:
                    R['BlockMushroom'] = cn
        ef_cls = R.get('EnumFacing', '')
        if 'sign' in blk_by_unloc and ef_cls:
            for cn in {x[0] for x in blk_by_unloc['sign']}:
                if ef_cls in jvm.cp_referenced_classes(cn):
                    R['BlockWallSign'] = cn
                else:
                    R['BlockStandingSign'] = cn
        if 'banner' in blk_by_unloc and ef_cls:
            for cn in {x[0] for x in blk_by_unloc['banner']}:
                if ef_cls in jvm.cp_referenced_classes(cn):
                    R['BlockBannerHanging'] = cn
                else:
                    R['BlockBannerStanding'] = cn
        if 'button' in blk_by_unloc:
            for cn in {x[0] for x in blk_by_unloc['button']}:
                ins_b = jvm.disasm(cn, '<init>', '()V')
                if ('iconst', 1) in ins_b:
                    R['BlockWoodButton'] = cn
                elif ('iconst', 0) in ins_b:
                    R['BlockStoneButton'] = cn
        for unloc, half_n, dbl_n in (('stoneSlab', 'BlockHalfStoneSlab', 'BlockDoubleStoneSlab'), ('stoneSlab2', 'BlockHalfStoneSlabNew', 'BlockDoubleStoneSlabNew'), ('woodSlab', 'BlockHalfWoodSlab', 'BlockDoubleWoodSlab')):
            for cn in {x[0] for x in blk_by_unloc.get(unloc, [])}:
                df = is_double_slab(cn)
                if df is True:
                    R[dbl_n] = cn
                elif df is False:
                    R[half_n] = cn
        if len(seen_logs) >= 2:
            R['BlockOldLog'], R['BlockNewLog'] = (seen_logs[0], seen_logs[1])
            R['BlockLog'] = classes[seen_logs[0]]['super']
        if len(seen_logs) >= 3:
            R['BlockLog3'] = seen_logs[2]
        if len(seen_leaves) >= 2:
            R['BlockOldLeaf'], R['BlockNewLeaf'] = (seen_leaves[0], seen_leaves[1])
            R['BlockLeaves'] = classes[seen_leaves[0]]['super']
        if 'pistonBase' in blk_by_unloc:
            p_cns = sorted({x[0] for x in blk_by_unloc['pistonBase']})
            if p_cns:
                R['BlockPistonBase'] = p_cns[0]
        for cn, entries in blk_all_runtime.items():
            if [x[0] for x in entries] == ['']:
                refs = jvm.cp_referenced_classes(cn)
                if R.get('TileEntityEndPortal') in refs:
                    R['BlockEndPortal'] = cn
                elif R.get('TileEntityPiston') in refs:
                    R['BlockPistonMoving'] = cn
                else:
                    R['BlockPistonExtension'] = cn
        if 'BlockFurnace' in R:
            R['BlockContainer'] = classes[R['BlockFurnace']]['super']
        if 'BlockTallGrass' in R:
            R['BlockBush'] = classes[R['BlockTallGrass']]['super']
        if 'BlockSand' in R:
            R['BlockFalling'] = classes[R['BlockSand']]['super']
        if 'BlockHalfStoneSlab' in R:
            bs_sup = classes[R['BlockHalfStoneSlab']]['super']
            R['BlockStoneSlab'] = bs_sup
            if bs_sup in classes:
                R['BlockSlab'] = classes[bs_sup]['super']
        if 'BlockHalfStoneSlabNew' in R:
            R['BlockStoneSlabNew'] = classes[R['BlockHalfStoneSlabNew']]['super']
        if 'BlockHalfWoodSlab' in R:
            R['BlockWoodSlab'] = classes[R['BlockHalfWoodSlab']]['super']
        if 'BlockDynamicLiquid' in R:
            R['BlockLiquid'] = classes[R['BlockDynamicLiquid']]['super']
        if 'BlockStoneButton' in R:
            R['BlockButton'] = classes[R['BlockStoneButton']]['super']
        if 'BlockRail' in R:
            R['BlockRailBase'] = classes[R['BlockRail']]['super']
        if 'BlockStandingSign' in R:
            R['BlockSign'] = classes[R['BlockStandingSign']]['super']
        if 'BlockBannerStanding' in R and '$' in R['BlockBannerStanding']:
            R['BlockBanner'] = R['BlockBannerStanding'].split('$')[0]
        if 'BlockYellowFlower' in R:
            bf = classes[R['BlockYellowFlower']]['super']
            R['BlockFlower'] = bf
            bf_inners = [k for k in classes if k.startswith(bf + '$') and classes[k]['super'] == 'java/lang/Enum']
            if bf_inners:
                R['BlockFlower_EnumFlowerType'] = bf_inners[0]
        if 'BlockGlass' in R:
            R['BlockBreakable'] = classes[R['BlockGlass']]['super']
        if 'BlockHay' in R:
            R['BlockRotatedPillar'] = classes[R['BlockHay']]['super']
        if 'BlockPumpkin' in R:
            R['BlockDirectional'] = classes[R['BlockPumpkin']]['super']
        if 'BlockPressurePlate' in R:
            R['BlockBasePressurePlate'] = classes[R['BlockPressurePlate']]['super']
        if 'BlockRedstoneRepeater' in R:
            R['BlockRedstoneDiode'] = classes[R['BlockRedstoneRepeater']]['super']
    if 'Items' in R and 'Item' in R:
        item_cls = R['Item']
        items_cls = R['Items']
        items_mirror = classes[items_cls]['mirror']
        itm_sfields = [(f['name'], f['offset']) for f in inst_fields(item_cls) if f['desc'] == 'Ljava/lang/String;']
        itm_by_unloc = {}
        for f in static_fields(items_cls):
            if not f['desc'].startswith('L'):
                continue
            oop = jvm.read_oop_field(items_mirror, f['offset'])
            cn = jvm.oop_class_name(oop)
            if cn and cn in classes:
                unlocs = [jvm.read_jstring(jvm.read_oop_field(oop, off)) for _, off in itm_sfields]
                unloc = next((s for s in unlocs if s), '')
                itm_by_unloc.setdefault(unloc, []).append(cn)
        UNLOC_TO_ITEM = {'swordDiamond': 'ItemSword', 'pickaxeDiamond': 'ItemPickaxe', 'hatchetDiamond': 'ItemAxe', 'shovelDiamond': 'ItemSpade', 'hoeDiamond': 'ItemHoe', 'helmetDiamond': 'ItemArmor', 'potion': 'ItemPotion', 'apple': 'ItemFood', 'appleGold': 'ItemAppleGold', 'bow': 'ItemBow', 'fishingRod': 'ItemFishingRod', 'enderPearl': 'ItemEnderPearl', 'snowball': 'ItemSnowball', 'egg': 'ItemEgg', 'mushroomStew': 'ItemSoup', 'bucket': 'ItemBucket', 'shears': 'ItemShears', 'flintAndSteel': 'ItemFlintAndSteel', 'writtenBook': 'ItemWrittenBook', 'glassBottle': 'ItemGlassBottle', 'writingBook': 'ItemWritableBook', 'eyeOfEnder': 'ItemEnderEye', 'expBottle': 'ItemExpBottle', 'fish': 'ItemFishFood', 'emptyMap': 'ItemEmptyMap', 'fireball': 'ItemFireball', 'leash': 'ItemLead', 'sign': 'ItemSign', 'book': 'ItemBook', 'frame': 'ItemHangingEntity', 'armorStand': 'ItemArmorStand', 'milk': 'ItemBucketMilk', 'magic_milk': 'ItemMagicMilk', 'seeds': 'ItemSeeds', 'skull': 'ItemSkull', 'nameTag': 'ItemNameTag', 'fireworksCharge': 'ItemFireworkCharge', 'boat': 'ItemBoat', 'string': 'ItemReed', 'carrotOnAStick': 'ItemCarrotOnAStick', 'doorOak': 'ItemDoor', 'fireworks': 'ItemFirework', 'minecart': 'ItemMinecart', 'saddle': 'ItemSaddle', 'banner': 'ItemBanner', 'redstone': 'ItemRedstone', 'monsterPlacer': 'ItemMonsterPlacer', 'enchantedBook': 'ItemEnchantedBook', 'netherStar': 'ItemSimpleFoiled', 'potato': 'ItemSeedFood', 'coal': 'ItemCoal', 'bed': 'ItemBed', 'record': 'ItemRecord', 'map': 'ItemMap', 'dyePowder': 'ItemDye'}
        for unloc, iname in UNLOC_TO_ITEM.items():
            if unloc in itm_by_unloc:
                cns = sorted(set(itm_by_unloc[unloc]))
                if len(cns) == 1:
                    R[iname] = cns[0]
        if 'ItemPickaxe' in R:
            R['ItemTool'] = classes[R['ItemPickaxe']]['super']
        for inr in classes:
            if inr.startswith(item_cls + '$') and classes[inr]['super'] == 'java/lang/Enum':
                R['ItemToolMaterial'] = inr
                break
        if 'ItemArmor' in R:
            for inr in classes:
                if inr.startswith(R['ItemArmor'] + '$') and classes[inr]['super'] == 'java/lang/Enum':
                    R['ItemArmorMaterial'] = inr
                    break
        if 'ItemMap' in R:
            R['ItemMapBase'] = classes[R['ItemMap']]['super']
        for sub in children.get(item_cls, []):
            kids = children.get(sub, [])
            if len(kids) >= 6:
                R['ItemBlock'] = sub
                for kid in kids:
                    if kid in R.values():
                        continue
                    fdescs = [f['desc'] for f in inst_fields(kid)]
                    if R.get('BlockSlab') and f"L{R['BlockSlab']};" in fdescs:
                        R['ItemSlab'] = kid
                    elif R.get('BlockLeaves') and f"L{R['BlockLeaves']};" in fdescs:
                        R['ItemLeaves'] = kid
                    elif any(('Function' in fd for fd in fdescs)):
                        R['ItemMultiTexture'] = kid
                        for gk in children.get(kid, []):
                            refs = jvm.cp_referenced_classes(gk)
                            if R.get('BlockAnvil') in refs:
                                R['ItemAnvilBlock'] = gk
                            elif R.get('BlockDoublePlant') in refs:
                                R['ItemDoublePlant'] = gk
                            elif len(children.get(kid, [])) == 1:
                                R['ItemAnvilBlock'] = gk
                    elif '[Ljava/lang/String;' in fdescs:
                        R['ItemColored'] = kid
                        gkids = children.get(kid, [])
                        if len(gkids) == 1:
                            R['ItemLilyPad'] = gkids[0]
                    else:
                        non_init = [m for m in real_methods(kid) if m['name'] not in ('<init>', '<clinit>') and (not m['static'])]
                        has_bipush7 = any((m['desc'] == '(I)I' and ('bipush', 7) in jvm.disasm(kid, m['name'], m['desc']) for m in non_init))
                        if has_bipush7:
                            R['ItemPiston'] = kid
                        elif R.get('BlockPos') and any((f"L{R['BlockPos']};" in m['desc'] for m in non_init)):
                            R['ItemSnow'] = kid
                        elif len(non_init) == 1:
                            R['ItemSponge'] = kid
                        elif len(non_init) == 2:
                            R['ItemCloth'] = kid
                break
    for fc in mc_fdescs:
        if fc in classes and len(children.get(fc, [])) >= 12:
            if any((f['desc'] == f"L{R.get('FontRenderer', '')};" for f in inst_fields(fc))):
                R['GuiScreen'] = fc
                R['Gui'] = classes[fc]['super']
                break
    if 'GuiScreen' in R:
        gs_cls = R['GuiScreen']
        gui_cls = R['Gui']
        for fc in mc_fdescs:
            if fc in classes and classes[fc]['super'] == gui_cls and (fc != gs_cls):
                if len(real_methods(fc)) >= 15:
                    R['GuiInGame'] = fc
                    break
        for gc in children.get(gs_cls, []):
            ctors = {m['desc'] for m in classes[gc]['methods'] if m['name'] == '<init>'}
            if '()V' in ctors and '(Ljava/lang/String;)V' in ctors and (len(children.get(gc, [])) <= 3):
                s_cnt = sum((1 for f in inst_fields(gc) if f['desc'] == 'Ljava/lang/String;'))
                has_textfield = any((f['desc'].startswith('L') and f['desc'][1:-1] in classes and (classes[f['desc'][1:-1]]['super'] == gui_cls) for f in inst_fields(gc)))
                if 1 <= s_cnt <= 4 and has_textfield:
                    R['GuiChat'] = gc
                    break
        for gc in children.get(gs_cls, []):
            if R.get('Container') and any((f['desc'] == f"L{R['Container']};" for f in inst_fields(gc))):
                R['GuiContainer'] = gc
                for sub in children.get(gc, []):
                    for m in classes[sub]['methods']:
                        if m['name'] == '<init>':
                            pd = parse_method_desc(m['desc'])
                            if pd and len(pd[0]) == 2 and (pd[0][0] == pd[0][1]) and pd[0][0].startswith('L'):
                                iinv = pd[0][0][1:-1]
                                if iinv in classes and classes[iinv]['acc'] & 512:
                                    R['GuiChest'] = sub
                                    R['IInventory'] = iinv
                                    break
                    gsubs = children.get(sub, [])
                    if gsubs:
                        R['InventoryEffectRenderer'] = sub
                        for gs2 in gsubs:
                            if any((m['name'] == '<init>' and m['desc'] == f'(L{ep_cls};)V' for m in classes[gs2]['methods'])):
                                R['GuiInventory'] = gs2
                break
        if 'GuiInGame' in R:
            for f in inst_fields(R['GuiInGame']):
                if f['desc'].startswith('L'):
                    cn = f['desc'][1:-1]
                    if cn in classes and classes[cn]['super'] == gui_cls:
                        mdescs = [m['desc'] for m in real_methods(cn)]
                        if R.get('IChatComponent') and any((f"L{R['IChatComponent']};" in md and 'I' in md for md in mdescs)):
                            R['GuiNewChat'] = cn
                        elif R.get('NetworkPlayerInfo') and any((f"L{R['NetworkPlayerInfo']};" in md for md in mdescs)):
                            R['GuiPlayerTabOverlay'] = cn
        if 'GuiChat' in R:
            for f in inst_fields(R['GuiChat']):
                if f['desc'].startswith('L'):
                    cn = f['desc'][1:-1]
                    if cn in classes and classes[cn]['super'] == gui_cls:
                        R['GuiTextField'] = cn
                        break
        for gc in children.get(gs_cls, []):
            if gc.startswith('crsecond/'):
                if any(('setupElements' in m['name'] or 'MainMenu' in m['name'] for m in classes[gc]['methods'])):
                    R['EscMenu'] = gc
            elif gc not in R.values():
                fdescs = [f['desc'] for f in inst_fields(gc)]
                if f'L{gs_cls};' in fdescs and fdescs.count('Z') >= 4 and any(('Logger' in f['desc'] for f in classes[gc]['fields'])):
                    R['GuiMultiplayer'] = gc
    if 'ItemStack' in R:
        for m in real_methods(R['ItemStack']):
            pd = parse_method_desc(m['desc'])
            if pd and len(pd[0]) == 1 and (pd[0][0] == pd[1]) and pd[0][0].startswith('L'):
                nbt_c = pd[0][0][1:-1]
                if nbt_c in classes and any(('Map;' in f['desc'] for f in inst_fields(nbt_c))):
                    R['NBTTagCompound'] = nbt_c
                    R['NBTBase'] = classes[nbt_c]['super']
                    for sub in children.get(R['NBTBase'], []):
                        if sub != nbt_c and any(('List;' in f['desc'] for f in inst_fields(sub))):
                            R['NBTTagList'] = sub
                    break
    for k, v in classes.items():
        arr_f = [f for f in static_fields(k) if f['desc'] == f'[L{k};']
        if arr_f and sum((1 for f in static_fields(k) if f['desc'] == f'L{k};')) >= 20:
            if k != R.get('BiomeGenBase'):
                arr_oop = jvm.read_oop_field(v['mirror'], arr_f[0]['offset'])
                if arr_oop and jvm.r4(arr_oop + 12) in (32, 64, 128):
                    R['Potion'] = k
                    for m in real_methods(R['EntityLivingBase']):
                        pd = parse_method_desc(m['desc'])
                        if pd and pd[0] == [f'L{k};'] and pd[1].startswith('L'):
                            R['PotionEffect'] = pd[1][1:-1]
                            break
                    break
    if 'RenderManager' in R:
        rm_cls = R['RenderManager']
        for f in inst_fields(rm_cls):
            if f['desc'].startswith('L'):
                fc = f['desc'][1:-1]
                if fc in classes and len(children.get(classes[fc]['super'], [])) >= 2:
                    sup1 = classes[fc]['super']
                    if sup1 in classes and classes[sup1]['super'] in classes:
                        sup2 = classes[sup1]['super']
                        if len(children.get(sup2, [])) >= 20:
                            R['RenderPlayer'] = fc
                            R['RendererLivingEntity'] = sup1
                            R['Render'] = sup2
                            break
        if 'RendererLivingEntity' in R:
            rle = R['RendererLivingEntity']
            for f in inst_fields(rle):
                if f['desc'].startswith('L'):
                    mb = f['desc'][1:-1]
                    if mb in classes and len(children.get(mb, [])) >= 15:
                        R['ModelBase'] = mb
                        for mm in real_methods(mb):
                            if mm['desc'].startswith('(Ljava/lang/String;)L'):
                                R['TextureOffset'] = mm['desc'].split(')')[1][1:-1]
                        for s in children.get(mb, []):
                            ft_c = collections.Counter((sf['desc'] for sf in inst_fields(s) if sf['desc'].startswith('L')))
                            for mr_desc, mr_cnt in ft_c.items():
                                if mr_cnt >= 6 and children.get(s):
                                    R['ModelBiped'] = s
                                    R['ModelRenderer'] = mr_desc[1:-1]
                                    for mp_sub in children[s]:
                                        if sum((1 for pf in inst_fields(mp_sub) if pf['desc'] == mr_desc)) >= 4:
                                            R['ModelPlayer'] = mp_sub
                                            break
                                    break
                        break
            if 'ModelBiped' in R:
                for sub in children.get(rle, []):
                    if any((f['desc'] == f"L{R['ModelBiped']};" for f in inst_fields(sub))):
                        R['RenderBiped'] = sub
                        break
    for f in inst_fields(mc_cls):
        if not f['desc'].startswith('L'):
            continue
        cn = f['desc'][1:-1]
        if cn not in classes or cn in R.values():
            continue
        fdescs = [x['desc'] for x in inst_fields(cn)]
        sdescs = [x['desc'] for x in static_fields(cn)]
        mdescs = [x['desc'] for x in real_methods(cn)]
        if classes[cn]['super'] == 'java/lang/Object' and fdescs.count('Ljava/util/Map;') >= 2 and R.get('ResourceLocation') and any((m.startswith(f"(L{R['ResourceLocation']};)") for m in mdescs)):
            R['TextureManager'] = cn
        elif '[F' in fdescs and fdescs.count('I') >= 6 and (len(inst_fields(cn)) <= 15):
            R['Framebuffer'] = cn
        elif R.get('ResourceLocation') and f"[L{R['ResourceLocation']};" in sdescs and (len(classes[cn]['fields']) >= 45):
            R['EntityRenderer'] = cn
            for ef in inst_fields(cn):
                if ef['desc'].startswith('L') and ef['desc'][1:-1] in classes:
                    ecn = ef['desc'][1:-1]
                    if '[I' in [x['desc'] for x in inst_fields(ecn)] and len(inst_fields(ecn)) <= 6:
                        R['DynamicTexture'] = ecn
        elif R.get('WorldClient') and R.get('RenderManager') and (f"L{R['WorldClient']};" in fdescs) and (f"L{R['RenderManager']};" in fdescs):
            R['RenderGlobal'] = cn
        elif 'Ljava/util/List;' in fdescs and 'Ljava/util/Map;' in fdescs and ('(Ljava/lang/String;)V' in mdescs) and ('()V' in mdescs) and (len(inst_fields(cn)) <= 10):
            R['Profiler'] = cn
        for sf in inst_fields(cn):
            if sf['desc'].startswith('L') and sf['desc'][1:-1] in classes:
                scn = sf['desc'][1:-1]
                if any(('paulscode' in x['desc'] or 'SoundSystem' in x['desc'] for x in classes[scn]['fields'])):
                    R['SoundHandler'] = cn
                    R['SoundManager'] = scn
    if 'TextureManager' in R:
        tm_desc = f"L{R['TextureManager']};"
        for fc in mc_fdescs:
            if fc not in classes or fc in R.values():
                continue
            fdescs = [x['desc'] for x in inst_fields(fc)]
            mdescs = [x['desc'] for x in real_methods(fc)]
            if tm_desc in fdescs and f"L{R.get('World', '')};" in fdescs and (len(inst_fields(fc)) <= 20):
                R['EffectRenderer'] = fc
            elif tm_desc in fdescs and R.get('ItemStack') and any((f"L{R['ItemStack']};" in m for m in mdescs)):
                R['RenderItem'] = fc
    if 'EntityRenderer' in R:
        er_ftypes = {f['desc'][1:-1] for f in inst_fields(R['EntityRenderer']) if f['desc'].startswith('L')}
        for cn in er_ftypes & mc_fdescs:
            if cn in classes and cn not in R.values():
                if R.get('ItemStack') and any((f"L{R['ItemStack']};" in m['desc'] for m in real_methods(cn))):
                    R['ItemRenderer'] = cn
        if 'Framebuffer' in R:
            fb_desc = f"L{R['Framebuffer']};"
            for cn in er_ftypes:
                if cn in classes and cn not in R.values():
                    fds = [x['desc'] for x in inst_fields(cn)]
                    if fb_desc in fds and fds.count('Ljava/util/List;') >= 2:
                        R['ShaderGroup'] = cn
    if 'IBlockState' in R:
        ibs_cls = R['IBlockState']
        gs_desc = f"L{R.get('GameSettings', '')};"
        for cn in mc_fdescs:
            if cn in classes and cn not in R.values():
                cn_fdescs = [x['desc'] for x in inst_fields(cn)]
                for f in inst_fields(cn):
                    if f['desc'].startswith('L') and f['desc'][1:-1] in classes:
                        bms = f['desc'][1:-1]
                        for m in real_methods(bms):
                            if m['desc'].startswith(f'(L{ibs_cls};)L'):
                                ibm = m['desc'].split(')')[1][1:-1]
                                if ibm in classes and ibm not in (R.get('Block'), ibs_cls):
                                    R['BlockModelShapes'] = bms
                                    R['IBakedModel'] = ibm
                                    if gs_desc in cn_fdescs or 'BlockRendererDispatcher' not in R:
                                        R['BlockRendererDispatcher'] = cn
    if 'RenderGlobal' in R:
        for m in real_methods(R['RenderGlobal']):
            if m['desc'].startswith(f"(L{R['Entity']};DL") and m['desc'].endswith(';IZ)V'):
                R['ICamera'] = m['desc'].split(';D')[1].split(';IZ')[0][1:]
                break
    for f in inst_fields(R['Entity']):
        if f['desc'].startswith('L') and f['desc'][1:-1] in classes:
            cn = f['desc'][1:-1]
            if any((x['desc'] == 'Ljava/util/concurrent/locks/ReadWriteLock;' for x in classes[cn]['fields'])):
                R['DataWatcher'] = cn
                break
    for f in inst_fields(ep_cls):
        if f['desc'].startswith('L') and f['desc'][1:-1] in classes:
            cn = f['desc'][1:-1]
            if cn in R.values():
                continue
            fds = [x['desc'] for x in inst_fields(cn)]
            mds = [m['desc'] for m in real_methods(cn)]
            if R.get('NBTTagCompound') and f"(L{R['NBTTagCompound']};)V" in mds:
                if '(IF)V' in mds and '()I' in mds:
                    R['FoodStats'] = cn
                elif fds.count('Z') >= 4:
                    R['PlayerCapabilities'] = cn
    for f in inst_fields(R['EntityPlayerSP']):
        if f['desc'].startswith('L') and f['desc'][1:-1] in classes:
            cn = f['desc'][1:-1]
            fds = [x['desc'] for x in inst_fields(cn)]
            if fds.count('F') == 2 and fds.count('Z') == 2:
                R['MovementInput'] = cn
                break
    if 'World' in R:
        for f in inst_fields(R['World']):
            if not f['desc'].startswith('L') or f['desc'][1:-1] not in classes:
                continue
            cn = f['desc'][1:-1]
            fds = [x['desc'] for x in inst_fields(cn)]
            if '[F' in fds and f"L{R['World']};" in fds:
                R['WorldProvider'] = cn
                for wf in inst_fields(cn):
                    if wf['desc'].startswith('L') and wf['desc'][1:-1] in classes:
                        wcn = wf['desc'][1:-1]
                        if any((x['static'] and x['desc'] == f'[L{wcn};' for x in classes[wcn]['fields'])):
                            R['WorldType'] = wcn
            elif fds.count('J') >= 5 and fds.count('I') >= 5 and ('Ljava/lang/String;' in fds):
                R['WorldInfo'] = cn
        if 'WorldInfo' in R:
            wi_cls = R['WorldInfo']
            for f in inst_fields(R['World']):
                if f['desc'].startswith('L') and f['desc'][1:-1] in classes:
                    cn = f['desc'][1:-1]
                    if any((m['desc'] == f'()L{wi_cls};' for m in classes[cn]['methods'])):
                        R['ISaveHandler'] = cn
            for m in classes[wi_cls]['methods']:
                if m['name'] == '<init>':
                    pd = parse_method_desc(m['desc'])
                    if pd and len(pd[0]) == 2 and (pd[0][1] == 'Ljava/lang/String;') and pd[0][0].startswith('L'):
                        ws_cls = pd[0][0][1:-1]
                        if ws_cls in classes:
                            R['WorldSettings'] = ws_cls
                            for inr in classes:
                                if inr.startswith(ws_cls + '$') and classes[inr]['super'] == 'java/lang/Enum':
                                    R['WorldSettings$GameType'] = inr
    if 'NetworkPlayerInfo' in R and R['NetworkPlayerInfo'] in classes and ('WorldSettings$GameType' not in R):
        for f in inst_fields(R['NetworkPlayerInfo']):
            if f['desc'].startswith('L') and '$' in f['desc']:
                ec = f['desc'][1:-1]
                if ec in classes and classes[ec]['super'] == 'java/lang/Enum':
                    R['WorldSettings$GameType'] = ec
                    R['WorldSettings'] = ec.split('$')[0]
                    break
    if 'Chunk' in R:
        for f in inst_fields(R['Chunk']):
            if f['desc'].startswith('[L'):
                ec = f['desc'][2:-1]
                if ec in classes and '[C' in [x['desc'] for x in inst_fields(ec)]:
                    R['ExtendedBlockStorage'] = ec
                    break
    for k, v in classes.items():
        f_inst = inst_fields(k)
        f_stat = static_fields(k)
        fdescs = [f['desc'] for f in f_inst]
        sdescs = [f['desc'] for f in f_stat]
        mdescs = [m['desc'] for m in real_methods(k)]
        if v['super'] == 'java/lang/Object' and any((m['name'] == '<init>' and m['desc'] == f'(L{mc_cls};)V' for m in v['methods'])):
            if fdescs.count('D') >= 2 and fdescs.count('I') >= 3:
                R['ScaledResolution'] = k
        if v['super'] == 'java/lang/Object' and '[S' in fdescs and R.get('IBlockState') and any((m == f"(III)L{R['IBlockState']};" for m in mdescs)):
            R['ChunkPrimer'] = k
        if v['super'] == 'java/lang/Object' and len(real_methods(k)) > 65 and ('(FFFF)V' in mdescs) and ('(DDD)V' in mdescs) and ('(FFF)V' in mdescs) and (sum((1 for sd in sdescs if sd.startswith(f'L{k}$'))) >= 5):
            R['GlStateManager'] = k
        if v['super'] == 'java/lang/Object' and 'Ljava/nio/FloatBuffer;' in sdescs and R.get('Vec3') and (sdescs.count(f"L{R['Vec3']};") == 2):
            R['RenderHelper'] = k
        if 'Ljava/nio/FloatBuffer;' in sdescs and 'Ljava/nio/IntBuffer;' in sdescs and (f'(L{ep_cls};Z)V' in mdescs):
            R['ActiveRenderInfo'] = k
        if k.startswith('crsecond/') and 'Ljava/lang/Runnable;' in sdescs and (f"L{R['EntityPlayerSP']};" in sdescs):
            R['ClientUtils'] = k
        if k.startswith('crsecond/') and 'Ljava/util/concurrent/ConcurrentHashMap;' in sdescs and ('J' in sdescs):
            s_cr = [sd for sd in sdescs if sd.startswith('Lcrsecond/')]
            if len(s_cr) >= 2 and len(s_cr) != len(set(s_cr)):
                R['CpsTracker'] = k
    if 'CpsTracker' in R:
        for f in static_fields(R['CpsTracker']):
            if f['desc'].startswith('Lcrsecond/'):
                wc = f['desc'][1:-1]
                if wc in classes and any((m['name'] == '<init>' and m['desc'] == '(I)V' for m in classes[wc]['methods'])):
                    R['IntegerWrapper'] = wc
                    break
    if 'ClientUtils' in R:
        for f in static_fields(R['ClientUtils']):
            if f['desc'].startswith('Lcrsecond/'):
                sc = f['desc'][1:-1]
                if sc in classes and any((m['name'] == '<init>' and m['desc'] == f"(L{R['Entity']};F)V" for m in classes[sc]['methods'])):
                    R['ScoreBoardUtil'] = sc
                    break
    return R
