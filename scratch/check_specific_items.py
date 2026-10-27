import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for item_id in [11815, 11726, 12940, 13965, 19019, 20130, 22416]:
    it = db['by_id'].get(str(item_id))
    if it:
        print(f"ID {item_id}: {it['name']} | req_level={it.get('req_level')}, ilvl={it.get('item_level')}")
    else:
        print(f"ID {item_id}: NOT FOUND")
