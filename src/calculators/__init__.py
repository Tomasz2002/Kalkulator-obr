from typing import Any, Dict, Optional

from .base import BaseCombatCalculator
from .generic import GenericCombatCalculator
from .hunter import HunterCombatCalculator
from .paladin import PaladinCombatCalculator
from .warrior import WarriorCombatCalculator

CALCULATORS = {
    "paladin": PaladinCombatCalculator,
    "warrior": WarriorCombatCalculator,
    "hunter": HunterCombatCalculator,
}


def get_calculator(class_name: str, db: Optional[Dict] = None) -> BaseCombatCalculator:
    key = class_name.lower().strip()
    if key == "paladin":
        return PaladinCombatCalculator(db=db)
    if key == "warrior":
        return WarriorCombatCalculator(db=db)
    if key == "hunter":
        return HunterCombatCalculator(db=db)
    return GenericCombatCalculator(class_name=key, db=db)


__all__ = [
    "BaseCombatCalculator",
    "PaladinCombatCalculator",
    "WarriorCombatCalculator",
    "HunterCombatCalculator",
    "GenericCombatCalculator",
    "get_calculator",
    "CALCULATORS",
]
