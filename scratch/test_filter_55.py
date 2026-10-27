import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']

def should_keep(it):
    req = it.get('req_level', 0)
    ilvl = it.get('item_level', 0)
    item_id = it.get('id')
    
    if item_id in [11815, 11726, 20130]:
        return True
    
    if req >= 55:
        return True
    
    if req == 0 and (ilvl >= 55 or it.get('set_id') or it.get('quality', 0) >= 5):
        return True
        
    return False

kept = [it for it in items if should_keep(it)]
removed = [it for it in items if not should_keep(it)]

print(f"Total current items: {len(items)}")
print(f"Items kept: {len(kept)}")
print(f"Items removed: {len(removed)}")

print("\nRemoved items sample:")
for it in removed[:15]:
    print(f"  {it['id']}: {it['name']} | req={it.get('req_level')}, ilvl={it.get('item_level')}, q={it.get('quality')}")

print("\nKept items check:")
for cid in [19019, 16865, 47242, 47254, 22416, 11815, 11726, 20130, 13965]:
    found = any(it['id'] == cid for it in kept)
    print(f"  ID {cid}: {'KEPT' if found else 'MISSING'}")
