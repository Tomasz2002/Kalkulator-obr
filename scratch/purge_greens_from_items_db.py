import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']
kept_items = [it for it in items if it.get('quality', 1) >= 3]

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

print(f"Purge complete: removed {len(items) - len(kept_items)} green items. Remaining items: {len(kept_items)}.")
