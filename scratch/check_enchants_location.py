import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print("Keys in items_db.json:", list(db.keys()))

with open('data/enchants.json', 'r', encoding='utf-8') as f:
    enchants = json.load(f)

print("Keys in data/enchants.json:", list(enchants.keys()))
for k, v in enchants.items():
    print(f"  {k}: {len(v)} enchants")
