import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for item_id in [16865, 47242, 16963, 47254, 22416, 47263]:
    it = db['by_id'].get(str(item_id))
    if it:
        print(f"\nItem {item_id}: {it.get('name')}")
        s = it.get('set')
        if s:
            print(f"  Set: {s.get('name')} (id: {s.get('id')})")
            for b in s.get('bonuses', []):
                print(f"    {b}")
        else:
            print("  NO SET EMBEDDED")
