import json, struct

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

for sid, sdata in octo_sets.items():
    if 47242 in sdata.get('pieces', []):
        print(f"Found 47242 in octo_sets[{sid}]: {sdata['name']}, pieces={sdata['pieces']}")

with open('data/ItemSet.dbc', 'rb') as f:
    header = f.read(20)
    magic, rec_count, field_count, rec_size, string_size = struct.unpack('<4sIIII', header)
    data = f.read(rec_count * rec_size)
    strings = f.read(string_size)

for i in range(rec_count):
    row = data[i * rec_size : (i + 1) * rec_size]
    vals = struct.unpack(f'<{field_count}i', row)
    items = [v for v in vals[10:27] if v > 0]
    if 47242 in items:
        print(f"Found 47242 in ItemSet.dbc set {vals[0]}")
