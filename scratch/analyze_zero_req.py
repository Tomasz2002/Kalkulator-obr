import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']

zero_req = [it for it in items if it.get('req_level', 0) == 0]
print(f"Total zero req_level items: {len(zero_req)}")

zero_high_ilvl = [it for it in zero_req if it.get('item_level', 0) >= 55]
print(f"Zero req_level items with item_level >= 55: {len(zero_high_ilvl)}")

zero_low_ilvl = [it for it in zero_req if it.get('item_level', 0) < 55]
print(f"Zero req_level items with item_level < 55: {len(zero_low_ilvl)}")

print("\nExamples of zero req_level with item_level >= 55:")
for it in zero_high_ilvl[:10]:
    print(f"  {it['id']}: {it['name']} (ilvl {it['item_level']}, quality {it['quality']})")

print("\nExamples of zero req_level with item_level < 55:")
for it in zero_low_ilvl[:10]:
    print(f"  {it['id']}: {it['name']} (ilvl {it['item_level']}, quality {it['quality']})")
