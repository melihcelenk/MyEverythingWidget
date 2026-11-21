namespace MyEverythingWidget.Core.Geometry;

/// <summary>
/// Tells whether a window is shown full screen: a video, a game or a presentation covering a whole monitor, taskbar
/// included.
/// </summary>
public static class FullScreen
{
    /// <summary>
    /// Returns whether <paramref name="window"/> covers all of <paramref name="monitor"/> (the monitor's whole area, not
    /// its work area). A maximised window leaves the taskbar visible and is not full screen.
    /// </summary>
    public static bool Covers(PixelRect window, PixelRect monitor) =>
        window.X <= monitor.X
        && window.Y <= monitor.Y
        && window.X + window.Width >= monitor.X + monitor.Width
        && window.Y + window.Height >= monitor.Y + monitor.Height;
}
