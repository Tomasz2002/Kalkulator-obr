import math
from typing import Any, Dict, List, Optional, Union

from src.items_db import calculate_gear_totals, compute_effective_weapon_skill, load_items_db
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
        paladin_build: str = "auto",
        rotation_mode: str = "priority_rotation",
        priority_list: Optional[List[str]] = None,
        spells_db: Optional[Dict[str, Any]] = None,
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
        vengeful_strikes = int(t.get("Vengeful Strikes", t.get("vengeful_strikes", 0)))
        righteous_strikes = int(t.get("Righteous Strikes", t.get("righteous_strikes", 0)))
        kings = bool(t.get("Blessing of Kings", t.get("blessing_of_kings", 0)))
        has_soc_talent = int(t.get("Seal of Command", t.get("seal_of_command", 0))) > 0

        item_ids = [it if isinstance(it, (int, str)) else it.get("id") for it in equipped_items]
        quest_ws = kwargs.get("quest_weapon_skills", None)
        gear = calculate_gear_totals(
            item_ids,
            self.db,
            enchants=enchants,
            race=race,
            character_class="paladin",
            quest_weapon_skills=quest_ws
        )

        race_clean = race.lower().strip()
        kings_mult = 1.10 if kings else 1.0
        base_str = gear["strength"]
        base_int = gear["intellect"]
        effective_int = base_int * (1.0 + (0.02 * divine_intellect)) * kings_mult
        effective_agi = gear["agility"] * kings_mult

        # Baseline effective_str & AP before holy might buff is applied in combat
        effective_str = base_str * (1.0 + (0.02 * divine_strength)) * kings_mult
        ap = gear["attack_power"] + int(effective_str * 2)
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
        lost_pieces = active_sets.get("6001", {}).get("equipped_count", 0)
        has_lost_set = (lost_pieces >= 3)

        if t1_holy_pieces >= 3:
            gear["healing"] += 31
        if t2_holy_pieces >= 3:
            gear["healing"] += 57
        if t2_tank_pieces >= 5 or t2_dps_pieces >= 5:
            sp += 27
        if t3_tank_pieces >= 8 or t3_dps_pieces >= 8:
            sp += 57

        crit_pct = gear["crit"] + (effective_agi / 20.0) + (1.0 * conviction)
        if t1_dps_pieces >= 5:
            crit_pct += 2.0
        if t3_dps_pieces >= 2:
            crit_pct += 3.0

        hit_pct = gear["hit"] + (1.0 * precision)
        spell_crit_pct = gear.get("spell_crit", 0.0) + (1.0 * sanctified_light) + (effective_int / 29.5)
        if t1_holy_pieces >= 5:
            spell_crit_pct += 2.0

        spell_hit_pct = 83.0 + gear.get("spell_hit", gear.get("hit", 0.0)) + (1.0 * precision)
        spell_hit_chance = max(0.20, min(0.99, spell_hit_pct / 100.0))

        set_haste = 2.0 if t3_dps_pieces >= 4 else 0.0
        total_haste = haste_percent + set_haste + gear.get("haste", 0.0)

        weapon_speed = gear["main_weapon_speed"] if gear["main_weapon_speed"] > 0 else 2.0
        effective_speed = weapon_speed / (1.0 + (total_haste / 100.0))
        exact_melee_swings = 1 + int(fight_duration / effective_speed) if fight_duration > 0 and effective_speed > 0 else 0

        min_dmg = gear["main_weapon_min_dmg"]
        max_dmg = gear["main_weapon_max_dmg"]
        weapon_name = gear["main_weapon_name"]
        is_two_hand = any(it.get("slot") in ("twohand", "two_hand") for it in gear["equipped_items"]) or (gear.get("main_weapon_slot") in ("twohand", "two_hand"))
        is_one_hand = any(it.get("slot") in ("onehand", "one_hand", "mainhand", "main_hand") for it in gear["equipped_items"]) or (gear.get("main_weapon_slot") in ("onehand", "one_hand", "mainhand", "main_hand"))

        avg_weapon_dmg = (min_dmg + max_dmg) / 2.0 if (min_dmg + max_dmg) > 0 else (weapon_speed * 25.0)

        weapon_talent_mult = 1.0
        if is_two_hand:
            weapon_talent_mult = 1.0 + (0.02 * two_handed_spec)
        elif is_one_hand:
            weapon_talent_mult = 1.0 + (0.02 * one_handed_spec)

        raw_subclass = (gear.get("main_weapon_subclass") or "sword").lower().strip()
        if is_two_hand:
            if "sword" in raw_subclass:
                weapon_subclass = "two_hand_sword"
            elif "mace" in raw_subclass:
                weapon_subclass = "two_hand_mace"
            elif "axe" in raw_subclass:
                weapon_subclass = "two_hand_axe"
            else:
                weapon_subclass = raw_subclass
        else:
            if "sword" in raw_subclass:
                weapon_subclass = "one_hand_sword"
            elif "mace" in raw_subclass:
                weapon_subclass = "one_hand_mace"
            elif "axe" in raw_subclass:
                weapon_subclass = "one_hand_axe"
            else:
                weapon_subclass = raw_subclass

        talent_ws = two_handed_spec if is_two_hand else 0
        eq_ws_list = gear.get("equipped_weapon_skills", [])
        if eq_ws_list:
            effective_weapon_skill = min(315, eq_ws_list[0]["skill"] + (talent_ws if is_two_hand else 0))
        else:
            effective_weapon_skill = compute_effective_weapon_skill(
                weapon_subclass,
                gear.get("weapon_skills", {}),
                gear.get("racial_skills", {}),
                talent_weapon_skill=talent_ws
            )

        ws_above_300 = max(0, effective_weapon_skill - 300)
        # Turtle WoW / Octo WoW: 5 weapon skill above 300 = +1.0% hit chance (cap 315)
        weapon_skill_hit_bonus = round((ws_above_300 // 5) * 1.0, 1)
        # Turtle WoW / Octo WoW: linear glancing blow factor: 0.70 at 300 skill + 0.02 per skill above 300, capped at 1.00 at 315
        glance_damage_factor = min(1.0, round(0.70 + (ws_above_300 * 0.02), 3))
        # Turtle WoW: each weapon skill above 300 reduces boss dodge chance by 0.1% (base 5.6% -> 4.1% at 315)
        effective_dodge = max(0.0, 0.056 - (ws_above_300 * 0.001))

        crit_chance = max(0.0, min(1.0, crit_pct / 100.0))
        swings_in_8s = 8.0 / effective_speed if effective_speed > 0 else 2.0
        vengeance_uptime = 1.0 - ((1.0 - crit_chance) ** swings_in_8s)
        vengeance_mult = 1.0 + (0.03 * vengeance * vengeance_uptime)

        physical_mult = weapon_talent_mult * vengeance_mult

        holy_mult = 1.0
        if sanctity_aura:
            holy_mult *= 1.10
        holy_mult *= vengeance_mult

        # Embrace of the Wind Serpent (ID 12462): Equip: 15% chance on landing damaging spells to deal Shadow damage;
        # also reduces enemy target armor by 400.
        has_wind_serpent = any(
            str(it.get("id")) == "12462" or "embrace of the wind serpent" in str(it.get("name", "")).lower()
            for it in gear.get("equipped_items", [])
        )
        effective_target_armor = max(0.0, target_armor - gear.get("arp", 0.0) - (400.0 if has_wind_serpent and fight_duration >= 10.0 else 0.0))
        armor_reduction = effective_target_armor / (effective_target_armor + 5500.0) if effective_target_armor > 0 else 0.0

        # Turtle WoW: base miss against lvl 63 boss is 8.0% (no 1.12 hit suppression bug)
        total_melee_hit = hit_pct + weapon_skill_hit_bonus
        effective_miss = max(0.0, 0.08 - (total_melee_hit / 100.0))
        glance_chance = 0.40
        capped_crit = max(0.0, min(1.0 - effective_miss - glance_chance - effective_dodge, crit_chance))
        white_hit_chance = max(0.0, 1.0 - effective_miss - glance_chance - effective_dodge - capped_crit)
        landed_swing_chance = max(0.0, 1.0 - effective_miss - effective_dodge)

        raw_swing_dmg = avg_weapon_dmg + (ap / 14.0) * weapon_speed
        avg_white_swing = raw_swing_dmg * (1.0 - armor_reduction) * physical_mult * (white_hit_chance + (2.0 * capped_crit) + (glance_damage_factor * glance_chance))
        white_damage_total = exact_melee_swings * avg_white_swing
        white_dps = white_damage_total / fight_duration if fight_duration > 0 else 0.0

        # Seal choice & Opener configuration
        primary_seal_req = str(kwargs.get("primary_seal", "auto")).lower().strip()
        apply_crusader_first = bool(kwargs.get("apply_crusader_first", True))

        seal_fallback_reason = None
        if primary_seal_req == "command":
            if has_soc_talent:
                chosen_seal = "command"
            else:
                chosen_seal = "righteousness"
                seal_fallback_reason = "Brak wymaganego talentu Seal of Command w drzewku Retribution — użyto Seal of Righteousness"
        elif primary_seal_req in ("righteousness", "sor"):
            chosen_seal = "righteousness"
        elif primary_seal_req in ("vengeance", "sov"):
            chosen_seal = "vengeance"
        elif primary_seal_req in ("crusader", "soc_crusader"):
            chosen_seal = "crusader"
        else:  # "auto"
            if has_soc_talent and (is_two_hand or ap >= max(sp * 1.5, 300.0)):
                chosen_seal = "command"
            else:
                chosen_seal = "righteousness"

        build_req = str(paladin_build).lower().strip()
        if build_req in ("retribution", "spellret", "nekrodyn"):
            active_build = build_req
        else:
            if has_lost_set:
                active_build = "nekrodyn"
            elif chosen_seal == "command":
                active_build = "retribution"
            else:
                active_build = "spellret"

        # Judgement of the Crusader (Opener Debuff)
        has_joc_gloves = any(
            str(it.get("id")) in ("16471", "23274", "16410")
            or "increases the holy damage bonus of your judgement of the crusader" in str(it.get("text", "")).lower()
            for it in gear.get("equipped_items", [])
        )
        joc_base = 140.0 + (20.0 if has_joc_gloves else 0.0)
        joc_holy_bonus = (joc_base * (1.10 if sanctity_aura else 1.0)) if apply_crusader_first else 0.0
        opener_joc_casts = 1 if apply_crusader_first else 0

        flat_holy_per_hit = (3.0 if t2_tank_pieces >= 3 else 0.0) + (3.0 if t2_dps_pieces >= 3 else 0.0)
        t2_instances_per_swing = (1 if t2_tank_pieces >= 3 else 0) + (1 if t2_dps_pieces >= 3 else 0)
        t2_flat_holy_total = exact_melee_swings * landed_swing_chance * flat_holy_per_hit * holy_mult
        t2_flat_holy_dps = t2_flat_holy_total / fight_duration if fight_duration > 0 else 0.0

        spell_crit_multiplier = 1.0 + (spell_crit_pct / 100.0 * 0.5)

        effective_judge_interval = max(6.0, judgement_interval - (1.0 * improved_judgement))
        actual_exorcism_interval = exorcism_interval
        if t3_tank_pieces >= 6 or t3_dps_pieces >= 6:
            actual_exorcism_interval = max(1.0, exorcism_interval - 5.0)

        if boss_hp_percent <= 20.0:
            exec_duration = fight_duration
        else:
            exec_ratio = min(1.0, max(0.0, execute_phase_percent / 100.0))
            exec_duration = fight_duration * exec_ratio

        rot_mode = str(rotation_mode).strip().lower()
        if rot_mode not in ("priority_rotation", "auto_attack_only"):
            rot_mode = "priority_rotation"

        strike_ramp_mode = str(kwargs.get("strike_ramp_mode", "3_cs")).strip().lower()
        strike_ramp_hs = int(kwargs.get("strike_ramp_hs", 0))
        strike_ramp_cs = int(kwargs.get("strike_ramp_cs", 3))
        strike_sustain_hs = int(kwargs.get("strike_sustain_hs", 1))
        strike_sustain_cs = int(kwargs.get("strike_sustain_cs", 1))
        enable_crusader_strike = bool(kwargs.get("enable_crusader_strike", True))
        enable_holy_strike = bool(kwargs.get("enable_holy_strike", True))

        if strike_ramp_mode in ("hs", "1_hs", "holy_strike"):
            ramp_hs_target = strike_ramp_hs if strike_ramp_hs > 0 else 1
            ramp_cs_target = 0
        elif strike_ramp_mode in ("hs_then_cs", "1_hs_3_cs", "holy_strike_then_cs"):
            ramp_hs_target = strike_ramp_hs if strike_ramp_hs > 0 else 1
            ramp_cs_target = strike_ramp_cs if strike_ramp_cs > 0 else 3
        elif strike_ramp_mode in ("custom",):
            ramp_hs_target = strike_ramp_hs
            ramp_cs_target = strike_ramp_cs
        else:  # "3_cs", "cs", "crusader_strike", default
            strike_ramp_mode = "3_cs"
            ramp_hs_target = 0
            ramp_cs_target = strike_ramp_cs if strike_ramp_cs > 0 else 3

        if priority_list is not None and isinstance(priority_list, list):
            raw_pri = [str(x).strip().lower() for x in priority_list if str(x).strip()]
        else:
            raw_pri = ["hammer_of_wrath", "crusader_holy_strike", "judgement", "consecration", "exorcism"]

        # Normalize priority list: consolidate any CS / HS / shared strike into single 'crusader_holy_strike'
        active_priority_list = []
        has_shared_strike = False
        for ab in raw_pri:
            if ab in ("crusader_holy_strike", "strike_category_40", "shared_strike", "crusader_strike", "holy_strike"):
                if not has_shared_strike:
                    active_priority_list.append("crusader_holy_strike")
                    has_shared_strike = True
            else:
                active_priority_list.append(ab)

        if not consecration and "consecration" in active_priority_list:
            active_priority_list = [x for x in active_priority_list if x != "consecration"]

        cs_count = 0
        holy_strike_count = 0
        judgement_count = 0
        consec_count = 0
        consecration_ticks = 0
        exorcism_count = 0
        how_count = 0
        holy_shock_count = 0
        zeal_stacks = 0
        zeal_expires_at = 0.0
        total_zeal_haste_time = 0.0
        holy_might_expires_at = 0.0
        total_holy_might_time = 0.0
        zeal_haste_per_stack = 1.0 + (0.4 * vengeful_strikes)

        # State tracking for strike sequence (Category 40 shared cooldown)
        ramp_hs_done = 0
        ramp_cs_done = 0
        sustain_hs_done = 0
        sustain_cs_done = 0

        if rot_mode == "priority_rotation" and fight_duration > 0:
            sim_t = 0.0
            dt = 0.1
            # If opener applies Judgement of the Crusader (1.5s GCD) and then activates combat seal (1.5s GCD),
            # standard priority rotation queue begins from t=3.0s:
            gcd_ready_at = 3.0 if (apply_crusader_first and fight_duration >= 3.0) else 0.0
            consec_active_until = 0.0
            next_consec_tick = 0.0
            cd_ready = {
                "hammer_of_wrath": 0.0,
                "shared_strike": 0.0,
                "judgement": 3.0 if apply_crusader_first else 0.0,
                "consecration": 0.0,
                "exorcism": 0.0,
                "holy_shock": 0.0,
            }

            while sim_t <= fight_duration:
                cur_time = round(sim_t, 2)
                if cur_time > zeal_expires_at:
                    zeal_stacks = 0
                total_zeal_haste_time += (zeal_stacks * zeal_haste_per_stack) * dt
                if cur_time <= holy_might_expires_at:
                    total_holy_might_time += dt

                if cur_time >= next_consec_tick and cur_time <= consec_active_until:
                    consecration_ticks += 1
                    next_consec_tick = round(cur_time + 1.0, 2)

                if cur_time >= gcd_ready_at:
                    for ab in active_priority_list:
                        if ab == "hammer_of_wrath":
                            is_exec = (cur_time >= (fight_duration - exec_duration)) or (boss_hp_percent <= 20.0)
                            if is_exec and cur_time >= cd_ready["hammer_of_wrath"]:
                                how_count += 1
                                cd_ready["hammer_of_wrath"] = round(cur_time + 6.0, 2)
                                gcd_ready_at = round(cur_time + 1.5, 2)
                                break
                        elif ab in ("crusader_holy_strike", "strike_category_40", "shared_strike", "crusader_strike", "holy_strike"):
                            # Category 40 Shared Strike Cooldown (6.0s)
                            if cur_time >= cd_ready["shared_strike"]:
                                cs_allowed = enable_crusader_strike and (ramp_cs_target > 0 or strike_sustain_cs > 0)
                                hs_allowed = enable_holy_strike and (ramp_hs_target > 0 or strike_sustain_hs > 0)

                                chosen_strike = None
                                # 1. Check Ramp-up phase first (HS opener for Holy Might, then CS for Zeal)
                                if hs_allowed and ramp_hs_done < ramp_hs_target:
                                    chosen_strike = "holy_strike"
                                    ramp_hs_done += 1
                                    # If ramp-up is complete and only HS was in ramp, initialize sustain to start with CS
                                    if ramp_hs_done >= ramp_hs_target and ramp_cs_done >= ramp_cs_target and strike_sustain_cs > 0:
                                        sustain_hs_done = strike_sustain_hs
                                        sustain_cs_done = 0
                                elif cs_allowed and ramp_cs_done < ramp_cs_target:
                                    chosen_strike = "crusader_strike"
                                    ramp_cs_done += 1
                                    # If ramp-up is complete, reset sustain counters
                                    if ramp_hs_done >= ramp_hs_target and ramp_cs_done >= ramp_cs_target:
                                        sustain_hs_done = 0
                                        sustain_cs_done = 0
                                else:
                                    # 2. Sustain phase (after ramp-up)
                                    if cs_allowed and hs_allowed:
                                        if strike_sustain_hs > 0 and sustain_hs_done < strike_sustain_hs:
                                            chosen_strike = "holy_strike"
                                            sustain_hs_done += 1
                                            if sustain_hs_done >= strike_sustain_hs and strike_sustain_cs == 0:
                                                sustain_hs_done = 0
                                        elif strike_sustain_cs > 0 and sustain_cs_done < strike_sustain_cs:
                                            chosen_strike = "crusader_strike"
                                            sustain_cs_done += 1
                                            if sustain_cs_done >= strike_sustain_cs:
                                                sustain_hs_done = 0
                                                sustain_cs_done = 0
                                        else:
                                            chosen_strike = "crusader_strike"
                                    elif cs_allowed:
                                        chosen_strike = "crusader_strike"
                                    elif hs_allowed:
                                        chosen_strike = "holy_strike"

                                if chosen_strike == "crusader_strike":
                                    cs_count += 1
                                    zeal_stacks = min(3, zeal_stacks + 1)
                                    zeal_expires_at = round(cur_time + 15.0, 2)
                                    next_strike_cd = round(cur_time + 6.0, 2)
                                    cd_ready["shared_strike"] = next_strike_cd
                                    gcd_ready_at = round(cur_time + 1.5, 2)
                                    break
                                elif chosen_strike == "holy_strike":
                                    holy_strike_count += 1
                                    if vengeful_strikes > 0:
                                        holy_might_expires_at = round(cur_time + 20.0, 2)
                                    next_strike_cd = round(cur_time + 6.0, 2)
                                    cd_ready["shared_strike"] = next_strike_cd
                                    gcd_ready_at = round(cur_time + 1.5, 2)
                                    break
                        elif ab == "judgement":
                            if cur_time >= cd_ready["judgement"]:
                                judgement_count += 1
                                cd_ready["judgement"] = round(cur_time + effective_judge_interval, 2)
                                gcd_ready_at = round(cur_time + 1.5, 2)
                                break
                        elif ab == "consecration":
                            if cur_time >= cd_ready["consecration"]:
                                consec_count += 1
                                consec_active_until = round(cur_time + 8.0, 2)
                                if cur_time >= next_consec_tick:
                                    next_consec_tick = round(cur_time + 1.0, 2)
                                cd_ready["consecration"] = round(cur_time + 8.0, 2)
                                gcd_ready_at = round(cur_time + 1.5, 2)
                                break
                        elif ab == "exorcism":
                            if cur_time >= cd_ready["exorcism"]:
                                exorcism_count += 1
                                cd_ready["exorcism"] = round(cur_time + actual_exorcism_interval, 2)
                                gcd_ready_at = round(cur_time + 1.5, 2)
                                break
                        elif ab == "holy_shock":
                            if cur_time >= cd_ready["holy_shock"]:
                                holy_shock_count += 1
                                cd_ready["holy_shock"] = round(cur_time + 20.0, 2)
                                gcd_ready_at = round(cur_time + 1.5, 2)
                                break

                sim_t = round(sim_t + dt, 2)
        else:
            active_priority_list = []

        holy_might_uptime = (total_holy_might_time / fight_duration) if fight_duration > 0 else 0.0
        holy_might_str_mult = 1.0 + (0.04 * vengeful_strikes * holy_might_uptime)

        # Weapon enchants procs: Crusader (+100 Strength, 1 PPM)
        has_crusader = any(p.get("procspell") == "Crusader" or "crusader" in p.get("enchant_name", "").lower() for p in gear.get("weapon_procs", []))
        crusader_proc_str = 0.0
        if has_crusader and fight_duration > 0:
            total_attacks_est = exact_melee_swings + cs_count + holy_strike_count
            attacks_per_sec = total_attacks_est / fight_duration
            proc_chance_per_attack = min(1.0, (weapon_speed * 1.0) / 60.0)
            crusader_rate = attacks_per_sec * proc_chance_per_attack
            crusader_uptime = min(1.0, 1.0 - math.exp(-crusader_rate * 15.0))
            crusader_proc_str = 100.0 * crusader_uptime

        effective_str = (base_str + crusader_proc_str) * (1.0 + (0.02 * divine_strength)) * kings_mult * holy_might_str_mult
        ap = gear["attack_power"] + int(effective_str * 2)

        avg_zeal_haste = (total_zeal_haste_time / fight_duration) if fight_duration > 0 else 0.0
        effective_speed = weapon_speed / (1.0 + ((total_haste + avg_zeal_haste) / 100.0))
        melee_swings_count = 1.0 + (fight_duration / effective_speed) if fight_duration > 0 and effective_speed > 0 else 0.0
        exact_melee_swings = int(round(melee_swings_count))

        raw_swing_dmg = avg_weapon_dmg + (ap / 14.0) * weapon_speed
        avg_white_swing = raw_swing_dmg * (1.0 - armor_reduction) * physical_mult * (white_hit_chance + (2.0 * capped_crit) + (glance_damage_factor * glance_chance))
        white_damage_total = melee_swings_count * avg_white_swing
        white_dps = white_damage_total / fight_duration if fight_duration > 0 else 0.0

        # Check effects and procs from items
        # 1. Spellpower Goggles Xtreme Plus+ (ID 33088)
        # Direct harmful spells have 8% chance to grant +200 SP for 6 sec.
        has_sp_goggles = any(str(it.get("id")) in ("33088", "33085") or "Spellpower Goggles" in it.get("name", "") for it in gear.get("equipped_items", []))
        direct_spell_casts = (judgement_count + exorcism_count + how_count + holy_shock_count + holy_strike_count)
        direct_spell_hits = direct_spell_casts * spell_hit_chance
        direct_casts_per_sec = (direct_spell_hits / fight_duration) if fight_duration > 0 else 0.0
        goggles_uptime = 0.0
        if has_sp_goggles and direct_casts_per_sec > 0:
            rate = direct_casts_per_sec * 0.08
            goggles_uptime = min(1.0, 1.0 - math.exp(-rate * 6.0))
            sp += (200.0 * goggles_uptime)

        # 2. Libram of Hallowed Ground (ID 33086)
        has_libram_hallowed = any(str(it.get("id")) == "33086" or "Libram of Hallowed Ground" in it.get("name", "") for it in gear.get("equipped_items", []))
        hallowed_consec_bonus = 0.0
        if has_libram_hallowed and consec_count > 0:
            hallowed_consec_bonus = consec_count * (96.0 + 0.10 * sp) * holy_mult * spell_crit_multiplier

        # 3. Sigil of Ancient Accord (ID 58244)
        has_sigil = any(str(it.get("id")) == "58244" or "Sigil of Ancient Accord" in it.get("name", "") for it in gear.get("equipped_items", []))
        sigil_damage_total = 0.0
        sigil_dps = 0.0
        if has_sigil and direct_spell_hits > 0:
            sigil_procs = direct_spell_hits * 0.08
            sigil_hit = (400.0 + 0.20 * sp) * spell_crit_multiplier
            sigil_damage_total = sigil_procs * sigil_hit
            sigil_dps = sigil_damage_total / fight_duration if fight_duration > 0 else 0.0

        consec_tick_dmg = (54.0 + 0.0416 * sp + (joc_holy_bonus / 8.0)) * holy_mult
        consec_damage_total = (consecration_ticks * consec_tick_dmg) + hallowed_consec_bonus
        consec_dps = consec_damage_total / fight_duration if fight_duration > 0 else 0.0

        exorcism_hit = (534.0 + 0.4286 * sp + joc_holy_bonus) * spell_crit_multiplier * holy_mult * spell_hit_chance
        exorcism_damage_total = exorcism_count * exorcism_hit
        exorcism_dps = exorcism_damage_total / fight_duration if fight_duration > 0 else 0.0

        how_hit = (530.0 + 0.4286 * sp + joc_holy_bonus) * spell_crit_multiplier * holy_mult * spell_hit_chance
        how_damage_total = how_count * how_hit
        how_dps = how_damage_total / fight_duration if fight_duration > 0 else 0.0

        holy_shock_hit = (654.0 + 0.4286 * sp + joc_holy_bonus) * spell_crit_multiplier * holy_mult * spell_hit_chance
        holy_shock_damage_total = holy_shock_count * holy_shock_hit
        holy_shock_dps = holy_shock_damage_total / fight_duration if fight_duration > 0 else 0.0

        cs_damage_total = 0.0
        cs_dps = 0.0
        holy_strike_damage_total = 0.0
        holy_strike_dps = 0.0
        seal_damage_total = 0.0
        seal_dps = 0.0
        judgement_damage_total = 0.0
        judgement_dps = 0.0
        total_magic_hits = 0

        cs_talent_mult = 1.0 + (0.02 * vengeful_strikes)
        cs_special_hit_chance = max(0.0, 1.0 - effective_miss - effective_dodge)
        cs_raw = avg_weapon_dmg + 160.0 + (ap / 14.0) * min(weapon_speed, 3.3)
        cs_hit = cs_raw * (1.0 - armor_reduction) * (1.0 + crit_chance) * physical_mult * cs_talent_mult * cs_special_hit_chance
        cs_damage_total = cs_count * cs_hit
        cs_dps = cs_damage_total / fight_duration if fight_duration > 0 else 0.0

        hs_talent_mult = 1.0 + (0.05 * righteous_strikes)
        hs_special_hit_chance = max(0.0, 1.0 - effective_miss - effective_dodge)
        hs_raw = avg_weapon_dmg + 137.0 + (ap / 14.0) * min(weapon_speed, 3.3) + (0.20 * sp) + joc_holy_bonus
        hs_hit = hs_raw * holy_mult * spell_crit_multiplier * hs_talent_mult * hs_special_hit_chance
        holy_strike_damage_total = holy_strike_count * hs_hit
        holy_strike_dps = holy_strike_damage_total / fight_duration if fight_duration > 0 else 0.0

        # Check Librams
        # 1. Libram of Final Judgement (ID 58240): +200 Holy damage to Judgement on enemies below 35% health
        has_libram_final_judgement = any(str(it.get("id")) == "58240" or "final judgement" in str(it.get("name", "")).lower() for it in gear.get("equipped_items", []))
        final_judgement_bonus = 0.0
        if has_libram_final_judgement and judgement_count > 0:
            boss_hp = max(1.0, min(100.0, float(boss_hp_percent)))
            sub_35_frac = min(1.0, 35.0 / boss_hp)
            sub_35_judgements = judgement_count * sub_35_frac * spell_hit_chance
            final_judgement_bonus = sub_35_judgements * 200.0 * holy_mult * spell_crit_multiplier

        # 2. Libram of Ardour (ID 33087): Increases proc chance of Seal of Command
        has_libram_ardour = any(str(it.get("id")) == "33087" or "ardour" in str(it.get("name", "")).lower() for it in gear.get("equipped_items", []))
        soc_ppm = 8.5 if has_libram_ardour else 7.0

        if chosen_seal == "command":
            soc_proc_chance = min(1.0, (weapon_speed * soc_ppm) / 60.0)
            soc_hit_chance = max(0.0, 1.0 - effective_miss - effective_dodge)
            raw_soc = 0.70 * raw_swing_dmg + (0.29 * sp) + joc_holy_bonus
            soc_hit = raw_soc * (1.0 + crit_chance) * holy_mult

            swing_soc_procs = melee_swings_count * soc_proc_chance * soc_hit_chance
            cs_soc_procs = cs_count * cs_special_hit_chance * soc_proc_chance * soc_hit_chance
            hs_soc_procs = holy_strike_count * hs_special_hit_chance * soc_proc_chance * soc_hit_chance
            total_soc_procs = swing_soc_procs + cs_soc_procs + hs_soc_procs
            seal_damage_total = total_soc_procs * soc_hit
            seal_dps = seal_damage_total / fight_duration if fight_duration > 0 else 0.0

            joc_hit = (177.5 + 0.4286 * sp + joc_holy_bonus) * spell_crit_multiplier * holy_mult * spell_hit_chance
            judgement_damage_total = (judgement_count * joc_hit) + final_judgement_bonus
            judgement_dps = judgement_damage_total / fight_duration if fight_duration > 0 else 0.0

            total_magic_hits = (
                int(total_soc_procs)
                + int(exact_melee_swings * landed_swing_chance * t2_instances_per_swing)
                + int(judgement_count * spell_hit_chance)
                + consecration_ticks
                + int(exorcism_count * spell_hit_chance)
                + int(how_count * spell_hit_chance)
                + int(holy_shock_count * spell_hit_chance)
                + int(holy_strike_count * spell_hit_chance)
            )
        elif chosen_seal == "vengeance":
            # Seal of Vengeance: Stacks a Holy DoT up to 5 times (640 damage over 15s at 5 stacks),
            # and each melee swing at 5 stacks deals bonus 33% weapon Holy damage.
            sov_dot_ticks = (fight_duration / 3.0) if fight_duration > 0 else 0.0
            sov_dot_tick_dmg = ((640.0 + 0.40 * sp + joc_holy_bonus) / 5.0) * holy_mult * spell_crit_multiplier
            sov_dot_damage_total = sov_dot_ticks * sov_dot_tick_dmg

            swings_at_5_stacks = max(0.0, melee_swings_count - 5.0) * landed_swing_chance
            sov_weapon_hit = (avg_weapon_dmg * 0.33 + 0.10 * sp + joc_holy_bonus) * holy_mult * spell_crit_multiplier
            sov_weapon_damage_total = swings_at_5_stacks * sov_weapon_hit

            seal_damage_total = sov_dot_damage_total + sov_weapon_damage_total
            seal_dps = seal_damage_total / fight_duration if fight_duration > 0 else 0.0

            jov_hit = (350.0 + 0.45 * sp + joc_holy_bonus) * holy_mult * spell_crit_multiplier * spell_hit_chance
            judgement_damage_total = (judgement_count * jov_hit) + final_judgement_bonus
            judgement_dps = judgement_damage_total / fight_duration if fight_duration > 0 else 0.0

            swing_magic_hits = int(exact_melee_swings * landed_swing_chance * (1 + t2_instances_per_swing))
            total_magic_hits = (
                swing_magic_hits
                + int(judgement_count * spell_hit_chance)
                + int(sov_dot_ticks)
                + consecration_ticks
                + int(exorcism_count * spell_hit_chance)
                + int(how_count * spell_hit_chance)
                + int(holy_shock_count * spell_hit_chance)
                + int(holy_strike_count * spell_hit_chance)
            )
        else:
            # Seal of Righteousness
            sor_mult = 1.0 + (0.02 * improved_sor)
            sor_base = weapon_speed * 18.5
            sor_sp_coef = (weapon_speed / 20.0) * (1.2 if is_two_hand else 1.0)
            sor_hit = (sor_base + sor_sp_coef * sp + (joc_holy_bonus * (weapon_speed / 2.6))) * spell_crit_multiplier * holy_mult * sor_mult
            seal_damage_total = melee_swings_count * landed_swing_chance * sor_hit
            seal_dps = seal_damage_total / fight_duration if fight_duration > 0 else 0.0

            jor_bonus = 148.0 if t1_dps_pieces >= 3 else 0.0
            jor_hit = (185.0 + jor_bonus + 0.50 * sp + joc_holy_bonus) * spell_crit_multiplier * holy_mult * sor_mult * spell_hit_chance
            judgement_damage_total = (judgement_count * jor_hit) + final_judgement_bonus
            judgement_dps = judgement_damage_total / fight_duration if fight_duration > 0 else 0.0

            swing_magic_hits = int(exact_melee_swings * landed_swing_chance * (1 + t2_instances_per_swing))
            total_magic_hits = (
                swing_magic_hits
                + int(judgement_count * spell_hit_chance)
                + consecration_ticks
                + int(exorcism_count * spell_hit_chance)
                + int(how_count * spell_hit_chance)
                + int(holy_shock_count * spell_hit_chance)
                + int(holy_strike_count * spell_hit_chance)
            )

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

        has_ragnaros = any(it.get("id") == 17182 for it in gear["equipped_items"])
        ragnaros_damage_total = 0.0
        ragnaros_dps = 0.0
        if has_ragnaros:
            rag_procs = exact_melee_swings * (weapon_speed * 1.0 / 60.0)
            rag_hit = (250.0 + 0.20 * sp) * spell_crit_multiplier
            ragnaros_damage_total = rag_procs * rag_hit
            ragnaros_dps = ragnaros_damage_total / fight_duration if fight_duration > 0 else 0.0

        # Weapon enchant procs: Fiery Weapon & Lifestealing
        fiery_procs_entry = [p for p in gear.get("weapon_procs", []) if "fiery" in p.get("enchant_name", "").lower() or p.get("magicdmg") == 40]
        fiery_damage_total = 0.0
        fiery_dps = 0.0
        if fiery_procs_entry and fight_duration > 0:
            total_attacks_count = exact_melee_swings + cs_count + holy_strike_count
            fiery_ppm = 6.0
            fiery_chance = min(1.0, (weapon_speed * fiery_ppm) / 60.0)
            fiery_procs = total_attacks_count * fiery_chance * landed_swing_chance
            fiery_hit = 40.0 * spell_crit_multiplier
            fiery_damage_total = fiery_procs * fiery_hit
            fiery_dps = fiery_damage_total / fight_duration
            total_magic_hits += int(fiery_procs)

        lifestealing_entry = [p for p in gear.get("weapon_procs", []) if "lifestealing" in p.get("enchant_name", "").lower() or p.get("magicdmg") == 30]
        lifestealing_damage_total = 0.0
        lifestealing_dps = 0.0
        if lifestealing_entry and fight_duration > 0:
            total_attacks_count = exact_melee_swings + cs_count + holy_strike_count
            life_ppm = 6.0
            life_chance = min(1.0, (weapon_speed * life_ppm) / 60.0)
            life_procs = total_attacks_count * life_chance * landed_swing_chance
            life_hit = 30.0 * spell_crit_multiplier
            lifestealing_damage_total = life_procs * life_hit
            lifestealing_dps = lifestealing_damage_total / fight_duration
        other_weapon_procs_list = []
        for p in gear.get("weapon_procs", []):
            p_name = p.get("enchant_name", "").strip()
            p_name_lower = p_name.lower()
            if "fiery" in p_name_lower or "lifestealing" in p_name_lower or p.get("procspell") == "Crusader":
                continue
            magicdmg = float(p.get("magicdmg", 0))
            if magicdmg > 0 and fight_duration > 0:
                total_attacks_count = exact_melee_swings + cs_count + holy_strike_count
                ppm = p.get("ppm")
                chance = p.get("chance")
                if ppm:
                    proc_chance = min(1.0, (weapon_speed * float(ppm)) / 60.0)
                elif chance:
                    proc_chance = float(chance) / 100.0
                else:
                    proc_chance = 0.05
                p_procs = total_attacks_count * proc_chance * landed_swing_chance
                p_hit = magicdmg * spell_crit_multiplier
                p_dmg = p_procs * p_hit
                p_dps = p_dmg / fight_duration
                total_magic_hits += int(p_procs)
                other_weapon_procs_list.append({
                    "name": p_name or "Weapon Proc",
                    "dps": p_dps,
                    "damage": p_dmg,
                })

        # Item Procs:
        # 1. Embrace of the Wind Serpent (ID 12462): 15% proc chance on damaging spells, deals 55-71 Shadow damage + 0.15*SP
        wind_serpent_damage_total = 0.0
        wind_serpent_dps = 0.0
        if has_wind_serpent and fight_duration > 0:
            ws_spell_hits = (
                consecration_ticks
                + int(judgement_count * spell_hit_chance)
                + int(exorcism_count * spell_hit_chance)
                + int(how_count * spell_hit_chance)
                + int(holy_shock_count * spell_hit_chance)
                + int(holy_strike_count * spell_hit_chance)
            )
            ws_procs = ws_spell_hits * 0.15
            ws_hit = (63.0 + 0.15 * sp) * spell_crit_multiplier
            wind_serpent_damage_total = ws_procs * ws_hit
            wind_serpent_dps = wind_serpent_damage_total / fight_duration
            total_magic_hits += int(ws_procs)

        # 2. Darkmoon Card: Maelstrom (ID 19289)
        has_maelstrom = any(str(it.get("id")) == "19289" or "maelstrom" in str(it.get("name", "")).lower() for it in gear.get("equipped_items", []))
        maelstrom_damage_total = 0.0
        maelstrom_dps = 0.0
        if has_maelstrom and fight_duration > 0:
            maelstrom_procs = exact_melee_swings * (weapon_speed * 1.7 / 60.0) * landed_swing_chance
            maelstrom_damage_total = maelstrom_procs * 250.0 * spell_crit_multiplier
            maelstrom_dps = maelstrom_damage_total / fight_duration
            total_magic_hits += int(maelstrom_procs)

        # 3. Thunderfury, Blessed Blade of the Windseeker (ID 19019)
        has_tf = any(str(it.get("id")) == "19019" or "thunderfury" in str(it.get("name", "")).lower() for it in gear.get("equipped_items", []))
        tf_damage_total = 0.0
        tf_dps = 0.0
        if has_tf and fight_duration > 0:
            tf_procs = exact_melee_swings * (weapon_speed * 6.0 / 60.0) * landed_swing_chance
            tf_damage_total = tf_procs * 300.0 * spell_crit_multiplier
            tf_dps = tf_damage_total / fight_duration
            total_magic_hits += int(tf_procs)

        # 4. Perdition's Blade (ID 18816)
        has_perdition = any(str(it.get("id")) == "18816" or "perdition" in str(it.get("name", "")).lower() for it in gear.get("equipped_items", []))
        perd_damage_total = 0.0
        perd_dps = 0.0
        if has_perdition and fight_duration > 0:
            perd_procs = exact_melee_swings * 0.04 * landed_swing_chance
            perd_damage_total = perd_procs * 45.0 * spell_crit_multiplier
            perd_dps = perd_damage_total / fight_duration

        # 5. Teebu's Blazing Longsword (ID 1728)
        has_teebu = any(str(it.get("id")) == "1728" or "teebu" in str(it.get("name", "")).lower() for it in gear.get("equipped_items", []))
        teebu_damage_total = 0.0
        teebu_dps = 0.0
        if has_teebu and fight_duration > 0:
            teebu_procs = exact_melee_swings * (weapon_speed * 1.5 / 60.0) * landed_swing_chance
            teebu_damage_total = teebu_procs * 150.0 * spell_crit_multiplier
            teebu_dps = teebu_damage_total / fight_duration

        # 6. Ring of Burning Talons (ID 33154)
        has_burning_talons = any(str(it.get("id")) == "33154" or "burning talons" in str(it.get("name", "")).lower() for it in gear.get("equipped_items", []))
        talons_damage_total = 0.0
        talons_dps = 0.0
        if has_burning_talons and fight_duration > 0:
            talons_procs = (direct_spell_hits + consecration_ticks) * 0.10
            talons_damage_total = talons_procs * (140.0 + 0.10 * sp) * spell_crit_multiplier
            talons_dps = talons_damage_total / fight_duration
            total_magic_hits += int(talons_procs)

        # 7. Flat Bonus Melee Elemental Items (e.g. Incendosaur Skin Boots, Sizzling Aureole, Fiery Retributer)
        on_hit_fire_per_swing = sum(2.0 for it in gear.get("equipped_items", []) if str(it.get("id")) in ("60568", "58209", "19968", "17111", "12590") or "adds 2 fire damage to your melee attacks" in str(it.get("text", "")).lower())
        on_hit_fire_damage_total = exact_melee_swings * landed_swing_chance * on_hit_fire_per_swing
        on_hit_fire_dps = on_hit_fire_damage_total / fight_duration if fight_duration > 0 else 0.0

        magic_hits_per_second = total_magic_hits / fight_duration if fight_duration > 0 else 0.0

        own_damage_total = (
            white_damage_total
            + cs_damage_total
            + holy_strike_damage_total
            + t2_flat_holy_total
            + seal_damage_total
            + judgement_damage_total
            + t2_proc_damage_total
            + t1_proc_damage_total
            + consec_damage_total
            + exorcism_damage_total
            + how_damage_total
            + holy_shock_damage_total
            + ragnaros_damage_total
            + sigil_damage_total
            + fiery_damage_total
            + lifestealing_damage_total
            + wind_serpent_damage_total
            + maelstrom_damage_total
            + tf_damage_total
            + perd_damage_total
            + teebu_damage_total
            + talons_damage_total
            + on_hit_fire_damage_total
            + sum(owp["damage"] for owp in other_weapon_procs_list)
        )
        own_dps = own_damage_total / fight_duration if fight_duration > 0 else 0.0

        has_minions = gear.get("has_pet_summon", False) or has_lost_set or (active_build == "nekrodyn")
        minion_dps_avg = 0.0
        minion_dps_min = 0.0
        minion_dps_max = 0.0
        minion_damage_total = 0.0
        expected_active_minions = 0.0
        procs_per_sec = 0.0

        if has_lost_set or active_build == "nekrodyn":
            lost_proc_chance = 0.04
            procs_per_sec = magic_hits_per_second * lost_proc_chance
            expected_active_minions = procs_per_sec * 20.0
            single_minion_avg_dps = 254.5 / 2.0
            single_minion_min_dps = 230.0 / 2.0
            single_minion_max_dps = 279.0 / 2.0
            minion_dps_avg += expected_active_minions * single_minion_avg_dps
            minion_dps_min += expected_active_minions * single_minion_min_dps
            minion_dps_max += expected_active_minions * single_minion_max_dps

        eskhandar_dps = 0.0
        eskhandar_damage_total = 0.0
        if gear.get("has_pet_summon", False) and "Spirit of Eskhandar" in gear.get("pet_summon_details", []):
            crit_swings_per_sec = (exact_melee_swings / fight_duration if fight_duration > 0 else 0.0) * crit_chance
            eskhandar_proc_chance = 0.01
            eskhandar_procs = crit_swings_per_sec * eskhandar_proc_chance
            eskhandar_minions = min(1.0, eskhandar_procs * 120.0)
            expected_active_minions += eskhandar_minions
            procs_per_sec += eskhandar_procs
            eskhandar_dps = eskhandar_minions * (70.0 / 1.5)
            eskhandar_damage_total = eskhandar_dps * fight_duration
            minion_dps_avg += eskhandar_dps
            minion_dps_min += eskhandar_minions * (60.0 / 1.5)
            minion_dps_max += eskhandar_minions * (80.0 / 1.5)

        minion_damage_total = minion_dps_avg * fight_duration
        total_dps = own_dps + minion_dps_avg
        total_damage = own_damage_total + minion_damage_total

        physical_dps = white_dps + cs_dps + eskhandar_dps
        holy_spell_dps = (
            seal_dps
            + judgement_dps
            + consec_dps
            + exorcism_dps
            + how_dps
            + holy_shock_dps
            + holy_strike_dps
            + t2_flat_holy_dps
            + t2_proc_dps
            + t1_proc_dps
            + sigil_dps
        )
        elemental_proc_dps = (
            ragnaros_dps
            + fiery_dps
            + lifestealing_dps
            + wind_serpent_dps
            + maelstrom_dps
            + tf_dps
            + perd_dps
            + teebu_dps
            + talons_dps
            + on_hit_fire_dps
        )
        minion_shadow_dps = max(0.0, minion_dps_avg - eskhandar_dps)

        safe_total_dps = total_dps if total_dps > 0 else 1.0
        physical_pct = round((physical_dps / safe_total_dps) * 100.0, 1)
        holy_pct = round((holy_spell_dps / safe_total_dps) * 100.0, 1)
        minion_pct = round(((minion_shadow_dps + eskhandar_dps) / safe_total_dps) * 100.0, 1)

        breakdown = {
            "white_melee_dps": round(white_dps, 2),
        }
        if cs_dps > 0:
            breakdown["crusader_strike_dps"] = round(cs_dps, 2)
        if holy_strike_dps > 0:
            breakdown["holy_strike_dps"] = round(holy_strike_dps, 2)

        if chosen_seal == "command":
            if seal_dps > 0:
                breakdown["seal_of_command_dps"] = round(seal_dps, 2)
            if judgement_dps > 0:
                breakdown["judgement_of_command_dps"] = round(judgement_dps, 2)
        elif chosen_seal == "vengeance":
            if seal_dps > 0:
                breakdown["seal_of_vengeance_dps"] = round(seal_dps, 2)
            if judgement_dps > 0:
                breakdown["judgement_of_vengeance_dps"] = round(judgement_dps, 2)
        else:
            if seal_dps > 0:
                breakdown["seal_of_righteousness_dps"] = round(seal_dps, 2)
            if judgement_dps > 0:
                breakdown["judgement_of_righteousness_dps"] = round(judgement_dps, 2)

        if consec_dps > 0:
            breakdown["consecration_dps"] = round(consec_dps, 2)
        if exorcism_dps > 0:
            breakdown["exorcism_dps"] = round(exorcism_dps, 2)
        if how_damage_total > 0:
            breakdown["hammer_of_wrath_dps"] = round(how_dps, 2)
        if holy_shock_dps > 0:
            breakdown["holy_shock_dps"] = round(holy_shock_dps, 2)
        if t2_flat_holy_dps > 0:
            breakdown["judgement_3set_holy_dps"] = round(t2_flat_holy_dps, 2)
        if t2_proc_dps > 0:
            breakdown["judgement_8set_smite_dps"] = round(t2_proc_dps, 2)
        if t1_proc_dps > 0:
            breakdown["lawbringer_8set_holy_dps"] = round(t1_proc_dps, 2)
        if ragnaros_dps > 0:
            breakdown["wrath_of_ragnaros_dps"] = round(ragnaros_dps, 2)
        if sigil_dps > 0:
            breakdown["sigil_of_ancient_accord_dps"] = round(sigil_dps, 2)
        if has_sp_goggles and goggles_uptime > 0:
            breakdown["goggles_proc_sp_avg"] = round(200.0 * goggles_uptime, 1)
        if has_libram_hallowed and hallowed_consec_bonus > 0:
            breakdown["consecration_hallowed_bonus_dps"] = round(hallowed_consec_bonus / fight_duration, 2)
        if has_libram_final_judgement and final_judgement_bonus > 0:
            breakdown["libram_of_final_judgement_dps"] = round(final_judgement_bonus / fight_duration, 2)
        if has_libram_ardour:
            breakdown["libram_of_ardour_active"] = True
        if fiery_dps > 0:
            breakdown["fiery_weapon_dps"] = round(fiery_dps, 2)
        if lifestealing_dps > 0:
            breakdown["lifestealing_dps"] = round(lifestealing_dps, 2)
        if wind_serpent_dps > 0:
            breakdown["embrace_of_the_wind_serpent_dps"] = round(wind_serpent_dps, 2)
        if maelstrom_dps > 0:
            breakdown["darkmoon_card_maelstrom_dps"] = round(maelstrom_dps, 2)
        if tf_dps > 0:
            breakdown["thunderfury_dps"] = round(tf_dps, 2)
        if perd_dps > 0:
            breakdown["perditions_blade_dps"] = round(perd_dps, 2)
        if teebu_dps > 0:
            breakdown["teebus_blazing_longsword_dps"] = round(teebu_dps, 2)
        if talons_dps > 0:
            breakdown["ring_of_burning_talons_dps"] = round(talons_dps, 2)
        if on_hit_fire_dps > 0:
            breakdown["on_hit_elemental_dps"] = round(on_hit_fire_dps, 2)
        if crusader_proc_str > 0:
            breakdown["crusader_proc_str_avg"] = round(crusader_proc_str, 1)

        # Build full unified damage_sources list for rich Attack Breakdown
        damage_sources = []
        def add_source(src_id, name, dps_val, dmg_val, cat, color, spell_key=None, is_minion=False, is_proc=False):
            if dps_val > 0.001 or dmg_val > 0.001:
                pct = round((dps_val / safe_total_dps) * 100.0, 1)
                damage_sources.append({
                    "id": src_id,
                    "name": name,
                    "category": cat,
                    "color": color,
                    "dps": round(dps_val, 2),
                    "damage": round(dmg_val, 1),
                    "percent": pct,
                    "spell_key": spell_key,
                    "is_minion": is_minion,
                    "is_proc": is_proc,
                })

        add_source("white_melee", "White Auto-Attacks", white_dps, white_damage_total, "Physical", "#c79c6e")
        if cs_dps > 0:
            add_source("crusader_strike", "Crusader Strike (Zeal Haste)", cs_dps, cs_damage_total, "Physical", "#c79c6e", spell_key="crusader_strike")
        if holy_strike_dps > 0:
            add_source("holy_strike", "Holy Strike", holy_strike_dps, holy_strike_damage_total, "Holy", "#f5d565", spell_key="holy_strike")

        if chosen_seal == "command":
            if seal_dps > 0:
                add_source("seal_of_command", "Seal of Command (Proc)", seal_dps, seal_damage_total, "Holy", "#f5d565", spell_key="seal_of_command", is_proc=True)
            if judgement_dps > 0:
                add_source("judgement_of_command", "Judgement of Command", judgement_dps, judgement_damage_total, "Holy", "#f5d565", spell_key="seal_of_command")
        elif chosen_seal == "vengeance":
            if seal_dps > 0:
                add_source("seal_of_vengeance", "Seal of Vengeance (DoT & Strike)", seal_dps, seal_damage_total, "Holy", "#f5d565", spell_key="seal_of_vengeance")
            if judgement_dps > 0:
                add_source("judgement_of_vengeance", "Judgement of Vengeance", judgement_dps, judgement_damage_total, "Holy", "#f5d565", spell_key="seal_of_vengeance")
        else:
            if seal_dps > 0:
                add_source("seal_of_righteousness", "Seal of Righteousness", seal_dps, seal_damage_total, "Holy", "#f5d565", spell_key="seal_of_righteousness")
            if judgement_dps > 0:
                add_source("judgement_of_righteousness", "Judgement of Righteousness", judgement_dps, judgement_damage_total, "Holy", "#f5d565", spell_key="seal_of_righteousness")

        if consec_dps > 0:
            add_source("consecration", "Consecration (Holy AoE)", consec_dps, consec_damage_total, "Holy", "#f5d565", spell_key="consecration")
        if exorcism_dps > 0:
            add_source("exorcism", "Exorcism", exorcism_dps, exorcism_damage_total, "Holy", "#f5d565", spell_key="exorcism")
        if how_damage_total > 0:
            add_source("hammer_of_wrath", "Hammer of Wrath (<20% Execute)", how_dps, how_damage_total, "Holy", "#f5d565", spell_key="hammer_of_wrath")
        if holy_shock_dps > 0:
            add_source("holy_shock", "Holy Shock", holy_shock_dps, holy_shock_damage_total, "Holy", "#f5d565", spell_key="holy_shock")
        if t2_flat_holy_dps > 0:
            add_source("judgement_3set_holy", "Judgement 3-Piece Holy Damage", t2_flat_holy_dps, t2_flat_holy_total, "Holy", "#f5d565")
        if t2_proc_dps > 0:
            add_source("judgement_8set_smite", "Judgement 8-Piece Smite Proc", t2_proc_dps, t2_proc_damage_total, "Holy", "#f5d565", is_proc=True)
        if t1_proc_dps > 0:
            add_source("lawbringer_8set_holy", "Lawbringer 8-Piece Holy Radiance", t1_proc_dps, t1_proc_damage_total, "Holy", "#f5d565", is_proc=True)
        if has_libram_final_judgement and final_judgement_bonus > 0:
            add_source("libram_of_final_judgement", "Libram of Final Judgement (<35% Execute)", final_judgement_bonus / fight_duration if fight_duration > 0 else 0.0, final_judgement_bonus, "Holy", "#f5d565")
        if fiery_dps > 0:
            add_source("fiery_weapon", "Fiery Weapon Enchant (Proc)", fiery_dps, fiery_damage_total, "Fire", "#ff5533", is_proc=True)
        if lifestealing_dps > 0:
            add_source("lifestealing", "Lifestealing Enchant (Proc)", lifestealing_dps, lifestealing_damage_total, "Shadow", "#a335ee", is_proc=True)
        if wind_serpent_dps > 0:
            add_source("embrace_of_the_wind_serpent", "Embrace of the Wind Serpent (Shadow Decay Proc)", wind_serpent_dps, wind_serpent_damage_total, "Shadow", "#a335ee", is_proc=True)
        if ragnaros_dps > 0:
            add_source("wrath_of_ragnaros", "Sulfuras: Wrath of Ragnaros (Fireball)", ragnaros_dps, ragnaros_damage_total, "Fire", "#ff5533", is_proc=True)
        if maelstrom_dps > 0:
            add_source("darkmoon_maelstrom", "Darkmoon Card: Maelstrom (Lightning)", maelstrom_dps, maelstrom_damage_total, "Nature", "#44dd66", is_proc=True)
        if tf_dps > 0:
            add_source("thunderfury", "Thunderfury (Chain Lightning)", tf_dps, tf_damage_total, "Nature", "#44dd66", is_proc=True)
        if perd_dps > 0:
            add_source("perditions_blade", "Perdition's Blade (Fire Blast)", perd_dps, perd_damage_total, "Fire", "#ff5533", is_proc=True)
        if teebu_dps > 0:
            add_source("teebus_blazing_longsword", "Teebu's Blazing Longsword (Fire Blast)", teebu_dps, teebu_damage_total, "Fire", "#ff5533", is_proc=True)
        if talons_dps > 0:
            add_source("ring_of_burning_talons", "Ring of Burning Talons (Conflagration)", talons_dps, talons_damage_total, "Fire", "#ff5533", is_proc=True)
        if sigil_dps > 0:
            add_source("sigil_of_ancient_accord", "Sigil of Ancient Accord", sigil_dps, sigil_damage_total, "Holy", "#f5d565", is_proc=True)
        if on_hit_fire_dps > 0:
            add_source("on_hit_elemental_items", "Equip: Bonus Melee Fire Damage", on_hit_fire_dps, on_hit_fire_damage_total, "Fire", "#ff5533")
        for owp in other_weapon_procs_list:
            if owp["dps"] > 0:
                slug = owp["name"].lower().replace(" ", "_").replace("(", "").replace(")", "").replace("+", "").replace("-", "")
                add_source(f"proc_{slug}", f"{owp['name']} (Proc)", owp["dps"], owp["damage"], "Fire", "#ff5533", is_proc=True)

        # Minions
        if (has_lost_set or active_build == "nekrodyn") and minion_shadow_dps > 0:
            lost_dmg = minion_shadow_dps * fight_duration
            add_source("minion_soul_bolts", "Set of the Lost: Soul Harvesters (Soul Bolt Minions)", minion_shadow_dps, lost_dmg, "Shadow", "#a335ee", is_minion=True)
        if eskhandar_dps > 0:
            add_source("minion_eskhandar", "Spirit of Eskhandar (Feline Minion)", eskhandar_dps, eskhandar_damage_total, "Physical", "#c79c6e", is_minion=True)

        build_names = {
            "retribution": "Classic Retribution",
            "spellret": "Spellret (Spelladin)",
            "nekrodyn": "Nekrodyn"
        }

        ability_casts = {
            "crusader_strike": cs_count,
            "holy_strike": holy_strike_count,
            "judgement": judgement_count,
            "consecration": consec_count,
            "consecration_ticks": consecration_ticks,
            "exorcism": exorcism_count,
            "hammer_of_wrath": how_count,
            "holy_shock": holy_shock_count,
        }
        if opener_joc_casts > 0:
            ability_casts["judgement_of_the_crusader"] = opener_joc_casts

        total_mana_spent = (cs_count * 120) + (holy_strike_count * 90) + (consec_count * 505) + (exorcism_count * 345) + (how_count * 425) + (holy_shock_count * 485)
        mana_per_second = total_mana_spent / fight_duration if fight_duration > 0 else 0.0

        return {
            "character_class": "paladin",
            "paladin_build": active_build,
            "paladin_build_name": build_names.get(active_build, "Paladin"),
            "primary_seal": chosen_seal,
            "primary_seal_name": "Seal of Command" if chosen_seal == "command" else ("Seal of Vengeance" if chosen_seal == "vengeance" else "Seal of Righteousness"),
            "seal_fallback_reason": seal_fallback_reason,
            "apply_crusader_first": apply_crusader_first,
            "joc_holy_bonus": round(joc_holy_bonus, 1),
            "rotation_mode": rot_mode,
            "rotation_mode_name": "Priority Rotation" if rot_mode == "priority_rotation" else "Auto Attack Only",
            "priority_list": active_priority_list,
            "ability_casts": ability_casts,
            "zeal_haste_percent": round(avg_zeal_haste, 1),
            "strike_sequence": {
                "ramp_mode": strike_ramp_mode,
                "ramp_hs": ramp_hs_target,
                "ramp_cs": ramp_cs_target,
                "sustain_hs": strike_sustain_hs,
                "sustain_cs": strike_sustain_cs,
            },
            "mana_stats": {
                "total_mana_spent": total_mana_spent,
                "mana_per_second": round(mana_per_second, 1)
            },
            "fight_duration": fight_duration,
            "race": race_clean.capitalize(),
            "weapon_name": weapon_name,
            "base_weapon_speed": weapon_speed,
            "effective_weapon_speed": round(effective_speed, 2),
            "exact_melee_swings": exact_melee_swings,
            "total_attack_power": ap,
            "total_spell_power": round(sp, 1),
            "goggles_proc_uptime_percent": round(goggles_uptime * 100.0, 1),
            "healing_power": gear["healing"],
            "total_crit_percent": round(crit_pct, 2),
            "total_spell_crit_percent": round(spell_crit_pct, 2),
            "total_hit_percent": round(hit_pct, 2),
            "total_spell_hit_percent": round(spell_hit_pct, 2),
            "boss_hp_percent": boss_hp_percent,
            "execute_phase_percent": execute_phase_percent if boss_hp_percent > 20.0 else 100.0,
            "execute_duration_seconds": round(exec_duration, 1),
            "resistances": gear["resistances"],
            "has_minions": has_minions,
            "total_magic_hits": total_magic_hits,
            "magic_hits_per_second": round(magic_hits_per_second, 3),
            "procs_per_second": round(procs_per_sec, 3),
            "expected_active_minions": round(expected_active_minions, 3),
            "t2_instances_per_swing": t2_instances_per_swing,
            "t2_tank_active": bool(t2_tank_pieces >= 3),
            "t2_dps_active": bool(t2_dps_pieces >= 3),
            "lost_set_active": has_lost_set,
            "active_sets": active_sets,
            "damage_type_breakdown": {
                "physical_dps": round(physical_dps, 2),
                "holy_spell_dps": round(holy_spell_dps, 2),
                "minion_shadow_dps": round(minion_shadow_dps, 2),
                "physical_percent": physical_pct,
                "holy_spell_percent": holy_pct,
                "minion_shadow_percent": minion_pct
            },
            "own_damage_breakdown": breakdown,
            "damage_sources": damage_sources,
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
                "agility": int(effective_agi),
                "stamina": int(gear["stamina"] * kings_mult),
                "intellect": int(effective_int),
                "spirit": int(gear["spirit"] * kings_mult),
                "armor": gear["armor"],
                "equipped_count": len(gear["equipped_items"]),
                "effective_weapon_skill": effective_weapon_skill,
                "weapon_skill": effective_weapon_skill,
                "weapon_skill_hit_bonus": weapon_skill_hit_bonus,
                "glance_damage_factor": round(glance_damage_factor, 3),
            },
            "weapon_skill": effective_weapon_skill,
            "effective_weapon_skill": effective_weapon_skill,
            "equipped_weapon_skills": gear.get("equipped_weapon_skills", []),
            "weapon_skill_hit_bonus": weapon_skill_hit_bonus,
            "glance_damage_factor": round(glance_damage_factor, 3),
            "effective_dodge_percent": round(effective_dodge * 100.0, 2),
            "effective_miss_percent": round(effective_miss * 100.0, 2),
            "holy_might_uptime_percent": round(holy_might_uptime * 100.0, 1),
            "holy_might_strength_bonus_percent": round(vengeful_strikes * 4.0, 1) if vengeful_strikes > 0 else 0.0,
            "dual_wield_warning": gear.get("dual_wield_warning"),
            "relic_warning": gear.get("relic_warning"),
            "class_warnings": gear.get("class_warnings", []),
        }
