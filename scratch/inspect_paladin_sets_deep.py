import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print('--- Scanning items 47000..47032 in items_db.json ---')
for iid in range(47000, 47032):
    it = db['by_id'].get(str(iid))
    if it:
        print(f"{iid}: {it['name']} ({it.get('slot')}) str={it.get('strength')} sta={it.get('stamina')} int={it.get('intellect')} sp={it.get('spell_power')}")
    else:
        print(f"{iid}: MISSING from items_db")

print('\n--- Scanning items 70500..70590 in items_db.json ---')
for iid in range(70500, 70590):
    it = db['by_id'].get(str(iid))
    if it:
        print(f"{iid}: {it['name']} ({it.get('slot')}) str={it.get('strength')} sta={it.get('stamina')} int={it.get('intellect')}")
