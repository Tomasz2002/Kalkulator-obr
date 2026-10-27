import struct, json

with open('data/itemcache.wdb', 'rb') as f:
    rec = f.read()

offset = 20
while offset < len(rec):
    e, s = struct.unpack('<II', rec[offset:offset+8])
    if e == 47242:
        chunk = rec[offset+8:offset+8+s]
        pos = 8
        for _ in range(4): pos = chunk.find(b'\x00', pos) + 1
        num_ints = (len(chunk) - pos) // 4
        ints = struct.unpack(f'<{num_ints}i', chunk[pos:pos + num_ints*4])
        for idx in range(100, min(120, len(ints))):
            print(f"ints[{idx}] = {ints[idx]}")
        break
    offset += 8 + s
