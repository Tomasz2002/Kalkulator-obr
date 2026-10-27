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

common = [k for k in wdb_items if str(k) in db['by_id']]
print("Common items:", len(common), common[:5])
if common:
    sample_id = common[0]
    sql_item = db['by_id'][str(sample_id)]
    rec = wdb_items[sample_id]
    pos = 8
    names = []
    for _ in range(4):
        end = rec.find(b'\x00', pos)
        names.append(rec[pos:end].decode('utf-8', errors='ignore'))
        pos = end + 1
    fixed = rec[pos:]
    ints = struct.unpack(f'<{len(fixed)//4}i', fixed[:(len(fixed)//4)*4])
    print(f"Sample {sample_id} ({sql_item['name']}):")
    print(f"SQL: slot={sql_item['slot']}, subclass={sql_item['subclass']}, quality={sql_item['quality']}, armor={sql_item['armor']}, str={sql_item['strength']}")
    for idx, val in enumerate(ints[:40]):
        print(f"ints[{idx}] = {val}")
