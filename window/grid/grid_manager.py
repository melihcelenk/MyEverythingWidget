"""
GridManager - Manages grid placement and layout.

Centralizes all grid-related logic for Android-like fixed grid behavior.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple, List

from window.grid.cell_calculator import CellCalculator
from window.grid.collision_detector import CollisionDetector, GridItem
from window.grid.constants import GRID_COLS, GRID_ROWS

if TYPE_CHECKING:
    pass


@dataclass
class PlacementResult:
    """Result of a placement operation."""
    success: bool
    row: int = 0
    col: int = 0
    message: str = ""


class GridManager:
    """
    Manages grid placement with Android-like behavior.
    
    Features:
    - Fixed 3x5 grid
    - No auto-compacting (gaps allowed)
    - Explicit positions for all items
    - Collision detection and swap logic
    """

    def __init__(self):
        self._detector = CollisionDetector()
        self._calculator = CellCalculator
        self._items: dict[str, GridItem] = {}

    def clear(self):
        """Clear all items from the grid."""
        self._detector.clear()
        self._items.clear()

    def add_item(self, item_id: str, row: int, col: int,
                 row_span: int = 1, col_span: int = 1) -> PlacementResult:
        """
        Add an item to the grid at a specific position.
        
        Args:
            item_id: Unique identifier for the item
            row: Grid row (0-based)
            col: Grid column (0-based)
            row_span: Number of rows the item occupies
            col_span: Number of columns the item occupies
            
        Returns:
            PlacementResult with success status
        """
        # Validate bounds
        if not self._detector.is_valid_position(row, col, row_span, col_span):
            return PlacementResult(
                success=False,
                message=f"Position ({row}, {col}) with span ({row_span}x{col_span}) out of bounds"
            )

        item = GridItem(
            id=item_id,
            row=row,
            col=col,
            row_span=row_span,
            col_span=col_span
        )

        # Check for collision
        if not self._detector.add_item(item):
            return PlacementResult(
                success=False,
                row=row,
                col=col,
                message=f"Collision at ({row}, {col})"
            )

        self._items[item_id] = item
        return PlacementResult(success=True, row=row, col=col)

    def remove_item(self, item_id: str) -> bool:
        """
        Remove an item from the grid.
        
        Args:
            item_id: ID of item to remove
            
        Returns:
            True if item was removed, False if not found
        """
        if item_id not in self._items:
            return False

        self._detector.remove_item(item_id)
        del self._items[item_id]
        return True

    def get_item(self, item_id: str) -> Optional[GridItem]:
        """Get an item by ID."""
        return self._items.get(item_id)

    def find_first_available(self, row_span: int = 1,
                             col_span: int = 1) -> Optional[Tuple[int, int]]:
        """
        Find the first available position for an item.
        
        Args:
            row_span: Number of rows needed
            col_span: Number of columns needed
            
        Returns:
            (row, col) tuple or None if grid is full
        """
        occupied = self._detector.get_occupied_cells()
        return self._calculator.find_first_available_cell(
            occupied, row_span, col_span
        )

    def auto_place_item(self, item_id: str,
                        row_span: int = 1,
                        col_span: int = 1) -> PlacementResult:
        """
        Automatically place an item at the first available position.
        
        Args:
            item_id: Unique identifier for the item
            row_span: Number of rows the item occupies
            col_span: Number of columns the item occupies
            
        Returns:
            PlacementResult with position if successful
        """
        position = self.find_first_available(row_span, col_span)

        if position is None:
            return PlacementResult(
                success=False,
                message="Grid is full"
            )

        row, col = position
        return self.add_item(item_id, row, col, row_span, col_span)

    def can_move_to(self, item_id: str, target_row: int, target_col: int) -> bool:
        """
        Check if an item can move to a target position.
        
        Args:
            item_id: ID of item to move
            target_row: Target row
            target_col: Target column
            
        Returns:
            True if the move is valid and no collision (excluding self)
        """
        item = self._items.get(item_id)
        if not item:
            return False

        # Check bounds
        if not self._detector.is_valid_position(
                target_row, target_col, item.row_span, item.col_span
        ):
            return False

        # Check collision excluding self
        collisions = self._detector.check_collision(
            target_row, target_col, item.row_span, item.col_span,
            exclude_id=item_id
        )

        return len(collisions) == 0

    def move_item(self, item_id: str,
                  target_row: int, target_col: int) -> PlacementResult:
        """
        Move an item to a new position.
        
        Args:
            item_id: ID of item to move
            target_row: Target row
            target_col: Target column
            
        Returns:
            PlacementResult with success status
        """
        item = self._items.get(item_id)
        if not item:
            return PlacementResult(
                success=False,
                message=f"Item {item_id} not found"
            )

        # Check bounds with span
        clamped_row, clamped_col = self._calculator.clamp_position(
            target_row, target_col, item.row_span, item.col_span
        )

        if not self.can_move_to(item_id, clamped_row, clamped_col):
            return PlacementResult(
                success=False,
                row=clamped_row,
                col=clamped_col,
                message="Cannot move to target position (collision)"
            )

        # Remove from old position
        self._detector.remove_item(item_id)

        # Add at new position
        new_item = GridItem(
            id=item_id,
            row=clamped_row,
            col=clamped_col,
            row_span=item.row_span,
            col_span=item.col_span
        )
        self._detector.add_item(new_item)
        self._items[item_id] = new_item

        return PlacementResult(success=True, row=clamped_row, col=clamped_col)

    def get_item_at(self, row: int, col: int) -> Optional[str]:
        """
        Get the item ID at a specific cell.
        
        Args:
            row: Grid row
            col: Grid column
            
        Returns:
            Item ID or None if cell is empty
        """
        return self._detector.find_colliding_item({(row, col)})

    def get_items_in_area(self, row: int, col: int,
                          row_span: int = 1, col_span: int = 1) -> List[str]:
        """
        Get all items that occupy any cell in the given area.
        
        Args:
            row: Start row
            col: Start column
            row_span: Number of rows
            col_span: Number of columns
            
        Returns:
            List of item IDs in the area
        """
        target_cells = set()
        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                target_cells.add((r, c))

        items_in_area = set()
        for item_id, item in self._items.items():
            if item.get_cells() & target_cells:
                items_in_area.add(item_id)

        return list(items_in_area)

    def try_swap(self, item_id: str,
                 target_row: int, target_col: int) -> Tuple[bool, Optional[str]]:
        """
        Try to swap an item with whatever is at the target position.
        
        Android-like behavior:
        - If target is empty, just move
        - If target has one item that fits in source, swap
        - Otherwise, reject
        
        Args:
            item_id: ID of item to move
            target_row: Target row
            target_col: Target column
            
        Returns:
            (success, swapped_item_id or None)
        """
        moving_item = self._items.get(item_id)
        if not moving_item:
            return (False, None)

        # Check bounds
        if not self._detector.is_valid_position(
                target_row, target_col, moving_item.row_span, moving_item.col_span
        ):
            return (False, None)

        # Get items in target area
        target_cells = set()
        for r in range(target_row, target_row + moving_item.row_span):
            for c in range(target_col, target_col + moving_item.col_span):
                target_cells.add((r, c))

        # Find colliding item (excluding self)
        colliding_id = self._detector.find_colliding_item(target_cells, exclude_id=item_id)

        if colliding_id is None:
            # Target is empty, just move
            result = self.move_item(item_id, target_row, target_col)
            return (result.success, None)

        # There's a colliding item - try to swap
        colliding_item = self._items.get(colliding_id)
        if not colliding_item:
            return (False, None)

        # Check if colliding item fits in moving item's source position
        source_row = moving_item.row
        source_col = moving_item.col

        if not self._detector.is_valid_position(
                source_row, source_col,
                colliding_item.row_span, colliding_item.col_span
        ):
            return (False, None)

        # Check source area is clear (excluding both items)
        source_cells = set()
        for r in range(source_row, source_row + colliding_item.row_span):
            for c in range(source_col, source_col + colliding_item.col_span):
                source_cells.add((r, c))

        # Temporarily remove both items to check
        self._detector.remove_item(item_id)
        self._detector.remove_item(colliding_id)

        # Check if both can be placed in swapped positions
        can_swap = True

        # Check moving item at target
        target_item = GridItem(
            id=item_id,
            row=target_row,
            col=target_col,
            row_span=moving_item.row_span,
            col_span=moving_item.col_span
        )
        if not self._detector.add_item(target_item):
            can_swap = False

        # Check colliding item at source
        if can_swap:
            source_item = GridItem(
                id=colliding_id,
                row=source_row,
                col=source_col,
                row_span=colliding_item.row_span,
                col_span=colliding_item.col_span
            )
            if not self._detector.add_item(source_item):
                can_swap = False
                # Remove the target item we just added
                self._detector.remove_item(item_id)

        if can_swap:
            # Update our items dict
            self._items[item_id] = target_item
            self._items[colliding_id] = source_item
            return (True, colliding_id)
        else:
            # Restore original positions
            self._detector.add_item(moving_item)
            self._detector.add_item(colliding_item)
            return (False, None)

    def get_all_items(self) -> List[GridItem]:
        """Get all items in the grid."""
        return list(self._items.values())

    def is_empty(self) -> bool:
        """Check if the grid has no items."""
        return len(self._items) == 0

    def get_occupied_count(self) -> int:
        """Get number of occupied cells."""
        return len(self._detector.get_occupied_cells())

    def get_stats(self) -> dict:
        """Get grid statistics."""
        total_cells = GRID_ROWS * GRID_COLS
        occupied = self.get_occupied_count()
        return {
            "total_cells": total_cells,
            "occupied_cells": occupied,
            "free_cells": total_cells - occupied,
            "item_count": len(self._items),
            "grid_size": f"{GRID_COLS}x{GRID_ROWS}"
        }
