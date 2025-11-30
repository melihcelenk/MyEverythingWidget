"""
Grid management module for Android-like grid layout.

This module provides:
- GridManager: Main grid layout management
- CollisionDetector: Cell collision detection
- CellCalculator: Grid cell calculations
- DropHandler: Drag-drop operations
"""

"""
Grid management module.

- constants: Grid dimensions and sizes
- populator: Fills grid with cards
- mover: Handles drag-drop and swap
- cell_calculator: Cell position calculations
- collision_detector: Detects cell collisions
"""
from window.grid.cell_calculator import CellCalculator
from window.grid.collision_detector import CollisionDetector, GridItem
from window.grid.constants import GRID_COLS, GRID_ROWS, CELL_WIDTH, CELL_HEIGHT, SPACING
from window.grid.mover import ItemMover
from window.grid.populator import GridPopulator

__all__ = [
    'GRID_COLS', 'GRID_ROWS', 'CELL_WIDTH', 'CELL_HEIGHT', 'SPACING',
    'CellCalculator',
    'CollisionDetector', 'GridItem',
    'GridPopulator',
    'ItemMover',
]
