import json
import re

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

octo_sets['208'] = {
    'id': 208,
    'name': 'Lawbringer Armor',
    'pieces': [16858, 16856, 16853, 16857, 16860, 16854, 16855, 16859],
    'bonuses': [
        {'threshold': 3, 'text': '(3) Set: Increases the chance of triggering a Judgement of Light heal by 10%.'},
        {'threshold': 5, 'text': '(5) Set: Improves your chance to get a critical strike with spells and melee attacks by 1%.'},
        {'threshold': 8, 'text': '(8) Set: Gives the Paladin a chance on every melee hit to heal your party for 189 to 212.'}
    ]
}

octo_sets['1004'] = {
    'id': 1004,
    'name': "Lawbringer's Aegis",
    'pieces': [47000, 47001, 47002, 47003, 47004, 47005, 47006, 47007],
    'bonuses': [
        {'threshold': 3, 'text': '(3) Set: Increases defense by 15.'},
        {'threshold': 5, 'text': '(5) Set: Holy Shield gains 2 additional charges and increases block value by 30.'},
        {'threshold': 8, 'text': '(8) Set: Judgement of Righteousness increases your armor by 300 for 10 sec.'}
    ]
}

octo_sets['1005'] = {
    'id': 1005,
    'name': "Lawbringer's Battlegear",
    'pieces': [47008, 47009, 47010, 47011, 47012, 47013, 47014, 47015],
    'bonuses': [
        {'threshold': 3, 'text': '(3) Set: Increases attack power by 30.'},
        {'threshold': 5, 'text': '(5) Set: Improves your chance to get a critical strike with melee attacks and Holy spells by 1%.'},
        {'threshold': 8, 'text': '(8) Set: Gives the Paladin a chance on every melee hit to inflict 120 Holy damage.'}
    ]
}

octo_sets['217'] = {
    'id': 217,
    'name': 'Judgement Armor',
    'pieces': [16952, 16951, 16958, 16955, 16956, 16954, 16957, 16953],
    'bonuses': [
        {'threshold': 3, 'text': "(3) Set: Increases the radius of a Paladin's auras by 10."},
        {'threshold': 5, 'text': '(5) Set: Increases damage and healing done by magical spells and effects by up to 47.'},
        {'threshold': 8, 'text': "(8) Set: Inflicts 60 to 67 additional Holy damage on the target of a Paladin's Judgement."}
    ]
}

octo_sets['2004'] = {
    'id': 2004,
    'name': 'Judgement Aegis',
    'pieces': [47016, 47017, 47018, 47019, 47020, 47021, 47022, 47023],
    'bonuses': [
        {'threshold': 3, 'text': '(3) Set: Increases the radius of Paladin auras by 10 and increases defense by 10.'},
        {'threshold': 5, 'text': '(5) Set: When struck in combat, 20% chance to generate 150 additional threat and heal for 100.'},
        {'threshold': 8, 'text': '(8) Set: Increases block chance by 5% and Holy Shield damage by 20%.'}
    ]
}

octo_sets['2005'] = {
    'id': 2005,
    'name': 'Judgement Battlegear',
    'pieces': [47024, 47025, 47026, 47027, 47028, 47029, 47030, 47031],
    'bonuses': [
        {'threshold': 3, 'text': '(3) Set: Increases attack power by 30 and spell damage by 20.'},
        {'threshold': 5, 'text': '(5) Set: Improves your chance to get a critical strike by 2%.'},
        {'threshold': 8, 'text': "(8) Set: Inflicts 60 to 67 additional Holy damage on the target of a Paladin's Judgement."}
    ]
}

octo_sets['528'] = {
    'id': 528,
    'name': 'Redemption Armor',
    'pieces': [22428, 22429, 22425, 22424, 22426, 22431, 22427, 22430, 23066],
    'bonuses': [
        {'threshold': 2, 'text': '(2) Set: Increases the amount healed by your Judgement of Light by 20.'},
        {'threshold': 4, 'text': '(4) Set: Reduces cooldown on your Lay on Hands by 12 min.'},
        {'threshold': 6, 'text': '(6) Set: Your Flash of Light and Holy Light spells have a chance to imbue your target with Holy Power.'},
        {'threshold': 8, 'text': '(8) Set: Your Cleanse spell also heals the target for 200.'}
    ]
}

octo_sets['3004'] = {
    'id': 3004,
    'name': 'Redemption Aegis',
    'pieces': [70571, 70572, 70573, 70574, 70575, 70576, 70577, 70578, 70579],
    'bonuses': [
        {'threshold': 2, 'text': '(2) Set: Increases the armor granted by Devotion Aura by 25%.'},
        {'threshold': 4, 'text': '(4) Set: Reduces the cooldown of Holy Shield by 2 sec and Blessing of Protection by 1 min.'},
        {'threshold': 6, 'text': '(6) Set: Increases block chance by 5% and block value by 30.'},
        {'threshold': 8, 'text': '(8) Set: Judgement of Righteousness heals the Paladin for 100% of damage dealt and generates 100% extra threat.'}
    ]
}

octo_sets['3005'] = {
    'id': 3005,
    'name': 'Redemption Battlegear',
    'pieces': [70580, 70581, 70582, 70583, 70584, 70585, 70586, 70587, 70588],
    'bonuses': [
        {'threshold': 2, 'text': '(2) Set: Increases the damage of your Judgement of Command and Judgement of Righteousness by 10%.'},
        {'threshold': 4, 'text': '(4) Set: Increases your chance to get a critical strike with melee attacks and Holy spells by 2%.'},
        {'threshold': 6, 'text': '(6) Set: Gives the Paladin a chance on every melee attack to restore 150 mana.'},
        {'threshold': 8, 'text': '(8) Set: Increases attack power by 100 and spell power by 50.'}
    ]
}

with open('data/octo_sets.json', 'w', encoding='utf-8') as f:
    json.dump(octo_sets, f, indent=2, ensure_ascii=False)

print('Updated data/octo_sets.json successfully')

with open('scratch/paladin_custom_raw.json', 'r', encoding='utf-8') as f:
    custom_raw = json.load(f)

with open('items_db.json', 'r', encoding='utf-8') as f:
    items_db = json.load(f)

existing_items = items_db.get('items', [])

for it in existing_items:
    clean_spells = []
    for sp in it.get('spells', []):
        if sp.get('spell_id') == 1 or 'word of recall' in str(sp.get('text', '')).lower():
            continue
        clean_spells.append(sp)
    it['spells'] = clean_spells

item_dict = {it['id']: it for it in existing_items}

def parse_int(pattern, text, default=0):
    m = re.search(pattern, text)
    return int(m.group(1)) if m else default

def determine_set_info(iid):
    if 47000 <= iid <= 47007:
        return 1004, octo_sets['1004']
    if 47008 <= iid <= 47015:
        return 1005, octo_sets['1005']
    if 47016 <= iid <= 47023:
        return 2004, octo_sets['2004']
    if 47024 <= iid <= 47031:
        return 2005, octo_sets['2005']
    if 70571 <= iid <= 70579:
        return 3004, octo_sets['3004']
    if 70580 <= iid <= 70588:
        return 3005, octo_sets['3005']
    return 0, None

slot_map = {
    'head': 'head',
    'shoulder': 'shoulder',
    'chest': 'chest',
    'wrist': 'wrist',
    'hands': 'hands',
    'waist': 'waist',
    'legs': 'legs',
    'feet': 'feet',
    'finger': 'finger'
}

for iid_str, raw_data in custom_raw.items():
    iid = int(iid_str)
    name = raw_data.get('name', '')
    icon = raw_data.get('icon', '')
    tt = raw_data.get('tooltip', '')

    slot_match = re.search(r'<tr><td>(Head|Shoulder|Chest|Wrist|Hands|Waist|Legs|Feet|Finger)</td>', tt)
    slot_raw = slot_match.group(1).lower() if slot_match else 'head'
    slot = slot_map.get(slot_raw, 'head')

    subclass = 'finger' if slot == 'finger' else 'plate'

    armor = parse_int(r'(\d+)\s+Armor', tt)
    strength = parse_int(r'\+(\d+)\s+Strength', tt)
    agility = parse_int(r'\+(\d+)\s+Agility', tt)
    stamina = parse_int(r'\+(\d+)\s+Stamina', tt)
    intellect = parse_int(r'\+(\d+)\s+Intellect', tt)
    spirit = parse_int(r'\+(\d+)\s+Spirit', tt)

    fire_res = parse_int(r'\+(\d+)\s+Fire Resistance', tt)
    nature_res = parse_int(r'\+(\d+)\s+Nature Resistance', tt)
    frost_res = parse_int(r'\+(\d+)\s+Frost Resistance', tt)
    shadow_res = parse_int(r'\+(\d+)\s+Shadow Resistance', tt)
    arcane_res = parse_int(r'\+(\d+)\s+Arcane Resistance', tt)
    holy_res = parse_int(r'\+(\d+)\s+Holy Resistance', tt)

    durability = parse_int(r'Durability\s+(\d+)\s+/', tt, 100 if slot != 'finger' else 0)

    if 70571 <= iid <= 70588:
        item_level = 86
    elif 47016 <= iid <= 47031:
        item_level = 76
    else:
        item_level = 66

    spells = []
    crit_val = 0.0
    hit_val = 0.0
    spell_power_val = 0
    attack_power_val = 0

    found_spells = re.findall(r'Equip:\s*<a[^>]*spell=(\d+)[^>]*>(.*?)</a>', tt)
    for sid_str, stext in found_spells:
        sid = int(sid_str)
        if sid == 1 or 'word of recall' in stext.lower():
            continue
        clean_text = f"Equip: {stext.strip()}"
        spells.append({
            'spell_id': sid,
            'trigger': 1,
            'text': clean_text
        })
        crit_m = re.search(r'critical strike[^0-9]*(\d+)%', clean_text)
        if crit_m:
            crit_val += float(crit_m.group(1))
        hit_m = re.search(r'chance to hit[^0-9]*(\d+)%', clean_text)
        if hit_m:
            hit_val += float(hit_m.group(1))
        sp_m = re.search(r'magical spells and effects by up to (\d+)', clean_text)
        if sp_m:
            spell_power_val += int(sp_m.group(1))
        ap_m = re.search(r'attack power by (\d+)', clean_text)
        if ap_m:
            attack_power_val += int(ap_m.group(1))

    set_id, set_obj = determine_set_info(iid)

    item_obj = {
        'id': iid,
        'name': name,
        'icon': icon,
        'slot': slot,
        'subclass': subclass,
        'quality': 4,
        'item_level': item_level,
        'req_level': 60,
        'armor': armor,
        'durability': durability,
        'unique': False,
        'bonding': 1,
        'speed': 0.0,
        'min_damage': 0.0,
        'max_damage': 0.0,
        'dps': 0.0,
        'strength': strength,
        'agility': agility,
        'stamina': stamina,
        'intellect': intellect,
        'spirit': spirit,
        'resistances': {
            'holy': holy_res,
            'fire': fire_res,
            'nature': nature_res,
            'frost': frost_res,
            'shadow': shadow_res,
            'arcane': arcane_res
        },
        'attack_power': attack_power_val,
        'spell_power': spell_power_val,
        'healing': spell_power_val,
        'crit': crit_val,
        'hit': hit_val,
        'spells': spells,
        'set_id': set_id,
        'set': set_obj,
        'classes': ['paladin']
    }

    item_dict[iid] = item_obj

for sid_str in ['208', '217', '528']:
    s_obj = octo_sets[sid_str]
    for pid in s_obj['pieces']:
        if pid in item_dict:
            item_dict[pid]['set_id'] = int(sid_str)
            item_dict[pid]['set'] = s_obj
            if 'classes' not in item_dict[pid] or not item_dict[pid]['classes']:
                item_dict[pid]['classes'] = ['paladin']

merged_items = sorted(item_dict.values(), key=lambda x: x['id'])

by_id = {str(it['id']): it for it in merged_items}
by_slot = {}
for it in merged_items:
    s = it['slot']
    if s not in by_slot:
        by_slot[s] = []
    by_slot[s].append(it)

items_db['items'] = merged_items
items_db['by_id'] = by_id
items_db['by_slot'] = by_slot
if 'metadata' not in items_db:
    items_db['metadata'] = {}
items_db['metadata']['total_items'] = len(merged_items)

with open('items_db.json', 'w', encoding='utf-8') as f:
    json.dump(items_db, f, indent=2, ensure_ascii=False)

print(f"Successfully processed and merged {len(merged_items)} items into items_db.json")
