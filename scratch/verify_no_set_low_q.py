import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

set_items_low_q = [it for it in db['items'] if it.get('set_id') and it.get('quality', 1) < 2]
print(f"Set items with quality < 2: {len(set_items_low_q)}")
