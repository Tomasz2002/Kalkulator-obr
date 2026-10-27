import json
import os
from typing import Dict, List, Optional, Union


def get_default_db_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "items_db.json")


def load_items_db(filepath: Optional[str] = None) -> Dict:
    path = filepath or get_default_db_path()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_item(item_id: Union[int, str], db: Optional[Dict] = None) -> Optional[Dict]:
    database = db if db is not None else load_items_db()
    return database.get("by_id", {}).get(str(item_id))


def get_items_by_slot(slot: str, db: Optional[Dict] = None) -> List[Dict]:
    database = db if db is not None else load_items_db()
    return database.get("by_slot", {}).get(slot, [])


def find_items_by_name(query: str, db: Optional[Dict] = None) -> List[Dict]:
    database = db if db is not None else load_items_db()
    q = query.lower()
    return [item for item in database.get("items", []) if q in item["name"].lower()]


def calculate_gear_totals(equipped_ids: List[Union[int, str]], db: Optional[Dict] = None) -> Dict:
    database = db if db is not None else load_items_db()
    totals = {
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
        "main_weapon_speed": 0.0,
        "main_weapon_dps": 0.0,
        "ranged_weapon_speed": 0.0,
        "ranged_weapon_dps": 0.0,
        "equipped_items": [],
    }

    weapon_slots = {"two_hand", "one_hand", "main_hand"}

    for item_id in equipped_ids:
        item = get_item(item_id, database)
        if not item:
            continue
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

        if item.get("slot") in weapon_slots and totals["main_weapon_speed"] == 0.0:
            totals["main_weapon_speed"] = item.get("speed", 0.0)
            totals["main_weapon_dps"] = item.get("dps", 0.0)

        if item.get("slot") == "ranged" and totals["ranged_weapon_speed"] == 0.0:
            totals["ranged_weapon_speed"] = item.get("speed", 0.0)
            totals["ranged_weapon_dps"] = item.get("dps", 0.0)

    totals["total_attack_power"] = totals["attack_power"] + (totals["strength"] * 2)
    totals["total_ranged_attack_power"] = totals["ranged_attack_power"] + totals["attack_power"] + (totals["agility"] * 2)
    totals["total_melee_crit"] = round(totals["crit"] + (totals["agility"] / 20.0), 2)
    totals["total_ranged_crit"] = round(totals["crit"] + (totals["agility"] / 53.0), 2)

    return totals
