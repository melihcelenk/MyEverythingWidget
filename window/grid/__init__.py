"""
Grid management module for Android-like grid layout.

This module provides:
- GridManager: Main grid layout management
- CollisionDetector: Cell collision detection
- CellCalculator: Grid cell calculations
- DropHandler: Drag-drop operations
"""

from window.grid.cell_calculator import CellCalculator
from window.grid.collision_detector import CollisionDetector, GridItem
from window.grid.constants import GRID_COLS, GRID_ROWS, CELL_WIDTH, CELL_HEIGHT, SPACING
from window.grid.drop_handler import DropHandler, DropResult, DropAction
from window.grid.grid_manager import GridManager, PlacementResult
from window.grid.grid_populator import GridPopulator
from window.grid.item_mover import ItemMover

__all__ = [
    'GRID_COLS', 'GRID_ROWS', 'CELL_WIDTH', 'CELL_HEIGHT', 'SPACING',
    'CollisionDetector', 'GridItem',
    'CellCalculator',
    'GridManager', 'PlacementResult',
    'DropHandler', 'DropResult', 'DropAction',
    'GridPopulator', 'ItemMover',
]
