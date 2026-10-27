import struct, json

with open('data/extracted_client_dbc/patch-5.mpq_Spell.dbc', 'rb') as f:
    header = f.read(20)
    magic, records, fields, rec_size, str_size = struct.unpack('<4sIIII', header)
    data = f.read(records * rec_size)
    strings = f.read(str_size)

def get_str(offset):
    if offset >= len(strings) or offset < 0: return ''
    end = strings.find(b'\x00', offset)
    return strings[offset:end].decode('utf-8', errors='ignore')

target_spell_ids = [
    # Lawbringer Armor (Holy T1)
    9317, 18382, 21747,
    # Lawbringer Battleplate (Tank T1)
    51806, 13675, 51805,
    # Lawbringer Battlegear (DPS T1)
    51801, 7598, 51803,
    # Judgement Armor (Holy T2)
    18037, 51807, 51809,
    # Judgement Battleplate (Tank T2)
    51811, 14054, 51815,
    # Judgement Battlegear (DPS T2)
    51811, 14054, 21882,
    # Redemption Armor (Holy T3)
    51820, 28774, 51821, 28787,
    # Redemption Battleplate (Tank T3)
    13676, 28325, 51823, 23213,
    # Redemption Battlegear (DPS T3)
    7599, 8815, 51823, 23213,
    # Warrior Armor of Might (DPS T1)
    51899, 53200, 52401,
    # Warrior Armor of Wrath (DPS T2)
    53203, 52322, 53204
]

res = {}
for i in range(records):
    rec = data[i*rec_size : (i+1)*rec_size]
    spell_id = struct.unpack('<I', rec[:4])[0]
    if spell_id in target_spell_ids:
        ints = struct.unpack(f'<{fields}I', rec)
        found_strs = [(idx, get_str(val)) for idx, val in enumerate(ints) if 0 < val < str_size and get_str(val).strip()]
        res[spell_id] = found_strs

with open('scratch/all_target_spells_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=2, ensure_ascii=False)

print('Dumped successfully!')
