from typing import Any, Dict, List, Optional, Union

from src.items_db import calculate_gear_totals, load_items_db
from .base import BaseCombatCalculator


class GenericCombatCalculator(BaseCombatCalculator):

    def __init__(self, class_name: str, db: Optional[Dict] = None):
        self.class_name = class_name.lower().strip()
        self.db = db if db is not None else load_items_db()

    def calculate(
        self,
        equipped_items: List[Union[int, str, Dict]],
        fight_duration: float = 60.0,
        haste_percent: float = 0.0,
        target_armor: float = 3731.0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        item_ids = [it if isinstance(it, (int, str)) else it.get("id") for it in equipped_items]
        gear = calculate_gear_totals(item_ids, self.db)

        str_val = gear["strength"]
        agi_val = gear["agility"]
        int_val = gear["intellect"]
        spi_val = gear["spirit"]
        sta_val = gear["stamina"]

        if self.class_name in ("warrior", "paladin"):
            ap = gear["attack_power"] + (str_val * 2)
            rap = gear["ranged_attack_power"] + gear["attack_power"] + agi_val
            crit_pct = gear["crit"] + (agi_val / 20.0)
        elif self.class_name in ("rogue", "hunter"):
            ap = gear["attack_power"] + str_val + agi_val
            rap = gear["ranged_attack_power"] + gear["attack_power"] + (agi_val * 2)
            crit_pct = gear["crit"] + (agi_val / 29.0 if self.class_name == "rogue" else agi_val / 53.0)
        elif self.class_name in ("druid", "shaman"):
            ap = gear["attack_power"] + (str_val * 2)
            rap = gear["ranged_attack_power"] + gear["attack_power"]
            crit_pct = gear["crit"] + (agi_val / 20.0)
        else:
            ap = gear["attack_power"] + str_val
            rap = gear["ranged_attack_power"] + gear["attack_power"]
            crit_pct = gear["crit"] + (agi_val / 20.0)

        sp = gear["spell_power"]
        heal = gear["healing"]
        hit_pct = gear["hit"]

        weapon_speed = gear["main_weapon_speed"] if gear["main_weapon_speed"] > 0 else 2.0
        effective_speed = weapon_speed / (1.0 + (haste_percent / 100.0))
        exact_melee_swings = 1 + int(fight_duration / effective_speed) if fight_duration > 0 and effective_speed > 0 else 0

        min_dmg = gear["main_weapon_min_dmg"]
        max_dmg = gear["main_weapon_max_dmg"]
        weapon_name = gear["main_weapon_name"]
        avg_weapon_dmg = (min_dmg + max_dmg) / 2.0 if (min_dmg + max_dmg) > 0 else (weapon_speed * 25.0)

        armor_reduction = target_armor / (target_armor + 5500.0) if target_armor > 0 else 0.0
        crit_chance = max(0.0, min(1.0, crit_pct / 100.0))
        crit_multiplier = 1.0 + crit_chance

        raw_swing_dmg = avg_weapon_dmg + (ap / 14.0) * weapon_speed
        avg_white_hit = raw_swing_dmg * (1.0 - armor_reduction) * crit_multiplier
        white_damage_total = exact_melee_swings * avg_white_hit
        white_dps = white_damage_total / fight_duration if fight_duration > 0 else 0.0

        spell_dps = 0.0
        spell_damage_total = 0.0
        if sp > 0 and self.class_name in ("mage", "warlock", "priest"):
            cast_time = 3.0
            casts = int(fight_duration / cast_time) if fight_duration > 0 else 0
            base_spell_dmg = 450.0 + (sp * 0.857)
            spell_crit_mult = 1.0 + (crit_chance * 0.5)
            avg_spell_hit = base_spell_dmg * spell_crit_mult
            spell_damage_total = casts * avg_spell_hit
            spell_dps = spell_damage_total / fight_duration if fight_duration > 0 else 0.0

        has_minions = gear.get("has_pet_summon", False)
        minion_dps_avg = 0.0
        minion_dps_min = 0.0
        minion_dps_max = 0.0
        minion_damage_total = 0.0
        expected_active_minions = 0.0

        if has_minions and "Spirit of Eskhandar" in gear.get("pet_summon_details", []):
            crit_swings_per_sec = (exact_melee_swings / fight_duration if fight_duration > 0 else 0.0) * crit_chance
            procs_per_sec = crit_swings_per_sec * 0.01
            expected_active_minions = min(1.0, procs_per_sec * 120.0)
            eskhandar_dps = 70.0 / 1.5
            minion_dps_avg = expected_active_minions * eskhandar_dps
            minion_dps_min = expected_active_minions * (60.0 / 1.5)
            minion_dps_max = expected_active_minions * (80.0 / 1.5)
            minion_damage_total = minion_dps_avg * fight_duration

        own_damage_total = white_damage_total + spell_damage_total
        own_dps = own_damage_total / fight_duration if fight_duration > 0 else 0.0
        total_dps = own_dps + minion_dps_avg
        total_damage = own_damage_total + minion_damage_total

        breakdown = {
            "white_melee_dps": round(white_dps, 2),
        }
        if spell_dps > 0:
            breakdown["primary_spell_dps"] = round(spell_dps, 2)

        return {
            "character_class": self.class_name,
            "fight_duration": fight_duration,
            "weapon_name": weapon_name,
            "base_weapon_speed": weapon_speed,
            "effective_weapon_speed": round(effective_speed, 2),
            "exact_melee_swings": exact_melee_swings,
            "total_attack_power": ap,
            "total_ranged_attack_power": rap,
            "total_spell_power": sp,
            "healing_power": heal,
            "total_crit_percent": round(crit_pct, 2),
            "total_hit_percent": round(hit_pct, 2),
            "resistances": gear["resistances"],
            "has_minions": has_minions,
            "expected_active_minions": round(expected_active_minions, 3),
            "active_sets": gear.get("active_sets", {}),
            "own_damage_breakdown": breakdown,
            "own_dps": round(own_dps, 2),
            "own_damage_total": round(own_damage_total, 2),
            "minion_dps": round(minion_dps_avg, 2),
            "minion_dps_min": round(minion_dps_min, 2),
            "minion_dps_max": round(minion_dps_max, 2),
            "minion_damage_total": round(minion_damage_total, 2),
            "total_dps": round(total_dps, 2),
            "total_damage": round(total_damage, 2),
            "gear_summary": {
                "raw_attack_power": gear["attack_power"],
                "strength": str_val,
                "agility": agi_val,
                "stamina": sta_val,
                "intellect": int_val,
                "spirit": spi_val,
                "armor": gear["armor"],
                "equipped_count": len(gear["equipped_items"]),
            },
        }
