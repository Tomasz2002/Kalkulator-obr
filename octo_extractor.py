import os
import sys
import struct
import json
import re
import shutil
import tempfile
import mpyq


def find_file(filename):
    for folder in ["plik octo wow", "data", "."]:
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            return path
    return None


def extract_dbcs(temp_dir):
    os.makedirs(temp_dir, exist_ok=True)
    targets = ["Item.dbc", "Spell.dbc", "ItemSet.dbc"]
    mpq_files = ["patch-3.mpq", "patch-O.mpq"]
    extracted = {}
    for mpq_name in mpq_files:
        mpq_path = find_file(mpq_name)
        if not mpq_path:
            continue
        archive = mpyq.MPQArchive(mpq_path)
        for file_name in archive.files:
            name_str = file_name.decode("utf-8", errors="ignore")
            for target in targets:
                if name_str.lower().endswith(target.lower()):
                    data = archive.read_file(file_name)
                    out_name = f"{mpq_name}_{target}"
                    out_path = os.path.join(temp_dir, out_name)
                    with open(out_path, "wb") as f_out:
                        f_out.write(data)
                    extracted[(mpq_name, target)] = out_path
    return extracted


def parse_dbc(file_path):
    if not file_path or not os.path.exists(file_path):
        return None, b"", 0, 0, 0
    with open(file_path, "rb") as f:
        header = f.read(20)
        magic, rec_count, field_count, rec_size, string_size = struct.unpack("<4sIIII", header)
        data = f.read(rec_count * rec_size)
        strings = f.read(string_size)
    return data, strings, field_count, rec_size, rec_count


def get_str(strings, offset):
    if offset <= 0 or offset >= len(strings):
        return ""
    end = strings.find(b"\x00", offset)
    if end == -1:
        end = len(strings)
    return strings[offset:end].decode("utf-8", errors="ignore")


def load_spells(data, strings, field_count, rec_size, rec_count, target_dict):
    if data is None:
        return
    for i in range(rec_count):
        off = i * rec_size
        vals = struct.unpack(f"<{field_count}i", data[off : off + rec_size])
        sid = vals[0]
        name = get_str(strings, vals[120])
        desc = get_str(strings, vals[138])
        bp = [vals[76] + 1, vals[77] + 1, vals[78] + 1]
        auras = [vals[91], vals[92], vals[93]]
        ap = rap = sp = heal = 0
        crit = hit = 0.0
        for e in range(3):
            a = auras[e]
            v = bp[e]
            if a == 99:
                ap += v
            elif a == 124:
                rap += v
            elif a == 13:
                sp += v
            elif a == 135:
                heal += v
            elif a in (52, 57, 71):
                crit += v
            elif a in (54, 55):
                hit += v
        target_dict[sid] = {
            "name": name,
            "desc": desc,
            "bp": bp,
            "auras": auras,
            "ap": ap,
            "rap": rap,
            "sp": sp,
            "heal": heal,
            "crit": crit,
            "hit": hit,
            "proc_chance": vals[40] if len(vals) > 40 else 0,
        }


def format_spell_text(spell_id, trigger, spells):
    s = spells.get(spell_id)
    if not s:
        return ""
    desc = s["desc"] or s["name"]
    for idx, bp_val in enumerate(s["bp"]):
        desc = desc.replace(f"$s{idx+1}", str(abs(bp_val)))
    for ref_id, ref_eff in re.findall(r"\$(\d+)s(\d+)", desc):
        ref_s = spells.get(int(ref_id))
        if ref_s and len(ref_s["bp"]) >= int(ref_eff):
            desc = desc.replace(f"${ref_id}s{ref_eff}", str(abs(ref_s["bp"][int(ref_eff) - 1])))
    desc = re.sub(r"\$[a-zA-Z0-9]+", "", desc)
    desc = re.sub(r"\/[a-zA-Z0-9]+", "", desc)
    desc = desc.strip()
    if not desc:
        return ""
    if trigger == 1:
        return f"Equip: {desc}"
    elif trigger == 2:
        return f"Chance on hit: {desc}"
    elif trigger == 0:
        return f"Use: {desc}"
    return desc


def load_itemsets(data, strings, field_count, rec_size, rec_count, spells, sets_dict):
    if data is None:
        return
    for i in range(rec_count):
        off = i * rec_size
        vals = struct.unpack(f"<{field_count}I", data[off : off + rec_size])
        set_id = vals[0]
        name = get_str(strings, vals[1])
        pieces = [vals[10 + p] for p in range(17) if vals[10 + p] != 0]
        sp_ids = [vals[27 + s] for s in range(8) if vals[27 + s] != 0]
        thresh = [vals[35 + t] for t in range(8) if vals[35 + t] != 0]
        bonuses = []
        for k in range(min(len(sp_ids), len(thresh))):
            th = thresh[k]
            sp_id = sp_ids[k]
            sp_info = spells.get(sp_id, {})
            sp_desc = sp_info.get("desc") or sp_info.get("name") or ""
            for idx, bp_val in enumerate(sp_info.get("bp", [])):
                sp_desc = sp_desc.replace(f"$s{idx+1}", str(abs(bp_val)))
            for ref_id, ref_eff in re.findall(r"\$(\d+)s(\d+)", sp_desc):
                ref_s = spells.get(int(ref_id))
                if ref_s and len(ref_s.get("bp", [])) >= int(ref_eff):
                    sp_desc = sp_desc.replace(f"${ref_id}s{ref_eff}", str(abs(ref_s["bp"][int(ref_eff) - 1])))
            sp_desc = re.sub(r"\$[a-zA-Z0-9]+", "", sp_desc)
            sp_desc = re.sub(r"\/[a-zA-Z0-9]+", "", sp_desc).strip()
            if not sp_desc:
                sp_desc = f"Spell {sp_id}"
            bonuses.append({"threshold": th, "text": f"({th}) Set: {sp_desc}"})
        bonuses.sort(key=lambda b: b["threshold"])
        if pieces or bonuses:
            sets_dict[set_id] = {
                "id": set_id,
                "name": name,
                "pieces": pieces,
                "bonuses": bonuses,
            }


INV_TYPE_MAP = {
    1: "head",
    2: "neck",
    3: "shoulder",
    4: "shirt",
    5: "chest",
    6: "waist",
    7: "legs",
    8: "feet",
    9: "wrist",
    10: "hands",
    11: "finger",
    12: "trinket",
    13: "one_hand",
    14: "shield",
    15: "ranged",
    16: "back",
    17: "two_hand",
    20: "chest",
    21: "main_hand",
    22: "off_hand",
    23: "off_hand",
    25: "ranged",
    26: "ranged",
    28: "relic",
}

ARMOR_SUBCLASS = {
    0: "misc",
    1: "cloth",
    2: "leather",
    3: "mail",
    4: "plate",
    6: "shield",
    7: "libram",
    8: "idol",
    9: "totem",
}

WEAPON_SUBCLASS = {
    0: "one_hand_axe",
    1: "two_hand_axe",
    2: "bow",
    3: "gun",
    4: "one_hand_mace",
    5: "two_hand_mace",
    6: "polearm",
    7: "one_hand_sword",
    8: "two_hand_sword",
    10: "staff",
    13: "fist",
    14: "misc",
    15: "dagger",
    18: "crossbow",
    19: "wand",
}

CLASS_MASKS = {
    1: "warrior",
    2: "paladin",
    4: "hunter",
    8: "rogue",
    16: "priest",
    64: "shaman",
    128: "mage",
    256: "warlock",
    1024: "druid",
}

ALL_CLASSES = ["warrior", "paladin", "hunter", "rogue", "priest", "shaman", "mage", "warlock", "druid"]


def resolve_classes(mask, item_cls, subcls):
    if mask not in (-1, 0, 4294967295, 32767, 65535):
        cls_list = [cname for bit, cname in CLASS_MASKS.items() if mask & bit]
        if cls_list:
            return cls_list
    if item_cls == 4:
        if subcls == "plate":
            return ["warrior", "paladin"]
        if subcls == "mail":
            return ["warrior", "paladin", "hunter", "shaman"]
        if subcls == "leather":
            return ["warrior", "paladin", "hunter", "rogue", "shaman", "druid"]
        if subcls == "shield":
            return ["warrior", "paladin", "shaman"]
        if subcls == "libram":
            return ["paladin"]
        if subcls == "idol":
            return ["druid"]
        if subcls == "totem":
            return ["shaman"]
        return list(ALL_CLASSES)
    if item_cls == 2:
        if subcls in ("bow", "gun", "crossbow"):
            return ["warrior", "hunter", "rogue"]
        if subcls == "wand":
            return ["priest", "mage", "warlock"]
        if subcls == "polearm":
            return ["warrior", "paladin", "hunter"]
        if subcls == "two_hand_mace":
            return ["warrior", "paladin", "shaman", "druid"]
        if subcls == "two_hand_axe":
            return ["warrior", "paladin", "hunter", "shaman"]
        if subcls == "two_hand_sword":
            return ["warrior", "paladin", "hunter"]
        if subcls == "one_hand_mace":
            return ["warrior", "paladin", "rogue", "priest", "shaman", "druid"]
        if subcls == "one_hand_sword":
            return ["warrior", "paladin", "hunter", "rogue", "mage", "warlock"]
        if subcls == "one_hand_axe":
            return ["warrior", "hunter", "rogue", "shaman"]
        if subcls == "dagger":
            return ["warrior", "hunter", "rogue", "priest", "shaman", "mage", "warlock", "druid"]
        if subcls == "staff":
            return ["warrior", "hunter", "priest", "shaman", "mage", "warlock", "druid"]
        if subcls == "fist":
            return ["warrior", "hunter", "rogue", "shaman", "druid"]
        return list(ALL_CLASSES)
    return list(ALL_CLASSES)


def parse_wdb(wdb_path, spells, item_to_set, icons_map, items_dict):
    if not wdb_path or not os.path.exists(wdb_path):
        return
    with open(wdb_path, "rb") as f:
        wdb = f.read()
    offset = 20
    while offset < len(wdb):
        if offset + 8 > len(wdb):
            break
        entry, size = struct.unpack_from("<II", wdb, offset)
        if size == 0:
            break
        rec = wdb[offset + 8 : offset + 8 + size]
        offset += 8 + size
        item_cls, item_subcls_id = struct.unpack_from("<II", rec, 0)
        pos = 8
        strings = []
        for _ in range(4):
            end = rec.find(b"\x00", pos)
            if end == -1:
                break
            strings.append(rec[pos:end].decode("utf-8", errors="ignore"))
            pos = end + 1
        if not strings:
            continue
        name = strings[0]
        fixed = rec[pos:]
        if len(fixed) < 380:
            continue
        ints = struct.unpack(f"<{len(fixed)//4}i", fixed[: (len(fixed) // 4) * 4])
        floats = struct.unpack(f"<{len(fixed)//4}f", fixed[: (len(fixed) // 4) * 4])
        display_id = ints[0]
        quality = ints[1]
        flags = ints[2]
        inv_type = ints[5]
        allowable_class = ints[6]
        allowable_race = ints[7]
        item_level = ints[8]
        req_level = ints[9]
        if inv_type not in INV_TYPE_MAP:
            continue
        slot = INV_TYPE_MAP[inv_type]
        subclass = "misc"
        if item_cls == 4:
            subclass = ARMOR_SUBCLASS.get(item_subcls_id, "misc")
        elif item_cls == 2:
            subclass = WEAPON_SUBCLASS.get(item_subcls_id, "misc")
        strength = agility = stamina = intellect = spirit = 0
        ap = rap = sp = healing = 0
        crit = hit = 0.0
        for s_idx in range(10):
            st_type = ints[20 + s_idx * 2]
            st_val = ints[20 + s_idx * 2 + 1]
            if st_type == 4:
                strength += st_val
            elif st_type == 3:
                agility += st_val
            elif st_type == 7:
                stamina += st_val
            elif st_type == 5:
                intellect += st_val
            elif st_type == 6:
                spirit += st_val
            elif st_type == 38:
                ap += st_val
            elif st_type == 39:
                rap += st_val
            elif st_type in (16, 17, 18, 31):
                hit += st_val
            elif st_type in (19, 20, 21, 32):
                crit += st_val
            elif st_type in (42, 45):
                sp += st_val
            elif st_type == 41:
                healing += st_val
        dmg_min = floats[40] if len(floats) > 40 else 0.0
        dmg_max = floats[41] if len(floats) > 41 else 0.0
        delay = ints[62] if len(ints) > 62 else 0
        armor = ints[55] if len(ints) > 55 else 0
        holy_res = ints[56] if len(ints) > 56 else 0
        fire_res = ints[57] if len(ints) > 57 else 0
        nature_res = ints[58] if len(ints) > 58 else 0
        frost_res = ints[59] if len(ints) > 59 else 0
        shadow_res = ints[60] if len(ints) > 60 else 0
        arcane_res = ints[61] if len(ints) > 61 else 0
        speed = round(delay / 1000.0, 2) if item_cls == 2 and delay > 0 else 0.0
        dps = round(((dmg_min + dmg_max) / 2.0) / speed, 1) if speed > 0 else 0.0
        item_spells = []
        for sp_i in range(5):
            s_id = ints[65 + sp_i * 6]
            s_trig = ints[65 + sp_i * 6 + 1]
            if s_id > 0:
                s_text = format_spell_text(s_id, s_trig, spells)
                if s_text:
                    item_spells.append({"spell_id": s_id, "trigger": s_trig, "text": s_text})
                sp_obj = spells.get(s_id, {})
                ap += sp_obj.get("ap", 0)
                rap += sp_obj.get("rap", 0)
                sp += sp_obj.get("sp", 0)
                healing += sp_obj.get("heal", 0)
                crit += sp_obj.get("crit", 0.0)
                hit += sp_obj.get("hit", 0.0)
        resistances = {}
        if holy_res > 0:
            resistances["holy"] = holy_res
        if fire_res > 0:
            resistances["fire"] = fire_res
        if nature_res > 0:
            resistances["nature"] = nature_res
        if frost_res > 0:
            resistances["frost"] = frost_res
        if shadow_res > 0:
            resistances["shadow"] = shadow_res
        if arcane_res > 0:
            resistances["arcane"] = arcane_res
        set_obj = item_to_set.get(entry)
        set_id = set_obj["id"] if set_obj else 0
        bonding = ints[95] if len(ints) > 95 else 0
        durability = ints[106] if len(ints) > 106 and ints[106] > 0 else 0
        classes = resolve_classes(allowable_class, item_cls, subclass)
        icon = icons_map.get(str(entry), "inv_misc_questionmark")
        items_dict[entry] = {
            "id": entry,
            "name": name,
            "icon": icon,
            "slot": slot,
            "subclass": subclass,
            "quality": quality,
            "item_level": item_level,
            "req_level": req_level,
            "armor": armor,
            "durability": durability,
            "unique": bool(flags & 1),
            "bonding": bonding,
            "speed": speed,
            "min_damage": dmg_min if speed > 0 else 0.0,
            "max_damage": dmg_max if speed > 0 else 0.0,
            "dps": dps,
            "strength": strength,
            "agility": agility,
            "stamina": stamina,
            "intellect": intellect,
            "spirit": spirit,
            "resistances": resistances,
            "attack_power": ap,
            "spell_power": sp,
            "healing": healing,
            "crit": round(crit, 2),
            "hit": round(hit, 2),
            "spells": item_spells,
            "set": set_obj,
            "set_id": set_id,
            "classes": classes,
        }


def run_pipeline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(base_dir, "data", "temp_octo_extracted")
    extracted = extract_dbcs(temp_dir)
    spells = {}
    p3_spell_path = extracted.get(("patch-3.mpq", "Spell.dbc"))
    if p3_spell_path:
        d, s, fc, rs, rc = parse_dbc(p3_spell_path)
        load_spells(d, s, fc, rs, rc, spells)
    pO_spell_path = extracted.get(("patch-O.mpq", "Spell.dbc"))
    if pO_spell_path:
        d, s, fc, rs, rc = parse_dbc(pO_spell_path)
        load_spells(d, s, fc, rs, rc, spells)
    sets_dict = {}
    p3_itemset_path = extracted.get(("patch-3.mpq", "ItemSet.dbc"))
    if p3_itemset_path:
        d, s, fc, rs, rc = parse_dbc(p3_itemset_path)
        load_itemsets(d, s, fc, rs, rc, spells, sets_dict)
    pO_itemset_path = extracted.get(("patch-O.mpq", "ItemSet.dbc"))
    if pO_itemset_path:
        d, s, fc, rs, rc = parse_dbc(pO_itemset_path)
        load_itemsets(d, s, fc, rs, rc, spells, sets_dict)
    octo_sets_path = find_file("octo_sets.json")
    if octo_sets_path and os.path.exists(octo_sets_path):
        with open(octo_sets_path, "r", encoding="utf-8") as f:
            octo_sets = json.load(f)
        for s_id_str, s_data in octo_sets.items():
            sets_dict[int(s_id_str)] = s_data
    item_to_set = {}
    for s_id, s_data in sets_dict.items():
        for piece_id in s_data.get("pieces", []):
            item_to_set[piece_id] = {
                "id": s_data["id"],
                "name": s_data["name"],
                "pieces": s_data["pieces"],
                "bonuses": s_data["bonuses"],
            }
    icons_map = {}
    icons_path = find_file("item_icons.json")
    if icons_path and os.path.exists(icons_path):
        with open(icons_path, "r", encoding="utf-8") as f:
            icons_map = json.load(f)
    items_dict = {}
    existing_db_path = os.path.join(base_dir, "items_db.json")
    if os.path.exists(existing_db_path):
        with open(existing_db_path, "r", encoding="utf-8") as f:
            existing_db = json.load(f)
        for it in existing_db.get("items", []):
            it_id = it["id"]
            if it_id in item_to_set:
                it["set"] = item_to_set[it_id]
                it["set_id"] = item_to_set[it_id]["id"]
            if str(it_id) in icons_map:
                it["icon"] = icons_map[str(it_id)]
            items_dict[it_id] = it
    data_wdb = os.path.join("data", "itemcache.wdb")
    if os.path.exists(data_wdb):
        parse_wdb(data_wdb, spells, item_to_set, icons_map, items_dict)
    octo_wdb = os.path.join("plik octo wow", "itemcache.wdb")
    if os.path.exists(octo_wdb):
        parse_wdb(octo_wdb, spells, item_to_set, icons_map, items_dict)
    preserved_ids = {14551, 11815, 11726, 20130, 11811}
    filtered_items = []
    for it in items_dict.values():
        it_id = it["id"]
        q = it.get("quality", 0)
        req_lvl = it.get("req_level", 0)
        item_lvl = it.get("item_level", 0)
        is_preserved = it_id in preserved_ids
        is_set_piece = it_id in item_to_set
        if not is_preserved and not is_set_piece:
            if q < 3:
                continue
            if req_lvl < 55 and not (req_lvl == 0 and item_lvl >= 55):
                continue
        filtered_items.append(it)
    filtered_items.sort(key=lambda x: (x["slot"], -x.get("quality", 0), -x.get("item_level", 0), x["name"]))
    by_id = {str(item["id"]): item for item in filtered_items}
    by_slot = {}
    for item in filtered_items:
        by_slot.setdefault(item["slot"], []).append(item)
    final_output = {
        "items": filtered_items,
        "by_id": by_id,
        "by_slot": by_slot,
    }
    with open(existing_db_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    return len(filtered_items)


if __name__ == "__main__":
    count = run_pipeline()
    print(f"Extracted and saved {count} items.")
