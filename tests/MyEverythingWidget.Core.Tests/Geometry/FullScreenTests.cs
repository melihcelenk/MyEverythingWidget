using MyEverythingWidget.Core.Geometry;

namespace MyEverythingWidget.Core.Tests.Geometry;

public sealed class FullScreenTests
{
    private static readonly PixelRect Monitor = new(0, 0, 1920, 1080);

    [Fact]
    public void WindowCoveringTheWholeMonitor_IsFullScreen()
    {
        Assert.True(FullScreen.Covers(new PixelRect(0, 0, 1920, 1080), Monitor));
    }

    [Fact]
    public void WindowLargerThanTheMonitor_IsFullScreen()
    {
        // Some games and video players overhang the monitor by their invisible borders.
        Assert.True(FullScreen.Covers(new PixelRect(-8, -8, 1936, 1096), Monitor));
    }

    [Fact]
    public void MaximisedWindow_LeavingTheTaskbar_IsNotFullScreen()
    {
        Assert.False(FullScreen.Covers(new PixelRect(0, 0, 1920, 1032), Monitor));
    }

    [Fact]
    public void WindowOnAnotherMonitor_IsNotFullScreenOnThisOne()
    {
        Assert.False(FullScreen.Covers(new PixelRect(1920, 0, 1920, 1080), Monitor));
    }

    [Fact]
    public void SmallWindow_IsNotFullScreen()
    {
        Assert.False(FullScreen.Covers(new PixelRect(100, 100, 800, 600), Monitor));
    }
}
