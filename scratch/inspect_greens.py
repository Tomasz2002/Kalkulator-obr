import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']
q_counts = {}
for it in items:
    q = it.get('quality', 1)
    q_counts[q] = q_counts.get(q, 0) + 1

print("Current quality distribution:", sorted(q_counts.items()))

q2_items = [it for it in items if it.get('quality', 1) == 2]
q_ge_3 = [it for it in items if it.get('quality', 1) >= 3]

print(f"Quality 2 (Green) items to remove: {len(q2_items)}")
print(f"Quality >= 3 (Rare, Epic, Legendary) items to keep: {len(q_ge_3)}")

q2_set_items = [it for it in q2_items if it.get('set_id')]
print(f"Quality 2 items that have set_id: {len(q2_set_items)}")
for it in q2_set_items:
    print(f"  {it['id']}: {it['name']} (Set: {it.get('set_name')})")
