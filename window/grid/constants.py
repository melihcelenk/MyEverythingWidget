"""
Grid system constants - single source of truth.

All grid-related dimensions and limits are defined here.
"""

# Grid dimensions (Android-like fixed grid)
GRID_COLS = 4
GRID_ROWS = 5

# Cell dimensions in pixels
CELL_WIDTH = 80
CELL_HEIGHT = 80
SPACING = 0  # No spacing between cards

# Layout margins (left aligned)
MARGIN_LEFT = 4
MARGIN_TOP = 4
MARGIN_RIGHT = 0
MARGIN_BOTTOM = 4

# Calculated values
CELL_WITH_SPACING_W = CELL_WIDTH + SPACING
CELL_WITH_SPACING_H = CELL_HEIGHT + SPACING

# Total grid size
TOTAL_WIDTH = MARGIN_LEFT + GRID_COLS * CELL_WITH_SPACING_W - SPACING + MARGIN_RIGHT
TOTAL_HEIGHT = MARGIN_TOP + GRID_ROWS * CELL_WITH_SPACING_H - SPACING + MARGIN_BOTTOM
