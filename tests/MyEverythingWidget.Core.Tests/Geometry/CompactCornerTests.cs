using MyEverythingWidget.Core.Geometry;

namespace MyEverythingWidget.Core.Tests.Geometry;

/// <summary>
/// The widget opens from the compact icon's corner nearest the screen corner, and shrinks back to that corner, so
/// the icon stays where the user put it (MEW-4 PHASE17 17.7, S11 → B).
/// </summary>
public sealed class CompactCornerTests
{
    private static readonly PixelRect WorkArea = new(0, 0, 1920, 1040);
    private static readonly PixelSize Widget = new(412, 496);
    private static readonly PixelSize Icon = new(80, 80);

    [Theory]
    [InlineData(1800, 20, true, false)]
    [InlineData(1800, 940, true, true)]
    [InlineData(40, 20, false, false)]
    [InlineData(40, 940, false, true)]
    public void NearestCorner_FollowsTheHalfOfTheScreenTheRectangleIsIn(int x, int y, bool right, bool bottom)
    {
        Assert.Equal(new WindowCorner(right, bottom), WindowPlacement.NearestCorner(new PixelRect(x, y, 80, 80), WorkArea));
    }

    [Fact]
    public void NearestCorner_OnASecondMonitor_UsesThatMonitorsMiddle()
    {
        var secondMonitor = new PixelRect(1920, 0, 1920, 1040);

        Assert.Equal(new WindowCorner(Right: false, Bottom: false), WindowPlacement.NearestCorner(new PixelRect(2000, 20, 80, 80), secondMonitor));
    }

    [Fact]
    public void Expanding_IconAtTheTopRight_LinesUpTheRightAndTopEdges()
    {
        var icon = new PixelRect(1800, 20, Icon.Width, Icon.Height);

        var widget = WindowPlacement.AlignCorner(icon, Widget, WindowPlacement.NearestCorner(icon, WorkArea));

        Assert.Equal(icon.Right, widget.Right);
        Assert.Equal(icon.Y, widget.Y);
        Assert.Equal(Widget, widget.Size);
    }

    [Fact]
    public void Expanding_IconAtTheBottomRight_LinesUpTheRightAndBottomEdges()
    {
        var icon = new PixelRect(1800, 940, Icon.Width, Icon.Height);

        var widget = WindowPlacement.AlignCorner(icon, Widget, WindowPlacement.NearestCorner(icon, WorkArea));

        Assert.Equal(icon.Right, widget.Right);
        Assert.Equal(icon.Bottom, widget.Bottom);
    }

    [Fact]
    public void Expanding_IconAtTheTopLeft_KeepsTheTopLeftCorner()
    {
        var icon = new PixelRect(40, 20, Icon.Width, Icon.Height);

        var widget = WindowPlacement.AlignCorner(icon, Widget, WindowPlacement.NearestCorner(icon, WorkArea));

        Assert.Equal(new PixelRect(40, 20, Widget.Width, Widget.Height), widget);
    }

    [Theory]
    [InlineData(1800, 20)]
    [InlineData(1800, 940)]
    [InlineData(40, 940)]
    [InlineData(1000, 500)]
    public void ExpandingThenShrinking_PutsTheIconBackWhereItWas(int x, int y)
    {
        var icon = new PixelRect(x, y, Icon.Width, Icon.Height);
        var corner = WindowPlacement.NearestCorner(icon, WorkArea);

        var widget = WindowPlacement.AlignCorner(icon, Widget, corner);
        var back = WindowPlacement.AlignCorner(widget, Icon, corner);

        Assert.Equal(icon, back);
    }
}
