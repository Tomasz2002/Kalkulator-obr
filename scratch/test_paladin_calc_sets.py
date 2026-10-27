import sys
sys.path.insert(0, '.')
import json
from src.calculators.paladin import PaladinCombatCalculator

calc = PaladinCombatCalculator()

tests = [
    ("T1 Holy: Lawbringer Armor", [16858, 16859, 16857, 16853, 16860, 16854, 16855, 16856]),
    ("T1 Tank: Lawbringer Battleplate", [47000, 47001, 47002, 47003, 47004, 47005, 47006, 47007]),
    ("T1 DPS: Lawbringer Battlegear", [47008, 47009, 47010, 47011, 47012, 47013, 47014, 47015]),
    ("T2 Holy: Judgement Armor", [16952, 16951, 16958, 16955, 16956, 16954, 16957, 16953]),
    ("T2 Tank: Judgement Battleplate", [47016, 47017, 47018, 47019, 47020, 47021, 47022, 47023]),
    ("T2 DPS: Judgement Battlegear", [47024, 47025, 47026, 47027, 47028, 47029, 47030, 47031]),
    ("T3 Holy: Redemption Armor", [22430, 22431, 22426, 22428, 22427, 22429, 22425, 22424, 23066]),
    ("T3 Tank: Redemption Battleplate", [70571, 70572, 70573, 70574, 70575, 70576, 70577, 70578, 70579]),
    ("T3 DPS: Redemption Battlegear", [70580, 70581, 70582, 70583, 70584, 70585, 70586, 70587, 70588]),
]

for label, pieces in tests:
    res = calc.calculate(equipped_items=pieces, fight_duration=60.0)
    print(f"=== {label} ===")
    print(f"  Total DPS: {res['total_dps']}")
    print(f"  Active Sets: {[s['name'] + ' (' + str(s['equipped_count']) + '/' + str(s['total_pieces']) + ')' for s in res['active_sets'].values()]}")
    print(f"  Active Bonuses:")
    for sid, s in res['active_sets'].items():
        for b in s['active_bonuses']:
            print(f"    - {b['text']}")
    print(f"  Breakdown: {res['own_damage_breakdown']}")
