import struct

wdb_path = r"C:\Octo wow gowno\WDB\itemcache.wdb"
with open(wdb_path, "rb") as f:
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
    num_ints = (len(rec) - pos) // 4
    ints = struct.unpack(f'<{num_ints}i', rec[pos:pos+num_ints*4])
    items[entry] = {'name': names[0], 'ints': ints}
    offset += 8 + size

for tid in [11815, 11726, 19019, 22416]:
    if tid in items:
        it = items[tid]
        print(f"ID {tid}: {it['name']} | req_level (int 9) = {it['ints'][9]}, ilvl (int 8) = {it['ints'][8]}")
    else:
        print(f"ID {tid}: not in client WDB")
