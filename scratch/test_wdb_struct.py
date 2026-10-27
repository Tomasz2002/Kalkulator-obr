import struct

with open('data/itemcache.wdb', 'rb') as f:
    data = f.read()

offset = 20
items = {}
while offset < len(data):
    entry, size = struct.unpack('<II', data[offset:offset+8])
    if size == 0: break
    rec = data[offset+8:offset+8+size]
    items[entry] = rec
    offset += 8 + size

def inspect_item(item_id):
    rec = items.get(item_id)
    if not rec:
        print(f"Item {item_id} not found in WDB")
        return
    pos = 8
    names = []
    for _ in range(4):
        end = rec.find(b'\x00', pos)
        names.append(rec[pos:end].decode('utf-8', errors='ignore'))
        pos = end + 1
    fixed = rec[pos:]
    print(f"Item {item_id}: Name='{names[0]}', fixed len={len(fixed)}")
    ints = struct.unpack(f'<{len(fixed)//4}i', fixed[:(len(fixed)//4)*4])
    print("First 30 ints:", ints[:30])
    for i in range(10):
        st_type = ints[20 + i*2]
        st_val = ints[20 + i*2 + 1]
        if st_type != 0 or st_val != 0:
            print(f"  Stat {i}: type={st_type}, val={st_val}")
    print(f"Armor: {ints[55]}, Res: {ints[56:62]}")
    for i in range(5):
        sp_id = ints[65 + i*7]
        sp_trig = ints[65 + i*7 + 1]
        if sp_id > 0:
            print(f"  Spell {i}: id={sp_id}, trigger={sp_trig}")
    print(f"Bonding: {ints[100]}, Durability: {ints[101] if len(ints)>101 else 'N/A'}")

inspect_item(16865)
print("---")
inspect_item(47242)
