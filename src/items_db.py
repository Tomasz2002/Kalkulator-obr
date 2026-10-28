import json
import os
import re
from typing import Any, Dict, List, Optional, Union

WEAPON_SKILL_PATTERNS = [
    (re.compile(r'increased\s+two-handed\s+swords\s*\+(\d+)', re.I), 'two_hand_sword'),
    (re.compile(r'increased\s+two-handed\s+maces\s*\+(\d+)', re.I), 'two_hand_mace'),
    (re.compile(r'increased\s+two-handed\s+axes\s*\+(\d+)', re.I), 'two_hand_axe'),
    (re.compile(r'increased\s+swords\s*\+(\d+)', re.I), 'sword'),
    (re.compile(r'increased\s+maces\s*\+(\d+)', re.I), 'mace'),
    (re.compile(r'increased\s+axes\s*\+(\d+)', re.I), 'axe'),
    (re.compile(r'increased\s+daggers\s*\+(\d+)', re.I), 'dagger'),
    (re.compile(r'increased\s+polearms\s*\+(\d+)', re.I), 'polearm'),
    (re.compile(r'increased\s+fist\s+weapons\s*\+(\d+)', re.I), 'fist'),
    (re.compile(r'increased\s+bows\s*\+(\d+)', re.I), 'bow'),
    (re.compile(r'increased\s+guns\s*\+(\d+)', re.I), 'gun'),
    (re.compile(r'increased\s+crossbows\s*\+(\d+)', re.I), 'crossbow'),
    (re.compile(r'increased\s+defense\s*\+(\d+)', re.I), 'defense'),
]


CLASS_EQUIPMENT_RULES = {
    "paladin": {
        "name": "Paladin",
        "can_dual_wield": False,
        "dual_wield_allowed": False,
        "valid_offhand_subclasses": ["shield", "misc"],
        "valid_relic_subclasses": ["libram"],
        "can_use_relic": True,
        "can_use_ranged": False,
        "valid_ranged_subclasses": [],
        "valid_armor_subclasses": ["cloth", "leather", "mail", "plate", "shield", "misc"],
        "valid_weapon_subclasses": [
            "one_hand_mace", "two_hand_mace",
            "one_hand_sword", "two_hand_sword",
            "one_hand_axe", "two_hand_axe",
            "polearm"
        ],
    },
    "warrior": {
        "name": "Warrior",
        "can_dual_wield": True,
        "dual_wield_allowed": True,
        "valid_offhand_subclasses": [
            "shield", "misc",
            "one_hand_sword", "one_hand_axe", "one_hand_mace", "dagger", "fist"
        ],
        "valid_relic_subclasses": [],
        "can_use_relic": False,
        "can_use_ranged": True,
        "valid_ranged_subclasses": ["bow", "gun", "crossbow", "thrown", "misc"],
        "valid_armor_subclasses": ["cloth", "leather", "mail", "plate", "shield", "misc"],
        "valid_weapon_subclasses": [
            "one_hand_mace", "two_hand_mace",
            "one_hand_sword", "two_hand_sword",
            "one_hand_axe", "two_hand_axe",
            "dagger", "fist", "polearm", "staff", "bow", "gun", "crossbow", "thrown"
        ],
    },
    "druid": {
        "name": "Druid",
        "can_dual_wield": False,
        "dual_wield_allowed": False,
        "valid_offhand_subclasses": ["misc"],
        "valid_relic_subclasses": ["idol"],
        "can_use_relic": True,
        "can_use_ranged": False,
        "valid_ranged_subclasses": [],
        "valid_armor_subclasses": ["cloth", "leather", "misc"],
        "valid_weapon_subclasses": ["one_hand_mace", "two_hand_mace", "dagger", "fist", "polearm", "staff"],
    },
    "shaman": {
        "name": "Shaman",
        "can_dual_wield": False,
        "dual_wield_allowed": False,
        "valid_offhand_subclasses": ["shield", "misc"],
        "valid_relic_subclasses": ["totem"],
        "can_use_relic": True,
        "can_use_ranged": False,
        "valid_ranged_subclasses": [],
        "valid_armor_subclasses": ["cloth", "leather", "mail", "shield", "misc"],
        "valid_weapon_subclasses": ["one_hand_mace", "two_hand_mace", "one_hand_axe", "two_hand_axe", "dagger", "fist", "staff"],
    },
    "rogue": {
        "name": "Rogue",
        "can_dual_wield": True,
        "dual_wield_allowed": True,
        "valid_offhand_subclasses": ["one_hand_sword", "one_hand_mace", "dagger", "fist", "misc"],
        "valid_relic_subclasses": [],
        "can_use_relic": False,
        "can_use_ranged": True,
        "valid_ranged_subclasses": ["bow", "gun", "crossbow", "thrown", "misc"],
        "valid_armor_subclasses": ["cloth", "leather", "misc"],
        "valid_weapon_subclasses": ["one_hand_sword", "one_hand_mace", "dagger", "fist", "bow", "gun", "crossbow", "thrown"],
    },
    "hunter": {
        "name": "Hunter",
        "can_dual_wield": True,
        "dual_wield_allowed": True,
        "valid_offhand_subclasses": ["one_hand_sword", "one_hand_axe", "dagger", "fist", "misc"],
        "valid_relic_subclasses": [],
        "can_use_relic": False,
        "can_use_ranged": True,
        "valid_ranged_subclasses": ["bow", "gun", "crossbow", "thrown", "misc"],
        "valid_armor_subclasses": ["cloth", "leather", "mail", "misc"],
        "valid_weapon_subclasses": ["one_hand_sword", "two_hand_sword", "one_hand_axe", "two_hand_axe", "dagger", "fist", "polearm", "staff", "bow", "gun", "crossbow"],
    },
    "priest": {
        "name": "Priest",
        "can_dual_wield": False,
        "dual_wield_allowed": False,
        "valid_offhand_subclasses": ["misc"],
        "valid_relic_subclasses": [],
        "can_use_relic": False,
        "can_use_ranged": True,
        "valid_ranged_subclasses": ["wand"],
        "valid_armor_subclasses": ["cloth", "misc"],
        "valid_weapon_subclasses": ["one_hand_mace", "dagger", "staff", "wand"],
    },
    "mage": {
        "name": "Mage",
        "can_dual_wield": False,
        "dual_wield_allowed": False,
        "valid_offhand_subclasses": ["misc"],
        "valid_relic_subclasses": [],
        "can_use_relic": False,
        "can_use_ranged": True,
        "valid_ranged_subclasses": ["wand"],
        "valid_armor_subclasses": ["cloth", "misc"],
        "valid_weapon_subclasses": ["one_hand_sword", "dagger", "staff", "wand"],
    },
    "warlock": {
        "name": "Warlock",
        "can_dual_wield": False,
        "dual_wield_allowed": False,
        "valid_offhand_subclasses": ["misc"],
        "valid_relic_subclasses": [],
        "can_use_relic": False,
        "can_use_ranged": True,
        "valid_ranged_subclasses": ["wand"],
        "valid_armor_subclasses": ["cloth", "misc"],
        "valid_weapon_subclasses": ["one_hand_sword", "dagger", "staff", "wand"],
    }
}

SUBCLASS_DISPLAY_NAMES = {
    "two_hand_sword": "Two-Handed Sword",
    "one_hand_sword": "One-Handed Sword",
    "sword": "Sword",
    "two_hand_mace": "Two-Handed Mace",
    "one_hand_mace": "One-Handed Mace",
    "mace": "Mace",
    "two_hand_axe": "Two-Handed Axe",
    "one_hand_axe": "One-Handed Axe",
    "axe": "Axe",
    "dagger": "Dagger",
    "fist": "Fist Weapon",
    "polearm": "Polearm",
    "staff": "Staff",
    "bow": "Bow",
    "gun": "Gun",
    "crossbow": "Crossbow",
    "thrown": "Thrown",
    "wand": "Wand",
    "shield": "Shield",
    "misc": "Misc",
}


def get_weapon_type_key(subclass: str, slot: str = "") -> str:
    s = (subclass or "").lower().strip()
    if "sword" in s: return "sword"
    if "mace" in s: return "mace"
    if "axe" in s: return "axe"
    if "dagger" in s: return "dagger"
    if "fist" in s: return "fist"
    if "polearm" in s: return "polearm"
    if "staff" in s: return "staff"
    if "bow" in s: return "bow"
    if "gun" in s: return "gun"
    if "crossbow" in s: return "crossbow"
    if "thrown" in s: return "thrown"
    return s


def compute_effective_weapon_skill(
    weapon_subclass: str,
    item_skills: Dict[str, int],
    racial_skills: Dict[str, int],
    talent_weapon_skill: int = 0,
    quest_bonus: int = 0
) -> int:
    base_skill = 300
    bonus = quest_bonus
    w_sub = (weapon_subclass or "").lower().strip()

    # 1. Talent bonus
    if w_sub in ("two_hand_sword", "two_hand_mace", "two_hand_axe", "twohand"):
        bonus += talent_weapon_skill

    # 2. Racial bonus
    if "sword" in w_sub:
        bonus += racial_skills.get("sword_skill", 0)
    elif "mace" in w_sub:
        bonus += racial_skills.get("mace_skill", 0)
    elif "axe" in w_sub:
        bonus += racial_skills.get("axe_skill", 0)
    elif "dagger" in w_sub:
        bonus += racial_skills.get("dagger_skill", 0)
    elif "bow" in w_sub:
        bonus += racial_skills.get("bow_skill", 0)
    elif "gun" in w_sub:
        bonus += racial_skills.get("gun_skill", 0)
    elif "crossbow" in w_sub:
        bonus += racial_skills.get("crossbow_skill", 0)

    # 3. Item weapon skill bonuses
    if w_sub == "two_hand_sword":
        bonus += item_skills.get("two_hand_sword", 0)
        bonus += item_skills.get("sword", 0)
    elif w_sub == "two_hand_mace":
        bonus += item_skills.get("two_hand_mace", 0)
        bonus += item_skills.get("mace", 0)
    elif w_sub == "two_hand_axe":
        bonus += item_skills.get("two_hand_axe", 0)
        bonus += item_skills.get("axe", 0)
    elif w_sub == "one_hand_sword":
        bonus += item_skills.get("sword", 0)
    elif w_sub == "one_hand_mace":
        bonus += item_skills.get("mace", 0)
    elif w_sub == "one_hand_axe":
        bonus += item_skills.get("axe", 0)
    elif w_sub in item_skills:
        bonus += item_skills.get(w_sub, 0)

    # Turtle / Octo WoW weapon skill cap is 315
    return min(315, base_skill + bonus)


def compute_weapon_skill_details(
    slot: str,
    item_name: str,
    subclass: str,
    item_skills: Dict[str, int],
    racial_skills: Dict[str, int],
    talent_weapon_skill: int = 0,
    quest_weapon_skills: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    base_skill = 300
    w_key = get_weapon_type_key(subclass, slot)
    quest_active = bool(quest_weapon_skills and (
        quest_weapon_skills.get(w_key) or
        quest_weapon_skills.get(subclass) or
        quest_weapon_skills.get(slot) or
        quest_weapon_skills.get(f"{slot}_{w_key}")
    ))
    quest_bonus = 5 if quest_active else 0

    racial_bonus = 0
    if "sword" in subclass: racial_bonus = racial_skills.get("sword_skill", 0)
    elif "mace" in subclass: racial_bonus = racial_skills.get("mace_skill", 0)
    elif "axe" in subclass: racial_bonus = racial_skills.get("axe_skill", 0)
    elif "dagger" in subclass: racial_bonus = racial_skills.get("dagger_skill", 0)
    elif "bow" in subclass: racial_bonus = racial_skills.get("bow_skill", 0)
    elif "gun" in subclass: racial_bonus = racial_skills.get("gun_skill", 0)
    elif "crossbow" in subclass: racial_bonus = racial_skills.get("crossbow_skill", 0)

    talent_bonus = 0
    if subclass in ("two_hand_sword", "two_hand_mace", "two_hand_axe", "twohand"):
        talent_bonus = talent_weapon_skill

    item_bonus = 0
    if subclass == "two_hand_sword":
        item_bonus = item_skills.get("two_hand_sword", 0) + item_skills.get("sword", 0)
    elif subclass == "two_hand_mace":
        item_bonus = item_skills.get("two_hand_mace", 0) + item_skills.get("mace", 0)
    elif subclass == "two_hand_axe":
        item_bonus = item_skills.get("two_hand_axe", 0) + item_skills.get("axe", 0)
    elif subclass == "one_hand_sword":
        item_bonus = item_skills.get("sword", 0)
    elif subclass == "one_hand_mace":
        item_bonus = item_skills.get("mace", 0)
    elif subclass == "one_hand_axe":
        item_bonus = item_skills.get("axe", 0)
    elif subclass in item_skills:
        item_bonus = item_skills.get(subclass, 0)

    raw_total = base_skill + racial_bonus + item_bonus + talent_bonus + quest_bonus
    skill = min(315, raw_total)
    skill_above = max(0, skill - 300)
    glance_factor = min(1.0, round(0.70 + (skill_above * 0.02), 3))
    hit_bonus = round((skill_above // 5) * 1.0, 1)

    return {
        "slot": slot,
        "item_name": item_name or "Unarmed",
        "subclass": subclass,
        "weapon_type_key": w_key,
        "subclass_display": SUBCLASS_DISPLAY_NAMES.get(subclass, subclass.replace("_", " ").title()),
        "skill": skill,
        "base_skill": base_skill,
        "racial_bonus": racial_bonus,
        "item_bonus": item_bonus,
        "talent_bonus": talent_bonus,
        "quest_bonus": quest_bonus,
        "quest_active": quest_active,
        "glance_damage_factor": glance_factor,
        "hit_bonus": hit_bonus,
        "cap": 315,
        "is_equipped": bool(item_name and item_name != "Unarmed")
    }


def get_default_db_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "items_db.json")


def load_items_db(filepath: Optional[str] = None) -> Dict:
    path = filepath or get_default_db_path()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_enchants_data() -> Dict[str, List[Dict]]:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "data", "enchants.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_races_data() -> Dict[str, List[Dict]]:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "data", "races.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_item(item_id: Union[int, str], db: Optional[Dict] = None) -> Optional[Dict]:
    database = db if db is not None else load_items_db()
    return database.get("by_id", {}).get(str(item_id))


def get_items_by_slot(slot: str, db: Optional[Dict] = None) -> List[Dict]:
    database = db if db is not None else load_items_db()
    return database.get("by_slot", {}).get(slot, [])


def find_items_by_name(query: str, db: Optional[Dict] = None) -> List[Dict]:
    database = db if db is not None else load_items_db()
    q = query.lower().strip()
    return [item for item in database.get("items", []) if q in item["name"].lower()]


def calculate_gear_totals(
    equipped_ids: List[Union[int, str]],
    db: Optional[Dict] = None,
    enchants: Optional[Dict[str, Any]] = None,
    race: Optional[str] = None,
    character_class: Optional[str] = None,
    quest_weapon_skills: Optional[Dict[str, bool]] = None,
) -> Dict[str, Any]:
    database = db if db is not None else load_items_db()
    totals: Dict[str, Any] = {
        "attack_power": 0,
        "ranged_attack_power": 0,
        "spell_power": 0,
        "healing": 0,
        "crit": 0.0,
        "hit": 0.0,
        "strength": 0,
        "agility": 0,
        "stamina": 0,
        "intellect": 0,
        "spirit": 0,
        "armor": 0,
        "haste": 0.0,
        "arp": 0,
        "block": 0,
        "resistances": {
            "holy": 0,
            "fire": 0,
            "nature": 0,
            "frost": 0,
            "shadow": 0,
            "arcane": 0,
        },
        "main_weapon_speed": 0.0,
        "main_weapon_dps": 0.0,
        "main_weapon_min_dmg": 0.0,
        "main_weapon_max_dmg": 0.0,
        "main_weapon_name": "Unarmed",
        "main_weapon_subclass": "misc",
        "main_weapon_slot": "",
        "off_weapon_speed": 0.0,
        "off_weapon_dps": 0.0,
        "off_weapon_min_dmg": 0.0,
        "off_weapon_max_dmg": 0.0,
        "off_weapon_name": "",
        "off_weapon_subclass": "misc",
        "ranged_weapon_speed": 0.0,
        "ranged_weapon_dps": 0.0,
        "ranged_weapon_min_dmg": 0.0,
        "ranged_weapon_max_dmg": 0.0,
        "ranged_weapon_name": "",
        "ranged_weapon_subclass": "bow",
        "equipped_items": [],
        "active_sets": {},
        "procs": [],
        "weapon_procs": [],
        "has_pet_summon": False,
        "pet_summon_details": [],
        "dual_wield_warning": None,
        "relic_warning": None,
        "class_warnings": [],
        "weapon_skills": {
            "sword": 0,
            "two_hand_sword": 0,
            "mace": 0,
            "two_hand_mace": 0,
            "axe": 0,
            "two_hand_axe": 0,
            "dagger": 0,
            "polearm": 0,
            "fist": 0,
            "bow": 0,
            "gun": 0,
            "crossbow": 0,
            "defense": 0,
        },
        "racial_skills": {},
    }

    cls_clean = (character_class or "paladin").lower().strip()
    cls_rules = CLASS_EQUIPMENT_RULES.get(cls_clean, CLASS_EQUIPMENT_RULES.get("paladin", {}))

    if race:
        races_all = load_races_data()
        race_list = races_all.get(cls_clean, races_all.get("warrior", []))
        race_lower = race.lower().strip()
        for r_entry in race_list:
            if r_entry["id"] == race_lower or r_entry["name"].lower() == race_lower:
                totals["strength"] += r_entry.get("str", 0)
                totals["agility"] += r_entry.get("agi", 0)
                totals["stamina"] += r_entry.get("sta", 0)
                totals["intellect"] += r_entry.get("int", 0)
                totals["spirit"] += r_entry.get("spi", 0)
                totals["racial_skills"] = {
                    "sword_skill": r_entry.get("sword_skill", 0),
                    "mace_skill": r_entry.get("mace_skill", 0),
                    "axe_skill": r_entry.get("axe_skill", 0),
                    "dagger_skill": r_entry.get("dagger_skill", 0),
                    "gun_skill": r_entry.get("gun_skill", 0),
                    "bow_skill": r_entry.get("bow_skill", 0),
                }
                break

    weapon_slots = {"two_hand", "one_hand", "main_hand", "twohand", "onehand", "mainhand"}
    set_counts: Dict[int, int] = {}
    set_defs: Dict[int, Dict] = {}

    for item_id in equipped_ids:
        item = get_item(item_id, database)
        if not item:
            continue

        slot = item.get("slot")
        subclass = (item.get("subclass") or "").lower().strip()
        speed = item.get("speed", 0.0)

        # Class restriction checks
        # 1. Dual wield restrictions (e.g. Paladin cannot dual wield weapons)
        is_weapon_item = subclass in ("sword", "mace", "axe", "dagger", "fist", "one_hand_sword", "one_hand_mace", "one_hand_axe") or (speed > 0 and slot in ("onehand", "one_hand", "offhand"))
        if not cls_rules.get("can_dual_wield", True) and totals["main_weapon_speed"] > 0:
            if is_weapon_item and slot in ("offhand", "onehand", "one_hand"):
                totals["dual_wield_warning"] = f"{cls_rules.get('name', 'Twoja klasa')} nie posiada umiejętności walki dwiema brońmi (Dual Wield). W lewej ręce dozwolona jest wyłącznie tarcza lub przedmiot trzymany (Off-hand)."
                totals["class_warnings"].append(totals["dual_wield_warning"])
                # Do not count weapon in off-hand for auto-attacks
                totals["equipped_items"].append(item)
                continue

        # 2. Relic vs Ranged restriction
        if slot in ("relic", "ranged"):
            if cls_rules.get("can_use_relic", False):
                valid_relics = cls_rules.get("valid_relic_subclasses", [])
                if subclass not in valid_relics and subclass != "misc":
                    warn_msg = f"{cls_rules.get('name', 'Twoja klasa')} może używać w tym slocie wyłącznie: {', '.join(valid_relics).title()}."
                    totals["relic_warning"] = warn_msg
                    totals["class_warnings"].append(warn_msg)
            elif cls_rules.get("can_use_ranged", False):
                valid_ranged = cls_rules.get("valid_ranged_subclasses", [])
                if subclass not in valid_ranged and subclass != "misc":
                    warn_msg = f"{cls_rules.get('name', 'Twoja klasa')} może używać w slocie dystansowym wyłącznie: {', '.join(valid_ranged).title()}."
                    totals["relic_warning"] = warn_msg
                    totals["class_warnings"].append(warn_msg)

        totals["equipped_items"].append(item)
        totals["attack_power"] += item.get("attack_power", 0)
        totals["ranged_attack_power"] += item.get("ranged_attack_power", 0)
        totals["spell_power"] += item.get("spell_power", 0)
        totals["healing"] += item.get("healing", 0)
        totals["crit"] += item.get("crit", 0.0)
        totals["hit"] += item.get("hit", 0.0)
        totals["strength"] += item.get("strength", 0)
        totals["agility"] += item.get("agility", 0)
        totals["stamina"] += item.get("stamina", 0)
        totals["intellect"] += item.get("intellect", 0)
        totals["spirit"] += item.get("spirit", 0)
        totals["armor"] += item.get("armor", 0)
        totals["arp"] += item.get("arp", 0)
        totals["block"] += item.get("block", 0)

        res = item.get("resistances", {})
        for r_key, r_val in res.items():
            if r_key in totals["resistances"]:
                totals["resistances"][r_key] += r_val

        for sp in item.get("spells", []):
            sp_text = sp.get("text", "")
            totals["procs"].append({
                "item_id": item["id"],
                "item_name": item["name"],
                "spell_id": sp.get("spell_id"),
                "trigger": sp.get("trigger"),
                "text": sp_text
            })
            for pat, sk_key in WEAPON_SKILL_PATTERNS:
                m = pat.search(sp_text)
                if m:
                    totals["weapon_skills"][sk_key] = totals["weapon_skills"].get(sk_key, 0) + int(m.group(1))

        if slot in weapon_slots and totals["main_weapon_speed"] == 0.0 and speed > 0:
            totals["main_weapon_speed"] = speed
            totals["main_weapon_dps"] = item.get("dps", 0.0)
            totals["main_weapon_min_dmg"] = item.get("min_damage", 0.0)
            totals["main_weapon_max_dmg"] = item.get("max_damage", 0.0)
            totals["main_weapon_name"] = item.get("name", "Weapon")
            totals["main_weapon_subclass"] = item.get("subclass", "sword")
            totals["main_weapon_slot"] = slot
        elif (slot in ("offhand", "onehand", "one_hand") or slot in weapon_slots) and speed > 0 and totals["off_weapon_speed"] == 0.0:
            if cls_rules.get("can_dual_wield", True) or subclass in ("shield", "misc"):
                totals["off_weapon_speed"] = speed
                totals["off_weapon_dps"] = item.get("dps", 0.0)
                totals["off_weapon_min_dmg"] = item.get("min_damage", 0.0)
                totals["off_weapon_max_dmg"] = item.get("max_damage", 0.0)
                totals["off_weapon_name"] = item.get("name", "Offhand Weapon")
                totals["off_weapon_subclass"] = item.get("subclass", "sword")

        if slot == "ranged" and totals["ranged_weapon_speed"] == 0.0:
            totals["ranged_weapon_speed"] = speed
            totals["ranged_weapon_dps"] = item.get("dps", 0.0)
            totals["ranged_weapon_min_dmg"] = item.get("min_damage", 0.0)
            totals["ranged_weapon_max_dmg"] = item.get("max_damage", 0.0)
            totals["ranged_weapon_name"] = item.get("name", "Ranged Weapon")
            totals["ranged_weapon_subclass"] = item.get("subclass", "bow")

        set_id = item.get("set_id", 0)
        if set_id > 0 and item.get("set"):
            set_counts[set_id] = set_counts.get(set_id, 0) + 1
            if set_id not in set_defs:
                set_defs[set_id] = item["set"]

    if enchants:
        all_enchants = load_enchants_data()
        for slot_key, ench_val in enchants.items():
            if not ench_val:
                continue
            ench_obj = None
            if isinstance(ench_val, dict):
                ench_obj = ench_val
            else:
                ench_id = int(ench_val) if str(ench_val).isdigit() else 0
                candidate_slots = [slot_key]
                if slot_key in ("main_hand", "mainhand"):
                    candidate_slots = ["twohand", "mainhand"]
                elif slot_key in ("off_hand", "offhand"):
                    candidate_slots = ["offhand", "shield"]
                elif slot_key in ("relic", "ranged", "range"):
                    candidate_slots = ["ranged"]
                elif slot_key in ("finger1", "finger2"):
                    candidate_slots = ["finger"]
                elif slot_key in ("trinket1", "trinket2"):
                    candidate_slots = ["trinket"]
                elif slot_key == "waist":
                    candidate_slots = ["waist"]
                elif slot_key == "neck":
                    candidate_slots = ["neck"]

                for c_slot in candidate_slots:
                    for e_item in all_enchants.get(c_slot, []):
                        if e_item.get("id") == ench_id:
                            ench_obj = e_item
                            break
                    if ench_obj:
                        break

                if not ench_obj:
                    # Global search in all categories as fallback
                    for cat_name, e_list in all_enchants.items():
                        for e_item in e_list:
                            if e_item.get("id") == ench_id:
                                ench_obj = e_item
                                break
                        if ench_obj:
                            break

            if ench_obj:
                totals["strength"] += ench_obj.get("str", 0)
                totals["agility"] += ench_obj.get("agi", 0)
                totals["stamina"] += ench_obj.get("sta", 0)
                totals["intellect"] += ench_obj.get("int", 0)
                totals["spirit"] += ench_obj.get("spi", 0)
                totals["attack_power"] += ench_obj.get("ap", 0)
                totals["hit"] += ench_obj.get("hit", 0.0)
                totals["crit"] += ench_obj.get("crit", 0.0)
                totals["haste"] += ench_obj.get("haste", 0.0)
                totals["armor"] += ench_obj.get("armor", 0) + ench_obj.get("defense", 0)
                totals["spell_power"] += ench_obj.get("sp", ench_obj.get("spellpower", 0))
                totals["healing"] += ench_obj.get("healing", 0)
                totals["arp"] += ench_obj.get("arp", 0)
                totals["block"] += ench_obj.get("block", 0)
                for res_key in ("arcane", "fire", "frost", "nature", "shadow", "holy"):
                    if res_key in ench_obj and res_key in totals["resistances"]:
                        totals["resistances"][res_key] += ench_obj[res_key]

                # Weapon bonus damage (Superior Striking, scopes, etc.)
                bonusdmg = ench_obj.get("bonusdmg", 0)
                if bonusdmg > 0:
                    if slot_key in ("mainhand", "main_hand", "twohand", "two_hand"):
                        totals["main_weapon_min_dmg"] += bonusdmg
                        totals["main_weapon_max_dmg"] += bonusdmg
                        if totals["main_weapon_speed"] > 0:
                            totals["main_weapon_dps"] += bonusdmg / totals["main_weapon_speed"]
                    elif slot_key in ("offhand", "off_hand"):
                        totals["off_weapon_min_dmg"] += bonusdmg
                        totals["off_weapon_max_dmg"] += bonusdmg
                        if totals["off_weapon_speed"] > 0:
                            totals["off_weapon_dps"] += bonusdmg / totals["off_weapon_speed"]
                    elif slot_key in ("ranged", "range"):
                        totals["ranged_weapon_min_dmg"] += bonusdmg
                        totals["ranged_weapon_max_dmg"] += bonusdmg
                        if totals["ranged_weapon_speed"] > 0:
                            totals["ranged_weapon_dps"] += bonusdmg / totals["ranged_weapon_speed"]

                # Track weapon enchant procs (Fiery, Crusader, Lifestealing, etc.)
                if slot_key in ("mainhand", "main_hand", "twohand", "two_hand", "offhand", "off_hand"):
                    if ench_obj.get("ppm") or ench_obj.get("magicdmg") or ench_obj.get("procspell") or ench_obj.get("chance"):
                        totals["weapon_procs"].append({
                            "slot": slot_key,
                            "enchant_name": ench_obj.get("name", ""),
                            "ppm": ench_obj.get("ppm"),
                            "magicdmg": ench_obj.get("magicdmg", 0),
                            "procspell": ench_obj.get("procspell", ""),
                            "chance": ench_obj.get("chance", 0),
                            "str": ench_obj.get("str", 0),
                        })

                if ench_obj.get("ppm") or ench_obj.get("procspell"):
                    totals["procs"].append({
                        "slot": slot_key,
                        "enchant_name": ench_obj.get("name", ""),
                        "ppm": ench_obj.get("ppm"),
                        "procspell": ench_obj.get("procspell")
                    })

    for sid, count in set_counts.items():
        s_info = set_defs.get(sid)
        if not s_info:
            continue
        active_bonuses = []
        for b in s_info.get("bonuses", []):
            if count >= b.get("threshold", 999):
                active_bonuses.append(b)
                if sid == 261 and b.get("threshold") == 4:
                    totals["has_pet_summon"] = True
                    totals["pet_summon_details"].append("Spirit of Eskhandar")
                # Set of the Lost (ID 6001, strictly 4 items: Memento of the Lost, Remains of the Lost, Loop of the Lost, Tome of the Lost)
                if sid == 6001 and b.get("threshold") == 3:
                    totals["has_pet_summon"] = True
                    totals["pet_summon_details"].append("Set of the Lost")
        totals["active_sets"][str(sid)] = {
            "id": sid,
            "name": s_info.get("name", ""),
            "equipped_count": count,
            "total_pieces": len(s_info.get("pieces", [])),
            "active_bonuses": active_bonuses,
        }

    totals["total_attack_power"] = totals["attack_power"] + (totals["strength"] * 2)
    totals["total_ranged_attack_power"] = totals["ranged_attack_power"] + totals["attack_power"] + (totals["agility"] * 2)
    totals["total_melee_crit"] = round(totals["crit"] + (totals["agility"] / 20.0), 2)
    totals["total_ranged_crit"] = round(totals["crit"] + (totals["agility"] / 53.0), 2)

    # Compute weapon skills breakdown for all equipped weapon slots
    equipped_weapon_skills = []
    if totals["main_weapon_name"] and totals["main_weapon_name"] != "Unarmed":
        mh_details = compute_weapon_skill_details(
            slot="main_hand",
            item_name=totals["main_weapon_name"],
            subclass=totals["main_weapon_subclass"],
            item_skills=totals["weapon_skills"],
            racial_skills=totals.get("racial_skills", {}),
            talent_weapon_skill=0,
            quest_weapon_skills=quest_weapon_skills
        )
        equipped_weapon_skills.append(mh_details)

    if totals["off_weapon_name"] and totals["off_weapon_speed"] > 0:
        oh_details = compute_weapon_skill_details(
            slot="off_hand",
            item_name=totals["off_weapon_name"],
            subclass=totals["off_weapon_subclass"],
            item_skills=totals["weapon_skills"],
            racial_skills=totals.get("racial_skills", {}),
            talent_weapon_skill=0,
            quest_weapon_skills=quest_weapon_skills
        )
        equipped_weapon_skills.append(oh_details)

    if totals["ranged_weapon_name"] and totals["ranged_weapon_speed"] > 0:
        rng_details = compute_weapon_skill_details(
            slot="ranged",
            item_name=totals["ranged_weapon_name"],
            subclass=totals.get("ranged_weapon_subclass", "bow"),
            item_skills=totals["weapon_skills"],
            racial_skills=totals.get("racial_skills", {}),
            talent_weapon_skill=0,
            quest_weapon_skills=quest_weapon_skills
        )
        equipped_weapon_skills.append(rng_details)

    totals["equipped_weapon_skills"] = equipped_weapon_skills

    # Effective main weapon skill
    effective_ws = 300
    if equipped_weapon_skills:
        effective_ws = equipped_weapon_skills[0]["skill"]
    else:
        effective_ws = compute_effective_weapon_skill(
            totals["main_weapon_subclass"],
            totals["weapon_skills"],
            totals.get("racial_skills", {}),
            talent_weapon_skill=0
        )

    ws_above = max(0, effective_ws - 300)
    totals["weapon_skill"] = effective_ws
    totals["effective_weapon_skill"] = effective_ws
    totals["weapon_skill_hit_bonus"] = round((ws_above // 5) * 1.0, 1)
    totals["glance_damage_factor"] = round(min(1.0, 0.70 + (ws_above * 0.02)), 3)

    return totals
