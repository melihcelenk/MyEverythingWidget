"""
Collision detection for grid items.

Handles:
- Occupied cell tracking
- Collision detection between items
- Finding available cells
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Set, Tuple, Optional

from window.grid.constants import GRID_COLS, GRID_ROWS

if TYPE_CHECKING:
    pass


@dataclass
class GridItem:
    """Represents an item's position and span in the grid."""
    id: str
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1

    def get_cells(self) -> Set[Tuple[int, int]]:
        """Get all cells occupied by this item."""
        cells = set()
        for r in range(self.row, self.row + self.row_span):
            for c in range(self.col, self.col + self.col_span):
                cells.add((r, c))
        return cells


class CollisionDetector:
    """Detects and handles grid cell collisions."""

    def __init__(self):
        self._occupied: Set[Tuple[int, int]] = set()
        self._item_cells: dict[str, Set[Tuple[int, int]]] = {}

    def clear(self):
        """Clear all occupation data."""
        self._occupied.clear()
        self._item_cells.clear()

    def add_item(self, item: GridItem) -> bool:
        """
        Add an item to the grid.
        
        Returns:
            True if added successfully, False if collision detected.
        """
        cells = item.get_cells()

        # Check for collision
        if cells & self._occupied:
            return False

        # Mark cells as occupied
        self._occupied.update(cells)
        self._item_cells[item.id] = cells
        return True

    def remove_item(self, item_id: str):
        """Remove an item from the grid."""
        if item_id in self._item_cells:
            cells = self._item_cells.pop(item_id)
            self._occupied -= cells

    def check_collision(self, row: int, col: int,
                        row_span: int = 1, col_span: int = 1,
                        exclude_id: Optional[str] = None) -> Set[Tuple[int, int]]:
        """
        Check if placing an item would cause collision.
        
        Args:
            row: Target row
            col: Target column
            row_span: Number of rows
            col_span: Number of columns
            exclude_id: Item ID to exclude from collision check (for moving items)
            
        Returns:
            Set of colliding cells (empty if no collision)
        """
        target_cells = set()
        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                target_cells.add((r, c))

        # Get occupied cells excluding the specified item
        occupied = self._occupied.copy()
        if exclude_id and exclude_id in self._item_cells:
            occupied -= self._item_cells[exclude_id]

        return target_cells & occupied

    def find_colliding_item(self, cells: Set[Tuple[int, int]],
                            exclude_id: Optional[str] = None) -> Optional[str]:
        """Find which item occupies any of the given cells."""
        for item_id, item_cells in self._item_cells.items():
            if item_id == exclude_id:
                continue
            if item_cells & cells:
                return item_id
        return None

    def is_valid_position(self, row: int, col: int,
                          row_span: int = 1, col_span: int = 1) -> bool:
        """Check if position is within grid bounds."""
        if row < 0 or col < 0:
            return False
        if row + row_span > GRID_ROWS:
            return False
        if col + col_span > GRID_COLS:
            return False
        return True

    def get_occupied_cells(self) -> Set[Tuple[int, int]]:
        """Get all currently occupied cells."""
        return self._occupied.copy()
