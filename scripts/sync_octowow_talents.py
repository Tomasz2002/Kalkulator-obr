"""
Synchronizes talent trees (Hunter, Paladin, Warrior) directly with the canonical
Octo WoW talent calculator: https://octowow.st/talents/
Also downloads any missing talent icons from https://octowow.st/talents/icons/
into static/icons/talents/.
"""
import os
import re
import sys
import time
import json
import urllib.request
import urllib.parse
import http.cookiejar

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://octowow.st"
CLASSES = ["hunter", "paladin", "warrior"]

TREE_NAMES = {
    "hunter": ["Beast Mastery", "Marksmanship", "Survival"],
    "paladin": ["Holy", "Protection", "Retribution"],
    "warrior": ["Arms", "Fury", "Protection"],
}


def create_octowow_opener():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
        ("Referer", f"{BASE_URL}/talents/"),
    ]
    return opener


def fetch_octo_path(opener, path: str) -> bytes:
    url = BASE_URL + path
    raw = opener.open(url, timeout=15).read()
    text = raw.decode("utf-8", "ignore")
    m_chal = re.search(r'name="bf_challenge" value="([0-9a-f]+)"', text)
    if m_chal:
        chal = m_chal.group(1)
        bfu_m = re.search(r'name="bfu" value="([^"]+)"', text)
        bfu = bfu_m.group(1) if bfu_m else path
        math_expr = re.search(r"value=([0-9+\-*]+);", text).group(1)
        ans = str(eval(math_expr))
        opener.open(f"{BASE_URL}/bf.jquery.max.js?bf_challenge={chal}", timeout=15).read()
        time.sleep(5.2)
        data = urllib.parse.urlencode(
            {"bf_challenge": chal, "bfu": bfu, "blazing_answer": ans}
        ).encode("utf-8")
        raw = opener.open(f"{BASE_URL}/blzgfst-shark/", data=data, timeout=15).read()
    return raw


def parse_live_class_html(html: str):
    pushes = re.findall(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', html, re.DOTALL)
    full_stream = "".join(json.loads('"' + p + '"') for p in pushes)

    refs = {}
    for line in full_stream.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            if val.startswith("[") or val.startswith("{"):
                try:
                    refs[key] = json.loads(val)
                except Exception:
                    pass

    def resolve(node):
        if isinstance(node, str) and node.startswith("$L"):
            ref_key = node[2:]
            if ref_key in refs:
                return resolve(refs[ref_key])
        elif isinstance(node, list):
            return [resolve(x) for x in node]
        elif isinstance(node, dict):
            return {k: resolve(v) for k, v in node.items()}
        return node

    talents = []
    seen = set()

    def walk(node):
        if isinstance(node, list):
            if (
                len(node) >= 4
                and node[0] == "$"
                and node[1] == "$L1c"
                and isinstance(node[3], dict)
            ):
                props = resolve(node[3])
                if "i" in props and "ranks" in props and "tooltip" in props:
                    pos = int(props["i"])
                    tree = int(props["index"])
                    if (tree, pos) in seen:
                        return
                    seen.add((tree, pos))
                    row = (pos // 4) + 1
                    col = (pos % 4) + 1
                    icon = str(props["icon"]).strip().lower()
                    ranks = int(props["ranks"])
                    requires = props.get("requires")
                    req_ranks = props.get("reqRanks")
                    tooltip = props["tooltip"]
                    name = tooltip[0][3]["children"]
                    desc_children = tooltip[3][3]["children"]
                    if isinstance(desc_children, str):
                        desc = desc_children
                    else:
                        parts = []
                        for c in desc_children:
                            if isinstance(c, str):
                                parts.append(c)
                            elif (
                                isinstance(c, list)
                                and len(c) >= 4
                                and isinstance(c[3], dict)
                                and "values" in c[3]
                            ):
                                parts.append("/".join(str(v) for v in c[3]["values"]))
                        desc = "".join(parts)
                    # Normalize line endings and double spaces for clean tooltips
                    desc = re.sub(r"\r\n", "\n", desc).strip()
                    talents.append(
                        {
                            "tree": tree,
                            "row": row,
                            "col": col,
                            "pos": pos,
                            "name": name,
                            "icon": icon,
                            "ranks": ranks,
                            "requires_pos": requires if requires != "$undefined" else None,
                            "req_ranks": req_ranks if req_ranks != "$undefined" else None,
                            "desc": desc,
                        }
                    )
                    return
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)

    for v in refs.values():
        walk(v)

    pos_to_name = {(t["tree"], t["pos"]): t["name"] for t in talents}
    for t in talents:
        if t["requires_pos"] is not None:
            req_name = pos_to_name.get((t["tree"], t["requires_pos"]))
            if req_name:
                t["req"] = [req_name, t["req_ranks"]]
        del t["requires_pos"]
        del t["req_ranks"]

    talents.sort(key=lambda x: (x["tree"], x["pos"]))
    return talents


def sync_all(use_cached_if_available: bool = True):
    opener = create_octowow_opener()

    # Load existing translations/builds reference if available
    step_ref_path = r"C:\Users\Tomas\.gemini\antigravity-ide\brain\52fdd071-d17b-4c15-a127-03cf4f3c6584\.system_generated\steps\1177\content.md"
    dane_ref = {}
    buildy_ref = {}
    if os.path.exists(step_ref_path):
        with open(step_ref_path, "r", encoding="utf-8") as f:
            st = f.read()
        m1 = re.search(r"const DANE = ({.*?});\s*const", st, re.DOTALL)
        m2 = re.search(r"const BUILDY = ({.*?});", st, re.DOTALL)
        if m1:
            dane_ref = json.loads(m1.group(1))
        if m2:
            buildy_ref = json.loads(m2.group(1))

    custom_translations = {
        "Pathfinding": {
            "descPl": "Zwiększa bonus do prędkości z Aspect of the Cheetah i Aspect of the Pack o 3/6% oraz zwiększa prędkość ruchu twojego zwierzaka o 15/30%.",
            "descDe": "Erhöht den Geschwindigkeitsbonus Eurer Aspekte des Geparden und des Rudels um 3/6% und erhöht das Bewegungstempo Eures Begleiters um 15/30%.",
            "descFr": "Augmente le bonus de vitesse de vos Aspects du guépard et de la meute de 3/6% et augmente la vitesse de déplacement de votre familier de 15/30%.",
            "descEs": "Aumenta la bonificación de velocidad de tu Aspecto del guepardo y Aspecto de la manada un 3/6% y aumenta la velocidad de movimiento de tu mascota un 15/30%.",
            "descIt": "Aumenta il bonus alla velocità di Aspect of the Cheetah e Aspect of the Pack del 3/6% e aumenta la velocità di movimento del tuo famiglio del 15/30%.",
            "descPt": "Aumenta o bônus de velocidade do seu Aspect of the Cheetah e Aspect of the Pack em 3/6% e aumenta a velocidade de movimento do seu ajudante em 15/30%.",
            "descRu": "Увеличивает бонус к скорости от «Духа гепарда» и «Духа стаи» на 3/6% и повышает скорость передвижения вашего питомца на 15/30%.",
        },
        "Alone Against the World": {
            "descPl": "Gdy nie kontrolujesz żadnego zwierzaka, wszystkie zadawane przez ciebie obrażenia są zwiększone o 3/6%.",
            "descDe": "Solange Ihr keinen Begleiter kontrolliert, ist jeglicher verursachter Schaden um 3/6% erhöht.",
            "descFr": "Tant que vous ne contrôlez aucun familier, tous les dégâts infligés sont augmentés de 3/6%.",
            "descEs": "Mientras no tengas ninguna mascota bajo tu control, todo el daño infligido aumenta un 3/6%.",
            "descIt": "Mentre non hai alcun famiglio sotto il tuo controllo, tutti i danni inflitti aumentano del 3/6%.",
            "descPt": "Enquanto você não tiver nenhum ajudante sob seu controle, todo o dano causado é aumentado em 3/6%.",
            "descRu": "Пока под вашим контролем нет питомца, весь наносимый урон увеличивается на 3/6%.",
        },
    }

    all_icons = set()

    for cls in CLASSES:
        cache_file = f"scratch/octowow_live/{cls}.html"
        if use_cached_if_available and os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            os.makedirs("scratch/octowow_live", exist_ok=True)
            html = fetch_octo_path(opener, f"/talents/{cls}/").decode("utf-8", "ignore")
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(html)

        live_talents = parse_live_class_html(html)

        # Load existing file or DANE reference for localized descriptions
        existing_by_name = {}
        existing_builds = []
        out_path = f"data/{cls}_talents.json"
        if os.path.exists(out_path):
            with open(out_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                for t in old_data.get("talents", []):
                    existing_by_name[t["name"]] = t
                existing_builds = old_data.get("builds", [])

        dane_by_name = {}
        if cls in dane_ref:
            for t in dane_ref[cls].get("t", []):
                dane_by_name[t["name"]] = t

        merged_talents = []
        for t in live_talents:
            name = t["name"]
            all_icons.add(t["icon"])
            ref_t = dane_by_name.get(name) or existing_by_name.get(name) or {}
            cust_t = custom_translations.get(name, {})

            entry = {
                "tree": t["tree"],
                "row": t["row"],
                "col": t["col"],
                "pos": t["pos"],
                "name": name,
                "icon": t["icon"],
                "ranks": t["ranks"],
            }
            if "req" in t:
                entry["req"] = t["req"]

            entry["desc"] = t["desc"]
            for lang_key in ["descPl", "descDe", "descFr", "descEs", "descIt", "descPt", "descRu"]:
                if lang_key in cust_t:
                    entry[lang_key] = cust_t[lang_key]
                elif lang_key in ref_t:
                    entry[lang_key] = ref_t[lang_key]
                else:
                    entry[lang_key] = t["desc"]

            merged_talents.append(entry)

        builds = buildy_ref.get(cls, existing_builds)
        if cls == "hunter":
            # Add a dedicated PvE Melee Survival build alongside the 3 official octowow.st builds
            has_pve_surv = any(b.get("nazwa") == "Survival Melee (PvE)" for b in builds)
            if not has_pve_surv:
                builds = list(builds) + [
                    {
                        "nazwa": "Survival Melee (PvE)",
                        "opis": "Maksymalne obrażenia w zwarciu pod makro rotacji Survival: Raptor Strike, Mongoose Bite, Carve, Immolation Trap, Lacerate i Wing Clip z pełnym skalowaniem Agility przez Lightning Reflexes.",
                        "tryb": "PvE",
                        "opisEn": "Maximum melee single-target & cleave DPS for Survival macro rotation: Raptor Strike, Mongoose Bite, Carve, Immolation Trap, Lacerate, and Wing Clip with Lightning Reflexes Agility-to-AP scaling.",
                        "ikona": "ability_hunter_swiftstrike",
                        "kolejnosc": [
                            "Improved Slaying 3, Swift Reflexes 2 i Savage Strikes 2 — prędkość ataku, obrażenia off-handu i szansa na krytyk uderzeń.",
                            "Carve 1, Stinging Nettle 2 i Surefooted 3 — trafienie (Hit) oraz nakładanie Serpent Sting z Mongoose Bite i pułapek.",
                            "Killer Instinct 3, Trap Mastery 3 i Lacerate 1 — +20% obrażeń krytycznych w zwarciu oraz krwawienie po krytyku.",
                            "Vicious Strikes 2 (-1s CD i +10% obrażeń Raptor Strike / Mongoose Bite), Lightning Reflexes 5 (+10% Agility i +100% Agility do Melee AP) oraz Untamed Trapper 1 (pułapki w walce skalowane z Melee AP).",
                            "Beast Mastery: Swift Aspects 5, Endurance Training 5, Unleashed Fury 5, Coordinated Assault 1 i Ferocity 4 dla synergii ze zwierzakiem."
                        ],
                        "kolejnoscEn": [
                            "Improved Slaying 3, Swift Reflexes 2 and Savage Strikes 2 — attack speed, off-hand damage and strike crit.",
                            "Carve 1, Stinging Nettle 2 and Surefooted 3 — hit chance and Serpent Sting application on Mongoose Bite & Fire traps.",
                            "Killer Instinct 3, Trap Mastery 3 and Lacerate 1 — +20% melee crit damage bonus and bleed after crits.",
                            "Vicious Strikes 2 (-1s CD and +10% Raptor/Mongoose damage), Lightning Reflexes 5 (+10% Agility and +100% Agility as Melee AP), and Untamed Trapper 1.",
                            "Beast Mastery: Swift Aspects 5, Endurance Training 5, Unleashed Fury 5, Coordinated Assault 1 and Ferocity 4."
                        ],
                        "uwagi": [
                            "Untamed Trapper pozwala kłaść Immolation Trap w trakcie walki i skaluje jej obrażenia z twoim Melee Attack Power.",
                            "Jeśli grasz bez zwierzaka (Brak Peta), weź 2/2 Alone Against the World (+6% wszystkich obrażeń)."
                        ],
                        "uwagiEn": [
                            "Untamed Trapper allows placing Immolation Trap in combat and scales its damage with your Melee Attack Power.",
                            "If playing without a pet, take 2/2 Alone Against the World (+6% all damage dealt)."
                        ],
                        "pkt": {
                            "2|Improved Slaying": 3,
                            "2|Resourcefulness": 2,
                            "2|Swift Reflexes": 2,
                            "2|Savage Strikes": 2,
                            "2|Planning Ahead": 2,
                            "2|Survivalist": 3,
                            "2|Carve": 1,
                            "2|Stinging Nettle": 2,
                            "2|Surefooted": 3,
                            "2|Killer Instinct": 3,
                            "2|Trap Mastery": 3,
                            "2|Lacerate": 1,
                            "2|Vicious Strikes": 2,
                            "2|Lightning Reflexes": 5,
                            "2|Untamed Trapper": 1,
                            "0|Swift Aspects": 5,
                            "0|Endurance Training": 5,
                            "0|Coordinated Assault": 1,
                            "0|Unleashed Fury": 5
                        }
                    }
                ]

        for b in builds:
            if b.get("ikona"):
                all_icons.add(b["ikona"].strip().lower())

        out_obj = {
            "trees": TREE_NAMES[cls],
            "talents": merged_talents,
            "builds": builds,
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out_obj, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved {out_path}: {len(merged_talents)} talents, {len(builds)} builds")

    # Check and download any missing icons from https://octowow.st/talents/icons/
    icons_dir = os.path.join("static", "icons", "talents")
    os.makedirs(icons_dir, exist_ok=True)
    missing_icons = []
    for ic in sorted(all_icons):
        local_png = os.path.join(icons_dir, f"{ic}.png")
        if not os.path.exists(local_png) or os.path.getsize(local_png) < 100:
            missing_icons.append(ic)

    print(f"Checking {len(all_icons)} talent icons ({len(missing_icons)} missing locally)...")
    for ic in missing_icons:
        local_png = os.path.join(icons_dir, f"{ic}.png")
        try:
            img_bytes = fetch_octo_path(opener, f"/talents/icons/{ic}.png")
            if img_bytes.startswith(b"\x89PNG"):
                with open(local_png, "wb") as f:
                    f.write(img_bytes)
                print(f"  [DOWNLOADED] {ic}.png ({len(img_bytes)} bytes)")
            else:
                print(f"  [WARN] {ic}.png did not return PNG header ({len(img_bytes)} bytes)")
        except Exception as e:
            print(f"  [ERR] Failed to download {ic}.png: {e}")


if __name__ == "__main__":
    use_cache = "--live" not in sys.argv
    sync_all(use_cached_if_available=use_cache)
