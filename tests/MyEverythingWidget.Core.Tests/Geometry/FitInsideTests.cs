using MyEverythingWidget.Core.Geometry;

namespace MyEverythingWidget.Core.Tests.Geometry;

/// <summary>Opening the widget from its compact icon keeps it entirely on the icon's monitor.</summary>
public sealed class FitInsideTests
{
    private static readonly PixelRect WorkArea = new(1920, 0, 1920, 1040);

    [Fact]
    public void FitInside_AlreadyInside_IsUnchanged()
    {
        var window = new PixelRect(2000, 100, 400, 500);

        Assert.Equal(window, WindowPlacement.FitInside(window, WorkArea));
    }

    [Fact]
    public void FitInside_PastRightEdge_ShiftsLeftOnlyAsFarAsNeeded()
    {
        Assert.Equal(new PixelRect(3840 - 400, 100, 400, 500), WindowPlacement.FitInside(new PixelRect(3800, 100, 400, 500), WorkArea));
    }

    [Fact]
    public void FitInside_PastBottomEdge_ShiftsUp()
    {
        Assert.Equal(new PixelRect(2000, 1040 - 500, 400, 500), WindowPlacement.FitInside(new PixelRect(2000, 900, 400, 500), WorkArea));
    }

    [Fact]
    public void FitInside_PastLeftAndTopEdges_ShiftsRightAndDown()
    {
        Assert.Equal(new PixelRect(1920, 0, 400, 500), WindowPlacement.FitInside(new PixelRect(1800, -50, 400, 500), WorkArea));
    }

    [Fact]
    public void FitInside_LargerThanArea_KeepsTopLeftOfArea()
    {
        Assert.Equal(new PixelRect(1920, 0, 2000, 1200), WindowPlacement.FitInside(new PixelRect(2500, 300, 2000, 1200), WorkArea));
    }
}
