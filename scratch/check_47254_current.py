import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

item_47254 = db['by_id'].get('47254')
print("47254 in items_db.json:", json.dumps(item_47254, indent=2))
