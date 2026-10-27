import re
import json

with open('WarriorSim-TurtleWoW-master/js/data/gear_turtle.js', 'r', encoding='utf-8') as f:
    text = f.read()

slot_names = ['head', 'shoulder', 'chest', 'wrist', 'hands', 'waist', 'legs', 'feet', 'finger', 'neck', 'back', 'trinket', 'mainhand', 'offhand', 'twohand', 'ranged']

found_items = {}
for slot in slot_names:
    pattern = re.compile(rf'"{slot}":\s*\[(.*?)\]\s*,', re.DOTALL)
    m = pattern.search(text)
    if not m:
        continue
    slot_text = m.group(1)
    item_blocks = slot_text.split('},')
    for b in item_blocks:
        id_m = re.search(r'"id":\s*(\d+)', b)
        name_m = re.search(r'"name":\s*"([^"]+)"', b)
        if id_m and name_m:
            iid = int(id_m.group(1))
            name = name_m.group(1)
            if (47248 <= iid <= 47255) or (47261 <= iid <= 47269):
                str_m = re.search(r'"str":\s*(\d+)', b)
                agi_m = re.search(r'"agi":\s*(\d+)', b)
                sta_m = re.search(r'"sta":\s*(\d+)', b)
                ap_m = re.search(r'"ap":\s*(\d+)', b)
                crit_m = re.search(r'"crit":\s*(\d+)', b)
                hit_m = re.search(r'"hit":\s*(\d+)', b)
                ac_m = re.search(r'"ac":\s*(\d+)', b)
                found_items[iid] = {
                    'id': iid,
                    'name': name,
                    'slot': slot,
                    'subclass': 'plate' if slot not in ('finger', 'neck', 'back', 'trinket') else 'misc',
                    'quality': 4,
                    'item_level': 76 if iid <= 47255 else 86,
                    'req_level': 60,
                    'armor': int(ac_m.group(1)) if ac_m else 0,
                    'durability': 100,
                    'unique': False,
                    'bonding': 1,
                    'speed': 0.0,
                    'min_damage': 0.0,
                    'max_damage': 0.0,
                    'dps': 0.0,
                    'strength': int(str_m.group(1)) if str_m else 0,
                    'agility': int(agi_m.group(1)) if agi_m else 0,
                    'stamina': int(sta_m.group(1)) if sta_m else 0,
                    'intellect': 0,
                    'spirit': 0,
                    'resistances': {'holy': 0, 'fire': 10, 'nature': 0, 'frost': 0, 'shadow': 0, 'arcane': 0},
                    'attack_power': int(ap_m.group(1)) if ap_m else 0,
                    'spell_power': 0,
                    'healing': 0,
                    'crit': float(crit_m.group(1)) if crit_m else 0.0,
                    'hit': float(hit_m.group(1)) if hit_m else 0.0,
                    'spells': [],
                    'classes': ['warrior']
                }

print(f'Found {len(found_items)} DPS items from WarriorSim')
for iid in sorted(found_items.keys()):
    it = found_items[iid]
    print(f"{iid}: {it['name']} ({it['slot']}) str={it['strength']} agi={it['agility']} ap={it['attack_power']} crit={it['crit']} hit={it['hit']}")

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

existing_ids = {it['id'] for it in db['items']}
added_count = 0
for iid, it in found_items.items():
    if iid not in existing_ids:
        if iid <= 47255:
            it['set_id'] = 2003
            it['set'] = octo_sets.get('2003')
            it['icon'] = 'INV_Helmet_09' if it['slot'] == 'head' else 'INV_Shoulder_02' if it['slot'] == 'shoulder' else 'INV_Chest_Plate04' if it['slot'] == 'chest' else 'INV_Bracer_07' if it['slot'] == 'wrist' else 'INV_Gauntlets_10' if it['slot'] == 'hands' else 'INV_Belt_09' if it['slot'] == 'waist' else 'INV_Pants_Plate_05' if it['slot'] == 'legs' else 'INV_Boots_Plate_01'
        else:
            it['set_id'] = 3002
            it['set'] = octo_sets.get('3002')
            it['icon'] = 'INV_Helmet_09' if it['slot'] == 'head' else 'INV_Shoulder_02' if it['slot'] == 'shoulder' else 'INV_Chest_Plate04' if it['slot'] == 'chest' else 'INV_Bracer_07' if it['slot'] == 'wrist' else 'INV_Gauntlets_10' if it['slot'] == 'hands' else 'INV_Belt_09' if it['slot'] == 'waist' else 'INV_Pants_Plate_05' if it['slot'] == 'legs' else 'INV_Boots_Plate_01' if it['slot'] == 'feet' else 'INV_Jewelry_Ring_03'
        db['items'].append(it)
        added_count += 1

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

print(f'Added {added_count} items to items_db. Total items now: {len(db["items"])}')
