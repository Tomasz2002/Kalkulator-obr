import struct

for path in ['data/itemcache.wdb', r'C:\Octo wow gowno\WDB\itemcache.wdb']:
    with open(path, 'rb') as f:
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
        items[entry] = names[0]
        offset += 8 + size
    print(f"{path}: {len(items)} items")
    dps_might = [x for x in range(47240, 47248) if x in items]
    dps_wrath = [x for x in range(47248, 47256) if x in items]
    dps_dread = [x for x in range(47261, 47270) if x in items]
    print(f"  Might DPS items: {dps_might}")
    print(f"  Wrath DPS items: {dps_wrath}")
    print(f"  Dread DPS items: {dps_dread}")
