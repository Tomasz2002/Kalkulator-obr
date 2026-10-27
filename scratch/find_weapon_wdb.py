import struct, json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

with open('data/itemcache.wdb', 'rb') as f:
    data = f.read()

offset = 20
wdb_items = {}
while offset < len(data):
    entry, size = struct.unpack('<II', data[offset:offset+8])
    if size == 0: break
    rec = data[offset+8:offset+8+size]
    wdb_items[entry] = rec
    offset += 8 + size

weapons = [it for it in db['items'] if it['slot'] in ('mainhand', 'twohand', 'onehand', 'ranged') and str(it['id']) in [str(k) for k in wdb_items]]
print("Common weapons:", len(weapons))
if weapons:
    w = weapons[0]
    rec = wdb_items[w['id']]
    pos = 8
    names = []
    for _ in range(4):
        end = rec.find(b'\x00', pos)
        names.append(rec[pos:end].decode('utf-8', errors='ignore'))
        pos = end + 1
    fixed = rec[pos:]
    ints = struct.unpack(f'<{len(fixed)//4}i', fixed[:(len(fixed)//4)*4])
    floats = struct.unpack(f'<{len(fixed)//4}f', fixed[:(len(fixed)//4)*4])
    print(f"Weapon {w['id']} ({w['name']}): min={w['min_damage']}, max={w['max_damage']}, speed={w['speed']}")
    for i, (iv, fv) in enumerate(zip(ints[35:55], floats[35:55])):
        print(f"idx {35+i}: int={iv}, float={fv:.2f}")
