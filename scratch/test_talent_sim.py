import urllib.request
import json

payload = {
    "equipped_items": [47024, 60790, 16953, 13340, 16958, 16951, 60799, 16952, 47022, 16957, 17063, 19397, 60809, 11815, 11684, 12602, 58240],
    "fight_duration": 60.0,
    "haste_percent": 0.0,
    "target_armor": 3731.0,
    "judgement_interval": 10.0,
    "exorcism_interval": 15.0,
    "t2_bonus_active": True,
    "lost_set_active": True,
    "consecration": True,
    "talents": {
        "Divine Strength": 5,
        "Improved Seal of Righteousness": 5,
        "Improved Blessings": 5,
        "Benediction": 5,
        "Improved Judgement": 2,
        "Improved Seal of the Crusader": 3,
        "Deflection": 3,
        "Conviction": 5,
        "Blessing of Kings": 1,
        "Two-Handed Weapon Specialization": 3,
        "Vindication": 3,
        "Vengeance": 5,
        "Seal of Command": 1,
        "Vengeful Strikes": 5
    }
}

req = urllib.request.Request("http://127.0.0.1:5000/api/simulate", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    print("Simulation result with Octo WoW talents:")
    print("Total DPS:", data["total_dps"])
    print("Own DPS:", data["own_dps"])
    print("Minion DPS:", data["minion_dps"])
    print("Has minions:", data["has_minions"])
    print("Melee swings:", data["exact_melee_swings"])
    print("Magic hits:", data["total_magic_hits"])
