import json

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

over_9 = []
for sid, s in octo_sets.items():
    pieces = s.get('pieces', [])
    if len(pieces) > 9:
        over_9.append((sid, s.get('name'), len(pieces)))

print('Sets with > 9 pieces:', over_9)

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for target_id in [16865, 47242, 16866, 47240, 16966, 47250]:
    it = db['by_id'].get(str(target_id))
    if it:
        set_obj = it.get('set') or {}
        print(f"Item {it['id']} ({it['name']}): set_id={it.get('set_id')}, set_name={set_obj.get('name')}, pieces_count={len(set_obj.get('pieces', []))}")
    else:
        print(f"Item {target_id}: MISSING")

might_tank = octo_sets.get('209', {})
print("\nBattlegear of Might (209) pieces:")
for p in might_tank.get('pieces', []):
    item = db['by_id'].get(str(p), {})
    print(f"  {p}: {item.get('name')}")

might_dps = octo_sets.get('1003', {})
print("\nArmor of Might (1003) pieces:")
for p in might_dps.get('pieces', []):
    item = db['by_id'].get(str(p), {})
    print(f"  {p}: {item.get('name')}")
