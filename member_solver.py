from jvm_reader import JVMProcess
TARGET_MEMBERS = {
    'Minecraft.theMinecraft': ('f', 'Minecraft', 'theMinecraft'),
    'Minecraft.theWorld': ('f', 'Minecraft', 'theWorld'),
    'Minecraft.currentScreen': ('f', 'Minecraft', 'currentScreen'),
    'Minecraft.ingameGUI': ('f', 'Minecraft', 'ingameGUI'),
    'Minecraft.objectMouseOver': ('f', 'Minecraft', 'objectMouseOver'),
    'Minecraft.playerController': ('f', 'Minecraft', 'playerController'),
    'Minecraft.renderManager': ('f', 'Minecraft', 'renderManager'),
    'Minecraft.gameSettings': ('f', 'Minecraft', 'gameSettings'),
    'Minecraft.getThePlayer': ('m', 'Minecraft', 'getThePlayer'),
    'Minecraft.getFontRendererObj': ('m', 'Minecraft', 'getFontRendererObj'),
    'Minecraft.getNetHandler': ('m', 'Minecraft', 'getNetHandler'),
    'Minecraft.clickMouse': ('m', 'Minecraft', 'clickMouse'),
    'Minecraft.rightClickMouse': ('m', 'Minecraft', 'rightClickMouse'),
    'Minecraft.leftClickCounter': ('f', 'Minecraft', 'leftClickCounter'),
    'Minecraft.rightClickDelayTimer': ('f', 'Minecraft', 'rightClickDelayTimer'),
    'Timer.timerSpeed': ('f', 'Timer', 'timerSpeed'),
    'TimerContainer.getValue': ('m', 'TimerContainer', 'getValue'),
    'TimerContainer.setValue': ('m', 'TimerContainer', 'setValue'),
    'TimerContainer.valA': ('f', 'TimerContainer', 'valA'),
    'TimerContainer.valB': ('f', 'TimerContainer', 'valB'),
    'TimerContainer.xorKey': ('f', 'TimerContainer', 'xorKey'),
    'TimerContainer.xorStatic': ('f', 'TimerContainer', 'xorStatic'),
    'GameSettings.keyBindForward': ('f', 'GameSettings', 'keyBindForward'),
    'GameSettings.keyBindBack': ('f', 'GameSettings', 'keyBindBack'),
    'GameSettings.keyBindLeft': ('f', 'GameSettings', 'keyBindLeft'),
    'GameSettings.keyBindRight': ('f', 'GameSettings', 'keyBindRight'),
    'GameSettings.keyBindJump': ('f', 'GameSettings', 'keyBindJump'),
    'GameSettings.keyBindSneak': ('f', 'GameSettings', 'keyBindSneak'),
    'GameSettings.keyBindSprint': ('f', 'GameSettings', 'keyBindSprint'),
    'KeyBinding.pressed': ('f', 'KeyBinding', 'pressed'),
    'KeyBinding.isKeyDown': ('m', 'KeyBinding', 'isKeyDown'),
    'KeyBinding.isPressed': ('m', 'KeyBinding', 'isPressed'),
    'KeyBinding.setKeyBindState': ('m', 'KeyBinding', 'setKeyBindState'),
    'MotionContainer.get': ('m', 'MotionContainer', 'get'),
    'MotionContainer.set': ('m', 'MotionContainer', 'set'),
    'BooleanContainer.getValue': ('m', 'BooleanContainer', 'getValue'),
    'FloatContainer.getFloatValue': ('m', 'FloatContainer', 'getFloatValue'),
    'Entity.entityId': ('f', 'Entity', 'entityId'),
    'Entity.worldObj': ('f', 'Entity', 'worldObj'),
    'Entity.posX': ('f', 'Entity', 'posX'),
    'Entity.posY': ('f', 'Entity', 'posY'),
    'Entity.posZ': ('f', 'Entity', 'posZ'),
    'Entity.lastTickPosX': ('f', 'Entity', 'lastTickPosX'),
    'Entity.lastTickPosY': ('f', 'Entity', 'lastTickPosY'),
    'Entity.lastTickPosZ': ('f', 'Entity', 'lastTickPosZ'),
    'Entity.motionX': ('f', 'Entity', 'motionX'),
    'Entity.motionY': ('f', 'Entity', 'motionY'),
    'Entity.motionZ': ('f', 'Entity', 'motionZ'),
    'Entity.onGround': ('f', 'Entity', 'onGround'),
    'Entity.fallDistance': ('f', 'Entity', 'fallDistance'),
    'Entity.rotationYaw': ('f', 'Entity', 'rotationYaw'),
    'Entity.rotationPitch': ('f', 'Entity', 'rotationPitch'),
    'Entity.prevRotationYaw': ('f', 'Entity', 'prevRotationYaw'),
    'Entity.prevRotationPitch': ('f', 'Entity', 'prevRotationPitch'),
    'Entity.setPositionAndRotation': ('m', 'Entity', 'setPositionAndRotation'),
    'Entity.setPositionAndUpdate': ('m', 'Entity', 'setPositionAndUpdate'),
    'Entity.getDistanceToEntity': ('m', 'Entity', 'getDistanceToEntity'),
    'Entity.getEyeHeight': ('m', 'Entity', 'getEyeHeight'),
    'Entity.getFlag': ('m', 'Entity', 'getFlag'),
    'Entity.getName': ('m', 'Entity', 'getName'),
    'Entity.rayTrace': ('m', 'Entity', 'rayTrace'),
    'EntityLivingBase.getHealth': ('m', 'EntityLivingBase', 'getHealth'),
    'EntityLivingBase.hurtTime': ('f', 'EntityLivingBase', 'hurtTime'),
    'EntityLivingBase.rotationYawHead': ('f', 'EntityLivingBase', 'rotationYawHead'),
    'EntityLivingBase.renderYawOffset': ('f', 'EntityLivingBase', 'renderYawOffset'),
    'EntityLivingBase.swingItem': ('m', 'EntityLivingBase', 'swingItem'),
    'EntityLivingBase.setSprinting': ('m', 'EntityLivingBase', 'setSprinting'),
    'EntityPlayer.inventory': ('f', 'EntityPlayer', 'inventory'),
    'EntityPlayer.inventoryContainer': ('f', 'EntityPlayer', 'inventoryContainer'),
    'EntityPlayer.openContainer': ('f', 'EntityPlayer', 'openContainer'),
    'EntityPlayer.getHeldItem': ('m', 'EntityPlayer', 'getHeldItem'),
    'EntityPlayer.closeScreen': ('m', 'EntityPlayer', 'closeScreen'),
    'EntityPlayer.dropOneItem': ('m', 'EntityPlayer', 'dropOneItem'),
    'AbstractClientPlayer.playerInfo': ('f', 'AbstractClientPlayer', 'playerInfo'),
    'AbstractClientPlayer.getLocationSkin': ('m', 'AbstractClientPlayer', 'getLocationSkin'),
    'EntityPlayerSP.sendQueue': ('f', 'EntityPlayerSP', 'sendQueue'),
    'EntityPlayerSP.sendChatMessage': ('m', 'EntityPlayerSP', 'sendChatMessage'),
    'EntityPlayerSP.addChatMessage': ('m', 'EntityPlayerSP', 'addChatMessage'),
    'EntityItem.getEntityItem': ('m', 'EntityItem', 'getEntityItem'),
    'InventoryPlayer.mainInventory': ('f', 'InventoryPlayer', 'mainInventory'),
    'InventoryPlayer.armorInventory': ('f', 'InventoryPlayer', 'armorInventory'),
    'InventoryPlayer.currentItem': ('f', 'InventoryPlayer', 'currentItem'),
    'Container.getSlot': ('m', 'Container', 'getSlot'),
    'Container.inventorySlots': ('f', 'Container', 'inventorySlots'),
    'Container.windowId': ('f', 'Container', 'windowId'),
    'Slot.getStack': ('m', 'Slot', 'getStack'),
    'ItemStack.item': ('f', 'ItemStack', 'item'),
    'ItemStack.stackSize': ('f', 'ItemStack', 'stackSize'),
    'ItemStack.itemDamage': ('f', 'ItemStack', 'itemDamage'),
    'ItemStack.getMetadata': ('m', 'ItemStack', 'getMetadata'),
    'ItemStack.getDisplayName': ('m', 'ItemStack', 'getDisplayName'),
    'Item.getUnlocalizedName': ('m', 'Item', 'getUnlocalizedName'),
    'EnchantmentHelper.getEnchantmentLevel': ('m', 'EnchantmentHelper', 'getEnchantmentLevel'),
    'World.playerEntities': ('f', 'World', 'playerEntities'),
    'World.loadedEntityList': ('f', 'World', 'loadedEntityList'),
    'World.getBlockState': ('m', 'World', 'getBlockState'),
    'Chunk.getBlock': ('m', 'Chunk', 'getBlock'),
    'Block.getIdFromBlock': ('m', 'Block', 'getIdFromBlock'),
    'Block.getUnlocalizedName': ('m', 'Block', 'getUnlocalizedName'),
    'Block.getLocalizedName': ('m', 'Block', 'getLocalizedName'),
    'IBlockState.getBlock': ('m', 'IBlockState', 'getBlock'),
    'MovingObjectPosition.entityHit': ('f', 'MovingObjectPosition', 'entityHit'),
    'MovingObjectPosition.typeOfHit': ('f', 'MovingObjectPosition', 'typeOfHit'),
    'MovingObjectPosition.hitVec': ('f', 'MovingObjectPosition', 'hitVec'),
    'MovingObjectPosition.blockPos': ('f', 'MovingObjectPosition', 'blockPos'),
    'MovingObjectPosition.sideHit': ('f', 'MovingObjectPosition', 'sideHit'),
    'PlayerControllerMP.windowClick': ('m', 'PlayerControllerMP', 'windowClick'),
    'PlayerControllerMP.blockHitDelay': ('f', 'PlayerControllerMP', 'blockHitDelay'),
    'PlayerControllerMP.syncCurrentPlayItem': ('m', 'PlayerControllerMP', 'syncCurrentPlayItem'),
    'RenderManager.renderPosX': ('f', 'RenderManager', 'renderPosX'),
    'RenderManager.renderPosY': ('f', 'RenderManager', 'renderPosY'),
    'RenderManager.renderPosZ': ('f', 'RenderManager', 'renderPosZ'),
    'RenderManager.viewerPosX': ('f', 'RenderManager', 'viewerPosX'),
    'RenderManager.viewerPosY': ('f', 'RenderManager', 'viewerPosY'),
    'RenderManager.viewerPosZ': ('f', 'RenderManager', 'viewerPosZ'),
    'RenderManager.playerViewY': ('f', 'RenderManager', 'playerViewY'),
    'RenderManager.playerViewX': ('f', 'RenderManager', 'playerViewX'),
    'FontRenderer.drawString': ('m', 'FontRenderer', 'drawString'),
    'FontRenderer.getStringWidth': ('m', 'FontRenderer', 'getStringWidth'),
    'NetHandlerPlayClient.networkManager': ('f', 'NetHandlerPlayClient', 'networkManager'),
    'NetHandlerPlayClient.sendPacket': ('m', 'NetHandlerPlayClient', 'sendPacket'),
    'NetworkManager.channel': ('f', 'NetworkManager', 'channel'),
    'NetworkPlayerInfo.getGameProfile': ('m', 'NetworkPlayerInfo', 'getGameProfile'),
    'NetworkPlayerInfo.getDisplayName': ('m', 'NetworkPlayerInfo', 'getDisplayName'),
    'NetworkPlayerInfo.getLocationSkin': ('m', 'NetworkPlayerInfo', 'getLocationSkin'),
    'NetworkPlayerInfo.responseTime': ('f', 'NetworkPlayerInfo', 'responseTime'),
    'NetworkPlayerInfo.getResponseTime': ('m', 'NetworkPlayerInfo', 'getResponseTime'),
    'GameProfile.getUUID': ('m', 'GameProfile', 'getUUID'),
    'GameProfile.getName': ('m', 'GameProfile', 'getName'),
}

def solve_members(jvm, R):
    classes = jvm.classes
    M = {}

    def fields_of(cn, static=None, desc=None):
        info = classes.get(cn)
        if not info:
            return []
        return [f for f in info['fields'] if not f['name'].startswith(('fake_', 'var_')) and (static is None or f['static'] == static) and (desc is None or f['desc'] == desc)]

    def methods_of(cn, static=None, desc=None):
        info = classes.get(cn)
        if not info:
            return []
        return [m for m in info['methods'] if not m['dummy_noop'] and m['name'] not in ('<init>', '<clinit>') and (static is None or m['static'] == static) and (desc is None or m['desc'] == desc)]

    def set_unique_field(const_key, cn, desc, static=False):
        fs = fields_of(cn, static=static, desc=desc)
        if len(fs) == 1:
            M[const_key] = (fs[0]['name'], desc)

    def set_unique_method(const_key, cn, desc, static=False):
        ms = methods_of(cn, static=static, desc=desc)
        if len(ms) == 1:
            M[const_key] = (ms[0]['name'], desc)
    mc_cls = R['Minecraft']
    mc_oop = 0
    for f in fields_of(mc_cls, static=True, desc=f'L{mc_cls};'):
        oop = jvm.read_oop_field(classes[mc_cls]['mirror'], f['offset'])
        if oop and jvm.oop_class_name(oop) == mc_cls:
            M['Minecraft.theMinecraft'] = (f['name'], f['desc'])
            mc_oop = oop
            break
    set_unique_field('Minecraft.theWorld', mc_cls, f"L{R['WorldClient']};")
    set_unique_field('Minecraft.currentScreen', mc_cls, f"L{R['GuiScreen']};")
    set_unique_field('Minecraft.ingameGUI', mc_cls, f"L{R['GuiInGame']};")
    set_unique_field('Minecraft.objectMouseOver', mc_cls, f"L{R['MovingObjectPosition']};")
    set_unique_field('Minecraft.playerController', mc_cls, f"L{R['PlayerControllerMP']};")
    set_unique_field('Minecraft.renderManager', mc_cls, f"L{R['RenderManager']};")
    set_unique_field('Minecraft.gameSettings', mc_cls, f"L{R['GameSettings']};")
    set_unique_method('Minecraft.getThePlayer', mc_cls, f"()L{R['EntityPlayerSP']};")
    set_unique_method('Minecraft.getFontRendererObj', mc_cls, f"()L{R['FontRenderer']};")
    set_unique_method('Minecraft.getNetHandler', mc_cls, f"()L{R['NetHandlerPlayClient']};")
    if 'Timer' in R and 'TimerContainer' in R:
        tm_cls = R['Timer']
        tc_cls = R['TimerContainer']
        set_unique_field('Timer.timerSpeed', tm_cls, f'L{tc_cls};', static=True)
        if 'Timer.timerSpeed' not in M:
            set_unique_field('Timer.timerSpeed', tm_cls, f'L{tc_cls};', static=False)
        if 'Timer.timerSpeed' not in M:
            for m in methods_of(tm_cls, static=False, desc='()V'):
                ops = jvm.disasm(tm_cls, m['name'], '()V')
                tc_refs = [op[1][1] for op in ops if op[0] in ('getstatic', 'getfield') and op[1] and (op[1][0] == tm_cls) and (op[1][2] == f'L{tc_cls};')]
                if tc_refs:
                    M['Timer.timerSpeed'] = (tc_refs[-1], f'L{tc_cls};')
                    break
        for m in methods_of(tc_cls, static=False, desc='()D'):
            ops = jvm.disasm(tc_cls, m['name'], '()D')
            if any((op[0] == 'invokestatic' and op[1] and (op[1][:2] == ('java/lang/Double', 'longBitsToDouble')) for op in ops)):
                M['TimerContainer.getValue'] = (m['name'], '()D')
                j_gfs = [op[1][1] for op in ops if op[0] == 'getfield' and op[1] and (op[1][0] == tc_cls) and (op[1][2] == 'J')]
                j_gss = [op[1][1] for op in ops if op[0] == 'getstatic' and op[1] and (op[1][0] == tc_cls) and (op[1][2] == 'J')]
                if len(j_gfs) >= 3:
                    M['TimerContainer.valA'] = (j_gfs[0], 'J')
                    M['TimerContainer.valB'] = (j_gfs[1], 'J')
                    M['TimerContainer.xorKey'] = (j_gfs[2], 'J')
                if len(j_gss) >= 1:
                    M['TimerContainer.xorStatic'] = (j_gss[0], 'J')
                break
        for m in methods_of(tc_cls, static=False, desc='(D)V'):
            ops = jvm.disasm(tc_cls, m['name'], '(D)V')
            if any((op[0] == 'invokestatic' and op[1] and (op[1][:2] == ('java/lang/Double', 'doubleToLongBits')) for op in ops)):
                M['TimerContainer.setValue'] = (m['name'], '(D)V')
                break
    if 'MotionContainer' in R:
        dw_cls = R['MotionContainer']
        for m in methods_of(dw_cls, static=False, desc='()D'):
            if m['code_sz'] >= 30:
                M['MotionContainer.get'] = (m['name'], '()D')
                break
        for m in methods_of(dw_cls, static=False, desc='(D)D'):
            if m['code_sz'] >= 25:
                M['MotionContainer.set'] = (m['name'], '(D)D')
                break
    if 'BooleanContainer' in R:
        bc_cls = R['BooleanContainer']
        for m in methods_of(bc_cls, static=False, desc='()Z'):
            if m['code_sz'] >= 30:
                M['BooleanContainer.getValue'] = (m['name'], '()Z')
                break
    if 'FloatContainer' in R:
        fc_cls = R['FloatContainer']
        for m in methods_of(fc_cls, static=False, desc='()F'):
            if m['code_sz'] >= 30:
                M['FloatContainer.getFloatValue'] = (m['name'], '()F')
                break
    gs_cls = R['GameSettings']
    kb_cls = R['KeyBinding']
    for m in methods_of(kb_cls, static=False, desc='()Z'):
        ops = jvm.disasm(kb_cls, m['name'], '()Z')
        if len(ops) == 3 and ops[0] == ('aload', 0) and (ops[1][0] == 'getfield') and ops[1][1] and (ops[1][1][2] == 'Z') and (ops[2] == ('ireturn',)):
            M['KeyBinding.isKeyDown'] = (m['name'], '()Z')
            M['KeyBinding.pressed'] = (ops[1][1][1], 'Z')
        elif any((op[0] == 'getfield' and op[1] and (op[1][2] == 'I') for op in ops)) and ('iconst', 1) in ops:
            M['KeyBinding.isPressed'] = (m['name'], '()Z')
    for m in methods_of(kb_cls, static=True):
        if m['desc'] in (f'(L{mc_cls};IZ)V', '(IZ)V'):
            ops = jvm.disasm(kb_cls, m['name'], m['desc'])
            if 'KeyBinding.pressed' not in M or any((op[0] == 'putfield' and op[1] and (op[1][1] == M['KeyBinding.pressed'][0]) for op in ops)):
                M['KeyBinding.setKeyBindState'] = (m['name'], m['desc'])
                break
    KEY_DESC_TO_CONST = {'key.forward': 'GameSettings.keyBindForward', 'key.back': 'GameSettings.keyBindBack', 'key.left': 'GameSettings.keyBindLeft', 'key.right': 'GameSettings.keyBindRight', 'key.jump': 'GameSettings.keyBindJump', 'key.sneak': 'GameSettings.keyBindSneak', 'key.sprint': 'GameSettings.keyBindSprint'}
    if mc_oop and 'Minecraft.gameSettings' in M:
        gs_f = next((f for f in fields_of(mc_cls, static=False) if f['name'] == M['Minecraft.gameSettings'][0]), None)
        gs_oop = jvm.read_oop_field(mc_oop, gs_f['offset']) if gs_f else 0
        if gs_oop:
            kb_str_offs = [f['offset'] for f in fields_of(kb_cls, static=False, desc='Ljava/lang/String;')]
            for f in fields_of(gs_cls, static=False, desc=f'L{kb_cls};'):
                kb_oop = jvm.read_oop_field(gs_oop, f['offset'])
                if not kb_oop:
                    continue
                for soff in kb_str_offs:
                    s_val = jvm.read_jstring(jvm.read_oop_field(kb_oop, soff))
                    if s_val in KEY_DESC_TO_CONST:
                        M[KEY_DESC_TO_CONST[s_val]] = (f['name'], f'L{kb_cls};')
    ent_cls = R['Entity']
    set_unique_field('Entity.worldObj', ent_cls, f"L{R['World']};")
    set_unique_method('Entity.getDistanceToEntity', ent_cls, f'(L{ent_cls};)F')
    set_unique_method('Entity.rayTrace', ent_cls, f"(DF)L{R['MovingObjectPosition']};")
    set_unique_method('Entity.getFlag', ent_cls, '(I)Z')
    hc_ops = jvm.disasm(ent_cls, 'hashCode', '()I')
    for op in hc_ops:
        if op[0] == 'getfield' and op[1] and (op[1][2] == 'I'):
            M['Entity.entityId'] = (op[1][1], 'I')
            break
    ts_ops = jvm.disasm(ent_cls, 'toString', '()Ljava/lang/String;')
    saw_simple_name = False
    for op in ts_ops:
        if op[0] == 'invokevirtual' and op[1] and (op[1][:2] == ('java/lang/Class', 'getSimpleName')):
            saw_simple_name = True
        elif saw_simple_name and op[0] == 'invokevirtual' and op[1] and (op[1][0] == ent_cls) and (op[1][2] == '()Ljava/lang/String;'):
            M['Entity.getName'] = (op[1][1], '()Ljava/lang/String;')
            break
    ufs_desc = f"(DZL{R['Block']};L{R['BlockPos']};)V"
    for m in methods_of(ent_cls, static=False, desc=ufs_desc):
        ops = jvm.disasm(ent_cls, m['name'], ufs_desc)
        f_puts = [op[1][1] for op in ops if op[0] == 'putfield' and op[1] and (op[1][0] == ent_cls) and (op[1][2] == 'F')]
        if f_puts:
            M['Entity.fallDistance'] = (f_puts[0], 'F')
            break
    set_loc_angles_name = None
    dw_cls = R.get('MotionContainer', '')
    aabb_cls = R.get('AxisAlignedBB', '')
    for m in methods_of(ent_cls, static=False, desc='(DDD)V'):
        ops = jvm.disasm(ent_cls, m['name'], '(DDD)V')
        if any((op == ('new', aabb_cls) for op in ops)):
            d_puts = [op[1][1] for op in ops if op[0] == 'putfield' and op[1] and (op[1][0] == ent_cls) and (op[1][2] == 'D')]
            if len(d_puts) >= 3:
                M['Entity.posX'] = (d_puts[0], 'D')
                M['Entity.posY'] = (d_puts[1], 'D')
                M['Entity.posZ'] = (d_puts[2], 'D')
        if dw_cls:
            mc_gfs = [op[1][1] for op in ops if op[0] == 'getfield' and op[1] and (op[1][0] == ent_cls) and (op[1][2] == f'L{dw_cls};')]
            if len(mc_gfs) == 3 and len(set(mc_gfs)) == 3 and (m['code_sz'] <= 80):
                M['Entity.motionX'] = (mc_gfs[0], f'L{dw_cls};')
                M['Entity.motionY'] = (mc_gfs[1], f'L{dw_cls};')
                M['Entity.motionZ'] = (mc_gfs[2], f'L{dw_cls};')
        calls_dddff = [op[1][1] for op in ops if op[0] == 'invokevirtual' and op[1] and (op[1][0] == ent_cls) and (op[1][2] == '(DDDFF)V')]
        if len(calls_dddff) == 1 and m['code_sz'] <= 40:
            M['Entity.setPositionAndUpdate'] = (m['name'], '(DDD)V')
            set_loc_angles_name = calls_dddff[0]
            f_gfs = [op[1][1] for op in ops if op[0] == 'getfield' and op[1] and (op[1][0] == ent_cls) and (op[1][2] == 'F')]
            if len(f_gfs) == 2:
                M['Entity.rotationYaw'] = (f_gfs[0], 'F')
                M['Entity.rotationPitch'] = (f_gfs[1], 'F')
    prev_pos = []
    for m in methods_of(ent_cls, static=False, desc='(DDDFF)V'):
        if m['name'] != set_loc_angles_name:
            M['Entity.setPositionAndRotation'] = (m['name'], '(DDDFF)V')
            ops = jvm.disasm(ent_cls, m['name'], '(DDDFF)V')
            d_puts = [op[1][1] for op in ops if op[0] == 'putfield' and op[1] and (op[1][0] == ent_cls) and (op[1][2] == 'D')]
            if len(d_puts) >= 6:
                prev_pos = [d_puts[1], d_puts[3], d_puts[5]]
            f_puts = [op[1][1] for op in ops[:45] if op[0] == 'putfield' and op[1] and (op[1][0] == ent_cls) and (op[1][2] == 'F')]
            if len(f_puts) >= 4:
                yaw_n = M.get('Entity.rotationYaw', (f_puts[0],))[0]
                pitch_n = M.get('Entity.rotationPitch', (f_puts[2],))[0]
                M['Entity.rotationYaw'] = (yaw_n, 'F')
                M['Entity.rotationPitch'] = (pitch_n, 'F')
                yaw_pair = [x for x in f_puts[:2] if x != yaw_n]
                pitch_pair = [x for x in f_puts[2:4] if x != pitch_n]
                if yaw_pair:
                    M['Entity.prevRotationYaw'] = (yaw_pair[0], 'F')
                if pitch_pair:
                    M['Entity.prevRotationPitch'] = (pitch_pair[0], 'F')
    if set_loc_angles_name:
        ops = jvm.disasm(ent_cls, set_loc_angles_name, '(DDDFF)V')
        d_puts = [op[1][1] for op in ops if op[0] == 'putfield' and op[1] and (op[1][0] == ent_cls) and (op[1][2] == 'D')]
        if len(d_puts) >= 9:
            known_d = {M.get('Entity.posX', ('',))[0], M.get('Entity.posY', ('',))[0], M.get('Entity.posZ', ('',))[0], *prev_pos}
            lt_x = next((x for x in d_puts[0:3] if x not in known_d), d_puts[2])
            lt_y = next((x for x in d_puts[3:6] if x not in known_d), d_puts[5])
            lt_z = next((x for x in d_puts[6:9] if x not in known_d), d_puts[8])
            M['Entity.lastTickPosX'] = (lt_x, 'D')
            M['Entity.lastTickPosY'] = (lt_y, 'D')
            M['Entity.lastTickPosZ'] = (lt_z, 'D')
    vec3_cls = R['Vec3']
    for m in methods_of(ent_cls, static=False, desc=f'(F)L{vec3_cls};'):
        ops = jvm.disasm(ent_cls, m['name'], f'(F)L{vec3_cls};')
        if any((op == ('new', vec3_cls) for op in ops)):
            for idx, op in enumerate(ops):
                if op[0] == 'getfield' and op[1] and (op[1][1] == M.get('Entity.posY', ('',))[0]):
                    for nxt_op in ops[idx + 1:idx + 5]:
                        if nxt_op[0] == 'invokevirtual' and nxt_op[1] and (nxt_op[1][2] == '()F'):
                            M['Entity.getEyeHeight'] = (nxt_op[1][1], '()F')
                            break
                if 'Entity.getEyeHeight' in M:
                    break
    sp_cls = R['EntityPlayerSP']
    bc_cls = R.get('BooleanContainer', '')
    c03_cls = R.get('C03PacketPlayer', '')
    if bc_cls and c03_cls:
        for m in methods_of(sp_cls, static=False, desc='()V'):
            ops = jvm.disasm(sp_cls, m['name'], '()V')
            if any((op == ('new', c03_cls) for op in ops)):
                bc_gfs = [op[1][1] for op in ops if op[0] == 'getfield' and op[1] and (op[1][2] == f'L{bc_cls};')]
                ent_bc_names = {f['name'] for f in fields_of(ent_cls, static=False, desc=f'L{bc_cls};')}
                hits = [fn for fn in bc_gfs if fn in ent_bc_names]
                if hits:
                    M['Entity.onGround'] = (hits[0], f'L{bc_cls};')
                    break
    elb_cls = R['EntityLivingBase']
    for m in methods_of(elb_cls, static=False, desc='(Z)V'):
        ops = jvm.disasm(elb_cls, m['name'], '(Z)V')
        if any((op[0] == 'invokespecial' and op[1] and (op[1][0] == ent_cls) and (op[1][2] == '(Z)V') for op in ops)) and any((op[0] == 'getstatic' and op[1] and (op[1][2] == 'Ljava/util/UUID;') for op in ops)):
            M['EntityLivingBase.setSprinting'] = (m['name'], '(Z)V')
            break
    for m in methods_of(elb_cls, static=False, desc='(FF)F'):
        ops = jvm.disasm(elb_cls, m['name'], '(FF)F')
        elb_f_names = {f['name'] for f in fields_of(elb_cls, static=False, desc='F')}
        f_puts = [op[1][1] for op in ops if op[0] == 'putfield' and op[1] and (op[1][1] in elb_f_names)]
        if f_puts:
            M['EntityLivingBase.renderYawOffset'] = (f_puts[0], 'F')
            break
    ent_f_methods = {m['name'] for m in methods_of(ent_cls, static=False, desc='()F')}
    for m in methods_of(elb_cls, static=False, desc='()F'):
        if m['name'] in ent_f_methods:
            ops = jvm.disasm(elb_cls, m['name'], '()F')
            if len(ops) == 3 and ops[0] == ('aload', 0) and (ops[1][0] == 'getfield') and ops[1][1] and (ops[1][1][0] == elb_cls) and (ops[1][1][2] == 'F'):
                M['EntityLivingBase.rotationYawHead'] = (ops[1][1][1], 'F')
                break
    dw_data_cls = R.get('DataWatcher', '')
    for m in methods_of(elb_cls, static=False, desc='()F'):
        if m['code_sz'] <= 96:
            ops = jvm.disasm(elb_cls, m['name'], '()F')
            uses_dw = any((op[0] == 'getfield' and op[1] and (op[1][2] == f'L{dw_data_cls};') for op in ops)) if dw_data_cls else any((op[0] == 'invokevirtual' and op[1] and (op[1][2] == '(I)F') for op in ops))
            has_fdiv = any((op == ('op_0x6e',) for op in ops))
            if uses_dw and (not has_fdiv):
                M['EntityLivingBase.getHealth'] = (m['name'], '()F')
                break
    decremented_i = set()
    paired_hurt_i = set()
    for m in methods_of(elb_cls, static=False):
        ops = jvm.disasm(elb_cls, m['name'], m['desc'])
        for idx, op in enumerate(ops):
            if op[0] == 'putfield' and op[1] and (op[1][0] == elb_cls) and (op[1][2] == 'I'):
                fn = op[1][1]
                window = ops[max(0, idx - 4):idx]
                if ('iconst', 1) in window and ('op_0x64',) in window:
                    decremented_i.add(fn)
                if idx >= 1 and ops[idx - 1][0] == 'putfield' and ops[idx - 1][1] and (ops[idx - 1][1][2] == 'I'):
                    paired_hurt_i.add(fn)
    hurt_hits = paired_hurt_i & decremented_i
    if len(hurt_hits) == 1:
        M['EntityLivingBase.hurtTime'] = (next(iter(hurt_hits)), 'I')
    elif len(paired_hurt_i) == 1:
        M['EntityLivingBase.hurtTime'] = (next(iter(paired_hurt_i)), 'I')
    s0b_cls = R.get('S0BPacketAnimation', '')
    for m in methods_of(elb_cls, static=False, desc='()V'):
        if m['code_sz'] <= 120:
            ops = jvm.disasm(elb_cls, m['name'], '()V')
            if s0b_cls and any((op == ('new', s0b_cls) for op in ops)):
                M['EntityLivingBase.swingItem'] = (m['name'], '()V')
                break
    mop_desc = f"L{R['MovingObjectPosition']};"
    pc_desc = f"L{R['PlayerControllerMP']};"
    for m in methods_of(mc_cls, static=False, desc='(Z)V'):
        ops = jvm.disasm(mc_cls, m['name'], '(Z)V')
        gfs = [op[1] for op in ops if op[0] == 'getfield' and op[1]]
        if any((g[2] == mop_desc for g in gfs)) and any((g[2] == pc_desc for g in gfs)):
            M['Minecraft.rightClickMouse'] = (m['name'], '(Z)V')
            for op in ops:
                if op[0] == 'putfield' and op[1] and (op[1][0] == mc_cls) and (op[1][2] == 'I'):
                    M['Minecraft.rightClickDelayTimer'] = (op[1][1], 'I')
                    break
            break
    swing_name = M.get('EntityLivingBase.swingItem', ('',))[0]
    for m in methods_of(mc_cls, static=False, desc='()V'):
        if 150 <= m['code_sz'] <= 700:
            ops = jvm.disasm(mc_cls, m['name'], '()V')
            gfs = [op[1] for op in ops if op[0] == 'getfield' and op[1]]
            calls = [op[1] for op in ops if op[0] == 'invokevirtual' and op[1]]
            if any((g[2] == mop_desc for g in gfs)) and (not swing_name or any((c[1] == swing_name and c[2] == '()V' for c in calls))):
                M['Minecraft.clickMouse'] = (m['name'], '()V')
                for op in ops:
                    if op[0] in ('getfield', 'putfield') and op[1] and (op[1][0] == mc_cls) and (op[1][2] == 'I'):
                        M['Minecraft.leftClickCounter'] = (op[1][1], 'I')
                        break
                break
    ep_cls = R['EntityPlayer']
    cont_cls = R['Container']
    ip_cls = R['InventoryPlayer']
    is_cls = R['ItemStack']
    ei_cls = R['EntityItem']
    set_unique_field('EntityPlayer.inventory', ep_cls, f'L{ip_cls};')
    set_unique_method('EntityPlayer.dropOneItem', ep_cls, f'(Z)L{ei_cls};')
    for m in classes[ep_cls]['methods']:
        if m['name'] == '<init>':
            ops = jvm.disasm(ep_cls, '<init>', m['desc'])
            c_puts = [op[1][1] for op in ops if op[0] == 'putfield' and op[1] and (op[1][0] == ep_cls) and (op[1][2] == f'L{cont_cls};')]
            if len(c_puts) >= 2 and c_puts[0] != c_puts[1]:
                M['EntityPlayer.inventoryContainer'] = (c_puts[0], f'L{cont_cls};')
                M['EntityPlayer.openContainer'] = (c_puts[1], f'L{cont_cls};')
                break
    if 'EntityPlayer.openContainer' in M and 'EntityPlayer.inventoryContainer' in M:
        for m in methods_of(ep_cls, static=False, desc='()V'):
            if m['code_sz'] <= 30:
                ops = jvm.disasm(ep_cls, m['name'], '()V')
                if any((op[0] == 'putfield' and op[1] and (op[1][1] == M['EntityPlayer.openContainer'][0]) for op in ops)) and any((op[0] == 'getfield' and op[1] and (op[1][1] == M['EntityPlayer.inventoryContainer'][0]) for op in ops)):
                    M['EntityPlayer.closeScreen'] = (m['name'], '()V')
                    break
    elb_is_methods = {m['name'] for m in methods_of(elb_cls, static=False, desc=f'()L{is_cls};')}
    held_cands = []
    ip_get_curr_item_m = ''
    for m in methods_of(ep_cls, static=False, desc=f'()L{is_cls};'):
        ops = jvm.disasm(ep_cls, m['name'], f'()L{is_cls};')
        if len(ops) <= 10 and any((op[0] == 'getfield' and op[1] and (op[1][2] == f'L{ip_cls};') for op in ops)):
            held_cands.append(m['name'])
            for op in ops:
                if op[0] == 'invokevirtual' and op[1] and (op[1][0] == ip_cls) and (op[1][2] == f'()L{is_cls};'):
                    ip_get_curr_item_m = op[1][1]
    if held_cands:
        chosen_held = next((mn for mn in held_cands if mn in elb_is_methods), held_cands[0])
        M['EntityPlayer.getHeldItem'] = (chosen_held, f'()L{is_cls};')
    acp_cls = R['AbstractClientPlayer']
    npi_cls = R['NetworkPlayerInfo']
    rl_cls = R['ResourceLocation']
    set_unique_field('AbstractClientPlayer.playerInfo', acp_cls, f'L{npi_cls};')
    for m in methods_of(acp_cls, static=False, desc=f'()L{rl_cls};'):
        ops = jvm.disasm(acp_cls, m['name'], f'()L{rl_cls};')
        has_null_ret = any((ops[i] == ('aconst_null',) and i + 1 < len(ops) and (ops[i + 1] == ('areturn',)) for i in range(len(ops))))
        calls_npi = any((op[0] == 'invokevirtual' and op[1] and (op[1][0] == npi_cls) and (op[1][2] == f'()L{rl_cls};') for op in ops))
        if calls_npi and (not has_null_ret):
            M['AbstractClientPlayer.getLocationSkin'] = (m['name'], f'()L{rl_cls};')
            for op in ops:
                if op[0] == 'invokevirtual' and op[1] and (op[1][0] == npi_cls) and (op[1][2] == f'()L{rl_cls};'):
                    M['NetworkPlayerInfo.getLocationSkin'] = (op[1][1], f'()L{rl_cls};')
                    break
            break
    nh_cls = R['NetHandlerPlayClient']
    icc_cls = R['IChatComponent']
    c01_cls = R.get('C01PacketChatMessage', '')
    set_unique_field('EntityPlayerSP.sendQueue', sp_cls, f'L{nh_cls};')
    set_unique_method('EntityPlayerSP.addChatMessage', sp_cls, f'(L{icc_cls};)V')
    if 'EntityPlayerSP.addChatMessage' not in M:
        ent_icc_m = {m['name'] for m in classes[ent_cls]['methods'] if m['desc'] == f'(L{icc_cls};)V'}
        sp_icc_cands = [m['name'] for m in methods_of(sp_cls, static=False, desc=f'(L{icc_cls};)V')]
        if sp_icc_cands:
            chosen_chat = next((mn for mn in sp_icc_cands if mn in ent_icc_m), sp_icc_cands[0])
            M['EntityPlayerSP.addChatMessage'] = (chosen_chat, f'(L{icc_cls};)V')
    for m in methods_of(sp_cls, static=False, desc='(Ljava/lang/String;)V'):
        ops = jvm.disasm(sp_cls, m['name'], '(Ljava/lang/String;)V')
        if not c01_cls or any((op == ('new', c01_cls) for op in ops)):
            M['EntityPlayerSP.sendChatMessage'] = (m['name'], '(Ljava/lang/String;)V')
            break
    if ei_cls in classes:
        set_unique_method('EntityItem.getEntityItem', ei_cls, f'()L{is_cls};')
    if 'EntityItem.getEntityItem' not in M:
        cp_hits = [mn for mn, md in jvm.cp_methods.get(ei_cls, set()) if md == f'()L{is_cls};']
        if len(cp_hits) == 1:
            M['EntityItem.getEntityItem'] = (cp_hits[0], f'()L{is_cls};')
    for m in classes[ip_cls]['methods']:
        if m['name'] == '<init>':
            ops = jvm.disasm(ip_cls, '<init>', m['desc'])
            for idx, op in enumerate(ops):
                if op[0] == 'putfield' and op[1] and (op[1][2] == f'[L{is_cls};'):
                    prev_ops = ops[max(0, idx - 4):idx]
                    if ('bipush', 36) in prev_ops:
                        M['InventoryPlayer.mainInventory'] = (op[1][1], f'[L{is_cls};')
                    elif ('iconst', 4) in prev_ops:
                        M['InventoryPlayer.armorInventory'] = (op[1][1], f'[L{is_cls};')
    set_unique_field('InventoryPlayer.currentItem', ip_cls, 'I')
    if 'InventoryPlayer.currentItem' not in M:
        cand_ms = [ip_get_curr_item_m] if ip_get_curr_item_m else [m['name'] for m in methods_of(ip_cls, static=False, desc=f'()L{is_cls};')]
        for mn in cand_ms:
            ops = jvm.disasm(ip_cls, mn, f'()L{is_cls};')
            if ('bipush', 9) in ops:
                for op in ops:
                    if op[0] == 'getfield' and op[1] and (op[1][0] == ip_cls) and (op[1][2] == 'I'):
                        M['InventoryPlayer.currentItem'] = (op[1][1], 'I')
                        break
            if 'InventoryPlayer.currentItem' in M:
                break
    slot_cls = R['Slot']
    set_unique_method('Container.getSlot', cont_cls, f'(I)L{slot_cls};')
    set_unique_field('Container.windowId', cont_cls, 'I')
    if 'Container.windowId' not in M:
        c0d_cls = R.get('C0DPacketCloseWindow', '')
        for m in methods_of(sp_cls, static=False, desc='()V'):
            ops = jvm.disasm(sp_cls, m['name'], '()V')
            if not c0d_cls or any((op == ('new', c0d_cls) for op in ops)):
                for op in ops:
                    if op[0] == 'getfield' and op[1] and (op[1][0] == cont_cls) and (op[1][2] == 'I'):
                        M['Container.windowId'] = (op[1][1], 'I')
                        break
            if 'Container.windowId' in M:
                break
    if 'Container.getSlot' in M:
        ops = jvm.disasm(cont_cls, M['Container.getSlot'][0], M['Container.getSlot'][1])
        for op in ops:
            if op[0] == 'getfield' and op[1] and (op[1][2] == 'Ljava/util/List;'):
                M['Container.inventorySlots'] = (op[1][1], 'Ljava/util/List;')
                break
    set_unique_method('Slot.getStack', slot_cls, f'()L{is_cls};')
    item_cls = R['Item']
    is_ctor_desc = f'(L{item_cls};II)V'
    ops_is = jvm.disasm(is_cls, '<init>', is_ctor_desc)
    for idx, op in enumerate(ops_is):
        if op[0] == 'putfield' and op[1] and (op[1][0] == is_cls):
            prev = ops_is[idx - 1] if idx > 0 else ()
            if prev == ('aload', 1) and op[1][2] == f'L{item_cls};':
                M['ItemStack.item'] = (op[1][1], f'L{item_cls};')
            elif prev == ('iload', 2) and op[1][2] == 'I':
                M['ItemStack.stackSize'] = (op[1][1], 'I')
            elif prev == ('iload', 3) and op[1][2] == 'I':
                M['ItemStack.itemDamage'] = (op[1][1], 'I')
    if 'ItemStack.itemDamage' in M:
        for m in methods_of(is_cls, static=False, desc='()I'):
            ops = jvm.disasm(is_cls, m['name'], '()I')
            if len(ops) == 3 and ops[0] == ('aload', 0) and (ops[1] == ('getfield', (is_cls, M['ItemStack.itemDamage'][0], 'I'))) and (ops[2] == ('ireturn',)):
                M['ItemStack.getMetadata'] = (m['name'], '()I')
                break
    nbt_cls = R.get('NBTTagCompound', '')
    for m in methods_of(is_cls, static=False, desc='()Ljava/lang/String;'):
        if m['name'] == 'toString':
            continue
        ops = jvm.disasm(is_cls, m['name'], '()Ljava/lang/String;')
        if ('bipush', 10) in ops and ('bipush', 8) in ops and (not nbt_cls or any((op[0] == 'getfield' and op[1] and (op[1][2] == f'L{nbt_cls};') for op in ops))):
            M['ItemStack.getDisplayName'] = (m['name'], '()Ljava/lang/String;')
            break
    for m in methods_of(item_cls, static=False, desc='()Ljava/lang/String;'):
        ops = jvm.disasm(item_cls, m['name'], '()Ljava/lang/String;')
        if any((op == ('new', 'java/lang/StringBuilder') for op in ops)) and any((op[0] == 'getfield' and op[1] and (op[1][0] == item_cls) and (op[1][2] == 'Ljava/lang/String;') for op in ops)) and (not any((op[0] == 'invokestatic' and op[1] and (op[1][2] == '(Ljava/lang/String;)Ljava/lang/String;') for op in ops))):
            M['Item.getUnlocalizedName'] = (m['name'], '()Ljava/lang/String;')
            break
    if 'EnchantmentHelper' in R:
        eh_cls = R['EnchantmentHelper']
        eh_desc = f'(IL{is_cls};)I'
        if eh_cls in classes:
            set_unique_method('EnchantmentHelper.getEnchantmentLevel', eh_cls, eh_desc, static=True)
        if 'EnchantmentHelper.getEnchantmentLevel' not in M:
            cp_hits = [mn for mn, md in jvm.cp_methods.get(eh_cls, set()) if md == eh_desc]
            if len(cp_hits) == 1:
                M['EnchantmentHelper.getEnchantmentLevel'] = (cp_hits[0], eh_desc)
    w_cls = R['World']
    blk_cls = R['Block']
    ibs_cls = R['IBlockState']
    bp_cls = R['BlockPos']
    ch_cls = R['Chunk']
    set_unique_method('World.getBlockState', w_cls, f'(L{bp_cls};)L{ibs_cls};')
    set_unique_method('Chunk.getBlock', ch_cls, f'(III)L{blk_cls};')
    if 'Chunk.getBlock' not in M:
        pub_gb = [m['name'] for m in methods_of(ch_cls, static=False, desc=f'(III)L{blk_cls};') if m['acc'] & 1]
        if pub_gb:
            M['Chunk.getBlock'] = (pub_gb[0], f'(III)L{blk_cls};')
    set_unique_method('Block.getIdFromBlock', blk_cls, f'(L{blk_cls};)I', static=True)
    set_unique_method('IBlockState.getBlock', ibs_cls, f'()L{blk_cls};')
    for m in methods_of(w_cls, static=False, desc=f'(L{ent_cls};)Z'):
        ops = jvm.disasm(w_cls, m['name'], f'(L{ent_cls};)Z')
        if any((op == ('instanceof', ep_cls) for op in ops)):
            saw_ep_inst = False
            lists_after_ep = []
            for op in ops:
                if op == ('instanceof', ep_cls):
                    saw_ep_inst = True
                elif saw_ep_inst and op[0] == 'getfield' and op[1] and (op[1][0] == w_cls) and (op[1][2] == 'Ljava/util/List;'):
                    if op[1][1] not in lists_after_ep:
                        lists_after_ep.append(op[1][1])
            if len(lists_after_ep) >= 2:
                M['World.playerEntities'] = (lists_after_ep[0], 'Ljava/util/List;')
                M['World.loadedEntityList'] = (lists_after_ep[1], 'Ljava/util/List;')
                break
    for m in methods_of(blk_cls, static=False, desc='()Ljava/lang/String;'):
        ops = jvm.disasm(blk_cls, m['name'], '()Ljava/lang/String;')
        if any((op == ('new', 'java/lang/StringBuilder') for op in ops)) and any((op[0] == 'getfield' and op[1] and (op[1][0] == blk_cls) and (op[1][2] == 'Ljava/lang/String;') for op in ops)):
            M['Block.getUnlocalizedName'] = (m['name'], '()Ljava/lang/String;')
            break
    if 'Block.getUnlocalizedName' in M:
        unloc_m = M['Block.getUnlocalizedName'][0]
        for m in methods_of(blk_cls, static=False, desc='()Ljava/lang/String;'):
            if m['name'] == unloc_m:
                continue
            ops = jvm.disasm(blk_cls, m['name'], '()Ljava/lang/String;')
            if any((op[0] == 'invokevirtual' and op[1] and (op[1][:2] == (blk_cls, unloc_m)) for op in ops)):
                M['Block.getLocalizedName'] = (m['name'], '()Ljava/lang/String;')
                break
    mop_cls = R['MovingObjectPosition']
    set_unique_field('MovingObjectPosition.entityHit', mop_cls, f'L{ent_cls};')
    set_unique_field('MovingObjectPosition.typeOfHit', mop_cls, f"L{R['MovingObjectType']};")
    set_unique_field('MovingObjectPosition.hitVec', mop_cls, f'L{vec3_cls};')
    set_unique_field('MovingObjectPosition.blockPos', mop_cls, f'L{bp_cls};')
    set_unique_field('MovingObjectPosition.sideHit', mop_cls, f"L{R['EnumFacing']};")
    pc_cls = R['PlayerControllerMP']
    set_unique_method('PlayerControllerMP.windowClick', pc_cls, f'(IIIIL{ep_cls};)L{is_cls};')
    c09_cls = R.get('C09PacketHeldItemChange', '')
    for m in methods_of(pc_cls, static=False, desc='()V'):
        ops = jvm.disasm(pc_cls, m['name'], '()V')
        if c09_cls and any((op == ('new', c09_cls) for op in ops)):
            M['PlayerControllerMP.syncCurrentPlayItem'] = (m['name'], '()V')
            break
    dmg_blk_desc = f"(L{bp_cls};L{R['EnumFacing']};)Z"
    for m in methods_of(pc_cls, static=False, desc=dmg_blk_desc):
        ops = jvm.disasm(pc_cls, m['name'], dmg_blk_desc)
        for idx, op in enumerate(ops):
            if op[0] == 'putfield' and op[1] and (op[1][0] == pc_cls) and (op[1][2] == 'I'):
                win = ops[max(0, idx - 4):idx]
                if ('iconst', 1) in win and ('op_0x64',) in win:
                    M['PlayerControllerMP.blockHitDelay'] = (op[1][1], 'I')
                    break
        if 'PlayerControllerMP.blockHitDelay' in M:
            break
    rm_cls = R['RenderManager']
    for m in methods_of(rm_cls, static=False, desc='(DDD)V'):
        ops = jvm.disasm(rm_cls, m['name'], '(DDD)V')
        d_puts = [op[1][1] for op in ops if op[0] == 'putfield' and op[1] and (op[1][0] == rm_cls) and (op[1][2] == 'D')]
        if len(d_puts) == 3:
            M['RenderManager.renderPosX'] = (d_puts[0], 'D')
            M['RenderManager.renderPosY'] = (d_puts[1], 'D')
            M['RenderManager.renderPosZ'] = (d_puts[2], 'D')
            break
    for m in methods_of(rm_cls, static=False):
        if f'L{w_cls};' in m['desc'] and f'L{gs_cls};' in m['desc']:
            ops = jvm.disasm(rm_cls, m['name'], m['desc'])
            f_puts = []
            d_puts = []
            for op in ops:
                if op[0] == 'putfield' and op[1] and (op[1][0] == rm_cls):
                    if op[1][2] == 'F' and op[1][1] not in f_puts:
                        f_puts.append(op[1][1])
                    elif op[1][2] == 'D' and op[1][1] not in d_puts:
                        d_puts.append(op[1][1])
            if len(f_puts) >= 2:
                M['RenderManager.playerViewY'] = (f_puts[0], 'F')
                M['RenderManager.playerViewX'] = (f_puts[1], 'F')
            if len(d_puts) >= 3:
                M['RenderManager.viewerPosX'] = (d_puts[0], 'D')
                M['RenderManager.viewerPosY'] = (d_puts[1], 'D')
                M['RenderManager.viewerPosZ'] = (d_puts[2], 'D')
            break
    fr_cls = R['FontRenderer']
    set_unique_method('FontRenderer.drawString', fr_cls, '(Ljava/lang/String;FFIZ)I')
    for m in methods_of(fr_cls, static=False, desc='(Ljava/lang/String;)I'):
        ops = jvm.disasm(fr_cls, m['name'], '(Ljava/lang/String;)I')
        if any((op[0] == 'invokestatic' and op[1] and (op[1][:2] == ('java/lang/Math', 'round')) for op in ops)) or any((op[0] == 'invokevirtual' and op[1] and (op[1][0] == fr_cls) and (op[1][2] == '(Ljava/lang/String;)F') for op in ops)):
            M['FontRenderer.getStringWidth'] = (m['name'], '(Ljava/lang/String;)I')
            break
    nm_cls = R['NetworkManager']
    gp_cls = R['GameProfile']
    set_unique_field('NetHandlerPlayClient.networkManager', nh_cls, f'L{nm_cls};')
    set_unique_method('NetHandlerPlayClient.sendPacket', nh_cls, f"(L{R['Packet']};)V")
    set_unique_field('NetworkManager.channel', nm_cls, 'Lio/netty/channel/Channel;')
    set_unique_method('GameProfile.getUUID', gp_cls, '()Ljava/util/UUID;')
    set_unique_method('GameProfile.getName', gp_cls, '()Ljava/lang/String;')
    if 'GameProfile.getName' not in M:
        for m in methods_of(gp_cls, static=False, desc='()Ljava/lang/String;'):
            if m['name'] == 'toString':
                continue
            ops = jvm.disasm(gp_cls, m['name'], '()Ljava/lang/String;')
            if len(ops) == 3 and ops[0] == ('aload', 0) and (ops[1][0] == 'getfield') and ops[1][1] and (ops[1][1][0] == gp_cls) and (ops[1][1][2] == 'Ljava/lang/String;') and (ops[2] == ('areturn',)):
                M['GameProfile.getName'] = (m['name'], '()Ljava/lang/String;')
                break
    if npi_cls in classes:
        set_unique_method('NetworkPlayerInfo.getGameProfile', npi_cls, f'()L{gp_cls};')
        set_unique_method('NetworkPlayerInfo.getDisplayName', npi_cls, f'()L{icc_cls};')
        tab_cls = R.get('GuiPlayerTabOverlay', '')
        if tab_cls and tab_cls in classes:
            for tm in methods_of(tab_cls, static=False, desc=f'(IIIL{npi_cls};)V'):
                ops = jvm.disasm(tab_cls, tm['name'], tm['desc'])
                for op in ops:
                    if op[0] == 'invokevirtual' and op[1] and (op[1][0] == npi_cls) and (op[1][2] == '()I'):
                        M['NetworkPlayerInfo.getResponseTime'] = (op[1][1], '()I')
                        break
        if 'NetworkPlayerInfo.getResponseTime' in M:
            ops = jvm.disasm(npi_cls, M['NetworkPlayerInfo.getResponseTime'][0], '()I')
            for op in ops:
                if op[0] == 'getfield' and op[1] and (op[1][0] == npi_cls) and (op[1][2] == 'I'):
                    M['NetworkPlayerInfo.responseTime'] = (op[1][1], 'I')
                    break
        else:
            init_put_i = set()
            for im in classes[npi_cls]['methods']:
                if im['name'] == '<init>':
                    for op in jvm.disasm(npi_cls, '<init>', im['desc']):
                        if op[0] == 'putfield' and op[1] and (op[1][2] == 'I'):
                            init_put_i.add(op[1][1])
            for gm in methods_of(npi_cls, static=False, desc='()I'):
                ops = jvm.disasm(npi_cls, gm['name'], '()I')
                if len(ops) == 3 and ops[1][0] == 'getfield' and ops[1][1] and (ops[1][1][1] not in init_put_i):
                    M['NetworkPlayerInfo.getResponseTime'] = (gm['name'], '()I')
                    M['NetworkPlayerInfo.responseTime'] = (ops[1][1][1], 'I')
                    break
    else:
        npi_cpm = jvm.cp_methods.get(npi_cls, set())
        gp_hits = [mn for mn, md in npi_cpm if md == f'()L{gp_cls};']
        if len(gp_hits) == 1:
            M['NetworkPlayerInfo.getGameProfile'] = (gp_hits[0], f'()L{gp_cls};')
        dn_hits = [mn for mn, md in npi_cpm if md == f'()L{icc_cls};']
        if len(dn_hits) == 1:
            M['NetworkPlayerInfo.getDisplayName'] = (dn_hits[0], f'()L{icc_cls};')
        tab_cls = R.get('GuiPlayerTabOverlay', '')
        if tab_cls and tab_cls in classes:
            for tm in methods_of(tab_cls, static=False, desc=f'(IIIL{npi_cls};)V'):
                for op in jvm.disasm(tab_cls, tm['name'], tm['desc']):
                    if op[0] == 'invokevirtual' and op[1] and (op[1][0] == npi_cls) and (op[1][2] == '()I'):
                        M['NetworkPlayerInfo.getResponseTime'] = (op[1][1], '()I')
                        break

    def lookup_live_meta(cls_slash, kind, obf_name, desc):
        cur = cls_slash
        while cur and cur in classes:
            info = classes[cur]
            if kind == 'f':
                for f in info['fields']:
                    if f['name'] == obf_name and f['desc'] == desc:
                        return {'owner': cur, 'desc': f['desc'], 'offset': f['offset'], 'static': f['static']}
            else:
                for m in info['methods']:
                    if m['name'] == obf_name and m['desc'] == desc:
                        return {'owner': cur, 'desc': m['desc'], 'offset': None, 'static': m['static'], 'mp': m.get('mp', 0), 'code_sz': m.get('code_sz', 0)}
                for ifc in info['interfaces']:
                    if ifc in classes:
                        for m in classes[ifc]['methods']:
                            if m['name'] == obf_name and m['desc'] == desc:
                                return {'owner': ifc, 'desc': m['desc'], 'offset': None, 'static': m['static'], 'mp': m.get('mp', 0), 'code_sz': m.get('code_sz', 0)}
            cur = info['super']
        return {'owner': cls_slash, 'desc': desc, 'offset': None, 'static': False, 'mp': 0, 'code_sz': 0}
    out_members = {}
    out_meta = {}
    missing = []
    for const_name, (kind, blk, deobf) in TARGET_MEMBERS.items():
        if const_name not in M or blk not in R:
            missing.append(const_name)
            continue
        obf_name, desc = M[const_name]
        out_members[const_name] = (kind, blk, deobf, obf_name, desc)
        out_meta[const_name] = lookup_live_meta(R[blk], kind, obf_name, desc)
    return (out_members, out_meta, missing)
