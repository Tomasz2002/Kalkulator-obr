import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']

zero_req_set_items = [it for it in items if it.get('req_level', 0) == 0 and it.get('set_id')]
print(f"Zero req_level items that have set_id: {len(zero_req_set_items)}")
for it in zero_req_set_items:
    print(f"  {it['id']}: {it['name']} (Set: {it.get('set_name')}, ilvl: {it.get('item_level')})")

legendaries = [it for it in items if it.get('quality') == 5]
print(f"\nLegendaries: {len(legendaries)}")
for it in legendaries:
    print(f"  {it['id']}: {it['name']} (req_level: {it.get('req_level')}, ilvl: {it.get('item_level')})")
