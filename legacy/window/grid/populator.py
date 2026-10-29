"""
GridPopulator - Handles populating grid layouts with cards.

Single Responsibility: Place cards in grid cells.
"""
from __future__ import annotations

import logging
from dataclasses import replace
from typing import TYPE_CHECKING, Callable

from PySide6.QtWidgets import QGridLayout

from models.note import NoteType
from services.image_cache_service import ImageCacheService
from widgets.app_card import AppCard
from widgets.image_card import ImageCard
from widgets.note_card import NoteCard
from window.grid.cell_calculator import CellCalculator

if TYPE_CHECKING:
    from window.app_state import AppState


class GridPopulator:
    """Populates grid layouts with app and note cards."""

    _logger = logging.getLogger(__name__)

    def __init__(self, app_state: AppState):
        self._app_state = app_state
        self._image_cache = ImageCacheService()

        # Callbacks - set by TabManager
        self.on_app_tap: Callable = None
        self.on_app_edit: Callable = None
        self.on_app_rename: Callable = None
        self.on_app_change_icon: Callable = None
        self.on_app_delete: Callable = None
        self.on_edit_note: Callable = None
        self.on_relocate_note: Callable = None
        self.on_resize_card: Callable = None

    def get_occupied_cells(self, category_name: str) -> set[tuple[int, int]]:
        """Get set of occupied grid cells for a category."""
        occupied = set()

        for app in self._app_state.apps:
            if app.category != category_name:
                continue
            if app.grid_row is not None and app.grid_col is not None:
                for r in range(app.grid_row, app.grid_row + app.row_span):
                    for c in range(app.grid_col, app.grid_col + app.col_span):
                        occupied.add((r, c))

        for note in self._app_state.notes:
            if note.category != category_name:
                continue
            if note.grid_row is not None and note.grid_col is not None:
                col_span = getattr(note, 'col_span', 1) or 1
                row_span = getattr(note, 'row_span', 1) or 1
                for r in range(note.grid_row, note.grid_row + row_span):
                    for c in range(note.grid_col, note.grid_col + col_span):
                        occupied.add((r, c))

        return occupied

    def get_cells_for_item(self, item) -> set[tuple[int, int]]:
        """Get all grid cells occupied by an item."""
        cells = set()

        if not hasattr(item, 'grid_row') or item.grid_row is None:
            return cells
        if not hasattr(item, 'grid_col') or item.grid_col is None:
            return cells

        row = item.grid_row
        col = item.grid_col
        row_span = getattr(item, 'row_span', 1)
        col_span = getattr(item, 'col_span', 1)

        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                cells.add((r, c))

        return cells

    def populate_grid(self, category, layout: QGridLayout):
        """Populate category grid with app and note cards."""
        # Clear existing widgets
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                widget = child.widget()
                widget.setParent(None)
                widget.deleteLater()

        apps = [app for app in self._app_state.apps if app.category == category.name]
        occupied = set()

        # Place apps with explicit positions first
        apps_with_grid = [a for a in apps if a.grid_row is not None and a.grid_col is not None]
        apps_without_grid = [a for a in apps if a.grid_row is None or a.grid_col is None]

        for app in apps_with_grid:
            card = self._create_app_card(app)
            layout.addWidget(card, app.grid_row, app.grid_col, app.row_span, app.col_span)

            for r in range(app.grid_row, app.grid_row + app.row_span):
                for c in range(app.grid_col, app.grid_col + app.col_span):
                    occupied.add((r, c))

        # Auto-place apps without positions
        for app in sorted(apps_without_grid, key=lambda a: a.order):
            cell = CellCalculator.find_first_available_cell(occupied, app.row_span, app.col_span)
            if cell is None:
                self._logger.warning("Grid full, cannot place app: %s", app.name)
                continue

            row, col = cell
            app.grid_row = row
            app.grid_col = col

            card = self._create_app_card(app)
            layout.addWidget(card, row, col, app.row_span, app.col_span)

            for r in range(row, row + app.row_span):
                for c in range(col, col + app.col_span):
                    occupied.add((r, c))

        if apps_without_grid:
            self._app_state.state_changed.emit()

        self._add_note_cards(category, layout, occupied)

    def _create_app_card(self, app) -> AppCard:
        """Create an app card with callbacks."""
        card = AppCard(
            app=app,
            on_tap=lambda a=app: self.on_app_tap(a) if self.on_app_tap else None,
            on_edit=lambda a=app: self.on_app_edit(a) if self.on_app_edit else None,
            on_rename=lambda a=app: self.on_app_rename(a) if self.on_app_rename else None,
            on_change_icon=lambda a=app: self.on_app_change_icon(a) if self.on_app_change_icon else None,
            on_delete=lambda a=app: self.on_app_delete(a) if self.on_app_delete else None,
        )
        card.setAcceptDrops(False)
        return card

    def _add_note_cards(self, category, layout: QGridLayout, occupied: set):
        """Add note cards to layout."""
        notes = [n for n in self._app_state.notes if n.category == category.name]
        if not notes:
            return

        notes_with_grid = [n for n in notes if n.grid_row is not None and n.grid_col is not None]
        notes_without_grid = [n for n in notes if n.grid_row is None or n.grid_col is None]
        notes_to_update = []  # For collision fixes (don't update state)
        newly_placed_notes = []  # For new notes (update state)

        # Place notes with explicit positions
        for note in notes_with_grid:
            col_span = note.col_span
            row_span = note.row_span

            # Check collision
            note_cells = {(r, c) for r in range(note.grid_row, note.grid_row + row_span)
                          for c in range(note.grid_col, note.grid_col + col_span)}

            if note_cells & occupied:
                new_cell = CellCalculator.find_first_available_cell(occupied, row_span, col_span)
                if new_cell:
                    note = replace(note, grid_row=new_cell[0], grid_col=new_cell[1])
                    notes_to_update.append(note)
                else:
                    continue

            card = self._create_note_card(note, category)
            if card:
                layout.addWidget(card, note.grid_row, note.grid_col, row_span, col_span)
                for r in range(note.grid_row, note.grid_row + row_span):
                    for c in range(note.grid_col, note.grid_col + col_span):
                        occupied.add((r, c))

        # Auto-place notes without positions
        for note in sorted(notes_without_grid, key=lambda n: n.order):
            col_span = note.col_span
            row_span = note.row_span

            if note.type == NoteType.TEXT and col_span == 1:
                col_span = 2

            if note.type == NoteType.IMAGE:
                pixmap = self._image_cache.get(note.content)
                if pixmap:
                    # Only auto-calculate span for NEW images (default 1x1)
                    # If user has set a custom span, respect it
                    if col_span == 1 and row_span == 1:
                        temp_card = ImageCard(note.id, pixmap, on_delete=lambda: None)
                        col_span = temp_card.col_span
                        row_span = temp_card.row_span

            cell = CellCalculator.find_first_available_cell(occupied, row_span, col_span)
            if cell is None:
                continue

            row, col = cell
            updated_note = replace(note, grid_row=row, grid_col=col, col_span=col_span, row_span=row_span)
            newly_placed_notes.append(updated_note)  # New notes need state update

            card = self._create_note_card(updated_note, category)
            if card:
                layout.addWidget(card, row, col, row_span, col_span)
                for r in range(row, row + row_span):
                    for c in range(col, col + col_span):
                        occupied.add((r, c))

        # Update state for newly auto-placed notes (first time placement)
        # This is safe because these notes had no grid position before
        for updated_note in newly_placed_notes:
            self._app_state.update_note(updated_note)

    def _create_note_card(self, note, category):
        """Create appropriate card for a note."""
        col_span = note.col_span
        row_span = note.row_span

        if note.type == NoteType.IMAGE:
            pixmap = self._image_cache.get(note.content)
            if pixmap is None:
                return None

            card = ImageCard(
                image_id=note.id,
                pixmap=pixmap,
                on_delete=self._app_state.remove_note
            )
            card.set_categories(self._app_state.categories, category.name)
            card.set_span(col_span, row_span)
            if self.on_resize_card:
                card.resizeRequested.connect(lambda cs, rs, c=card: self.on_resize_card(c, cs, rs))
            if self.on_relocate_note:
                card.relocateRequested.connect(self.on_relocate_note)
            card.setAcceptDrops(False)
            return card

        # Text note
        card = NoteCard(note, col_span=col_span, row_span=row_span)
        card.set_categories(self._app_state.categories)
        card.copyRequested.connect(lambda note_id: None)
        card.deleteRequested.connect(self._app_state.remove_note)
        if self.on_edit_note:
            card.editRequested.connect(self.on_edit_note)
        if self.on_resize_card:
            card.resizeRequested.connect(lambda cs, rs, c=card: self.on_resize_card(c, cs, rs))
        if self.on_relocate_note:
            card.relocateRequested.connect(self.on_relocate_note)
        card.setAcceptDrops(False)
        return card
