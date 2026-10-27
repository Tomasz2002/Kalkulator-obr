import json

with open('data/octo_sets.json', 'r', encoding='utf-8') as f:
    octo_sets = json.load(f)

true_sets = {
    "208": {
        "id": 208,
        "name": "Lawbringer Armor",
        "pieces": [16858, 16859, 16857, 16853, 16860, 16854, 16855, 16856],
        "bonuses": [
            {"threshold": 3, "text": "(3) Set: Increases healing done by spells and effects by up to 31."},
            {"threshold": 5, "text": "(5) Set: Improves your chance to get a critical strike with spells by 2%."},
            {"threshold": 8, "text": "(8) Set: Gives the Paladin a chance on every melee hit to heal your party for 189 to 211."}
        ]
    },
    "1004": {
        "id": 1004,
        "name": "Lawbringer Battleplate",
        "pieces": [47000, 47001, 47002, 47003, 47004, 47005, 47006, 47007],
        "bonuses": [
            {"threshold": 3, "text": "(3) Set: Reduces the cost of Consecration by 20%."},
            {"threshold": 5, "text": "(5) Set: Increases your chance to block attacks with a shield by 2%."},
            {"threshold": 8, "text": "(8) Set: Gives the Paladin a chance on each melee hit to burst with Holy radiance, dealing an additional 90 Holy damage to the target."}
        ]
    },
    "1005": {
        "id": 1005,
        "name": "Lawbringer Battlegear",
        "pieces": [47008, 47009, 47010, 47011, 47012, 47013, 47014, 47015],
        "bonuses": [
            {"threshold": 3, "text": "(3) Set: Judgement of Righteousness and Judgement of Command deal an additional 148 Holy damage."},
            {"threshold": 5, "text": "(5) Set: Improves your chance to get a critical strike by 2%."},
            {"threshold": 8, "text": "(8) Set: Gives the Paladin a chance on each melee hit to burst with Holy radiance, dealing an additional 112 Holy damage to the target."}
        ]
    },
    "217": {
        "id": 217,
        "name": "Judgement Armor",
        "pieces": [16952, 16951, 16958, 16955, 16956, 16954, 16957, 16953],
        "bonuses": [
            {"threshold": 3, "text": "(3) Set: Increases healing done by spells and effects by up to 57."},
            {"threshold": 5, "text": "(5) Set: Reduces the mana cost of your Holy Light spell by 15%."},
            {"threshold": 8, "text": "(8) Set: Whenever you critically heal a target, you have a chance to heal them for an additional 300 health."}
        ]
    },
    "2004": {
        "id": 2004,
        "name": "Judgement Battleplate",
        "pieces": [47016, 47017, 47018, 47019, 47020, 47021, 47022, 47023],
        "bonuses": [
            {"threshold": 3, "text": "(3) Set: Adds 3 Holy damage to your melee attacks."},
            {"threshold": 5, "text": "(5) Set: Increases damage and healing done by magical spells and effects by up to 27."},
            {"threshold": 8, "text": "(8) Set: Whenever you block an attack, you have a chance to increase the block value of your next block by 200."}
        ]
    },
    "2005": {
        "id": 2005,
        "name": "Judgement Battlegear",
        "pieces": [47024, 47025, 47026, 47027, 47028, 47029, 47030, 47031],
        "bonuses": [
            {"threshold": 3, "text": "(3) Set: Adds 3 Holy damage to your melee attacks."},
            {"threshold": 5, "text": "(5) Set: Increases damage and healing done by magical spells and effects by up to 27."},
            {"threshold": 8, "text": "(8) Set: Chance to deal 300 additional Holy damage whenever you cause a critical hit in melee."}
        ]
    },
    "528": {
        "id": 528,
        "name": "Redemption Armor",
        "pieces": [22430, 22431, 22426, 22428, 22427, 22429, 22425, 22424, 23066],
        "bonuses": [
            {"threshold": 2, "text": "(2) Set: Increases the amount healed by your Judgement of Light by 20 and Flash of Light by 60."},
            {"threshold": 4, "text": "(4) Set: Reduces cooldown on your Lay on Hands by 12 min."},
            {"threshold": 6, "text": "(6) Set: Your Flash of Light, Holy Light and Holy Shock spells have a chance to imbue your target with Holy Power."},
            {"threshold": 8, "text": "(8) Set: Your Cleanse spell also heals the target for 200."}
        ]
    },
    "3004": {
        "id": 3004,
        "name": "Redemption Battleplate",
        "pieces": [70571, 70572, 70573, 70574, 70575, 70576, 70577, 70578, 70579],
        "bonuses": [
            {"threshold": 2, "text": "(2) Set: Increases your chance to block attacks with a shield by 3%."},
            {"threshold": 4, "text": "(4) Set: Increases the block value of your shield by 32."},
            {"threshold": 6, "text": "(6) Set: Reduces the cooldown of Exorcism by 5 seconds."},
            {"threshold": 8, "text": "(8) Set: Increases damage and healing done by magical spells and effects by up to 57."}
        ]
    },
    "3005": {
        "id": 3005,
        "name": "Redemption Battlegear",
        "pieces": [70580, 70581, 70582, 70583, 70584, 70585, 70586, 70587, 70588],
        "bonuses": [
            {"threshold": 2, "text": "(2) Set: Improves your chance to get a critical strike by 3%."},
            {"threshold": 4, "text": "(4) Set: Increases your attack and casting speed by 2%."},
            {"threshold": 6, "text": "(6) Set: Reduces the cooldown of Exorcism by 5 seconds."},
            {"threshold": 8, "text": "(8) Set: Increases damage and healing done by magical spells and effects by up to 57."}
        ]
    },
    "209": {
        "id": 209,
        "name": "Battlegear of Might",
        "pieces": [16864, 16861, 16865, 16863, 16866, 16867, 16868, 16862],
        "bonuses": [
            {"threshold": 3, "text": "(3) Set: Increases the block value of your shield by 30."},
            {"threshold": 5, "text": "(5) Set: Gives you a 20% chance to generate an additional Rage point whenever damage is dealt to you."},
            {"threshold": 8, "text": "(8) Set: Increases the threat generated by Sunder Armor by 15%."}
        ]
    },
    "1003": {
        "id": 1003,
        "name": "Armor of Might",
        "pieces": [47240, 47241, 47242, 47243, 47244, 47245, 47246, 47247],
        "bonuses": [
            {"threshold": 3, "text": "(3) Set: Whenever you hit with an ability, you have a chance to gain 10 Rage."},
            {"threshold": 5, "text": "(5) Set: Your Bloodthirst and Mortal Strike abilities cost 10 less Rage."},
            {"threshold": 8, "text": "(8) Set: Increases your Critical Strike chance by 2% when in Berserker Stance."}
        ]
    },
    "218": {
        "id": 218,
        "name": "Battlegear of Wrath",
        "pieces": [16959, 16966, 16964, 16963, 16962, 16961, 16965, 16960],
        "bonuses": [
            {"threshold": 3, "text": "(3) Set: Increases the attack power granted by Battle Shout by 30."},
            {"threshold": 5, "text": "(5) Set: 20% chance after using an offensive ability requiring rage that your next offensive ability requires 5 less rage to use."},
            {"threshold": 8, "text": "(8) Set: 4% chance to parry the next attack after a block."}
        ]
    },
    "2003": {
        "id": 2003,
        "name": "Armor of Wrath",
        "pieces": [47248, 47249, 47250, 47251, 47252, 47253, 47254, 47255],
        "bonuses": [
            {"threshold": 3, "text": "(3) Set: Your Overpower ability now increases your attack speed by 30% for 6 sec."},
            {"threshold": 5, "text": "(5) Set: +5 to All Weapons."},
            {"threshold": 8, "text": "(8) Set: Whirlwind now hits 2 additional targets."}
        ]
    },
    "523": {
        "id": 523,
        "name": "Dreadnaught's Battlegear",
        "pieces": [22423, 22416, 22421, 22422, 22418, 22417, 22419, 22420, 23059],
        "bonuses": [
            {"threshold": 2, "text": "(2) Set: Increases the damage done by your Revenge ability by 75."},
            {"threshold": 4, "text": "(4) Set: Improves your chance to hit with Taunt and Challenging Shout by 5%."},
            {"threshold": 6, "text": "(6) Set: Improves your chance to hit with Sunder Armor, Heroic Strike, Revenge, and Shield Slam by 5%."},
            {"threshold": 8, "text": "(8) Set: When your health drops below 20%, for the next 5 seconds healing spells cast on you help you to Cheat Death, increasing healing done by up to 160."}
        ]
    }
}

for k, v in true_sets.items():
    octo_sets[k] = v

with open('data/octo_sets.json', 'w', encoding='utf-8') as f:
    json.dump(octo_sets, f, indent=2, ensure_ascii=False)

with open('items_db.json', 'r', encoding='utf-8') as f:
    items_db = json.load(f)

items_list = items_db.get('items', [])
by_id = items_db.get('by_id', {})

updated_count = 0
for it in items_list:
    item_id = it.get('id')
    set_id = str(it.get('set_id')) if it.get('set_id') is not None else None
    
    if not set_id:
        for sid, sdata in true_sets.items():
            if item_id in sdata['pieces']:
                set_id = sid
                it['set_id'] = int(sid)
                break
                
    if set_id and set_id in true_sets:
        sdata = true_sets[set_id]
        it['set'] = sdata
        it['set_name'] = sdata['name']
        it['set_id'] = int(set_id)
        if str(item_id) in by_id:
            by_id[str(item_id)]['set'] = sdata
            by_id[str(item_id)]['set_name'] = sdata['name']
            by_id[str(item_id)]['set_id'] = int(set_id)
        updated_count += 1

items_db['items'] = items_list
items_db['by_id'] = by_id

with open('items_db.json', 'w', encoding='utf-8') as f:
    json.dump(items_db, f, indent=2, ensure_ascii=False)

print(f'Updated {updated_count} items with true Turtle WoW set bonuses!')
