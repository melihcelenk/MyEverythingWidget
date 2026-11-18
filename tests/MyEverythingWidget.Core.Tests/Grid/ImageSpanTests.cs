using MyEverythingWidget.Core.Grid;

namespace MyEverythingWidget.Core.Tests.Grid;

/// <summary>Image card size from the image's aspect ratio (MEW-4 I2; same rules as the Python version).</summary>
public sealed class ImageSpanTests
{
    [Theory]
    [InlineData(3000, 1000, 3, 1)] // panorama 3:1
    [InlineData(1920, 1080, 3, 2)] // 16:9
    [InlineData(1600, 1200, 2, 1)] // 4:3
    [InlineData(1000, 1000, 2, 2)] // square
    [InlineData(1080, 1920, 1, 2)] // portrait 9:16
    [InlineData(500, 2000, 1, 3)]  // tall 1:4
    public void FromPixelSize_FollowsAspectRatio(int width, int height, int columns, int rows)
    {
        Assert.Equal(new GridSpan(columns, rows), ImageSpan.FromPixelSize(width, height));
    }

    [Theory]
    [InlineData(0, 100)]
    [InlineData(100, 0)]
    [InlineData(-5, 10)]
    public void FromPixelSize_WithoutSize_IsOneCell(int width, int height)
    {
        Assert.Equal(GridSpan.One, ImageSpan.FromPixelSize(width, height));
    }
}
