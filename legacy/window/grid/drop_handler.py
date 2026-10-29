"""
DropHandler - Handles drag-and-drop operations for the grid.

Provides Android-like drop behavior:
- Drop to empty cell: move item
- Drop to occupied cell: swap if possible
- Reject if swap not possible
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, Callable, Tuple

from window.grid.cell_calculator import CellCalculator
from window.grid.grid_manager import GridManager

if TYPE_CHECKING:
    pass


class DropAction(Enum):
    """Types of drop actions."""
    MOVE = "move"
    SWAP = "swap"
    REJECT = "reject"


@dataclass
class DropResult:
    """Result of a drop operation."""
    action: DropAction
    success: bool
    source_id: str
    source_row: int
    source_col: int
    target_row: int
    target_col: int
    swapped_id: Optional[str] = None
    swapped_to_row: Optional[int] = None
    swapped_to_col: Optional[int] = None
    message: str = ""


class DropHandler:
    """
    Handles drag-and-drop operations on the grid.
    
    Coordinates with GridManager for collision detection and item movement.
    """

    def __init__(self, grid_manager: GridManager):
        """
        Initialize the drop handler.
        
        Args:
            grid_manager: The GridManager instance to use
        """
        self._grid = grid_manager
        self._calculator = CellCalculator

        # Callbacks for when items are moved/swapped
        self._on_move: Optional[Callable[[str, int, int], None]] = None
        self._on_swap: Optional[Callable[[str, int, int, str, int, int], None]] = None

    def set_move_callback(self, callback: Callable[[str, int, int], None]):
        """
        Set callback for when an item is moved.
        
        Args:
            callback: Function(item_id, new_row, new_col)
        """
        self._on_move = callback

    def set_swap_callback(self, callback: Callable[[str, int, int, str, int, int], None]):
        """
        Set callback for when items are swapped.
        
        Args:
            callback: Function(item1_id, item1_new_row, item1_new_col, 
                              item2_id, item2_new_row, item2_new_col)
        """
        self._on_swap = callback

    def handle_drop(self, item_id: str, target_row: int, target_col: int) -> DropResult:
        """
        Handle a drop operation.
        
        Implements Android-like behavior:
        1. If target is empty, move item there
        2. If target has one item, try to swap
        3. If swap not possible, reject
        
        Args:
            item_id: ID of the item being dropped
            target_row: Target grid row
            target_col: Target grid column
            
        Returns:
            DropResult with operation details
        """
        item = self._grid.get_item(item_id)
        if not item:
            return DropResult(
                action=DropAction.REJECT,
                success=False,
                source_id=item_id,
                source_row=0,
                source_col=0,
                target_row=target_row,
                target_col=target_col,
                message=f"Item {item_id} not found"
            )

        source_row = item.row
        source_col = item.col

        # Clamp target position based on item span
        clamped_row, clamped_col = self._calculator.clamp_position(
            target_row, target_col, item.row_span, item.col_span
        )

        # Check if target is same as source
        if clamped_row == source_row and clamped_col == source_col:
            return DropResult(
                action=DropAction.REJECT,
                success=False,
                source_id=item_id,
                source_row=source_row,
                source_col=source_col,
                target_row=clamped_row,
                target_col=clamped_col,
                message="Same position"
            )

        # Try to perform the drop (move or swap)
        success, swapped_id = self._grid.try_swap(item_id, clamped_row, clamped_col)

        if not success:
            return DropResult(
                action=DropAction.REJECT,
                success=False,
                source_id=item_id,
                source_row=source_row,
                source_col=source_col,
                target_row=clamped_row,
                target_col=clamped_col,
                message="Cannot drop here"
            )

        if swapped_id:
            # Swap occurred
            swapped_item = self._grid.get_item(swapped_id)
            result = DropResult(
                action=DropAction.SWAP,
                success=True,
                source_id=item_id,
                source_row=source_row,
                source_col=source_col,
                target_row=clamped_row,
                target_col=clamped_col,
                swapped_id=swapped_id,
                swapped_to_row=swapped_item.row if swapped_item else source_row,
                swapped_to_col=swapped_item.col if swapped_item else source_col,
                message="Items swapped"
            )

            # Call swap callback
            if self._on_swap:
                self._on_swap(
                    item_id, clamped_row, clamped_col,
                    swapped_id, result.swapped_to_row, result.swapped_to_col
                )
        else:
            # Simple move
            result = DropResult(
                action=DropAction.MOVE,
                success=True,
                source_id=item_id,
                source_row=source_row,
                source_col=source_col,
                target_row=clamped_row,
                target_col=clamped_col,
                message="Item moved"
            )

            # Call move callback
            if self._on_move:
                self._on_move(item_id, clamped_row, clamped_col)

        return result

    def can_drop(self, item_id: str, target_row: int, target_col: int) -> bool:
        """
        Check if dropping at target is possible (preview).
        
        Args:
            item_id: ID of item being dragged
            target_row: Target row
            target_col: Target column
            
        Returns:
            True if drop would succeed
        """
        item = self._grid.get_item(item_id)
        if not item:
            return False

        # Clamp position
        clamped_row, clamped_col = self._calculator.clamp_position(
            target_row, target_col, item.row_span, item.col_span
        )

        # Same position
        if clamped_row == item.row and clamped_col == item.col:
            return False

        # Check if can move or swap
        if self._grid.can_move_to(item_id, clamped_row, clamped_col):
            return True

        # Check for swap possibility
        items_at_target = self._grid.get_items_in_area(
            clamped_row, clamped_col, item.row_span, item.col_span
        )

        # Remove self from consideration
        items_at_target = [i for i in items_at_target if i != item_id]

        # If exactly one item, check if it can fit in our source
        if len(items_at_target) == 1:
            other_id = items_at_target[0]
            other_item = self._grid.get_item(other_id)
            if other_item:
                # Check if other item fits in our source position
                return self._grid._detector.is_valid_position(
                    item.row, item.col,
                    other_item.row_span, other_item.col_span
                )

        return False

    def get_drop_preview(self, item_id: str,
                         target_row: int, target_col: int) -> Tuple[int, int, int, int]:
        """
        Get the visual preview area for a drop.
        
        Args:
            item_id: ID of item being dragged
            target_row: Target row
            target_col: Target column
            
        Returns:
            (row, col, row_span, col_span) for the highlight area
        """
        item = self._grid.get_item(item_id)
        if not item:
            return (target_row, target_col, 1, 1)

        # Clamp position
        clamped_row, clamped_col = self._calculator.clamp_position(
            target_row, target_col, item.row_span, item.col_span
        )

        return (clamped_row, clamped_col, item.row_span, item.col_span)
