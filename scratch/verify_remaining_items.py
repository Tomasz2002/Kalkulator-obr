import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']
q_counts = {}
for it in items:
    q = it.get('quality', 1)
    q_counts[q] = q_counts.get(q, 0) + 1

print("Remaining items count:", len(items))
print("Quality distribution:", sorted(q_counts.items()))
print("By_id count:", len(db['by_id']))
print("By_slot slots:", {k: len(v) for k, v in db['by_slot'].items()})
