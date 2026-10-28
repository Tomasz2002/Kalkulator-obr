import json
import os
import re
import struct
from typing import Any, Dict, List, Optional


def get_clean_spell_description(key: str, name: str, rank: str, desc: str, sp: Dict[str, Any]) -> str:
    """Returns accurate, resolved description matching Octo WoW 1.18 DBC mechanics."""
    if key == "crusader_strike":
        return "A strike that deals 100% weapon damage plus an additional 160 and increases your attack speed by 3%. Stacks up to 3 times. Lasts 15 sec."
    if key == "holy_strike":
        return "Strikes the target for Holy damage, dealing 100% weapon damage plus an additional 128, and restores health and mana to you and up to 4 allies within 10 yards. Healing on yourself is reduced by half."
    if key == "hammer_of_wrath":
        return "Hurls a hammer that strikes an enemy for 504 to 556 Holy damage. Only usable on enemies that have 20% or less health."
    if key == "consecration":
        return "Consecrates the land beneath the Paladin, inflicting 384 Holy damage over 8 sec to enemies within the area. The consecrated power wanes, dealing reduced damage as time passes."
    if key == "exorcism":
        return "Causes 505 to 563 Holy damage to an Undead or Demon target. This spell generates reduced threat."
    if key == "holy_shock":
        return "Blasts the target with Holy energy, causing 365 to 395 Holy damage to an enemy, or 365 to 395 healing to an ally. Casting Holy Shock has a chance to have no cooldown for its next cast."
    if key == "seal_of_command":
        return "Gives the Paladin a chance to deal additional Holy damage equal to 70% of weapon damage. Only one Seal can be active on the Paladin at any one time. Lasts 30 sec.\n\nUnleashing this Seal's energy will judge an enemy, instantly causing 170 Holy damage (340 if the target is stunned or incapacitated). This damage is increased by 15% of your attack power."
    if key == "seal_of_righteousness":
        return "Fills the Paladin with holy spirit for 30 sec, giving each melee attack a chance to cause up to 66 additional Holy damage. Only one Seal can be active on the Paladin at any one time.\n\nUnleashing this Seal's energy will cause 185 Holy damage to an enemy."
    if key == "seal_of_the_crusader":
        return "Fills the Paladin with the spirit of a crusader for 30 sec, granting 306 melee attack power. The Paladin also attacks 40% faster, but deals less damage with each attack.\n\nUnleashing this Seal's energy will judge an enemy for 10 sec, increasing Holy damage taken by up to 140. Your melee strikes will refresh the spell's duration."
    if key == "judgement":
        return "Unleashes the energy of a Seal spell upon an enemy. Refer to individual Seals for Judgement effect."

    if not desc:
        return ""
    res = desc
    res = re.sub(r"\$s1%", "100%", res)
    res = re.sub(r"\$s1", str(int(sp.get("avg_damage", 0))), res)
    res = re.sub(r"\$s2", str(int(sp.get("bonus_flat", 0))), res)
    res = re.sub(r"\$d", "30 sec", res)
    res = re.sub(r"\$\d+[a-z]\d*", "", res)
    res = re.sub(r"\$/\d+;\d+[a-z]\d*", "", res)
    return res.strip()


def get_spell_scaling_note(key: str, sp: Dict[str, Any]) -> str:
    """Provides exact theorycraft scaling coefficients for Octo WoW."""
    if key == "crusader_strike":
        return "Physical Damage (mitigated by armor). Scales with +100% Weapon Damage + AP. Grants Zeal (+3% Haste/stack, max +9% Haste for 15s)."
    if key == "holy_strike":
        return "Holy Weapon Damage (bypasses armor). Scales with +100% Weapon Damage, AP and +20% Spell Power. Harmful Spell Hit."
    if key == "hammer_of_wrath":
        return "Execute Ability (<20% Boss HP). Holy damage scaling with +42.86% Spell Power."
    if key == "consecration":
        return "Ground AoE (1 Holy tick/sec over 8s). Total scales with +33% Spell Power."
    if key == "exorcism":
        return "Holy spell damage scaling with +42.86% Spell Power. Usable on any target in Octo WoW."
    if key == "holy_shock":
        return "Instant burst Holy spell scaling with +42.86% Spell Power."
    if key == "seal_of_command":
        return "7.0 PPM proc rate. Proc deals 70% weapon dmg + 29% SP. Judgement deals 170 Holy + 15% AP + 42.86% SP."
    if key == "seal_of_righteousness":
        return "Guaranteed on-hit on every swing. Scales with weapon speed and +10-12% SP per hit. Judgement deals 185 Holy + 50% SP."
    if key == "seal_of_the_crusader":
        return "Grants +306 Attack Power & +40% Attack Speed. Judgement increases Holy damage taken by up to 140."
    if key == "judgement":
        return "Unleashes current Seal burst. Base CD 10s (reduced to 8-9s with Improved Judgement talent)."
    return ""


def generate_spell_tooltip_html(sp: Dict[str, Any]) -> str:
    """Generates an authentic World of Warcraft spell tooltip markup."""
    name = sp.get("name", "Spell")
    rank = sp.get("rank", "")
    mana = sp.get("mana_cost", 0)
    range_yds = sp.get("range_yards", 0)
    cast_time = sp.get("cast_time", 0.0)
    cd = sp.get("cooldown", 0.0)
    desc = sp.get("description_clean", sp.get("description", ""))
    scaling = sp.get("scaling_note", "")

    mana_str = f"{mana} Mana" if mana > 0 else ""
    if range_yds > 0:
        range_str = "Melee Range" if range_yds <= 5 else f"{range_yds} yd range"
    else:
        range_str = ""

    cast_str = f"{cast_time:.1f} sec cast" if cast_time > 0 else "Instant"
    cd_str = f"{cd:.1f} sec cooldown" if cd > 0 else ""

    lines = []
    lines.append('<div class="tt-spell-wrap">')
    lines.append('  <div class="tt-spell-header">')
    lines.append(f'    <span class="tt-spell-name">{name}</span>')
    if rank:
        lines.append(f'    <span class="tt-spell-rank">{rank}</span>')
    lines.append('  </div>')

    if mana_str or range_str:
        lines.append('  <div class="tt-spell-subline">')
        lines.append(f'    <span>{mana_str}</span>')
        lines.append(f'    <span>{range_str}</span>')
        lines.append('  </div>')

    if cast_str or cd_str:
        lines.append('  <div class="tt-spell-subline">')
        lines.append(f'    <span>{cast_str}</span>')
        lines.append(f'    <span>{cd_str}</span>')
        lines.append('  </div>')

    if desc:
        desc_formatted = desc.replace("\n", "<br>")
        lines.append(f'  <div class="tt-spell-desc">{desc_formatted}</div>')

    if scaling:
        lines.append(f'  <div class="tt-spell-scaling">&#9733; {scaling}</div>')

    lines.append('  <div class="tt-spell-octo">Octo WoW 1.18 DBC Data</div>')
    lines.append('</div>')
    return "\n".join(lines)


def enrich_spell(spell_obj: Dict[str, Any]) -> Dict[str, Any]:
    spell_obj["description_clean"] = get_clean_spell_description(
        spell_obj["key"], spell_obj["name"], spell_obj["rank"], spell_obj.get("description", ""), spell_obj
    )
    spell_obj["scaling_note"] = get_spell_scaling_note(spell_obj["key"], spell_obj)
    spell_obj["tooltip_html"] = generate_spell_tooltip_html(spell_obj)
    return spell_obj


def extract_paladin_spells(dbc_path: str = "data/Spell.dbc") -> Dict[str, Any]:
    if not os.path.exists(dbc_path):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        alt_path = os.path.join(base_dir, dbc_path)
        if os.path.exists(alt_path):
            dbc_path = alt_path

    with open(dbc_path, "rb") as f:
        header = f.read(20)
        magic, rec_count, field_count, rec_size, string_size = struct.unpack("<4sIIII", header)
        data = f.read(rec_count * rec_size)
        strings = f.read(string_size)

    def get_str(offset: int) -> str:
        if offset <= 0 or offset >= len(strings):
            return ""
        end = strings.find(b"\x00", offset)
        if end == -1:
            end = len(strings)
        return strings[offset:end].decode("utf-8", errors="ignore")

    abilities_def = {
        "Crusader Strike": {
            "key": "crusader_strike",
            "category": "strike",
            "range": 5,
            "gcd": 1.5,
            "ap_coef": 1.0,
            "sp_coef": 0.0,
            "condition": "always",
            "icon": "spell_holy_crusaderstrike"
        },
        "Holy Strike": {
            "key": "holy_strike",
            "category": "strike",
            "range": 5,
            "gcd": 1.5,
            "ap_coef": 1.0,
            "sp_coef": 0.20,
            "condition": "always",
            "icon": "spell_holy_righteousnessaura"
        },
        "Consecration": {
            "key": "consecration",
            "category": "consecration",
            "range": 0,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.33,
            "condition": "always",
            "icon": "spell_holy_innerfire"
        },
        "Exorcism": {
            "key": "exorcism",
            "category": "exorcism",
            "range": 30,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.4286,
            "condition": "always",
            "icon": "spell_holy_exorcism_02"
        },
        "Hammer of Wrath": {
            "key": "hammer_of_wrath",
            "category": "execute",
            "range": 30,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.4286,
            "condition": "target_hp_le_20",
            "icon": "ability_thunderbolt"
        },
        "Holy Shock": {
            "key": "holy_shock",
            "category": "holy_shock",
            "range": 20,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.4286,
            "condition": "always",
            "icon": "spell_holy_searinglight"
        },
        "Judgement": {
            "key": "judgement",
            "category": "judgement",
            "range": 10,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.0,
            "condition": "seal_active",
            "icon": "spell_holy_righteousfury"
        },
        "Judgement of Command": {
            "key": "judgement_of_command",
            "category": "judgement_proc",
            "range": 10,
            "gcd": 0.0,
            "ap_coef": 0.15,
            "sp_coef": 0.4286,
            "condition": "seal_command_active",
            "icon": "ability_warrior_innerrage"
        },
        "Judgement of Righteousness": {
            "key": "judgement_of_righteousness",
            "category": "judgement_proc",
            "range": 10,
            "gcd": 0.0,
            "ap_coef": 0.0,
            "sp_coef": 0.50,
            "condition": "seal_righteousness_active",
            "icon": "spell_holy_righteousnessaura"
        },
        "Judgement of the Crusader": {
            "key": "judgement_of_the_crusader",
            "category": "judgement_proc",
            "range": 10,
            "gcd": 0.0,
            "ap_coef": 0.0,
            "sp_coef": 0.0,
            "condition": "seal_crusader_active",
            "icon": "spell_holy_holysmite"
        },
        "Seal of Command": {
            "key": "seal_of_command",
            "category": "seal",
            "range": 0,
            "gcd": 1.5,
            "ap_coef": 0.70,
            "sp_coef": 0.29,
            "condition": "always",
            "icon": "ability_warrior_innerrage"
        },
        "Seal of Righteousness": {
            "key": "seal_of_righteousness",
            "category": "seal",
            "range": 0,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.12,
            "condition": "always",
            "icon": "ability_thunderbolt"
        },
        "Seal of the Crusader": {
            "key": "seal_of_the_crusader",
            "category": "seal",
            "range": 0,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.0,
            "condition": "always",
            "icon": "spell_holy_holysmite"
        },
        "Seal of the Martyr": {
            "key": "seal_of_the_martyr",
            "category": "seal",
            "range": 0,
            "gcd": 1.5,
            "ap_coef": 0.50,
            "sp_coef": 0.25,
            "condition": "always",
            "icon": "spell_holy_healingaura"
        },
        "Blessing of Might": {
            "key": "blessing_of_might",
            "category": "blessing",
            "range": 30,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.0,
            "condition": "always",
            "icon": "spell_holy_fistofjustice"
        },
        "Blessing of Wisdom": {
            "key": "blessing_of_wisdom",
            "category": "blessing",
            "range": 30,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.0,
            "condition": "always",
            "icon": "spell_holy_sealofwisdom"
        },
        "Blessing of Kings": {
            "key": "blessing_of_kings",
            "category": "blessing",
            "range": 30,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.0,
            "condition": "always",
            "icon": "spell_magic_magearmor"
        },
        "Blessing of Sanctuary": {
            "key": "blessing_of_sanctuary",
            "category": "blessing",
            "range": 30,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.0,
            "condition": "always",
            "icon": "spell_nature_lightningshield"
        },
        "Sanctity Aura": {
            "key": "sanctity_aura",
            "category": "aura",
            "range": 0,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.0,
            "condition": "always",
            "icon": "spell_holy_mindvision"
        },
        "Retribution Aura": {
            "key": "retribution_aura",
            "category": "aura",
            "range": 0,
            "gcd": 1.5,
            "ap_coef": 0.0,
            "sp_coef": 0.0,
            "condition": "always",
            "icon": "spell_holy_auraoflight"
        },
    }

    spells_db: Dict[str, Any] = {
        "metadata": {
            "class": "paladin",
            "source": dbc_path,
            "total_records": 0
        },
        "spells": {},
        "by_id": {},
        "rotational_spells": []
    }

    for i in range(rec_count):
        row = data[i * rec_size : (i + 1) * rec_size]
        vals = struct.unpack(f"<{field_count}i", row)
        spell_id = vals[0]
        name = get_str(vals[120])
        rank_str = get_str(vals[129])

        if name not in abilities_def:
            continue

        mana = vals[32]
        cd_ms = vals[20]
        cat_cd_ms = vals[21]
        cooldown = max(cd_ms, cat_cd_ms) / 1000.0

        if name == "Judgement" and cooldown == 0.0:
            cooldown = 10.0

        cast_time = 0.0
        cast_idx = vals[18]
        if cast_idx == 4:
            cast_time = 1.0
        elif cast_idx in (2, 3):
            cast_time = 1.5

        lvl = vals[29]
        bp1 = vals[76]
        die1 = vals[64]
        bp2 = vals[77]

        min_dmg = float(bp1 + 1) if bp1 >= 0 else 0.0
        max_dmg = float(bp1 + max(1, die1)) if bp1 >= 0 else 0.0
        avg_dmg = (min_dmg + max_dmg) / 2.0

        rank_match = re.search(r"\d+", rank_str)
        rank_num = int(rank_match.group(0)) if rank_match else 1

        meta = abilities_def[name]

        spell_obj = {
            "id": spell_id,
            "key": meta["key"],
            "name": name,
            "rank": rank_str,
            "rank_num": rank_num,
            "spell_level": lvl,
            "category": meta["category"],
            "icon": meta["icon"],
            "cast_time": cast_time,
            "mana_cost": mana,
            "cooldown": cooldown,
            "range_yards": meta["range"],
            "min_damage": min_dmg,
            "max_damage": max_dmg,
            "avg_damage": avg_dmg,
            "bonus_flat": float(bp2) if bp2 > 0 else 0.0,
            "spell_power_coef": meta["sp_coef"],
            "ap_coef": meta["ap_coef"],
            "gcd": meta["gcd"],
            "condition": meta["condition"],
            "description": get_str(vals[138]),
            "tooltip": get_str(vals[147]),
        }

        enrich_spell(spell_obj)

        if name not in spells_db["spells"]:
            spells_db["spells"][name] = []
        spells_db["spells"][name].append(spell_obj)
        spells_db["by_id"][str(spell_id)] = spell_obj

    for name in spells_db["spells"]:
        spells_db["spells"][name].sort(key=lambda s: (s["spell_level"], s["rank_num"], s["id"]))

    canonical_rotational = [
        {"key": "hammer_of_wrath", "name": "Hammer of Wrath", "preferred_id": 24239},
        {"key": "crusader_strike", "name": "Crusader Strike", "preferred_id": 10337},
        {"key": "holy_strike", "name": "Holy Strike", "preferred_id": 10333},
        {"key": "judgement", "name": "Judgement", "preferred_id": 20271},
        {"key": "consecration", "name": "Consecration", "preferred_id": 20924},
        {"key": "exorcism", "name": "Exorcism", "preferred_id": 10314},
        {"key": "holy_shock", "name": "Holy Shock", "preferred_id": 51786},
        {"key": "seal_of_command", "name": "Seal of Command", "preferred_id": 20920},
        {"key": "seal_of_righteousness", "name": "Seal of Righteousness", "preferred_id": 25715},
        {"key": "seal_of_the_crusader", "name": "Seal of the Crusader", "preferred_id": 20308},
    ]

    for item in canonical_rotational:
        pid = str(item["preferred_id"])
        if pid in spells_db["by_id"]:
            sp = spells_db["by_id"][pid].copy()
            sp["key"] = item["key"]
            if item["key"] == "judgement":
                sp["cooldown"] = 10.0
            enrich_spell(sp)
            spells_db["rotational_spells"].append(sp)
        else:
            cand = spells_db["spells"].get(item["name"], [])
            if cand:
                sp = cand[-1].copy()
                sp["key"] = item["key"]
                enrich_spell(sp)
                spells_db["rotational_spells"].append(sp)

    spells_db["metadata"]["total_records"] = len(spells_db["by_id"])
    return spells_db


def save_spells_db(output_path: str = "data/spells_db.json", dbc_path: str = "data/Spell.dbc") -> Dict[str, Any]:
    db = extract_paladin_spells(dbc_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    return db


def load_spells_db(db_path: str = "data/spells_db.json") -> Dict[str, Any]:
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return save_spells_db(db_path)


if __name__ == "__main__":
    db = save_spells_db()
    print(f"Generated spells_db.json with {db['metadata']['total_records']} spells.")
    for s in db["rotational_spells"]:
        print(f"  {s['key']}: {s['name']} ({s['rank']}) - CD: {s['cooldown']}s, Mana: {s['mana_cost']}, SP Coef: {s['spell_power_coef']}")
