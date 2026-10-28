import math
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
        pet_family: str = "cat",
        combat_style: str = "auto",
        quiver_haste: float = 14.0,
        ammo_dps: float = 17.5,
        talents: Optional[Dict[str, int]] = None,
        race: str = "nightelf",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        t = talents or {}

        # Beast Mastery Talents
        unleashed_fury = int(t.get("Unleashed Fury", t.get("unleashed_fury", 0)))
        ferocity = int(t.get("Ferocity", t.get("ferocity", 0)))
        frenzy = int(t.get("Frenzy", t.get("frenzy", 0)))
        bestial_discipline = int(t.get("Bestial Discipline", t.get("bestial_discipline", 0)))
        bestial_wrath_talent = int(t.get("Bestial Wrath", t.get("bestial_wrath", 0)))
        intimidation_talent = int(t.get("Intimidation", t.get("intimidation", 0)))

        # Marksmanship Talents (including Turtle WoW 1.18 rework)
        lethal_shots = int(t.get("Lethal Shots", t.get("lethal_shots", 0)))
        mortal_shots = int(t.get("Mortal Shots", t.get("mortal_shots", 0)))
        aimed_shot_talent = int(t.get("Aimed Shot", t.get("aimed_shot", 0)))
        barrage = int(t.get("Barrage", t.get("barrage", 0)))
        ranged_weapon_spec = int(t.get("Ranged Weapon Specialization", t.get("ranged_weapon_spec", 0)))
        trueshot_aura = int(t.get("Trueshot Aura", t.get("trueshot_aura", 0)))
        rapid_killing = int(t.get("Rapid Killing", t.get("rapid_killing", 0)))
        imp_serpent_sting = int(t.get("Improved Serpent Sting", t.get("improved_serpent_sting", 0)))

        # Survival Talents (Turtle / Octo WoW Melee Support)
        imp_slaying = int(t.get("Improved Slaying", t.get("improved_slaying", 0)))
        superior_strikes = int(t.get("Superior Strikes", t.get("superior_strikes", 0)))
        deflection = int(t.get("Deflection", t.get("deflection", 0)))
        savage_strikes = int(t.get("Savage Strikes", t.get("savage_strikes", 0)))
        survivalist = int(t.get("Survivalist", t.get("survivalist", 0)))
        surefooted = int(t.get("Surefooted", t.get("surefooted", 0)))
        killer_instinct = int(t.get("Killer Instinct", t.get("killer_instinct", 0)))
        counterattack_talent = int(t.get("Counterattack", t.get("counterattack", 0)))
        lightning_reflexes = int(t.get("Lightning Reflexes", t.get("lightning_reflexes", 0)))
        clever_traps = int(t.get("Clever Traps", t.get("clever_traps", 0)))

        item_ids = [it if isinstance(it, (int, str)) else it.get("id") for it in equipped_items]
        enchants = kwargs.get("enchants")
        race_clean = str(race).lower().replace("_", "").replace(" ", "").strip()
        quest_weapon_skills = kwargs.get("quest_weapon_skills")
        gear = calculate_gear_totals(
            item_ids,
            self.db,
            enchants=enchants,
            race=race_clean,
            character_class="hunter",
            quest_weapon_skills=quest_weapon_skills
        )

        # Lightning Reflexes (+3/6/9/12/15% Agility)
        base_agi = gear["agility"]
        effective_agi = base_agi * (1.0 + (0.03 * lightning_reflexes))
        gear["agility"] = int(round(effective_agi))

        # Detect weapons
        ranged_weapon = None
        mainhand_weapon = None
        offhand_weapon = None

        for it in gear.get("equipped_items", []):
            slot = it.get("slot")
            if slot == "ranged":
                ranged_weapon = it
            elif slot in ("main_hand", "two_hand"):
                mainhand_weapon = it
            elif slot == "off_hand" and it.get("speed", 0) > 0:
                offhand_weapon = it

        is_dw = mainhand_weapon is not None and offhand_weapon is not None
        has_melee = mainhand_weapon is not None and (mainhand_weapon.get("speed", 0) > 0)
        has_ranged = ranged_weapon is not None and (ranged_weapon.get("speed", 0) > 0)

        # Determine Hunter Spec & Style
        req_spec = str(kwargs.get("hunter_spec", kwargs.get("spec", ""))).lower().strip()
        req_style = str(kwargs.get("combat_style", combat_style)).lower().strip()

        if req_spec in ("marksmanship", "marksman", "mm"):
            active_spec = "marksmanship"
            active_style = "ranged"
        elif req_spec in ("survival", "surv", "sv", "melee"):
            active_spec = "survival"
            active_style = "melee"
        elif req_spec in ("beast_mastery", "beastmastery", "bm", "pet"):
            active_spec = "beast_mastery"
            active_style = "ranged"
        else:
            # Auto-detect from combat_style or talents
            if req_style in ("melee", "survival_melee", "survival"):
                active_spec = "survival"
                active_style = "melee"
            elif superior_strikes > 0 or savage_strikes > 0 or (has_melee and not has_ranged):
                active_spec = "survival"
                active_style = "melee"
            elif unleashed_fury >= 3 or bestial_wrath_talent > 0:
                active_spec = "beast_mastery"
                active_style = "ranged"
            else:
                active_spec = "marksmanship"
                active_style = "ranged"

        # Priority List configuration
        pri_arg = kwargs.get("priority_list", None)
        if pri_arg is not None and isinstance(pri_arg, list):
            active_priority_list = [str(x).strip().lower() for x in pri_arg if str(x).strip()]
        else:
            if active_spec == "survival":
                active_priority_list = ["mongoose_bite", "counterattack", "raptor_strike", "immolation_trap", "wing_clip", "white_melee"]
            elif active_spec == "beast_mastery":
                active_priority_list = ["bestial_wrath", "intimidation", "multi_shot", "arcane_shot", "serpent_sting", "auto_shot", "pet_focus_dump"]
            else:  # marksmanship 1.18 rework
                active_priority_list = ["rapid_fire", "aimed_shot", "multi_shot", "arcane_shot", "serpent_sting", "steady_shot", "auto_shot"]

        # General multipliers
        slaying_mult = 1.0 + (0.01 * imp_slaying)
        effective_target_armor = max(0.0, target_armor - gear.get("arp", 0.0))
        armor_reduction = effective_target_armor / (effective_target_armor + 5500.0) if effective_target_armor > 0 else 0.0

        # Trueshot Aura
        ts_bonus_rap = 100 if (trueshot_aura > 0 or active_spec == "marksmanship") else 0
        ts_bonus_map = 50 if (trueshot_aura > 0 or active_spec == "marksmanship") else 0

        # Attack Power
        rap = gear.get("ranged_attack_power", 0) + gear["attack_power"] + int(effective_agi * 2) + ts_bonus_rap
        map_ap = gear["attack_power"] + gear["strength"] + int(effective_agi * 1) + ts_bonus_map

        # Racial bonuses
        is_orc = race_clean == "orc"
        if is_orc:
            map_ap += int(gear["attack_power"] * 0.25)  # Blood Fury
        is_troll = race_clean == "troll"
        troll_haste = 0.10 if is_troll else 0.0

        # Crit & Hit
        ranged_crit = gear["crit"] + (effective_agi / 53.0) + (1.0 * lethal_shots) + (1.0 * killer_instinct)
        ranged_hit = gear["hit"] + (1.0 * surefooted) + (3.0 if race_clean in ("troll", "dwarf", "highelf") else 0.0)

        melee_crit = gear["crit"] + (effective_agi / 53.0) + (1.0 * killer_instinct)
        melee_hit = gear["hit"] + (1.0 * surefooted)

        own_damage_breakdown = {}
        own_damage_total = 0.0
        ability_casts = {}
        total_melee_swings = 0

        # Fallback weapons if none equipped
        if not mainhand_weapon:
            mainhand_weapon = {"name": "Standard Polearm", "speed": 3.3, "min_damage": 130.0, "max_damage": 195.0, "slot": "two_hand"}
        if not ranged_weapon:
            ranged_weapon = {"name": "Standard Longbow", "speed": 2.8, "min_damage": 85.0, "max_damage": 145.0, "slot": "ranged"}

        # -------------------------------------------------------------
        # 1. MARKSMANSHIP SPEC (Patch 1.18 Rework)
        # -------------------------------------------------------------
        if active_spec == "marksmanship" and fight_duration > 0:
            rw_speed = ranged_weapon.get("speed", 2.8)
            rw_min = ranged_weapon.get("min_damage", 85.0)
            rw_max = ranged_weapon.get("max_damage", 145.0)
            avg_rw_dmg = (rw_min + rw_max) / 2.0

            rw_mult = 1.0 + (0.01 * ranged_weapon_spec)
            ranged_crit_mult = 2.0 + (0.06 * mortal_shots)  # 2.30x crit with Mortal Shots 5/5
            ranged_crit_rate = min(1.0, max(0.0, ranged_crit / 100.0))

            # 1.1 Rapid Fire (1.18 Rework: -40% Aimed/Steady cast time, +40% ranged haste for 15s)
            rf_uptime = 0.0
            if "rapid_fire" in active_priority_list:
                rf_cd = 180.0 if rapid_killing == 0 else 120.0
                rf_casts = 1 + int(max(0.0, fight_duration - 1.0) / rf_cd)
                ability_casts["rapid_fire"] = rf_casts
                total_rf_time = min(fight_duration, rf_casts * 15.0)
                rf_uptime = total_rf_time / fight_duration if fight_duration > 0 else 0.0

            # Dynamic cast times under 1.18 Rapid Fire
            # Base Aimed Shot in 1.18: 2.0s (down from 3.0s). Under RF: 1.2s.
            # Base Steady Shot in 1.18: 1.5s. Under RF: 0.9s.
            aimed_cast_dur = 2.0 * (1.0 - (0.40 * rf_uptime))
            steady_cast_dur = 1.5 * (1.0 - (0.40 * rf_uptime))

            total_ranged_haste = (haste_percent / 100.0) + (quiver_haste / 100.0) + (gear.get("haste", 0.0) / 100.0) + troll_haste + (0.40 * rf_uptime)
            eff_ranged_speed = (rw_speed / (1.0 + total_ranged_haste)) if (1.0 + total_ranged_haste) > 0 else rw_speed

            time_used_by_shots = 0.0

            # 1.2 Aimed Shot (2.0s cast, 6.0s CD, Experimental Ammunition +5% elemental)
            if "aimed_shot" in active_priority_list:
                aimed_cd = 6.0
                aimed_casts = int(round(fight_duration / aimed_cd))
                ability_casts["aimed_shot"] = aimed_casts
                time_used_by_shots += (aimed_casts * aimed_cast_dur)

                # Damage: (Wpn + RAP/14*2.8 + Ammo*2.8 + 600) * 1.05 (Experimental Ammunition)
                raw_aimed = (avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * 2.8) + 600.0) * 1.05
                avg_aimed_hit = raw_aimed * (1.0 - armor_reduction) * slaying_mult * rw_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                aimed_total = aimed_casts * avg_aimed_hit
                own_damage_breakdown["aimed_shot_dps"] = round(aimed_total / fight_duration, 2)
                own_damage_total += aimed_total

            # 1.3 Multi-Shot (10.0s CD, instant 0.5s volley, Barrage +15%)
            if "multi_shot" in active_priority_list:
                multi_cd = 10.0
                multi_casts = int(round(fight_duration / multi_cd))
                ability_casts["multi_shot"] = multi_casts
                time_used_by_shots += (multi_casts * 0.5)

                barrage_mult = 1.0 + (0.05 * barrage)
                raw_multi = avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * 2.8) + 120.0
                avg_multi_hit = raw_multi * (1.0 - armor_reduction) * slaying_mult * rw_mult * barrage_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                multi_total = multi_casts * avg_multi_hit
                own_damage_breakdown["multi_shot_dps"] = round(multi_total / fight_duration, 2)
                own_damage_total += multi_total

            # 1.4 Arcane Shot (1.18 Rework: Independent 6.0s CD, instant magic)
            if "arcane_shot" in active_priority_list:
                arcane_cd = 6.0
                arcane_casts = int(round(fight_duration / arcane_cd))
                ability_casts["arcane_shot"] = arcane_casts
                time_used_by_shots += (arcane_casts * 0.5)

                raw_arcane = 183.0 + (rap * 0.15) + (gear["spell_power"] * 0.15)
                # Arcane magic completely ignores physical boss armor!
                avg_arcane_hit = raw_arcane * slaying_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                arcane_total = arcane_casts * avg_arcane_hit
                own_damage_breakdown["arcane_shot_dps"] = round(arcane_total / fight_duration, 2)
                own_damage_total += arcane_total

            # 1.5 Serpent Sting (Nature DoT, 555 dmg over 15s)
            if "serpent_sting" in active_priority_list:
                serpent_casts = int(round(fight_duration / 15.0))
                ability_casts["serpent_sting"] = max(1, serpent_casts)
                serpent_dps = 37.0 * (1.0 + (0.02 * imp_serpent_sting)) * slaying_mult
                serpent_total = serpent_dps * fight_duration
                own_damage_breakdown["serpent_sting_dps"] = round(serpent_dps, 2)
                own_damage_total += serpent_total

            # 1.6 Steady Shot (1.18 Rework Filler: 1.5s cast, fills windows between Aimed & Multi)
            if "steady_shot" in active_priority_list:
                remaining_time = max(0.0, fight_duration - time_used_by_shots)
                steady_casts = int(round(remaining_time / steady_cast_dur)) if steady_cast_dur > 0 else 0
                ability_casts["steady_shot"] = steady_casts

                # Damage: Weapon dmg + ammo + 150 flat + 15% RAP
                raw_steady = avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * 2.8) + 150.0
                avg_steady_hit = raw_steady * (1.0 - armor_reduction) * slaying_mult * rw_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                steady_total = steady_casts * avg_steady_hit
                own_damage_breakdown["steady_shot_dps"] = round(steady_total / fight_duration, 2)
                own_damage_total += steady_total

            # 1.7 Auto Shot (Woven ranged auto attacks)
            if "auto_shot" in active_priority_list:
                auto_shots_count = fight_duration / eff_ranged_speed if eff_ranged_speed > 0 else 0.0
                ability_casts["auto_shot"] = int(round(auto_shots_count))

                raw_auto_shot = avg_rw_dmg + (rap / 14.0) * rw_speed + (ammo_dps * rw_speed)
                avg_auto_hit = raw_auto_shot * (1.0 - armor_reduction) * slaying_mult * rw_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                auto_shot_damage = auto_shots_count * avg_auto_hit
                own_damage_breakdown["auto_shot_dps"] = round(auto_shot_damage / fight_duration, 2)
                own_damage_total += auto_shot_damage

        # -------------------------------------------------------------
        # 2. SURVIVAL SPEC (Melee & Traps)
        # -------------------------------------------------------------
        elif active_spec == "survival" and fight_duration > 0:
            mh_speed = mainhand_weapon.get("speed", 3.0)
            mh_min = mainhand_weapon.get("min_damage", 110.0)
            mh_max = mainhand_weapon.get("max_damage", 180.0)
            mh_avg = (mh_min + mh_max) / 2.0

            melee_haste = (haste_percent / 100.0) + (gear.get("haste", 0.0) / 100.0) + troll_haste
            eff_mh_speed = (mh_speed / (1.0 + melee_haste)) if (1.0 + melee_haste) > 0 else mh_speed
            mh_swings = fight_duration / eff_mh_speed if eff_mh_speed > 0 else 0.0

            crit_mult = 2.0
            crit_rate = min(1.0, max(0.0, melee_crit / 100.0))
            hit_rate = min(1.0, max(0.0, (100.0 - max(0.0, (8.0 - melee_hit))) / 100.0))

            # 2.1 Mongoose Bite (5.0s - 0.2s * Superior Strikes, 4.0s with 5/5, Savage Strikes +20% Crit)
            if "mongoose_bite" in active_priority_list:
                mongoose_cd = max(2.5, 5.0 - (0.2 * superior_strikes))
                # Dodge (~15%) + Deflection Parry (5%) -> reliable procs
                mongoose_count = (fight_duration / mongoose_cd) * 0.90
                ability_casts["mongoose_bite"] = int(round(mongoose_count))

                mongoose_raw_hit = 115.0 + (map_ap / 14.0) * 1.5
                mongoose_crit_rate = min(1.0, max(0.0, (melee_crit / 100.0) + (0.10 * savage_strikes)))
                avg_mongoose = mongoose_raw_hit * (1.0 - armor_reduction) * slaying_mult * (1.0 + mongoose_crit_rate)
                mongoose_damage = mongoose_count * avg_mongoose
                own_damage_breakdown["mongoose_bite_dps"] = round(mongoose_damage / fight_duration, 2)
                own_damage_total += mongoose_damage

            # 2.2 Counterattack (5.0s CD, triggered on Parry)
            if "counterattack" in active_priority_list:
                ca_count = (fight_duration / 5.0) * min(1.0, 0.05 + (0.01 * deflection))
                ability_casts["counterattack"] = int(round(ca_count))

                ca_raw = 110.0 + (map_ap / 14.0) * 1.5
                avg_ca = ca_raw * (1.0 - armor_reduction) * slaying_mult * (1.0 + crit_rate)
                ca_damage = ca_count * avg_ca
                own_damage_breakdown["counterattack_dps"] = round(ca_damage / fight_duration, 2)
                own_damage_total += ca_damage

            # 2.3 Raptor Strike (6.0s - 0.2s * Superior Strikes, 5.0s with 5/5, Savage Strikes +20% Crit)
            if "raptor_strike" in active_priority_list:
                raptor_cd = max(3.0, 6.0 - (0.2 * superior_strikes))
                raptor_count = fight_duration / raptor_cd
                ability_casts["raptor_strike"] = int(round(raptor_count))

                raptor_bonus_dmg = 140.0
                raptor_raw_hit = mh_avg + (map_ap / 14.0) * mh_speed + raptor_bonus_dmg
                raptor_crit_rate = min(1.0, max(0.0, (melee_crit / 100.0) + (0.10 * savage_strikes)))
                avg_raptor = raptor_raw_hit * (1.0 - armor_reduction) * slaying_mult * (1.0 + raptor_crit_rate)
                raptor_damage = raptor_count * avg_raptor
                own_damage_breakdown["raptor_strike_dps"] = round(raptor_damage / fight_duration, 2)
                own_damage_total += raptor_damage

            # 2.4 Immolation Trap (Clever Traps, Fire DoT)
            if "immolation_trap" in active_priority_list:
                immolation_dps = 90.0 * (1.0 + 0.15 * clever_traps) * slaying_mult
                immolation_damage = immolation_dps * (fight_duration * 0.75)  # 75% uptime
                ability_casts["immolation_trap"] = int(round(fight_duration / 20.0))
                own_damage_breakdown["immolation_trap_dps"] = round(immolation_damage / fight_duration, 2)
                own_damage_total += immolation_damage

            # 2.5 Wing Clip (Instant melee hit filler)
            if "wing_clip" in active_priority_list:
                wc_count = fight_duration / 3.0
                ability_casts["wing_clip"] = int(round(wc_count))
                wc_raw = 50.0 + (map_ap / 14.0) * 1.0
                avg_wc = wc_raw * (1.0 - armor_reduction) * slaying_mult * (1.0 + crit_rate)
                wc_damage = wc_count * avg_wc
                own_damage_breakdown["wing_clip_dps"] = round(wc_damage / fight_duration, 2)
                own_damage_total += wc_damage

            # 2.6 White Melee Swings (MH & OH Dual Wield)
            if "white_melee" in active_priority_list:
                raw_mh_hit = mh_avg + (map_ap / 14.0) * mh_speed
                avg_mh_white = raw_mh_hit * (1.0 - armor_reduction) * slaying_mult * (hit_rate + (crit_mult - 1.0) * crit_rate)
                mh_white_damage = mh_swings * avg_mh_white
                own_damage_breakdown["white_melee_dps"] = round(mh_white_damage / fight_duration, 2)
                own_damage_total += mh_white_damage
                total_melee_swings += int(round(mh_swings))

                # Dual Wield Off-Hand
                if is_dw:
                    oh_speed = offhand_weapon.get("speed", 1.8)
                    oh_min = offhand_weapon.get("min_damage", 50.0)
                    oh_max = offhand_weapon.get("max_damage", 100.0)
                    oh_avg = (oh_min + oh_max) / 2.0
                    eff_oh_speed = oh_speed / (1.0 + melee_haste) if (1.0 + melee_haste) > 0 else oh_speed
                    oh_swings = fight_duration / eff_oh_speed if eff_oh_speed > 0 else 0.0

                    raw_oh_hit = (oh_avg + (map_ap / 14.0) * oh_speed) * 0.5  # 50% OH penalty
                    dw_hit_rate = min(1.0, max(0.0, (100.0 - max(0.0, (27.0 - melee_hit))) / 100.0))
                    avg_oh_white = raw_oh_hit * (1.0 - armor_reduction) * slaying_mult * (dw_hit_rate + (crit_mult - 1.0) * crit_rate)
                    oh_white_damage = oh_swings * avg_oh_white
                    own_damage_breakdown["offhand_white_dps"] = round(oh_white_damage / fight_duration, 2)
                    own_damage_total += oh_white_damage
                    total_melee_swings += int(round(oh_swings))

        # -------------------------------------------------------------
        # 3. BEAST MASTERY SPEC (Pet Synergy & Ranged Support)
        # -------------------------------------------------------------
        elif active_spec == "beast_mastery" and fight_duration > 0:
            rw_speed = ranged_weapon.get("speed", 2.8)
            rw_min = ranged_weapon.get("min_damage", 85.0)
            rw_max = ranged_weapon.get("max_damage", 145.0)
            avg_rw_dmg = (rw_min + rw_max) / 2.0

            ranged_crit_mult = 2.0 + (0.06 * mortal_shots)
            ranged_crit_rate = min(1.0, max(0.0, ranged_crit / 100.0))

            total_ranged_haste = (haste_percent / 100.0) + (quiver_haste / 100.0) + (gear.get("haste", 0.0) / 100.0) + troll_haste
            eff_ranged_speed = (rw_speed / (1.0 + total_ranged_haste)) if (1.0 + total_ranged_haste) > 0 else rw_speed

            # 3.1 Bestial Wrath (120s CD, 18s duration: +20% pet damage)
            bw_active_ratio = 0.0
            if "bestial_wrath" in active_priority_list and (bestial_wrath_talent > 0 or True):
                bw_casts = 1 + int(max(0.0, fight_duration - 1.0) / 120.0)
                ability_casts["bestial_wrath"] = bw_casts
                bw_active_ratio = min(fight_duration, bw_casts * 18.0) / fight_duration

            # 3.2 Intimidation (60s CD)
            if "intimidation" in active_priority_list:
                intim_casts = int(round(fight_duration / 60.0))
                ability_casts["intimidation"] = max(1, intim_casts)

            # 3.3 Multi-Shot
            if "multi_shot" in active_priority_list:
                multi_casts = int(round(fight_duration / 10.0))
                ability_casts["multi_shot"] = multi_casts
                raw_multi = avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * 2.8) + 120.0
                avg_multi_hit = raw_multi * (1.0 - armor_reduction) * slaying_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                multi_total = multi_casts * avg_multi_hit
                own_damage_breakdown["multi_shot_dps"] = round(multi_total / fight_duration, 2)
                own_damage_total += multi_total

            # 3.4 Arcane Shot
            if "arcane_shot" in active_priority_list:
                arcane_casts = int(round(fight_duration / 6.0))
                ability_casts["arcane_shot"] = arcane_casts
                raw_arcane = 183.0 + (rap * 0.15) + (gear["spell_power"] * 0.15)
                avg_arcane_hit = raw_arcane * slaying_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                arcane_total = arcane_casts * avg_arcane_hit
                own_damage_breakdown["arcane_shot_dps"] = round(arcane_total / fight_duration, 2)
                own_damage_total += arcane_total

            # 3.5 Serpent Sting
            if "serpent_sting" in active_priority_list:
                serpent_casts = int(round(fight_duration / 15.0))
                ability_casts["serpent_sting"] = max(1, serpent_casts)
                serpent_dps = 37.0 * (1.0 + (0.02 * imp_serpent_sting)) * slaying_mult
                serpent_total = serpent_dps * fight_duration
                own_damage_breakdown["serpent_sting_dps"] = round(serpent_dps, 2)
                own_damage_total += serpent_total

            # 3.6 Auto Shot
            if "auto_shot" in active_priority_list:
                auto_shots_count = fight_duration / eff_ranged_speed if eff_ranged_speed > 0 else 0.0
                ability_casts["auto_shot"] = int(round(auto_shots_count))
                raw_auto_shot = avg_rw_dmg + (rap / 14.0) * rw_speed + (ammo_dps * rw_speed)
                avg_auto_hit = raw_auto_shot * (1.0 - armor_reduction) * slaying_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                auto_shot_damage = auto_shots_count * avg_auto_hit
                own_damage_breakdown["auto_shot_dps"] = round(auto_shot_damage / fight_duration, 2)
                own_damage_total += auto_shot_damage

        own_dps = own_damage_total / fight_duration if fight_duration > 0 else 0.0

        # -------------------------------------------------------------
        # PET SYSTEM & PET SKILLS
        # -------------------------------------------------------------
        pet_dps = 0.0
        pet_damage_total = 0.0
        minion_damage_breakdown = {}
        chosen_pet = str(kwargs.get("pet_family", pet_family)).lower().strip()
        if chosen_pet not in ("cat", "wind_serpent", "wolf", "raptor", "owl_bat", "boar"):
            chosen_pet = "cat"

        family_cfg = {
            "cat": {"name": "Cat (Kot)", "dmg_mod": 1.10, "base_speed": 1.2, "skills": ["Claw", "Bite"]},
            "wind_serpent": {"name": "Wind Serpent (Wąż Wiatru)", "dmg_mod": 1.07, "base_speed": 2.0, "skills": ["Lightning Breath", "Bite"]},
            "wolf": {"name": "Wolf (Wilk)", "dmg_mod": 1.00, "base_speed": 1.5, "skills": ["Furious Howl", "Bite"]},
            "raptor": {"name": "Raptor", "dmg_mod": 1.10, "base_speed": 2.0, "skills": ["Claw", "Bite"]},
            "owl_bat": {"name": "Owl / Bat (Sowa)", "dmg_mod": 1.07, "base_speed": 2.0, "skills": ["Screech", "Claw"]},
            "boar": {"name": "Boar (Dzik)", "dmg_mod": 0.90, "base_speed": 2.0, "skills": ["Charge", "Bite"]},
        }
        pet_info = family_cfg.get(chosen_pet, family_cfg["cat"])

        if pet_active and fight_duration > 0:
            pet_dmg_mult = pet_info["dmg_mod"]
            pet_dmg_mult *= (1.0 + (0.03 * unleashed_fury))  # Unleashed Fury: +3/6/9/12/15%
            if is_orc:
                pet_dmg_mult *= 1.05  # Orc Command racial: +5% pet damage

            # Bestial Wrath multiplier
            if active_spec == "beast_mastery" and "bestial_wrath" in active_priority_list:
                pet_dmg_mult *= (1.0 + (0.20 * bw_active_ratio))
            elif bestial_wrath_talent > 0:
                pet_dmg_mult *= 1.03

            pet_base_crit = 0.05 + (0.03 * ferocity)  # Ferocity: +3/6/9/12/15% crit
            pet_crit_mult = 2.0

            # Frenzy (+30% attack speed on crit)
            frenzy_uptime = min(1.0, pet_base_crit * (frenzy / 5.0) * (8.0 / pet_info["base_speed"])) if frenzy > 0 else 0.0
            eff_pet_speed = pet_info["base_speed"] / (1.0 + (0.30 * frenzy_uptime))

            pet_ap = 300.0 + (rap * 0.22)
            pet_swings = fight_duration / eff_pet_speed

            # 1. Pet White Melee Swings
            raw_pet_swing = (pet_ap / 14.0) * pet_info["base_speed"]
            avg_pet_white = raw_pet_swing * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
            pet_white_total = pet_swings * avg_pet_white
            minion_damage_breakdown["pet_melee_dps"] = round(pet_white_total / fight_duration, 2)
            pet_damage_total += pet_white_total
            ability_casts["pet_swings"] = int(round(pet_swings))

            # 2. Pet Focus Abilities
            focus_allowed = (active_spec != "beast_mastery") or ("pet_focus_dump" in active_priority_list)
            if focus_allowed:
                focus_regen = 25.0 * (1.0 + (0.50 * bestial_discipline))
                total_focus = focus_regen * fight_duration

                if chosen_pet == "wind_serpent":
                    # Lightning Breath: 50 focus, ignores armor!
                    lb_cost = 50.0
                    lb_count = total_focus / lb_cost
                    raw_lb = 106.0 + (pet_ap * 0.15)
                    avg_lb = raw_lb * pet_dmg_mult * (1.0 + pet_base_crit)
                    lb_total = lb_count * avg_lb
                    minion_damage_breakdown["pet_lightning_breath_dps"] = round(lb_total / fight_duration, 2)
                    pet_damage_total += lb_total
                    ability_casts["pet_lightning_breath"] = int(round(lb_count))

                elif chosen_pet == "wolf":
                    # Furious Howl: +51 damage to hunter attacks
                    howl_count = fight_duration / 10.0
                    howl_dps_gain = (howl_count * 51.0 * (1.0 - armor_reduction)) / fight_duration
                    minion_damage_breakdown["furious_howl_bonus_dps"] = round(howl_dps_gain, 2)
                    pet_damage_total += (howl_count * 51.0 * (1.0 - armor_reduction))
                    ability_casts["furious_howl"] = int(round(howl_count))

                    rem_focus = max(0.0, total_focus - (howl_count * 60.0))
                    bite_count = min(fight_duration / 10.0, rem_focus / 35.0)
                    raw_bite = 90.0 + (pet_ap * 0.10)
                    avg_bite = raw_bite * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                    bite_total = bite_count * avg_bite
                    minion_damage_breakdown["pet_bite_dps"] = round(bite_total / fight_duration, 2)
                    pet_damage_total += bite_total
                    ability_casts["pet_bites"] = int(round(bite_count))

                else:
                    bite_count = fight_duration / 10.0
                    raw_bite = 90.0 + (pet_ap * 0.10)
                    avg_bite = raw_bite * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                    bite_total = bite_count * avg_bite
                    minion_damage_breakdown["pet_bite_dps"] = round(bite_total / fight_duration, 2)
                    pet_damage_total += bite_total
                    ability_casts["pet_bites"] = int(round(bite_count))

                    rem_focus = max(0.0, total_focus - (bite_count * 35.0))
                    if "Screech" in pet_info["skills"]:
                        screech_count = rem_focus / 20.0
                        raw_screech = 36.0 + (pet_ap * 0.05)
                        avg_screech = raw_screech * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                        screech_total = screech_count * avg_screech
                        minion_damage_breakdown["pet_screech_dps"] = round(screech_total / fight_duration, 2)
                        pet_damage_total += screech_total
                        ability_casts["pet_screech"] = int(round(screech_count))
                    else:
                        claw_count = rem_focus / 25.0
                        raw_claw = 51.0 + (pet_ap * 0.08)
                        avg_claw = raw_claw * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                        claw_total = claw_count * avg_claw
                        minion_damage_breakdown["pet_claw_dps"] = round(claw_total / fight_duration, 2)
                        pet_damage_total += claw_total
                        ability_casts["pet_claws"] = int(round(claw_count))

            pet_dps = pet_damage_total / fight_duration

        total_dps = own_dps + pet_dps
        total_damage = own_damage_total + pet_damage_total

        primary_weapon = mainhand_weapon if (active_style == "melee" and mainhand_weapon) else (ranged_weapon or mainhand_weapon)
        prim_name = primary_weapon.get("name", "Standard Weapon") if primary_weapon else "Default Weapon"
        prim_speed = primary_weapon.get("speed", 2.8) if primary_weapon else 2.8

        # Build detailed damage sources for breakdown table
        damage_sources = []
        safe_total = max(0.001, total_dps)

        source_defs = [
            ("white_melee_dps", "Main Hand Auto Attack", "White Melee", "#e0e0e0", "white_melee"),
            ("offhand_white_dps", "Off Hand Auto Attack", "White Melee", "#b0b0b0", "white_melee"),
            ("raptor_strike_dps", "Raptor Strike", "Survival Melee", "#c9a227", "raptor_strike"),
            ("mongoose_bite_dps", "Mongoose Bite", "Survival Melee", "#40c7eb", "mongoose_bite"),
            ("counterattack_dps", "Counterattack", "Survival Melee", "#55c07b", "counterattack"),
            ("immolation_trap_dps", "Immolation Trap", "Trap / Fire", "#ff5533", "immolation_trap"),
            ("wing_clip_dps", "Wing Clip", "Survival Melee", "#a38249", "wing_clip"),
            ("auto_shot_dps", "Auto Shot", "Ranged White", "#ffffff", "auto_shot"),
            ("aimed_shot_dps", "Aimed Shot (1.18)", "Ranged Skill", "#e268a8", "aimed_shot"),
            ("steady_shot_dps", "Steady Shot (1.18)", "Ranged Filler", "#38bdf8", "steady_shot"),
            ("multi_shot_dps", "Multi-Shot", "Ranged Skill", "#f0a04b", "multi_shot"),
            ("arcane_shot_dps", "Arcane Shot", "Arcane Magic", "#818cf8", "arcane_shot"),
            ("serpent_sting_dps", "Serpent Sting", "Nature DoT", "#44d67c", "serpent_sting"),
        ]

        for item_def in source_defs:
            key, name, cat, col, sp_key = item_def
            val = own_damage_breakdown.get(key, 0.0)
            if val > 0.001:
                damage_sources.append({
                    "id": key,
                    "name": name,
                    "category": cat,
                    "color": col,
                    "dps": round(val, 2),
                    "damage": round(val * fight_duration, 1),
                    "percent": round((val / safe_total) * 100.0, 1),
                    "spell_key": sp_key,
                    "is_minion": False,
                    "is_proc": False,
                })

        if pet_active:
            pet_source_defs = [
                ("pet_melee_dps", f"Pet {pet_info['name']} Auto Attack", "Pet Melee", "#e6cc80"),
                ("pet_claw_dps", f"Pet Claw ({pet_info['name']})", "Pet Skill", "#ffaa00"),
                ("pet_bite_dps", f"Pet Bite ({pet_info['name']})", "Pet Skill", "#d9534f"),
                ("pet_lightning_breath_dps", "Pet Lightning Breath (Nature)", "Pet Nature", "#33ccff"),
                ("pet_screech_dps", "Pet Screech", "Pet Skill", "#c084fc"),
                ("furious_howl_bonus_dps", "Furious Howl (Hunter Bonus)", "Pet Buff", "#f59e0b"),
            ]
            for key, name, cat, col in pet_source_defs:
                val = minion_damage_breakdown.get(key, 0.0)
                if val > 0.001:
                    damage_sources.append({
                        "id": key,
                        "name": name,
                        "category": cat,
                        "color": col,
                        "dps": round(val, 2),
                        "damage": round(val * fight_duration, 1),
                        "percent": round((val / safe_total) * 100.0, 1),
                        "is_minion": True,
                        "is_proc": False,
                    })

        magic_dps = (
            own_damage_breakdown.get("immolation_trap_dps", 0.0)
            + own_damage_breakdown.get("serpent_sting_dps", 0.0)
            + own_damage_breakdown.get("arcane_shot_dps", 0.0)
            + minion_damage_breakdown.get("pet_lightning_breath_dps", 0.0)
        )
        phys_dps = max(0.0, total_dps - magic_dps)

        damage_type_breakdown = {
            "physical_dps": round(phys_dps, 2),
            "physical_percent": round((phys_dps / safe_total) * 100.0, 1),
            "holy_spell_dps": round(magic_dps, 2),
            "holy_spell_percent": round((magic_dps / safe_total) * 100.0, 1),
            "minion_shadow_dps": round(pet_dps, 2),
            "minion_shadow_percent": round((pet_dps / safe_total) * 100.0, 1),
        }

        spec_names = {
            "marksmanship": "Marksmanship (1.18 Rework)",
            "survival": "Survival Melee",
            "beast_mastery": "Beast Mastery"
        }

        eff_ws = gear.get("effective_weapon_skill", 300)
        ws_hit = gear.get("weapon_skill_hit_bonus", 0.0)
        glance_fac = gear.get("glance_damage_factor", 0.65)

        return {
            "character_class": "hunter",
            "hunter_spec": active_spec,
            "hunter_spec_name": spec_names.get(active_spec, active_spec.capitalize()),
            "combat_style": active_style,
            "combat_style_name": spec_names.get(active_spec, active_spec.capitalize()),
            "priority_list": active_priority_list,
            "fight_duration": fight_duration,
            "weapon_name": prim_name,
            "base_weapon_speed": prim_speed,
            "effective_weapon_speed": round(eff_ranged_speed if active_style == "ranged" else eff_mh_speed, 2),
            "exact_melee_swings": total_melee_swings if active_style == "melee" else int(round(fight_duration / eff_ranged_speed)),
            "total_attack_power": map_ap if active_style == "melee" else rap,
            "melee_attack_power": map_ap,
            "ranged_attack_power": rap,
            "total_spell_power": gear["spell_power"],
            "healing_power": gear["healing"],
            "total_crit_percent": round(melee_crit if active_style == "melee" else ranged_crit, 2),
            "melee_crit_percent": round(melee_crit, 2),
            "ranged_crit_percent": round(ranged_crit, 2),
            "total_hit_percent": round(melee_hit if active_style == "melee" else ranged_hit, 2),
            "effective_weapon_skill": eff_ws,
            "weapon_skill": eff_ws,
            "weapon_skill_hit_bonus": ws_hit,
            "glance_damage_factor": glance_fac,
            "equipped_weapon_skills": gear.get("equipped_weapon_skills", []),
            "total_magic_hits": int(round(magic_dps > 0 and (fight_duration / 2.0) or 0)),
            "magic_hits_per_second": round(magic_dps / 100.0, 2),
            "procs_per_second": 0.0,
            "has_minions": bool(pet_active and pet_dps > 0),
            "expected_active_minions": 1.0 if pet_active else 0.0,
            "damage_sources": damage_sources,
            "damage_type_breakdown": damage_type_breakdown,
            "ability_casts": ability_casts,
            "own_damage_breakdown": own_damage_breakdown,
            "own_dps": round(own_dps, 2),
            "own_damage_total": round(own_damage_total, 2),
            "minion_dps": round(pet_dps, 2),
            "minion_dps_min": round(pet_dps * 0.95, 2),
            "minion_dps_max": round(pet_dps * 1.05, 2),
            "minion_damage_total": round(pet_damage_total, 2),
            "minion_damage_breakdown": minion_damage_breakdown,
            "pet_details": {
                "family": chosen_pet,
                "name": pet_info["name"],
                "active": pet_active,
                "skills": pet_info["skills"],
                "dmg_modifier_percent": int(round((pet_info["dmg_mod"] - 1.0) * 100)),
            },
            "total_dps": round(total_dps, 2),
            "total_damage": round(total_damage, 2),
            "gear_summary": {
                "raw_attack_power": gear["attack_power"],
                "ranged_attack_power": rap,
                "melee_attack_power": map_ap,
                "strength": gear["strength"],
                "agility": gear["agility"],
                "stamina": gear["stamina"],
                "intellect": gear["intellect"],
                "armor": gear["armor"],
                "effective_weapon_skill": eff_ws,
                "weapon_skill_hit_bonus": ws_hit,
                "glance_damage_factor": glance_fac,
                "equipped_count": len(gear["equipped_items"]),
            },
        }
