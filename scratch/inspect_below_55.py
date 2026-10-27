import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']
below_55 = [it for it in items if 1 <= it.get('req_level', 0) < 55]
print(f"Items with 1 <= req_level < 55: {len(below_55)}")

ge_55 = [it for it in items if it.get('req_level', 0) >= 55]
print(f"Items with req_level >= 55: {len(ge_55)}")

print("\nSample items with 50 <= req_level < 55:")
for it in [it for it in below_55 if it.get('req_level', 0) >= 50][:15]:
    print(f"  {it['id']}: {it['name']} (req_level={it['req_level']}, ilvl={it['item_level']}, quality={it['quality']})")
