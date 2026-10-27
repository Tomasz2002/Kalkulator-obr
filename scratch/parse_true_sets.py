import struct, json, re

with open('data/extracted_client_dbc/patch-5.mpq_Spell.dbc', 'rb') as f:
    header = f.read(20)
    magic, records, fields, rec_size, str_size = struct.unpack('<4sIIII', header)
    data = f.read(records * rec_size)
    strings = f.read(str_size)

def get_str(offset):
    if offset >= len(strings) or offset < 0: return ''
    end = strings.find(b'\x00', offset)
    return strings[offset:end].decode('utf-8', errors='ignore')

# 1.12 Spell.dbc structure:
# EffectBasePoints is at indices 58, 59, 60 (for effects 1, 2, 3) (or let's check)
# Let's inspect EffectBasePoints for a known spell (e.g. 7598 has +2% crit -> base points = 1 or 2)

spells_info = {}
for i in range(records):
    rec = data[i*rec_size : (i+1)*rec_size]
    spell_id = struct.unpack('<I', rec[:4])[0]
    ints = struct.unpack(f'<{fields}i', rec)
    
    # 120: name
    # 138: description
    name = get_str(ints[120])
    desc = get_str(ints[138])
    
    # base points for effect 1, 2, 3
    # in 1.12: effectBasePoints[3] are at ints[58], ints[59], ints[60]
    # effectDieSides[3] are at ints[61], ints[62], ints[63]
    # basePoints is usually (value - 1) or value
    # let's grab them
    spells_info[spell_id] = {
        'id': spell_id,
        'name': name,
        'desc': desc,
        'ints': ints
    }

def format_desc(spell):
    d = spell['desc']
    if not d:
        return spell['name']
    ints = spell['ints']
    
    # Effect 1 base points: ints[58] + 1
    # Effect 2 base points: ints[59] + 1
    # Effect 3 base points: ints[60] + 1
    # Let's format $s1, $s2, $s3, $/1000;s1, etc.
    s1 = ints[58] + 1
    s2 = ints[59] + 1
    s3 = ints[60] + 1
    
    text = d
    text = text.replace('$s1', str(s1))
    text = text.replace('$s2', str(s2))
    text = text.replace('$s3', str(s3))
    text = text.replace('$/1000;s1', str(s1 / 1000))
    text = text.replace('$/1000;s2', str(s2 / 1000))
    text = text.replace('$o1', str(s1))
    text = text.replace('$m1', str(s1))
    return text

# Load ItemSet.dbc from patch-4.mpq
with open('data/extracted_client_dbc/patch-4.mpq_ItemSet.dbc', 'rb') as f:
    h = f.read(20)
    _, s_records, s_fields, s_rec_size, s_str_size = struct.unpack('<4sIIII', h)
    s_data = f.read(s_records * s_rec_size)
    s_strings = f.read(s_str_size)

def get_set_str(offset):
    if offset >= len(s_strings) or offset < 0: return ''
    end = s_strings.find(b'\x00', offset)
    return s_strings[offset:end].decode('utf-8', errors='ignore')

sets_output = {}
for i in range(s_records):
    rec = s_data[i*s_rec_size : (i+1)*s_rec_size]
    vals = struct.unpack(f'<{s_fields}I', rec)
    set_id = vals[0]
    name = get_set_str(vals[1])
    item_ids = [x for x in vals[10:27] if x != 0]
    spells = vals[27:35]
    thresholds = vals[35:43]
    bonuses = []
    for j in range(8):
        sid = spells[j]
        th = thresholds[j]
        if sid != 0 and sid in spells_info:
            sp = spells_info[sid]
            bonuses.append({
                'threshold': th,
                'spell_id': sid,
                'name': sp['name'],
                'raw_desc': sp['desc'],
                'text': f"({th}) Set: {format_desc(sp)}"
            })
    if any(k in name.lower() for k in ['lawbringer', 'judgement', 'redemption', 'might', 'wrath', 'dreadnaught']):
        sets_output[set_id] = {
            'id': set_id,
            'name': name,
            'item_ids': item_ids,
            'bonuses': bonuses
        }

with open('scratch/paladin_warrior_true_sets.json', 'w', encoding='utf-8') as f:
    json.dump(sets_output, f, indent=2, ensure_ascii=False)

print(f'Wrote {len(sets_output)} sets to scratch/paladin_warrior_true_sets.json')
