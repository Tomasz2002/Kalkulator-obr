import struct

with open('data/extracted_client_dbc/patch-4.mpq_ItemSet.dbc', 'rb') as f:
    header = f.read(20)
    magic, records, fields, rec_size, str_size = struct.unpack('<4sIIII', header)
    data = f.read(records * rec_size)
    strings = f.read(str_size)

print(f'ItemSet.dbc -> records: {records}, fields: {fields}, rec_size: {rec_size}, str_size: {str_size}')

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
    # check item_ids (10..26)
    item_ids = [x for x in vals[10:27] if x != 0]
    spells = vals[27:35]
    thresholds = vals[35:43]
    bonuses = [(thresholds[j], spells[j]) for j in range(8) if spells[j] != 0]
    all_sets.append((set_id, name, item_ids, bonuses))

print(f'Total sets in patch-4: {len(all_sets)}')

# Let's search for sets 641, 642, 643, 644 or any paladin sets
for s in all_sets:
    if s[0] in [641, 642, 643, 644] or any(k in s[1].lower() for k in ['lawbringer', 'judge', 'judg', 'redempt', 'might', 'wrath', 'dreadnaught']):
        print(s)
