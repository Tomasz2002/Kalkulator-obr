import json

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    sets = json.load(f)

for s in sets.values():
    if s.get('id') in [209, 1003, 218, 2003, 523]:
        print(json.dumps(s, indent=2))
