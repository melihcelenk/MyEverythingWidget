using MyEverythingWidget.Core.Geometry;
using MyEverythingWidget.Core.Grid;

namespace MyEverythingWidget.Core.Tests.Geometry;

/// <summary>Converting between the window's client size and the number of grid cells.</summary>
public sealed class GridWindowSizingTests
{
    private static readonly GridWindowSizing Sizing = new(CellSize: 80, ChromeWidth: 12, ChromeHeight: 100);

    [Theory]
    [InlineData(1.0, 5, 5, 412, 500)]
    [InlineData(1.5, 2, 3, 378, 390)]
    public void ClientSize_IsCellsPlusChromeScaled(double scale, int rows, int columns, int width, int height)
    {
        Assert.Equal(new PixelSize(width, height), Sizing.ClientSize(new GridSize(rows, columns), scale));
    }

    [Theory]
    [InlineData(1.0, 412, 500, 5, 5)]
    [InlineData(1.0, 450, 539, 5, 5)]
    [InlineData(1.0, 455, 541, 6, 6)]
    [InlineData(1.5, 378, 390, 2, 3)]
    public void GridSizeFor_RoundsToNearestCellCount(double scale, int width, int height, int rows, int columns)
    {
        Assert.Equal(new GridSize(rows, columns), Sizing.GridSizeFor(new PixelSize(width, height), scale));
    }

    [Fact]
    public void GridSizeFor_TinyWindow_IsZeroNotNegative()
    {
        Assert.Equal(new GridSize(0, 0), Sizing.GridSizeFor(new PixelSize(1, 1), 1.0));
    }
}
