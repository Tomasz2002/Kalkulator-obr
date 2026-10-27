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

print(f"Total warrior set items to check: {len(all_warrior_item_ids)}")
print(all_warrior_item_ids)

wdb_path = r"C:\Octo wow gowno\WDB\itemcache.wdb"
with open(wdb_path, "rb") as f:
    header = f.read(16)
    wdb_data = f.read()

offset = 0
found_items = {}

while offset < len(wdb_data) - 8:
    entry_id, entry_len = struct.unpack_from("<II", wdb_data, offset)
    if entry_id == 0:
        break
    if entry_id in all_warrior_item_ids:
        chunk = wdb_data[offset + 8 : offset + 8 + entry_len]
        found_items[entry_id] = chunk
    offset += 8 + entry_len

print(f"Found {len(found_items)} out of {len(all_warrior_item_ids)} in WDB")
missing = [x for x in all_warrior_item_ids if x not in found_items]
print(f"Missing from client WDB: {missing}")
