import math
from typing import Any, Dict, List, Optional, Union

from src.items_db import calculate_gear_totals, load_items_db
from .base import BaseCombatCalculator


class HunterCombatCalculator(BaseCombatCalculator):

    AMMO_CATALOG: Dict[str, Dict[str, Any]] = {
        "thorium_arrow": {"name": "Thorium Headed Arrow / Thorium Shells", "dps": 17.5},
        "doomshot": {"name": "Doomshot (Strzały LBRS)", "dps": 20.0},
        "miniature_cannon_balls": {"name": "Miniature Cannon Balls (Pociski Strat)", "dps": 20.5},
        "rockshard_pellets": {"name": "Rockshard Pellets (Pociski Maraudon)", "dps": 18.0},
        "ice_threaded": {"name": "Ice Threaded Arrow / Bullet (AV)", "dps": 16.5},
        "mithril_gyro_shot": {"name": "Mithril Gyro-Shot (Engineering)", "dps": 15.0},
        "explosive_arrow": {"name": "Explosive Arrow", "dps": 14.5},
        "jagged_arrow": {"name": "Jagged Arrow / Accurate Slugs", "dps": 13.0},
        "hi_impact_mithril": {"name": "Hi-Impact Mithril Slugs", "dps": 12.5},
        "precision_arrow": {"name": "Precision Arrow", "dps": 11.5},
        "feathered_arrow": {"name": "Feathered Arrow / Exploding Shot", "dps": 9.5},
        "razor_arrow": {"name": "Razor Arrow / Solid Shot", "dps": 7.5},
        "sharp_arrow": {"name": "Sharp Arrow / Heavy Shot", "dps": 3.5},
        "rough_arrow": {"name": "Rough Arrow / Light Shot", "dps": 1.5},
        "none": {"name": "Brak amunicji", "dps": 0.0},
    }

    def __init__(self, db: Optional[Dict] = None):
        self.db = db if db is not None else load_items_db()

    def calculate(
        self,
        equipped_items: List[Union[int, str, Dict]],
        fight_duration: float = 60.0,
        haste_percent: float = 0.0,
        target_armor: float = 3731.0,
        pet_active: bool = True,
        pet_family: str = "raptor",
        use_rapid_fire: bool = True,
        combat_style: str = "auto",
        quiver_haste: float = 14.0,
        ammo_dps: float = 17.5,
        ammo_type: str = "thorium_arrow",
        talents: Optional[Dict[str, int]] = None,
        race: str = "nightelf",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        t = talents or {}

        # Rapid Fire toggle (increases attack speed by 40% for 15s)
        if "use_rapid_fire" in kwargs:
            use_rapid_fire = bool(kwargs.get("use_rapid_fire"))

        # Beast Mastery Talents (https://octowow.st/talents/hunter/)
        swift_aspects = int(t.get("Swift Aspects", t.get("swift_aspects", 0)))
        coordinated_assault = int(t.get("Coordinated Assault", t.get("coordinated_assault", 0)))
        unleashed_fury = int(t.get("Unleashed Fury", t.get("unleashed_fury", 0)))
        bestial_discipline = int(t.get("Bestial Discipline", t.get("bestial_discipline", 0)))
        ferocity = int(t.get("Ferocity", t.get("ferocity", 0)))
        scent_of_blood = int(t.get("Scent of Blood", t.get("scent_of_blood", 0)))
        bestial_wrath_talent = int(t.get("Bestial Wrath", t.get("bestial_wrath", 0)))
        intimidation_talent = int(t.get("Intimidation", t.get("intimidation", 0)))
        bestial_precision = int(t.get("Bestial Precision", t.get("bestial_precision", 0)))
        spirit_bond = int(t.get("Spirit Bond", t.get("spirit_bond", 0)))
        frenzy = int(t.get("Frenzy", t.get("frenzy", 0)))
        kill_command_talent = int(t.get("Kill Command", t.get("kill_command", 0)))

        # Marksmanship Talents (https://octowow.st/talents/hunter/)
        imp_stings = int(t.get("Improved Stings", t.get("Improved Serpent Sting", t.get("improved_stings", 0))))
        lethal_shots = int(t.get("Lethal Shots", t.get("lethal_shots", 0)))
        aimed_shot_talent = int(t.get("Aimed Shot", t.get("aimed_shot", 0)))
        swiftshot = int(t.get("Swiftshot", t.get("swiftshot", 0)))
        endless_quiver = int(t.get("Endless Quiver", t.get("endless_quiver", 0)))
        mortal_shots = int(t.get("Mortal Shots", t.get("mortal_shots", 0)))
        experimental_ammo = int(t.get("Experimental Ammunition", t.get("experimental_ammunition", 0)))
        piercing_shots = int(t.get("Piercing Shots", t.get("piercing_shots", 0)))
        barrage = int(t.get("Barrage", t.get("barrage", 0)))
        imp_marksmanship = int(t.get("Improved Marksmanship", t.get("improved_marksmanship", 0)))
        ranged_weapon_spec = int(t.get("Ranged Weapon Specialization", t.get("ranged_weapon_spec", 0)))
        lock_and_load = int(t.get("Lock and Load", t.get("lock_and_load", 0)))
        trueshot_aura = int(t.get("Trueshot Aura", t.get("trueshot_aura", 0)))
        rapid_killing = int(t.get("Rapid Killing", t.get("rapid_killing", 0)))

        # Survival Talents (https://octowow.st/talents/hunter/)
        imp_slaying = int(t.get("Improved Slaying", t.get("improved_slaying", 0)))
        resourcefulness = int(t.get("Resourcefulness", t.get("resourcefulness", 0)))
        swift_reflexes = int(t.get("Swift Reflexes", t.get("swift_reflexes", 0)))
        savage_strikes = int(t.get("Savage Strikes", t.get("savage_strikes", 0)))
        alone_against_world = int(t.get("Alone Against the World", t.get("alone_against_the_world", 0)))
        planning_ahead = int(t.get("Planning Ahead", t.get("planning_ahead", 0)))
        survivalist = int(t.get("Survivalist", t.get("survivalist", 0)))
        carve_talent = int(t.get("Carve", t.get("carve", 0)))
        stinging_nettle = int(t.get("Stinging Nettle", t.get("stinging_nettle", 0)))
        surefooted = int(t.get("Surefooted", t.get("surefooted", 0)))
        killer_instinct = int(t.get("Killer Instinct", t.get("killer_instinct", 0)))
        trap_mastery = int(t.get("Trap Mastery", t.get("Clever Traps", t.get("trap_mastery", 0))))
        lacerate_talent = int(t.get("Lacerate", t.get("lacerate", 0)))
        vicious_strikes = int(t.get("Vicious Strikes", t.get("vice_strikes", 0)))
        superior_strikes = int(t.get("Superior Strikes", t.get("superior_strikes", 0)))
        lightning_reflexes = int(t.get("Lightning Reflexes", t.get("lightning_reflexes", 0)))
        untamed_trapper = int(t.get("Untamed Trapper", t.get("untamed_trapper", 0)))

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

        # High Elf (+2% Agility racial) & Lightning Reflexes (Octo WoW: +2/4/6/8/10% Agility and +20/40/60/80/100% of Agility as Melee AP)
        base_agi = gear["agility"]
        highelf_agi_mult = 1.02 if race_clean == "highelf" else 1.0
        effective_agi = base_agi * highelf_agi_mult * (1.0 + (0.02 * lightning_reflexes))
        gear["agility"] = int(round(effective_agi))

        equipped_id_set = {int(it["id"]) for it in gear.get("equipped_items", []) if str(it.get("id", "")).isdigit()}
        active_sets = gear.get("active_sets", {})
        set_counts_map = {int(sid): int(sdata.get("equipped_count", 0)) for sid, sdata in active_sets.items() if str(sid).isdigit()}

        # Hunter Set & Item Bonuses (Octo WoW ItemSet.dbc & Spell.dbc)
        has_giantstalker_8pc = set_counts_map.get(206, 0) >= 8
        has_dragonstalker_3pc = set_counts_map.get(215, 0) >= 3
        has_dragonstalker_8pc = set_counts_map.get(215, 0) >= 8
        has_predator_3pc = set_counts_map.get(477, 0) >= 3
        has_predator_5pc = set_counts_map.get(477, 0) >= 5
        has_strikers_3pc = set_counts_map.get(509, 0) >= 3
        has_strikers_5pc = set_counts_map.get(509, 0) >= 5
        has_unseen_path_3pc = set_counts_map.get(510, 0) >= 3
        has_cryptstalker_2pc = set_counts_map.get(530, 0) >= 2
        has_pvp_wing_clip_cd = any(
            set_counts_map.get(sid, 0) >= thr
            for sid, thr in ((361, 4), (362, 4), (395, 3), (396, 3), (543, 4), (550, 4))
        )

        # PvP Gloves (Spell 28539: +4% Multi-Shot and Carve damage) & Giantstalker 8pc (Spell 23566: +15% Multi-Shot and Carve damage)
        has_pvp_multishot_gloves = bool(equipped_id_set.intersection({16571, 16463, 22862, 23279}))
        multishot_carve_item_mult = (1.04 if has_pvp_multishot_gloves else 1.0) * (1.15 if has_giantstalker_8pc else 1.0)
        unseen_path_strike_crit_bonus = 0.02 if has_unseen_path_3pc else 0.0
        use_trinkets = bool(kwargs.get("use_trinkets", True))
        has_renataki_trinket = (19953 in equipped_id_set) and use_trinkets
        has_arcane_infused_gem = (19336 in equipped_id_set) and use_trinkets
        has_black_book = (19337 in equipped_id_set) and use_trinkets

        # Detect weapons
        ranged_weapon = None
        mainhand_weapon = None
        offhand_weapon = None

        for it in gear.get("equipped_items", []):
            slot = it.get("slot")
            subclass = (it.get("subclass") or "").lower().strip()
            if slot == "ranged" and subclass in ("bow", "crossbow", "gun"):
                ranged_weapon = it
            elif slot in ("main_hand", "two_hand", "one_hand", "mainhand", "twohand", "onehand"):
                mainhand_weapon = it
            elif slot in ("off_hand", "offhand") and it.get("speed", 0) > 0:
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
            elif vicious_strikes > 0 or superior_strikes > 0 or savage_strikes > 0 or carve_talent > 0 or lacerate_talent > 0 or untamed_trapper > 0 or (has_melee and not has_ranged):
                active_spec = "survival"
                active_style = "melee"
            elif bestial_wrath_talent > 0 or kill_command_talent > 0:
                active_spec = "beast_mastery"
                active_style = "ranged"
            elif lock_and_load > 0 or experimental_ammo > 0 or mortal_shots >= 3:
                active_spec = "marksmanship"
                active_style = "ranged"
            elif unleashed_fury >= 3:
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
                active_priority_list = [
                    "raptor_strike",
                    "mongoose_bite",
                    "carve",
                    "immolation_trap",
                    "lacerate",
                    "wing_clip",
                    "white_melee",
                ]
            elif active_spec == "beast_mastery":
                active_priority_list = [
                    "bestial_wrath",
                    "kill_command",
                    "serpent_sting",
                    "arcane_shot",
                    "steady_shot",
                    "auto_shot",
                    "strike_together",
                    "pet_focus_dump",
                ]
            else:  # marksmanship 1.18 rework (Auto Shot <-> Steady Shot alternating)
                active_priority_list = [
                    "aimed_shot",
                    "multi_shot",
                    "serpent_sting",
                    "arcane_shot",
                    "steady_shot",
                    "auto_shot",
                ]

        # Pet Family selection (only the 4 Octo WoW pets: Raptor, Wind Serpent, Serpent, Wolf)
        chosen_pet = str(kwargs.get("pet_family", pet_family)).lower().strip()
        valid_pets = ("raptor", "wind_serpent", "serpent", "wolf")
        if chosen_pet not in valid_pets:
            chosen_pet = "raptor"

        # Ammunition selection (used in Marksmanship and Beast Mastery ranged rotations)
        chosen_ammo = str(kwargs.get("ammo_type", ammo_type)).lower().strip()
        if chosen_ammo in self.AMMO_CATALOG:
            ammo_info = self.AMMO_CATALOG[chosen_ammo]
            ammo_dps = float(ammo_info["dps"])
        else:
            chosen_ammo = "thorium_arrow"
            ammo_info = self.AMMO_CATALOG["thorium_arrow"]
            if "ammo_dps" in kwargs:
                ammo_dps = float(kwargs["ammo_dps"])
            else:
                ammo_dps = float(ammo_info["dps"])
        ammo_damage_total = 0.0

        # Alone Against the World (Survival Row 2 Col 4: +3/6% all damage dealt while no pet is active)
        lone_wolf_mult = (1.0 + (0.03 * alone_against_world)) if not pet_active else 1.0

        # General multipliers
        slaying_mult = (1.0 + (0.01 * imp_slaying)) * lone_wolf_mult
        effective_target_armor = max(0.0, target_armor - gear.get("arp", 0.0))
        armor_reduction = effective_target_armor / (effective_target_armor + 5500.0) if effective_target_armor > 0 else 0.0

        # Aspect Selection (Auto, Wolf, Hawk, Monkey, None)
        chosen_aspect = str(kwargs.get("hunter_aspect", kwargs.get("aspect", "auto"))).lower().strip()
        if chosen_aspect == "auto":
            chosen_aspect = "hawk" if active_style == "ranged" else "wolf"

        hawk_rap = 0
        wolf_map = 0
        monkey_dodge = 0.0
        if chosen_aspect in ("wolf", "aspect_of_the_wolf"):
            # Octo WoW custom aspect: Aspect of the Wolf (Rank 7: +120 Melee AP, +20% with Dragonstalker 3pc = +144 Melee AP)
            wolf_map = 144 if has_dragonstalker_3pc else 120
        elif chosen_aspect in ("hawk", "aspect_of_the_hawk"):
            hawk_rap = 144 if has_dragonstalker_3pc else 120
        elif chosen_aspect in ("monkey", "aspect_of_the_monkey"):
            monkey_dodge = 0.08  # Rank 6 Aspect of the Monkey (+8% Dodge)

        # Trueshot Aura in Octo WoW (Spell 19506: +3% Attack Power plus +30 flat AP to party members)
        has_trueshot_aura = bool(kwargs.get("trueshot_aura", False)) or (trueshot_aura > 0)
        ts_flat_ap = 30 if has_trueshot_aura else 0
        ts_pct_mult = 1.03 if has_trueshot_aura else 1.0
        ds_8pc_ap = int(450 * 0.20) if has_dragonstalker_8pc else 0

        # Level 60 Base AP (Vanilla Hunter Level 60 base AP = 100)
        base_lvl60_ap = 100

        # On-Use Trinkets Engine (Devilsaur Eye, Earthstrike, Slayer's Crest, Kiss of the Spider, Jom Gabbar, etc.)
        use_trinkets = bool(kwargs.get("use_trinkets", True))
        is_orc = race_clean == "orc"
        on_use_ap = 0.0
        on_use_hit = 0.0
        on_use_haste = 0.0
        on_use_arp = 0.0
        active_onuse_trinkets = []

        if use_trinkets:
            for itm in gear.get("equipped_items", []):
                slot_clean = (itm.get("slot") or "").lower().strip()
                if slot_clean not in ("trinket", "trinket1", "trinket2"):
                    continue
                try:
                    iid = int(itm.get("id", 0))
                except (ValueError, TypeError):
                    continue
                if iid == 19991:  # Devilsaur Eye (+150 AP, +2% Hit for 20s, 120s CD)
                    up = min(fight_duration, 20.0) / fight_duration if fight_duration > 0 else 0.0
                    on_use_ap += 150.0 * up
                    on_use_hit += 2.0 * up
                    active_onuse_trinkets.append("Devilsaur Eye (+150 AP, +2% Hit for 20s)")
                elif iid == 21180:  # Earthstrike (+280 AP for 20s, 120s CD)
                    up = min(fight_duration, 20.0) / fight_duration if fight_duration > 0 else 0.0
                    on_use_ap += 280.0 * up
                    active_onuse_trinkets.append("Earthstrike (+280 AP for 20s)")
                elif iid == 23041:  # Slayer's Crest (+260 AP for 20s, 120s CD)
                    up = min(fight_duration, 20.0) / fight_duration if fight_duration > 0 else 0.0
                    on_use_ap += 260.0 * up
                    active_onuse_trinkets.append("Slayer's Crest (+260 AP for 20s)")
                elif iid == 22954:  # Kiss of the Spider (+20% Haste for 15s, 120s CD)
                    up = min(fight_duration, 15.0) / fight_duration if fight_duration > 0 else 0.0
                    on_use_haste += 0.20 * up
                    active_onuse_trinkets.append("Kiss of the Spider (+20% Haste for 15s)")
                elif iid == 21670:  # Badge of the Swarmguard (Stacking ArP, ~400 avg over 30s)
                    up = min(fight_duration, 30.0) / fight_duration if fight_duration > 0 else 0.0
                    on_use_arp += 400.0 * up
                    active_onuse_trinkets.append("Badge of the Swarmguard (Stacking ArP)")
                elif iid == 23570:  # Jom Gabbar (Ramping AP, ~357 avg for 20s)
                    up = min(fight_duration, 20.0) / fight_duration if fight_duration > 0 else 0.0
                    on_use_ap += 357.0 * up
                    active_onuse_trinkets.append("Jom Gabbar (+357 AP for 20s)")
                elif iid == 60559:  # Hatereaver Cog (+150 AP for 15s)
                    up = min(fight_duration, 15.0) / fight_duration if fight_duration > 0 else 0.0
                    on_use_ap += 150.0 * up
                    active_onuse_trinkets.append("Hatereaver Cog (+150 AP for 15s)")

        # Orc Blood Fury racial bonus (+25% base melee AP for 15s on 120s CD)
        racial_ap = 0.0
        if is_orc and fight_duration > 0 and (active_style == "melee" or has_melee):
            bf_uptime = min(fight_duration, 15.0) / fight_duration
            naked_base_ap = base_lvl60_ap + gear["strength"] + int(effective_agi * 1)
            racial_ap = (naked_base_ap * 0.25) * bf_uptime

        # Attack Power Calculation
        # Lightning Reflexes in Octo WoW adds 20/40/60/80/100% of Agility to Melee AP
        # Aspect of the Wolf in Octo WoW adds +120 Melee AP (+144 with Dragonstalker 3pc)
        lr_bonus_map = int(effective_agi * (0.20 * lightning_reflexes))
        base_rap = int(round((base_lvl60_ap + gear.get("ranged_attack_power", 0) + gear["attack_power"] + int(effective_agi * 2) + hawk_rap + ds_8pc_ap + ts_flat_ap) * ts_pct_mult))
        base_map = int(round((base_lvl60_ap + gear["attack_power"] + gear["strength"] + int(effective_agi * 1) + lr_bonus_map + wolf_map + ds_8pc_ap + ts_flat_ap + racial_ap) * ts_pct_mult))

        rap = int(round(base_rap + on_use_ap))
        map_ap = int(round(base_map + on_use_ap))

        is_troll = race_clean == "troll"
        is_nightelf = race_clean == "nightelf"
        troll_haste = (0.10 * min(1.0, 10.0 / max(1.0, fight_duration)) if is_troll else 0.0) + (0.01 if is_nightelf else 0.0)

        # Ranged Weapon Skill bonus (+5 Bow for Troll, +5 Gun for Dwarf, +item weapon skills, +5 quest weapon skills)
        ranged_sub = (ranged_weapon.get("subclass") or "").lower().strip() if ranged_weapon else ""
        ranged_ws_bonus = 0
        if has_ranged:
            ranged_ws_bonus += int(gear.get("weapon_skills", {}).get(ranged_sub, 0))
            if race_clean == "troll" and ranged_sub == "bow":
                ranged_ws_bonus += 5
            elif race_clean == "dwarf" and ranged_sub == "gun":
                ranged_ws_bonus += 5
            if quest_weapon_skills and (quest_weapon_skills.get(ranged_sub) or quest_weapon_skills.get("ranged")):
                ranged_ws_bonus += 5
        ranged_ws_hit_bonus = (ranged_ws_bonus // 5) * 1.0

        # Crit & Hit (Surefooted in Octo WoW grants +1/2/3% hit and an additional +1/2/3% while dual wielding)
        ranged_crit = gear["crit"] + (effective_agi / 53.0) + (1.0 * lethal_shots) + (1.0 * killer_instinct)
        ranged_hit = gear["hit"] + (1.0 * surefooted) + ranged_ws_hit_bonus + on_use_hit
        ranged_hit_rate = min(1.0, max(0.0, (100.0 - max(0.0, 8.0 - ranged_hit)) / 100.0))

        melee_crit = gear["crit"] + (effective_agi / 53.0) + (1.0 * killer_instinct)
        dw_surefooted_bonus = (1.0 * surefooted) if is_dw else 0.0
        melee_hit = gear["hit"] + (1.0 * surefooted) + dw_surefooted_bonus + on_use_hit

        own_damage_breakdown = {}
        own_damage_total = 0.0
        ability_casts = {}
        total_melee_swings = 0

        if active_style == "ranged" and not has_ranged:
            gear.setdefault("class_warnings", []).append(
                "Brak założonej broni dystansowej (Ranged: Łuk / Kusza / Strzelba) – umiejętności dystansowe Huntera wymagają broni dystansowej."
            )
        elif active_style == "melee" and not has_melee:
            gear.setdefault("class_warnings", []).append(
                "Brak założonej broni białej (Main Hand / Two-Hand) – umiejętności walki w zwarciu wymagają broni białej."
            )

        # Rapid Fire cooldown & uptime (40% attack speed for 15s [+4s with Cryptstalker 2pc]; -120s CD with Striker's Garb 5pc)
        rf_uptime = 0.0
        if use_rapid_fire and fight_duration > 0 and (has_ranged or has_melee):
            base_rf_cd = 180.0 - (60.0 if rapid_killing > 0 else 0.0) - (120.0 if has_strikers_5pc else 0.0)
            rf_cd = max(45.0, base_rf_cd)
            rf_dur = 15.0 + (4.0 if has_cryptstalker_2pc else 0.0)
            rf_casts = 1 + int(max(0.0, fight_duration - 1.0) / rf_cd)
            ability_casts["rapid_fire"] = rf_casts
            total_rf_time = min(fight_duration, rf_casts * rf_dur)
            rf_uptime = total_rf_time / fight_duration

        # Swift Aspects in Octo WoW:
        # While Aspect of the Hawk is active, 10% chance on ranged attack to increase ranged attack speed by 3/6/9/12/15% for 12s.
        # While Aspect of the Wolf is active, 10% chance on melee attack to increase melee attack speed by 3/6/9/12/15% for 12s.
        swift_aspects_ranged_haste = (0.03 * swift_aspects) * 0.68 if (swift_aspects > 0 and chosen_aspect in ("hawk", "aspect_of_the_hawk")) else 0.0
        swift_aspects_melee_haste = (0.03 * swift_aspects) * 0.68 if (swift_aspects > 0 and chosen_aspect in ("wolf", "aspect_of_the_wolf")) else 0.0
        swift_reflexes_haste = 0.01 * swift_reflexes

        eff_ranged_speed = ranged_weapon.get("speed", 2.8) if has_ranged else 0.0
        eff_mh_speed = mainhand_weapon.get("speed", 3.0) if has_melee else 0.0
        bw_active_ratio = 0.0

        # -------------------------------------------------------------
        # 1. MARKSMANSHIP SPEC (Patch 1.18 Rework: Auto Shot <-> Steady Shot 1:1 Weaving)
        # -------------------------------------------------------------
        if active_spec == "marksmanship" and fight_duration > 0 and has_ranged:
            rw_speed = ranged_weapon.get("speed", 2.8)
            rw_min = ranged_weapon.get("min_damage", 0.0)
            rw_max = ranged_weapon.get("max_damage", 0.0)
            avg_rw_dmg = (rw_min + rw_max) / 2.0

            # Ranged Weapon Specialization in Octo WoW: +2/4/6/8/10% ranged weapon damage
            rw_mult = 1.0 + (0.02 * ranged_weapon_spec)
            imp_mm_mult = 1.0 + (0.05 * imp_marksmanship)
            ranged_crit_mult = 2.0 + (0.06 * mortal_shots) + (0.01 * imp_slaying)
            # 3% crit suppression against Level 63 Raid Boss
            ranged_crit_rate = min(1.0, max(0.01, (ranged_crit - 3.0) / 100.0))
            piercing_bleed_mult = 1.0 + ((0.15 * piercing_shots) * ranged_crit_rate)

            total_ranged_haste = (
                (haste_percent / 100.0)
                + (quiver_haste / 100.0)
                + (gear.get("haste", 0.0) / 100.0)
                + troll_haste
                + swift_aspects_ranged_haste
                + swift_reflexes_haste
                + (0.40 * rf_uptime)
            )
            haste_div = max(0.1, 1.0 + total_ranged_haste)
            eff_ranged_speed = rw_speed / haste_div
            auto_windup = 0.5 / haste_div
            steady_cast_dur = 1.5 / haste_div

            # Alternating Auto Shot <-> Steady Shot 1:1 cycle duration
            steady_pair_dur = max(eff_ranged_speed, auto_windup + steady_cast_dur)

            # Aimed Shot (Spell 20904: 26.0s base CD, -2/4/6s via Swiftshot; Lock and Load resets CD on Steady/Arcane/Aimed crit & -1.0s cast time)
            lnl_cast_red = 0.65 if lock_and_load > 0 else 0.0
            aimed_cast_dur = max(1.0, (2.5 - lnl_cast_red) / haste_div)
            aimed_pair_dur = max(eff_ranged_speed, auto_windup + aimed_cast_dur)

            renataki_bonus_casts = (1 + int(max(0.0, fight_duration - 1.0) / 180.0)) if has_renataki_trinket else 0
            base_aimed_cd = max(14.0, 26.0 - (2.0 * swiftshot))
            if lock_and_load > 0:
                aimed_cd = max(6.5, min(base_aimed_cd, 2.4 / max(0.08, ranged_crit_rate)))
            else:
                aimed_cd = base_aimed_cd
            est_aimed_casts = (int(round(fight_duration / aimed_cd)) + renataki_bonus_casts) if "aimed_shot" in active_priority_list else 0

            # Total 1:1 Auto Shot <-> Woven Shot cycles in fight_duration
            aimed_time_used = min(fight_duration * 0.65, est_aimed_casts * aimed_pair_dur)
            rem_fight_time = max(0.0, fight_duration - aimed_time_used)
            rem_auto_cycles = rem_fight_time / steady_pair_dur if steady_pair_dur > 0 else 0.0
            base_auto_shots = float(est_aimed_casts) + rem_auto_cycles
            remaining_weave_slots = float(int(round(base_auto_shots)))

            for spell_key in active_priority_list:
                # 1.2 Aimed Shot
                if spell_key == "aimed_shot" and remaining_weave_slots > 0:
                    aimed_casts = int(round(min(remaining_weave_slots, float(est_aimed_casts))))
                    remaining_weave_slots = max(0.0, remaining_weave_slots - aimed_casts)
                    ability_casts["aimed_shot"] = aimed_casts

                    exp_ammo_mult = 1.05 if experimental_ammo > 0 else 1.0
                    aimed_shot_mult = (
                        (1.0 - armor_reduction)
                        * slaying_mult
                        * rw_mult
                        * imp_mm_mult
                        * ranged_hit_rate
                        * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                        * piercing_bleed_mult
                    )
                    raw_aimed = (avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * rw_speed) + 600.0) * exp_ammo_mult
                    avg_aimed_hit = raw_aimed * aimed_shot_mult
                    aimed_total = aimed_casts * avg_aimed_hit
                    ammo_damage_total += aimed_casts * ((ammo_dps * rw_speed) * exp_ammo_mult * aimed_shot_mult)
                    own_damage_breakdown["aimed_shot_dps"] = round(aimed_total / fight_duration, 2)
                    own_damage_total += aimed_total

                # 1.3 Multi-Shot (Spell 25294: 10.0s CD, +150 dmg, Barrage +5/10/15%, Giantstalker 8pc +15%, PvP Gloves +4%, Piercing Shots bleed)
                elif spell_key == "multi_shot" and remaining_weave_slots > 0:
                    multi_cd = 10.0
                    max_multi = int(round(fight_duration / multi_cd)) + renataki_bonus_casts
                    multi_casts = int(round(min(remaining_weave_slots, float(max_multi))))
                    remaining_weave_slots = max(0.0, remaining_weave_slots - multi_casts)
                    ability_casts["multi_shot"] = multi_casts

                    barrage_mult = (1.0 + (0.05 * barrage)) * multishot_carve_item_mult
                    multi_shot_mult = (
                        (1.0 - armor_reduction)
                        * slaying_mult
                        * rw_mult
                        * barrage_mult
                        * ranged_hit_rate
                        * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                        * piercing_bleed_mult
                    )
                    raw_multi = avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * rw_speed) + 150.0
                    avg_multi_hit = raw_multi * multi_shot_mult
                    multi_total = multi_casts * avg_multi_hit
                    ammo_damage_total += multi_casts * ((ammo_dps * rw_speed) * multi_shot_mult)
                    own_damage_breakdown["multi_shot_dps"] = round(multi_total / fight_duration, 2)
                    own_damage_total += multi_total

                # 1.4 Arcane Shot (Spell 14287: 6.0s CD [-0.5/1.0/1.5s Swiftshot], 45% ranged weapon damage + 166 Arcane damage)
                elif spell_key == "arcane_shot" and remaining_weave_slots > 0:
                    arcane_cd = max(4.5, 6.0 - (0.5 * swiftshot))
                    max_arcane = int(round(fight_duration / arcane_cd)) + renataki_bonus_casts
                    arcane_casts = int(round(min(remaining_weave_slots, float(max_arcane))))
                    remaining_weave_slots = max(0.0, remaining_weave_slots - arcane_casts)
                    if arcane_casts > 0:
                        ability_casts["arcane_shot"] = arcane_casts
                        raw_arcane_wpn = 0.45 * (avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * rw_speed)) * (1.0 - armor_reduction) * rw_mult
                        raw_arcane_magic = 166.0 + (gear["spell_power"] * 0.15)
                        arcane_shot_mult = slaying_mult * ranged_hit_rate * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                        avg_arcane_hit = (raw_arcane_wpn + raw_arcane_magic) * arcane_shot_mult
                        arcane_total = (arcane_casts * avg_arcane_hit) + (1110.0 * slaying_mult if has_arcane_infused_gem else 0.0)
                        ammo_damage_total += arcane_casts * (0.45 * (ammo_dps * rw_speed) * (1.0 - armor_reduction) * rw_mult * arcane_shot_mult)
                        own_damage_breakdown["arcane_shot_dps"] = round(arcane_total / fight_duration, 2)
                        own_damage_total += arcane_total

                # 1.5 Serpent Sting (Nature DoT, Improved Stings +6/12/18/24/30%, Predator 5pc +25% tick speed, Striker 3pc venom proc)
                elif spell_key == "serpent_sting" and remaining_weave_slots > 0:
                    max_serpent = max(1, int(round(fight_duration / 15.0)))
                    serpent_casts = int(round(min(remaining_weave_slots, float(max_serpent))))
                    remaining_weave_slots = max(0.0, remaining_weave_slots - serpent_casts)
                    ability_casts["serpent_sting"] = serpent_casts
                    pred_sting_mult = 1.25 if has_predator_5pc else 1.0
                    strikers_venom_dps = 8.33 if has_strikers_3pc else 0.0
                    serpent_uptime = min(1.0, (serpent_casts * 15.0) / fight_duration)
                    serpent_dps = ((37.0 * (1.0 + (0.06 * imp_stings)) * pred_sting_mult) + strikers_venom_dps) * slaying_mult * ranged_hit_rate * serpent_uptime
                    serpent_total = serpent_dps * fight_duration
                    own_damage_breakdown["serpent_sting_dps"] = round(serpent_dps, 2)
                    own_damage_total += serpent_total

                # 1.6 Steady Shot (Spell 45974 Rank 8: 1.5s cast, 100% normalized weapon dmg + 125, woven 1:1 alternating with Auto Shot)
                elif spell_key == "steady_shot" and remaining_weave_slots > 0:
                    steady_casts = int(round(remaining_weave_slots))
                    remaining_weave_slots = 0.0
                    ability_casts["steady_shot"] = steady_casts

                    steady_crit_rate = min(1.0, ranged_crit_rate + unseen_path_strike_crit_bonus)
                    steady_shot_mult = (
                        (1.0 - armor_reduction)
                        * slaying_mult
                        * rw_mult
                        * imp_mm_mult
                        * ranged_hit_rate
                        * (1.0 + (ranged_crit_mult - 1.0) * steady_crit_rate)
                        * piercing_bleed_mult
                    )
                    raw_steady = avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * rw_speed) + 125.0
                    avg_steady_hit = raw_steady * steady_shot_mult
                    steady_total = steady_casts * avg_steady_hit
                    ammo_damage_total += steady_casts * ((ammo_dps * rw_speed) * steady_shot_mult)
                    own_damage_breakdown["steady_shot_dps"] = round(steady_total / fight_duration, 2)
                    own_damage_total += steady_total

            # 1.7 Auto Shot (Alternating with Steady Shot + Endless Quiver 3/6% extra shot proc)
            if "auto_shot" in active_priority_list:
                total_ranged_triggers = (
                    base_auto_shots
                    + ability_casts.get("arcane_shot", 0)
                    + ability_casts.get("steady_shot", 0)
                    + ability_casts.get("multi_shot", 0)
                )
                quiver_extra_shots = total_ranged_triggers * (0.03 * endless_quiver)
                auto_shots_count = base_auto_shots + quiver_extra_shots
                ability_casts["auto_shot"] = int(round(auto_shots_count))

                auto_shot_mult = (
                    (1.0 - armor_reduction)
                    * slaying_mult
                    * rw_mult
                    * ranged_hit_rate
                    * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                )
                raw_auto_shot = avg_rw_dmg + (rap / 14.0) * rw_speed + (ammo_dps * rw_speed)
                avg_auto_hit = raw_auto_shot * auto_shot_mult
                auto_shot_damage = auto_shots_count * avg_auto_hit
                ammo_damage_total += auto_shots_count * ((ammo_dps * rw_speed) * auto_shot_mult)
                own_damage_breakdown["auto_shot_dps"] = round(auto_shot_damage / fight_duration, 2)
                own_damage_total += auto_shot_damage

        # -------------------------------------------------------------
        # 2. SURVIVAL SPEC (Melee Single-Target Macro Rotation)
        #    Macro Priority:
        #    1. /cast Raptor Strike
        #    2. /cast Mongoose Bite
        #    3. /cast Carve
        #    4. /cast Immolation Trap
        #    5. /cast Lacerate
        #    6. /cast Wing Clip
        #    + White Melee Swings
        # -------------------------------------------------------------
        elif active_spec == "survival" and fight_duration > 0 and has_melee:
            mh_speed = mainhand_weapon.get("speed", 3.0)
            mh_min = mainhand_weapon.get("min_damage", 0.0)
            mh_max = mainhand_weapon.get("max_damage", 0.0)
            mh_avg = (mh_min + mh_max) / 2.0

            # Melee haste comes from gear, racials, Swift Reflexes, on-use trinkets, Swift Aspects, and Rapid Fire (+40% attack speed)
            melee_haste = (
                (haste_percent / 100.0)
                + (gear.get("haste", 0.0) / 100.0)
                + troll_haste
                + swift_aspects_melee_haste
                + swift_reflexes_haste
                + on_use_haste
                + (0.40 * rf_uptime)
            )
            eff_mh_speed = (mh_speed / (1.0 + melee_haste)) if (1.0 + melee_haste) > 0 else mh_speed
            mh_swings = fight_duration / eff_mh_speed if eff_mh_speed > 0 else 0.0

            # Killer Instinct in Octo WoW increases melee critical strike damage bonus by 7/14/20%
            ki_crit_bonus = {0: 0.0, 1: 0.07, 2: 0.14}.get(killer_instinct, 0.20 if killer_instinct >= 3 else 0.0)
            crit_mult = 2.0 + ki_crit_bonus + (0.01 * imp_slaying)
            crit_rate = min(1.0, max(0.0, melee_crit / 100.0))
            # Savage Strikes increases crit of Raptor Strike, Mongoose Bite, Carve, Lacerate, Wing Clip by 3/6%
            strike_crit_bonus = 0.03 * savage_strikes if savage_strikes > 0 else 0.0
            strike_crit_rate = min(1.0, max(0.0, crit_rate + strike_crit_bonus))

            # Mainhand weapon skill calculation for Melee
            eq_ws_list = gear.get("equipped_weapon_skills", [])
            if eq_ws_list:
                eff_ws = min(315, eq_ws_list[0].get("skill", 300))
            else:
                eff_ws = gear.get("effective_weapon_skill", 300)
            ws_above_300 = max(0, eff_ws - 300)

            # Turtle WoW / Octo WoW weapon skill mechanics vs Level 63 boss:
            # 5 weapon skill = +1.0% hit chance
            ws_hit_bonus = (ws_above_300 // 5) * 1.0
            # Glancing blow factor: 0.70 at 300 skill + 0.02 per skill above 300, capped at 1.00 at 315
            glance_damage_factor = min(1.0, round(0.70 + (ws_above_300 * 0.02), 3))
            # Dodge chance reduction: each point above 300 reduces boss dodge by 0.1% (base 5.6% -> 5.1% at 305)
            effective_dodge = max(0.0, 0.056 - (ws_above_300 * 0.001))
            # Base miss chance against level 63 boss (8.0% - ws_hit_bonus - gear/talent hit)
            effective_miss = max(0.0, 0.08 - (ws_hit_bonus / 100.0) - (melee_hit / 100.0))
            glance_chance = 0.40
            boss_crit_suppression = 0.03

            # Special attacks hit rate (yellow attacks do not glance)
            special_hit_rate = max(0.0, 1.0 - effective_miss - effective_dodge)
            special_crit_rate = max(0.0, strike_crit_rate - boss_crit_suppression)
            strike_crit_factor = 1.0 + (crit_mult - 1.0) * special_crit_rate
            rs_mb_crit_rate = max(0.0, strike_crit_rate + unseen_path_strike_crit_bonus - boss_crit_suppression)
            rs_mb_crit_factor = 1.0 + (crit_mult - 1.0) * rs_mb_crit_rate

            # White swings hit table against Level 63 boss
            capped_white_crit = max(0.0, min(1.0 - effective_miss - glance_chance - effective_dodge, crit_rate - boss_crit_suppression))
            white_hit_chance = max(0.0, 1.0 - effective_miss - glance_chance - effective_dodge - capped_white_crit)
            white_damage_factor = white_hit_chance + (crit_mult * capped_white_crit) + (glance_damage_factor * glance_chance)

            # Vicious Strikes (Octo WoW: -0.5/1.0s CD and +5/10% damage on Raptor Strike & Mongoose Bite)
            vs_cd_reduction = (0.5 * vicious_strikes) if vicious_strikes > 0 else (0.2 * superior_strikes)
            vs_dmg_mult = 1.0 + (0.05 * vicious_strikes)

            # Off-hand damage bonus from Savage Strikes (+13/25% OH damage)
            oh_talent_mult = 0.5 * (1.0 + (0.125 * min(2, savage_strikes)))

            # Track GCDs (1.5s) across the priority queue so priority order determines filler casts
            total_gcds = fight_duration / 1.5
            remaining_gcds = total_gcds
            renataki_bonus_casts = (1 + int(max(0.0, fight_duration - 1.0) / 180.0)) if has_renataki_trinket else 0

            # Weapon swing consumption: Raptor Strike replaces the mainhand melee swing
            raptor_cd = max(3.0, 6.0 - vs_cd_reduction)
            max_raptor_from_cd = fight_duration / raptor_cd
            max_raptor_from_swings = max(1.0, mh_swings * 0.58)
            actual_raptor_casts = min(max_raptor_from_cd, max_raptor_from_swings) if "raptor_strike" in active_priority_list else 0.0

            for spell_key in active_priority_list:
                # 2.1 Raptor Strike (5.0s CD with Vicious Strikes 2/2, replaces MH swing)
                if spell_key == "raptor_strike":
                    ability_casts["raptor_strike"] = int(round(actual_raptor_casts))

                    raptor_bonus_dmg = 140.0
                    raptor_raw_hit = (mh_avg + (map_ap / 14.0) * mh_speed + raptor_bonus_dmg) * vs_dmg_mult
                    avg_raptor = raptor_raw_hit * (1.0 - armor_reduction) * slaying_mult * special_hit_rate * rs_mb_crit_factor
                    raptor_damage = (actual_raptor_casts * avg_raptor) + (1110.0 * slaying_mult if has_arcane_infused_gem else 0.0)
                    own_damage_breakdown["raptor_strike_dps"] = round(raptor_damage / fight_duration, 2)
                    own_damage_total += raptor_damage

                # 2.2 Mongoose Bite (4.0s CD with Vicious Strikes 2/2, 60% Wpn + 70, strikes with both weapons if DW)
                elif spell_key == "mongoose_bite":
                    mongoose_cd = max(2.5, 5.0 - vs_cd_reduction)
                    max_mongoose = min(remaining_gcds, fight_duration / mongoose_cd)
                    # In rotation with traps & weave, fires ~4.5 times in 30s
                    mongoose_count = min(remaining_gcds, max(1.0, max_mongoose * 0.60))
                    remaining_gcds = max(0.0, remaining_gcds - mongoose_count)
                    ability_casts["mongoose_bite"] = int(round(mongoose_count))

                    mh_mongoose_raw = 0.60 * (mh_avg + (map_ap / 14.0) * mh_speed) + 70.0
                    oh_mongoose_raw = 0.0
                    if is_dw and offhand_weapon:
                        oh_speed_mb = offhand_weapon.get("speed", 1.8)
                        oh_avg_mb = (offhand_weapon.get("min_damage", 50.0) + offhand_weapon.get("max_damage", 100.0)) / 2.0
                        oh_mongoose_raw = (0.60 * (oh_avg_mb + (map_ap / 14.0) * oh_speed_mb) + 70.0) * oh_talent_mult

                    mongoose_raw_hit = (mh_mongoose_raw + oh_mongoose_raw) * vs_dmg_mult
                    avg_mongoose = mongoose_raw_hit * (1.0 - armor_reduction) * slaying_mult * special_hit_rate * rs_mb_crit_factor
                    mongoose_damage = mongoose_count * avg_mongoose
                    own_damage_breakdown["mongoose_bite_dps"] = round(mongoose_damage / fight_duration, 2)
                    own_damage_total += mongoose_damage

                # 2.3 Carve (10.0s CD, 60-70% Weapon Damage sweeping strike, +4% PvP Gloves, +15% Giantstalker 8pc)
                elif spell_key == "carve":
                    carve_cd = 10.0
                    max_carve = (fight_duration / carve_cd) + renataki_bonus_casts
                    carve_count = min(remaining_gcds, max(1.0, max_carve * 0.67))
                    remaining_gcds = max(0.0, remaining_gcds - carve_count)
                    ability_casts["carve"] = int(round(carve_count))

                    carve_raw = 0.70 * (mh_avg + (map_ap / 14.0) * mh_speed) * multishot_carve_item_mult
                    avg_carve = carve_raw * (1.0 - armor_reduction) * slaying_mult * special_hit_rate * strike_crit_factor
                    carve_damage = carve_count * avg_carve
                    own_damage_breakdown["carve_dps"] = round(carve_damage / fight_duration, 2)
                    own_damage_total += carve_damage

                # 2.4 Immolation Trap (15.0s CD, Untamed Trapper Melee AP scaling + Trap Mastery +10/20/30% + Planning Ahead +13/25%)
                elif spell_key == "immolation_trap":
                    trap_cd = 15.0
                    max_traps = fight_duration / trap_cd
                    trap_count = min(remaining_gcds, max_traps)
                    remaining_gcds = max(0.0, remaining_gcds - trap_count)
                    ability_casts["immolation_trap"] = int(round(trap_count))

                    trap_ap_coeff = 0.38 if untamed_trapper > 0 else 0.30
                    trap_talent_mult = (1.0 + (0.10 * trap_mastery)) * (1.0 + (0.04 * planning_ahead))
                    raw_trap_dmg = (690.0 + (map_ap * trap_ap_coeff)) * trap_talent_mult * slaying_mult
                    immolation_damage = trap_count * raw_trap_dmg
                    own_damage_breakdown["immolation_trap_dps"] = round(immolation_damage / fight_duration, 2)
                    own_damage_total += immolation_damage

                # 2.5 Lacerate (Triggered after critical strike, 40% Melee AP + 20% Bleed over 8s)
                elif spell_key == "lacerate":
                    crit_proc_factor = min(1.0, max(0.20, special_crit_rate * 1.5))
                    max_lacerate = max(1.0, (fight_duration / 20.0) * crit_proc_factor * 2.0)
                    lacerate_count = min(remaining_gcds, max_lacerate)
                    remaining_gcds = max(0.0, remaining_gcds - lacerate_count)
                    ability_casts["lacerate"] = int(round(lacerate_count))

                    direct_lacerate = (0.35 * map_ap) * (1.0 - armor_reduction) * slaying_mult * special_hit_rate * strike_crit_factor
                    bleed_lacerate = (0.15 * (0.35 * map_ap)) * slaying_mult * special_hit_rate
                    lacerate_damage = lacerate_count * (direct_lacerate + bleed_lacerate)
                    own_damage_breakdown["lacerate_dps"] = round(lacerate_damage / fight_duration, 2)
                    own_damage_total += lacerate_damage

                # 2.6 Wing Clip (3.0s CD melee filler [-1.0s with Predator 3pc / PvP Set], 35% Wpn + 50, used as filler ~1 per 8.5s)
                elif spell_key == "wing_clip":
                    wc_cd = 2.0 if (has_predator_3pc or has_pvp_wing_clip_cd) else 3.0
                    max_wc = min(remaining_gcds, max(1.0, fight_duration / 8.5))
                    wc_count = min(remaining_gcds, max_wc)
                    remaining_gcds = max(0.0, remaining_gcds - wc_count)
                    ability_casts["wing_clip"] = int(round(wc_count))

                    wc_raw = 0.35 * (mh_avg + (map_ap / 14.0) * mh_speed) + 50.0
                    avg_wc = wc_raw * (1.0 - armor_reduction) * slaying_mult * special_hit_rate * strike_crit_factor
                    wc_damage = wc_count * avg_wc
                    own_damage_breakdown["wing_clip_dps"] = round(wc_damage / fight_duration, 2)
                    own_damage_total += wc_damage

                # 2.7 White Melee Swings (MH & OH Dual Wield, with Boss Glancing Blows)
                elif spell_key == "white_melee":
                    # Swings not replaced by Raptor Strike
                    effective_mh_white_swings = max(1.0, mh_swings - actual_raptor_casts)

                    raw_mh_hit = mh_avg + (map_ap / 14.0) * mh_speed
                    avg_mh_white = raw_mh_hit * (1.0 - armor_reduction) * slaying_mult * white_damage_factor
                    mh_white_damage = effective_mh_white_swings * avg_mh_white
                    own_damage_breakdown["white_melee_dps"] = round(mh_white_damage / fight_duration, 2)
                    own_damage_total += mh_white_damage
                    total_melee_swings += int(round(mh_swings))

                    # Dual Wield Off-Hand
                    if is_dw and offhand_weapon:
                        oh_speed = offhand_weapon.get("speed", 1.8)
                        oh_min = offhand_weapon.get("min_damage", 50.0)
                        oh_max = offhand_weapon.get("max_damage", 100.0)
                        oh_avg = (oh_min + oh_max) / 2.0
                        eff_oh_speed = oh_speed / (1.0 + melee_haste) if (1.0 + melee_haste) > 0 else oh_speed
                        oh_swings = fight_duration / eff_oh_speed if eff_oh_speed > 0 else 0.0

                        raw_oh_hit = (oh_avg + (map_ap / 14.0) * oh_speed) * oh_talent_mult
                        dw_effective_miss = max(0.0, 0.24 - (ws_hit_bonus / 100.0) - (melee_hit / 100.0))
                        dw_capped_white_crit = max(0.0, min(1.0 - dw_effective_miss - glance_chance - effective_dodge, crit_rate - boss_crit_suppression))
                        dw_white_hit_chance = max(0.0, 1.0 - dw_effective_miss - glance_chance - effective_dodge - dw_capped_white_crit)
                        dw_white_damage_factor = dw_white_hit_chance + (crit_mult * dw_capped_white_crit) + (glance_damage_factor * glance_chance)

                        avg_oh_white = raw_oh_hit * (1.0 - armor_reduction) * slaying_mult * dw_white_damage_factor
                        oh_white_damage = oh_swings * avg_oh_white
                        own_damage_breakdown["offhand_white_dps"] = round(oh_white_damage / fight_duration, 2)
                        own_damage_total += oh_white_damage
                        total_melee_swings += int(round(oh_swings))

            # 2.8 Stinging Nettle (Survival Row 4 Col 1: Mongoose Bite & Fire traps apply Serpent Sting for 20/40% duration)
            if stinging_nettle > 0:
                sn_triggers = ability_casts.get("mongoose_bite", 0) + ability_casts.get("immolation_trap", 0)
                if sn_triggers > 0:
                    sn_uptime = min(1.0, (sn_triggers * (15.0 * 0.20 * stinging_nettle)) / fight_duration)
                    sn_dps = 37.0 * (1.0 + (0.06 * imp_stings)) * slaying_mult * sn_uptime
                    sn_total = sn_dps * fight_duration
                    own_damage_breakdown["serpent_sting_dps"] = round(sn_dps, 2)
                    own_damage_total += sn_total

        # -------------------------------------------------------------
        # 3. BEAST MASTERY SPEC (Octo WoW Raid Rotation: Auto Shot <-> Steady Shot 1:1,
        #    Kill Command, Strike Together [Coordinated Assault], Arcane Shot, Serpent Sting)
        # -------------------------------------------------------------
        elif active_spec == "beast_mastery" and fight_duration > 0:
            # 3.1 Bestial Wrath (Spell 19574: 90.0s CD, 18.0s duration, grants Scent of Blood +40% pet damage)
            if "bestial_wrath" in active_priority_list:
                bw_casts = 1 + int(max(0.0, fight_duration - 1.0) / 90.0)
                ability_casts["bestial_wrath"] = bw_casts
                bw_active_ratio = min(fight_duration, bw_casts * 18.0) / fight_duration

            if has_ranged:
                rw_speed = ranged_weapon.get("speed", 2.8)
                rw_min = ranged_weapon.get("min_damage", 0.0)
                rw_max = ranged_weapon.get("max_damage", 0.0)
                avg_rw_dmg = (rw_min + rw_max) / 2.0

                rw_mult = 1.0 + (0.02 * ranged_weapon_spec)
                imp_mm_mult = 1.0 + (0.05 * imp_marksmanship)
                ranged_crit_mult = 2.0 + (0.06 * mortal_shots) + (0.01 * imp_slaying)
                # 3% crit suppression against Level 63 Raid Boss
                ranged_crit_rate = min(1.0, max(0.01, (ranged_crit - 3.0) / 100.0))
                piercing_bleed_mult = 1.0 + ((0.15 * piercing_shots) * ranged_crit_rate)

                total_ranged_haste = (
                    (haste_percent / 100.0)
                    + (quiver_haste / 100.0)
                    + (gear.get("haste", 0.0) / 100.0)
                    + troll_haste
                    + swift_aspects_ranged_haste
                    + swift_reflexes_haste
                    + (0.40 * rf_uptime)
                )
                haste_div = max(0.1, 1.0 + total_ranged_haste)
                eff_ranged_speed = rw_speed / haste_div
                auto_windup = 0.5 / haste_div
                steady_cast_dur = 1.5 / haste_div
                steady_pair_dur = max(eff_ranged_speed, auto_windup + steady_cast_dur)

                renataki_bonus_casts = (1 + int(max(0.0, fight_duration - 1.0) / 180.0)) if has_renataki_trinket else 0

                # 1:1 Auto Shot <-> Steady Shot alternating cycle count
                base_auto_shots = fight_duration / (steady_pair_dur if "steady_shot" in active_priority_list else eff_ranged_speed)
                remaining_weave_slots = float(int(round(base_auto_shots)))

                for spell_key in active_priority_list:
                    # 3.2 Serpent Sting (Maintained DoT: 1 cast per 15s, 5 ticks per cast)
                    if spell_key == "serpent_sting" and remaining_weave_slots > 0:
                        max_serpent = max(1, int(round(fight_duration / 15.0)))
                        serpent_casts = int(round(min(remaining_weave_slots, float(max_serpent))))
                        # Instant DoT refresh displaces ~0.5 of a Steady Shot weave window
                        remaining_weave_slots = max(0.0, remaining_weave_slots - (serpent_casts * 0.5))
                        ability_casts["serpent_sting"] = serpent_casts
                        pred_sting_mult = 1.25 if has_predator_5pc else 1.0
                        strikers_venom_dps = 8.33 if has_strikers_3pc else 0.0
                        serpent_uptime = min(1.0, (serpent_casts * 15.0) / fight_duration)
                        serpent_dps = ((37.0 * (1.0 + (0.06 * imp_stings)) * pred_sting_mult) + strikers_venom_dps) * slaying_mult * ranged_hit_rate * serpent_uptime
                        serpent_total = serpent_dps * fight_duration
                        own_damage_breakdown["serpent_sting_dps"] = round(serpent_dps, 2)
                        own_damage_total += serpent_total

                    # 3.3 Steady Shot (Spell 45974 Rank 8: 1.5s cast, 100% normalized weapon dmg + 125, woven 1:1 with Auto Shot)
                    elif spell_key == "steady_shot" and remaining_weave_slots > 0:
                        # Reserve ~2 instant weave windows per 18 Auto Shots if Arcane Shot is queued after Steady Shot
                        arcane_queued_after = (
                            "arcane_shot" in active_priority_list
                            and active_priority_list.index("arcane_shot") > active_priority_list.index("steady_shot")
                        )
                        reserved_for_arcane = min(remaining_weave_slots * 0.12, fight_duration / 18.0) if arcane_queued_after else 0.0
                        steady_casts = int(round(max(0.0, remaining_weave_slots - reserved_for_arcane)))
                        remaining_weave_slots = max(0.0, remaining_weave_slots - steady_casts)
                        ability_casts["steady_shot"] = steady_casts

                        steady_crit_rate = min(1.0, ranged_crit_rate + unseen_path_strike_crit_bonus)
                        bm_steady_mult = (
                            (1.0 - armor_reduction)
                            * slaying_mult
                            * rw_mult
                            * imp_mm_mult
                            * ranged_hit_rate
                            * (1.0 + (ranged_crit_mult - 1.0) * steady_crit_rate)
                            * piercing_bleed_mult
                        )
                        raw_steady = avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * rw_speed) + 125.0
                        steady_total = steady_casts * (raw_steady * bm_steady_mult)
                        ammo_damage_total += steady_casts * ((ammo_dps * rw_speed) * bm_steady_mult)
                        own_damage_breakdown["steady_shot_dps"] = round(steady_total / fight_duration, 2)
                        own_damage_total += steady_total

                    # 3.4 Arcane Shot (Spell 14287: 6.0s CD, 45% ranged weapon damage + 166 Arcane damage)
                    elif spell_key == "arcane_shot" and remaining_weave_slots > 0:
                        arcane_cd = max(4.5, 6.0 - (0.5 * swiftshot))
                        # Instant shot woven in gaps (~2 casts per weave slot)
                        max_arcane = int(round(fight_duration / (9.0 if "steady_shot" in active_priority_list else arcane_cd))) + renataki_bonus_casts
                        arcane_casts = int(round(min(remaining_weave_slots * 2.0, float(max_arcane))))
                        remaining_weave_slots = max(0.0, remaining_weave_slots - (arcane_casts * 0.5))
                        if arcane_casts > 0:
                            ability_casts["arcane_shot"] = arcane_casts
                            raw_arcane_wpn = 0.45 * (avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * rw_speed)) * (1.0 - armor_reduction) * rw_mult
                            raw_arcane_magic = 166.0 + (gear["spell_power"] * 0.15)
                            arcane_shot_mult = slaying_mult * ranged_hit_rate * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                            avg_arcane_hit = (raw_arcane_wpn + raw_arcane_magic) * arcane_shot_mult
                            arcane_total = (arcane_casts * avg_arcane_hit) + (1110.0 * slaying_mult if has_arcane_infused_gem else 0.0)
                            ammo_damage_total += arcane_casts * (0.45 * (ammo_dps * rw_speed) * (1.0 - armor_reduction) * rw_mult * arcane_shot_mult)
                            own_damage_breakdown["arcane_shot_dps"] = round(arcane_total / fight_duration, 2)
                            own_damage_total += arcane_total

                    # 3.5 Optional Multi-Shot if enabled
                    elif spell_key == "multi_shot" and remaining_weave_slots > 0:
                        max_multi = int(round(fight_duration / 10.0)) + renataki_bonus_casts
                        multi_casts = int(round(min(remaining_weave_slots, float(max_multi))))
                        remaining_weave_slots = max(0.0, remaining_weave_slots - multi_casts)
                        ability_casts["multi_shot"] = multi_casts
                        barrage_mult = (1.0 + (0.05 * barrage)) * multishot_carve_item_mult
                        bm_multi_mult = (
                            (1.0 - armor_reduction)
                            * slaying_mult
                            * rw_mult
                            * barrage_mult
                            * ranged_hit_rate
                            * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                            * piercing_bleed_mult
                        )
                        raw_multi = avg_rw_dmg + (rap / 14.0) * 2.8 + (ammo_dps * rw_speed) + 150.0
                        multi_total = multi_casts * (raw_multi * bm_multi_mult)
                        ammo_damage_total += multi_casts * ((ammo_dps * rw_speed) * bm_multi_mult)
                        own_damage_breakdown["multi_shot_dps"] = round(multi_total / fight_duration, 2)
                        own_damage_total += multi_total

                # 3.6 Auto Shot (+ Endless Quiver 3/6% extra shot proc)
                if "auto_shot" in active_priority_list:
                    total_ranged_triggers = (
                        base_auto_shots
                        + ability_casts.get("arcane_shot", 0)
                        + ability_casts.get("steady_shot", 0)
                        + ability_casts.get("multi_shot", 0)
                    )
                    auto_shots_count = base_auto_shots + (total_ranged_triggers * (0.03 * endless_quiver))
                    ability_casts["auto_shot"] = int(round(auto_shots_count))
                    bm_auto_mult = (
                        (1.0 - armor_reduction)
                        * slaying_mult
                        * rw_mult
                        * ranged_hit_rate
                        * (1.0 + (ranged_crit_mult - 1.0) * ranged_crit_rate)
                    )
                    raw_auto_shot = avg_rw_dmg + (rap / 14.0) * rw_speed + (ammo_dps * rw_speed)
                    avg_auto_hit = raw_auto_shot * bm_auto_mult
                    auto_shot_damage = auto_shots_count * avg_auto_hit
                    ammo_damage_total += auto_shots_count * ((ammo_dps * rw_speed) * bm_auto_mult)
                    own_damage_breakdown["auto_shot_dps"] = round(auto_shot_damage / fight_duration, 2)
                    own_damage_total += auto_shot_damage

        own_dps = own_damage_total / fight_duration if fight_duration > 0 else 0.0

        # -------------------------------------------------------------
        # 4. OCTO WOW PET SYSTEM & CUSTOM PET ABILITIES (Spell.dbc)
        # -------------------------------------------------------------
        pet_dps = 0.0
        pet_damage_total = 0.0
        minion_damage_breakdown = {}

        family_cfg = {
            "raptor": {
                "name": "Raptor (Octo)",
                "dmg_mod": 1.10,
                "base_speed": 2.0,
                "skills": ["Savage Rend (Rank 6: 27-36 + 80 Bleed / 5s)", "Bite (Rank 8)", "Claw (Rank 8)"],
            },
            "wind_serpent": {
                "name": "Wind Serpent (Wąż Wiatru)",
                "dmg_mod": 1.07,
                "base_speed": 2.0,
                "skills": ["Lightning Breath (Rank 6: 99-113 Nature)", "Bite (Rank 8)"],
            },
            "serpent": {
                "name": "Serpent (Wąż - Octo)",
                "dmg_mod": 1.00,
                "base_speed": 2.0,
                "skills": ["Poison Spit (Rank 3: 140 Nature / 8s)", "Bite (Rank 8)"],
            },
            "wolf": {
                "name": "Wolf (Wilk)",
                "dmg_mod": 1.00,
                "base_speed": 1.5,
                "skills": ["Furious Howl (Rank 4: +45-57 Dmg Buff)", "Bite (Rank 8)"],
            },
        }
        pet_info = family_cfg.get(chosen_pet, family_cfg["raptor"])
        gear_pet_dmg_pct = float(gear.get("pet_dmg_percent", 0.0))
        gear_pet_crit_pct = float(gear.get("pet_crit", 0.0))
        gear_pet_ap_bonus = int(gear.get("pet_ap_bonus", 0))
        gear_pet_focus_bonus = float(gear.get("pet_focus_regen_bonus", 0.0))
        active_pet_bonuses = list(gear.get("pet_effects", []))
        if is_orc:
            active_pet_bonuses.append("Orc Command (Racial): +5% Pet Damage")
        if has_black_book:
            active_pet_bonuses.append("The Black Book (Trinket): +50% Pet Damage (30s / 5m CD)")
        pet_total_crit_pct = round(5.0 + (3.0 * ferocity) + gear_pet_crit_pct, 1)
        pet_final_ap = 0

        if pet_active and fight_duration > 0:
            pet_dmg_mult = pet_info["dmg_mod"]
            # Unleashed Fury in Octo WoW: +4/8/12/16/20% pet damage
            pet_dmg_mult *= (1.0 + (0.04 * unleashed_fury))
            # Bestial Precision (+4/8% physical hit, +9/18% spell hit, +5/10 weapon skill)
            pet_dmg_mult *= (1.0 + (0.03 * bestial_precision))
            # Orc Command racial: +5% pet damage
            if is_orc:
                pet_dmg_mult *= 1.05
            # Equipped Items & Set Bonuses Pet Damage (e.g. Ancient Cornerstone Grimoire +5%, Beastmaster's Boots +3%,
            # Ferra's Collar +4%, Charm of Dark Domination +3%, Breastplate of Beast Mastery +3%, Trappings of the Unseen Path +3%)
            if gear_pet_dmg_pct > 0:
                pet_dmg_mult *= (1.0 + (gear_pet_dmg_pct / 100.0))
            # The Black Book (ID 19337: +50% pet damage for 30s on 300s CD)
            if has_black_book:
                bb_casts = 1 + int(max(0.0, fight_duration - 1.0) / 300.0)
                bb_uptime = min(fight_duration, bb_casts * 30.0) / fight_duration
                pet_dmg_mult *= (1.0 + (0.50 * bb_uptime))

            # Scent of Blood (5/10/15% chance on Hunter attacks to grant +40% pet damage for 8s) & Bestial Wrath (18s of Scent of Blood)
            sob_proc_uptime = min(0.85, (0.05 * scent_of_blood) * 3.2) if scent_of_blood > 0 else 0.0
            if active_spec == "beast_mastery" and "bestial_wrath" in active_priority_list:
                combined_sob_uptime = min(1.0, bw_active_ratio + sob_proc_uptime * (1.0 - bw_active_ratio))
            elif bestial_wrath_talent > 0:
                bw_r = min(fight_duration, 18.0) / fight_duration
                combined_sob_uptime = min(1.0, bw_r + sob_proc_uptime * (1.0 - bw_r))
            else:
                combined_sob_uptime = sob_proc_uptime
            pet_dmg_mult *= (1.0 + (0.40 * combined_sob_uptime))

            # Pet Critical Strike Chance: Base 5% + Ferocity (+3/6/9/12/15%) + Gear Pet Crit (Beastmaster's Gloves +2%, Breastplate of BM +2%, Deathmist Wraps +2%)
            pet_base_crit = 0.05 + (0.03 * ferocity) + (gear_pet_crit_pct / 100.0)

            # Frenzy (+30% attack speed for 8s after crit)
            frenzy_uptime = min(1.0, pet_base_crit * (frenzy / 5.0) * (8.0 / pet_info["base_speed"])) if frenzy > 0 else 0.0
            eff_pet_speed = pet_info["base_speed"] / (1.0 + (0.30 * frenzy_uptime))

            # Spirit Bond in Octo WoW: pet gains melee AP equal to 12/25% of RAP and spell power equal to 7/15% of RAP
            sb_ap_bonus = rap * (0.125 * spirit_bond)
            pet_sp = rap * (0.075 * spirit_bond)
            pet_ap = 300.0 + (max(rap, map_ap) * 0.22) + sb_ap_bonus + gear_pet_ap_bonus
            pet_final_ap = int(round(pet_ap))
            pet_swings = fight_duration / eff_pet_speed

            # 4.1 Pet White Melee Swings
            raw_pet_swing = (pet_ap / 14.0) * pet_info["base_speed"]
            avg_pet_white = raw_pet_swing * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
            pet_white_total = pet_swings * avg_pet_white
            minion_damage_breakdown["pet_melee_dps"] = round(pet_white_total / fight_duration, 2)
            pet_damage_total += pet_white_total
            ability_casts["pet_swings"] = int(round(pet_swings))

            # Strike Together / Coordinated Assault (Spell 49557 / 49559: Arcane Shot, Steady Shot, or Raptor Strike
            # causes pet's next attack within 6s to strike for Physical damage equal to 20% of Hunter AP, 3.0s ICD)
            st_enabled = (
                ("strike_together" in active_priority_list or coordinated_assault > 0)
                if active_spec == "beast_mastery"
                else (coordinated_assault > 0)
            )
            if st_enabled and (active_spec != "beast_mastery" or "strike_together" in active_priority_list):
                ca_triggers = (
                    ability_casts.get("arcane_shot", 0)
                    + ability_casts.get("steady_shot", 0)
                    + ability_casts.get("raptor_strike", 0)
                )
                ca_procs = min(fight_duration / 4.0, float(ca_triggers))
                if ca_procs > 0:
                    hunter_ap_for_ca = map_ap if active_style == "melee" else rap
                    ca_hit = (0.20 * hunter_ap_for_ca) * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                    ca_total = ca_procs * ca_hit
                    minion_damage_breakdown["pet_coordinated_assault_dps"] = round(ca_total / fight_duration, 2)
                    pet_damage_total += ca_total
                    ability_casts["pet_coordinated_assault"] = int(round(ca_procs))

            # Kill Command (Spell 41827: 8.0s CD, instant pet attack for 80% of Pet AP after Hunter critical strike)
            kc_enabled = (
                ("kill_command" in active_priority_list)
                if active_spec == "beast_mastery"
                else (kill_command_talent > 0)
            )
            if kc_enabled:
                hunter_crit_r = min(1.0, max(0.05, ((melee_crit if active_style == "melee" else ranged_crit) - 3.0) / 100.0))
                kc_eff_cd = max(8.0, 8.0 + (1.2 / max(0.08, hunter_crit_r)))
                kc_procs = fight_duration / kc_eff_cd
                kc_hit = (raw_pet_swing + (0.80 * pet_ap)) * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                kc_total = kc_procs * kc_hit
                minion_damage_breakdown["pet_kill_command_dps"] = round(kc_total / fight_duration, 2)
                pet_damage_total += kc_total
                ability_casts["pet_kill_command"] = max(1, int(round(kc_procs)))

            # 4.2 Pet Focus Abilities (exact Octo WoW patch-O.mpq_Spell.dbc data)
            focus_allowed = (active_spec != "beast_mastery") or ("pet_focus_dump" in active_priority_list)
            if focus_allowed:
                # Bestial Discipline (Octo WoW: +2/5 Focus per 4s tick [base 20 -> 22/25] + Trappings of the Unseen Path 3pc [+2 Focus/tick] and -10/20% special ability CD)
                bd_focus_bonus_per_tick = {0: 0.0, 1: 2.0}.get(bestial_discipline, 5.0 if bestial_discipline >= 2 else 0.0) + gear_pet_focus_bonus
                focus_regen_per_sec = (20.0 + bd_focus_bonus_per_tick) / 4.0
                total_focus = 100.0 + (focus_regen_per_sec * fight_duration)
                special_cd_mult = max(0.80, 1.0 - (0.10 * bestial_discipline))

                if chosen_pet == "raptor":
                    # Savage Rend (Rank 6, ID 36541): 35 Focus, 10s CD (reduced by Bestial Discipline),
                    # 27..36 (avg 31.5) physical hit + 16 bleed per 1s for 5s = 80 bleed (+1s / +16 bleed on crit)
                    sr_cd = 10.0 * special_cd_mult
                    sr_casts = fight_duration / sr_cd
                    raw_sr_direct = (31.5 + (pet_ap * 0.08)) * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                    raw_sr_bleed = (80.0 + (pet_ap * 0.15)) * pet_dmg_mult * (1.0 + (0.20 * pet_base_crit))
                    sr_total = sr_casts * (raw_sr_direct + raw_sr_bleed)
                    minion_damage_breakdown["pet_savage_rend_dps"] = round(sr_total / fight_duration, 2)
                    pet_damage_total += sr_total
                    ability_casts["pet_savage_rend"] = int(round(sr_casts))

                    rem_focus = max(0.0, total_focus - (sr_casts * 35.0))
                    # Bite (Rank 8, ID 17261): 35 Focus, 6s CD, 81..99 (avg 90.0) physical dmg
                    bite_count = min(fight_duration / 6.0, rem_focus / 35.0)
                    raw_bite = 90.0 + (pet_ap * 0.10)
                    bite_total = bite_count * raw_bite * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                    if bite_total > 0:
                        minion_damage_breakdown["pet_bite_dps"] = round(bite_total / fight_duration, 2)
                        pet_damage_total += bite_total
                        ability_casts["pet_bites"] = int(round(bite_count))

                    rem_focus_claw = max(0.0, rem_focus - (bite_count * 35.0))
                    # Claw (Rank 8, ID 3009): 25 Focus, 0s CD, 43..59 (avg 51.0) physical dmg
                    claw_count = rem_focus_claw / 25.0
                    if claw_count > 0:
                        raw_claw = 51.0 + (pet_ap * 0.08)
                        claw_total = claw_count * raw_claw * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                        minion_damage_breakdown["pet_claw_dps"] = round(claw_total / fight_duration, 2)
                        pet_damage_total += claw_total
                        ability_casts["pet_claws"] = int(round(claw_count))

                elif chosen_pet == "wind_serpent":
                    # Lightning Breath (Rank 6, ID 25012): 50 Focus, 0s CD, 99..113 (avg 106.0) Nature dmg, ignores armor
                    lb_count = total_focus / 50.0
                    raw_lb = 106.0 + (pet_ap * 0.12) + (pet_sp * 0.4285)
                    avg_lb = raw_lb * pet_dmg_mult * (1.0 + pet_base_crit)
                    lb_total = lb_count * avg_lb
                    minion_damage_breakdown["pet_lightning_breath_dps"] = round(lb_total / fight_duration, 2)
                    pet_damage_total += lb_total
                    ability_casts["pet_lightning_breath"] = int(round(lb_count))

                elif chosen_pet == "serpent":
                    # Poison Spit (Rank 3, ID 46273): 35 Focus, 8s CD (reduced by Bestial Discipline),
                    # 35 Nature dmg every 2s for 8s = 140 Nature DoT (ignores armor) + Bite (Rank 8)
                    ps_cd = 8.0 * special_cd_mult
                    ps_casts = fight_duration / ps_cd
                    raw_ps = (140.0 + (pet_ap * 0.12) + (pet_sp * 0.80)) * pet_dmg_mult
                    ps_total = ps_casts * raw_ps
                    minion_damage_breakdown["pet_poison_spit_dps"] = round(ps_total / fight_duration, 2)
                    pet_damage_total += ps_total
                    ability_casts["pet_poison_spit"] = int(round(ps_casts))

                    rem_focus = max(0.0, total_focus - (ps_casts * 35.0))
                    bite_count = min(fight_duration / 6.0, rem_focus / 35.0)
                    raw_bite = 90.0 + (pet_ap * 0.10)
                    bite_total = bite_count * raw_bite * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                    minion_damage_breakdown["pet_bite_dps"] = round(bite_total / fight_duration, 2)
                    pet_damage_total += bite_total
                    ability_casts["pet_bites"] = int(round(bite_count))

                elif chosen_pet == "wolf":
                    # Furious Howl (Rank 4, ID 24597): 50 Focus, 10s CD (reduced by Bestial Discipline),
                    # party members within 15 yd receive an extra 45..57 (avg 51.0) physical dmg on next attack + Bite (Rank 8)
                    howl_cd = 10.0 * special_cd_mult
                    howl_count = fight_duration / howl_cd
                    raw_howl = 51.0 + (pet_ap * 0.07)
                    howl_hunter_bonus = raw_howl * (1.0 - armor_reduction) * slaying_mult
                    howl_wolf_bonus = raw_howl * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                    howl_total = howl_count * (howl_hunter_bonus + howl_wolf_bonus)
                    minion_damage_breakdown["furious_howl_bonus_dps"] = round(howl_total / fight_duration, 2)
                    pet_damage_total += howl_total
                    ability_casts["furious_howl"] = int(round(howl_count))

                    rem_focus = max(0.0, total_focus - (howl_count * 50.0))
                    bite_count = min(fight_duration / 6.0, rem_focus / 35.0)
                    raw_bite = 90.0 + (pet_ap * 0.10)
                    bite_total = bite_count * raw_bite * (1.0 - armor_reduction) * pet_dmg_mult * (1.0 + pet_base_crit)
                    minion_damage_breakdown["pet_bite_dps"] = round(bite_total / fight_duration, 2)
                    pet_damage_total += bite_total
                    ability_casts["pet_bites"] = int(round(bite_count))

            pet_dps = pet_damage_total / fight_duration

        total_dps = own_dps + pet_dps
        total_damage = own_damage_total + pet_damage_total

        primary_weapon = mainhand_weapon if (active_style == "melee" and mainhand_weapon) else (ranged_weapon if active_style == "ranged" else mainhand_weapon)
        prim_name = primary_weapon.get("name", "Brak broni") if primary_weapon else ("Brak broni dystansowej" if active_style == "ranged" else "Brak broni białej")
        prim_speed = primary_weapon.get("speed", 0.0) if primary_weapon else 0.0

        # Build detailed damage sources for breakdown table
        damage_sources = []
        safe_total = max(0.001, total_dps)

        source_defs = [
            ("raptor_strike_dps", "Raptor Strike", "Survival Melee", "#c9a227", "raptor_strike"),
            ("mongoose_bite_dps", "Mongoose Bite", "Survival Melee", "#40c7eb", "mongoose_bite"),
            ("carve_dps", "Carve", "Survival Melee", "#f59e0b", "carve"),
            ("immolation_trap_dps", "Immolation Trap", "Trap / Fire", "#ff5533", "immolation_trap"),
            ("lacerate_dps", "Lacerate", "Survival Bleed", "#ef4444", "lacerate"),
            ("wing_clip_dps", "Wing Clip", "Survival Melee", "#a38249", "wing_clip"),
            ("white_melee_dps", "Main Hand Auto Attack", "White Melee", "#e0e0e0", "white_melee"),
            ("offhand_white_dps", "Off Hand Auto Attack", "White Melee", "#b0b0b0", "white_melee"),
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
                ("pet_melee_dps", f"Auto Attack (by Pet {pet_info['name']})", "Pet Melee", "#e6cc80", "pet_focus_dump"),
                ("pet_kill_command_dps", f"Kill Command (by Pet {pet_info['name']})", "Pet Skill", "#fb7185", "kill_command"),
                ("pet_coordinated_assault_dps", "Strike Together (Coordinated Assault)", "Pet Skill", "#38bdf8", "strike_together"),
                ("pet_claw_dps", f"Claw (by Pet {pet_info['name']})", "Pet Skill", "#ffaa00", "pet_focus_dump"),
                ("pet_bite_dps", f"Bite (by Pet {pet_info['name']})", "Pet Skill", "#d9534f", "pet_focus_dump"),
                ("pet_savage_rend_dps", "Savage Rend (by Pet Raptor)", "Pet Bleed", "#ef4444", "pet_focus_dump"),
                ("pet_lightning_breath_dps", "Lightning Breath (by Pet Wind Serpent)", "Pet Nature", "#33ccff", "pet_focus_dump"),
                ("pet_poison_spit_dps", "Poison Spit (by Pet Serpent)", "Pet Nature", "#4ade80", "pet_focus_dump"),
                ("furious_howl_bonus_dps", "Furious Howl (Hunter & Pet Buff)", "Pet Buff", "#f59e0b", "pet_focus_dump"),
            ]
            for key, name, cat, col, sp_key in pet_source_defs:
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
                        "spell_key": sp_key,
                        "is_minion": True,
                        "is_proc": False,
                    })

        magic_dps = (
            own_damage_breakdown.get("immolation_trap_dps", 0.0)
            + own_damage_breakdown.get("serpent_sting_dps", 0.0)
            + own_damage_breakdown.get("arcane_shot_dps", 0.0)
            + minion_damage_breakdown.get("pet_lightning_breath_dps", 0.0)
            + minion_damage_breakdown.get("pet_poison_spit_dps", 0.0)
        )
        phys_dps = max(0.0, total_dps - magic_dps)

        damage_type_breakdown = {
            "physical_dps": round(phys_dps, 2),
            "physical_percent": round((phys_dps / safe_total) * 100.0, 1),
            "magic_spell_dps": round(magic_dps, 2),
            "magic_spell_percent": round((magic_dps / safe_total) * 100.0, 1),
            "pet_dps": round(pet_dps, 2),
            "pet_percent": round((pet_dps / safe_total) * 100.0, 1),
            # Backwards-compatibility aliases for shared UI components
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

        if active_style == "melee":
            final_eff_ws = eff_ws if "eff_ws" in locals() else gear.get("effective_weapon_skill", 300)
            final_ws_hit = ws_hit_bonus if "ws_hit_bonus" in locals() else gear.get("weapon_skill_hit_bonus", 0.0)
            final_glance_fac = glance_damage_factor if "glance_damage_factor" in locals() else gear.get("glance_damage_factor", 0.70)
        else:
            final_eff_ws = 300 + ranged_ws_bonus
            final_ws_hit = ranged_ws_hit_bonus
            final_glance_fac = 1.0

        return {
            "character_class": "hunter",
            "hunter_spec": active_spec,
            "hunter_spec_name": spec_names.get(active_spec, active_spec.capitalize()),
            "combat_style": active_style,
            "combat_style_name": spec_names.get(active_spec, active_spec.capitalize()),
            "priority_list": active_priority_list,
            "use_rapid_fire": use_rapid_fire,
            "rapid_fire_uptime": round(rf_uptime * 100.0, 1),
            "fight_duration": fight_duration,
            "weapon_name": prim_name,
            "base_weapon_speed": prim_speed,
            "effective_weapon_speed": round(eff_ranged_speed if active_style == "ranged" else eff_mh_speed, 2),
            "exact_melee_swings": total_melee_swings if active_style == "melee" else ability_casts.get("auto_shot", 0),
            "class_warnings": gear.get("class_warnings", []),
            "total_attack_power": map_ap if active_style == "melee" else rap,
            "melee_attack_power": map_ap,
            "ranged_attack_power": rap,
            "total_spell_power": gear["spell_power"],
            "healing_power": gear["healing"],
            "total_crit_percent": round(melee_crit if active_style == "melee" else ranged_crit, 2),
            "melee_crit_percent": round(melee_crit, 2),
            "ranged_crit_percent": round(ranged_crit, 2),
            "total_hit_percent": round(melee_hit if active_style == "melee" else ranged_hit, 2),
            "effective_weapon_skill": final_eff_ws,
            "weapon_skill": final_eff_ws,
            "weapon_skill_hit_bonus": final_ws_hit,
            "glance_damage_factor": final_glance_fac,
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
                "gear_pet_dmg_percent": gear_pet_dmg_pct + (5.0 if is_orc else 0.0),
                "gear_pet_crit_percent": gear_pet_crit_pct,
                "total_pet_crit_percent": pet_total_crit_pct,
                "pet_ap": pet_final_ap,
                "orc_command_active": is_orc,
                "active_pet_bonuses": active_pet_bonuses,
            },
            "ammo_details": {
                "key": chosen_ammo,
                "name": ammo_info["name"],
                "dps": ammo_dps,
                "bonus_per_shot": round(ammo_dps * ranged_weapon.get("speed", 0.0), 1) if has_ranged else 0.0,
                "contribution_dps": round((ammo_damage_total / fight_duration) if fight_duration > 0 else 0.0, 2),
                "active_in_spec": active_style == "ranged" and has_ranged,
            },
            "total_dps": round(total_dps, 2),
            "total_damage": round(total_damage, 2),
            "map_ap": map_ap,
            "rap": rap,
            "melee_crit": round(melee_crit, 2),
            "ranged_crit": round(ranged_crit, 2),
            "melee_hit": round(melee_hit, 2),
            "ranged_hit": round(ranged_hit, 2),
            "active_onuse_trinkets": active_onuse_trinkets,
            "chosen_aspect": chosen_aspect,
            "has_trueshot_aura": has_trueshot_aura,
            "gear_summary": {
                "raw_attack_power": gear["attack_power"],
                "ranged_attack_power": rap,
                "melee_attack_power": map_ap,
                "melee_crit": round(melee_crit, 2),
                "ranged_crit": round(ranged_crit, 2),
                "melee_hit": round(melee_hit, 2),
                "ranged_hit": round(ranged_hit, 2),
                "strength": gear["strength"],
                "agility": gear["agility"],
                "stamina": gear["stamina"],
                "intellect": gear["intellect"],
                "armor": gear["armor"],
                "total_armor": gear.get("total_armor", gear["armor"] + int(gear["agility"] * 2)),
                "effective_weapon_skill": final_eff_ws,
                "weapon_skill_hit_bonus": final_ws_hit,
                "glance_damage_factor": final_glance_fac,
                "equipped_count": len(gear["equipped_items"]),
                "active_onuse_trinkets": active_onuse_trinkets,
                "chosen_aspect": chosen_aspect,
                "has_trueshot_aura": has_trueshot_aura,
            },
        }
