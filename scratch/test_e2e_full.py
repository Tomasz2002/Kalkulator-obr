import urllib.request, json

BASE = 'http://127.0.0.1:5000'

def test_url(url, method='GET', data=None):
    req = urllib.request.Request(
        f'{BASE}{url}',
        data=json.dumps(data).encode('utf-8') if data else None,
        headers={'Content-Type': 'application/json'} if data else {}
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read().decode('utf-8')

status, html = test_url('/')
assert status == 200 and '<title>' in html
print("1. Index page loads OK (200)")

status, _ = test_url('/static/style.css')
assert status == 200
print("2. style.css loads OK (200)")

status, _ = test_url('/static/app.js')
assert status == 200
print("3. app.js loads OK (200)")

status, raw = test_url('/api/talents?class=warrior')
assert status == 200
w_talents = json.loads(raw)
assert w_talents['trees'] == ['Arms', 'Fury', 'Protection']
assert len(w_talents['talents']) == 54
assert len(w_talents['builds']) == 3
print(f"4. Warrior talents API loads OK: {len(w_talents['talents'])} talents, {len(w_talents['builds'])} builds")

status, raw = test_url('/api/races')
assert status == 200
races = json.loads(raw)
assert len(races['warrior']) == 8
assert len(races['paladin']) == 3
print(f"5. Races API loads OK: {len(races['warrior'])} warrior races, {len(races['paladin'])} paladin races")

status, raw = test_url('/api/enchants')
assert status == 200
ench = json.loads(raw)
assert 'mainhand' in ench and 'ranged' in ench and 'chest' in ench
print(f"6. Enchants API loads OK: {len(ench)} slots available")

status, raw = test_url('/api/items?class=warrior')
assert status == 200
items_data = json.loads(raw)
chest_might = [it for it in items_data['items'] if it['id'] == 47242]
assert len(chest_might) == 1
print(f"7. Custom Octo WoW item 47242 ({chest_might[0]['name']}) found in items API!")

sim_warrior_dw = {
    "character_class": "warrior",
    "equipped_items": [47242, 11684, 11684],
    "race": "orc",
    "fight_duration": 60.0,
    "boss_hp_percent": 100.0,
    "execute_phase_percent": 20.0,
    "talents": {
        "Cruelty": 5,
        "Flurry": 5,
        "Bloodthirst": 1,
        "Dual Wield Specialization": 5,
        "Deep Wounds": 3
    },
    "enchants": {
        "chest": 20025,
        "mainhand": 20034,
        "offhand": 20034
    }
}
status, raw = test_url('/api/simulate', method='POST', data=sim_warrior_dw)
assert status == 200
res_dw = json.loads(raw)
assert res_dw['is_dual_wield'] == True
assert res_dw['weapon_skill'] == 300
print(f"8. Warrior Dual Wield sim OK: DPS={res_dw['total_dps']}, swings={res_dw['exact_melee_swings']}, Breakdown={res_dw['own_damage_breakdown']}")

sim_warrior_exec = {
    "character_class": "warrior",
    "equipped_items": [47242, 19364],
    "race": "human",
    "fight_duration": 60.0,
    "boss_hp_percent": 15.0,
    "talents": {
        "Cruelty": 5,
        "Flurry": 5,
        "Bloodthirst": 1,
        "Two-Handed Weapon Specialization": 5,
        "Improved Execute": 2,
        "Impale": 2
    }
}
status, raw = test_url('/api/simulate', method='POST', data=sim_warrior_exec)
assert status == 200
res_exec = json.loads(raw)
assert res_exec['weapon_skill'] == 305
assert res_exec['own_damage_breakdown']['execute_dps'] > 0
print(f"9. Warrior Execute phase sim (<20% HP) OK: DPS={res_exec['total_dps']}, Execute DPS={res_exec['own_damage_breakdown']['execute_dps']}")

sim_paladin_exec = {
    "character_class": "paladin",
    "equipped_items": [19364],
    "race": "human",
    "fight_duration": 60.0,
    "boss_hp_percent": 20.0
}
status, raw = test_url('/api/simulate', method='POST', data=sim_paladin_exec)
assert status == 200
res_pal = json.loads(raw)
assert 'hammer_of_wrath_dps' in res_pal['own_damage_breakdown']
print(f"10. Paladin Execute phase sim (<20% HP) OK: DPS={res_pal['total_dps']}, Hammer of Wrath DPS={res_pal['own_damage_breakdown']['hammer_of_wrath_dps']}")

print("\nALL 10 TESTS PASSED PERFECTLY!")
