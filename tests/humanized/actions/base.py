"""Base class for action executors."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ActionExecutor(ABC):
    """Base class for executing test actions."""

    @abstractmethod
    def execute(self, action: Any, name_to_id: Dict[str, str], win_x: int, win_y: int) -> bool:
        """
        Execute an action.
        
        Args:
            action: The action to execute
            name_to_id: Mapping from test IDs (e.g., 'N1', 'A1') to actual item IDs
            win_x: Window X position
            win_y: Window Y position
        
        Returns:
            True if action succeeded, False otherwise
        """
        pass
