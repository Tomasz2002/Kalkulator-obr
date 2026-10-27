import struct

with open(r'C:\Octo wow gowno\WDB\itemcache.wdb', 'rb') as f:
    data = f.read()

offset = 20
items = {}
while offset < len(data):
    entry, size = struct.unpack('<II', data[offset:offset+8])
    if size == 0: break
    rec = data[offset+8:offset+8+size]
    pos = 8
    names = []
    for _ in range(4):
        end = rec.find(b'\x00', pos)
        names.append(rec[pos:end].decode('utf-8', errors='replace'))
        pos = end + 1
    items[entry] = names[0]
    offset += 8 + size

for e in range(47042, 47060):
    print(f'{e}: {items.get(e)}')

for e in range(70571, 70589):
    print(f'{e}: {items.get(e)}')
