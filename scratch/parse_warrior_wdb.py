import struct
import json

warrior_set_ids = [209, 1003, 218, 2003, 523, 3002, 189, 511, 496]

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

all_warrior_item_ids = []
for sid in warrior_set_ids:
    s = octo_sets.get(str(sid))
    if s and 'pieces' in s:
        all_warrior_item_ids.extend(s['pieces'])

wdb_path = r"C:\Octo wow gowno\WDB\itemcache.wdb"
with open(wdb_path, "rb") as f:
    data = f.read()

offset = 20
items = {}
while offset < len(data):
    entry, size = struct.unpack('<II', data[offset:offset+8])
    if size == 0:
        break
    rec = data[offset+8:offset+8+size]
    pos = 8
    names = []
    for _ in range(4):
        end = rec.find(b'\x00', pos)
        names.append(rec[pos:end].decode('utf-8', errors='replace'))
        pos = end + 1
    num_ints = (len(rec) - pos) // 4
    ints = struct.unpack(f'<{num_ints}i', rec[pos:pos+num_ints*4])
    items[entry] = {'name': names[0], 'ints': ints}
    offset += 8 + size

print(f"Total items in client WDB: {len(items)}")

found = [x for x in all_warrior_item_ids if x in items]
print(f"Found {len(found)} out of {len(all_warrior_item_ids)} warrior set items in client WDB")
for x in all_warrior_item_ids:
    if x in items:
        it = items[x]
        print(f"ID {x}: {it['name']}")
    else:
        print(f"ID {x}: NOT in client WDB")
