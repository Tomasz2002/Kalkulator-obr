import struct, json

with open('data/ItemSet.dbc', 'rb') as f:
    header = f.read(20)
    magic, rec_count, field_count, rec_size, string_size = struct.unpack('<4sIIII', header)
    data = f.read(rec_count * rec_size)
    strings = f.read(string_size)

def get_str(offset):
    if offset <= 0 or offset >= len(strings): return ''
    end = strings.find(b'\x00', offset)
    if end == -1: end = len(strings)
    return strings[offset:end].decode('utf-8', errors='ignore')

dbc_sets = {}
for i in range(rec_count):
    row = data[i * rec_size : (i + 1) * rec_size]
    vals = struct.unpack(f'<{field_count}i', row)
    set_id = vals[0]
    name = get_str(vals[1])
    items = [v for v in vals[10:27] if v > 0]
    dbc_sets[set_id] = {
        'id': set_id,
        'name': name,
        'items': items
    }

print(f"Loaded {len(dbc_sets)} sets from ItemSet.dbc")
for sid in [209, 218, 208, 217, 523]:
    if sid in dbc_sets:
        print(f"Set {sid}: {dbc_sets[sid]}")
