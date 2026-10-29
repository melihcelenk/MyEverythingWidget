"""
Image grid span calculator
Calculates how many grid cells an image should span based on aspect ratio
"""
from typing import Tuple


class ImageGridCalculator:
    """Calculates grid span for images based on aspect ratio"""

    def __init__(self, max_columns: int = 3, max_rows: int = 3):
        self._max_columns = max_columns
        self._max_rows = max_rows

    def get_aspect_ratio(self, width: int, height: int) -> float:
        """Calculate aspect ratio (width / height)"""
        if height == 0:
            return 1.0
        return width / height

    def calculate_span(self, width: int, height: int) -> Tuple[int, int]:
        """
        Calculate grid span based on image dimensions.

        Returns:
            Tuple of (col_span, row_span)

        Span rules based on aspect ratio:
        - Square (0.9-1.1): 2x2
        - Wide horizontal (>2.5): 3x1
        - Medium horizontal (1.5-2.5): 3x2
        - Narrow horizontal (1.1-1.5): 2x1
        - Vertical (<0.9): 1x2 or 1x3
        """
        if width <= 0 or height <= 0:
            return (1, 1)

        ratio = self.get_aspect_ratio(width, height)

        # Very wide (panoramic)
        if ratio >= 2.5:
            return (3, 1)

        # Medium horizontal (16:9, etc)
        if ratio >= 1.5:
            return (3, 2)

        # Narrow horizontal (4:3, etc)
        if ratio >= 1.1:
            return (2, 1)

        # Square
        if ratio >= 0.9:
            return (2, 2)

        # Vertical
        if ratio >= 0.5:
            return (1, 2)

        # Very tall
        return (1, 3)
