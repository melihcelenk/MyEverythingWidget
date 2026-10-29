"""Constants for humanized UI test runner."""

# Grid constants (copied from window.grid.constants to avoid PySide6 dependency)
CELL_WIDTH = 80
CELL_HEIGHT = 80
SPACING = 0
MARGIN_LEFT = 4

# Dialog dimensions
DIALOG_WIDTH = 336  # Actual observed width
DIALOG_HEIGHT = 380  # Actual observed height
TAB_HEIGHT = 32
LABEL_HEIGHT = 20
MARGIN_TOP = 16
INPUT_HEIGHT = 25
GAP = 12

# Window dimensions
WINDOW_WIDTH = 320
WINDOW_HEIGHT = 500
FAB_SIZE = 40
FAB_MARGIN = 12


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
