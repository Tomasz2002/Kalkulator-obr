from typing import Any, Dict, Optional

from .base import BaseCombatCalculator
from .hunter import HunterCombatCalculator
from .paladin import PaladinCombatCalculator

CALCULATORS = {
    "paladin": PaladinCombatCalculator,
    "hunter": HunterCombatCalculator,
}


def get_calculator(class_name: str, db: Optional[Dict] = None) -> BaseCombatCalculator:
    key = class_name.lower().strip()
    cls = CALCULATORS.get(key)
    if not cls:
        raise ValueError(f"Unknown class '{class_name}'. Supported classes: {list(CALCULATORS.keys())}")
    return cls(db=db)


__all__ = [
    "BaseCombatCalculator",
    "PaladinCombatCalculator",
    "HunterCombatCalculator",
    "get_calculator",
    "CALCULATORS",
]
