import urllib.request, json

payload = {
    "character_class": "warrior",
    "equipped_items": [47242, 19364],
    "race": "human",
    "fight_duration": 60.0,
    "boss_hp_percent": 100.0,
    "execute_phase_percent": 20.0,
    "talents": {
        "Cruelty": 5,
        "Flurry": 5,
        "Bloodthirst": 1,
        "Deep Wounds": 3,
        "Two-Handed Weapon Specialization": 5
    },
    "enchants": {
        "chest": 20025,
        "mainhand": 20034
    }
}

req = urllib.request.Request(
    'http://127.0.0.1:5000/api/simulate',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("Character Class:", data.get("character_class"))
    print("Race:", data.get("race"))
    print("Main Weapon:", data.get("main_weapon_name"))
    print("Total DPS:", data.get("total_dps"))
    print("Own DPS:", data.get("own_dps"))
    print("Own Breakdown:", data.get("own_damage_breakdown"))
    print("Weapon skill:", data.get("weapon_skill"))
    print("Flurry uptime %:", data.get("flurry_uptime_percent"))
