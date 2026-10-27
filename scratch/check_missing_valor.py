import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for pid in [16736, 16734, 16735, 16737]:
    it = db['by_id'].get(str(pid))
    if it:
        print(f"ID {pid}: {it['name']} | req_level={it.get('req_level')}, ilvl={it.get('item_level')}")
