import json

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    sets = json.load(f)

for s_id in [189, 511, 496, 3002]:
    s = sets.get(str(s_id))
    if s:
        print(json.dumps(s, indent=2))
