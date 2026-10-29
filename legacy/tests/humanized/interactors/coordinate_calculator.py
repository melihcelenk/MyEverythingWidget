"""Coordinate calculation utilities for UI interactions."""

from typing import Tuple

from ..runner.constants import (
    CELL_WIDTH, CELL_HEIGHT, SPACING, MARGIN_LEFT,
    WINDOW_WIDTH, WINDOW_HEIGHT, FAB_SIZE, FAB_MARGIN,
    TAB_HEIGHT, LABEL_HEIGHT,
    MARGIN_TOP, INPUT_HEIGHT, GAP
)


class CoordinateCalculator:
    """Calculates screen coordinates for UI elements."""

    @staticmethod
    def cell_to_pixel(row: int, col: int, win_x: int, win_y: int) -> Tuple[int, int]:
        """Convert grid cell coordinates to pixel coordinates."""
        # Grid starts at MARGIN_LEFT from left edge
        # Each cell is CELL_WIDTH wide with SPACING between
        x = win_x + MARGIN_LEFT + col * (CELL_WIDTH + SPACING) + CELL_WIDTH // 2
        y = win_y + MARGIN_TOP + row * (CELL_HEIGHT + SPACING) + CELL_HEIGHT // 2
        return x, y

    @staticmethod
    def get_fab_position(win_x: int, win_y: int) -> Tuple[int, int]:
        """Get FAB (Floating Action Button) position."""
        fab_x = win_x + WINDOW_WIDTH - FAB_SIZE - FAB_MARGIN
        fab_y = win_y + WINDOW_HEIGHT - FAB_SIZE - FAB_MARGIN
        return fab_x, fab_y

    @staticmethod
    def get_tab_position(tab_index: int, dialog_x: int, dialog_y: int, dialog_width: int) -> Tuple[int, int]:
        """Get tab position in dialog."""
        tab_width = dialog_width // 3  # 3 tabs
        tab_x = dialog_x + (tab_index * tab_width) + (tab_width // 2)
        tab_y = dialog_y + TAB_HEIGHT // 2
        return tab_x, tab_y

    @staticmethod
    def get_name_input_position(dialog_x: int, dialog_y: int, dialog_width: int) -> Tuple[int, int]:
        """Get name input field position in Add Item Dialog."""
        name_input_x = dialog_x + dialog_width // 2  # Center of dialog
        name_input_y = dialog_y + TAB_HEIGHT + MARGIN_TOP + LABEL_HEIGHT + GAP + (INPUT_HEIGHT // 2)
        return name_input_x, name_input_y

    @staticmethod
    def get_path_input_position(dialog_x: int, dialog_y: int, dialog_width: int, name_input_y: int) -> Tuple[int, int]:
        """Get path input field position in Add Item Dialog."""
        path_input_x = dialog_x + dialog_width // 2  # Center of dialog (same as name input)
        path_input_y = name_input_y + (INPUT_HEIGHT // 2) + GAP + LABEL_HEIGHT + GAP + (INPUT_HEIGHT // 2)
        return path_input_x, path_input_y

    @staticmethod
    def get_add_button_position(dialog_x: int, dialog_y: int, dialog_width: int, dialog_height: int) -> Tuple[int, int]:
        """Get Add button position in Add Item Dialog."""
        BUTTON_HEIGHT = 35
        BUTTON_MARGIN_BOTTOM = 15
        add_button_x = dialog_x + dialog_width // 2
        add_button_y = dialog_y + dialog_height - BUTTON_MARGIN_BOTTOM - (BUTTON_HEIGHT // 2)
        return add_button_x, add_button_y
