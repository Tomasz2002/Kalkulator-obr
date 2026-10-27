import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']

iconic_ids = {14551, 11815, 11726, 20130, 11811}
non_set_51_54 = [it for it in items if 0 < it.get('req_level', 0) < 55 and not it.get('set_id') and it.get('id') not in iconic_ids]
print(f"Non-set items with 0 < req_level < 55: {len(non_set_51_54)}")
for it in non_set_51_54:
    print(f"  {it['id']}: {it['name']} | req={it.get('req_level')}, q={it.get('quality')}")
