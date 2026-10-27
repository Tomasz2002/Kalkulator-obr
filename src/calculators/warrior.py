import math
from typing import Any, Dict, List, Optional, Union

from src.items_db import calculate_gear_totals, load_items_db
from .base import BaseCombatCalculator


class WarriorCombatCalculator(BaseCombatCalculator):

    def __init__(self, db: Optional[Dict] = None):
        self.db = db if db is not None else load_items_db()

    def calculate(
        self,
        equipped_items: List[Union[int, str, Dict]],
        fight_duration: float = 60.0,
        haste_percent: float = 0.0,
        target_armor: float = 3731.0,
        boss_hp_percent: float = 100.0,
        execute_phase_percent: float = 20.0,
        race: str = "human",
        talents: Optional[Dict[str, int]] = None,
        enchants: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        t = talents or {}
        cruelty = int(t.get("Cruelty", t.get("cruelty", 0)))
        unbridled_wrath = int(t.get("Unbridled Wrath", t.get("unbridled_wrath", 0)))
        flurry = int(t.get("Flurry", t.get("flurry", 0)))
        enrage = int(t.get("Enrage", t.get("enrage", 0)))
        death_wish = bool(t.get("Death Wish", t.get("death_wish", 0)))
        bloodthirst = bool(t.get("Bloodthirst", t.get("bloodthirst", 0)))
        dw_spec = int(t.get("Dual Wield Specialization", t.get("dw_spec", 0)))
        imp_execute = int(t.get("Improved Execute", t.get("imp_execute", 0)))
        imp_heroic = int(t.get("Improved Heroic Strike", t.get("imp_heroic", 0)))
        two_hand_spec = int(t.get("Two-Handed Weapon Specialization", t.get("two_hand_spec", 0)))
        one_hand_spec = int(t.get("One-Handed Weapon Specialization", t.get("one_hand_spec", 0)))
        mortal_strike = bool(t.get("Mortal Strike", t.get("mortal_strike", 0)))
        impale = int(t.get("Impale", t.get("impale", 0)))
        deep_wounds = int(t.get("Deep Wounds", t.get("deep_wounds", 0)))

        item_ids = [it if isinstance(it, (int, str)) else it.get("id") for it in equipped_items]
        gear = calculate_gear_totals(item_ids, self.db, enchants=enchants, race=race)

        active_sets = gear.get("active_sets", {})
        might_dps_pieces = active_sets.get("1003", active_sets.get("673", {})).get("equipped_count", 0)
        wrath_dps_pieces = active_sets.get("2003", active_sets.get("674", {})).get("equipped_count", 0)
        dread_dps_pieces = active_sets.get("3002", {}).get("equipped_count", 0)
        valor_pieces = active_sets.get("189", {}).get("equipped_count", 0)
        heroism_pieces = active_sets.get("511", {}).get("equipped_count", 0)

        race_clean = race.lower().strip()
        str_val = gear["strength"]
        agi_val = gear["agility"]

        set_ap_bonus = 0.0
        if valor_pieces >= 4:
            set_ap_bonus += 40.0
        if heroism_pieces >= 6:
            set_ap_bonus += 40.0
        if dread_dps_pieces >= 8:
            set_ap_bonus += 100.0

        base_ap = gear["attack_power"] + (str_val * 2) + set_ap_bonus

        has_mh = gear["main_weapon_speed"] > 0
        has_oh = gear.get("off_weapon_speed", 0.0) > 0
        is_dw = has_mh and has_oh
        is_2h = any(it.get("slot") == "twohand" for it in gear.get("equipped_items", [])) or (has_mh and not has_oh and gear.get("main_weapon_slot") == "twohand")

        mh_subclass = gear.get("main_weapon_subclass", "sword").lower()
        oh_subclass = gear.get("off_weapon_subclass", "sword").lower()

        weapon_skill = 300
        if wrath_dps_pieces >= 5:
            weapon_skill += 5
        if race_clean == "human":
            if "sword" in mh_subclass or "mace" in mh_subclass:
                weapon_skill += 3
        elif race_clean == "orc":
            if "axe" in mh_subclass:
                weapon_skill += 3

        for eq in gear.get("equipped_items", []):
            if eq.get("id") == 14551:
                weapon_skill += 7

        delta_skill = 315 - weapon_skill
        if delta_skill <= 10:
            special_miss_base = 0.05 + delta_skill * 0.001
            glance_penalty = 0.15
            dodge_chance = 0.06
        else:
            special_miss_base = 0.06 + (delta_skill - 10) * 0.002
            glance_penalty = 0.30
            dodge_chance = 0.065

        hit_gear = gear["hit"] / 100.0
        if dread_dps_pieces >= 4:
            hit_gear += 0.02
        special_miss = max(0.0, special_miss_base - hit_gear)

        if is_dw:
            white_miss = max(0.0, (special_miss_base + 0.19) - hit_gear)
        else:
            white_miss = special_miss

        set_crit_bonus = 0.0
        if might_dps_pieces >= 8:
            set_crit_bonus += 0.02
        if dread_dps_pieces >= 6:
            set_crit_bonus += 0.02

        crit_base = (gear["crit"] + (agi_val / 20.0) + (cruelty * 1.0)) / 100.0 + set_crit_bonus
        crit_suppression = 0.03
        effective_crit = max(0.01, min(0.95, crit_base - crit_suppression))

        glance_chance = 0.40 if not is_2h else 0.40

        flurry_bonus = [0.0, 0.10, 0.15, 0.20, 0.25, 0.30][min(5, flurry)]
        flurry_uptime = min(0.95, 1.0 - ((1.0 - effective_crit) ** 3.5)) if flurry_bonus > 0 else 0.0
        effective_flurry_haste = flurry_bonus * flurry_uptime

        death_wish_uptime = min(1.0, 30.0 / fight_duration) if death_wish and fight_duration > 0 else 0.0
        death_wish_mult = 1.0 + (0.20 * death_wish_uptime)

        enrage_mult = 1.0 + (0.05 * enrage * 0.4)

        blood_fury_uptime = min(1.0, 15.0 / fight_duration) if race_clean == "orc" and fight_duration > 0 else 0.0
        racial_ap_bonus = (base_ap * 0.25 * blood_fury_uptime) if race_clean == "orc" else 0.0

        troll_haste = 0.15 * min(1.0, 10.0 / fight_duration) if race_clean == "troll" and fight_duration > 0 else 0.0
        nelf_haste = 0.01 if race_clean == "nightelf" else 0.0
        wrath_haste = 0.12 if wrath_dps_pieces >= 3 else 0.0

        ap = base_ap + racial_ap_bonus

        total_haste = (haste_percent / 100.0) + effective_flurry_haste + troll_haste + nelf_haste + wrath_haste

        arp = 0.0
        for sp in gear.get("spells", []):
            if sp.get("spell_id") == 48030:
                arp += 25.0
        eff_armor = max(0.0, target_armor - arp)
        armor_reduction = eff_armor / (eff_armor + 5500.0) if eff_armor > 0 else 0.0
        armor_mult = 1.0 - armor_reduction

        general_phys_mult = death_wish_mult * enrage_mult

        weapon_damage_mult = 1.0
        if is_2h:
            weapon_damage_mult *= (1.0 + (0.01 * two_hand_spec))
        elif not is_dw and has_mh:
            weapon_damage_mult *= (1.0 + (0.02 * one_hand_spec))

        crit_damage_mult = 2.0 * (1.0 + (0.10 * impale))

        white_crit_multiplier = 1.0 + (effective_crit * 1.0)
        yellow_crit_multiplier = 1.0 + (effective_crit * (crit_damage_mult - 1.0))

        mh_speed = gear["main_weapon_speed"] if gear["main_weapon_speed"] > 0 else 2.6
        eff_mh_speed = mh_speed / (1.0 + total_haste)
        mh_swings = int(fight_duration / eff_mh_speed) if eff_mh_speed > 0 and fight_duration > 0 else 0

        mh_min = gear["main_weapon_min_dmg"]
        mh_max = gear["main_weapon_max_dmg"]
        avg_mh_base = (mh_min + mh_max) / 2.0 if (mh_min + mh_max) > 0 else (mh_speed * 40.0)

        raw_mh_hit = avg_mh_base + ((ap / 14.0) * mh_speed)

        mh_hit_rate = max(0.0, 1.0 - white_miss - dodge_chance - glance_chance - effective_crit)
        mh_white_avg = (
            (mh_hit_rate * 1.0)
            + (glance_chance * (1.0 - glance_penalty))
            + (effective_crit * 2.0)
        ) * raw_mh_hit * armor_mult * general_phys_mult * weapon_damage_mult

        oh_swings = 0
        oh_white_avg = 0.0
        oh_white_total = 0.0
        eff_oh_speed = 0.0
        if is_dw:
            oh_speed = gear.get("off_weapon_speed", 2.0)
            eff_oh_speed = oh_speed / (1.0 + total_haste)
            oh_swings = int(fight_duration / eff_oh_speed) if eff_oh_speed > 0 and fight_duration > 0 else 0

            oh_min = gear.get("off_weapon_min_dmg", 0.0)
            oh_max = gear.get("off_weapon_max_dmg", 0.0)
            avg_oh_base = (oh_min + oh_max) / 2.0 if (oh_min + oh_max) > 0 else (oh_speed * 30.0)

            oh_talent_mod = 0.50 * (1.0 + (0.05 * dw_spec))
            raw_oh_hit = (avg_oh_base + ((ap / 14.0) * oh_speed)) * oh_talent_mod

            oh_hit_rate = max(0.0, 1.0 - white_miss - dodge_chance - glance_chance - effective_crit)
            oh_white_avg = (
                (oh_hit_rate * 1.0)
                + (glance_chance * (1.0 - glance_penalty))
                + (effective_crit * 2.0)
            ) * raw_oh_hit * armor_mult * general_phys_mult

            oh_white_total = oh_swings * oh_white_avg

        rage_conversion = 230.6
        mh_rage_per_swing = max(5.0, min(30.0, ((raw_mh_hit * armor_mult) / rage_conversion) * 7.5))
        oh_rage_per_swing = max(3.0, min(15.0, ((raw_mh_hit * 0.5 * armor_mult) / rage_conversion) * 3.75)) if is_dw else 0.0

        uw_proc_rate = unbridled_wrath * 0.08
        mh_total_rage = mh_swings * (mh_rage_per_swing * (1.0 - white_miss) + uw_proc_rate)
        oh_total_rage = oh_swings * (oh_rage_per_swing * (1.0 - white_miss) + uw_proc_rate) if is_dw else 0.0

        if boss_hp_percent <= 20.0:
            exec_duration = fight_duration
            normal_duration = 0.0
        else:
            exec_ratio = min(1.0, max(0.0, execute_phase_percent / 100.0))
            exec_duration = fight_duration * exec_ratio
            normal_duration = fight_duration - exec_duration

        bt_damage_total = 0.0
        bt_dps = 0.0
        bt_count = 0
        if bloodthirst:
            bt_cd = 6.0
            bt_count = int(fight_duration / bt_cd) if fight_duration > 0 else 0
            bt_mult = 1.10 if dread_dps_pieces >= 2 else 1.0
            bt_hit = (0.45 * ap) * yellow_crit_multiplier * (1.0 - special_miss) * general_phys_mult * armor_mult * bt_mult
            bt_damage_total = bt_count * bt_hit
            bt_dps = bt_damage_total / fight_duration if fight_duration > 0 else 0.0

        ms_damage_total = 0.0
        ms_dps = 0.0
        ms_count = 0
        if mortal_strike and not bloodthirst:
            ms_cd = 6.0
            ms_count = int(fight_duration / ms_cd) if fight_duration > 0 else 0
            norm_speed = 3.3 if is_2h else 2.4
            ms_raw = avg_mh_base + ((ap / 14.0) * norm_speed) + 160.0
            ms_hit = ms_raw * yellow_crit_multiplier * (1.0 - special_miss) * general_phys_mult * armor_mult * weapon_damage_mult
            ms_damage_total = ms_count * ms_hit
            ms_dps = ms_damage_total / fight_duration if fight_duration > 0 else 0.0

        ww_damage_total = 0.0
        ww_dps = 0.0
        ww_count = 0
        ww_cd = 10.0
        ww_count = int(fight_duration / ww_cd) if fight_duration > 0 else 0
        ww_norm_speed = 3.3 if is_2h else 2.4
        ww_raw = avg_mh_base + ((ap / 14.0) * ww_norm_speed)
        ww_hit = ww_raw * yellow_crit_multiplier * (1.0 - special_miss) * general_phys_mult * armor_mult * weapon_damage_mult
        ww_damage_total = ww_count * ww_hit
        ww_dps = ww_damage_total / fight_duration if fight_duration > 0 else 0.0

        bt_ms_cost = 20 if might_dps_pieces >= 5 else 30
        ability_rage_bonus = 2.0 if might_dps_pieces >= 3 else 0.0
        total_generated_rage = mh_total_rage + oh_total_rage + ((bt_count + ms_count + ww_count) * ability_rage_bonus)

        consumed_primary_rage = (bt_count * bt_ms_cost) + (ms_count * bt_ms_cost) + (ww_count * 25)
        remaining_rage = max(0.0, total_generated_rage - consumed_primary_rage)

        hs_cost = max(9, 15 - imp_heroic)
        hs_count = 0
        hs_damage_total = 0.0
        hs_dps = 0.0

        normal_mh_swings = int(mh_swings * (normal_duration / fight_duration)) if fight_duration > 0 else 0
        exec_mh_swings = mh_swings - normal_mh_swings

        if normal_duration > 0 and remaining_rage > hs_cost:
            hs_candidates = int(normal_mh_swings * 0.65)
            hs_affordable = int(remaining_rage / hs_cost)
            hs_count = min(hs_candidates, hs_affordable)
            remaining_rage -= (hs_count * hs_cost)

            hs_raw = raw_mh_hit + 138.0
            hs_hit = hs_raw * yellow_crit_multiplier * (1.0 - special_miss) * armor_mult * general_phys_mult * weapon_damage_mult
            hs_damage_total = hs_count * hs_hit
            hs_dps = hs_damage_total / fight_duration if fight_duration > 0 else 0.0

        white_mh_swings = max(0, mh_swings - hs_count)
        white_mh_total = white_mh_swings * mh_white_avg
        white_total_dmg = white_mh_total + oh_white_total
        white_dps = white_total_dmg / fight_duration if fight_duration > 0 else 0.0

        exec_damage_total = 0.0
        exec_dps = 0.0
        exec_count = 0
        if exec_duration > 0:
            exec_cost = 15 - (imp_execute * 2.5)
            gcd_exec_limit = int(exec_duration / 1.5)
            exec_rage_available = remaining_rage + (exec_mh_swings * mh_rage_per_swing)
            if exec_rage_available >= exec_cost and gcd_exec_limit > 0:
                exec_count = min(gcd_exec_limit, int(exec_rage_available / exec_cost))
                if exec_count > 0:
                    avg_rage_per_exec = exec_rage_available / exec_count
                    extra_rage = max(0.0, avg_rage_per_exec - exec_cost)
                    raw_exec_dmg = 600.0 + (extra_rage * 15.0)
                    exec_hit = raw_exec_dmg * yellow_crit_multiplier * (1.0 - special_miss) * general_phys_mult * armor_mult
                    exec_damage_total = exec_count * exec_hit
                    exec_dps = exec_damage_total / fight_duration if fight_duration > 0 else 0.0

        dw_bleed_total = 0.0
        dw_bleed_dps = 0.0
        if deep_wounds > 0:
            total_physical_hits = (white_mh_swings + oh_swings + bt_count + ms_count + ww_count + hs_count + exec_count)
            crit_hits = total_physical_hits * effective_crit
            dw_bleed_total = crit_hits * (avg_mh_base * 0.20 * deep_wounds)
            dw_bleed_dps = dw_bleed_total / fight_duration if fight_duration > 0 else 0.0

        has_minions = gear.get("has_pet_summon", False)
        minion_dps_avg = 0.0
        minion_dps_min = 0.0
        minion_dps_max = 0.0
        minion_damage_total = 0.0
        expected_active_minions = 0.0

        if has_minions and "Spirit of Eskhandar" in gear.get("pet_summon_details", []):
            crit_swings_per_sec = ((white_mh_swings + oh_swings) / fight_duration if fight_duration > 0 else 0.0) * effective_crit
            procs_per_sec = crit_swings_per_sec * 0.01
            expected_active_minions = min(1.0, procs_per_sec * 120.0)
            eskhandar_dps = 70.0 / 1.5
            minion_dps_avg = expected_active_minions * eskhandar_dps
            minion_dps_min = expected_active_minions * (60.0 / 1.5)
            minion_dps_max = expected_active_minions * (80.0 / 1.5)
            minion_damage_total = minion_dps_avg * fight_duration

        own_damage_total = (
            white_total_dmg
            + bt_damage_total
            + ms_damage_total
            + ww_damage_total
            + hs_damage_total
            + exec_damage_total
            + dw_bleed_total
        )
        own_dps = own_damage_total / fight_duration if fight_duration > 0 else 0.0

        total_dps = own_dps + minion_dps_avg
        total_damage = own_damage_total + minion_damage_total

        breakdown = {
            "white_melee_dps": round(white_dps, 2),
        }
        if bloodthirst:
            breakdown["bloodthirst_dps"] = round(bt_dps, 2)
        if mortal_strike and not bloodthirst:
            breakdown["mortal_strike_dps"] = round(ms_dps, 2)
        if ww_damage_total > 0:
            breakdown["whirlwind_dps"] = round(ww_dps, 2)
        if hs_damage_total > 0:
            breakdown["heroic_strike_dps"] = round(hs_dps, 2)
        if exec_damage_total > 0:
            breakdown["execute_dps"] = round(exec_dps, 2)
        if dw_bleed_total > 0:
            breakdown["deep_wounds_bleed_dps"] = round(dw_bleed_dps, 2)

        return {
            "character_class": "warrior",
            "fight_duration": fight_duration,
            "race": race_clean.capitalize(),
            "is_dual_wield": is_dw,
            "is_two_handed": is_2h,
            "weapon_skill": weapon_skill,
            "main_weapon_name": gear["main_weapon_name"],
            "base_weapon_speed": mh_speed,
            "effective_weapon_speed": round(eff_mh_speed, 2),
            "off_weapon_name": gear.get("off_weapon_name", ""),
            "off_weapon_speed": round(eff_oh_speed, 2) if is_dw else 0.0,
            "exact_melee_swings": mh_swings + oh_swings,
            "total_attack_power": int(ap),
            "total_crit_percent": round(effective_crit * 100.0, 2),
            "total_hit_percent": round(gear["hit"], 2),
            "special_miss_percent": round(special_miss * 100.0, 2),
            "white_miss_percent": round(white_miss * 100.0, 2),
            "flurry_uptime_percent": round(flurry_uptime * 100.0, 1),
            "boss_hp_percent": boss_hp_percent,
            "execute_phase_percent": execute_phase_percent if boss_hp_percent > 20.0 else 100.0,
            "execute_duration_seconds": round(exec_duration, 1),
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
                "stamina": gear["stamina"],
                "intellect": gear["intellect"],
                "spirit": gear["spirit"],
                "armor": gear["armor"],
                "equipped_count": len(gear["equipped_items"]),
            },
        }
