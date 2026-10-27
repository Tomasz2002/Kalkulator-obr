import json

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

items = db['items']

by_id = {str(it['id']): it for it in items}

it_47241 = by_id.get('47241')
if it_47241:
    it_47241['attack_power'] = 38
    if 'spells' not in it_47241 or not it_47241['spells']:
        it_47241['spells'] = []
    if not any(sp.get('spell_id') == 15808 for sp in it_47241['spells']):
        it_47241['spells'].append({
            'spell_id': 15808,
            'trigger': 1,
            'text': '+38 Attack Power.'
        })

it_47244 = by_id.get('47244')
if it_47244:
    it_47244['hit'] = 1.0
    if 'spells' not in it_47244 or not it_47244['spells']:
        it_47244['spells'] = []
    if not any(sp.get('spell_id') == 15464 for sp in it_47244['spells']):
        it_47244['spells'].append({
            'spell_id': 15464,
            'trigger': 1,
            'text': 'Equip: Improves your chance to hit by 1%.'
        })

it_47246 = by_id.get('47246')
if it_47246:
    it_47246['attack_power'] = 52
    if 'spells' not in it_47246 or not it_47246['spells']:
        it_47246['spells'] = []
    if not any(sp.get('spell_id') == 15812 for sp in it_47246['spells']):
        it_47246['spells'].append({
            'spell_id': 15812,
            'trigger': 1,
            'text': '+52 Attack Power.'
        })

it_47249 = by_id.get('47249')
if it_47249:
    it_47249['name'] = 'Spaulders of Wrath'
    if 'spells' not in it_47249 or not it_47249['spells']:
        it_47249['spells'] = []
    if not any(sp.get('spell_id') == 48030 for sp in it_47249['spells']):
        it_47249['spells'].append({
            'spell_id': 48030,
            'trigger': 1,
            'text': "Equip: Your attacks ignore 25 of the target's armor."
        })

it_47254 = by_id.get('47254')
if it_47254:
    it_47254['hit'] = 2.0
    it_47254['attack_power'] = 50
    if 'spells' not in it_47254 or not it_47254['spells']:
        it_47254['spells'] = []
    if not any(sp.get('spell_id') == 15465 for sp in it_47254['spells']):
        it_47254['spells'].append({
            'spell_id': 15465,
            'trigger': 1,
            'text': 'Equip: Improves your chance to hit by 2%.'
        })
    if not any(sp.get('spell_id') == 14056 for sp in it_47254['spells']):
        it_47254['spells'].append({
            'spell_id': 14056,
            'trigger': 1,
            'text': '+50 Attack Power.'
        })

filtered_items = [it for it in items if it.get('quality', 1) >= 2]

new_by_id = {}
new_by_slot = {}

for it in filtered_items:
    sid = str(it['id'])
    new_by_id[sid] = it
    slot = it.get('slot')
    if slot:
        if slot not in new_by_slot:
            new_by_slot[slot] = []
        new_by_slot[slot].append(it)

new_db = {
    'items': filtered_items,
    'by_id': new_by_id,
    'by_slot': new_by_slot
}

with open('items_db.json', 'w', encoding='utf-8') as f:
    json.dump(new_db, f, indent=2, ensure_ascii=False)

print(f"Successfully cleaned items_db.json: kept {len(filtered_items)} items (removed {len(items) - len(filtered_items)} white/gray items).")
