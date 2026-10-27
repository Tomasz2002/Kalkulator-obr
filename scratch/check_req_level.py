import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']
print("Total items currently:", len(items))

check_ids = [19019, 17063, 18821, 19406, 20130, 13965, 11815, 16865, 47242, 47254, 22416, 23059, 19379, 19375, 19355]
for cid in check_ids:
    it = db['by_id'].get(str(cid))
    if it:
        print(f"ID {cid} ({it['name']}): req_level={it.get('req_level')}, item_level={it.get('item_level')}")
    else:
        print(f"ID {cid}: NOT FOUND")

zero_req_level = [it for it in items if it.get('req_level', 0) == 0]
print(f"\nItems with req_level == 0: {len(zero_req_level)}")
for it in zero_req_level[:15]:
    print(f"  {it['id']}: {it['name']} | ilvl={it.get('item_level')} quality={it.get('quality')}")
