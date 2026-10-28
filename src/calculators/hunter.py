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
        bestial_wrath = int(t.get("Bestial Wrath", t.get("bestial_wrath", 0)))

        # Marksmanship Talents
        lethal_shots = int(t.get("Lethal Shots", t.get("lethal_shots", 0)))
        mortal_shots = int(t.get("Mortal Shots", t.get("mortal_shots", 0)))
        aimed_shot_talent = int(t.get("Aimed Shot", t.get("aimed_shot", 0)))
        barrage = int(t.get("Barrage", t.get("barrage", 0)))
        ranged_weapon_spec = int(t.get("Ranged Weapon Specialization", t.get("ranged_weapon_spec", 0)))
        trueshot_aura = int(t.get("Trueshot Aura", t.get("trueshot_aura", 0)))

        # Survival Talents (Octo / Turtle WoW Custom Melee Support)
        imp_slaying = int(t.get("Improved Slaying", t.get("improved_slaying", 0)))
        superior_strikes = int(t.get("Superior Strikes", t.get("superior_strikes", 0)))
        deflection = int(t.get("Deflection", t.get("deflection", 0)))
        savage_strikes = int(t.get("Savage Strikes", t.get("savage_strikes", 0)))
        survivalist = int(t.get("Survivalist", t.get("survivalist", 0)))
        surefooted = int(t.get("Surefooted", t.get("surefooted", 0)))
        killer_instinct = int(t.get("Killer Instinct", t.get("killer_instinct", 0)))
        counterattack_talent = int(t.get("Counterattack", t.get("counterattack", 0)))
        lightning_reflexes = int(t.get("Lightning Reflexes", t.get("lightning_reflexes", 0)))

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

        # Determine combat style
        req_style = str(kwargs.get("combat_style", combat_style)).lower().strip()
        if req_style in ("melee", "survival_melee", "survival"):
            active_style = "melee"
        elif req_style in ("ranged", "marksman"):
            active_style = "ranged"
        elif req_style == "hybrid":
            active_style = "hybrid"
        else:  # "auto"
            if has_melee and (superior_strikes > 0 or savage_strikes > 0 or not has_ranged):
                active_style = "melee"
            elif has_ranged:
                active_style = "ranged"
            else:
                active_style = "melee" if has_melee else "ranged"

        # General multipliers
        slaying_mult = 1.0 + (0.01 * imp_slaying)
        effective_target_armor = max(0.0, target_armor - gear.get("arp", 0.0))
        armor_reduction = effective_target_armor / (effective_target_armor + 5500.0) if effective_target_armor > 0 else 0.0

        # Trueshot Aura
        ts_bonus_rap = 100 if trueshot_aura > 0 else 0
        ts_bonus_map = 50 if trueshot_aura > 0 else 0

        # Stats
        rap = gear.get("ranged_attack_power", 0) + gear["attack_power"] + int(effective_agi * 2) + ts_bonus_rap
        map_ap = gear["attack_power"] + gear["strength"] + int(effective_agi * 1) + ts_bonus_map

        # Racial bonuses
        is_orc = race_clean == "orc"
        if is_orc:
            map_ap += int(gear["attack_power"] * 0.25)  # Blood Fury
        is_troll = race_clean == "troll"
        troll_haste = 0.10 if is_troll else 0.0

        ranged_crit = gear["crit"] + (effective_agi / 53.0) + (1.0 * lethal_shots) + (1.0 * killer_instinct)
        ranged_hit = gear["hit"] + (1.0 * surefooted) + (3.0 if race_clean in ("troll", "dwarf", "highelf") else 0.0)

        melee_crit = gear["crit"] + (effective_agi / 53.0) + (1.0 * killer_instinct)
        melee_hit = gear["hit"] + (1.0 * surefooted)

        own_damage_breakdown = {}
        own_damage_total = 0.0

        # -------------------------------------------------------------
        # MELEE COMBAT (Survival Spec)
        # -------------------------------------------------------------
        total_melee_swings = 0
        if active_style in ("melee", "hybrid") and has_melee and fight_duration > 0:
            mh_speed = mainhand_weapon.get("speed", 2.6)
            mh_min = mainhand_weapon.get("min_damage", 80.0)
            mh_max = mainhand_weapon.get("max_damage", 150.0)
            mh_avg = (mh_min + mh_max) / 2.0

            melee_haste = (haste_percent / 100.0) + (gear.get("haste", 0.0) / 100.0) + troll_haste
            eff_mh_speed = (mh_speed / (1.0 + melee_haste)) if (1.0 + melee_haste) > 0 else mh_speed
            mh_swings = fight_duration / eff_mh_speed if eff_mh_speed > 0 else 0.0

            # 1. White Melee Swings
            raw_mh_hit = mh_avg + (map_ap / 14.0) * mh_speed
            crit_mult = 2.0
            crit_rate = min(1.0, max(0.0, melee_crit / 100.0))
            hit_rate = min(1.0, max(0.0, (100.0 - max(0.0, (8.0 - melee_hit))) / 100.0))
            avg_mh_white = raw_mh_hit * (1.0 - armor_reduction) * slaying_mult * (hit_rate + (crit_mult - 1.0) * crit_rate)
            mh_white_damage = mh_swings * avg_mh_white
            own_damage_breakdown["white_melee_dps"] = round(mh_white_damage / fight_duration, 2)
            own_damage_total += mh_white_damage
            total_melee_swings += int(round(mh_swings))

            # Dual Wield OH
            if is_dw:
                oh_speed = offhand_weapon.get("speed", 1.8)
                oh_min = offhand_weapon.get("min_damage", 50.0)
                oh_max = offhand_weapon.get("max_damage", 100.0)
                oh_avg = (oh_min + oh_max) / 2.0
                eff_oh_speed = oh_speed / (1.0 + melee_haste)
                oh_swings = fight_duration / eff_oh_speed if eff_oh_speed > 0 else 0.0
                raw_oh_hit = (oh_avg + (map_ap / 14.0) * oh_speed) * 0.5  # 50% OH penalty
                dw_hit_rate = min(1.0, max(0.0, (100.0 - max(0.0, (27.0 - melee_hit))) / 100.0))
                avg_oh_white = raw_oh_hit * (1.0 - armor_reduction) * slaying_mult * (dw_hit_rate + (crit_mult - 1.0) * crit_rate)
                oh_white_damage = oh_swings * avg_oh_white
                own_damage_breakdown["offhand_white_dps"] = round(oh_white_damage / fight_duration, 2)
                own_damage_total += oh_white_damage
                total_melee_swings += int(round(oh_swings))

            # 2. Raptor Strike (CD: 6.0s - 0.2s * superior_strikes, with 5/5 -> 5.0s)
            raptor_cd = max(3.0, 6.0 - (0.2 * superior_strikes))
            raptor_count = fight_duration / raptor_cd
            raptor_bonus_dmg = 140.0
            raptor_raw_hit = mh_avg + (map_ap / 14.0) * mh_speed + raptor_bonus_dmg
            raptor_crit_rate = min(1.0, max(0.0, (melee_crit / 100.0) + (0.10 * savage_strikes)))
            avg_raptor = raptor_raw_hit * (1.0 - armor_reduction) * slaying_mult * (1.0 + raptor_crit_rate)
            raptor_damage = raptor_count * avg_raptor
            own_damage_breakdown["raptor_strike_dps"] = round(raptor_damage / fight_duration, 2)
            own_damage_total += raptor_damage

            # 3. Mongoose Bite (CD: 5.0s - 0.2s * superior_strikes, with 5/5 -> 4.0s, triggers after dodge/parry)
            mongoose_cd = max(2.5, 5.0 - (0.2 * superior_strikes))
            # Deflection grants +5% parry, base dodge ~10-15%, making Mongoose Bite proc reliably on CD
            mongoose_count = (fight_duration / mongoose_cd) * 0.90
            mongoose_raw_hit = 115.0 + (map_ap / 14.0) * 1.5
            mongoose_crit_rate = min(1.0, max(0.0, (melee_crit / 100.0) + (0.10 * savage_strikes)))
            avg_mongoose = mongoose_raw_hit * (1.0 - armor_reduction) * slaying_mult * (1.0 + mongoose_crit_rate)
            mongoose_damage = mongoose_count * avg_mongoose
            own_damage_breakdown["mongoose_bite_dps"] = round(mongoose_damage / fight_duration, 2)
            own_damage_total += mongoose_damage

            # 4. Counterattack (if talented, triggered on parry, 5s CD)
            if counterattack_talent > 0:
                ca_count = (fight_duration / 5.0) * min(1.0, 0.05 + (0.01 * deflection))
                ca_raw = 110.0 + (map_ap / 14.0) * 1.5
                avg_ca = ca_raw * (1.0 - armor_reduction) * slaying_mult * (1.0 + crit_rate)
                ca_damage = ca_count * avg_ca
                own_damage_breakdown["counterattack_dps"] = round(ca_damage / fight_duration, 2)
                own_damage_total += ca_damage

            # 5. Immolation Trap (clever traps)
            immolation_dps = 90.0 * (1.0 + 0.15 * int(t.get("Clever Traps", 0)))
            immolation_damage = immolation_dps * (fight_duration * 0.5)  # 50% uptime
            own_damage_breakdown["immolation_trap_dps"] = round(immolation_damage / fight_duration, 2)
            own_damage_total += immolation_damage

        # -------------------------------------------------------------
        # RANGED COMBAT (Marksmanship & Auto Shot)
        # -------------------------------------------------------------
        if active_style in ("ranged", "hybrid") and has_ranged and fight_duration > 0:
            base_speed = ranged_weapon.get("speed", 2.8)
            min_dmg = ranged_weapon.get("min_damage", 75.0)
            max_dmg = ranged_weapon.get("max_damage", 140.0)
            avg_ranged_dmg = (min_dmg + max_dmg) / 2.0

            total_ranged_haste = haste_percent + quiver_haste + gear.get("haste", 0.0) + (troll_haste * 100.0)
            eff_ranged_speed = base_speed / (1.0 + (total_ranged_haste / 100.0))
            shots_count = (fight_duration / eff_ranged_speed) if eff_ranged_speed > 0 else 0.0

            rw_mult = 1.0 + (0.01 * ranged_weapon_spec)
            ranged_crit_mult = 2.0 + (0.06 * mortal_shots)
            ranged_crit_rate = min(1.0, max(0.0, ranged_crit / 100.0))

            # Auto Shot
            raw_auto_shot = avg_ranged_dmg + (rap / 14.0) * base_speed + (ammo_dps * base_speed)
            avg_auto_hit = raw_auto_shot * (1.0 - armor_reduction) * slaying_mult * rw_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
            auto_shot_damage = shots_count * avg_auto_hit
            own_damage_breakdown["auto_shot_dps"] = round(auto_shot_damage / fight_duration, 2)
            own_damage_total += auto_shot_damage

            # Aimed Shot (if talented or standard)
            if aimed_shot_talent > 0:
                aimed_cooldown = 6.0
                aimed_count = fight_duration / aimed_cooldown
                raw_aimed = avg_ranged_dmg + (rap / 14.0) * 2.8 + (ammo_dps * 2.8) + 600.0
                avg_aimed_hit = raw_aimed * (1.0 - armor_reduction) * slaying_mult * rw_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                aimed_damage = aimed_count * avg_aimed_hit
                own_damage_breakdown["aimed_shot_dps"] = round(aimed_damage / fight_duration, 2)
                own_damage_total += aimed_damage

            # Multi-Shot
            multi_cooldown = 10.0
            multi_count = fight_duration / multi_cooldown
            barrage_mult = 1.0 + (0.05 * barrage)
            raw_multi = avg_ranged_dmg + (rap / 14.0) * 2.8 + (ammo_dps * 2.8) + 120.0
            avg_multi_hit = raw_multi * (1.0 - armor_reduction) * slaying_mult * rw_mult * barrage_mult * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
            multi_damage = multi_count * avg_multi_hit
            own_damage_breakdown["multi_shot_dps"] = round(multi_damage / fight_duration, 2)
            own_damage_total += multi_damage

            # Serpent Sting
            serpent_dps = 37.0 * (1.0 + 0.02 * int(t.get("Improved Serpent Sting", 0)))
            serpent_damage = serpent_dps * fight_duration
            own_damage_breakdown["serpent_sting_dps"] = round(serpent_dps, 2)
            own_damage_total += serpent_damage

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

        # Pet family characteristics
        # Cat: +10% dmg, 1.2s speed, Claw + Bite
        # Wind Serpent: +7% dmg, 2.0s speed, Lightning Breath (Nature spell, ignores armor!) + Bite
        # Wolf: 1.5s speed, Furious Howl (+51 physical dmg to hunter attacks) + Bite
        # Raptor: +10% dmg, 2.0s speed, Claw + Bite
        # Owl / Bat: +7% dmg, 2.0s speed, Screech + Claw
        # Boar: -10% dmg, 2.0s speed, Charge + Bite
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
            if bestial_wrath > 0:
                # 18s duration every 120s = 15% uptime of +20% damage
                pet_dmg_mult *= 1.03

            pet_base_crit = 0.05 + (0.03 * ferocity)  # Ferocity: +3/6/9/12/15% crit
            pet_crit_mult = 2.0

            # Frenzy (+30% attack speed on crit)
            frenzy_uptime = min(1.0, pet_base_crit * (frenzy / 5.0) * (8.0 / pet_info["base_speed"])) if frenzy > 0 else 0.0
            eff_pet_speed = pet_info["base_speed"] / (1.0 + (0.30 * frenzy_uptime))

            # Pet Attack Power: base ~300 + 22% of Hunter RAP
            pet_ap = 300.0 + (rap * 0.22)
            pet_swings = fight_duration / eff_pet_speed

            # 1. Pet White Melee Swings
            raw_pet_swing = (pet_ap / 14.0) * pet_info["base_speed"]
            avg_pet_white = raw_pet_swing * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
            pet_white_total = pet_swings * avg_pet_white
            minion_damage_breakdown["pet_melee_dps"] = round(pet_white_total / fight_duration, 2)
            pet_damage_total += pet_white_total

            # Pet Focus Budget: 25/sec base, +50/100% with Bestial Discipline
            focus_regen = 25.0 * (1.0 + (0.50 * bestial_discipline))
            total_focus = focus_regen * fight_duration

            # 2. Family specific skills
            if chosen_pet == "wind_serpent":
                # Lightning Breath (Nature spell: 106 avg nature dmg, completely ignores physical armor!)
                lb_cost = 50.0
                lb_count = total_focus / lb_cost
                raw_lb = 106.0 + (pet_ap * 0.15)
                avg_lb = raw_lb * pet_dmg_mult * (1.0 + pet_base_crit)  # Magic, no armor reduction!
                lb_total = lb_count * avg_lb
                minion_damage_breakdown["pet_lightning_breath_dps"] = round(lb_total / fight_duration, 2)
                pet_damage_total += lb_total

            elif chosen_pet == "wolf":
                # Furious Howl: 60 focus, 10s CD, grants +51 damage to hunter's next physical hit
                howl_count = fight_duration / 10.0
                howl_dps_gain = (howl_count * 51.0 * (1.0 - armor_reduction)) / fight_duration
                minion_damage_breakdown["furious_howl_bonus_dps"] = round(howl_dps_gain, 2)
                pet_damage_total += (howl_count * 51.0 * (1.0 - armor_reduction))

                # Bite with remaining focus
                rem_focus = max(0.0, total_focus - (howl_count * 60.0))
                bite_count = min(fight_duration / 10.0, rem_focus / 35.0)
                raw_bite = 90.0 + (pet_ap * 0.10)
                avg_bite = raw_bite * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                bite_total = bite_count * avg_bite
                minion_damage_breakdown["pet_bite_dps"] = round(bite_total / fight_duration, 2)
                pet_damage_total += bite_total

            else:
                # Cat / Raptor / Owl / Boar: Bite (10s CD, 35 focus) + Claw / Screech (25 focus, no CD dump)
                bite_count = fight_duration / 10.0
                raw_bite = 90.0 + (pet_ap * 0.10)
                avg_bite = raw_bite * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                bite_total = bite_count * avg_bite
                minion_damage_breakdown["pet_bite_dps"] = round(bite_total / fight_duration, 2)
                pet_damage_total += bite_total

                rem_focus = max(0.0, total_focus - (bite_count * 35.0))
                if "Screech" in pet_info["skills"]:
                    screech_count = rem_focus / 20.0
                    raw_screech = 36.0 + (pet_ap * 0.05)
                    avg_screech = raw_screech * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                    screech_total = screech_count * avg_screech
                    minion_damage_breakdown["pet_screech_dps"] = round(screech_total / fight_duration, 2)
                    pet_damage_total += screech_total
                else:
                    claw_count = rem_focus / 25.0
                    raw_claw = 51.0 + (pet_ap * 0.08)
                    avg_claw = raw_claw * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                    claw_total = claw_count * avg_claw
                    minion_damage_breakdown["pet_claw_dps"] = round(claw_total / fight_duration, 2)
                    pet_damage_total += claw_total

            pet_dps = pet_damage_total / fight_duration

        total_dps = own_dps + pet_dps
        total_damage = own_damage_total + pet_damage_total

        primary_weapon = mainhand_weapon if (active_style == "melee" and mainhand_weapon) else (ranged_weapon or mainhand_weapon)
        prim_name = primary_weapon.get("name", "Standard Weapon") if primary_weapon else "Default Weapon"
        prim_speed = primary_weapon.get("speed", 2.8) if primary_weapon else 2.8

        # Build detailed damage sources for breakdown table
        damage_sources = []
        safe_total = max(0.001, total_dps)

        # 1. Player attacks
        source_defs = [
            ("white_melee_dps", "Main Hand Auto Attack", "White Melee", "#e0e0e0"),
            ("offhand_white_dps", "Off Hand Auto Attack", "White Melee", "#b0b0b0"),
            ("raptor_strike_dps", "Raptor Strike", "Survival Melee", "#c9a227"),
            ("mongoose_bite_dps", "Mongoose Bite", "Survival Melee", "#40c7eb"),
            ("counterattack_dps", "Counterattack", "Survival Melee", "#55c07b"),
            ("immolation_trap_dps", "Immolation Trap", "Trap / Fire", "#ff5533"),
            ("auto_shot_dps", "Auto Shot", "Ranged White", "#ffffff"),
            ("aimed_shot_dps", "Aimed Shot", "Ranged Skill", "#e268a8"),
            ("multi_shot_dps", "Multi-Shot", "Ranged Skill", "#f0a04b"),
            ("serpent_sting_dps", "Serpent Sting", "Nature DoT", "#44d67c"),
        ]

        for key, name, cat, col in source_defs:
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
                    "is_minion": False,
                    "is_proc": False,
                })

        # 2. Pet attacks
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

        # Ability casts summary
        ability_casts = {}
        if active_style == "melee":
            if "raptor_strike_dps" in own_damage_breakdown:
                ability_casts["raptor_strike"] = int(round(fight_duration / max(3.0, 6.0 - (0.2 * superior_strikes))))
            if "mongoose_bite_dps" in own_damage_breakdown:
                ability_casts["mongoose_bite"] = int(round((fight_duration / max(2.5, 5.0 - (0.2 * superior_strikes))) * 0.90))
            if counterattack_talent > 0 and "counterattack_dps" in own_damage_breakdown:
                ability_casts["counterattack"] = int(round((fight_duration / 5.0) * min(1.0, 0.05 + (0.01 * deflection))))
            if "immolation_trap_dps" in own_damage_breakdown:
                ability_casts["immolation_trap"] = int(round(fight_duration / 30.0))
        elif active_style == "ranged":
            if "auto_shot_dps" in own_damage_breakdown:
                eff_spd = base_speed / (1.0 + (haste_percent + quiver_haste + gear.get("haste", 0.0) + (troll_haste * 100.0)) / 100.0)
                ability_casts["auto_shot"] = int(round(fight_duration / eff_spd)) if eff_spd > 0 else 0
            if aimed_shot_talent > 0 and "aimed_shot_dps" in own_damage_breakdown:
                ability_casts["aimed_shot"] = int(round(fight_duration / 6.0))
            if "multi_shot_dps" in own_damage_breakdown:
                ability_casts["multi_shot"] = int(round(fight_duration / 10.0))
            if "serpent_sting_dps" in own_damage_breakdown:
                ability_casts["serpent_sting"] = int(round(fight_duration / 15.0))

        if pet_active and fight_duration > 0:
            if "pet_melee_dps" in minion_damage_breakdown:
                ability_casts["pet_swings"] = int(round(pet_swings))
            if "pet_claw_dps" in minion_damage_breakdown:
                ability_casts["pet_claws"] = int(round(total_focus / 25.0))
            if "pet_bite_dps" in minion_damage_breakdown:
                ability_casts["pet_bites"] = int(round(fight_duration / 10.0))
            if "pet_lightning_breath_dps" in minion_damage_breakdown:
                ability_casts["pet_lightning_breath"] = int(round(total_focus / 50.0))
            if "furious_howl_bonus_dps" in minion_damage_breakdown:
                ability_casts["furious_howl"] = int(round(fight_duration / 10.0))

        # Damage type breakdown
        magic_dps = (
            own_damage_breakdown.get("immolation_trap_dps", 0.0)
            + own_damage_breakdown.get("serpent_sting_dps", 0.0)
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

        # Weapon skills
        eff_ws = gear.get("effective_weapon_skill", 300)
        ws_hit = gear.get("weapon_skill_hit_bonus", 0.0)
        glance_fac = gear.get("glance_damage_factor", 0.65)

        return {
            "character_class": "hunter",
            "combat_style": active_style,
            "combat_style_name": "Survival Melee" if active_style == "melee" else ("Marksmanship Ranged" if active_style == "ranged" else "Hybrid"),
            "fight_duration": fight_duration,
            "weapon_name": prim_name,
            "base_weapon_speed": prim_speed,
            "effective_weapon_speed": round(prim_speed / (1.0 + (haste_percent / 100.0)), 2),
            "exact_melee_swings": total_melee_swings if active_style == "melee" else int(round(fight_duration / prim_speed)),
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
            "magic_hits_per_second": 0.0,
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
