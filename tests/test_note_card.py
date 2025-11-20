"""
Tests for the NoteCard widget
"""
import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard, QContextMenuEvent
from PySide6.QtWidgets import QApplication, QPushButton, QMenu

from widgets.note_card import NoteCard
from window.models.note import Note, NoteType


@pytest.mark.usefixtures("qtbot")
def test_note_card_copy_emits_signal(qtbot):
    note = Note(
        id="note-1",
        content="Copy this text",
        type=NoteType.TEXT,
        category="Notes",
    )
    card = NoteCard(note)
    qtbot.addWidget(card)

    emitted = []
    card.copyRequested.connect(lambda note_id: emitted.append(note_id))

    copy_button = card.findChildren(QPushButton)[0]
    qtbot.mouseClick(copy_button, Qt.MouseButton.LeftButton)

    assert emitted == ["note-1"]
    clipboard = QApplication.clipboard()
    assert clipboard.text() == note.content


@pytest.mark.usefixtures("qtbot")
def test_note_card_context_menu_delete(qtbot, monkeypatch):
    note = Note(
        id="note-2",
        content="Delete me",
        type=NoteType.TEXT,
        category="Notes",
    )
    card = NoteCard(note)
    qtbot.addWidget(card)

    emitted = []
    card.deleteRequested.connect(lambda note_id: emitted.append(note_id))

    def fake_exec(self, pos):
        return self.actions()[1]

    monkeypatch.setattr(QMenu, "exec", fake_exec)

    global_pos = card.mapToGlobal(card.rect().center())
    event = QContextMenuEvent(QContextMenuEvent.Mouse, card.rect().center(), global_pos)
    card.contextMenuEvent(event)

    assert emitted == ["note-2"]
