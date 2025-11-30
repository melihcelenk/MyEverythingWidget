"""State management for humanized UI tests."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .constants import Colors
from .models import TestCase


class StateManager:
    """Manages test state files."""

    def __init__(self, initial_state_file: Path, state_file: Path, backup_file: Path):
        self.initial_state_file = initial_state_file
        self.state_file = state_file
        self.backup_file = backup_file

    def backup_state(self):
        """Backup current state file."""
        if self.state_file.exists():
            import shutil
            shutil.copy2(self.state_file, self.backup_file)
            print(f"  {Colors.CYAN}State backed up{Colors.RESET}")

    def restore_state(self):
        """Restore state from backup."""
        if self.backup_file.exists():
            import shutil
            shutil.copy2(self.backup_file, self.state_file)
            print(f"  {Colors.CYAN}State restored{Colors.RESET}")
        elif self.initial_state_file.exists():
            import shutil
            shutil.copy2(self.initial_state_file, self.state_file)
            print(f"  {Colors.CYAN}Test state reset from {self.initial_state_file.name}{Colors.RESET}")

    def create_test_state(self, test: TestCase) -> dict:
        """Create test state from test case."""
        with open(self.initial_state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)

        test_category_id = "test-category-" + str(uuid.uuid4())[:8]

        state["categories"] = [
            {"id": test_category_id, "name": "Test", "icon": "🧪"}
        ]

        state["apps"] = []
        state["notes"] = []

        now = datetime.now(timezone.utc).isoformat()

        for item_id, item in test.initial_items.items():
            if item.item_type == 'app':
                state["apps"].append({
                    "id": f"test-app-{item_id}",
                    "name": f"App {item_id}",
                    "icon_path": "📱",
                    "target": "https://example.com",
                    "category": "Test",
                    "type": "url",
                    "order": 0,
                    "grid_row": item.row,
                    "grid_col": item.col,
                    "col_span": item.col_span,
                    "row_span": item.row_span
                })
            elif item.item_type in ('note', 'image'):
                state["notes"].append({
                    "id": f"test-note-{item_id}",
                    "content": f"Note {item_id}",
                    "type": "image" if item.item_type == 'image' else "text",
                    "category": "Test",
                    "created_at": now,
                    "updated_at": now,
                    "order": 0,
                    "grid_row": item.row,
                    "grid_col": item.col,
                    "col_span": item.col_span,
                    "row_span": item.row_span
                })

        return state

    def write_state(self, state: dict):
        """Write state to state file."""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        print(f"  {Colors.GREEN}Test state created{Colors.RESET}")

    def read_state(self) -> dict:
        """Read state from state file."""
        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
