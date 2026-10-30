namespace MyEverythingWidget.Core.Geometry;

/// <summary>
/// Decides the bounds of the window that shows an image large: at most 90% of the monitor's work area, the image's
/// own shape, centred on that monitor. Images smaller than that are shown at their own size.
/// </summary>
public static class ImageViewerPlacement
{
    /// <summary>Largest share of the work area the viewer may cover in either direction.</summary>
    public const double MaxShare = 0.9;

    /// <summary>Returns the viewer bounds for an image of <paramref name="image"/> pixels on <paramref name="workArea"/>.</summary>
    public static PixelRect Fit(PixelSize image, PixelRect workArea)
    {
        var size = image.Width > 0 && image.Height > 0
            ? Scaled(image, workArea)
            : new PixelSize(workArea.Width / 2, workArea.Height / 2);
        return new PixelRect(
            workArea.X + ((workArea.Width - size.Width) / 2),
            workArea.Y + ((workArea.Height - size.Height) / 2),
            size.Width,
            size.Height);
    }

    private static PixelSize Scaled(PixelSize image, PixelRect workArea)
    {
        var scale = Math.Min(1.0, Math.Min(workArea.Width * MaxShare / image.Width, workArea.Height * MaxShare / image.Height));
        return new PixelSize((int)Math.Round(image.Width * scale), (int)Math.Round(image.Height * scale));
    }
}
