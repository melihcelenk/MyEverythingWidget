using MyEverythingWidget.Core.Geometry;

namespace MyEverythingWidget.Core.Tests.Geometry;

public sealed class WindowPlacementTests
{
    private static readonly PixelRect PrimaryWorkArea = new(0, 0, 1920, 1040);
    private static readonly PixelSize DefaultSize = new(404, 480);

    [Fact]
    public void Resolve_WhenNothingSaved_PlacesDefaultSizeAtTopRightOfPrimary()
    {
        var result = WindowPlacement.Resolve(null, [PrimaryWorkArea], PrimaryWorkArea, DefaultSize);

        Assert.Equal(new PixelRect(1920 - 404 - WindowPlacement.EdgeMargin, WindowPlacement.EdgeMargin, 404, 480), result);
    }

    [Fact]
    public void Resolve_WhenSavedIsFullyVisible_KeepsIt()
    {
        var saved = new PixelRect(300, 200, 500, 600);

        var result = WindowPlacement.Resolve(saved, [PrimaryWorkArea], PrimaryWorkArea, DefaultSize);

        Assert.Equal(saved, result);
    }

    [Fact]
    public void Resolve_WhenSavedIsOnRemovedMonitor_FallsBackToPrimary()
    {
        var saved = new PixelRect(2500, 100, 404, 480);

        var result = WindowPlacement.Resolve(saved, [PrimaryWorkArea], PrimaryWorkArea, DefaultSize);

        Assert.Equal(new PixelRect(1920 - 404 - WindowPlacement.EdgeMargin, WindowPlacement.EdgeMargin, 404, 480), result);
    }

    [Fact]
    public void Resolve_WhenSavedIsOnSecondMonitorThatStillExists_KeepsIt()
    {
        var secondary = new PixelRect(1920, 0, 2560, 1400);
        var saved = new PixelRect(2500, 100, 404, 480);

        var result = WindowPlacement.Resolve(saved, [PrimaryWorkArea, secondary], PrimaryWorkArea, DefaultSize);

        Assert.Equal(saved, result);
    }

    [Fact]
    public void Resolve_WhenSavedIsPartlyOffScreenButTitleBarReachable_KeepsIt()
    {
        var saved = new PixelRect(1700, 100, 404, 480);

        var result = WindowPlacement.Resolve(saved, [PrimaryWorkArea], PrimaryWorkArea, DefaultSize);

        Assert.Equal(saved, result);
    }

    [Fact]
    public void Resolve_WhenSavedTitleBarIsAboveScreen_FallsBackToPrimary()
    {
        var saved = new PixelRect(300, -200, 404, 480);

        var result = WindowPlacement.Resolve(saved, [PrimaryWorkArea], PrimaryWorkArea, DefaultSize);

        Assert.Equal(new PixelRect(1920 - 404 - WindowPlacement.EdgeMargin, WindowPlacement.EdgeMargin, 404, 480), result);
    }

    [Fact]
    public void Resolve_KeepsSavedSizeWhenFallingBack()
    {
        var saved = new PixelRect(5000, 5000, 600, 700);

        var result = WindowPlacement.Resolve(saved, [PrimaryWorkArea], PrimaryWorkArea, DefaultSize);

        Assert.Equal(new PixelRect(1920 - 600 - WindowPlacement.EdgeMargin, WindowPlacement.EdgeMargin, 600, 700), result);
    }
}
