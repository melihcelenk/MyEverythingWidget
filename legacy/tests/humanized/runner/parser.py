"""DSL parser for humanized UI tests."""

import re
from pathlib import Path
from typing import Dict, List, Tuple

from .models import TestCase, GridItem, CreateAction, DragAction, LaunchAction


class DSLParser:
    """Parses DSL test files into TestCase objects."""

    @staticmethod
    def parse_file(file_path: Path) -> TestCase:
        """Parse a DSL test file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return DSLParser.parse(content, file_path.stem)

    @staticmethod
    def parse(content: str, name: str = "test") -> TestCase:
        """Parse DSL content into a TestCase."""
        lines = content.strip().split('\n')
        test = TestCase(name=name)
        current_section = None
        grid_lines: List[str] = []

        for line in lines:
            line = line.rstrip()  # Keep trailing spaces for grid parsing
            if not line.strip():
                continue
            # Skip comments
            if line.strip().startswith('#'):
                continue

            # Section headers
            if line.lower().startswith('rows:'):
                test.rows = int(line.split(':')[1].strip())
            elif line.lower().startswith('columns:'):
                test.cols = int(line.split(':')[1].strip())
            elif line.lower() == 'initial:':
                current_section = 'initial'
                grid_lines = []
            elif line.lower() == 'action:' or line.lower() == 'actions:':
                current_section = 'action'
                if grid_lines:
                    test.initial_items = DSLParser._parse_grid(grid_lines, test.rows, test.cols)
                    grid_lines = []
            elif line.lower() == 'expected:':
                current_section = 'expected'
                if grid_lines:
                    # This shouldn't happen, but handle it
                    grid_lines = []
            elif current_section == 'action' and line.strip():
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                # Parse actions
                # Parse Drag action - support multiple formats
                drag_match = re.search(r'Drag\((\w+)[,\s]+R(\d+)C(\d+)\)', line)
                if not drag_match:
                    drag_match = re.search(r'Drag\((\w+)\).*?R(\d+)C(\d+)', line)
                if drag_match:
                    item_id = drag_match.group(1)
                    target_row = int(drag_match.group(2)) - 1  # Convert to 0-based
                    target_col = int(drag_match.group(3)) - 1
                    test.actions.append(DragAction(item_id, target_row, target_col))
                    # Legacy field for backward compatibility
                    test.action_item = item_id
                    test.action_target_row = target_row
                    test.action_target_col = target_col
                # Parse Create action
                create_match = re.search(r'Create\((\w+),\s*"([^"]+)",\s*(\w+)\)', line)
                if create_match:
                    item_type = create_match.group(1)
                    content = create_match.group(2)
                    item_id = create_match.group(3)
                    test.actions.append(CreateAction(item_type, content, item_id))
                # Parse Launch action
                launch_match = re.search(r'Launch\((\w+)\)', line)
                if launch_match:
                    item_id = launch_match.group(1)
                    test.actions.append(LaunchAction(item_id))
            elif current_section in ('initial', 'expected') and line.strip():
                grid_lines.append(line)

        # Handle remaining grid lines
        if grid_lines:
            if current_section == 'expected':
                test.expected_items = DSLParser._parse_grid(grid_lines, test.rows, test.cols)
            elif current_section == 'initial':
                test.initial_items = DSLParser._parse_grid(grid_lines, test.rows, test.cols)

        return test

    @staticmethod
    def _parse_grid(lines: List[str], rows: int, cols: int) -> Dict[str, GridItem]:
        """Parse grid lines into items."""
        items: Dict[str, GridItem] = {}
        item_positions: Dict[str, List[Tuple[int, int]]] = {}

        for row_idx, line in enumerate(lines):
            if row_idx >= rows:
                break
            cells = line.split()
            for col_idx, cell in enumerate(cells):
                if col_idx >= cols:
                    break
                if cell in ('.', 'x', '_'):
                    continue
                if cell not in item_positions:
                    item_positions[cell] = []
                item_positions[cell].append((row_idx, col_idx))

        for item_id, positions in item_positions.items():
            if not positions:
                continue
            if item_id.startswith('A'):
                item_type = 'app'
            elif item_id.startswith('N'):
                item_type = 'note'
            elif item_id.startswith('I'):
                item_type = 'image'
            else:
                item_type = 'unknown'

            min_row = min(p[0] for p in positions)
            max_row = max(p[0] for p in positions)
            min_col = min(p[1] for p in positions)
            max_col = max(p[1] for p in positions)

            items[item_id] = GridItem(
                id=item_id,
                item_type=item_type,
                row=min_row,
                col=min_col,
                row_span=max_row - min_row + 1,
                col_span=max_col - min_col + 1
            )

        return items
