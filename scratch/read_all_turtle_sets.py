import struct

with open('data/turtle_dbc/ItemSet.dbc', 'rb') as f:
    header = f.read(20)
    magic, records, fields, rec_size, str_size = struct.unpack('<4sIIII', header)
    data = f.read(records * rec_size)
    strings = f.read(str_size)

def get_str(offset):
    if offset >= len(strings) or offset < 0: return ''
    end = strings.find(b'\x00', offset)
    return strings[offset:end].decode('utf-8', errors='ignore')

all_sets = []
for i in range(records):
    rec = data[i*rec_size : (i+1)*rec_size]
    vals = struct.unpack(f'<{fields}I', rec)
    set_id = vals[0]
    name = get_str(vals[1])
    item_ids = [x for x in vals[10:27] if x != 0]
    spells = vals[27:35]
    thresholds = vals[35:43]
    bonuses = [(thresholds[j], spells[j]) for j in range(8) if spells[j] != 0]
    all_sets.append((set_id, name, item_ids, bonuses))

print(f'Total sets: {len(all_sets)}')
for s in all_sets:
    if s[0] > 550 or any(k in s[1].lower() for k in ['paladin', 'warrior', 'might', 'wrath', 'lawbringer', 'judge', 'redempt', 'crusader', 'aegis', 'battlegear']):
        print(s)
