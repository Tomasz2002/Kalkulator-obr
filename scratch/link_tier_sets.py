import json

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

with open('items_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

set_keywords = {
    '209': 'of Might',
    '218': 'of Wrath',
    '217': 'Judgement',
    '208': 'Lawbringer',
    '213': 'Netherwind',
    '201': 'Arcanist',
    '212': 'Bloodfang',
    '205': 'Shadowcraft',
    '204': 'Nightslayer',
    '207': 'Giantstalker',
    '215': 'Dragonstalker',
    '206': 'Prophecy',
    '211': 'Transcendence',
    '202': 'Felheart',
    '214': 'Nemesis',
    '210': 'Earthfury',
    '216': 'Ten Storms',
    '203': 'Cenarion',
    '215': 'Stormrage'
}

linked = 0
for sid, kw in set_keywords.items():
    if sid in octo_sets:
        sdata = octo_sets[sid]
        sname = sdata['name'].replace(' - Item sets', '').strip()
        set_info = {
            'id': int(sid),
            'name': sname,
            'pieces': sdata.get('pieces', []),
            'bonuses': sdata.get('bonuses', [])
        }
        for item in db['items']:
            if kw in item['name']:
                if item['id'] not in set_info['pieces']:
                    set_info['pieces'].append(item['id'])
                item['set_id'] = int(sid)
                item['set'] = set_info
                linked += 1

print(f"Linked {linked} items to sets!")

with open('items_db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2)

with open('data/octo_sets.json', 'w', encoding='utf-8') as f:
    json.dump(octo_sets, f, indent=2)

print("Saved updated sets and items_db!")
