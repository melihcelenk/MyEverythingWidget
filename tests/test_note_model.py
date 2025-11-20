"""
Tests for Note model serialization and default behavior
"""
import uuid
from datetime import datetime

import pytest

from window.models.note import Note, NoteType


@pytest.fixture
def sample_note():
    return Note(
        id="note-1",
        content="Test note",
        type=NoteType.TEXT,
        category="Notes",
        created_at=datetime(2025, 1, 1, 12, 0, 0),
        updated_at=datetime(2025, 1, 1, 12, 0, 0),
    )


def test_note_serialization_round_trip(sample_note):
    payload = sample_note.to_dict()
    deserialized = Note.from_dict(payload)

    assert deserialized == sample_note
    assert deserialized.type == NoteType.TEXT
    assert deserialized.created_at == sample_note.created_at


def test_note_default_timestamps():
    note = Note(
        id=str(uuid.uuid4()),
        content="Auto timestamp",
        type=NoteType.LINK,
        category="Notes",
    )

    assert note.created_at <= datetime.utcnow()
    assert note.updated_at <= datetime.utcnow()
    assert note.type == NoteType.LINK


def test_note_type_is_media():
    assert NoteType.IMAGE.is_media
    assert NoteType.FILE.is_media
    assert not NoteType.TEXT.is_media
