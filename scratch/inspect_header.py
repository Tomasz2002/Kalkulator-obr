import struct

with open('data/itemcache.wdb', 'rb') as f:
    rec = f.read()

offset = 20
while offset < len(rec):
    e, s = struct.unpack('<II', rec[offset:offset+8])
    if e == 22411:
        chunk = rec[offset+8:offset+8+s]
        print("Header ints (before strings?):", struct.unpack('<2I', chunk[:8]))
        pos = 8
        for i in range(4):
            end = chunk.find(b'\x00', pos)
            print(f"String {i}:", chunk[pos:end])
            pos = end + 1
        break
    offset += 8 + s
