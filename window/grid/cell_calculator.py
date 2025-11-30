"""
Grid cell calculations.

Handles:
- Position to cell conversion
- Cell to position conversion
- Finding first available cell
"""
from __future__ import annotations

from typing import Set, Tuple, Optional

from window.grid.constants import (
    GRID_COLS, GRID_ROWS,
    CELL_WIDTH, CELL_HEIGHT, SPACING,
    MARGIN_LEFT, MARGIN_TOP,
    CELL_WITH_SPACING_W, CELL_WITH_SPACING_H
)


class CellCalculator:
    """Calculates grid cell positions and finds available cells."""

    @staticmethod
    def pos_to_cell(x: int, y: int) -> Tuple[int, int]:
        """
        Convert pixel position to grid cell.
        
        Args:
            x: X position in pixels
            y: Y position in pixels
            
        Returns:
            (row, col) tuple, clamped to valid grid bounds
        """
        # Subtract margins
        adj_x = x - MARGIN_LEFT
        adj_y = y - MARGIN_TOP

        # Calculate cell
        col = max(0, adj_x // CELL_WITH_SPACING_W)
        row = max(0, adj_y // CELL_WITH_SPACING_H)

        # Clamp to grid bounds
        col = min(col, GRID_COLS - 1)
        row = min(row, GRID_ROWS - 1)

        return (row, col)

    @staticmethod
    def cell_to_pos(row: int, col: int) -> Tuple[int, int]:
        """
        Convert grid cell to pixel position.
        
        Args:
            row: Grid row
            col: Grid column
            
        Returns:
            (x, y) tuple in pixels
        """
        x = MARGIN_LEFT + col * CELL_WITH_SPACING_W
        y = MARGIN_TOP + row * CELL_WITH_SPACING_H
        return (x, y)

    @staticmethod
    def get_cell_size(col_span: int = 1, row_span: int = 1) -> Tuple[int, int]:
        """
        Get pixel size for a cell span.
        
        Args:
            col_span: Number of columns
            row_span: Number of rows
            
        Returns:
            (width, height) tuple in pixels
        """
        width = col_span * CELL_WIDTH + (col_span - 1) * SPACING
        height = row_span * CELL_HEIGHT + (row_span - 1) * SPACING
        return (width, height)

    @staticmethod
    def find_first_available_cell(occupied: Set[Tuple[int, int]],
                                  row_span: int = 1,
                                  col_span: int = 1) -> Optional[Tuple[int, int]]:
        """
        Find the first available grid cell for an item.
        
        Scans row by row, left to right.
        
        Args:
            occupied: Set of already occupied (row, col) cells
            row_span: Number of rows the item needs
            col_span: Number of columns the item needs
            
        Returns:
            (row, col) tuple or None if grid is full
        """
        for row in range(GRID_ROWS):
            # Check if item would overflow rows
            if row + row_span > GRID_ROWS:
                break

            for col in range(GRID_COLS):
                # Check if item would overflow columns
                if col + col_span > GRID_COLS:
                    continue

                # Check if all required cells are free
                can_fit = True
                for r in range(row, row + row_span):
                    for c in range(col, col + col_span):
                        if (r, c) in occupied:
                            can_fit = False
                            break
                    if not can_fit:
                        break

                if can_fit:
                    return (row, col)

        return None  # Grid is full

    @staticmethod
    def clamp_position(row: int, col: int,
                       row_span: int = 1, col_span: int = 1) -> Tuple[int, int]:
        """
        Clamp position to ensure item fits within grid.
        
        Args:
            row: Desired row
            col: Desired column
            row_span: Number of rows
            col_span: Number of columns
            
        Returns:
            (row, col) clamped to valid bounds
        """
        max_row = GRID_ROWS - row_span
        max_col = GRID_COLS - col_span

        clamped_row = max(0, min(row, max_row))
        clamped_col = max(0, min(col, max_col))

        return (clamped_row, clamped_col)
