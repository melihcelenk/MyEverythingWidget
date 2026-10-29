"""
Tests for ImageGridCalculator service
Calculates grid span based on image aspect ratio
"""


class TestImageGridCalculator:
    """Tests for grid span calculation based on aspect ratio"""

    def test_calculator_creation(self):
        """Test ImageGridCalculator can be created"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()
        assert calc is not None

    def test_square_image_returns_2x2(self):
        """Square image (1:1) should return 2x2 span"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()
        col_span, row_span = calc.calculate_span(width=100, height=100)

        assert col_span == 2
        assert row_span == 2

    def test_wide_horizontal_image_returns_3x1(self):
        """Very wide image (3:1 or wider) should return 3x1 span"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()
        col_span, row_span = calc.calculate_span(width=300, height=100)

        assert col_span == 3
        assert row_span == 1

    def test_medium_horizontal_image_returns_3x2(self):
        """Medium horizontal image (1.5:1 to 2.5:1) should return 3x2 span"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()
        col_span, row_span = calc.calculate_span(width=200, height=100)

        assert col_span == 3
        assert row_span == 2

    def test_narrow_horizontal_image_returns_2x1(self):
        """Narrow horizontal image (1.2:1 to 1.5:1) should return 2x1 span"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()
        col_span, row_span = calc.calculate_span(width=140, height=100)

        assert col_span == 2
        assert row_span == 1

    def test_vertical_image_returns_1x2(self):
        """Vertical image (taller than wide) should return 1x2 span"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()
        col_span, row_span = calc.calculate_span(width=100, height=200)

        assert col_span == 1
        assert row_span == 2

    def test_very_vertical_image_returns_1x3(self):
        """Very tall image should return 1x3 span"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()
        col_span, row_span = calc.calculate_span(width=100, height=300)

        assert col_span == 1
        assert row_span == 3

    def test_small_square_image_returns_1x1(self):
        """Small images should return minimum 1x1"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()
        col_span, row_span = calc.calculate_span(width=50, height=50)

        assert col_span >= 1
        assert row_span >= 1

    def test_aspect_ratio_calculation(self):
        """Test aspect ratio is calculated correctly"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()

        # 16:9 aspect ratio
        ratio = calc.get_aspect_ratio(width=1920, height=1080)
        assert abs(ratio - 1.78) < 0.01

    def test_zero_dimensions_handled(self):
        """Test zero dimensions don't cause errors"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()

        # Should return minimum span, not crash
        col_span, row_span = calc.calculate_span(width=0, height=100)
        assert col_span >= 1
        assert row_span >= 1

        col_span, row_span = calc.calculate_span(width=100, height=0)
        assert col_span >= 1
        assert row_span >= 1

    def test_16x9_screenshot_returns_3x2(self):
        """16:9 screenshot should return 3x2 span"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()
        col_span, row_span = calc.calculate_span(width=1920, height=1080)

        assert col_span == 3
        assert row_span == 2

    def test_4x3_photo_returns_2x2_or_3x2(self):
        """4:3 photo should return reasonable span"""
        from services.image_grid_calculator import ImageGridCalculator

        calc = ImageGridCalculator()
        col_span, row_span = calc.calculate_span(width=400, height=300)

        # 4:3 ratio is 1.33, should be 2x1 or 2x2
        assert col_span in [2, 3]
        assert row_span in [1, 2]
