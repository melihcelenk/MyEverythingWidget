"""
Grid management module for Android-like grid layout.

This module provides:
- constants: Grid dimensions and sizes (GRID_COLS, GRID_ROWS, CELL_WIDTH, etc.)
- cell_calculator: Grid cell calculations
- collision_detector: Cell collision detection

Note: populator and mover are imported directly where needed to avoid circular imports.
"""
from window.grid.constants import (
    GRID_COLS, GRID_ROWS, CELL_WIDTH, CELL_HEIGHT, SPACING,
    MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM,
    TOTAL_WIDTH, TOTAL_HEIGHT
)

__all__ = [
    'GRID_COLS', 'GRID_ROWS', 'CELL_WIDTH', 'CELL_HEIGHT', 'SPACING',
    'MARGIN_LEFT', 'MARGIN_TOP', 'MARGIN_RIGHT', 'MARGIN_BOTTOM',
    'TOTAL_WIDTH', 'TOTAL_HEIGHT',
]
