from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union


class BaseCombatCalculator(ABC):

    @abstractmethod
    def calculate(
        self,
        equipped_items: List[Union[int, str, Dict]],
        fight_duration: float = 60.0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        pass
