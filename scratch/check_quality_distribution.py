import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']
q_counts = {}
for it in items:
    q = it.get('quality', 1)
    q_counts[q] = q_counts.get(q, 0) + 1

print("Total items:", len(items))
print("Quality distribution:", sorted(q_counts.items()))

quality_ge_2 = [it for it in items if it.get('quality', 1) >= 2]
print(f"Items with quality >= 2: {len(quality_ge_2)}")
print(f"Items to remove (quality < 2): {len(items) - len(quality_ge_2)}")
