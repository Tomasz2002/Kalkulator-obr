import json
import os
from flask import Flask, jsonify, render_template, request

from main import simulate_combat
from src.items_db import calculate_gear_totals, get_item, get_items_by_slot, load_items_db

app = Flask(__name__, template_folder="templates", static_folder="static")

db = load_items_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/paladin_talents")
def api_paladin_talents():
    path = os.path.join(os.path.dirname(__file__), "data", "paladin_talents.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"trees": ["Holy", "Protection", "Retribution"], "talents": [], "builds": []})


@app.route("/api/items")
def api_items():
    icons_path = os.path.join(os.path.dirname(__file__), "data", "item_icons.json")
    item_icons = {}
    if os.path.exists(icons_path):
        try:
            with open(icons_path, "r", encoding="utf-8") as f:
                item_icons = json.load(f)
        except Exception:
            pass

    lightweight_items = []
    for item in db.get("items", []):
        if "paladin" in item.get("classes", ["paladin"]):
            item_id_str = str(item["id"])
            lightweight_items.append({
                "id": item["id"],
                "name": item["name"],
                "slot": item["slot"],
                "subclass": item.get("subclass", ""),
                "quality": item.get("quality", 1),
                "icon": item_icons.get(item_id_str, ""),
                "item_level": item.get("item_level", 0),
                "req_level": item.get("req_level", 0),
                "speed": item.get("speed", 0.0),
                "min_damage": item.get("min_damage", 0.0),
                "max_damage": item.get("max_damage", 0.0),
                "dps": item.get("dps", 0.0),
                "armor": item.get("armor", 0),
                "ap": item.get("attack_power", 0),
                "sp": item.get("spell_power", 0),
                "healing": item.get("healing", 0),
                "crit": item.get("crit", 0.0),
                "hit": item.get("hit", 0.0),
                "strength": item.get("strength", 0),
                "agility": item.get("agility", 0),
                "stamina": item.get("stamina", 0),
                "intellect": item.get("intellect", 0),
                "spirit": item.get("spirit", 0),
                "set_id": item.get("set_id", 0),
            })

    return jsonify({
        "metadata": db.get("metadata", {}),
        "items": lightweight_items,
        "by_slot": db.get("by_slot", {}),
    })


@app.route("/api/gear_totals", methods=["POST"])
def api_gear_totals():
    data = request.get_json() or {}
    equipped_ids = data.get("equipped_items", [])
    totals = calculate_gear_totals(equipped_ids, db)
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
    t2_bonus_active = bool(data.get("t2_bonus_active", True))
    lost_set_active = bool(data.get("lost_set_active", True))
    talents = data.get("talents", {})

    result = simulate_combat(
        equipped_items=equipped_items,
        fight_duration=fight_duration,
        haste_percent=haste_percent,
        target_armor=target_armor,
        judgement_interval=judgement_interval,
        consecration=consecration,
        exorcism_interval=exorcism_interval,
        t2_bonus_active=t2_bonus_active,
        lost_set_active=lost_set_active,
        talents=talents,
        character_class="paladin",
        db=db,
    )
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
