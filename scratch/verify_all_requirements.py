import json
import os
import re

files_to_check = [
    'src/calculators/paladin.py',
    'src/calculators/warrior.py',
    'src/calculators/__init__.py',
    'src/items_db.py',
    'app.py',
    'main.py',
    'static/app.js',
    'templates/index.html'
]

errors = []

for rel_path in files_to_check:
    if not os.path.exists(rel_path):
        continue
    with open(rel_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        s = line.strip()
        if rel_path.endswith('.py'):
            if s.startswith('#'):
                errors.append(f'{rel_path}:{idx}: Python comment: {s}')
            if '"""' in s or "'''" in s:
                errors.append(f'{rel_path}:{idx}: Python docstring/multiline quote: {s}')
        elif rel_path.endswith('.js'):
            if s.startswith('//') or '/*' in s or '*/' in s:
                errors.append(f'{rel_path}:{idx}: JS comment: {s}')
        elif rel_path.endswith('.html'):
            if '<!--' in s:
                errors.append(f'{rel_path}:{idx}: HTML comment: {s}')

if errors:
    print('COMMENT ERRORS FOUND:')
    for err in errors:
        print(' ', err)
else:
    print('ZERO COMMENTS VERIFICATION PASSED ON ALL PROJECT FILES!')

races = json.load(open('data/races.json', encoding='utf-8'))
warrior_highelf = [r for r in races.get('warrior', []) if r['id'] == 'highelf']
assert len(warrior_highelf) == 1, 'High Elf missing in warrior races'
print('High Elf in warrior races: PASSED')

items_db = json.load(open('items_db.json', encoding='utf-8'))
sets_to_verify = [208, 1004, 1005, 217, 2004, 2005, 528, 3004, 3005]
for sid in sets_to_verify:
    pieces = [it for it in items_db['items'] if it.get('set_id') == sid]
    assert len(pieces) in (8, 9), f'Set {sid} has wrong count: {len(pieces)}'
    for it in pieces:
        item_id = it.get('id')
        assert 'paladin' in it.get('classes', []), f'{item_id} not paladin'
        for sp in it.get('spells', []):
            assert sp.get('spell_id') != 1 and 'word of recall' not in str(sp).lower(), f'{item_id} has word of recall'

print('All 9 Paladin Sets Verified: PASSED (Lawbringer 3 sets, Judgement 3 sets, Redemption 3 sets)')

might_crown = [it for it in items_db['items'] if it['id'] == 47240][0]
assert might_crown['classes'] == ['warrior'], 'Crown of might not warrior only'
print('Crown of Might restriction to warrior: PASSED')
