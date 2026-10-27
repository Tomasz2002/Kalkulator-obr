import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db['by_id'] = {str(it['id']): it for it in db['items']}
db['by_slot'] = {}
for it in db['items']:
    db['by_slot'].setdefault(it['slot'], []).append(it)

with open('items_db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2)

print("Check 47242 set:", db['by_id']['47242']['set']['name'])
