import json

with open('data/warrior_talents.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

builds = [
    {
        "nazwa": "Fury Dual Wield (17/34/0)",
        "opis": "Najpopularniejszy raidowy build PvE dla Wojownika DW: Flurry, Bloodthirst, Death Wish oraz Deep Wounds i Impale z drzewka Arms.",
        "tryb": "PvE",
        "opisEn": "Standard raid Fury Dual Wield build: Flurry, Bloodthirst, Death Wish with Deep Wounds and Impale from Arms.",
        "ikona": "ability_warrior_innerrage",
        "kolejnosc": [
            "Cruelty 5 - natychmiastowe +5% szansy na krytyk.",
            "Unbridled Wrath 5 - generowanie dodatkowego Rage przy uderzeniach.",
            "Dual Wield Specialization 5 - wiekszy dmg z lewej reki.",
            "Enrage 5 i Flurry 5 - gigantyczny wzrost szybkosci ataku po krytyku.",
            "Death Wish 1 i Bloodthirst 1 - glowne cooldowny i atak.",
            "W Arms: Tactical Mastery 5, Improved Overpower 2, Deep Wounds 3 i Impale 2."
        ],
        "kolejnoscEn": [
            "Cruelty 5 - instant +5% melee crit chance.",
            "Unbridled Wrath 5 - generates additional Rage on melee swings.",
            "Dual Wield Specialization 5 - increases off-hand damage.",
            "Enrage 5 and Flurry 5 - massive attack speed boost following critical hits.",
            "Death Wish 1 and Bloodthirst 1 - core burst cooldown and AP-scaling strike.",
            "In Arms: Tactical Mastery 5, Improved Overpower 2, Deep Wounds 3 and Impale 2."
        ],
        "uwagi": [
            "Dla optymalnego DPS trzymaj Flurry aktywne tak czesto jak mozliwe.",
            "W fazie egzekucji (<20% HP) uzywaj Execute z zachowaniem Bloodthirst jesli rage pozwala."
        ],
        "uwagiEn": [
            "Keep Flurry up as much as possible for sustained rage and DPS.",
            "During execute phase (<20% boss HP), utilize Execute aggressively."
        ],
        "pkt": {
            "1|Cruelty": 5,
            "1|Unbridled Wrath": 5,
            "1|Dual Wield Specialization": 5,
            "1|Enrage": 5,
            "1|Death Wish": 1,
            "1|Improved Execute": 2,
            "1|Flurry": 5,
            "1|Bloodthirst": 1,
            "0|Tactical Mastery": 5,
            "0|Improved Rend": 3,
            "0|Deflection": 2,
            "0|Improved Overpower": 2,
            "0|Deep Wounds": 3,
            "0|Impale": 2
        }
    },
    {
        "nazwa": "Arms 2-Hand (31/20/0)",
        "opis": "Klasyczny build dwureczny pod Mortal Strike, Two-Handed Weapon Spec, Sweeping Strikes oraz Flurry/Cruelty z Fury.",
        "tryb": "PvE/PvP",
        "opisEn": "Classic Two-Handed build featuring Mortal Strike, Two-Handed Weapon Spec, Sweeping Strikes, and Fury crit/haste.",
        "ikona": "ability_warrior_savageblow",
        "kolejnosc": [
            "Tactical Mastery 5 i Improved Heroic Strike 3.",
            "Deep Wounds 3, Two-Handed Weapon Specialization 5 i Impale 2.",
            "Sweeping Strikes 1 i Mortal Strike 1.",
            "W Fury: Cruelty 5, Unbridled Wrath 5, Enrage 5."
        ],
        "kolejnoscEn": [
            "Tactical Mastery 5 and Improved Heroic Strike 3.",
            "Deep Wounds 3, Two-Handed Weapon Specialization 5 and Impale 2.",
            "Sweeping Strikes 1 and Mortal Strike 1.",
            "In Fury: Cruelty 5, Unbridled Wrath 5, Enrage 5."
        ],
        "uwagi": [
            "Mortal Strike zadaje potezne natychmiastowe obrazenia broni dwurecznej.",
            "Dwureczna bron ma mniejszy miss penalty na bialych atakach niz Dual Wield (8% vs 24%)."
        ],
        "uwagiEn": [
            "Mortal Strike delivers massive instant weapon damage normalized for 2-handers.",
            "Two-handed weapons only suffer 8% base white miss penalty compared to 24% for dual wielding."
        ],
        "pkt": {
            "0|Improved Heroic Strike": 3,
            "0|Tactical Mastery": 5,
            "0|Improved Overpower": 2,
            "0|Deep Wounds": 3,
            "0|Two-Handed Weapon Specialization": 5,
            "0|Impale": 2,
            "0|Sweeping Strikes": 1,
            "0|Precision Cut": 5,
            "0|Mortal Strike": 1,
            "1|Cruelty": 5,
            "1|Unbridled Wrath": 5,
            "1|Enrage": 5,
            "1|Improved Execute": 2,
            "1|Death Wish": 1
        }
    },
    {
        "nazwa": "Protection Tank (11/5/35)",
        "opis": "Pancerny tank raidowy: Shield Slam, Defiance, One-Handed Spec, Toughness i Last Stand z wsparciem Tactical Mastery.",
        "tryb": "PvE",
        "opisEn": "Raid main tank build: Shield Slam, Defiance, One-Handed Spec, Toughness, and Last Stand.",
        "ikona": "inv_shield_06",
        "kolejnosc": [
            "Shield Specialization 5 i Toughness 5 w Protection.",
            "Last Stand 1, Defiance 5 i One-Handed Weapon Specialization 5.",
            "Shield Slam 1 - kluczowa zdolnosc generujaca wysokie zagrozenie.",
            "Tactical Mastery 5 w Arms."
        ],
        "kolejnoscEn": [
            "Shield Specialization 5 and Toughness 5 in Protection.",
            "Last Stand 1, Defiance 5 and One-Handed Weapon Specialization 5.",
            "Shield Slam 1 - primary high threat generator.",
            "Tactical Mastery 5 in Arms."
        ],
        "uwagi": [
            "Defiance zwieksza zagrozenie w Defensive Stance.",
            "Shield Slam skaluje sie z wartoscia bloku tarczy (Shield Block Value)."
        ],
        "uwagiEn": [
            "Defiance significantly boosts threat generation in Defensive Stance.",
            "Shield Slam scales directly with Shield Block Value."
        ],
        "pkt": {
            "2|Shield Specialization": 5,
            "2|Anticipation": 5,
            "2|Toughness": 5,
            "2|Last Stand": 1,
            "2|Defiance": 5,
            "2|One-Handed Weapon Specialization": 5,
            "2|Shield Slam": 1,
            "2|Improved Shield Slam": 2,
            "2|Concussion Blow": 1,
            "2|Reprisal": 3,
            "2|Defensive Tactics": 2,
            "0|Tactical Mastery": 5,
            "0|Deflection": 5,
            "0|Improved Overpower": 1,
            "1|Cruelty": 5
        }
    }
]

data['builds'] = builds
with open('data/warrior_talents.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated data/warrior_talents.json with builds successfully!")
