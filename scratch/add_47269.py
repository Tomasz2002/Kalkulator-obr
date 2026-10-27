import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

ring = {
    'id': 47269,
    'name': 'Ring of the Dreadnaught',
    'icon': 'INV_Jewelry_Ring_03',
    'slot': 'finger',
    'subclass': 'misc',
    'quality': 4,
    'item_level': 86,
    'req_level': 60,
    'armor': 0,
    'durability': 0,
    'unique': False,
    'bonding': 1,
    'speed': 0.0,
    'min_damage': 0.0,
    'max_damage': 0.0,
    'dps': 0.0,
    'strength': 22,
    'agility': 0,
    'stamina': 11,
    'intellect': 0,
    'spirit': 0,
    'resistances': {'holy': 0, 'fire': 0, 'nature': 0, 'frost': 0, 'shadow': 0, 'arcane': 0},
    'attack_power': 0,
    'spell_power': 0,
    'healing': 0,
    'crit': 1.0,
    'hit': 1.0,
    'spells': [],
    'set_id': 3002,
    'set': octo_sets.get('3002'),
    'classes': ['warrior']
}

existing = [it for it in db['items'] if it['id'] != 47269]
existing.append(ring)
db['items'] = existing
db['by_id'] = {str(it['id']): it for it in db['items']}
by_slot = {}
for it in db['items']:
    slot = it.get('slot', 'misc')
    if slot not in by_slot:
        by_slot[slot] = []
    by_slot[slot].append(it['id'])
db['by_slot'] = by_slot

with open('items_db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2)

print('Added Ring of the Dreadnaught 47269. Total items:', len(db['items']))
