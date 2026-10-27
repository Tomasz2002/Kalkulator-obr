import struct

with open('data/turtle_dbc/ItemSet.dbc', 'rb') as f:
    header = f.read(20)
    magic, records, fields, rec_size, str_size = struct.unpack('<4sIIII', header)
    data = f.read(records * rec_size)
    strings = f.read(str_size)

print(f'ItemSet.dbc -> records: {records}, fields: {fields}, rec_size: {rec_size}, str_size: {str_size}')

def get_str(offset):
    if offset >= len(strings) or offset < 0: return ''
    end = strings.find(b'\x00', offset)
    return strings[offset:end].decode('utf-8', errors='ignore')

# 1.12 ItemSet.dbc layout:
# 0: id
# 1..8: name_lang (offset into strings)
# 9: string flags
# 10..26: item_id[17]
# 27..34: spell_id[8]
# 35..42: threshold[8]
# 43: required_skill
# 44: required_skill_rank
# fields count: let's check what fields is (usually 45 or similar)
print('Total fields:', fields)

for i in range(records):
    rec = data[i*rec_size : (i+1)*rec_size]
    vals = struct.unpack(f'<{fields}I', rec)
    set_id = vals[0]
    name = get_str(vals[1])
    item_ids = [x for x in vals[10:27] if x != 0]
    spells = vals[27:35]
    thresholds = vals[35:43]
    bonuses = [(thresholds[j], spells[j]) for j in range(8) if spells[j] != 0]
    if any(k in name.lower() for k in ['lawbringer', 'judgement', 'judgment', 'redemption', 'might', 'wrath', 'dreadnaught', 'valor', 'heroism']):
        print(f'Set {set_id}: {name}')
        print(f'  Items: {item_ids}')
        print(f'  Bonuses: {bonuses}')
