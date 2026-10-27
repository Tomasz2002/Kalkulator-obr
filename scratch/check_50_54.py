import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']
r50_54 = [it for it in items if 50 <= it.get('req_level', 0) < 55]
print(f"Items with 50 <= req_level < 55: {len(r50_54)}")
for it in r50_54:
    if it.get('quality', 0) >= 4 or it.get('id') in [11815, 11726, 20130]:
        print(f"  {it['id']}: {it['name']} | req={it.get('req_level')}, ilvl={it.get('item_level')}, q={it.get('quality')}")
