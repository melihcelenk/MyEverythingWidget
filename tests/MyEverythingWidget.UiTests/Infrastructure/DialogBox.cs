using System.Drawing;
using FlaUI.Core.Capturing;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Finds the visible box of an open WinUI dialog on screen. Its UI Automation element covers the whole window, so the
/// box edges are found by colour: from a point on the dialog's plain surface outwards until the colour changes.
/// </summary>
internal static class DialogBox
{
    private const int ColourStep = 24;

    /// <summary>Returns the y of the dialog's top edge above <paramref name="surface"/>, a point on its plain surface.</summary>
    public static int TopEdgeAbove(Point surface) => Scan(surface, dx: 0, dy: -1).Y;

    /// <summary>Returns the x just past the dialog's right edge, right of <paramref name="surface"/>.</summary>
    public static int RightEdgeOf(Point surface) => Scan(surface, dx: 1, dy: 0).X + 1;

    private static Point Scan(Point start, int dx, int dy)
    {
        using var screen = Capture.Screen().Bitmap;
        var colour = screen.GetPixel(start.X, start.Y);
        var point = start;
        while (point.X + dx >= 0 && point.X + dx < screen.Width && point.Y + dy >= 0 && point.Y + dy < screen.Height
            && Same(screen.GetPixel(point.X + dx, point.Y + dy), colour))
        {
            point = new Point(point.X + dx, point.Y + dy);
        }

        return point;
    }

    private static bool Same(Color a, Color b) =>
        Math.Abs(a.R - b.R) < ColourStep && Math.Abs(a.G - b.G) < ColourStep && Math.Abs(a.B - b.B) < ColourStep;
}
