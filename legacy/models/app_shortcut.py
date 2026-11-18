"""
Application shortcut model
Represents a launchable application or URL
"""
from dataclasses import dataclass, field
from enum import Enum


class LaunchType(Enum):
    """Type of application launch"""
    EXE = "exe"  # Windows executable
    URL = "url"  # Web URL
    FOLDER = "folder"  # Folder path


@dataclass
class AppShortcut:
    """Application shortcut data model"""
    id: str
    name: str
    icon_path: str
    target: str
    category: str
    type: LaunchType
    order: int = field(default=0)
    grid_row: int | None = field(default=None)
    grid_col: int | None = field(default=None)
    col_span: int = field(default=1)
    row_span: int = field(default=1)

    def __eq__(self, other):
        if not isinstance(other, AppShortcut):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

