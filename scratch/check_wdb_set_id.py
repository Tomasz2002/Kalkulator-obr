import struct

with open('data/itemcache.wdb', 'rb') as f:
    data = f.read()

offset = 20
items_by_id = {}
while offset < len(data):
    entry, size = struct.unpack('<II', data[offset:offset+8])
    if size == 0: break
    rec = data[offset+8:offset+8+size]
    items_by_id[entry] = rec
    offset += 8 + size

def get_item_set_id(entry):
    rec = items_by_id.get(entry)
    if not rec: return None
    pos = 8
    for _ in range(4): pos = rec.find(b'\x00', pos) + 1
    num_ints = (len(rec) - pos) // 4
    ints = struct.unpack(f'<{num_ints}i', rec[pos:pos+num_ints*4])
    return ints[109] if len(ints) > 109 else None

print("47242 set_id in WDB:", get_item_set_id(47242))
print("47241 set_id in WDB:", get_item_set_id(47241))
print("16865 set_id in WDB:", get_item_set_id(16865))
