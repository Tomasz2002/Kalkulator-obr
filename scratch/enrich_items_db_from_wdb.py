import struct, re, json, os

with open('data/Spell.dbc', 'rb') as f:
    header = f.read(20)
    magic, rec_count, field_count, rec_size, string_size = struct.unpack('<4sIIII', header)
    data = f.read(rec_count * rec_size)
    strings = f.read(string_size)

def get_str(offset):
    if offset <= 0 or offset >= len(strings):
        return ''
    end = strings.find(b'\x00', offset)
    if end == -1: end = len(strings)
    return strings[offset:end].decode('utf-8', errors='ignore')

spells_info = {}
for i in range(rec_count):
    row = data[i * rec_size : (i + 1) * rec_size]
    vals = struct.unpack(f'<{field_count}i', row)
    sid = vals[0]
    name = get_str(vals[120])
    desc = get_str(vals[138])
    bp = [vals[76], vals[77], vals[78]]
    spells_info[sid] = {'name': name, 'desc': desc, 'bp': bp}

def format_spell_text(spell_id, trigger):
    sp = spells_info.get(spell_id)
    if not sp: return ''
    desc = sp['desc']
    if not desc: desc = sp['name']
    for idx, bp_val in enumerate(sp['bp']):
        token = f"$s{idx+1}"
        desc = desc.replace(token, str(bp_val + 1))
    desc = re.sub(r'\$[a-zA-Z0-9]+', '', desc)
    desc = re.sub(r'\/[a-zA-Z0-9]+', '', desc)
    desc = desc.strip()
    if not desc: return ''
    if trigger == 1: prefix = "Equip: "
    elif trigger == 2: prefix = "Chance on hit: "
    elif trigger == 0: prefix = "Use: "
    else: prefix = ""
    return prefix + desc

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

with open('data/item_icons.json', 'r', encoding='utf-8') as f:
    icons_map = json.load(f)

INV_TYPE_MAP = {
    1: 'head', 2: 'neck', 3: 'shoulder', 4: 'shirt', 5: 'chest',
    6: 'waist', 7: 'legs', 8: 'feet', 9: 'wrist', 10: 'hands',
    11: 'finger', 12: 'trinket', 13: 'onehand', 14: 'offhand',
    15: 'ranged', 16: 'back', 17: 'twohand', 20: 'chest',
    21: 'mainhand', 22: 'offhand', 23: 'offhand', 25: 'ranged',
    26: 'ranged', 28: 'relic'
}

ARMOR_SUBCLASS = {
    0: 'misc', 1: 'cloth', 2: 'leather', 3: 'mail', 4: 'plate',
    6: 'shield', 7: 'libram', 8: 'idol', 9: 'totem'
}

WEAPON_SUBCLASS = {
    0: 'one_hand_axe', 1: 'two_hand_axe', 2: 'bow', 3: 'gun',
    4: 'one_hand_mace', 5: 'two_hand_mace', 6: 'polearm',
    7: 'one_hand_sword', 8: 'two_hand_sword', 10: 'staff',
    13: 'fist', 14: 'misc', 15: 'dagger', 18: 'crossbow', 19: 'wand'
}

CLASS_MASKS = {
    1: 'warrior', 2: 'paladin', 4: 'hunter', 8: 'rogue',
    16: 'priest', 64: 'shaman', 128: 'mage', 256: 'warlock', 1024: 'druid'
}

ALL_CLASSES = ['warrior', 'paladin', 'hunter', 'rogue', 'priest', 'shaman', 'mage', 'warlock', 'druid']

def resolve_classes(mask, item_class, subclass):
    if mask not in (-1, 0, 32767, 65535):
        cls = [cname for bit, cname in CLASS_MASKS.items() if mask & bit]
        if cls: return cls
    if item_class == 4:
        if subclass == 'plate': return ['warrior', 'paladin']
        if subclass == 'mail': return ['warrior', 'paladin', 'hunter', 'shaman']
        if subclass == 'leather': return ['warrior', 'paladin', 'hunter', 'rogue', 'shaman', 'druid']
        if subclass == 'shield': return ['warrior', 'paladin', 'shaman']
        if subclass == 'libram': return ['paladin']
        if subclass == 'idol': return ['druid']
        if subclass == 'totem': return ['shaman']
        return ALL_CLASSES
    if item_class == 2:
        if subclass in ('bow', 'gun', 'crossbow'): return ['warrior', 'hunter', 'rogue']
        if subclass == 'wand': return ['priest', 'mage', 'warlock']
        if subclass == 'polearm': return ['warrior', 'paladin', 'hunter']
        if subclass == 'two_hand_mace': return ['warrior', 'paladin', 'shaman', 'druid']
        if subclass == 'two_hand_axe': return ['warrior', 'paladin', 'hunter', 'shaman']
        if subclass == 'two_hand_sword': return ['warrior', 'paladin', 'hunter']
        if subclass == 'one_hand_mace': return ['warrior', 'paladin', 'rogue', 'priest', 'shaman', 'druid']
        if subclass == 'one_hand_sword': return ['warrior', 'paladin', 'hunter', 'rogue', 'mage', 'warlock']
        if subclass == 'one_hand_axe': return ['warrior', 'hunter', 'rogue', 'shaman']
        if subclass == 'dagger': return ['warrior', 'hunter', 'rogue', 'priest', 'shaman', 'mage', 'warlock', 'druid']
        if subclass == 'staff': return ['warrior', 'hunter', 'priest', 'shaman', 'mage', 'warlock', 'druid']
        if subclass == 'fist': return ['warrior', 'hunter', 'rogue', 'shaman', 'druid']
        return ALL_CLASSES
    return ALL_CLASSES

with open('data/itemcache.wdb', 'rb') as f:
    wdb_bytes = f.read()

offset = 20
new_items_count = 0
while offset < len(wdb_bytes):
    if offset + 8 > len(wdb_bytes): break
    entry, size = struct.unpack('<II', wdb_bytes[offset:offset+8])
    if size == 0: break
    chunk = wdb_bytes[offset+8:offset+8+size]
    offset += 8 + size

    if str(entry) in db['by_id']:
        continue

    item_class, item_subclass_id = struct.unpack('<2I', chunk[:8])
    pos = 8
    names = []
    for _ in range(4):
        end = chunk.find(b'\x00', pos)
        names.append(chunk[pos:end].decode('utf-8', errors='ignore'))
        pos = end + 1
    name = names[0]
    fixed = chunk[pos:]
    if len(fixed) < 440: continue
    ints = struct.unpack(f'<{len(fixed)//4}i', fixed[:(len(fixed)//4)*4])
    floats = struct.unpack(f'<{len(fixed)//4}f', fixed[:(len(fixed)//4)*4])

    display_id = ints[0]
    quality = ints[1]
    flags = ints[2]
    inv_type = ints[5]
    allowable_class = ints[6]
    allowable_race = ints[7]
    item_level = ints[8]
    req_level = ints[9]

    if inv_type not in INV_TYPE_MAP:
        continue

    slot = INV_TYPE_MAP[inv_type]
    subclass = ''
    if item_class == 4:
        subclass = ARMOR_SUBCLASS.get(item_subclass_id, 'misc')
    elif item_class == 2:
        subclass = WEAPON_SUBCLASS.get(item_subclass_id, 'misc')

    strength = 0
    agility = 0
    stamina = 0
    intellect = 0
    spirit = 0

    for s_idx in range(10):
        st_type = ints[20 + s_idx * 2]
        st_val = ints[20 + s_idx * 2 + 1]
        if st_type == 4: strength += st_val
        elif st_type == 3: agility += st_val
        elif st_type == 7: stamina += st_val
        elif st_type == 5: intellect += st_val
        elif st_type == 6: spirit += st_val

    dmg_min = floats[40] if len(floats) > 40 else 0.0
    dmg_max = floats[41] if len(floats) > 41 else 0.0
    delay = (ints[62] / 1000.0) if len(ints) > 62 and ints[62] > 0 else 0.0
    armor = ints[55] if len(ints) > 55 else 0

    holy_res = ints[56] if len(ints) > 56 else 0
    fire_res = ints[57] if len(ints) > 57 else 0
    nature_res = ints[58] if len(ints) > 58 else 0
    frost_res = ints[59] if len(ints) > 59 else 0
    shadow_res = ints[60] if len(ints) > 60 else 0
    arcane_res = ints[61] if len(ints) > 61 else 0

    dps = round(((dmg_min + dmg_max) / 2.0) / delay, 1) if delay > 0 else 0.0

    spells = []
    attack_power = 0
    spell_power = 0
    healing = 0
    crit = 0.0
    hit = 0.0

    for sp_i in range(5):
        s_id = ints[65 + sp_i * 7]
        s_trig = ints[65 + sp_i * 7 + 1]
        if s_id > 0:
            s_text = format_spell_text(s_id, s_trig)
            if s_text:
                spells.append({'spell_id': s_id, 'trigger': s_trig, 'text': s_text})
                m_ap = re.search(r'attack power by (\d+)', s_text, re.I)
                if m_ap: attack_power += int(m_ap.group(1))
                m_sp = re.search(r'damage and healing done by (?:magical spells and effects|all magical spells and effects) by up to (\d+)', s_text, re.I)
                if m_sp: spell_power += int(m_sp.group(1))
                m_heal = re.search(r'healing done by spells and effects by up to (\d+)', s_text, re.I)
                if m_heal: healing += int(m_heal.group(1))
                m_crit = re.search(r'(?:critical strike|critical) by (\d+)%', s_text, re.I)
                if m_crit: crit += float(m_crit.group(1))
                m_hit = re.search(r'chance to hit by (\d+)%', s_text, re.I)
                if m_hit: hit += float(m_hit.group(1))

    bonding = ints[100] if len(ints) > 100 else 0
    set_id = 0
    for s_id_cand, s_data in db.get('sets', {}).items():
        if entry in s_data.get('pieces', []):
            set_id = int(s_id_cand)
            break

    resistances = {}
    if holy_res > 0: resistances['holy'] = holy_res
    if fire_res > 0: resistances['fire'] = fire_res
    if nature_res > 0: resistances['nature'] = nature_res
    if frost_res > 0: resistances['frost'] = frost_res
    if shadow_res > 0: resistances['shadow'] = shadow_res
    if arcane_res > 0: resistances['arcane'] = arcane_res

    classes = resolve_classes(allowable_class, item_class, subclass)
    icon = icons_map.get(str(entry), "")

    item_obj = {
        'id': entry,
        'name': name,
        'icon': icon,
        'slot': slot,
        'subclass': subclass,
        'quality': quality,
        'item_level': item_level,
        'req_level': req_level,
        'armor': armor,
        'durability': 0,
        'unique': bool(flags & 1),
        'bonding': bonding,
        'speed': delay,
        'min_damage': dmg_min,
        'max_damage': dmg_max,
        'dps': dps,
        'strength': strength,
        'agility': agility,
        'stamina': stamina,
        'intellect': intellect,
        'spirit': spirit,
        'resistances': resistances,
        'attack_power': attack_power,
        'spell_power': spell_power,
        'healing': healing,
        'crit': crit,
        'hit': hit,
        'spells': spells,
        'set': None,
        'set_id': set_id,
        'classes': classes
    }

    db['items'].append(item_obj)
    db['by_id'][str(entry)] = item_obj
    db['by_slot'].setdefault(slot, []).append(item_obj)
    new_items_count += 1

print(f"Added {new_items_count} new equipment items from WDB!")
db['metadata']['total_items'] = len(db['items'])

with open('items_db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2)

print("Saved updated items_db.json!")
print("Check 47242:", db['by_id'].get('47242'))
