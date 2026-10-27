import struct

with open('data/itemcache.wdb', 'rb') as f:
    rec = f.read()

offset = 20
while offset < len(rec):
    e, s = struct.unpack('<II', rec[offset:offset+8])
    if e == 2100:
        chunk = rec[offset+8:offset+8+s]
        pos = 8
        for _ in range(4): pos = chunk.find(b'\x00', pos) + 1
        num_ints = (len(chunk) - pos) // 4
        ints = struct.unpack(f'<{num_ints}i', chunk[pos:pos + num_ints*4])
        for i, val in enumerate(ints):
            if val == 1500:
                print('Found 1500 at index:', i)
        break
    offset += 8 + s
