import json
import os
import struct


def load_spell_stats(spell_dbc_path):
    if not os.path.exists(spell_dbc_path):
        return {}
    with open(spell_dbc_path, "rb") as f:
        header = f.read(20)
        magic, rec_count, field_count, rec_size, string_size = struct.unpack("<4sIIII", header)
        data = f.read(rec_count * rec_size)
    spell_stats = {}
    for i in range(rec_count):
        row = data[i * rec_size : (i + 1) * rec_size]
        vals = struct.unpack(f"<{field_count}i", row)
        spell_id = vals[0]
        ap = 0
        rap = 0
        sp = 0
        healing = 0
        crit = 0
        hit = 0
        for e in range(3):
            aura = vals[91 + e]
            bp = vals[76 + e] + 1
            if aura == 99:
                ap += bp
            elif aura == 124:
                rap += bp
            elif aura == 13:
                sp += bp
            elif aura == 135:
                healing += bp
            elif aura in (52, 57, 71):
                crit += bp
            elif aura in (54, 55):
                hit += bp
        if ap or rap or sp or healing or crit or hit:
            spell_stats[spell_id] = {
                "ap": ap,
                "rap": rap,
                "sp": sp,
                "healing": healing,
                "crit": crit,
                "hit": hit,
            }
    return spell_stats


def parse_sql_values(val_str):
    fields = []
    current = []
    in_quote = False
    escape = False
    for char in val_str:
        if escape:
            current.append(char)
            escape = False
        elif char == "\\":
            escape = True
        elif char == "'" and not escape:
            in_quote = not in_quote
        elif char == "," and not in_quote:
            fields.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    fields.append("".join(current).strip())
    return fields


def extract_items_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    spell_dbc_path = os.path.join(data_dir, "Spell.dbc")
    sql_path = os.path.join(data_dir, "item_template.sql")
    wdb_path = os.path.join(data_dir, "itemcache.wdb")
    output_json = os.path.join(base_dir, "items_db.json")

    spell_stats = load_spell_stats(spell_dbc_path)

    slot_names = {
        1: "head",
        2: "neck",
        3: "shoulder",
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
        26: "ranged",
        28: "relic",
    }

    weapon_subclasses = {
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
        15: "dagger",
        18: "crossbow",
    }

    armor_subclasses = {
        0: "misc",
        1: "cloth",
        2: "leather",
        3: "mail",
        4: "plate",
        6: "shield",
        7: "relic",
    }

    items_dict = {}

    if os.path.exists(sql_path):
        with open(sql_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.startswith("INSERT INTO `item_template` VALUES"):
                    continue
                val_str = line[line.find("(") + 1 : line.rfind(")")]
                fields = parse_sql_values(val_str)
                if len(fields) < 115:
                    continue

                entry = int(fields[0])
                item_cls = int(fields[1])
                item_subcls = int(fields[2])
                name = fields[3].strip("'")
                quality = int(fields[6])
                inv_type = int(fields[11])
                allowable_class = int(fields[12])
                item_level = int(fields[14])
                req_level = int(fields[15])
                delay = int(fields[46])
                dmg_min = float(fields[49])
                dmg_max = float(fields[50])
                armor = int(fields[65])
                set_id = int(fields[116]) if len(fields) > 116 else 0

                if inv_type not in slot_names:
                    continue

                is_pal = (allowable_class == -1) or bool(allowable_class & 2)
                is_hun = (allowable_class == -1) or bool(allowable_class & 4)
                if not is_pal and not is_hun:
                    continue

                subclass_name = "unknown"
                if item_cls == 2:
                    if item_subcls not in weapon_subclasses:
                        continue
                    subclass_name = weapon_subclasses[item_subcls]
                elif item_cls == 4:
                    if item_subcls not in armor_subclasses:
                        continue
                    subclass_name = armor_subclasses[item_subcls]
                else:
                    continue

                if quality < 2:
                    continue
                if item_level < 45 and req_level < 45 and entry not in (11815, 17774, 13965):
                    continue
                if quality == 2 and req_level < 50:
                    continue

                classes = []
                if is_pal:
                    pal_weapon_ok = item_cls != 2 or item_subcls in (0, 1, 4, 5, 6, 7, 8)
                    pal_armor_ok = item_cls != 4 or item_subcls in (0, 1, 2, 3, 4, 6, 7)
                    if pal_weapon_ok and pal_armor_ok:
                        classes.append("paladin")

                if is_hun:
                    hun_weapon_ok = item_cls != 2 or item_subcls in (0, 1, 2, 3, 6, 7, 8, 10, 13, 15, 18)
                    hun_armor_ok = item_cls != 4 or item_subcls in (0, 2, 3)
                    if hun_weapon_ok and hun_armor_ok:
                        classes.append("hunter")

                if not classes:
                    continue

                spells = [
                    int(fields[72]),
                    int(fields[79]),
                    int(fields[86]),
                    int(fields[93]),
                    int(fields[100]),
                ]

                ap = 0
                rap = 0
                sp = 0
                healing = 0
                crit = 0.0
                hit = 0.0

                for sp_id in spells:
                    if sp_id in spell_stats:
                        ap += spell_stats[sp_id]["ap"]
                        rap += spell_stats[sp_id]["rap"]
                        sp += spell_stats[sp_id]["sp"]
                        healing += spell_stats[sp_id]["healing"]
                        crit += spell_stats[sp_id]["crit"]
                        hit += spell_stats[sp_id]["hit"]

                strength = 0
                agility = 0
                stamina = 0
                intellect = 0
                spirit = 0

                for s_i in range(10):
                    st = int(fields[26 + s_i * 2])
                    sv = int(fields[27 + s_i * 2])
                    if st == 3:
                        agility += sv
                    elif st == 4:
                        strength += sv
                    elif st == 5:
                        intellect += sv
                    elif st == 6:
                        spirit += sv
                    elif st == 7:
                        stamina += sv
                    elif st == 38:
                        ap += sv
                    elif st == 39:
                        rap += sv
                    elif st in (16, 17, 18, 31):
                        hit += sv
                    elif st in (19, 20, 21, 32):
                        crit += sv
                    elif st in (42, 45):
                        sp += sv
                    elif st == 41:
                        healing += sv

                speed = round(delay / 1000.0, 2) if item_cls == 2 else 0.0
                dps = round(((dmg_min + dmg_max) / 2.0) / speed, 1) if speed > 0 else 0.0

                items_dict[entry] = {
                    "id": entry,
                    "name": name,
                    "slot": slot_names[inv_type],
                    "subclass": subclass_name,
                    "quality": quality,
                    "item_level": item_level,
                    "req_level": req_level,
                    "speed": speed,
                    "min_damage": dmg_min if speed > 0 else 0.0,
                    "max_damage": dmg_max if speed > 0 else 0.0,
                    "dps": dps,
                    "attack_power": ap,
                    "ranged_attack_power": rap,
                    "spell_power": sp,
                    "healing": healing,
                    "crit": crit,
                    "hit": hit,
                    "strength": strength,
                    "agility": agility,
                    "stamina": stamina,
                    "intellect": intellect,
                    "spirit": spirit,
                    "armor": armor,
                    "set_id": set_id,
                    "classes": classes,
                }

    if os.path.exists(wdb_path):
        with open(wdb_path, "rb") as f:
            wdb_data = f.read()

        offset = 20
        while offset < len(wdb_data):
            entry, size = struct.unpack("<II", wdb_data[offset : offset + 8])
            if size == 0:
                break
            rec = wdb_data[offset + 8 : offset + 8 + size]
            item_cls, item_subcls = struct.unpack_from("<II", rec, 0)

            pos = 8
            strings = []
            for _ in range(4):
                end = rec.find(b"\x00", pos)
                if end == -1:
                    break
                strings.append(rec[pos:end].decode("utf-8", errors="ignore"))
                pos = end + 1

            if not strings:
                offset += 8 + size
                continue

            name = strings[0]
            fixed = rec[pos:]
            if len(fixed) < 380:
                offset += 8 + size
                continue

            display_id, quality, flags, buy_price, sell_price, inv_type, allowable_class, allowable_race, item_level, req_level = struct.unpack_from("<10I", fixed, 0)

            if inv_type not in slot_names:
                offset += 8 + size
                continue

            is_pal = (allowable_class == 4294967295 or allowable_class == -1) or bool(allowable_class & 2)
            is_hun = (allowable_class == 4294967295 or allowable_class == -1) or bool(allowable_class & 4)
            if not is_pal and not is_hun:
                offset += 8 + size
                continue

            subclass_name = "unknown"
            if item_cls == 2:
                if item_subcls not in weapon_subclasses:
                    offset += 8 + size
                    continue
                subclass_name = weapon_subclasses[item_subcls]
            elif item_cls == 4:
                if item_subcls not in armor_subclasses:
                    offset += 8 + size
                    continue
                subclass_name = armor_subclasses[item_subcls]
            else:
                offset += 8 + size
                continue

            if quality < 2:
                offset += 8 + size
                continue
            if item_level < 45 and req_level < 45 and entry not in (11815, 17774, 13965):
                offset += 8 + size
                continue
            if quality == 2 and req_level < 50:
                offset += 8 + size
                continue

            classes = []
            if is_pal:
                pal_weapon_ok = item_cls != 2 or item_subcls in (0, 1, 4, 5, 6, 7, 8)
                pal_armor_ok = item_cls != 4 or item_subcls in (0, 1, 2, 3, 4, 6, 7)
                if pal_weapon_ok and pal_armor_ok:
                    classes.append("paladin")

            if is_hun:
                hun_weapon_ok = item_cls != 2 or item_subcls in (0, 1, 2, 3, 6, 7, 8, 10, 13, 15, 18)
                hun_armor_ok = item_cls != 4 or item_subcls in (0, 2, 3)
                if hun_weapon_ok and hun_armor_ok:
                    classes.append("hunter")

            if not classes:
                offset += 8 + size
                continue

            strength = 0
            agility = 0
            stamina = 0
            intellect = 0
            spirit = 0
            ap = 0
            rap = 0
            sp = 0
            healing = 0
            crit = 0.0
            hit = 0.0

            for s_i in range(10):
                st, sv = struct.unpack_from("<ii", fixed, 80 + s_i * 8)
                if st == 3:
                    agility += sv
                elif st == 4:
                    strength += sv
                elif st == 5:
                    intellect += sv
                elif st == 6:
                    spirit += sv
                elif st == 7:
                    stamina += sv
                elif st == 38:
                    ap += sv
                elif st == 39:
                    rap += sv
                elif st in (16, 17, 18, 31):
                    hit += sv
                elif st in (19, 20, 21, 32):
                    crit += sv
                elif st in (42, 45):
                    sp += sv
                elif st == 41:
                    healing += sv

            dmg_min, dmg_max, dmg_type = struct.unpack_from("<ffi", fixed, 160)
            armor = struct.unpack_from("<i", fixed, 220)[0]
            delay = struct.unpack_from("<I", fixed, 248)[0]

            for sp_i in range(5):
                sp_id = struct.unpack_from("<i", fixed, 260 + sp_i * 24)[0]
                if sp_id in spell_stats:
                    ap += spell_stats[sp_id]["ap"]
                    rap += spell_stats[sp_id]["rap"]
                    sp += spell_stats[sp_id]["sp"]
                    healing += spell_stats[sp_id]["healing"]
                    crit += spell_stats[sp_id]["crit"]
                    hit += spell_stats[sp_id]["hit"]

            speed = round(delay / 1000.0, 2) if item_cls == 2 else 0.0
            dps = round(((dmg_min + dmg_max) / 2.0) / speed, 1) if speed > 0 else 0.0
            set_id = struct.unpack_from("<i", fixed, 384)[0] if len(fixed) > 388 else 0

            items_dict[entry] = {
                "id": entry,
                "name": name,
                "slot": slot_names[inv_type],
                "subclass": subclass_name,
                "quality": quality,
                "item_level": item_level,
                "req_level": req_level,
                "speed": speed,
                "min_damage": dmg_min if speed > 0 else 0.0,
                "max_damage": dmg_max if speed > 0 else 0.0,
                "dps": dps,
                "attack_power": ap,
                "ranged_attack_power": rap,
                "spell_power": sp,
                "healing": healing,
                "crit": crit,
                "hit": hit,
                "strength": strength,
                "agility": agility,
                "stamina": stamina,
                "intellect": intellect,
                "spirit": spirit,
                "armor": armor,
                "set_id": set_id,
                "classes": classes,
            }

            offset += 8 + size

    raw_items = list(items_dict.values())
    raw_items.sort(key=lambda x: (1 if x["id"] >= 100000 else 0, 0 if x.get("set_id", 0) > 0 else 1, -x.get("quality", 1), -x.get("item_level", 0), x["id"]))
    seen_keys = set()
    items_list = []
    for it in raw_items:
        key = (it["name"].strip().lower(), it["slot"])
        if key not in seen_keys:
            seen_keys.add(key)
            items_list.append(it)
    items_list.sort(key=lambda x: (x["slot"], -x["quality"], -x["item_level"], x["name"]))

    by_slot = {}
    for item in items_list:
        by_slot.setdefault(item["slot"], []).append(item)

    by_id = {str(item["id"]): item for item in items_list}

    by_class = {
        "paladin": [it for it in items_list if "paladin" in it.get("classes", [])],
        "hunter": [it for it in items_list if "hunter" in it.get("classes", [])],
    }

    db_output = {
        "metadata": {
            "total_items": len(items_list),
            "paladin_items": len(by_class["paladin"]),
            "hunter_items": len(by_class["hunter"]),
            "slots": {slot: len(items) for slot, items in by_slot.items()},
        },
        "by_id": by_id,
        "by_slot": by_slot,
        "by_class": by_class,
        "items": items_list,
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(db_output, f, indent=2, ensure_ascii=False)

    return db_output


if __name__ == "__main__":
    db = extract_items_database()
    print(f"Extraction complete! Total items: {db['metadata']['total_items']}")
    print(f"Paladin items: {db['metadata']['paladin_items']}, Hunter items: {db['metadata']['hunter_items']}")
