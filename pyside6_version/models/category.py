"""
Category model for organizing apps and notes
"""
from dataclasses import dataclass


@dataclass
class AppCategory:
    """Application category data model"""
    id: str
    name: str
    icon: str

    def __eq__(self, other):
        if not isinstance(other, AppCategory):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

