"""
Local storage helper for saving/restoring categories and apps
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_DIR = Path(
    os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")
) / "MyEverythingWidget"
DEFAULT_FILENAME = "app_state.json"


class StorageService:
    """Handles loading and saving the serialized app state."""

    def __init__(self, path: Optional[Path | str] = None):
        env_path = os.getenv("MEW_STATE_PATH")
        if path:
            self._path = Path(path)
        elif env_path:
            self._path = Path(env_path)
        else:
            self._path = DEFAULT_DIR / DEFAULT_FILENAME

        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> Dict[str, List[Any]]:
        """Load the persisted state, returning empty dict if missing."""
        if not self._path.exists():
            return {}

        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def save(self, categories: List[Dict[str, Any]], apps: List[Dict[str, Any]]):
        """Persist the category and app lists."""
        payload = {
            "categories": categories,
            "apps": apps,
        }
        self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

