import json
import os
from flask import Flask, jsonify, render_template, request

from main import simulate_combat
from src.items_db import CLASS_EQUIPMENT_RULES, calculate_gear_totals, get_item, get_items_by_slot, load_items_db
from src.spells_extractor import load_spells_db

app = Flask(__name__, template_folder="templates", static_folder="static")

db = load_items_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/class_equipment_rules")
def api_class_equipment_rules():
    return jsonify(CLASS_EQUIPMENT_RULES)


@app.route("/api/paladin_talents")
def api_paladin_talents():
    path = os.path.join(os.path.dirname(__file__), "data", "paladin_talents.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"trees": ["Holy", "Protection", "Retribution"], "talents": [], "builds": []})


@app.route("/api/talents")
def api_talents():
    cls = request.args.get("class", "paladin").lower().strip()
    filename = "warrior_talents.json" if cls == "warrior" else "paladin_talents.json"
    path = os.path.join(os.path.dirname(__file__), "data", filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"trees": [], "talents": [], "builds": []})


@app.route("/api/enchants")
def api_enchants():
    path = os.path.join(os.path.dirname(__file__), "data", "enchants.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({})


@app.route("/api/races")
def api_races():
    path = os.path.join(os.path.dirname(__file__), "data", "races.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"warrior": [], "paladin": []})


@app.route("/api/spells")
def api_spells():
    cls = request.args.get("class", "paladin").lower().strip()
    s_db = load_spells_db()
    if cls == "paladin":
        rotational = s_db.get("rotational_spells", [])
        return jsonify({
            "character_class": "paladin",
            "rotational_spells": rotational,
            "canonical_rotational": {s["key"]: s for s in rotational if "key" in s},
            "all_spells": s_db.get("paladin_spells", []),
        })
    return jsonify({"character_class": cls, "rotational_spells": [], "canonical_rotational": {}, "all_spells": []})


@app.route("/api/items")
def api_items():
    class_filter = request.args.get("class", "paladin").lower().strip()
    all_items = db.get("items", [])

    if class_filter and class_filter != "all":
        filtered_items = [it for it in all_items if class_filter in it.get("classes", [])]
    else:
        filtered_items = all_items

    return jsonify({
        "metadata": {
            "total_items": len(filtered_items),
            "class_filter": class_filter,
            "version": db.get("metadata", {}).get("version", "faithful_v1")
        },
        "items": filtered_items,
        "by_slot": db.get("by_slot", {}),
    })


@app.route("/api/gear_totals", methods=["POST"])
def api_gear_totals():
    data = request.get_json() or {}
    equipped_ids = data.get("equipped_items", [])
    enchants = data.get("enchants", {})
    race = data.get("race", "human")
    character_class = data.get("character_class", "paladin")
    quest_weapon_skills = data.get("quest_weapon_skills", {})
    totals = calculate_gear_totals(
        equipped_ids=equipped_ids,
        db=db,
        enchants=enchants,
        race=race,
        character_class=character_class,
        quest_weapon_skills=quest_weapon_skills,
    )
    return jsonify(totals)


@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    data = request.get_json() or {}
    equipped_items = data.get("equipped_items", [])
    fight_duration = float(data.get("fight_duration", 60.0))
    haste_percent = float(data.get("haste_percent", 0.0))
    target_armor = float(data.get("target_armor", 3731.0))
    judgement_interval = float(data.get("judgement_interval", 10.0))
    consecration = bool(data.get("consecration", True))
    exorcism_interval = float(data.get("exorcism_interval", 15.0))
    character_class = str(data.get("character_class", "paladin")).lower().strip()
    paladin_build = str(data.get("paladin_build", "auto")).lower().strip()
    talents = data.get("talents", {})
    boss_hp_percent = float(data.get("boss_hp_percent", 100.0))
    execute_phase_percent = float(data.get("execute_phase_percent", 20.0))
    race = str(data.get("race", "human")).lower().strip()
    enchants = data.get("enchants", {})
    rotation_mode = str(data.get("rotation_mode", "priority_rotation")).lower().strip()
    priority_list = data.get("priority_list", None)
    strike_ramp_mode = str(data.get("strike_ramp_mode", "3_cs")).lower().strip()
    strike_ramp_hs = int(data.get("strike_ramp_hs", 0))
    strike_ramp_cs = int(data.get("strike_ramp_cs", 3))
    strike_sustain_hs = int(data.get("strike_sustain_hs", 1))
    strike_sustain_cs = int(data.get("strike_sustain_cs", 1))
    enable_crusader_strike = bool(data.get("enable_crusader_strike", True))
    enable_holy_strike = bool(data.get("enable_holy_strike", True))
    quest_weapon_skills = data.get("quest_weapon_skills", {})
    primary_seal = str(data.get("primary_seal", "auto")).lower().strip()
    apply_crusader_first = bool(data.get("apply_crusader_first", True))

    result = simulate_combat(
        equipped_items=equipped_items,
        fight_duration=fight_duration,
        haste_percent=haste_percent,
        target_armor=target_armor,
        judgement_interval=judgement_interval,
        consecration=consecration,
        exorcism_interval=exorcism_interval,
        talents=talents,
        boss_hp_percent=boss_hp_percent,
        execute_phase_percent=execute_phase_percent,
        race=race,
        enchants=enchants,
        character_class=character_class,
        paladin_build=paladin_build,
        rotation_mode=rotation_mode,
        priority_list=priority_list,
        strike_ramp_mode=strike_ramp_mode,
        strike_ramp_hs=strike_ramp_hs,
        strike_ramp_cs=strike_ramp_cs,
        strike_sustain_hs=strike_sustain_hs,
        strike_sustain_cs=strike_sustain_cs,
        enable_crusader_strike=enable_crusader_strike,
        enable_holy_strike=enable_holy_strike,
        quest_weapon_skills=quest_weapon_skills,
        primary_seal=primary_seal,
        apply_crusader_first=apply_crusader_first,
        db=db,
    )
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
