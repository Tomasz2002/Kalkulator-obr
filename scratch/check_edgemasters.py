import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

it = db['by_id'].get('14551')
if it:
    print(f"Edgemaster's Handguards: req_level={it.get('req_level')}, ilvl={it.get('item_level')}")
else:
    print("Edgemaster's Handguards: NOT FOUND")
