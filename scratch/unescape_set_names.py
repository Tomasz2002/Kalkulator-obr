import html
import json

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

for sid, s in octo_sets.items():
    s['name'] = html.unescape(s.get('name', ''))
    for b in s.get('bonuses', []):
        b['text'] = html.unescape(b.get('text', ''))

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for it in db['items']:
    s = it.get('set')
    if s:
        s['name'] = html.unescape(s.get('name', ''))
        for b in s.get('bonuses', []):
            b['text'] = html.unescape(b.get('text', ''))

db['by_id'] = {str(it['id']): it for it in db['items']}

with open('data/octo_sets.json', 'w', encoding='utf-8') as f:
    json.dump(octo_sets, f, indent=2)

with open('items_db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2)

print('Unescaped all set names and bonuses successfully.')
