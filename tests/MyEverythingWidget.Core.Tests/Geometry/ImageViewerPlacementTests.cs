using MyEverythingWidget.Core.Geometry;

namespace MyEverythingWidget.Core.Tests.Geometry;

/// <summary>Where and how large the image viewer opens.</summary>
public sealed class ImageViewerPlacementTests
{
    private static readonly PixelRect WorkArea = new(1920, 0, 1920, 1040);

    [Fact]
    public void SmallImage_IsShownAtItsOwnSizeInTheMiddle()
    {
        var rect = ImageViewerPlacement.Fit(new PixelSize(800, 400), WorkArea);

        Assert.Equal(new PixelRect(1920 + 560, 320, 800, 400), rect);
    }

    [Fact]
    public void LargeImage_ShrinksToNinetyPercentKeepingItsShape()
    {
        var rect = ImageViewerPlacement.Fit(new PixelSize(4000, 1000), WorkArea);

        Assert.Equal(1728, rect.Width);
        Assert.Equal(432, rect.Height);
        Assert.Equal(1920 + 96, rect.X);
        Assert.Equal(304, rect.Y);
    }

    [Fact]
    public void TallImage_IsLimitedByHeight()
    {
        var rect = ImageViewerPlacement.Fit(new PixelSize(1000, 3000), WorkArea);

        Assert.Equal(936, rect.Height);
        Assert.Equal(312, rect.Width);
    }

    [Fact]
    public void UnknownImageSize_UsesHalfTheArea()
    {
        var rect = ImageViewerPlacement.Fit(new PixelSize(0, 0), WorkArea);

        Assert.Equal(new PixelRect(1920 + 480, 260, 960, 520), rect);
    }
}
