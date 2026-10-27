import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']
print("Total items now in DB:", len(items))

req_levels = [it.get('req_level', 0) for it in items]
print(f"Max req_level: {max(req_levels)}")
print(f"Min req_level among items with req_level > 0 and id not in iconic: {min(it.get('req_level', 0) for it in items if it.get('req_level', 0) > 0 and not it.get('set_id') and it.get('id') not in [14551, 11815, 11726, 20130, 11811])}")

for cid in [19019, 14551, 11815, 11726, 20130, 16865, 47242, 47254, 22416, 23059]:
    it = db['by_id'].get(str(cid))
    print(f"ID {cid} ({it['name'] if it else 'MISSING'}): {'FOUND' if it else 'MISSING'}")
