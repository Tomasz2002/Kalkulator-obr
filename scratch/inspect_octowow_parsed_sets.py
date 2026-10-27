import json

with open('scratch/octowow_all_sets.json', 'r', encoding='utf-8') as f:
    sets = json.load(f)

print('--- Searching for Paladin/Warrior/Custom sets in octowow_all_sets.json ---')
for s in sets:
    name = s.get('name', '')
    if any(k in name.lower() for k in ['law', 'judg', 'redemp', 'light', 'soul', 'might', 'wrath', 'dread', 'heroism', 'valor', 'armor of', 'battlegear of']):
        print(f"ID {s.get('id')}: '{name}' ({len(s.get('pieces', []))} pieces) -> {s.get('pieces')}")
