"""
NoteActions - Handles note editing, resizing, and relocating.

Single Responsibility: Process note modification actions.
"""
import logging
from dataclasses import replace
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from window.app_state import AppState


class NoteActions:
    """Handles note modification actions."""

    _logger = logging.getLogger(__name__)

    def __init__(self, app_state: 'AppState'):
        self._app_state = app_state
        self.on_refresh: Callable = None

    def edit_note(self, note_id: str):
        """Handle edit note request."""
        self._logger.debug("Edit note requested: %s", note_id)
        # TODO: Implement note editing dialog

    def relocate_note(self, note_id: str, new_category: str):
        """Move note to a different category."""
        note = next((n for n in self._app_state.notes if n.id == note_id), None)
        if note:
            updated_note = replace(note, category=new_category)
            self._app_state.update_note(updated_note)
            if self.on_refresh:
                self.on_refresh()

    def resize_card(self, card, col_span: int, row_span: int):
        """Handle card resize and persist to state."""
        card.set_span(col_span, row_span)
        card.disable_resize_mode()

        note_id = None
        if hasattr(card, 'note'):
            note_id = card.note.id
        elif hasattr(card, '_image_id'):
            note_id = card._image_id

        if note_id:
            note = next((n for n in self._app_state.notes if n.id == note_id), None)
            if note:
                updated_note = replace(note, col_span=col_span, row_span=row_span)
                self._app_state.update_note(updated_note)
                self._logger.info("Saved note span: %s -> %dx%d", note_id, col_span, row_span)

        if self.on_refresh:
            self.on_refresh()
