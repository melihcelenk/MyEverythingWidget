"""
ItemMover - Handles moving and swapping items in the grid.

Single Responsibility: Move/swap items between grid cells.
"""
from __future__ import annotations

import logging
from dataclasses import replace
from typing import TYPE_CHECKING, Callable

from window.grid.constants import GRID_COLS, GRID_ROWS

if TYPE_CHECKING:
    from window.app_state import AppState


class ItemMover:
    """Handles grid-based item movement and swapping."""

    _logger = logging.getLogger(__name__)

    def __init__(self, app_state: AppState, get_occupied_cells: Callable, get_cells_for_item: Callable):
        self._app_state = app_state
        self._get_occupied_cells = get_occupied_cells
        self._get_cells_for_item = get_cells_for_item
        self.on_refresh: Callable = None

    def handle_grid_drop(self, item_id: str, target_row: int, target_col: int):
        """Handle grid-based drop (Android-like behavior).

        Rules:
        1. Fixed 3x5 grid - no overflow allowed
        2. If target is empty, move item there
        3. If target is occupied by ONE item that fits in source, swap
        4. If swap not possible, reject the drop
        """
        self._logger.info("Grid drop: item=%s to row=%d col=%d", item_id, target_row, target_col)

        # Find the dragged item
        dragged_app = next((a for a in self._app_state.apps if a.id == item_id), None)
        dragged_note = None if dragged_app else next(
            (n for n in self._app_state.notes if n.id == item_id), None
        )

        if dragged_app is None and dragged_note is None:
            self._logger.warning("Dropped item not found: %s", item_id)
            return

        dragged_item = dragged_app or dragged_note
        category_name = dragged_item.category

        row_span = getattr(dragged_item, 'row_span', 1)
        col_span = getattr(dragged_item, 'col_span', 1)

        # Check grid bounds
        if target_col + col_span > GRID_COLS or target_row + row_span > GRID_ROWS:
            self._logger.warning("Drop would overflow grid")
            return

        # Calculate cells
        target_cells = {(r, c) for r in range(target_row, target_row + row_span)
                        for c in range(target_col, target_col + col_span)}
        source_cells = self._get_cells_for_item(dragged_item)
        source_row = dragged_item.grid_row
        source_col = dragged_item.grid_col

        occupied = self._get_occupied_cells(category_name) - source_cells
        collision_cells = target_cells & occupied

        if not collision_cells:
            self._move_item(dragged_item, target_row, target_col)
            if self.on_refresh:
                self.on_refresh()
            return

        # Find colliding item
        colliding_item = self._find_item_at_cells(category_name, collision_cells, item_id)
        if colliding_item is None:
            return

        # Check if swap is possible
        colliding_span_row = getattr(colliding_item, 'row_span', 1)
        colliding_span_col = getattr(colliding_item, 'col_span', 1)

        if source_row is None or source_col is None:
            self._logger.warning("Cannot swap - source position unknown")
            return

        # Check grid bounds for colliding item at source
        if (source_col + colliding_span_col > GRID_COLS or
                source_row + colliding_span_row > GRID_ROWS):
            self._logger.warning("Cannot swap - colliding item doesn't fit at source (grid bounds)")
            return

        # Check if source area is free (excluding dragged item's cells)
        colliding_source_cells = {
            (r, c) for r in range(source_row, source_row + colliding_span_row)
            for c in range(source_col, source_col + colliding_span_col)
        }
        colliding_item_cells = self._get_cells_for_item(colliding_item)
        other_occupied = occupied - colliding_item_cells  # Remove colliding item from occupied

        if colliding_source_cells & other_occupied:
            self._logger.warning("Cannot swap - source area blocked by other items")
            return

        # Perform swap
        self._logger.info("SWAP: %s -> (%d,%d), %s -> (%d,%d)",
                          dragged_item.id if hasattr(dragged_item, 'id') else 'note',
                          target_row, target_col,
                          colliding_item.id if hasattr(colliding_item, 'id') else 'item',
                          source_row, source_col)
        self._move_item(dragged_item, target_row, target_col)
        self._move_item(colliding_item, source_row, source_col)
        if self.on_refresh:
            self.on_refresh()

    def handle_item_dropped(self, item_id: str, target_item_id: str):
        """Handle item drop for reordering (swap)."""
        self._logger.info("Item dropped: id=%s onto target=%s", item_id, target_item_id)

        app = next((a for a in self._app_state.apps if a.id == item_id), None)
        if app:
            target_app = next((a for a in self._app_state.apps if a.id == target_item_id), None)
            if target_app:
                self._swap_apps(app, target_app)
            return

        note = next((n for n in self._app_state.notes if n.id == item_id), None)
        if note:
            target_note = next((n for n in self._app_state.notes if n.id == target_item_id), None)
            if target_note:
                self._swap_notes(note, target_note)

    def _move_item(self, item, row: int, col: int):
        """Move an item to a new grid position."""
        item_id = getattr(item, 'id', 'unknown')
        old_row = getattr(item, 'grid_row', '?')
        old_col = getattr(item, 'grid_col', '?')
        self._logger.info("MOVE: %s from (%s,%s) to (%d,%d)", item_id, old_row, old_col, row, col)
        
        if hasattr(item, 'name'):  # AppShortcut
            item.grid_row = row
            item.grid_col = col
            self._app_state.update_app(item)  # Save to persist
        else:  # Note
            updated = replace(item, grid_row=row, grid_col=col)
            self._logger.info("MOVE NOTE: new grid_col=%d", updated.grid_col)
            self._app_state.update_note(updated)

    def _find_item_at_cells(self, category: str, cells: set, exclude_id: str = None):
        """Find the item occupying any of the given cells."""
        for app in self._app_state.apps:
            if app.category != category or app.id == exclude_id:
                continue
            if self._get_cells_for_item(app) & cells:
                return app

        for note in self._app_state.notes:
            if note.category != category or note.id == exclude_id:
                continue
            if self._get_cells_for_item(note) & cells:
                return note

        return None

    def _swap_apps(self, app, target_app):
        """Swap app positions."""
        if app.id == target_app.id:
            return

        target_row, target_col, target_order = target_app.grid_row, target_app.grid_col, target_app.order
        source_row, source_col, source_order = app.grid_row, app.grid_col, app.order

        app.grid_row, app.grid_col, app.order = target_row, target_col, target_order
        target_app.grid_row, target_app.grid_col, target_app.order = source_row, source_col, source_order

        self._app_state.update_app(app)
        self._app_state.update_app(target_app)
        if self.on_refresh:
            self.on_refresh()

    def _swap_notes(self, note, target_note):
        """Swap note positions."""
        if note.id == target_note.id:
            return

        updated_note = replace(
            note,
            grid_row=target_note.grid_row,
            grid_col=target_note.grid_col,
            order=target_note.order
        )
        updated_target = replace(
            target_note,
            grid_row=note.grid_row,
            grid_col=note.grid_col,
            order=note.order
        )

        self._app_state.blockSignals(True)
        try:
            self._app_state.update_note(updated_note)
            self._app_state.update_note(updated_target)
        finally:
            self._app_state.blockSignals(False)

        self._app_state.state_changed.emit()
        if self.on_refresh:
            self.on_refresh()
