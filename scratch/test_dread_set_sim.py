import sys
sys.path.insert(0, '.')

from src.calculators.warrior import WarriorCombatCalculator

calc = WarriorCombatCalculator()

dread_dps_items = list(range(47261, 47270)) + [19019]
res_dread = calc.calculate(equipped_items=dread_dps_items, race="human", talents={"Bloodthirst": 1, "Cruelty": 5, "Flurry": 5})
print("Armor of the Dreadnaught result:")
print(f"  DPS: {res_dread['total_dps']}, AP: {res_dread['total_attack_power']}, Crit%: {res_dread['total_crit_percent']}, Hit%: {res_dread['total_hit_percent']}")
for sid, s in res_dread['active_sets'].items():
    print(f"  Set {sid}: {s['name']} ({s['equipped_count']}/{s['total_pieces']})")
    for b in s['active_bonuses']:
        print(f"    {b['text']}")
