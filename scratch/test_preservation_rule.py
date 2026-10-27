import json

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

check_set_ids = [208, 1004, 1005, 217, 2004, 2005, 528, 3004, 3005,
                 209, 1003, 218, 2003, 523, 3002, 189, 511, 496]

all_pieces = []
for sid in check_set_ids:
    s = octo_sets.get(str(sid))
    if s and 'pieces' in s:
        all_pieces.extend(s['pieces'])

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']

def should_keep(it):
    item_id = it.get('id')
    if item_id in [11815, 11726, 20130]:
        return True
    if it.get('set_id'):
        return True
    req = it.get('req_level', 0)
    ilvl = it.get('item_level', 0)
    if req >= 55:
        return True
    if req == 0 and (ilvl >= 55 or it.get('quality', 0) >= 5):
        return True
    return False

kept = [it for it in items if should_keep(it)]
kept_ids = set(it['id'] for it in kept)

missing = [pid for pid in all_pieces if pid not in kept_ids]
print(f"Total set pieces checked: {len(all_pieces)}")
print(f"Missing set pieces: {len(missing)}")
print(f"Total items kept: {len(kept)} (removed: {len(items) - len(kept)})")
