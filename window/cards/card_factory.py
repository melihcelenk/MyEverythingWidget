"""
CardFactory - Creates card widgets for the grid.

Centralizes card creation logic, decoupling it from TabManager.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtGui import QPixmap

from widgets.app_card import AppCard
from widgets.image_card import ImageCard
from widgets.note_card import NoteCard
from window.models.note import Note, NoteType

if TYPE_CHECKING:
    from models.app_shortcut import AppShortcut


class CardFactory:
    """
    Factory for creating card widgets.
    
    Provides a centralized place for card creation with consistent styling
    and callback handling.
    """

    def __init__(self):
        """Initialize the factory."""
        # Callbacks
        self._on_app_tap: Optional[Callable[[str], None]] = None
        self._on_app_edit: Optional[Callable[[str], None]] = None
        self._on_app_delete: Optional[Callable[[str], None]] = None
        self._on_app_drop: Optional[Callable[[str, str], None]] = None

        self._on_note_copy: Optional[Callable[[str], None]] = None
        self._on_note_delete: Optional[Callable[[str], None]] = None
        self._on_note_drop: Optional[Callable[[str, str], None]] = None

        self._on_image_delete: Optional[Callable[[str], None]] = None
        self._on_image_resize: Optional[Callable[[str, int, int], None]] = None
        self._on_image_drop: Optional[Callable[[str, str], None]] = None

    # App card callbacks
    def set_app_callbacks(self,
                          on_tap: Optional[Callable[[str], None]] = None,
                          on_edit: Optional[Callable[[str], None]] = None,
                          on_delete: Optional[Callable[[str], None]] = None,
                          on_drop: Optional[Callable[[str, str], None]] = None):
        """Set callbacks for app cards."""
        self._on_app_tap = on_tap
        self._on_app_edit = on_edit
        self._on_app_delete = on_delete
        self._on_app_drop = on_drop

    # Note card callbacks
    def set_note_callbacks(self,
                           on_copy: Optional[Callable[[str], None]] = None,
                           on_delete: Optional[Callable[[str], None]] = None,
                           on_drop: Optional[Callable[[str, str], None]] = None):
        """Set callbacks for note cards."""
        self._on_note_copy = on_copy
        self._on_note_delete = on_delete
        self._on_note_drop = on_drop

    # Image card callbacks
    def set_image_callbacks(self,
                            on_delete: Optional[Callable[[str], None]] = None,
                            on_resize: Optional[Callable[[str, int, int], None]] = None,
                            on_drop: Optional[Callable[[str, str], None]] = None):
        """Set callbacks for image cards."""
        self._on_image_delete = on_delete
        self._on_image_resize = on_resize
        self._on_image_drop = on_drop

    def create_app_card(self, app: AppShortcut) -> AppCard:
        """
        Create an app card widget.
        
        Args:
            app: The AppShortcut model
            
        Returns:
            Configured AppCard widget
        """
        card = AppCard(
            app=app,
            on_tap=lambda: self._on_app_tap(app.id) if self._on_app_tap else None,
            on_edit=lambda: self._on_app_edit(app.id) if self._on_app_edit else None,
            on_delete=lambda: self._on_app_delete(app.id) if self._on_app_delete else None
        )

        # Connect drop signal
        if self._on_app_drop:
            card.item_dropped.connect(
                lambda dropped_id: self._on_app_drop(dropped_id, app.id)
            )

        return card

    def create_note_card(self, note: Note,
                         col_span: int = 2,
                         row_span: int = 1) -> NoteCard:
        """
        Create a note card widget.
        
        Args:
            note: The Note model
            col_span: Number of columns the card spans
            row_span: Number of rows the card spans
            
        Returns:
            Configured NoteCard widget
        """
        card = NoteCard(
            note=note,
            col_span=col_span,
            row_span=row_span
        )

        # Connect signals
        if self._on_note_copy:
            card.copy_clicked.connect(
                lambda: self._on_note_copy(note.id)
            )

        if self._on_note_delete:
            card.delete_clicked.connect(
                lambda: self._on_note_delete(note.id)
            )

        if self._on_note_drop:
            card.item_dropped.connect(
                lambda dropped_id: self._on_note_drop(dropped_id, note.id)
            )

        return card

    def create_image_card(self, note: Note,
                          pixmap: QPixmap,
                          col_span: Optional[int] = None,
                          row_span: Optional[int] = None) -> ImageCard:
        """
        Create an image card widget.
        
        Args:
            note: The Note model containing image data
            pixmap: The image pixmap
            col_span: Override column span (uses calculated if None)
            row_span: Override row span (uses calculated if None)
            
        Returns:
            Configured ImageCard widget
        """
        card = ImageCard(note.id, pixmap)

        # Set span if provided
        if col_span is not None and row_span is not None:
            card.set_span(col_span, row_span)

        # Connect signals
        if self._on_image_delete:
            card.delete_clicked.connect(
                lambda: self._on_image_delete(note.id)
            )

        if self._on_image_resize:
            card.resize_clicked.connect(
                lambda cols, rows: self._on_image_resize(note.id, cols, rows)
            )

        if self._on_image_drop:
            card.item_dropped.connect(
                lambda dropped_id: self._on_image_drop(dropped_id, note.id)
            )

        return card

    def create_card_for_note(self, note: Note) -> NoteCard | ImageCard:
        """
        Create the appropriate card type for a note.
        
        Args:
            note: The Note model
            
        Returns:
            NoteCard for text notes, ImageCard for media notes
        """
        if note.type == NoteType.MEDIA:
            # Load image from content (base64 or path)
            pixmap = self._load_note_image(note)
            if pixmap and not pixmap.isNull():
                return self.create_image_card(
                    note, pixmap,
                    col_span=note.col_span,
                    row_span=note.row_span
                )

        # Default to text note card
        return self.create_note_card(
            note,
            col_span=note.col_span,
            row_span=note.row_span
        )

    def _load_note_image(self, note: Note) -> Optional[QPixmap]:
        """
        Load image from note content.
        
        Args:
            note: Note containing image data
            
        Returns:
            QPixmap or None if load fails
        """
        import base64

        if not note.content:
            return None

        try:
            # Try base64 first
            if note.content.startswith("data:image") or len(note.content) > 200:
                # Extract base64 data
                if "base64," in note.content:
                    data = note.content.split("base64,")[1]
                else:
                    data = note.content

                image_bytes = base64.b64decode(data)
                pixmap = QPixmap()
                pixmap.loadFromData(image_bytes)
                return pixmap

            # Try as file path
            pixmap = QPixmap(note.content)
            if not pixmap.isNull():
                return pixmap

        except Exception:
            pass

        return None
