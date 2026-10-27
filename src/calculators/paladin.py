from typing import Any, Dict, List, Optional, Union

from src.items_db import calculate_gear_totals, load_items_db
from .base import BaseCombatCalculator


class PaladinCombatCalculator(BaseCombatCalculator):

    def __init__(self, db: Optional[Dict] = None):
        self.db = db if db is not None else load_items_db()

    def calculate(
        self,
        equipped_items: List[Union[int, str, Dict]],
        fight_duration: float = 60.0,
        haste_percent: float = 0.0,
        target_armor: float = 3731.0,
        judgement_interval: float = 10.0,
        consecration: bool = True,
        exorcism_interval: float = 15.0,
        t2_bonus_active: bool = True,
        lost_set_active: bool = True,
        talents: Optional[Dict[str, int]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        t = talents or {}
        divine_strength = int(t.get("Divine Strength", t.get("divine_strength", 0)))
        divine_intellect = int(t.get("Divine Intellect", t.get("divine_intellect", 0)))
        sanctified_light = int(t.get("Sanctified Light", t.get("sanctified_light", 0)))
        conviction = int(t.get("Conviction", t.get("conviction", 0)))
        precision = int(t.get("Precision", t.get("precision", 0)))
        two_handed_spec = int(t.get("Two-Handed Weapon Specialization", t.get("two_handed_spec", 0)))
        one_handed_spec = int(t.get("One-Handed Spec", t.get("one_handed_spec", 0)))
        sanctity_aura = bool(t.get("Sanctity Aura", t.get("sanctity_aura", 0)))
        vengeance = int(t.get("Vengeance", t.get("vengeance", 0)))
        improved_judgement = int(t.get("Improved Judgement", t.get("improved_judgement", 0)))
        improved_sor = int(t.get("Improved Seal of Righteousness", t.get("improved_seal_of_righteousness", 0)))
        kings = bool(t.get("Blessing of Kings", t.get("blessing_of_kings", 0)))
        command = bool(t.get("Seal of Command", t.get("seal_of_command", 0)))

        item_ids = [it if isinstance(it, (int, str)) else it.get("id") for it in equipped_items]
        gear = calculate_gear_totals(item_ids, self.db)

        kings_mult = 1.10 if kings else 1.0
        base_str = gear["strength"]
        effective_str = base_str * (1.0 + (0.02 * divine_strength)) * kings_mult
        base_int = gear["intellect"]
        effective_int = base_int * (1.0 + (0.02 * divine_intellect)) * kings_mult

        ap = (gear["attack_power"] * kings_mult) + int(effective_str * 2)
        sp = gear["spell_power"]

        crit_pct = gear["crit"] + (gear["agility"] / 20.0) + (1.0 * conviction)
        hit_pct = gear["hit"] + (1.0 * precision)
        spell_crit_pct = crit_pct + (1.0 * sanctified_light)

        weapon_speed = gear["main_weapon_speed"] if gear["main_weapon_speed"] > 0 else 2.0
        effective_speed = weapon_speed / (1.0 + (haste_percent / 100.0))
        exact_melee_swings = 1 + int(fight_duration / effective_speed) if fight_duration > 0 and effective_speed > 0 else 0

        min_dmg = 0.0
        max_dmg = 0.0
        weapon_name = "Unarmed"
        is_two_hand = False
        is_one_hand = False
        for it in gear["equipped_items"]:
            if it.get("slot") == "two_hand":
                min_dmg = it.get("min_damage", 0.0)
                max_dmg = it.get("max_damage", 0.0)
                weapon_name = it.get("name", "Two-Handed Weapon")
                is_two_hand = True
                break
            elif it.get("slot") in ("one_hand", "main_hand"):
                min_dmg = it.get("min_damage", 0.0)
                max_dmg = it.get("max_damage", 0.0)
                weapon_name = it.get("name", "One-Handed Weapon")
                is_one_hand = True
                break

        avg_weapon_dmg = (min_dmg + max_dmg) / 2.0 if (min_dmg + max_dmg) > 0 else (weapon_speed * 25.0)

        weapon_talent_mult = 1.0
        if is_two_hand:
            weapon_talent_mult = 1.0 + (0.02 * two_handed_spec)
        elif is_one_hand:
            weapon_talent_mult = 1.0 + (0.02 * one_handed_spec)

        crit_chance = max(0.0, min(1.0, crit_pct / 100.0))
        swings_in_8s = 8.0 / effective_speed if effective_speed > 0 else 2.0
        vengeance_uptime = 1.0 - ((1.0 - crit_chance) ** swings_in_8s)
        vengeance_mult = 1.0 + (0.03 * vengeance * vengeance_uptime)

        physical_mult = weapon_talent_mult * vengeance_mult

        holy_mult = 1.0
        if sanctity_aura:
            holy_mult *= 1.10
        holy_mult *= vengeance_mult

        armor_reduction = target_armor / (target_armor + 5500.0) if target_armor > 0 else 0.0
        crit_multiplier = 1.0 + crit_chance
        raw_swing_dmg = avg_weapon_dmg + (ap / 14.0) * weapon_speed
        avg_white_hit = raw_swing_dmg * (1.0 - armor_reduction) * crit_multiplier * physical_mult
        white_damage_total = exact_melee_swings * avg_white_hit
        white_dps = white_damage_total / fight_duration if fight_duration > 0 else 0.0

        spell_crit_multiplier = 1.0 + (spell_crit_pct / 100.0 * 0.5)
        sor_mult = 1.0 + (0.02 * improved_sor)
        sor_base = weapon_speed * 18.5
        sor_hit = (sor_base + (weapon_speed / 20.0) * sp) * spell_crit_multiplier * holy_mult * sor_mult
        seal_damage_total = exact_melee_swings * sor_hit
        seal_dps = seal_damage_total / fight_duration if fight_duration > 0 else 0.0

        effective_judge_interval = max(6.0, judgement_interval - (1.0 * improved_judgement))
        judgement_count = int(fight_duration / effective_judge_interval) if effective_judge_interval > 0 else 0
        jor_hit = (185.0 + 0.50 * sp) * spell_crit_multiplier * holy_mult * sor_mult
        judgement_damage_total = judgement_count * jor_hit
        judgement_dps = judgement_damage_total / fight_duration if fight_duration > 0 else 0.0

        t2_instances_per_swing = 3 if t2_bonus_active else 0
        t2_instances_per_judge = 3 if t2_bonus_active else 0
        total_t2_instances = (exact_melee_swings * t2_instances_per_swing) + (judgement_count * t2_instances_per_judge)
        t2_hit = (63.0 + 0.05 * sp) * spell_crit_multiplier * holy_mult
        t2_damage_total = total_t2_instances * t2_hit
        t2_dps = t2_damage_total / fight_duration if fight_duration > 0 else 0.0

        consecration_ticks = int(fight_duration * 1.0) if consecration else 0
        consec_tick_dmg = (48.0 + 0.0416 * sp) * holy_mult
        consec_damage_total = consecration_ticks * consec_tick_dmg
        consec_dps = consec_damage_total / fight_duration if fight_duration > 0 else 0.0

        exorcism_count = int(fight_duration / exorcism_interval) if exorcism_interval > 0 else 0
        exorcism_hit = (535.0 + 0.428 * sp) * spell_crit_multiplier * holy_mult
        exorcism_damage_total = exorcism_count * exorcism_hit
        exorcism_dps = exorcism_damage_total / fight_duration if fight_duration > 0 else 0.0

        own_damage_total = (
            white_damage_total
            + seal_damage_total
            + judgement_damage_total
            + t2_damage_total
            + consec_damage_total
            + exorcism_damage_total
        )
        own_dps = own_damage_total / fight_duration if fight_duration > 0 else 0.0

        swing_magic_hits = exact_melee_swings * (1 + t2_instances_per_swing)
        judge_magic_hits = judgement_count * (1 + t2_instances_per_judge)
        total_magic_hits = swing_magic_hits + judge_magic_hits + consecration_ticks + exorcism_count
        magic_hits_per_second = total_magic_hits / fight_duration if fight_duration > 0 else 0.0

        lost_pieces = sum(1 for it in gear["equipped_items"] if it.get("id") in (60790, 60799, 60809) or it.get("set_id") == 882)
        has_minions = bool(lost_set_active and lost_pieces > 0)

        if has_minions:
            proc_chance = 0.04
            procs_per_second = magic_hits_per_second * proc_chance
            expected_active_minions = procs_per_second * 20.0
            minion_single_dps = 254.5 / 2.0
            minion_dps_avg = expected_active_minions * minion_single_dps
            minion_dps_min = expected_active_minions * (230.0 / 2.0)
            minion_dps_max = expected_active_minions * (279.0 / 2.0)
            minion_damage_total = minion_dps_avg * fight_duration
        else:
            proc_chance = 0.0
            procs_per_second = 0.0
            expected_active_minions = 0.0
            minion_dps_avg = 0.0
            minion_dps_min = 0.0
            minion_dps_max = 0.0
            minion_damage_total = 0.0

        total_dps = own_dps + minion_dps_avg
        total_damage = own_damage_total + minion_damage_total

        return {
            "character_class": "paladin",
            "fight_duration": fight_duration,
            "weapon_name": weapon_name,
            "base_weapon_speed": weapon_speed,
            "effective_weapon_speed": round(effective_speed, 2),
            "exact_melee_swings": exact_melee_swings,
            "total_attack_power": ap,
            "total_spell_power": sp,
            "healing_power": gear["healing"],
            "total_crit_percent": round(crit_pct, 2),
            "total_hit_percent": round(hit_pct, 2),
            "total_magic_hits": total_magic_hits,
            "magic_hits_per_second": round(magic_hits_per_second, 3),
            "procs_per_second": round(procs_per_second, 4),
            "has_minions": has_minions,
            "expected_active_minions": round(expected_active_minions, 3),
            "own_damage_breakdown": {
                "white_melee_dps": round(white_dps, 2),
                "seal_dps": round(seal_dps, 2),
                "judgement_dps": round(judgement_dps, 2),
                "t2_holy_dps": round(t2_dps, 2),
                "consecration_dps": round(consec_dps, 2),
                "exorcism_dps": round(exorcism_dps, 2),
            },
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
                "strength": int(effective_str),
                "agility": gear["agility"],
                "stamina": gear["stamina"],
                "intellect": int(effective_int),
                "armor": gear["armor"],
                "equipped_count": len(gear["equipped_items"]),
            },
        }
