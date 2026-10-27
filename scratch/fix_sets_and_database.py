import struct
import json

with open('data/ItemSet.dbc', 'rb') as f:
    header = f.read(20)
    magic, rec_count, field_count, rec_size, string_size = struct.unpack('<4sIIII', header)
    data = f.read(rec_count * rec_size)
    strings = f.read(string_size)

def get_str(offset):
    if offset <= 0 or offset >= len(strings):
        return ''
    end = strings.find(b'\x00', offset)
    if end == -1:
        end = len(strings)
    return strings[offset:end].decode('utf-8', errors='ignore')

dbc_sets = {}
for i in range(rec_count):
    row = data[i * rec_size : (i + 1) * rec_size]
    vals = struct.unpack(f'<{field_count}i', row)
    sid = vals[0]
    name = get_str(vals[1])
    items = [v for v in vals[10:27] if v > 0]
    dbc_sets[sid] = {
        'name': name,
        'items': items
    }

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

for sid_str, s in list(octo_sets.items()):
    sid = int(sid_str)
    raw_name = s.get('name', '')
    clean_name = raw_name.replace(' - Item sets', '').strip()
    s['name'] = clean_name
    if sid in dbc_sets:
        s['pieces'] = list(dbc_sets[sid]['items'])
    else:
        pieces = [p for p in s.get('pieces', []) if p < 100000]
        seen = set()
        deduped = []
        for p in pieces:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        s['pieces'] = deduped[:9]

octo_sets['1003'] = {
    'id': 1003,
    'name': 'Armor of Might',
    'pieces': [47240, 47241, 47242, 47243, 47244, 47245, 47246, 47247],
    'bonuses': [
        {'threshold': 3, 'text': '(3) Set: Increases attack power by 30.'},
        {'threshold': 5, 'text': '(5) Set: Improves your chance to get a critical strike by 1%.'},
        {'threshold': 8, 'text': '(8) Set: Improves your chance to get a critical strike by 2%.'}
    ]
}

octo_sets['2003'] = {
    'id': 2003,
    'name': 'Armor of Wrath',
    'pieces': [47248, 47249, 47250, 47251, 47252, 47253, 47254, 47255],
    'bonuses': [
        {'threshold': 3, 'text': '(3) Set: Increases attack power by 30.'},
        {'threshold': 5, 'text': '(5) Set: Increases your skill with Swords, Axes, and Maces by 5.'},
        {'threshold': 8, 'text': '(8) Set: Improves your chance to get a critical strike by 2%.'}
    ]
}

octo_sets['3002'] = {
    'id': 3002,
    'name': 'Armor of the Dreadnaught',
    'pieces': [47261, 47262, 47263, 47264, 47265, 47266, 47267, 47268, 47269],
    'bonuses': [
        {'threshold': 2, 'text': '(2) Set: Increases the damage done by your Bloodthirst ability by 10%.'},
        {'threshold': 4, 'text': '(4) Set: Improves your chance to hit by 2%.'},
        {'threshold': 6, 'text': '(6) Set: Improves your chance to get a critical strike by 2%.'},
        {'threshold': 8, 'text': '(8) Set: Your melee attacks have a chance to increase your melee attack power by 200 for 10 sec.'}
    ]
}

item_to_set = {}
for sid_str, s in octo_sets.items():
    sid = int(sid_str)
    set_obj = {
        'id': sid,
        'name': s['name'],
        'pieces': list(s.get('pieces', [])),
        'bonuses': list(s.get('bonuses', []))
    }
    for p in s.get('pieces', []):
        item_to_set[p] = set_obj

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db.get('items', [])
filtered_items = [it for it in items if it['id'] < 100000]

has_47240 = any(it['id'] == 47240 for it in filtered_items)
if not has_47240:
    filtered_items.append({
        'id': 47240,
        'name': 'Crown of Might',
        'icon': 'INV_Helmet_09',
        'slot': 'head',
        'subclass': 'plate',
        'quality': 4,
        'item_level': 66,
        'req_level': 60,
        'armor': 608,
        'durability': 100,
        'unique': False,
        'bonding': 1,
        'speed': 0.0,
        'min_damage': 0.0,
        'max_damage': 0.0,
        'dps': 0.0,
        'strength': 30,
        'agility': 14,
        'stamina': 16,
        'intellect': 0,
        'spirit': 0,
        'resistances': {'holy': 0, 'fire': 10, 'nature': 0, 'frost': 0, 'shadow': 0, 'arcane': 0},
        'attack_power': 0,
        'spell_power': 0,
        'healing': 0,
        'crit': 0.0,
        'hit': 0.0,
        'spells': [],
        'set_id': 1003,
        'set': octo_sets['1003'],
        'classes': ['warrior']
    })

for it in filtered_items:
    iid = it['id']
    if iid in item_to_set:
        it['set_id'] = item_to_set[iid]['id']
        it['set'] = item_to_set[iid]
    else:
        it['set_id'] = 0
        it['set'] = None

by_id = {str(it['id']): it for it in filtered_items}
by_slot = {}
for it in filtered_items:
    slot = it.get('slot', 'misc')
    if slot not in by_slot:
        by_slot[slot] = []
    by_slot[slot].append(it['id'])

new_db = {
    'items': filtered_items,
    'by_id': by_id,
    'by_slot': by_slot
}

with open('data/octo_sets.json', 'w', encoding='utf-8') as f:
    json.dump(octo_sets, f, indent=2)

with open('items_db.json', 'w', encoding='utf-8') as f:
    json.dump(new_db, f, indent=2)

print(f"Purged ghost items. Final items count: {len(filtered_items)}")
print(f"Cleaned sets in octo_sets.json. Total sets: {len(octo_sets)}")
