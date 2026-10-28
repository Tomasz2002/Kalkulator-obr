from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from src.calculators import get_calculator
from src.items_db import calculate_gear_totals, get_item, load_items_db


@dataclass
class PaladinCombatProfile:
    weapon_speed: float = 3.8
    haste_percent: float = 0.0
    seal_active: bool = True
    t2_instances_per_swing: int = 3
    judgement_interval: float = 10.0
    t2_instances_per_judgement: int = 3
    consecration_ticks_per_second: float = 1.0
    exorcism_interval: float = 15.0
    holy_shock_interval: float = 0.0
    extra_magic_hits_per_second: float = 0.0
    attack_power: int = 0
    spell_power: int = 0
    crit_percent: float = 0.0
    hit_percent: float = 0.0


@dataclass
class MinionStats:
    cast_time: float = 2.0
    min_damage: float = 230.0
    max_damage: float = 279.0
    avg_damage: float = 254.5
    lifetime: float = 20.0
    proc_chance: float = 0.04


def calculate_effective_weapon_speed(base_speed: float, haste_percent: float) -> float:
    return base_speed / (1.0 + (haste_percent / 100.0))


def calculate_swings_per_second(weapon_speed: float, haste_percent: float = 0.0) -> float:
    effective_speed = calculate_effective_weapon_speed(weapon_speed, haste_percent)
    return 1.0 / effective_speed if effective_speed > 0 else 0.0


def calculate_magic_hits_per_swing(seal_active: bool = True, t2_instances: int = 3) -> int:
    seal_hits = 1 if seal_active else 0
    return seal_hits + t2_instances


def calculate_magic_hits_per_second(profile: PaladinCombatProfile) -> float:
    swings_per_sec = calculate_swings_per_second(profile.weapon_speed, profile.haste_percent)
    hits_per_swing = calculate_magic_hits_per_swing(profile.seal_active, profile.t2_instances_per_swing)
    swing_magic_hits = swings_per_sec * hits_per_swing

    judgement_magic_hits = 0.0
    if profile.judgement_interval > 0:
        judgement_magic_hits = (1.0 / profile.judgement_interval) * (1 + profile.t2_instances_per_judgement)

    exorcism_hits = (1.0 / profile.exorcism_interval) if profile.exorcism_interval > 0 else 0.0
    holy_shock_hits = (1.0 / profile.holy_shock_interval) if profile.holy_shock_interval > 0 else 0.0

    spell_hits = profile.consecration_ticks_per_second + exorcism_hits + holy_shock_hits + profile.extra_magic_hits_per_second

    return swing_magic_hits + judgement_magic_hits + spell_hits


def calculate_procs_per_second(magic_hits_per_second: float, proc_chance: float = 0.04) -> float:
    return magic_hits_per_second * proc_chance


def calculate_expected_active_minions(procs_per_second: float, minion_lifetime: float = 20.0) -> float:
    return procs_per_second * minion_lifetime


def calculate_single_minion_dps(minion: MinionStats = MinionStats()) -> Dict[str, float]:
    min_dps = minion.min_damage / minion.cast_time
    max_dps = minion.max_damage / minion.cast_time
    avg_dps = minion.avg_damage / minion.cast_time
    return {
        "min_dps": min_dps,
        "max_dps": max_dps,
        "avg_dps": avg_dps,
    }


def calculate_expected_minion_dps(expected_minions: float, minion: MinionStats = MinionStats()) -> Dict[str, float]:
    single_dps = calculate_single_minion_dps(minion)
    return {
        "min_dps": expected_minions * single_dps["min_dps"],
        "max_dps": expected_minions * single_dps["max_dps"],
        "avg_dps": expected_minions * single_dps["avg_dps"],
    }


def calculate_nekrodyn_dps(profile: PaladinCombatProfile, minion: MinionStats = MinionStats()) -> Dict[str, Any]:
    hits_per_sec = calculate_magic_hits_per_second(profile)
    procs_per_sec = calculate_procs_per_second(hits_per_sec, minion.proc_chance)
    expected_minions = calculate_expected_active_minions(procs_per_sec, minion.lifetime)
    dps_results = calculate_expected_minion_dps(expected_minions, minion)
    return {
        "effective_weapon_speed": calculate_effective_weapon_speed(profile.weapon_speed, profile.haste_percent),
        "swings_per_second": calculate_swings_per_second(profile.weapon_speed, profile.haste_percent),
        "magic_hits_per_second": hits_per_sec,
        "procs_per_second": procs_per_sec,
        "expected_active_minions": expected_minions,
        "minion_dps_min": dps_results["min_dps"],
        "minion_dps_max": dps_results["max_dps"],
        "minion_dps_avg": dps_results["avg_dps"],
        "attack_power": profile.attack_power,
        "spell_power": profile.spell_power,
        "crit_percent": profile.crit_percent,
        "hit_percent": profile.hit_percent,
    }


def build_profile_from_equipment(
    equipped_ids: List[Union[int, str]],
    base_weapon_speed: Optional[float] = None,
    haste_percent: float = 0.0,
    consecration_ticks_per_second: float = 1.0,
    judgement_interval: float = 10.0,
    db: Optional[Dict] = None,
) -> Tuple[PaladinCombatProfile, Dict]:
    gear = calculate_gear_totals(equipped_ids, db)
    weapon_speed = base_weapon_speed or (gear["main_weapon_speed"] if gear["main_weapon_speed"] > 0 else 3.8)
    active_sets = gear.get("active_sets", {})
    t2_tank_3pc = 1 if active_sets.get("2004", {}).get("equipped_count", 0) >= 3 else 0
    t2_dps_3pc = 1 if active_sets.get("2005", {}).get("equipped_count", 0) >= 3 else 0
    t2_instances = t2_tank_3pc + t2_dps_3pc

    profile = PaladinCombatProfile(
        weapon_speed=weapon_speed,
        haste_percent=haste_percent,
        seal_active=True,
        t2_instances_per_swing=t2_instances,
        judgement_interval=judgement_interval,
        t2_instances_per_judgement=0,
        consecration_ticks_per_second=consecration_ticks_per_second,
        attack_power=gear["total_attack_power"],
        spell_power=gear["spell_power"],
        crit_percent=gear["total_melee_crit"],
        hit_percent=gear["hit"],
    )
    return profile, gear


def simulate_combat(
    equipped_items: List[Union[int, str, Dict]],
    fight_duration: float = 60.0,
    haste_percent: float = 0.0,
    target_armor: float = 3731.0,
    judgement_interval: float = 10.0,
    consecration: bool = True,
    exorcism_interval: float = 15.0,
    t2_bonus_active: bool = True,
    lost_set_active: bool = True,
    minion_stats: Optional[MinionStats] = None,
    db: Optional[Dict] = None,
    character_class: str = "paladin",
    paladin_build: str = "auto",
    rotation_mode: str = "priority_rotation",
    priority_list: Optional[List[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    calculator = get_calculator(character_class, db=db)
    return calculator.calculate(
        equipped_items=equipped_items,
        fight_duration=fight_duration,
        haste_percent=haste_percent,
        target_armor=target_armor,
        judgement_interval=judgement_interval,
        consecration=consecration,
        exorcism_interval=exorcism_interval,
        t2_bonus_active=t2_bonus_active,
        lost_set_active=lost_set_active,
        paladin_build=paladin_build,
        rotation_mode=rotation_mode,
        priority_list=priority_list,
        **kwargs,
    )


if __name__ == "__main__":
    db = load_items_db()
    print(f"Loaded items database with {db['metadata']['total_items']} items.\n")

    classic_ret_gear = [19364, 16955, 16953, 16958, 16957, 16956, 16952, 16954, 16951, 19379, 11815, 13965, 19434, 19384]
    classic_ret_talents = {
        "Divine Strength": 5,
        "Conviction": 5,
        "Two-Handed Weapon Specialization": 3,
        "Seal of Command": 1,
        "Vengeance": 5,
        "Sanctity Aura": 1,
        "Blessing of Kings": 1,
        "Improved Judgement": 2,
        "Precision": 3,
    }

    spellret_gear = [11684, 12462, 19138, 16812, 16817, 16813, 19142, 19147, 19137, 19139, 19434, 19384]
    spellret_talents = {
        "Divine Strength": 5,
        "Divine Intellect": 5,
        "Improved Seal of Righteousness": 5,
        "Sanctity Aura": 1,
        "Conviction": 5,
        "Vengeance": 5,
        "Improved Judgement": 2,
        "Precision": 3,
        "One-Handed Spec": 5,
        "Blessing of Kings": 1,
    }

    # Set of the Lost consists strictly of 4 items: Memento of the Lost (60790), Remains of the Lost (60809), Loop of the Lost (60798), Tome of the Lost (22253)
    nekrodyn_gear = [60790, 60798, 60809, 22253, 11684, 47016, 47017, 47019, 47026, 47029, 47030, 11815, 19434]
    nekrodyn_talents = {
        "Divine Strength": 5,
        "Divine Intellect": 5,
        "Improved Seal of Righteousness": 5,
        "Sanctity Aura": 1,
        "Precision": 3,
        "Conviction": 5,
        "Vengeance": 5,
        "Improved Judgement": 2,
        "Blessing of Kings": 1,
    }

    scenarios = [
        ("Czysty Build Fizyczny (Strength / Retribution) - Pełna Rotacja", classic_ret_gear, classic_ret_talents, "retribution", "priority_rotation", None),
        ("Czysty Build Fizyczny (Strength / Retribution) - Uproszczony Tryb (Tylko Auto Attacki + Seal)", classic_ret_gear, classic_ret_talents, "retribution", "auto_attack_only", None),
        ("Build Hybrydowy (Spellret / Spell Power & Consecration) - Pełna Rotacja", spellret_gear, spellret_talents, "spellret", "priority_rotation", None),
        ("Build Hybrydowy (Spellret) - Wlasny Planer Priorytetow (Consecration Nr 1)", spellret_gear, spellret_talents, "spellret", "priority_rotation", ["consecration", "crusader_strike", "holy_strike", "judgement", "exorcism"]),
        ("Build Specjalny (Nekrodyn: Set of the Lost + 3x T2 Tank + 3x T2 DPS)", nekrodyn_gear, nekrodyn_talents, "nekrodyn", "priority_rotation", None),
    ]

    for title, loadout, talents, build_type, rot_mode, custom_pri in scenarios:
        res = simulate_combat(
            loadout,
            fight_duration=60.0,
            talents=talents,
            paladin_build=build_type,
            rotation_mode=rot_mode,
            priority_list=custom_pri,
            db=db,
        )
        print("=" * 76)
        print(f"SCENARIUSZ: {title}")
        print(f"  Tryb walki: {res['rotation_mode_name']} | Build: {res['paladin_build_name']} | Broń: {res['weapon_name']} ({res['base_weapon_speed']}s)")
        print(f"  Priorytety rotacji: {res['priority_list']}")
        print(f"  Zeal Buff Haste (Crusader Strike): +{res.get('zeal_haste_percent', 0.0)}% haste | Efektywny Swing Speed: {res.get('effective_weapon_speed', 0.0)}s")
        print(f"  Rzucone skille (Casts): {res['ability_casts']}")
        print(f"  Zużycie many: {res['mana_stats']['total_mana_spent']} mana ({res['mana_stats']['mana_per_second']} mana/s)")
        print(f"  Swings: {res['exact_melee_swings']} | AP: {res['total_attack_power']} | SP: {res['total_spell_power']} | Crit: {res['total_crit_percent']}% | Hit: {res['total_hit_percent']}%")
        print(f"  Harmful Spell Hits: {res['total_magic_hits']} ({res['magic_hits_per_second']}/s) | Minion Procs/s: {res['procs_per_second']} | Aktywne Miniony: {res['expected_active_minions']}")
        print(f"  PODZIAŁ TYPÓW OBRAŻEŃ (DPS):")
        dtb = res.get("damage_type_breakdown", {})
        print(f"    - Obrażenia fizyczne: {dtb.get('physical_dps', 0.0):.2f} DPS ({dtb.get('physical_percent', 0.0)}%)")
        print(f"    - Obrażenia od czarów (Holy): {dtb.get('holy_spell_dps', 0.0):.2f} DPS ({dtb.get('holy_spell_percent', 0.0)}%)")
        print(f"    - Obrażenia z minionów (Shadow): {dtb.get('minion_shadow_dps', 0.0):.2f} DPS ({dtb.get('minion_shadow_percent', 0.0)}%)")
        print(f"  Szczegółowy rozkład ataków gracza:")
        for k, v in res["own_damage_breakdown"].items():
            print(f"    - {k}: {v:.2f} DPS")
        print(f"  -> DIRECT CHARACTER DPS: {res['own_dps']:.2f}")
        print(f"  -> MINION DPS: {res['minion_dps']:.2f} (Przedział: {res['minion_dps_min']:.2f} - {res['minion_dps_max']:.2f})")
        print(f"  ==> CAŁKOWITY DPS POSTACI: {res['total_dps']:.2f} (Łączne obrażenia: {res['total_damage']:.1f})")
        print()
