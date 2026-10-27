import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print('--- Paladin sets items in items_db.json ---')
for it in db['items']:
    name = it.get('name', '')
    if any(k in name.lower() for k in ['lawbringer', 'judgement', 'judgment', 'redemption']):
        print(f"{it['id']}: {name} ({it.get('slot')}) -> set_id: {it.get('set_id')}, set: {it.get('set', {}).get('name') if it.get('set') else 'None'}")
