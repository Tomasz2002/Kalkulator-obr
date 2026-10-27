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
        boss_hp_percent: float = 100.0,
        execute_phase_percent: float = 20.0,
        race: str = "human",
        talents: Optional[Dict[str, int]] = None,
        enchants: Optional[Dict[str, Any]] = None,
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

        item_ids = [it if isinstance(it, (int, str)) else it.get("id") for it in equipped_items]
        gear = calculate_gear_totals(item_ids, self.db, enchants=enchants, race=race)

        race_clean = race.lower().strip()

        kings_mult = 1.10 if kings else 1.0
        base_str = gear["strength"]
        effective_str = base_str * (1.0 + (0.02 * divine_strength)) * kings_mult
        base_int = gear["intellect"]
        effective_int = base_int * (1.0 + (0.02 * divine_intellect)) * kings_mult

        ap = (gear["attack_power"] * kings_mult) + int(effective_str * 2)
        sp = gear["spell_power"]

        active_sets = gear.get("active_sets", {})
        t1_holy_pieces = active_sets.get("208", {}).get("equipped_count", 0)
        t1_tank_pieces = active_sets.get("1004", {}).get("equipped_count", 0)
        t1_dps_pieces = active_sets.get("1005", {}).get("equipped_count", 0)
        t2_holy_pieces = active_sets.get("217", {}).get("equipped_count", 0)
        t2_tank_pieces = active_sets.get("2004", {}).get("equipped_count", 0)
        t2_dps_pieces = active_sets.get("2005", {}).get("equipped_count", 0)
        t3_holy_pieces = active_sets.get("528", {}).get("equipped_count", 0)
        t3_tank_pieces = active_sets.get("3004", {}).get("equipped_count", 0)
        t3_dps_pieces = active_sets.get("3005", {}).get("equipped_count", 0)

        if t1_holy_pieces >= 3:
            gear["healing"] += 31
        if t2_holy_pieces >= 3:
            gear["healing"] += 57
        if t2_tank_pieces >= 5 or t2_dps_pieces >= 5:
            sp += 27
        if t3_tank_pieces >= 8 or t3_dps_pieces >= 8:
            sp += 57

        crit_pct = gear["crit"] + (gear["agility"] / 20.0) + (1.0 * conviction)
        if t1_dps_pieces >= 5:
            crit_pct += 2.0
        if t3_dps_pieces >= 2:
            crit_pct += 3.0

        hit_pct = gear["hit"] + (1.0 * precision)
        spell_crit_pct = crit_pct + (1.0 * sanctified_light)
        if t1_holy_pieces >= 5:
            spell_crit_pct += 2.0

        set_haste = 2.0 if t3_dps_pieces >= 4 else 0.0
        total_haste = haste_percent + set_haste

        weapon_speed = gear["main_weapon_speed"] if gear["main_weapon_speed"] > 0 else 2.0
        effective_speed = weapon_speed / (1.0 + (total_haste / 100.0))
        exact_melee_swings = 1 + int(fight_duration / effective_speed) if fight_duration > 0 and effective_speed > 0 else 0

        min_dmg = gear["main_weapon_min_dmg"]
        max_dmg = gear["main_weapon_max_dmg"]
        weapon_name = gear["main_weapon_name"]
        is_two_hand = any(it.get("slot") == "twohand" for it in gear["equipped_items"])
        is_one_hand = any(it.get("slot") in ("onehand", "mainhand") for it in gear["equipped_items"])

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

        flat_holy_per_hit = 3.0 if (t2_tank_pieces >= 3 or t2_dps_pieces >= 3) else 0.0
        t2_flat_holy_total = exact_melee_swings * flat_holy_per_hit * holy_mult
        t2_flat_holy_dps = t2_flat_holy_total / fight_duration if fight_duration > 0 else 0.0

        spell_crit_multiplier = 1.0 + (spell_crit_pct / 100.0 * 0.5)

        sor_mult = 1.0 + (0.02 * improved_sor)
        sor_base = weapon_speed * 18.5
        sor_hit = (sor_base + (weapon_speed / 20.0) * sp) * spell_crit_multiplier * holy_mult * sor_mult
        seal_damage_total = exact_melee_swings * sor_hit
        seal_dps = seal_damage_total / fight_duration if fight_duration > 0 else 0.0

        jor_bonus = 148.0 if t1_dps_pieces >= 3 else 0.0
        effective_judge_interval = max(6.0, judgement_interval - (1.0 * improved_judgement))
        judgement_count = int(fight_duration / effective_judge_interval) if effective_judge_interval > 0 else 0
        jor_hit = (185.0 + jor_bonus + 0.50 * sp) * spell_crit_multiplier * holy_mult * sor_mult
        judgement_damage_total = judgement_count * jor_hit
        judgement_dps = judgement_damage_total / fight_duration if fight_duration > 0 else 0.0

        t2_proc_damage_total = 0.0
        t2_proc_dps = 0.0
        if t2_dps_pieces >= 8:
            t2_proc_hits = exact_melee_swings * crit_chance
            t2_proc_damage_total = t2_proc_hits * 300.0 * spell_crit_multiplier * holy_mult
            t2_proc_dps = t2_proc_damage_total / fight_duration if fight_duration > 0 else 0.0

        t1_proc_damage_total = 0.0
        t1_proc_dps = 0.0
        if t1_dps_pieces >= 8:
            t1_proc_damage_total = exact_melee_swings * 0.20 * 112.0 * spell_crit_multiplier * holy_mult
            t1_proc_dps = t1_proc_damage_total / fight_duration if fight_duration > 0 else 0.0
        elif t1_tank_pieces >= 8:
            t1_proc_damage_total = exact_melee_swings * 0.20 * 90.0 * spell_crit_multiplier * holy_mult
            t1_proc_dps = t1_proc_damage_total / fight_duration if fight_duration > 0 else 0.0

        consecration_ticks = int(fight_duration * 1.0) if consecration else 0
        consec_tick_dmg = (48.0 + 0.0416 * sp) * holy_mult
        consec_damage_total = consecration_ticks * consec_tick_dmg
        consec_dps = consec_damage_total / fight_duration if fight_duration > 0 else 0.0

        actual_exorcism_interval = exorcism_interval
        if t3_tank_pieces >= 6 or t3_dps_pieces >= 6:
            actual_exorcism_interval = max(1.0, exorcism_interval - 5.0)

        exorcism_count = int(fight_duration / actual_exorcism_interval) if actual_exorcism_interval > 0 else 0
        exorcism_hit = (535.0 + 0.428 * sp) * spell_crit_multiplier * holy_mult
        exorcism_damage_total = exorcism_count * exorcism_hit
        exorcism_dps = exorcism_damage_total / fight_duration if fight_duration > 0 else 0.0

        if boss_hp_percent <= 20.0:
            exec_duration = fight_duration
        else:
            exec_ratio = min(1.0, max(0.0, execute_phase_percent / 100.0))
            exec_duration = fight_duration * exec_ratio

        how_damage_total = 0.0
        how_dps = 0.0
        if exec_duration > 0:
            how_count = int(exec_duration / 6.0)
            how_hit = (530.0 + 0.428 * sp) * spell_crit_multiplier * holy_mult
            how_damage_total = how_count * how_hit
            how_dps = how_damage_total / fight_duration if fight_duration > 0 else 0.0

        own_damage_total = (
            white_damage_total
            + t2_flat_holy_total
            + seal_damage_total
            + judgement_damage_total
            + t2_proc_damage_total
            + t1_proc_damage_total
            + consec_damage_total
            + exorcism_damage_total
            + how_damage_total
        )
        own_dps = own_damage_total / fight_duration if fight_duration > 0 else 0.0

        has_minions = gear.get("has_pet_summon", False)
        minion_dps_avg = 0.0
        minion_dps_min = 0.0
        minion_dps_max = 0.0
        minion_damage_total = 0.0
        expected_active_minions = 0.0

        if has_minions and "Spirit of Eskhandar" in gear.get("pet_summon_details", []):
            crit_swings_per_sec = (exact_melee_swings / fight_duration if fight_duration > 0 else 0.0) * crit_chance
            eskhandar_proc_chance = 0.01
            procs_per_sec = crit_swings_per_sec * eskhandar_proc_chance
            expected_active_minions = min(1.0, procs_per_sec * 120.0)
            eskhandar_dps = 70.0 / 1.5
            minion_dps_avg = expected_active_minions * eskhandar_dps
            minion_dps_min = expected_active_minions * (60.0 / 1.5)
            minion_dps_max = expected_active_minions * (80.0 / 1.5)
            minion_damage_total = minion_dps_avg * fight_duration

        total_dps = own_dps + minion_dps_avg
        total_damage = own_damage_total + minion_damage_total

        breakdown = {
            "white_melee_dps": round(white_dps, 2),
            "seal_dps": round(seal_dps, 2),
            "judgement_dps": round(judgement_dps, 2),
            "consecration_dps": round(consec_dps, 2),
            "exorcism_dps": round(exorcism_dps, 2),
        }
        if t2_flat_holy_dps > 0:
            breakdown["judgement_3set_holy_dps"] = round(t2_flat_holy_dps, 2)
        if t2_proc_dps > 0:
            breakdown["judgement_8set_smite_dps"] = round(t2_proc_dps, 2)
        if t1_proc_dps > 0:
            breakdown["lawbringer_8set_holy_dps"] = round(t1_proc_dps, 2)
        if how_damage_total > 0:
            breakdown["hammer_of_wrath_dps"] = round(how_dps, 2)

        return {
            "character_class": "paladin",
            "fight_duration": fight_duration,
            "race": race_clean.capitalize(),
            "weapon_name": weapon_name,
            "base_weapon_speed": weapon_speed,
            "effective_weapon_speed": round(effective_speed, 2),
            "exact_melee_swings": exact_melee_swings,
            "total_attack_power": ap,
            "total_spell_power": sp,
            "healing_power": gear["healing"],
            "total_crit_percent": round(crit_pct, 2),
            "total_hit_percent": round(hit_pct, 2),
            "boss_hp_percent": boss_hp_percent,
            "execute_phase_percent": execute_phase_percent if boss_hp_percent > 20.0 else 100.0,
            "execute_duration_seconds": round(exec_duration, 1),
            "resistances": gear["resistances"],
            "has_minions": has_minions,
            "expected_active_minions": round(expected_active_minions, 3),
            "active_sets": active_sets,
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
                "strength": int(effective_str),
                "agility": gear["agility"],
                "stamina": gear["stamina"],
                "intellect": int(effective_int),
                "spirit": gear["spirit"],
                "armor": gear["armor"],
                "equipped_count": len(gear["equipped_items"]),
            },
        }
