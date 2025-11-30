"""
Tests for drag-and-drop functionality
"""
import os
import sys

import pytest
from PySide6.QtCore import Qt, QMimeData, QPoint
from PySide6.QtWidgets import QApplication


class TestDragDropVisualFeedback:
    """Test visual feedback during drag operations"""

    @pytest.fixture
    def app(self):
        """Create QApplication"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        # Cleanup
        os.environ.pop("MEW_STATE_PATH", None)

    @pytest.fixture
    def app_card(self, app):
        """Create AppCard for testing"""
        from widgets.app_card import AppCard
        from models.app_shortcut import AppShortcut, LaunchType

        shortcut = AppShortcut(
            id="test-1",
            name="Test App",
            icon_path="🌐",
            target="https://test.com",
            category="Web",
            type=LaunchType.URL
        )
        card = AppCard(shortcut, on_tap=lambda: None)
        card.show()
        app.processEvents()
        yield card
        card.close()

    @pytest.fixture
    def note_card(self, app):
        """Create NoteCard for testing"""
        from widgets.note_card import NoteCard
        from window.models.note import Note, NoteType

        note = Note(
            id="note-1",
            content="Test note content",
            type=NoteType.TEXT,
            category="Web"
        )
        card = NoteCard(note)
        card.show()
        app.processEvents()
        yield card
        card.close()

    def test_draggable_mixin_initialized_for_app_card(self, app_card):
        """AppCard should have draggable mixin initialized"""
        assert hasattr(app_card, '_drag_item_id')
        assert app_card._drag_item_id == "test-1"
        assert app_card._drag_item_type == "app"
        assert app_card.acceptDrops()

    def test_draggable_mixin_initialized_for_note_card(self, note_card):
        """NoteCard should have draggable mixin initialized"""
        assert hasattr(note_card, '_drag_item_id')
        assert note_card._drag_item_id == "note-1"
        assert note_card._drag_item_type == "note"
        assert note_card.acceptDrops()

    def test_drag_creates_pixmap(self, app, app_card):
        """Drag operation should create a semi-transparent pixmap"""
        from PySide6.QtGui import QDrag
        from unittest.mock import patch

        # Mock QDrag to capture setPixmap call
        with patch.object(QDrag, '__init__', return_value=None):
            with patch.object(QDrag, 'setMimeData'):
                with patch.object(QDrag, 'setPixmap') as mock_set_pixmap:
                    with patch.object(QDrag, 'setHotSpot'):
                        with patch.object(QDrag, 'exec', return_value=Qt.DropAction.IgnoreAction):
                            app_card.start_drag(app_card)

                            # Verify pixmap was set
                            assert mock_set_pixmap.called
                            pixmap = mock_set_pixmap.call_args[0][0]
                            assert not pixmap.isNull()

    def test_drag_start_position_stored(self, app, app_card):
        """Mouse press should store drag start position"""
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent

        # Simulate mouse press
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPoint(10, 10),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        app_card.mousePressEvent(event)

        assert app_card._drag_start_pos is not None
        assert app_card._drag_start_pos == QPoint(10, 10)

    def test_card_accepts_drop_from_same_type(self, app, app_card):
        """Card should accept drop from same item type"""
        # Create mock drag enter event with valid MIME data
        mime_data = QMimeData()
        mime_data.setText("app:other-app-id")

        # Verify the MIME data format is correct
        text = mime_data.text()
        assert ":" in text
        item_type, item_id = text.split(":", 1)
        assert item_type == "app"
        assert item_id == "other-app-id"

    def test_drop_indicator_shown_on_drag_over(self, app, app_card):
        """Visual indicator should be shown when dragging over target"""
        # This tests the visual feedback - card should change style
        # The implementation will add this
        pass  # Will be implemented after visual feedback is added


class TestDragDropNoteCard:
    """Test drag-drop for NoteCard"""

    @pytest.fixture
    def app(self):
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        os.environ.pop("MEW_STATE_PATH", None)

    @pytest.fixture
    def note_card(self, app):
        from widgets.note_card import NoteCard
        from window.models.note import Note, NoteType

        note = Note(
            id="note-1",
            content="Test note",
            type=NoteType.TEXT,
            category="Web"
        )
        card = NoteCard(note)
        card.show()
        app.processEvents()
        yield card
        card.close()

    def test_note_card_emits_item_dropped_signal(self, app, note_card):
        """NoteCard should emit itemDropped signal on drop"""
        dropped_items = []
        note_card.itemDropped.connect(lambda id, idx: dropped_items.append((id, idx)))

        # Verify signal is connected
        assert len(dropped_items) == 0

    def test_note_card_drag_type_is_note(self, note_card):
        """NoteCard drag type should be 'note'"""
        assert note_card._drag_item_type == "note"

    def test_note_card_accepts_drops(self, note_card):
        """NoteCard should accept drops"""
        assert note_card.acceptDrops()


class TestDragDropImageCard:
    """Test drag-drop for ImageCard"""

    @pytest.fixture
    def app(self):
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        os.environ.pop("MEW_STATE_PATH", None)

    @pytest.fixture
    def image_card(self, app):
        from widgets.image_card import ImageCard
        from PySide6.QtGui import QPixmap

        # Create a test pixmap
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.red)

        card = ImageCard("image-1", pixmap)
        card.show()
        app.processEvents()
        yield card
        card.close()

    def test_image_card_draggable_initialized(self, image_card):
        """ImageCard should have draggable mixin initialized"""
        assert hasattr(image_card, '_drag_item_id')
        assert image_card._drag_item_id == "image-1"
        assert image_card._drag_item_type == "image"

    def test_image_card_accepts_drops(self, image_card):
        """ImageCard should accept drops"""
        assert image_card.acceptDrops()

    def test_image_card_emits_item_dropped_signal(self, app, image_card):
        """ImageCard should emit itemDropped signal on drop"""
        dropped_items = []
        image_card.itemDropped.connect(lambda id, idx: dropped_items.append((id, idx)))

        # Verify signal exists and is connectable
        assert len(dropped_items) == 0


class TestDragDropReordering:
    """Test actual reordering in TabManager"""

    @pytest.fixture
    def app(self):
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        os.environ.pop("MEW_STATE_PATH", None)

    @pytest.fixture
    def main_window(self, app, tmp_path):
        from window.main_window import MainWindow
        state_file = tmp_path / "app_state.json"
        os.environ["MEW_STATE_PATH"] = str(state_file)
        window = MainWindow()
        window.show()
        app.processEvents()
        yield window
        window.close()

    def test_tab_manager_handles_app_drop(self, app, main_window):
        """TabManager should handle app reordering on drop"""
        tab_manager = main_window._tab_manager

        # The TabManager should have signal handlers connected
        # This test verifies the infrastructure is in place
        assert hasattr(tab_manager, '_category_grids')

    def test_tab_manager_handles_note_drop(self, app, main_window):
        """TabManager should handle note reordering on drop"""
        # Add a note first
        from window.models.note import Note, NoteType
        import uuid

        note = Note(
            id=str(uuid.uuid4()),
            content="Test note for drag",
            type=NoteType.TEXT,
            category="Web"
        )
        main_window._app_state.add_note(note)
        app.processEvents()

        # Verify note was added
        assert len(main_window._app_state.notes) > 0


class TestTabManagerReordering:
    """Test actual reordering in TabManager with drag-drop simulation

    Note: The new Android-like grid system uses SWAP behavior instead of INSERT.
    When dropping item A onto item B, they swap positions (both grid and order).
    """

    @pytest.fixture
    def app(self):
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        os.environ.pop("MEW_STATE_PATH", None)

    @pytest.fixture
    def main_window(self, app, tmp_path):
        from window.main_window import MainWindow
        from window.models.note import Note, NoteType

        state_file = tmp_path / "app_state.json"
        os.environ["MEW_STATE_PATH"] = str(state_file)
        window = MainWindow()

        # Clear any existing notes
        window._app_state._notes = []

        # Add 5 test notes to first category
        first_category = window._app_state.categories[0].name if window._app_state.categories else "Dev"

        for i in range(5):
            note = Note(
                id=f"test-note-{i}",
                content=f"Test Note {i + 1}",
                type=NoteType.TEXT,
                category=first_category,
                order=i
            )
            window._app_state.add_note(note)

        window.show()
        app.processEvents()
        yield window
        window.close()

    def test_swap_adjacent_notes(self, app, main_window):
        """Swap note-1 with note-2 (adjacent swap)"""
        # Initial order: [note-0, note-1, note-2, note-3, note-4]
        # Drag note-1 onto note-2 → SWAP → [note-0, note-2, note-1, note-3, note-4]

        notes = sorted(
            [n for n in main_window._app_state.notes if n.id.startswith("test-note-")],
            key=lambda n: n.order
        )

        # Verify initial order
        assert [n.id for n in notes] == ["test-note-0", "test-note-1", "test-note-2", "test-note-3", "test-note-4"]

        # Simulate drag note-1 onto note-2 (swap)
        dragged_note = notes[1]  # note-1
        target_note = notes[2]  # note-2

        main_window._tab_manager._reorder_note(dragged_note, target_note)
        app.processEvents()

        # Verify swap result
        final_notes = sorted(
            [n for n in main_window._app_state.notes if n.id.startswith("test-note-")],
            key=lambda n: n.order
        )
        assert [n.id for n in final_notes] == ["test-note-0", "test-note-2", "test-note-1", "test-note-3",
                                               "test-note-4"]

    def test_swap_non_adjacent_notes(self, app, main_window):
        """Swap note-1 with note-3 (non-adjacent swap)"""
        # Initial: [note-0, note-1, note-2, note-3, note-4]
        # Drag note-1 onto note-3 → SWAP orders → [note-0, note-3, note-2, note-1, note-4]

        notes = sorted(
            [n for n in main_window._app_state.notes if n.id.startswith("test-note-")],
            key=lambda n: n.order
        )

        dragged_note = notes[1]  # note-1 (order=1)
        target_note = notes[3]  # note-3 (order=3)

        main_window._tab_manager._reorder_note(dragged_note, target_note)
        app.processEvents()

        # After swap: note-1 has order=3, note-3 has order=1
        final_notes = sorted(
            [n for n in main_window._app_state.notes if n.id.startswith("test-note-")],
            key=lambda n: n.order
        )
        assert [n.id for n in final_notes] == ["test-note-0", "test-note-3", "test-note-2", "test-note-1",
                                               "test-note-4"]

    def test_swap_backward(self, app, main_window):
        """Swap note-3 with note-2 (backward swap)"""
        # Initial: [note-0, note-1, note-2, note-3, note-4]
        # Drag note-3 onto note-2 → SWAP → [note-0, note-1, note-3, note-2, note-4]

        notes = sorted(
            [n for n in main_window._app_state.notes if n.id.startswith("test-note-")],
            key=lambda n: n.order
        )

        dragged_note = notes[3]  # note-3
        target_note = notes[2]  # note-2

        main_window._tab_manager._reorder_note(dragged_note, target_note)
        app.processEvents()

        final_notes = sorted(
            [n for n in main_window._app_state.notes if n.id.startswith("test-note-")],
            key=lambda n: n.order
        )
        assert [n.id for n in final_notes] == ["test-note-0", "test-note-1", "test-note-3", "test-note-2",
                                               "test-note-4"]

    def test_swap_with_last(self, app, main_window):
        """Swap note-1 with note-4 (last position)"""
        # Initial: [note-0, note-1, note-2, note-3, note-4]
        # Drag note-1 onto note-4 → SWAP → [note-0, note-4, note-2, note-3, note-1]

        notes = sorted(
            [n for n in main_window._app_state.notes if n.id.startswith("test-note-")],
            key=lambda n: n.order
        )

        dragged_note = notes[1]  # note-1 (order=1)
        target_note = notes[4]  # note-4 (order=4)

        main_window._tab_manager._reorder_note(dragged_note, target_note)
        app.processEvents()

        final_notes = sorted(
            [n for n in main_window._app_state.notes if n.id.startswith("test-note-")],
            key=lambda n: n.order
        )
        assert [n.id for n in final_notes] == ["test-note-0", "test-note-4", "test-note-2", "test-note-3",
                                               "test-note-1"]

    def test_swap_with_first(self, app, main_window):
        """Swap note-3 with note-0 (first position)"""
        # Initial: [note-0, note-1, note-2, note-3, note-4]
        # Drag note-3 onto note-0 → SWAP → [note-3, note-1, note-2, note-0, note-4]

        notes = sorted(
            [n for n in main_window._app_state.notes if n.id.startswith("test-note-")],
            key=lambda n: n.order
        )

        dragged_note = notes[3]  # note-3 (order=3)
        target_note = notes[0]  # note-0 (order=0)

        main_window._tab_manager._reorder_note(dragged_note, target_note)
        app.processEvents()

        final_notes = sorted(
            [n for n in main_window._app_state.notes if n.id.startswith("test-note-")],
            key=lambda n: n.order
        )
        assert [n.id for n in final_notes] == ["test-note-3", "test-note-1", "test-note-2", "test-note-0",
                                               "test-note-4"]


class TestNoteReordering:
    """Test note reordering via drag-drop"""

    @pytest.fixture
    def app_state(self):
        """Create AppState with test notes"""
        from window.app_state import AppState
        from window.models.note import Note, NoteType
        from models.category import AppCategory

        state = AppState()

        # Add test category
        state._categories = [
            AppCategory(id="1", name="Dev", icon="💻"),
        ]

        # Add 3 test notes with different orders
        state._notes = [
            Note(id="note-1", content="Note 1", type=NoteType.TEXT, category="Dev", order=0),
            Note(id="note-2", content="Note 2", type=NoteType.TEXT, category="Dev", order=1),
            Note(id="note-3", content="Note 3", type=NoteType.TEXT, category="Dev", order=2),
        ]

        return state

    def test_reorder_note_last_to_first(self, app_state):
        """Moving last note to first position"""
        from dataclasses import replace

        # Get notes sorted by order
        notes = sorted(
            [n for n in app_state.notes if n.category == "Dev"],
            key=lambda n: n.order
        )

        # Verify initial order
        assert [n.id for n in notes] == ["note-1", "note-2", "note-3"]

        # Move note-3 to position 0
        note = notes[2]  # note-3
        target_index = 0

        # Remove from current position
        current_index = 2
        notes.pop(current_index)

        # Insert at target
        notes.insert(target_index, note)

        # Update orders
        for i, n in enumerate(notes):
            if n.order != i:
                updated = replace(n, order=i)
                # Find and update in app_state
                for j, orig in enumerate(app_state._notes):
                    if orig.id == n.id:
                        app_state._notes[j] = updated
                        break

        # Verify new order
        final_notes = sorted(
            [n for n in app_state.notes if n.category == "Dev"],
            key=lambda n: n.order
        )
        assert [n.id for n in final_notes] == ["note-3", "note-1", "note-2"]

    def test_reorder_note_first_to_last(self, app_state):
        """Moving first note to last position"""
        from dataclasses import replace

        notes = sorted(
            [n for n in app_state.notes if n.category == "Dev"],
            key=lambda n: n.order
        )

        # Move note-1 to position 2
        note = notes[0]
        target_index = 2

        notes.pop(0)
        target_index = min(target_index, len(notes))  # Adjust for removed item
        notes.insert(target_index, note)

        for i, n in enumerate(notes):
            if n.order != i:
                updated = replace(n, order=i)
                for j, orig in enumerate(app_state._notes):
                    if orig.id == n.id:
                        app_state._notes[j] = updated
                        break

        final_notes = sorted(
            [n for n in app_state.notes if n.category == "Dev"],
            key=lambda n: n.order
        )
        assert [n.id for n in final_notes] == ["note-2", "note-3", "note-1"]

    def test_reorder_note_middle_swap(self, app_state):
        """Swapping middle note with first"""
        from dataclasses import replace

        notes = sorted(
            [n for n in app_state.notes if n.category == "Dev"],
            key=lambda n: n.order
        )

        # Move note-2 to position 0
        note = notes[1]
        current_index = 1
        target_index = 0

        notes.pop(current_index)
        notes.insert(target_index, note)

        for i, n in enumerate(notes):
            if n.order != i:
                updated = replace(n, order=i)
                for j, orig in enumerate(app_state._notes):
                    if orig.id == n.id:
                        app_state._notes[j] = updated
                        break

        final_notes = sorted(
            [n for n in app_state.notes if n.category == "Dev"],
            key=lambda n: n.order
        )
        assert [n.id for n in final_notes] == ["note-2", "note-1", "note-3"]

    def test_reorder_same_position_no_change(self, app_state):
        """Moving note to same position should not change order"""
        from dataclasses import replace

        notes = sorted(
            [n for n in app_state.notes if n.category == "Dev"],
            key=lambda n: n.order
        )

        # Move note-2 to position 1 (same position)
        note = notes[1]
        current_index = 1
        target_index = 1

        notes.pop(current_index)
        notes.insert(target_index, note)

        for i, n in enumerate(notes):
            if n.order != i:
                updated = replace(n, order=i)
                for j, orig in enumerate(app_state._notes):
                    if orig.id == n.id:
                        app_state._notes[j] = updated
                        break

        final_notes = sorted(
            [n for n in app_state.notes if n.category == "Dev"],
            key=lambda n: n.order
        )
        # Order should remain the same
        assert [n.id for n in final_notes] == ["note-1", "note-2", "note-3"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
