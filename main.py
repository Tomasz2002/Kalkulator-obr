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

    profile = PaladinCombatProfile(
        weapon_speed=weapon_speed,
        haste_percent=haste_percent,
        seal_active=True,
        t2_instances_per_swing=3,
        judgement_interval=judgement_interval,
        t2_instances_per_judgement=3,
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
        **kwargs,
    )


if __name__ == "__main__":
    db = load_items_db()
    print(f"Loaded items database with {db['metadata']['total_items']} items.\n")

    pre_raid_loadout = [11684, 11815, 13965, 12930, 16726]
    t2_judgement_loadout = [19364, 16955, 16953, 16958, 16957, 16956, 16952, 16954, 16951, 19379]
    t3_naxx_loadout = [22691, 22424, 22425, 22808, 22954, 60799]
    karazhan_loadout = [61247, 61246, 61270, 61262, 61443, 60799]
    nekrodyn_full_lost = [60790, 60799, 60809, 11684, 16958]

    scenarios = [
        ("Pre-Raid Dungeon Loadout (Ironfoe 2.4s + HoJ + BB)", pre_raid_loadout),
        ("Tier 2 Judgement Full Set (Ashkandi 3.5s + T2 8/8)", t2_judgement_loadout),
        ("Naxxramas End-Game Loadout (Corrupted Ashbringer 3.6s + T3)", t3_naxx_loadout),
        ("Karazhan 40 Loadout (Shadowbringer 3.3s + Kara Plate)", karazhan_loadout),
        ("Nekrodyn Optimal BiS (Ironfoe 2.4s + Set of the Lost + T2 Bonus)", nekrodyn_full_lost),
    ]

    for title, loadout in scenarios:
        res = simulate_combat(loadout, fight_duration=60.0, db=db)
        print("=" * 65)
        print(f"Scenario: {title}")
        print(f"  Weapon: {res['weapon_name']} | Swing Timer: {res['base_weapon_speed']}s (Effective: {res['effective_weapon_speed']}s)")
        print(f"  Exact Melee Swings (60s): {res['exact_melee_swings']}")
        print(f"  AP: {res['total_attack_power']} | SP: {res['total_spell_power']} | Crit: {res['total_crit_percent']}% | Hit: {res['total_hit_percent']}%")
        print(f"  Magic Hits: {res['total_magic_hits']} ({res['magic_hits_per_second']}/s) -> Procs/s: {res['procs_per_second']} -> Active Minions: {res['expected_active_minions']}")
        print(f"  Own Damage Breakdown (DPS):")
        for k, v in res["own_damage_breakdown"].items():
            print(f"    - {k}: {v:.2f}")
        print(f"  -> OWN DPS: {res['own_dps']:.2f}")
        print(f"  -> MINION DPS: {res['minion_dps']:.2f} (Range: {res['minion_dps_min']:.2f} - {res['minion_dps_max']:.2f})")
        print(f"  ==> TOTAL CHARACTER DPS: {res['total_dps']:.2f} (Total Damage: {res['total_damage']:.1f})")
        print()
