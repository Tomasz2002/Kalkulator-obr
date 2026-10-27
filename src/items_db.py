import json
import os
from typing import Any, Dict, List, Optional, Union


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
        "equipped_items": [],
        "active_sets": {},
        "procs": [],
        "has_pet_summon": False,
        "pet_summon_details": [],
    }

    if race:
        races_all = load_races_data()
        cls_key = (character_class or "warrior").lower().strip()
        race_list = races_all.get(cls_key, races_all.get("warrior", []))
        race_lower = race.lower().strip()
        for r_entry in race_list:
            if r_entry["id"] == race_lower or r_entry["name"].lower() == race_lower:
                totals["strength"] += r_entry.get("str", 0)
                totals["agility"] += r_entry.get("agi", 0)
                totals["stamina"] += r_entry.get("sta", 0)
                totals["intellect"] += r_entry.get("int", 0)
                totals["spirit"] += r_entry.get("spi", 0)
                break

    weapon_slots = {"two_hand", "one_hand", "main_hand", "twohand", "onehand", "mainhand"}
    set_counts: Dict[int, int] = {}
    set_defs: Dict[int, Dict] = {}

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

        res = item.get("resistances", {})
        for r_key, r_val in res.items():
            if r_key in totals["resistances"]:
                totals["resistances"][r_key] += r_val

        for sp in item.get("spells", []):
            totals["procs"].append({
                "item_id": item["id"],
                "item_name": item["name"],
                "spell_id": sp.get("spell_id"),
                "trigger": sp.get("trigger"),
                "text": sp.get("text", "")
            })

        slot = item.get("slot")
        speed = item.get("speed", 0.0)

        if slot in weapon_slots and totals["main_weapon_speed"] == 0.0 and speed > 0:
            totals["main_weapon_speed"] = speed
            totals["main_weapon_dps"] = item.get("dps", 0.0)
            totals["main_weapon_min_dmg"] = item.get("min_damage", 0.0)
            totals["main_weapon_max_dmg"] = item.get("max_damage", 0.0)
            totals["main_weapon_name"] = item.get("name", "Weapon")
            totals["main_weapon_subclass"] = item.get("subclass", "sword")
            totals["main_weapon_slot"] = slot
        elif (slot in ("offhand", "onehand", "one_hand") or slot in weapon_slots) and speed > 0 and totals["off_weapon_speed"] == 0.0:
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
                lookup_slot = slot_key
                if lookup_slot in ("finger1", "finger2"):
                    lookup_slot = "finger"
                elif lookup_slot in ("trinket1", "trinket2"):
                    lookup_slot = "trinket"
                slot_ench_list = all_enchants.get(lookup_slot, [])
                for e_item in slot_ench_list:
                    if e_item.get("id") == ench_id:
                        ench_obj = e_item
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

    return totals
