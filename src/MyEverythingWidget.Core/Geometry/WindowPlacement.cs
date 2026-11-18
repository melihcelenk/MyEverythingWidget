namespace MyEverythingWidget.Core.Geometry;

/// <summary>
/// Decides where the widget window opens, given the saved bounds and the monitors that exist now.
/// </summary>
public static class WindowPlacement
{
    /// <summary>Distance, in pixels, between the default window position and the work area edges.</summary>
    public const int EdgeMargin = 16;

    /// <summary>Height of the strip at the top of the window that must be on screen so it can be dragged.</summary>
    public const int TitleBarGripHeight = 32;

    /// <summary>Minimum visible width of that strip for the window to count as reachable.</summary>
    public const int MinimumVisibleWidth = 100;

    /// <summary>
    /// Returns <paramref name="saved"/> when the user can still reach its title bar on one of
    /// <paramref name="workAreas"/>; otherwise returns a rectangle at the top-right corner of
    /// <paramref name="primaryWorkArea"/>, keeping the saved size when there is one.
    /// </summary>
    public static PixelRect Resolve(
        PixelRect? saved,
        IReadOnlyList<PixelRect> workAreas,
        PixelRect primaryWorkArea,
        PixelSize defaultSize)
    {
        ArgumentNullException.ThrowIfNull(workAreas);

        if (saved is { } bounds && workAreas.Any(area => IsTitleBarReachable(bounds, area)))
        {
            return bounds;
        }

        var size = saved?.Size ?? defaultSize;
        return new PixelRect(
            primaryWorkArea.Right - size.Width - EdgeMargin,
            primaryWorkArea.Y + EdgeMargin,
            size.Width,
            size.Height);
    }

    /// <summary>
    /// Moves <paramref name="window"/> by the smallest amount that puts it entirely inside <paramref name="workArea"/>;
    /// a window larger than the area keeps the area's top-left corner. The size never changes.
    /// </summary>
    public static PixelRect FitInside(PixelRect window, PixelRect workArea)
    {
        var x = Math.Max(workArea.X, Math.Min(window.X, workArea.Right - window.Width));
        var y = Math.Max(workArea.Y, Math.Min(window.Y, workArea.Bottom - window.Height));
        return window with { X = x, Y = y };
    }

    /// <summary>
    /// Returns the corner of <paramref name="workArea"/> that <paramref name="rect"/> is nearest to, judged by which
    /// half of the area its centre is in. The widget opens from, and shrinks back to, this corner of the compact icon.
    /// </summary>
    public static WindowCorner NearestCorner(PixelRect rect, PixelRect workArea)
    {
        var centreX = rect.X + (rect.Width / 2);
        var centreY = rect.Y + (rect.Height / 2);
        return new WindowCorner(
            Right: centreX > workArea.X + (workArea.Width / 2),
            Bottom: centreY > workArea.Y + (workArea.Height / 2));
    }

    /// <summary>
    /// Returns a rectangle of <paramref name="size"/> whose <paramref name="corner"/> is at the same point as that
    /// corner of <paramref name="anchor"/>.
    /// </summary>
    public static PixelRect AlignCorner(PixelRect anchor, PixelSize size, WindowCorner corner)
    {
        var x = corner.Right ? anchor.Right - size.Width : anchor.X;
        var y = corner.Bottom ? anchor.Bottom - size.Height : anchor.Y;
        return new PixelRect(x, y, size.Width, size.Height);
    }

    private static bool IsTitleBarReachable(PixelRect window, PixelRect area)
    {
        var titleBarFitsVertically = window.Y >= area.Y && window.Y + TitleBarGripHeight <= area.Bottom;
        var visibleWidth = Math.Min(window.Right, area.Right) - Math.Max(window.X, area.X);
        return titleBarFitsVertically && visibleWidth >= MinimumVisibleWidth;
    }
}
