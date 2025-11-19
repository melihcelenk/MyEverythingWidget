"""
Application shortcut model
Represents a launchable application or URL
"""
from enum import Enum
from dataclasses import dataclass


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

    def __eq__(self, other):
        if not isinstance(other, AppShortcut):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

