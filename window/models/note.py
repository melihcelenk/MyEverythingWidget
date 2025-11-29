"""
Note model for My Everything Widget
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict


class NoteType(Enum):
    TEXT = "text"
    IMAGE = "image"
    LINK = "link"
    FILE = "file"

    @property
    def is_media(self) -> bool:
        return self in {NoteType.IMAGE, NoteType.FILE}


@dataclass(frozen=True)
class Note:
    id: str
    content: str
    type: NoteType
    category: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    order: int = field(default=0)
    grid_row: int | None = field(default=None)
    grid_col: int | None = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["type"] = self.type.value
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"])
        return cls(
            id=data["id"],
            content=data["content"],
            type=NoteType(data["type"]),
            category=data["category"],
            created_at=created_at,
            updated_at=updated_at,
            order=data.get("order", 0),
            grid_row=data.get("grid_row"),
            grid_col=data.get("grid_col"),
        )

