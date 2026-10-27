import struct

with open('data/itemcache.wdb', 'rb') as f:
    data = f.read()

offset = 20
items = []
while offset < len(data):
    entry, size = struct.unpack('<II', data[offset:offset+8])
    if size == 0:
        break
    chunk = data[offset+8 : offset+8+size]
    pos = 8
    names = []
    for _ in range(4):
        end = chunk.find(b'\x00', pos)
        if end != -1:
            names.append(chunk[pos:end].decode('utf-8', errors='ignore'))
            pos = end + 1
        else:
            names.append('')
    name = names[0]
    num_ints = (len(chunk) - pos) // 4
    ints = struct.unpack(f'<{num_ints}i', chunk[pos : pos + num_ints * 4])
    set_id = ints[109] if len(ints) > 109 else 0
    slot_id = ints[1] if len(ints) > 1 else 0
    items.append((entry, name, slot_id, set_id))
    offset += 8 + size

range_items = [it for it in items if 47000 <= it[0] <= 47300]
print(f"Total items in 47000..47300 range: {len(range_items)}")
for entry, name, slot_id, sid in sorted(range_items, key=lambda x: x[0]):
    print(f"{entry}: '{name}', slot_id={slot_id}, set_id={sid}")
