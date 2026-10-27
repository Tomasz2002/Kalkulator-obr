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

targets = [
    # Holy T1
    9317, 18382, 21747,
    # Tank T1
    51806, 13675, 51805, 51804,
    # Ret T1
    51801, 7598, 51803, 51802,
    # Holy T2
    18037, 51807, 51809, 51808,
    # Tank T2
    51811, 14054, 51815, 51814,
    # Ret T2
    51811, 14054, 21882, 21889,
    # Holy T3
    51820, 28774, 51821, 28787,
    # Tank T3
    13676, 28325, 51823, 23213,
    # Ret T3
    7599, 8815, 51823, 23213,
    # Warrior DPS T1
    51899, 53200, 52401,
    # Warrior DPS T2
    53203, 52322, 53204
]

res = {}
for i in range(records):
    rec = data[i*rec_size : (i+1)*rec_size]
    spell_id = struct.unpack('<I', rec[:4])[0]
    if spell_id in targets:
        ints = struct.unpack(f'<{fields}i', rec)
        name = get_str(ints[120])
        desc = get_str(ints[138])
        bp0 = ints[76] + 1
        bp1 = ints[77] + 1
        bp2 = ints[78] + 1
        res[spell_id] = {
            'id': spell_id,
            'name': name,
            'desc': desc,
            'bp': [bp0, bp1, bp2],
            'proc_chance': ints[40] if len(ints) > 40 else 0
        }

for sid in targets:
    if sid in res:
        it = res[sid]
        print(f"{sid} ({it['name']}): bp={it['bp']}, proc={it['proc_chance']}")
        print(f"   raw: {it['desc']}")
