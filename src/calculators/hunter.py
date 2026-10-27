from typing import Any, Dict, List, Optional, Union

from src.items_db import calculate_gear_totals, load_items_db
from .base import BaseCombatCalculator


class HunterCombatCalculator(BaseCombatCalculator):

    def __init__(self, db: Optional[Dict] = None):
        self.db = db if db is not None else load_items_db()

    def calculate(
        self,
        equipped_items: List[Union[int, str, Dict]],
        fight_duration: float = 60.0,
        haste_percent: float = 0.0,
        target_armor: float = 3731.0,
        pet_active: bool = True,
        quiver_haste: float = 14.0,
        ammo_dps: float = 17.5,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        item_ids = [it if isinstance(it, (int, str)) else it.get("id") for it in equipped_items]
        gear = calculate_gear_totals(item_ids, self.db)

        ranged_weapon = None
        for it in gear["equipped_items"]:
            if it.get("slot") == "ranged":
                ranged_weapon = it
                break

        weapon_name = ranged_weapon.get("name", "Standard Bow") if ranged_weapon else "Default Bow"
        base_speed = ranged_weapon.get("speed", 2.8) if ranged_weapon else 2.8
        min_dmg = ranged_weapon.get("min_damage", 75.0) if ranged_weapon else 75.0
        max_dmg = ranged_weapon.get("max_damage", 140.0) if ranged_weapon else 140.0
        avg_ranged_dmg = (min_dmg + max_dmg) / 2.0

        total_haste = haste_percent + quiver_haste
        effective_speed = base_speed / (1.0 + (total_haste / 100.0))

        rap = gear.get("ranged_attack_power", 0) + gear["attack_power"] + (gear["agility"] * 2)
        ranged_crit = gear["crit"] + (gear["agility"] / 53.0)
        hit_pct = gear["hit"]

        exact_shots = 1 + int(fight_duration / effective_speed) if fight_duration > 0 and effective_speed > 0 else 0

        armor_reduction = target_armor / (target_armor + 5500.0) if target_armor > 0 else 0.0
        crit_multiplier = 1.0 + (ranged_crit / 100.0)

        raw_auto_shot = avg_ranged_dmg + (rap / 14.0) * base_speed + (ammo_dps * base_speed)
        avg_auto_hit = raw_auto_shot * (1.0 - armor_reduction) * crit_multiplier
        auto_shot_damage = exact_shots * avg_auto_hit
        auto_shot_dps = auto_shot_damage / fight_duration if fight_duration > 0 else 0.0

        aimed_cooldown = 6.0
        aimed_count = int(fight_duration / aimed_cooldown) if fight_duration > 0 else 0
        raw_aimed = avg_ranged_dmg + (rap / 14.0) * 2.8 + (ammo_dps * 2.8) + 600.0
        avg_aimed_hit = raw_aimed * (1.0 - armor_reduction) * crit_multiplier
        aimed_damage = aimed_count * avg_aimed_hit
        aimed_dps = aimed_damage / fight_duration if fight_duration > 0 else 0.0

        multi_cooldown = 10.0
        multi_count = int(fight_duration / multi_cooldown) if fight_duration > 0 else 0
        raw_multi = avg_ranged_dmg + (rap / 14.0) * 2.8 + (ammo_dps * 2.8) + 120.0
        avg_multi_hit = raw_multi * (1.0 - armor_reduction) * crit_multiplier
        multi_damage = multi_count * avg_multi_hit
        multi_dps = multi_damage / fight_duration if fight_duration > 0 else 0.0

        serpent_dps = 37.0
        serpent_damage = serpent_dps * fight_duration

        own_damage_total = auto_shot_damage + aimed_damage + multi_damage + serpent_damage
        own_dps = own_damage_total / fight_duration if fight_duration > 0 else 0.0

        base_pet_dps = 85.0 if pet_active else 0.0
        pet_scaling_dps = (rap * 0.12) if pet_active else 0.0
        pet_dps = base_pet_dps + pet_scaling_dps
        pet_damage_total = pet_dps * fight_duration

        total_dps = own_dps + pet_dps
        total_damage = own_damage_total + pet_damage_total

        return {
            "character_class": "hunter",
            "fight_duration": fight_duration,
            "weapon_name": weapon_name,
            "base_weapon_speed": base_speed,
            "effective_weapon_speed": round(effective_speed, 2),
            "exact_melee_swings": exact_shots,
            "total_attack_power": rap,
            "total_spell_power": gear["spell_power"],
            "healing_power": gear["healing"],
            "total_crit_percent": round(ranged_crit, 2),
            "total_hit_percent": round(hit_pct, 2),
            "total_magic_hits": exact_shots + aimed_count + multi_count,
            "magic_hits_per_second": round((exact_shots + aimed_count + multi_count) / fight_duration, 3),
            "procs_per_second": 0.0,
            "expected_active_minions": 1.0 if pet_active else 0.0,
            "own_damage_breakdown": {
                "auto_shot_dps": round(auto_shot_dps, 2),
                "aimed_shot_dps": round(aimed_dps, 2),
                "multi_shot_dps": round(multi_dps, 2),
                "serpent_sting_dps": round(serpent_dps, 2),
            },
            "own_dps": round(own_dps, 2),
            "own_damage_total": round(own_damage_total, 2),
            "minion_dps": round(pet_dps, 2),
            "minion_dps_min": round(pet_dps * 0.9, 2),
            "minion_dps_max": round(pet_dps * 1.1, 2),
            "minion_damage_total": round(pet_damage_total, 2),
            "total_dps": round(total_dps, 2),
            "total_damage": round(total_damage, 2),
            "gear_summary": {
                "raw_attack_power": gear["attack_power"],
                "ranged_attack_power": rap,
                "strength": gear["strength"],
                "agility": gear["agility"],
                "stamina": gear["stamina"],
                "intellect": gear["intellect"],
                "armor": gear["armor"],
                "equipped_count": len(gear["equipped_items"]),
            },
        }
