"""Data models for humanized UI tests."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GridItem:
    """Represents an item in the grid."""
    id: str
    item_type: str
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1


@dataclass
class CreateAction:
    """Represents a create action."""
    item_type: str  # 'NOTE' or 'APP'
    content: str  # Note content or app name
    item_id: str  # ID to assign (e.g., 'N1', 'A1')


@dataclass
class DragAction:
    """Represents a drag action."""
    item_id: str
    target_row: int
    target_col: int


@dataclass
class LaunchAction:
    """Represents a launch action (for apps)."""
    item_id: str  # ID of app to launch (e.g., 'A1')


@dataclass
class TestCase:
    """Represents a test case."""
    name: str
    rows: int = 5
    cols: int = 5
    initial_items: Dict[str, GridItem] = field(default_factory=dict)
    actions: List[DragAction | CreateAction | LaunchAction] = field(default_factory=list)
    # Legacy fields for backward compatibility
    action_item: str = ""
    action_target_row: int = 0
    action_target_col: int = 0
    expected_items: Dict[str, GridItem] = field(default_factory=dict)
