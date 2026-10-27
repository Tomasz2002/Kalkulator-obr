import sys
sys.path.insert(0, '.')

import json
from src.calculators.warrior import WarriorCombatCalculator

calc = WarriorCombatCalculator()

might_dps_items = [47240, 47241, 47242, 47243, 47244, 47245, 47246, 47247, 19019]
res_might = calc.calculate(equipped_items=might_dps_items, race="human", talents={"Bloodthirst": 1, "Cruelty": 5, "Flurry": 5})
print("Armor of Might result:")
print(f"  DPS: {res_might['total_dps']}, AP: {res_might['total_attack_power']}, Crit%: {res_might['total_crit_percent']}, Hit%: {res_might['total_hit_percent']}")
for sid, s in res_might['active_sets'].items():
    print(f"  Set {sid}: {s['name']} ({s['equipped_count']}/{s['total_pieces']})")
    for b in s['active_bonuses']:
        print(f"    {b['text']}")

wrath_dps_items = [47248, 47249, 47250, 47251, 47252, 47253, 47254, 47255, 19019]
res_wrath = calc.calculate(equipped_items=wrath_dps_items, race="human", talents={"Bloodthirst": 1, "Cruelty": 5, "Flurry": 5})
print("\nArmor of Wrath result:")
print(f"  DPS: {res_wrath['total_dps']}, Weapon Skill: {res_wrath['weapon_skill']}, AP: {res_wrath['total_attack_power']}, Crit%: {res_wrath['total_crit_percent']}, Hit%: {res_wrath['total_hit_percent']}")
for sid, s in res_wrath['active_sets'].items():
    print(f"  Set {sid}: {s['name']} ({s['equipped_count']}/{s['total_pieces']})")
    for b in s['active_bonuses']:
        print(f"    {b['text']}")
