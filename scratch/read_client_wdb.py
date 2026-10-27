import struct

with open(r'C:\Octo wow gowno\WDB\itemcache.wdb', 'rb') as f:
    data = f.read()

print('itemcache.wdb total size:', len(data))
magic, build, locale, rec_size = struct.unpack('<4sII4s', data[:16])
print(f'magic={magic}, build={build}, rec_size={rec_size}')

offset = 20
items = {}
while offset < len(data):
    entry, size = struct.unpack('<II', data[offset:offset+8])
    if size == 0: break
    rec = data[offset+8:offset+8+size]
    # find names
    pos = 8
    names = []
    for _ in range(4):
        end = rec.find(b'\x00', pos)
        names.append(rec[pos:end].decode('utf-8', errors='replace'))
        pos = end + 1
    
    # parse integers in rest
    num_ints = (len(rec) - pos) // 4
    ints = struct.unpack(f'<{num_ints}i', rec[pos:pos+num_ints*4])
    items[entry] = {'name': names[0], 'ints': ints}
    offset += 8 + size

print(f'Total items in client WDB: {len(items)}')

target_ids = list(range(47000, 47032)) + list(range(70571, 70589)) + [16858, 16952, 22430]
for tid in target_ids:
    if tid in items:
        it = items[tid]
        # in standard 1.12 WDB:
        # ints[109] is itemset (or check other columns)
        print(f'{tid}: {it["name"]} | len(ints)={len(it["ints"])}')
        # find non-zero ints near the end (where itemset, spells, stats are)
        print('  spells/set candidates:', [(idx, val) for idx, val in enumerate(it['ints']) if idx in [70,71,72,73,74,75,76,77,78,79,80, 105,106,107,108,109,110]])
