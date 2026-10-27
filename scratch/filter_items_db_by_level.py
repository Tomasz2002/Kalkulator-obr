import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']

iconic_ids = {14551, 11815, 11726, 20130, 11811}

def should_keep(it):
    item_id = it.get('id')
    if item_id in iconic_ids:
        return True
    if it.get('set_id'):
        return True
    if it.get('quality', 0) >= 5:
        return True
    req = it.get('req_level', 0)
    ilvl = it.get('item_level', 0)
    if req >= 55:
        return True
    if req == 0 and ilvl >= 55:
        return True
    return False

kept_items = [it for it in items if should_keep(it)]
removed_items = [it for it in items if not should_keep(it)]

new_by_id = {}
new_by_slot = {}

for it in kept_items:
    sid = str(it['id'])
    new_by_id[sid] = it
    slot = it.get('slot')
    if slot:
        if slot not in new_by_slot:
            new_by_slot[slot] = []
        new_by_slot[slot].append(it)

new_db = {
    'items': kept_items,
    'by_id': new_by_id,
    'by_slot': new_by_slot
}

with open('items_db.json', 'w', encoding='utf-8') as f:
    json.dump(new_db, f, indent=2, ensure_ascii=False)

print(f"Purge complete: removed {len(removed_items)} items below lvl 55. Remaining items: {len(kept_items)}.")
